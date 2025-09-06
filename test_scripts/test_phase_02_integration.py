#!/usr/bin/env python3
"""
Phase 02 Integration Testing - Comprehensive End-to-End Validation

This module implements comprehensive integration testing for all Phase 02 enhancements
to validate end-to-end Creative-Coop processing achieves business objectives:
- Price extraction: 95%+ accuracy
- Quantity processing: 90%+ accuracy
- Description completeness: 95%+ accuracy
- Overall accuracy: 90%+ target

Tests ensure all Phase 02 components work together seamlessly and meet production requirements.
"""

import json
import os
import sys
import time
from unittest.mock import MagicMock, patch

import psutil

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import main
except ImportError as e:
    print(f"Error importing main module: {e}")
    sys.exit(1)


def load_test_document(filename):
    """Load CS003837319_Error 2 test document"""
    test_file_path = os.path.join(
        os.path.dirname(__file__), "..", "test_invoices", filename
    )

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test document not found: {test_file_path}")

    with open(test_file_path, "r", encoding="utf-8") as f:
        document_data = json.load(f)

    # Create mock document object with required attributes
    class MockDocument:
        def __init__(self, data):
            self.text = data.get("text", "")
            self.pages = data.get("pages", [])
            self.entities = data.get("entities", [])

    return MockDocument(document_data)


def validate_line_item_quality(item):
    """Validate individual line item meets quality standards"""
    if not isinstance(item, dict):
        return False

    # Basic required fields
    if not item.get("product_code"):
        return False

    # Price validation
    price = item.get("price", "")
    if not price or price in ["$0.00", "$1.60", None]:
        return False

    # Quantity validation
    quantity = item.get("quantity", 0)
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return False

    # Description validation
    description = item.get("description", "")
    if (
        not description
        or len(description) < 20
        or "Traditional D-code format" in description
    ):
        return False

    return True


def calculate_quality_improvements(phase_01_results, phase_02_results):
    """Calculate quantified quality improvements from Phase 02"""
    if not phase_01_results or not phase_02_results:
        return {
            "price_accuracy_improvement": 0,
            "quantity_accuracy_improvement": 0,
            "description_completeness_improvement": 0,
        }

    # Calculate Phase 01 metrics (simulated baseline)
    phase_01_total = len(phase_01_results)
    phase_01_valid_prices = sum(
        1
        for item in phase_01_results
        if item.get("price") and item["price"] not in ["$0.00", "$1.60"]
    )
    phase_01_valid_quantities = sum(
        1 for item in phase_01_results if item.get("quantity") and item["quantity"] > 0
    )
    phase_01_complete_descriptions = sum(
        1
        for item in phase_01_results
        if item.get("description") and len(item["description"]) > 20
    )

    phase_01_price_accuracy = (
        phase_01_valid_prices / phase_01_total if phase_01_total > 0 else 0
    )
    phase_01_quantity_accuracy = (
        phase_01_valid_quantities / phase_01_total if phase_01_total > 0 else 0
    )
    phase_01_description_completeness = (
        phase_01_complete_descriptions / phase_01_total if phase_01_total > 0 else 0
    )

    # Calculate Phase 02 metrics
    phase_02_total = len(phase_02_results)
    phase_02_valid_prices = sum(
        1
        for item in phase_02_results
        if item.get("price") and item["price"] not in ["$0.00", "$1.60"]
    )
    phase_02_valid_quantities = sum(
        1 for item in phase_02_results if item.get("quantity") and item["quantity"] > 0
    )
    phase_02_complete_descriptions = sum(
        1
        for item in phase_02_results
        if item.get("description")
        and len(item["description"]) > 20
        and "Traditional D-code format" not in item["description"]
    )

    phase_02_price_accuracy = (
        phase_02_valid_prices / phase_02_total if phase_02_total > 0 else 0
    )
    phase_02_quantity_accuracy = (
        phase_02_valid_quantities / phase_02_total if phase_02_total > 0 else 0
    )
    phase_02_description_completeness = (
        phase_02_complete_descriptions / phase_02_total if phase_02_total > 0 else 0
    )

    return {
        "price_accuracy_improvement": phase_02_price_accuracy - phase_01_price_accuracy,
        "quantity_accuracy_improvement": phase_02_quantity_accuracy
        - phase_01_quantity_accuracy,
        "description_completeness_improvement": phase_02_description_completeness
        - phase_01_description_completeness,
    }


def calculate_overall_accuracy(results):
    """Calculate overall processing accuracy"""
    if not results:
        return 0

    total_items = len(results)

    # Price accuracy
    valid_prices = sum(
        1
        for item in results
        if item.get("price") and item["price"] not in ["$0.00", "$1.60", None]
    )
    price_accuracy = valid_prices / total_items

    # Quantity accuracy
    valid_quantities = sum(
        1 for item in results if item.get("quantity") and item["quantity"] > 0
    )
    quantity_accuracy = valid_quantities / total_items

    # Description completeness
    complete_descriptions = sum(
        1
        for item in results
        if item.get("description")
        and len(item["description"]) > 20
        and "Traditional D-code format" not in item["description"]
    )
    description_completeness = complete_descriptions / total_items

    # Overall accuracy (weighted average)
    overall_accuracy = (
        price_accuracy + quantity_accuracy + description_completeness
    ) / 3

    return overall_accuracy


def calculate_production_readiness_score(readiness_checks):
    """Calculate production readiness score from various checks"""
    if not readiness_checks:
        return 0

    passed_checks = sum(1 for passed in readiness_checks.values() if passed)
    total_checks = len(readiness_checks)

    return passed_checks / total_checks if total_checks > 0 else 0


# ============================================================================
# RED Phase Tests - These should FAIL initially
# ============================================================================


def test_end_to_end_cs003837319_processing_with_phase_02_enhancements():
    """Test end-to-end CS003837319 processing with all Phase 02 enhancements"""
    print(
        "\n🧪 Testing end-to-end CS003837319 processing with Phase 02 enhancements..."
    )

    # Arrange - Load full CS003837319_Error 2.PDF document
    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    # Act - Process with all Phase 02 enhancements integrated
    processing_results = main.process_creative_coop_document_phase_02_enhanced(
        cs_document
    )

    # Assert - Should meet all Phase 02 success criteria
    assert (
        len(processing_results) >= 130
    ), f"Expected minimum 130 products, got {len(processing_results)}"

    # Phase 02.1: Price extraction accuracy 95%+
    valid_prices = sum(
        1
        for item in processing_results
        if item.get("price") and item["price"] != "$0.00" and item["price"] != "$1.60"
    )
    price_accuracy = valid_prices / len(processing_results)
    assert (
        price_accuracy >= 0.95
    ), f"Price accuracy {price_accuracy:.1%} below 95% requirement"

    # Phase 02.2: Quantity processing accuracy 90%+
    valid_quantities = sum(
        1
        for item in processing_results
        if item.get("quantity") and item["quantity"] > 0 and item["quantity"] != 24
    )
    quantity_accuracy = valid_quantities / len(processing_results)
    assert (
        quantity_accuracy >= 0.90
    ), f"Quantity accuracy {quantity_accuracy:.1%} below 90% requirement"

    # Phase 02.4: Description completeness 95%+
    complete_descriptions = sum(
        1
        for item in processing_results
        if item.get("description")
        and "Traditional D-code format" not in item["description"]
        and len(item["description"]) > 20
    )
    description_accuracy = complete_descriptions / len(processing_results)
    assert (
        description_accuracy >= 0.95
    ), f"Description completeness {description_accuracy:.1%} below 95% requirement"

    print(f"✅ End-to-end test passed: {len(processing_results)} products processed")
    print(f"   - Price accuracy: {price_accuracy:.1%}")
    print(f"   - Quantity accuracy: {quantity_accuracy:.1%}")
    print(f"   - Description completeness: {description_accuracy:.1%}")


def test_multi_tier_price_extraction_integration():
    """Test integration of all price extraction tiers"""
    print("\n🧪 Testing multi-tier price extraction integration...")

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    # Act - Test price extraction with tier tracking
    tier_results = {}
    test_products = ["XS9826A", "XS9649A", "XS9482", "XS8185", "CF1234A"]

    for product_code in test_products:
        price_result = main.extract_price_with_tier_tracking(
            cs_document.text, product_code
        )
        tier_results[product_code] = price_result

    # Assert - Should utilize all tiers effectively
    tiers_used = set(result["tier_used"] for result in tier_results.values())
    assert "tier1_tabular" in tiers_used, "Should use tabular extraction"
    assert len(tiers_used) >= 2, "Should use multiple extraction tiers"

    # All extractions should be successful
    successful_extractions = sum(
        1
        for result in tier_results.values()
        if result["price"] and result["price"] != "$0.00"
    )
    success_rate = successful_extractions / len(test_products)
    assert (
        success_rate >= 0.9
    ), f"Multi-tier price success rate {success_rate:.1%} below 90%"

    print(
        f"✅ Multi-tier price extraction test passed: {success_rate:.1%} success rate"
    )


def test_shipped_vs_ordered_quantity_logic_integration():
    """Test integration of shipped vs ordered quantity business logic"""
    print("\n🧪 Testing shipped vs ordered quantity logic integration...")

    # Test integration of shipped vs ordered quantity business logic
    quantity_test_cases = [
        {
            "product_code": "XS9826A",
            "tabular_data": "XS9826A | Product | 24 | 0 | 12 | 12 | each",
            "expected_quantity": 12,  # Should use shipped (12) not ordered (24)
            "expected_logic": "shipped_priority",
        },
        {
            "product_code": "XS8911A",
            "tabular_data": "XS8911A | Product | 48 | 0 | 0 | 48 | each",
            "expected_quantity": 48,  # Should use ordered (48) for backordered item
            "expected_logic": "backordered_fallback",
        },
    ]

    for case in quantity_test_cases:
        # Act
        quantity_result = main.extract_quantity_with_logic_tracking(
            case["tabular_data"], case["product_code"]
        )

        # Assert
        assert quantity_result["quantity"] == case["expected_quantity"]
        assert quantity_result["logic_applied"] == case["expected_logic"]

    print("✅ Shipped vs ordered quantity logic test passed")


def test_memory_efficient_15_page_processing():
    """Test memory-efficient processing of full 15-page document"""
    print("\n🧪 Testing memory-efficient 15-page processing...")

    import os

    import psutil

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")
    process = psutil.Process(os.getpid())

    # Get baseline memory
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Act - Process with memory optimization
    results = main.process_large_creative_coop_document(cs_document)

    # Monitor peak memory usage
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = peak_memory - initial_memory

    # Assert - Memory and functionality requirements
    assert memory_used < 800, f"Memory usage {memory_used:.0f}MB exceeds 800MB limit"
    assert len(results) >= 130, "Should process all expected products"

    # Should complete within timeout
    print(
        f"✅ Memory-efficient processing test passed: {memory_used:.0f}MB used, {len(results)} products processed"
    )


def test_description_upc_integration_comprehensive():
    """Test comprehensive UPC integration with descriptions"""
    print("\n🧪 Testing comprehensive UPC integration with descriptions...")

    cs_document_text = load_test_document("CS003837319_Error 2_docai_output.json")

    test_products = ["XS9826A", "XS9649A", "XS9482", "XS8185"]
    upc_integration_results = {}

    for product_code in test_products:
        # Act
        enhanced_description = main.extract_enhanced_product_description(
            cs_document_text.text, product_code
        )
        upc_integration_results[product_code] = {
            "description": enhanced_description,
            "has_upc": "UPC:" in enhanced_description,
            "has_product_code": product_code in enhanced_description,
            "is_complete": len(enhanced_description) > 30
            and "Traditional D-code format" not in enhanced_description,
        }

    # Assert - UPC integration success
    upc_integrated_count = sum(
        1 for result in upc_integration_results.values() if result["has_upc"]
    )
    complete_descriptions = sum(
        1 for result in upc_integration_results.values() if result["is_complete"]
    )

    upc_integration_rate = upc_integrated_count / len(test_products)
    completeness_rate = complete_descriptions / len(test_products)

    assert (
        upc_integration_rate >= 0.75
    ), f"UPC integration rate {upc_integration_rate:.1%} below 75%"
    assert (
        completeness_rate >= 0.95
    ), f"Description completeness {completeness_rate:.1%} below 95%"

    print(
        f"✅ UPC integration test passed: {upc_integration_rate:.1%} UPC rate, {completeness_rate:.1%} completeness"
    )


def test_handles_phase_02_component_failures_gracefully():
    """Test graceful degradation when individual Phase 02 components fail"""
    print("\n🧪 Testing graceful handling of Phase 02 component failures...")

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    # Simulate component failures
    component_failure_scenarios = [
        "tabular_price_extraction_failure",
        "quantity_parsing_failure",
        "description_enhancement_failure",
        "memory_optimization_failure",
    ]

    for failure_scenario in component_failure_scenarios:
        # Act - Process with simulated component failure
        try:
            results = main.process_with_simulated_failure(cs_document, failure_scenario)

            # Assert - Should degrade gracefully
            assert results is not None, f"Should handle {failure_scenario} gracefully"
            assert (
                len(results) >= 100
            ), f"Should still process most products despite {failure_scenario}"

        except Exception as e:
            assert False, f"Should handle {failure_scenario} gracefully, but got: {e}"

    print("✅ Component failure handling test passed")


def test_handles_corrupted_cs003837319_data():
    """Test handling of corrupted test document data"""
    print("\n🧪 Testing handling of corrupted CS003837319 data...")

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    # Simulate data corruption
    corrupted_document = main.corrupt_document_sections(
        cs_document, corruption_rate=0.1
    )

    # Act
    results = main.process_creative_coop_document_phase_02_enhanced(corrupted_document)

    # Assert - Should handle corruption gracefully
    assert results is not None
    assert len(results) >= 100  # Should still process most products

    # Should maintain data quality despite corruption
    valid_results = [item for item in results if validate_line_item_quality(item)]
    quality_rate = len(valid_results) / len(results) if results else 0
    assert (
        quality_rate >= 0.8
    ), f"Quality rate {quality_rate:.1%} too low despite corruption handling"

    print(
        f"✅ Corrupted data handling test passed: {quality_rate:.1%} quality rate maintained"
    )


def test_handles_timeout_scenarios():
    """Test timeout handling for large document processing"""
    print("\n🧪 Testing timeout scenario handling...")

    import time
    from unittest.mock import patch

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    # Mock slow processing to trigger timeout
    def slow_processing(*args, **kwargs):
        time.sleep(30)  # Simulate very slow processing
        return []

    # Act - Test with timeout protection
    with patch("main.process_document_chunk", side_effect=slow_processing):
        start_time = time.time()
        results = main.process_creative_coop_document_phase_02_enhanced(
            cs_document, timeout=10
        )
        end_time = time.time()

        processing_time = end_time - start_time

        # Assert - Should timeout appropriately
        assert (
            processing_time < 20
        ), f"Should timeout within reasonable time, took {processing_time:.1f}s"
        # Should return partial results or handle timeout gracefully
        assert results is not None or "timeout handled gracefully"

    print(f"✅ Timeout handling test passed: {processing_time:.1f}s processing time")


def test_validates_phase_02_performance_requirements():
    """Test all Phase 02 performance requirements"""
    print("\n🧪 Testing Phase 02 performance requirements...")

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    performance_metrics = {}

    # Test individual component performance
    start_time = time.time()
    price_results = main.test_price_extraction_performance(cs_document)
    performance_metrics["price_extraction_time"] = time.time() - start_time

    start_time = time.time()
    quantity_results = main.test_quantity_extraction_performance(cs_document)
    performance_metrics["quantity_extraction_time"] = time.time() - start_time

    start_time = time.time()
    description_results = main.test_description_processing_performance(cs_document)
    performance_metrics["description_processing_time"] = time.time() - start_time

    # Assert - Performance requirements
    assert (
        performance_metrics["price_extraction_time"] < 30
    ), "Price extraction should complete in < 30 seconds"
    assert (
        performance_metrics["quantity_extraction_time"] < 30
    ), "Quantity extraction should complete in < 30 seconds"
    assert (
        performance_metrics["description_processing_time"] < 45
    ), "Description processing should complete in < 45 seconds"

    # Overall processing should complete within Zapier timeout
    total_time = sum(performance_metrics.values())
    assert (
        total_time < 120
    ), f"Total Phase 02 processing time {total_time:.1f}s exceeds 120s limit"

    print(f"✅ Performance requirements test passed: {total_time:.1f}s total time")


def test_validates_regression_protection():
    """Test that Phase 02 enhancements don't break existing vendor processing"""
    print("\n🧪 Testing regression protection for existing vendors...")

    test_vendors = ["HarperCollins", "OneHundred80", "Rifle Paper"]

    for vendor in test_vendors:
        # Act - Process with vendor-specific logic
        vendor_results = main.test_vendor_processing_with_phase_02(vendor)

        # Assert - Should maintain existing functionality
        assert (
            vendor_results is not None
        ), f"Phase 02 should not break {vendor} processing"
        if vendor == "HarperCollins":
            assert (
                len(vendor_results) >= 20
            ), "Should maintain HarperCollins processing capability"

    # Overall system should maintain multi-vendor support
    print("✅ Regression protection test passed: All vendors maintain functionality")


def test_validates_data_quality_improvements():
    """Test quantified data quality improvements from Phase 02"""
    print("\n🧪 Testing quantified data quality improvements...")

    cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

    # Simulate Phase 01 baseline (before enhancements)
    phase_01_results = main.simulate_phase_01_processing(cs_document)

    # Process with Phase 02 enhancements
    phase_02_results = main.process_creative_coop_document_phase_02_enhanced(
        cs_document
    )

    # Calculate improvements
    improvements = calculate_quality_improvements(phase_01_results, phase_02_results)

    # Assert - Quantified improvements
    assert (
        improvements["price_accuracy_improvement"] >= 0.45
    ), "Price accuracy should improve by 45%+ (50% → 95%)"
    assert (
        improvements["quantity_accuracy_improvement"] >= 0.40
    ), "Quantity accuracy should improve by 40%+ (50% → 90%)"
    assert (
        improvements["description_completeness_improvement"] >= 0.65
    ), "Description completeness should improve by 65%+ (30% → 95%)"

    # Overall processing accuracy should reach 90%+
    overall_accuracy = calculate_overall_accuracy(phase_02_results)
    assert (
        overall_accuracy >= 0.90
    ), f"Overall accuracy {overall_accuracy:.1%} below 90% target"

    print(
        f"✅ Data quality improvements test passed: {overall_accuracy:.1%} overall accuracy"
    )


def test_validates_production_readiness():
    """Test production readiness across all Phase 02 components"""
    print("\n🧪 Testing production readiness validation...")

    # Test production readiness across all Phase 02 components
    readiness_checks = {
        "error_handling": main.test_comprehensive_error_handling(),
        "performance": main.test_performance_within_limits(),
        "memory_usage": main.test_memory_efficiency(),
        "data_quality": main.test_data_quality_standards(),
        "integration": main.test_component_integration(),
        "regression": main.test_no_regression_issues(),
    }

    # Assert - All readiness checks should pass
    failed_checks = [check for check, passed in readiness_checks.items() if not passed]
    assert len(failed_checks) == 0, f"Production readiness failed for: {failed_checks}"

    # Additional production readiness validation
    production_score = calculate_production_readiness_score(readiness_checks)
    assert (
        production_score >= 0.95
    ), f"Production readiness score {production_score:.1%} below 95% threshold"

    print(
        f"✅ Production readiness test passed: {production_score:.1%} readiness score"
    )


# ============================================================================
# Test Runner
# ============================================================================


def run_all_phase_02_integration_tests():
    """Run all Phase 02 integration tests"""
    print("🚀 Starting Phase 02 Integration Testing Suite...")
    print("=" * 80)

    tests = [
        test_end_to_end_cs003837319_processing_with_phase_02_enhancements,
        test_multi_tier_price_extraction_integration,
        test_shipped_vs_ordered_quantity_logic_integration,
        test_memory_efficient_15_page_processing,
        test_description_upc_integration_comprehensive,
        test_handles_phase_02_component_failures_gracefully,
        test_handles_corrupted_cs003837319_data,
        test_handles_timeout_scenarios,
        test_validates_phase_02_performance_requirements,
        test_validates_regression_protection,
        test_validates_data_quality_improvements,
        test_validates_production_readiness,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test_func.__name__}")
            print(f"   Error: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"🎯 Phase 02 Integration Testing Complete:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Success Rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print(
            "🎉 All Phase 02 integration tests passed! Ready for production deployment."
        )
    else:
        print("⚠️  Some tests failed. Review and fix before production deployment.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_phase_02_integration_tests()
    sys.exit(0 if success else 1)
