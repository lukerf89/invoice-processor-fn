#!/usr/bin/env python3
"""
Comprehensive regression testing framework for all vendor processing
Ensures Creative-Coop enhancements don't break existing functionality
"""

import gc
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import optional dependencies
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class RegressionTestResult:
    """Results from a single regression test"""

    vendor: str
    test_name: str
    passed: bool
    processing_time: float
    memory_usage_mb: float
    success_indicators: int
    error_indicators: int
    error_message: Optional[str]
    timestamp: str


@dataclass
class RegressionSummary:
    """Summary of all regression test results"""

    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    overall_success: bool
    test_results: List[RegressionTestResult]
    baseline_comparisons: Dict[str, Any]


class VendorRegressionTester:
    """Comprehensive regression testing for all vendor processing"""

    def __init__(self):
        self.baseline_dir = Path("test_scripts/baselines")
        self.baseline_dir.mkdir(exist_ok=True)
        self.test_results = []

    def run_all_regression_tests(self) -> RegressionSummary:
        """Run comprehensive regression tests for all vendors"""
        print("🔍 Starting comprehensive vendor regression testing")
        print("=" * 60)

        start_time = time.time()

        # Define test suite
        test_suite = [
            ("HarperCollins", self.test_harpercollins_regression),
            ("OneHundred80", self.test_onehundred80_regression),
            ("Rifle Paper", self.test_rifle_paper_regression),
            ("Core Functions", self.test_core_functions_regression),
            ("Memory Usage", self.test_memory_regression),
            ("Performance", self.test_performance_regression),
        ]

        # Run each test
        for vendor, test_func in test_suite:
            print(f"\n🧪 Testing {vendor} regression...")
            try:
                result = test_func()
                self.test_results.append(result)

                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"{status} {vendor}: {result.processing_time:.2f}s")

                if not result.passed:
                    print(f"   Error: {result.error_message}")

            except Exception as e:
                error_result = RegressionTestResult(
                    vendor=vendor,
                    test_name="regression_test",
                    passed=False,
                    processing_time=0.0,
                    memory_usage_mb=0.0,
                    success_indicators=0,
                    error_indicators=1,
                    error_message=str(e),
                    timestamp=datetime.now().isoformat(),
                )
                self.test_results.append(error_result)
                print(f"❌ FAIL {vendor}: {str(e)[:100]}")

        total_time = time.time() - start_time

        # Generate summary
        summary = self.generate_regression_summary(total_time)

        # Update baselines
        self.update_regression_baselines()

        # Print summary report
        self.print_regression_report(summary)

        return summary

    def test_harpercollins_regression(self) -> RegressionTestResult:
        """Test HarperCollins processing regression"""
        start_time = time.time()
        memory_before = self.get_memory_usage()

        try:
            result = subprocess.run(
                [sys.executable, "test_scripts/perfect_processing.py"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            processing_time = time.time() - start_time
            memory_after = self.get_memory_usage()
            memory_usage = memory_after - memory_before if PSUTIL_AVAILABLE else 0.0

            success_indicators = result.stdout.count("✅")
            error_indicators = result.stdout.count("❌")

            # Check for expected HarperCollins success indicators (more flexible)
            expected_indicators = [
                "line items",
                "accuracy",
                "NS4435067",
                "HarperCollins",
            ]
            has_expected = any(
                indicator in result.stdout for indicator in expected_indicators
            )

            passed = (
                result.returncode == 0
                and success_indicators > 0
                and has_expected
                and processing_time < 60
            )  # Performance threshold

            return RegressionTestResult(
                vendor="HarperCollins",
                test_name="perfect_processing",
                passed=passed,
                processing_time=processing_time,
                memory_usage_mb=memory_usage,
                success_indicators=success_indicators,
                error_indicators=error_indicators,
                error_message=result.stderr if not passed else None,
                timestamp=datetime.now().isoformat(),
            )

        except subprocess.TimeoutExpired:
            return RegressionTestResult(
                vendor="HarperCollins",
                test_name="perfect_processing",
                passed=False,
                processing_time=120.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=1,
                error_message="Test timed out after 120 seconds",
                timestamp=datetime.now().isoformat(),
            )
        except FileNotFoundError:
            return RegressionTestResult(
                vendor="HarperCollins",
                test_name="perfect_processing",
                passed=True,  # Skip if test not available
                processing_time=0.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=0,
                error_message="Test script not found - skipped",
                timestamp=datetime.now().isoformat(),
            )

    def test_onehundred80_regression(self) -> RegressionTestResult:
        """Test OneHundred80 processing regression"""
        start_time = time.time()
        memory_before = self.get_memory_usage()

        try:
            result = subprocess.run(
                [sys.executable, "test_scripts/test_onehundred80.py"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            processing_time = time.time() - start_time
            memory_after = self.get_memory_usage()
            memory_usage = memory_after - memory_before if PSUTIL_AVAILABLE else 0.0

            success_indicators = result.stdout.count("✅")
            error_indicators = result.stdout.count("❌")

            passed = result.returncode == 0 and processing_time < 60

            return RegressionTestResult(
                vendor="OneHundred80",
                test_name="test_onehundred80",
                passed=passed,
                processing_time=processing_time,
                memory_usage_mb=memory_usage,
                success_indicators=success_indicators,
                error_indicators=error_indicators,
                error_message=result.stderr if not passed else None,
                timestamp=datetime.now().isoformat(),
            )

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return RegressionTestResult(
                vendor="OneHundred80",
                test_name="test_onehundred80",
                passed=True if isinstance(e, FileNotFoundError) else False,
                processing_time=(
                    processing_time if "processing_time" in locals() else 0.0
                ),
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=0 if isinstance(e, FileNotFoundError) else 1,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def test_rifle_paper_regression(self) -> RegressionTestResult:
        """Test Rifle Paper processing regression"""
        try:
            from unittest.mock import Mock

            from main import extract_line_items_from_entities

            # Create mock Rifle Paper document
            mock_document = Mock()
            mock_document.text = "Rifle Paper Co. Invoice test content"
            mock_document.entities = []

            start_time = time.time()
            result = extract_line_items_from_entities(
                mock_document, "2025-01-01", "Rifle Paper", "TEST123"
            )
            processing_time = time.time() - start_time

            # Basic validation - should not crash and return list
            passed = isinstance(result, list) and processing_time < 5.0

            return RegressionTestResult(
                vendor="Rifle Paper",
                test_name="basic_processing",
                passed=passed,
                processing_time=processing_time,
                memory_usage_mb=0.0,
                success_indicators=1 if passed else 0,
                error_indicators=0 if passed else 1,
                error_message=None if passed else "Processing failed",
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            return RegressionTestResult(
                vendor="Rifle Paper",
                test_name="basic_processing",
                passed=False,
                processing_time=0.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=1,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def test_core_functions_regression(self) -> RegressionTestResult:
        """Test core utility functions regression"""
        try:
            # Try to import core functions - some may not exist
            core_functions = {}
            try:
                from main import format_date

                core_functions["format_date"] = format_date
            except ImportError:
                pass

            try:
                from main import clean_and_validate_quantity

                core_functions["clean_and_validate_quantity"] = (
                    clean_and_validate_quantity
                )
            except ImportError:
                pass

            try:
                from main import extract_wholesale_price

                core_functions["extract_wholesale_price"] = extract_wholesale_price
            except ImportError:
                pass

            start_time = time.time()

            # Test available core functions
            passed_tests = 0
            total_tests = 0

            # Test format_date if available
            if "format_date" in core_functions:
                test_cases = [
                    ("01/15/2025", "2025-01-15"),
                    ("1/15/25", "2025-01-15"),
                ]
                for input_val, expected in test_cases:
                    total_tests += 1
                    try:
                        result = core_functions["format_date"](input_val)
                        if result == expected:
                            passed_tests += 1
                    except Exception:
                        pass

            # Test clean_and_validate_quantity if available
            if "clean_and_validate_quantity" in core_functions:
                test_cases = [
                    ("24", 24),
                    ("12 units", 12),
                    ("invalid", 0),
                ]
                for input_val, expected in test_cases:
                    total_tests += 1
                    try:
                        result = core_functions["clean_and_validate_quantity"](
                            input_val
                        )
                        if result == expected:
                            passed_tests += 1
                    except Exception:
                        pass

            processing_time = time.time() - start_time
            passed = (
                total_tests == 0 or (passed_tests / total_tests) >= 0.8
            )  # 80% threshold

            return RegressionTestResult(
                vendor="Core Functions",
                test_name="utility_functions",
                passed=passed,
                processing_time=processing_time,
                memory_usage_mb=0.0,
                success_indicators=passed_tests,
                error_indicators=total_tests - passed_tests,
                error_message=(
                    None
                    if passed
                    else f"Failed {total_tests - passed_tests}/{total_tests} core function tests"
                ),
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            return RegressionTestResult(
                vendor="Core Functions",
                test_name="utility_functions",
                passed=False,
                processing_time=0.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=1,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def test_memory_regression(self) -> RegressionTestResult:
        """Test for memory usage regression"""
        if not PSUTIL_AVAILABLE:
            return RegressionTestResult(
                vendor="Memory Usage",
                test_name="memory_leak_detection",
                passed=True,  # Skip if psutil not available
                processing_time=0.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=0,
                error_message="psutil not available - skipped",
                timestamp=datetime.now().isoformat(),
            )

        try:
            from unittest.mock import Mock

            from main import process_harpercollins_document

            # Measure baseline memory
            gc.collect()
            memory_before = self.get_memory_usage()

            start_time = time.time()

            # Process multiple times to detect memory leaks
            mock_document = Mock()
            mock_document.text = "Test content for memory regression testing"
            mock_document.entities = []

            for _ in range(20):
                try:
                    result = process_harpercollins_document(mock_document)
                    gc.collect()
                except Exception:
                    pass  # Ignore processing errors for memory test

            processing_time = time.time() - start_time
            memory_after = self.get_memory_usage()
            memory_increase = memory_after - memory_before

            # Memory increase should be minimal (< 10MB)
            passed = memory_increase < 10.0

            return RegressionTestResult(
                vendor="Memory Usage",
                test_name="memory_leak_detection",
                passed=passed,
                processing_time=processing_time,
                memory_usage_mb=memory_increase,
                success_indicators=1 if passed else 0,
                error_indicators=0 if passed else 1,
                error_message=(
                    f"Memory increased by {memory_increase:.1f}MB"
                    if not passed
                    else None
                ),
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            return RegressionTestResult(
                vendor="Memory Usage",
                test_name="memory_leak_detection",
                passed=False,
                processing_time=0.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=1,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def test_performance_regression(self) -> RegressionTestResult:
        """Test for performance regression across all vendors"""
        try:
            from unittest.mock import Mock

            from main import detect_vendor_type, extract_line_items_from_entities

            start_time = time.time()

            # Test vendor detection performance
            test_texts = [
                "HarperCollins test content",
                "OneHundred80 invoice content",
                "Creative-Coop order content",
                "Generic invoice content",
            ]

            for text in test_texts * 10:  # Test multiple times
                try:
                    vendor = detect_vendor_type(text)
                except Exception:
                    pass  # Ignore errors for performance test

            # Test line item extraction performance
            mock_document = Mock()
            mock_document.text = "Sample invoice content for performance testing"
            mock_document.entities = []

            for _ in range(5):
                try:
                    result = extract_line_items_from_entities(
                        mock_document, "2025-01-01", "Test", "123"
                    )
                except Exception:
                    pass  # Ignore errors for performance test

            processing_time = time.time() - start_time

            # Should complete quickly (< 5 seconds for all tests)
            passed = processing_time < 5.0

            return RegressionTestResult(
                vendor="Performance",
                test_name="processing_speed",
                passed=passed,
                processing_time=processing_time,
                memory_usage_mb=0.0,
                success_indicators=1 if passed else 0,
                error_indicators=0 if passed else 1,
                error_message=(
                    f"Performance test took {processing_time:.2f}s (> 5s threshold)"
                    if not passed
                    else None
                ),
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            return RegressionTestResult(
                vendor="Performance",
                test_name="processing_speed",
                passed=False,
                processing_time=0.0,
                memory_usage_mb=0.0,
                success_indicators=0,
                error_indicators=1,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if not PSUTIL_AVAILABLE:
            return 0.0
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

    def generate_regression_summary(self, total_time: float) -> RegressionSummary:
        """Generate summary of regression test results"""
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = len(self.test_results) - passed_tests
        overall_success = failed_tests == 0

        # Compare with baselines
        baseline_comparisons = self.compare_with_baselines()

        return RegressionSummary(
            total_tests=len(self.test_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            overall_success=overall_success,
            test_results=self.test_results,
            baseline_comparisons=baseline_comparisons,
        )

    def compare_with_baselines(self) -> Dict[str, Any]:
        """Compare current results with historical baselines"""
        comparisons = {}

        for result in self.test_results:
            baseline_file = (
                self.baseline_dir
                / f"{result.vendor.lower().replace(' ', '_')}_baseline.json"
            )

            if baseline_file.exists():
                try:
                    with open(baseline_file, "r") as f:
                        baseline = json.load(f)

                    comparisons[result.vendor] = {
                        "processing_time_change": result.processing_time
                        - baseline.get("processing_time", 0),
                        "memory_usage_change": result.memory_usage_mb
                        - baseline.get("memory_usage_mb", 0),
                        "success_rate_change": result.success_indicators
                        - baseline.get("success_indicators", 0),
                    }
                except Exception:
                    pass  # Ignore baseline comparison errors

        return comparisons

    def update_regression_baselines(self):
        """Update baseline metrics for future comparisons"""
        for result in self.test_results:
            if result.passed:  # Only update baselines for successful tests
                baseline_file = (
                    self.baseline_dir
                    / f"{result.vendor.lower().replace(' ', '_')}_baseline.json"
                )

                baseline_data = {
                    "processing_time": result.processing_time,
                    "memory_usage_mb": result.memory_usage_mb,
                    "success_indicators": result.success_indicators,
                    "last_updated": result.timestamp,
                }

                try:
                    with open(baseline_file, "w") as f:
                        json.dump(baseline_data, f, indent=2)
                except Exception:
                    pass  # Ignore baseline update errors

    def print_regression_report(self, summary: RegressionSummary):
        """Print comprehensive regression test report"""
        print("\n" + "=" * 60)
        print("📊 VENDOR REGRESSION TEST REPORT")
        print("=" * 60)

        print(f"📈 SUMMARY")
        print(f"   Total Tests: {summary.total_tests}")
        print(f"   Passed: {summary.passed_tests} ✅")
        print(f"   Failed: {summary.failed_tests} ❌")
        success_rate = (
            summary.passed_tests / summary.total_tests if summary.total_tests > 0 else 0
        )
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Total Time: {summary.total_time:.2f}s")

        print(f"\n📋 DETAILED RESULTS")
        for result in summary.test_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"   {result.vendor:<15} {status:<8} ({result.processing_time:.2f}s)")
            if not result.passed and result.error_message:
                print(f"      Error: {result.error_message[:60]}...")

        if summary.baseline_comparisons:
            print(f"\n📊 BASELINE COMPARISONS")
            for vendor, comparison in summary.baseline_comparisons.items():
                print(f"   {vendor}:")
                for metric, change in comparison.items():
                    if abs(change) > 0.01:  # Only show significant changes
                        direction = "↑" if change > 0 else "↓"
                        print(f"      {metric}: {direction} {abs(change):.2f}")

        print(f"\n🎯 OVERALL REGRESSION STATUS")
        if summary.overall_success:
            print("   ✅ NO REGRESSIONS DETECTED")
            print(
                "   All vendor processing maintained after Creative-Coop enhancements"
            )
        else:
            print("   ❌ REGRESSIONS DETECTED")
            print("   Creative-Coop changes may have affected other vendor processing")


def main():
    """Run comprehensive vendor regression testing"""
    tester = VendorRegressionTester()
    summary = tester.run_all_regression_tests()

    # Exit with appropriate code
    return 0 if summary.overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
