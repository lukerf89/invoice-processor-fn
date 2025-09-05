#!/usr/bin/env python3
"""
Task 07 - RED Phase: Failing tests for multi-tier quantity extraction system
Creative-Coop integration with existing pattern-based extraction

This implements TDD RED phase with comprehensive failing tests for the new
multi-tier fallback system that integrates tabular parsing with existing logic.
"""

import time
from unittest.mock import Mock, patch

import pytest


def test_tier1_tabular_extraction_success():
    """Test Tier 1 (tabular) extraction succeeds and skips lower tiers"""
    # Arrange - tabular format should be detected and processed
    tabular_text = (
        'XS9826A 191009727774 6"H Metal Ballerina 24 0 0 24 each 2.00 1.60 38.40'
    )

    # Import the function we need to implement
    from main import extract_creative_coop_quantity_improved

    # Act
    result = extract_creative_coop_quantity_improved(tabular_text, "XS9826A")

    # Assert
    assert result == 24


def test_tier2_pattern_fallback_when_tabular_fails():
    """Test Tier 2 (pattern-based) fallback when tabular parsing fails"""
    # Arrange - old Creative-Coop format that tabular parser can't handle
    pattern_text = "DF6802 8 0 lo each $12.50 $100.00 description continues..."

    from main import extract_creative_coop_quantity_improved

    # Act
    result = extract_creative_coop_quantity_improved(pattern_text, "DF6802")

    # Assert
    assert result == 8  # Should extract from "8 0 lo each" pattern


def test_tier3_context_fallback_when_patterns_fail():
    """Test Tier 3 (context-aware) fallback when both higher tiers fail"""
    # Arrange - complex format requiring context analysis
    context_text = """
    Product: XS9826A
    Description: 6"H Metal Ballerina Ornament
    Ordered: 24 units
    Status: Available
    """

    from main import extract_creative_coop_quantity_improved

    # Act
    result = extract_creative_coop_quantity_improved(context_text, "XS9826A")

    # Assert
    assert result == 24  # Should extract from "Ordered: 24 units"


def test_all_tiers_fail_returns_none():
    """Test that None is returned when all tiers fail"""
    # Arrange - text with no extractable quantity
    no_quantity_text = "XS9826A Some description without any numbers"

    from main import extract_creative_coop_quantity_improved

    # Act
    result = extract_creative_coop_quantity_improved(no_quantity_text, "XS9826A")

    # Assert
    assert result is None


def test_tier_performance_early_exit():
    """Test that successful tier exits early without trying lower tiers"""
    # Arrange
    mixed_text = """
    XS9826A 191009727774 Ballerina 24 0 0 24 each 2.00  # Tabular format
    DF6802 8 0 lo each $12.50  # Pattern format
    """

    from main import extract_creative_coop_quantity_improved

    # Mock lower tiers to track if they're called
    with patch("main.extract_quantity_from_patterns") as mock_patterns:
        with patch("main.extract_quantity_from_context") as mock_context:
            # Act
            result = extract_creative_coop_quantity_improved(mixed_text, "XS9826A")

            # Assert
            assert result == 24
            # Lower tiers should not be called since tabular succeeded
            mock_patterns.assert_not_called()
            mock_context.assert_not_called()


def test_backward_compatibility_existing_invoices():
    """Test that existing D-code Creative-Coop invoices still work"""
    # Arrange - existing working format from previous invoices
    existing_format = """
    DF6802 8 0 lo each $12.50 $100.00
    ST1234 6 0 Set $8.00 $48.00
    """

    from main import extract_creative_coop_quantity_improved

    # Act & Assert - both should work via pattern fallback
    assert extract_creative_coop_quantity_improved(existing_format, "DF6802") == 8
    assert extract_creative_coop_quantity_improved(existing_format, "ST1234") == 6


def test_cs_error2_specific_products():
    """Test specific products from CS003837319_Error 2.PDF"""
    cs_error2_sample = """
    XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
    XS8911A 191009710615 4-3/4"L x 3-1/2"W x 10"H Metal 12 0 0 0 each 10.00 8.00 0.00
    XS9482 191009714712 8.25"H Wood Shoe Ornament 12 0 0 12 each 3.50 2.80 33.60
    """

    from main import extract_creative_coop_quantity_improved

    # Act & Assert
    assert extract_creative_coop_quantity_improved(cs_error2_sample, "XS9826A") == 24
    assert extract_creative_coop_quantity_improved(cs_error2_sample, "XS8911A") == 12
    assert extract_creative_coop_quantity_improved(cs_error2_sample, "XS9482") == 12


def test_integration_with_process_creative_coop_document():
    """Test integration with main Creative-Coop processing function"""
    # This test ensures the new quantity extraction works with the full pipeline
    from main import process_creative_coop_document

    # Create a mock document
    class MockEntity:
        def __init__(self, entity_type, mention_text):
            self.type_ = entity_type
            self.mention_text = mention_text
            self.confidence = 0.9
            self.properties = []

    class MockDocument:
        def __init__(self):
            self.text = """
            XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
            """
            self.entities = [
                MockEntity("line_item", 'XS9826A 191009727774 6"H Metal Ballerina'),
                MockEntity("vendor_name", "Creative-Coop"),
                MockEntity("invoice_id", "CS003837319"),
                MockEntity("invoice_date", "1/17/2025"),
            ]

    document = MockDocument()

    # This should use the new multi-tier extraction
    rows = process_creative_coop_document(document)

    # Should extract at least one row with quantity
    assert len(rows) > 0
    # Verify the row contains expected data structure
    assert len(rows[0]) == 6  # B:G format


def test_tier_logging_and_debugging():
    """Test that tier selection is logged for debugging"""
    import io
    import sys
    from contextlib import redirect_stdout

    from main import extract_creative_coop_quantity_improved

    # Capture output
    log_output = io.StringIO()

    tabular_text = (
        'XS9826A 191009727774 6"H Metal Ballerina 24 0 0 24 each 2.00 1.60 38.40'
    )

    with redirect_stdout(log_output):
        result = extract_creative_coop_quantity_improved(tabular_text, "XS9826A")

    # Should log which tier was used
    log_content = log_output.getvalue()
    assert "Tier" in log_content
    assert result == 24


def test_performance_multi_tier_overhead():
    """Test that multi-tier approach doesn't add significant overhead"""
    from main import extract_creative_coop_quantity_improved

    # Test data that should hit Tier 1 (tabular)
    tabular_text = (
        'XS9826A 191009727774 6"H Metal Ballerina 24 0 0 24 each 2.00 1.60 38.40'
    )

    # Measure processing time
    times = []
    for _ in range(10):
        start_time = time.time()
        result = extract_creative_coop_quantity_improved(tabular_text, "XS9826A")
        end_time = time.time()
        times.append(end_time - start_time)

    avg_time = sum(times) / len(times)
    max_time = max(times)

    print(f"Multi-tier average time: {avg_time:.4f}s")
    print(f"Multi-tier max time: {max_time:.4f}s")

    # Should be fast (under 10ms average)
    assert avg_time < 0.01, f"Multi-tier processing too slow: {avg_time:.4f}s"
    assert result == 24


def test_error_handling_graceful_degradation():
    """Test graceful error handling when tiers fail"""
    from main import extract_creative_coop_quantity_improved

    # Test with corrupted data that might cause exceptions
    corrupted_data = [
        None,  # None input
        "",  # Empty string
        "XS9826A" + "\x00" * 100,  # Binary data
        "XS9826A " * 1000,  # Very long repetitive text
    ]

    for data in corrupted_data:
        try:
            result = extract_creative_coop_quantity_improved(data, "XS9826A")
            # Should return None gracefully, not crash
            assert result is None
        except Exception as e:
            pytest.fail(f"Should handle corrupted data gracefully: {e}")


def test_existing_function_compatibility():
    """Test that existing extract_creative_coop_quantity still works"""
    from main import extract_creative_coop_quantity

    # Test existing function with known patterns
    existing_pattern = "DF6802 8 0 lo each $12.50 $100.00"

    # Should still return string (existing behavior)
    result = extract_creative_coop_quantity(existing_pattern, "DF6802")
    assert result == "8"  # Note: existing function returns string


if __name__ == "__main__":
    # Run specific test to verify RED phase (should fail)
    print("🔴 Running Task 07 RED Phase Tests - Should FAIL until GREEN implementation")
    print("=" * 70)

    try:
        test_tier1_tabular_extraction_success()
        print("❌ Tier 1 test should have failed (function not implemented)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Tier 1 test failed as expected - {e}")

    try:
        test_tier2_pattern_fallback_when_tabular_fails()
        print("❌ Tier 2 test should have failed (function not implemented)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Tier 2 test failed as expected - {e}")

    try:
        test_backward_compatibility_existing_invoices()
        print(
            "❌ Backward compatibility test should have failed (function not implemented)"
        )
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Backward compatibility test failed as expected - {e}")

    print(
        "\n🎯 Task 07 RED Phase Complete: All tests should fail until GREEN implementation"
    )
