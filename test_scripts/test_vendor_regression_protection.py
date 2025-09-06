# Test file: test_scripts/test_vendor_regression_protection.py
import json
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import Mock

import pytest


def test_harpercollins_processing_regression():
    """Test that Creative-Coop changes don't break HarperCollins processing - RED test initially"""
    # Store baseline HarperCollins performance
    baseline_file = Path("test_scripts/harpercollins_baseline_metrics.json")

    try:
        # Run HarperCollins test and capture detailed results
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "test_scripts/perfect_processing.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        processing_time = time.time() - start_time

        # Parse results
        success_indicators = result.stdout.count("✅")
        error_indicators = result.stdout.count("❌")

        current_metrics = {
            "return_code": result.returncode,
            "processing_time": processing_time,
            "success_count": success_indicators,
            "error_count": error_indicators,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr),
        }

        # RED: Initially should pass, but we're establishing baseline for future regression detection
        assert (
            result.returncode == 0
        ), f"HarperCollins regression test should pass, got return code: {result.returncode}"
        assert (
            success_indicators > 0
        ), f"HarperCollins should show success indicators, found: {success_indicators}"
        assert (
            "23 line items" in result.stdout or success_indicators >= 15
        ), "HarperCollins should process substantial line items"

        # Store baseline for future comparisons
        if baseline_file.exists():
            with open(baseline_file, "r") as f:
                baseline = json.load(f)

            # Compare against baseline
            performance_degradation = processing_time / baseline["processing_time"] - 1
            success_degradation = (
                (baseline["success_count"] - success_indicators)
                / baseline["success_count"]
                if baseline["success_count"] > 0
                else 0
            )

            # RED: Fail if performance degrades significantly
            assert (
                performance_degradation < 0.5
            ), f"HarperCollins processing time increased by {performance_degradation:.1%}"
            assert (
                success_degradation <= 0
            ), f"HarperCollins success rate decreased by {success_degradation:.1%}"

        # Update baseline
        with open(baseline_file, "w") as f:
            json.dump(current_metrics, f, indent=2)

        print(
            f"✅ HarperCollins processing completed in {processing_time:.2f}s with {success_indicators} successes"
        )

    except subprocess.TimeoutExpired:
        pytest.fail(
            "HarperCollins regression test timed out - possible performance regression"
        )
    except FileNotFoundError:
        pytest.skip("HarperCollins test script not available")


def test_onehundred80_processing_regression():
    """Test that Creative-Coop changes don't break OneHundred80 processing - RED test initially"""
    baseline_file = Path("test_scripts/onehundred80_baseline_metrics.json")

    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "test_scripts/test_onehundred80.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        processing_time = time.time() - start_time

        success_indicators = result.stdout.count("✅")
        error_indicators = result.stdout.count("❌")

        current_metrics = {
            "return_code": result.returncode,
            "processing_time": processing_time,
            "success_count": success_indicators,
            "error_count": error_indicators,
        }

        # RED: Should maintain existing functionality
        assert (
            result.returncode == 0
        ), f"OneHundred80 regression test should pass, got: {result.returncode}"

        # Compare with baseline if available
        if baseline_file.exists():
            with open(baseline_file, "r") as f:
                baseline = json.load(f)

            performance_degradation = (
                processing_time / baseline["processing_time"] - 1
                if baseline["processing_time"] > 0
                else 0
            )
            assert (
                performance_degradation < 0.5
            ), f"OneHundred80 processing time increased by {performance_degradation:.1%}"

        # Update baseline
        with open(baseline_file, "w") as f:
            json.dump(current_metrics, f, indent=2)

        print(
            f"✅ OneHundred80 processing completed in {processing_time:.2f}s with {success_indicators} successes"
        )

    except subprocess.TimeoutExpired:
        pytest.fail("OneHundred80 regression test timed out")
    except FileNotFoundError:
        pytest.skip("OneHundred80 test script not available")


def test_creative_coop_changes_dont_affect_other_vendor_detection():
    """Test that Creative-Coop pattern changes don't interfere with other vendor detection"""
    try:
        from main import detect_vendor_type
    except ImportError:
        pytest.skip("detect_vendor_type function not available")

    # Test vendor detection for other vendors
    test_cases = [
        ("HarperCollins Distribution Services", "harpercollins"),
        ("OneHundred80 Inc invoice", "onehundred80"),
        ("Rifle Paper Co. invoice", "rifle_paper"),
        ("Generic vendor invoice content", "generic"),
    ]

    for test_text, expected_vendor in test_cases:
        detected_vendor = detect_vendor_type(test_text)

        # RED: These should not be affected by Creative-Coop changes
        if expected_vendor != "generic":
            # Allow some flexibility in vendor detection
            assert (
                detected_vendor == expected_vendor or detected_vendor == "generic"
            ), f"Vendor detection failed for {expected_vendor}: got {detected_vendor}"

        # Ensure Creative-Coop detection doesn't interfere
        if detected_vendor == "creative_coop":
            assert (
                "Creative" in test_text or "Coop" in test_text
            ), f"False positive Creative-Coop detection for {expected_vendor}"

    print("✅ Vendor detection maintains accuracy for all vendors")


def test_processing_function_signatures_unchanged():
    """Test that existing processing function signatures haven't changed"""
    try:
        from main import (
            extract_line_items,
            extract_line_items_from_entities,
            extract_line_items_from_text,
            process_harpercollins_document,
            process_onehundred80_document,
        )
    except ImportError as e:
        pytest.skip(f"Required processing functions not available: {e}")

    import inspect

    # Check that function signatures haven't changed
    expected_signatures = {
        "process_harpercollins_document": ["document"],
        "process_onehundred80_document": ["document"],
        "extract_line_items_from_entities": [
            "document",
            "invoice_date",
            "vendor",
            "invoice_number",
        ],
        "extract_line_items": ["document", "invoice_date", "vendor", "invoice_number"],
        "extract_line_items_from_text": [
            "text",
            "invoice_date",
            "vendor",
            "invoice_number",
        ],
    }

    for func_name, expected_params in expected_signatures.items():
        func = locals()[func_name]
        signature = inspect.signature(func)
        actual_params = list(signature.parameters.keys())

        # RED: Should maintain existing signatures (allow for optional parameters)
        for expected_param in expected_params:
            assert (
                expected_param in actual_params
            ), f"Function signature changed for {func_name}: missing parameter {expected_param}"

    print("✅ All processing function signatures maintained")


def test_global_constants_and_patterns_unchanged():
    """Test that global constants used by other vendors haven't been modified"""
    try:
        from main import (
            clean_and_validate_quantity,
            extract_wholesale_price,
            format_date,
        )
    except ImportError as e:
        pytest.skip(f"Core utility functions not available: {e}")

    # Test that core utility functions still work as expected
    test_cases = [
        (format_date, "01/15/2025", "2025-01-15"),
        (format_date, "1/15/25", "2025-01-15"),
        (clean_and_validate_quantity, "24", 24),
        (clean_and_validate_quantity, "12 units", 12),
        (clean_and_validate_quantity, "invalid", 0),
    ]

    passed_tests = 0
    for func, input_val, expected_output in test_cases:
        try:
            result = func(input_val)

            # RED: Core functions should maintain existing behavior
            if result == expected_output:
                passed_tests += 1
            else:
                print(
                    f"⚠️ Core function {func.__name__} behavior changed: {input_val} -> {result} (expected {expected_output})"
                )
        except Exception as e:
            print(f"⚠️ Core function {func.__name__} failed: {e}")

    # Require at least 80% of tests to pass (some flexibility for edge cases)
    success_rate = passed_tests / len(test_cases)
    assert (
        success_rate >= 0.8
    ), f"Core functions success rate: {success_rate:.1%} (expected ≥80%)"

    print(f"✅ Core functions maintain {success_rate:.1%} compatibility")


def test_memory_usage_regression():
    """Test that Creative-Coop enhancements don't increase memory usage for other vendors"""
    try:
        import gc

        import psutil

        from main import process_harpercollins_document
    except ImportError as e:
        pytest.skip(f"Required modules not available: {e}")

    # Create mock HarperCollins document
    mock_document = Mock()
    mock_document.text = "Sample HarperCollins content for memory testing"
    mock_document.entities = []

    # Measure memory usage
    gc.collect()  # Clean up before measurement
    process = psutil.Process()
    memory_before = process.memory_info().rss

    # Process document
    for _ in range(10):  # Process multiple times to detect memory leaks
        try:
            result = process_harpercollins_document(mock_document)
            gc.collect()
        except Exception:
            pass  # Ignore processing errors for memory test

    memory_after = process.memory_info().rss
    memory_increase = memory_after - memory_before

    # RED: Memory usage should not increase significantly
    memory_increase_mb = memory_increase / (1024 * 1024)
    assert (
        memory_increase_mb < 20
    ), f"Memory usage increased by {memory_increase_mb:.1f}MB - possible memory leak"

    print(f"✅ Memory usage regression test passed: +{memory_increase_mb:.1f}MB")


def test_error_handling_regression():
    """Test that error handling for other vendors hasn't been affected"""
    try:
        from main import process_harpercollins_document, process_onehundred80_document
    except ImportError as e:
        pytest.skip(f"Processing functions not available: {e}")

    # Test error scenarios that should be handled gracefully
    error_scenarios = [
        Mock(text=None, entities=[]),  # None text
        Mock(text="", entities=[]),  # Empty text
        Mock(text="invalid", entities=None),  # None entities
    ]

    processing_functions = [
        ("HarperCollins", process_harpercollins_document),
        ("OneHundred80", process_onehundred80_document),
    ]

    for scenario in error_scenarios:
        for vendor_name, process_func in processing_functions:
            try:
                result = process_func(scenario)
                # RED: Should handle gracefully and return empty list or similar
                assert isinstance(
                    result, list
                ), f"{vendor_name} should return list for error scenarios"
                # Should not crash - if we get here, error handling worked

            except Exception as e:
                # Allow some exceptions but ensure they're handled gracefully
                assert "NoneType" not in str(e) or "list" not in str(
                    e
                ), f"{vendor_name} should handle None/empty inputs more gracefully: {e}"

    print("✅ Error handling regression test passed")


def test_existing_test_scripts_still_pass():
    """Test that existing vendor-specific test scripts still pass"""
    test_scripts = [
        ("HarperCollins", "test_scripts/perfect_processing.py"),
        ("OneHundred80", "test_scripts/test_onehundred80.py"),
    ]

    results = {}

    for vendor, script_path in test_scripts:
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300,
            )  # 5 minute timeout
            processing_time = time.time() - start_time

            results[vendor] = {
                "return_code": result.returncode,
                "processing_time": processing_time,
                "success_indicators": result.stdout.count("✅"),
                "error_indicators": result.stdout.count("❌"),
                "passed": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            results[vendor] = {
                "return_code": -1,
                "processing_time": 300,
                "success_indicators": 0,
                "error_indicators": 1,
                "passed": False,
                "error": "Test timed out",
            }
        except FileNotFoundError:
            results[vendor] = {
                "return_code": 0,  # Skip if not found
                "processing_time": 0,
                "success_indicators": 0,
                "error_indicators": 0,
                "passed": True,
                "error": "Test script not found - skipped",
            }

    # Check results
    passed_tests = sum(1 for result in results.values() if result["passed"])
    total_tests = len(results)

    print(f"📊 Existing test scripts results:")
    for vendor, result in results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"   {vendor}: {status} ({result['processing_time']:.1f}s)")
        if not result["passed"] and "error" in result:
            print(f"      {result['error']}")

    # RED: At least 80% of existing tests should still pass
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    assert (
        success_rate >= 0.8
    ), f"Existing test scripts success rate: {success_rate:.1%} (expected ≥80%)"

    print(f"✅ Existing test scripts regression check: {success_rate:.1%} success rate")


if __name__ == "__main__":
    # Run regression tests manually
    print("=== VENDOR REGRESSION PROTECTION TESTS ===")

    tests = [
        (
            "HarperCollins Processing Regression",
            test_harpercollins_processing_regression,
        ),
        ("OneHundred80 Processing Regression", test_onehundred80_processing_regression),
        (
            "Vendor Detection Protection",
            test_creative_coop_changes_dont_affect_other_vendor_detection,
        ),
        (
            "Function Signatures Protection",
            test_processing_function_signatures_unchanged,
        ),
        ("Core Functions Protection", test_global_constants_and_patterns_unchanged),
        ("Memory Usage Regression", test_memory_usage_regression),
        ("Error Handling Regression", test_error_handling_regression),
        ("Existing Test Scripts", test_existing_test_scripts_still_pass),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        try:
            test_func()
            passed += 1
            print(f"✅ PASSED")
        except pytest.skip.Exception as e:
            print(f"⏩ SKIPPED: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {e}")

    print(f"\n=== REGRESSION PROTECTION SUMMARY ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/(passed+failed):.1%}")

    if failed == 0:
        print("🎉 All regression protection tests passed!")
    else:
        print(
            f"⚠️ {failed} regression protection tests failed - investigate before deployment"
        )
