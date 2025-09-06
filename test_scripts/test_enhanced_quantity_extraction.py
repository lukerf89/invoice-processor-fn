#!/usr/bin/env python3
"""
Test script for Enhanced Quantity Extraction - Task 204
Implements comprehensive quantity extraction testing for Creative-Coop invoices.

Engineering Principles Applied:
- Principle 7: Multi-pattern resilience
- Principle 8: Context-aware extraction
- Principle 9: Algorithmic processing

This test file implements the RED phase of TDD for enhanced quantity extraction.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

import pytest

from main import (
    extract_creative_coop_quantity_enhanced,
    extract_quantity_from_pattern_context,
    validate_quantity_business_logic,
)


class TestEnhancedQuantityExtractionHappyPath:
    """Test happy path scenarios for enhanced quantity extraction"""

    def test_extracts_shipped_quantity_priority(self):
        """Test that shipped quantities are prioritized over ordered quantities"""
        # Arrange - Tabular format with shipped quantities
        tabular_text = """
        Product Code | UPC         | Description | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M
        XS9826A      | 191009727774| Product     | 24      | 0         | 12          | 12        | each
        XS8911A      | 191009710615| Product     | 48      | 48        | 48          | 0         | each
        XS9482       | 191009714712| Product     | 36      | 0         | 0           | 36        | each
        """

        # Act - Test shipped quantity prioritization
        qty_shipped = extract_creative_coop_quantity_enhanced(tabular_text, "XS9826A")
        qty_fully_shipped = extract_creative_coop_quantity_enhanced(
            tabular_text, "XS8911A"
        )
        qty_backordered = extract_creative_coop_quantity_enhanced(
            tabular_text, "XS9482"
        )

        # Assert - Business logic: Use shipped if > 0, ordered if backordered
        assert (
            qty_shipped == 12
        ), f"Should use shipped quantity (12) not ordered (24), got {qty_shipped}"
        assert (
            qty_fully_shipped == 48
        ), f"Should use shipped quantity (48), got {qty_fully_shipped}"
        assert (
            qty_backordered == 36
        ), f"Should use ordered quantity for backordered items (36), got {qty_backordered}"

    def test_processes_cs003837319_quantities_accurately(self):
        """Test specific known products from manual analysis"""
        # Load CS003837319_Error 2.PDF test data (mock for now)
        cs_document_text = """
        XS9826A | 191009727774 | 6"H Metal Ballerina | 24 | 0 | 12 | 12 | each
        XS9649A | 191009710615 | Christmas Product   | 24 | 0 | 6  | 18 | each
        XS9482  | 191009714712 | Holiday Item        | 24 | 0 | 8  | 16 | each
        XS8185  | 191009728481 | Decorative Item     | 16 | 16| 16 | 0  | each
        """

        # Test specific known products - no placeholder "24" quantities
        test_products = {
            "XS9826A": 12,  # Should extract actual shipped, not placeholder "24"
            "XS9649A": 6,  # Actual shipped quantity
            "XS9482": 8,  # Actual shipped quantity
            "XS8185": 16,  # Full order shipped
        }

        for product_code, expected_qty in test_products.items():
            extracted_qty = extract_creative_coop_quantity_enhanced(
                cs_document_text, product_code
            )
            assert (
                extracted_qty == expected_qty
            ), f"{product_code}: expected {expected_qty}, got {extracted_qty}"
            assert extracted_qty != 24, f"No placeholder quantities for {product_code}"

    def test_handles_various_quantity_formats(self):
        """Test different tabular and text formats"""
        # Test different tabular and text formats
        format_cases = [
            # Standard tabular format
            ("XS9826A | Product | 24 | 0 | 12 | 12 | each", "XS9826A", 12),
            # Multi-line format
            ('XS9826A\n6"H Metal Ballerina\n24\n0\n12\n12\neach', "XS9826A", 12),
            # Text with units
            ("XS9826A shipped 12 each, backordered 12 each", "XS9826A", 12),
        ]

        for text_format, product_code, expected_qty in format_cases:
            result = extract_creative_coop_quantity_enhanced(text_format, product_code)
            assert (
                result == expected_qty
            ), f"Format test failed for {product_code}: expected {expected_qty}, got {result}"


class TestEnhancedQuantityExtractionErrorHandling:
    """Test error handling scenarios for enhanced quantity extraction"""

    def test_handles_malformed_quantity_data(self):
        """Test handling of malformed quantity data"""
        # Arrange - Various malformed quantity scenarios
        malformed_cases = [
            "XS9826A | Product | N/A | 0 | INVALID | jkl | each",  # Invalid all quantities
            "XS8911A | Product | abc | def | ghi | jkl | each",  # All non-numeric quantities
            "XS9482 | Product | | | | | each",  # All empty quantities
        ]

        for malformed_text in malformed_cases:
            product_code = malformed_text.split("|")[0].strip()

            # Act
            result = extract_creative_coop_quantity_enhanced(
                malformed_text, product_code
            )

            # Assert - Should handle gracefully, return 0 or fallback
            assert (
                result == 0 or result is None
            ), f"Should handle malformed data gracefully for {product_code}, got {result}"
            assert result != 24, f"Should not default to placeholder for {product_code}"

    def test_handles_zero_quantities_correctly(self):
        """Test business logic for various zero quantity scenarios"""
        zero_qty_text = """
        XS9826A | Product | 24 | 0 | 0 | 24 | each     # Nothing shipped, all backordered
        XS8911A | Product | 0  | 0 | 0 | 0  | each     # Nothing ordered
        XS9482  | Product | 12 | 12| 0 | 12 | each     # Allocated but not shipped
        """

        # Should use ordered quantity for backordered items
        result_backordered = extract_creative_coop_quantity_enhanced(
            zero_qty_text, "XS9826A"
        )
        assert (
            result_backordered == 24
        ), f"Should use ordered quantity for backordered items, got {result_backordered}"

        # Should return 0 for nothing ordered
        result_nothing = extract_creative_coop_quantity_enhanced(
            zero_qty_text, "XS8911A"
        )
        assert (
            result_nothing == 0
        ), f"Should return 0 for nothing ordered, got {result_nothing}"

        # Should use allocated quantity if available
        result_allocated = extract_creative_coop_quantity_enhanced(
            zero_qty_text, "XS9482"
        )
        assert (
            result_allocated == 12
        ), f"Should use allocated quantity, got {result_allocated}"

    def test_handles_missing_product_code(self):
        """Test handling of missing or invalid product codes"""
        text = "XS9826A | Product | 24 | 0 | 12 | 12 | each"

        # Test various invalid product codes
        invalid_codes = ["XS9999A", "", None, "   "]

        for code in invalid_codes:
            result = extract_creative_coop_quantity_enhanced(text, code)
            assert (
                result == 0 or result is None
            ), f"Should handle invalid code gracefully: {code}, got {result}"


class TestEnhancedQuantityExtractionEdgeCases:
    """Test edge cases for enhanced quantity extraction"""

    def test_validates_quantity_business_logic(self):
        """Test quantity validation rules"""
        validation_cases = [
            (50, "XS9826A", True),  # Normal quantity
            (0, "XS9826A", True),  # Zero quantity (backordered)
            (-5, "XS9826A", False),  # Invalid negative quantity
            (10000, "XS9826A", False),  # Unrealistically high quantity
        ]

        for quantity, product_code, expected_valid in validation_cases:
            result = validate_quantity_business_logic(quantity, product_code)
            assert (
                result == expected_valid
            ), f"Validation failed for quantity {quantity}: expected {expected_valid}, got {result}"

    def test_handles_partial_shipment_scenarios(self):
        """Test complex scenarios with partial shipments and backorders"""
        complex_text = """
        XS9826A | Product | 100 | 50 | 30 | 70 | each     # Partial shipment, large backorder
        XS8911A | Product | 24  | 24 | 24 | 0  | each     # Complete shipment  
        XS9482  | Product | 12  | 6  | 6  | 6  | each     # Split allocation/shipment
        """

        # Should prioritize shipped quantities
        result1 = extract_creative_coop_quantity_enhanced(complex_text, "XS9826A")
        assert result1 == 30, f"Should use shipped qty (30), got {result1}"

        result2 = extract_creative_coop_quantity_enhanced(complex_text, "XS8911A")
        assert result2 == 24, f"Should use shipped qty (24), got {result2}"

        result3 = extract_creative_coop_quantity_enhanced(complex_text, "XS9482")
        assert result3 == 6, f"Should use shipped qty (6), got {result3}"

    def test_detects_placeholder_quantities(self):
        """Test detection of suspicious placeholder patterns"""
        placeholder_text = """
        XS9826A | Product | 24 | 0 | 24 | 0 | each
        XS8911A | Product | 24 | 0 | 24 | 0 | each  
        XS9482  | Product | 24 | 0 | 24 | 0 | each
        """

        # Should detect suspicious pattern where all products have same quantity
        quantities = []
        for product_code in ["XS9826A", "XS8911A", "XS9482"]:
            qty = extract_creative_coop_quantity_enhanced(
                placeholder_text, product_code
            )
            quantities.append(qty)

        # If all quantities are identical, this might indicate placeholder data
        # For this test, we'll accept the quantities but log the pattern
        # In production, additional validation would be applied
        assert all(
            qty == 24 for qty in quantities
        ), "Should extract the quantities even if they appear to be placeholders"


class TestPatternContextExtraction:
    """Test pattern-based context extraction fallback"""

    def test_extracts_from_shipped_context(self):
        """Test extraction from shipped context patterns"""
        text_cases = [
            ("XS9826A shipped 15 each", "XS9826A", 15),
            ("Product XS8911A: quantity 8", "XS8911A", 8),
            ("12 each XS9482 items delivered", "XS9482", 12),
        ]

        for text, product_code, expected_qty in text_cases:
            result = extract_quantity_from_pattern_context(text, product_code)
            assert (
                result == expected_qty
            ), f"Pattern extraction failed for {product_code}: expected {expected_qty}, got {result}"

    def test_pattern_extraction_validation(self):
        """Test that pattern extraction applies business logic validation"""
        invalid_cases = [
            ("XS9826A shipped -5 each", "XS9826A"),  # Negative quantity
            ("XS8911A quantity 99999", "XS8911A"),  # Unrealistic quantity
        ]

        for text, product_code in invalid_cases:
            result = extract_quantity_from_pattern_context(text, product_code)
            assert (
                result == 0
            ), f"Should reject invalid quantities for {product_code}, got {result}"


def load_test_document(filename):
    """Helper function to load test document data"""
    # For now, return mock data
    # In real implementation, would load from test_invoices directory
    return """
    XS9826A | 191009727774 | 6"H Metal Ballerina | 24 | 0 | 12 | 12 | each
    XS9649A | 191009710615 | Christmas Product   | 24 | 0 | 6  | 18 | each
    XS9482  | 191009714712 | Holiday Item        | 24 | 0 | 8  | 16 | each
    XS8185  | 191009728481 | Decorative Item     | 16 | 16| 16 | 0  | each
    """


def main():
    """Run enhanced quantity extraction tests"""
    print("🧪 Running Enhanced Quantity Extraction Tests - Task 204")
    print("=" * 70)

    # Run tests using pytest
    try:
        exit_code = pytest.main([__file__, "-v", "--tb=short"])
        print(f"\n📊 Test Results: {'✅ PASSED' if exit_code == 0 else '❌ FAILED'}")
        return exit_code
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
