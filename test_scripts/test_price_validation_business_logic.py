#!/usr/bin/env python3
"""
Test script for Price Validation and Business Logic - Task 203
Implements comprehensive price validation testing for Creative-Coop invoices.

Engineering Principles Applied:
- Principle 2: Data quality validation
- Principle 5: Error resilience
- Principle 9: Algorithmic processing

This test file implements the RED phase of TDD for price validation.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from main import (
    apply_business_price_logic,
    attempt_price_correction,
    is_valid_discount_context,
    validate_price_against_industry_standards,
    validate_price_extraction,
    validate_price_with_quantity_context,
    validate_product_line_pricing,
)


class TestPriceValidationHappyPath:
    """Test happy path scenarios for price validation"""

    def test_validates_normal_wholesale_prices(self):
        """Test validation of normal wholesale price ranges"""
        # Arrange - Valid wholesale price range
        test_cases = [
            ("XS9826A", "$1.60", True),  # Normal wholesale price
            ("XS8911A", "$8.00", True),  # Higher wholesale price
            ("XS9482", "$2.80", True),  # Mid-range wholesale price
            ("XS8185", "$12.00", True),  # Premium wholesale price
        ]

        for product_code, price, expected_valid in test_cases:
            # Act
            is_valid = validate_price_extraction(
                price, product_code, "document_context"
            )

            # Assert
            assert (
                is_valid == expected_valid
            ), f"Price {price} for {product_code} should be {expected_valid}"
            if is_valid:
                business_price = apply_business_price_logic(
                    price, product_code, "document_context"
                )
                assert (
                    business_price == price
                ), f"No modification needed for valid price {price}"

    def test_applies_creative_coop_industry_standards(self):
        """Test Creative-Coop specific business rule validation"""
        # Creative-Coop specific business rules
        test_validation_rules = {
            "wholesale_margin": {"min_percentage": 40, "max_percentage": 70},
            "price_ranges": {
                "XS_products": {"min": 0.50, "max": 50.00},
                "CF_products": {"min": 1.00, "max": 100.00},
                "CD_products": {"min": 0.25, "max": 25.00},
            },
        }

        # Test XS product line price validation
        assert (
            validate_price_against_industry_standards(
                "$25.00", "XS9826A", test_validation_rules
            )
            == True
        )
        assert (
            validate_price_against_industry_standards(
                "$75.00", "XS9826A", test_validation_rules
            )
            == False
        )  # Too high

        # Test CF product line price validation
        assert (
            validate_price_against_industry_standards(
                "$50.00", "CF1234A", test_validation_rules
            )
            == True
        )
        assert (
            validate_price_against_industry_standards(
                "$0.25", "CF1234A", test_validation_rules
            )
            == False
        )  # Too low


class TestPriceValidationErrorHandling:
    """Test error handling scenarios for price validation"""

    def test_detects_and_rejects_placeholder_prices(self):
        """Test detection and rejection of known placeholder prices"""
        # Arrange - Known placeholder prices that should be rejected
        placeholder_prices = [
            "$1.60",  # Known Creative-Coop placeholder
            "$0.00",  # Zero price (invalid)
            "$999.99",  # Unrealistic high price
            "$0.01",  # Unrealistic low price for Creative-Coop products
        ]

        for price in placeholder_prices:
            # Act
            is_valid = validate_price_extraction(price, "XS9826A", "test document")

            # Assert - Should be rejected
            assert is_valid == False, f"Placeholder price {price} should be rejected"

            # Should trigger business logic correction
            corrected_price = apply_business_price_logic(price, "XS9826A")
            assert (
                corrected_price != price or corrected_price is None
            ), f"Placeholder {price} should be corrected or rejected"

    def test_handles_malformed_price_formats(self):
        """Test handling of various malformed price formats"""
        # Arrange - Various malformed price formats
        malformed_prices = [
            ("N/A", False),  # Text instead of price
            ("", False),  # Empty string
            ("$", False),  # Currency symbol only
            ("Price: 1.60", False),  # Contains extra text
            ("1.60 USD", False),  # Wrong format
            ("$-5.00", False),  # Negative price
            ("$1,234.56", True),  # Comma formatting (should be handled)
            ("€1.60", False),  # Wrong currency
        ]

        for price, expected_valid in malformed_prices:
            # Act
            is_valid = validate_price_extraction(price, "XS9826A", "test document")

            # Assert - Should be rejected or corrected
            if price == "$1,234.56":  # This should be correctable but out of range
                assert is_valid == False, "High price should be rejected"
            else:
                assert (
                    is_valid == expected_valid
                ), f"Price format {price} validation incorrect"

    def test_handles_missing_context_gracefully(self):
        """Test validation when document context is missing or invalid"""
        test_cases = [
            (None, "XS9826A"),  # No document context
            ("", "XS9826A"),  # Empty document context
            ("valid context", None),  # No product code
            ("valid context", ""),  # Empty product code
            (None, None),  # Both missing
        ]

        for context, product_code in test_cases:
            result = validate_price_extraction("$1.60", product_code, context)
            # Should handle gracefully without crashing
            assert (
                isinstance(result, bool) or result is None
            ), f"Should handle missing context gracefully for {context}, {product_code}"


class TestPriceValidationEdgeCases:
    """Test edge cases for price validation"""

    def test_validates_context_dependent_pricing(self):
        """Test prices validated based on document context clues"""
        # Prices should be validated based on document context clues
        context_with_discount = """
        Creative Coop Wholesale Invoice
        Volume Discount Applied: 50%
        XS9826A 6"H Metal Ballerina Ornament
        Original Price: $3.20
        Discounted Price: $1.60
        """

        # In discount context, $1.60 might be valid
        result = validate_price_extraction("$1.60", "XS9826A", context_with_discount)
        assert result == True, "Should be valid in discount context"

        # Without discount context, $1.60 is suspicious as placeholder
        context_no_discount = 'XS9826A 6"H Metal Ballerina Ornament Standard pricing'
        result = validate_price_extraction("$1.60", "XS9826A", context_no_discount)
        assert result == False, "Should be suspicious as placeholder"

    def test_applies_quantity_based_pricing_validation(self):
        """Test quantity-based pricing validation logic"""
        # Higher quantities should generally have lower unit prices
        quantity_price_cases = [
            (1, "$5.00", True),  # Single unit - higher price acceptable
            (24, "$3.00", True),  # Bulk quantity - moderate price
            (100, "$1.50", True),  # Large bulk - lower price acceptable
            (1, "$0.50", False),  # Single unit - suspiciously low
            (100, "$10.00", False),  # Large bulk - suspiciously high
        ]

        for quantity, price, expected_valid in quantity_price_cases:
            document_with_qty = f"XS9826A Product Quantity: {quantity} Price: {price}"
            result = validate_price_with_quantity_context(
                price, "XS9826A", document_with_qty
            )
            assert (
                result == expected_valid
            ), f"Quantity {quantity} with price {price} validation failed"


class TestBusinessLogicCorrection:
    """Test business logic correction functionality"""

    def test_attempts_price_correction_for_invalid_prices(self):
        """Test business logic attempts to correct invalid prices"""
        # Test known correction scenarios
        correction_cases = [
            ("$0.00", "XS9826A", True),  # Zero price should be correctable
            ("$999.99", "XS9826A", True),  # Obviously wrong price
            ("Price: 5.60", "XS9826A", True),  # Format correction
            ("N/A", "XS9826A", False),  # Uncorrectable
        ]

        for invalid_price, product_code, should_correct in correction_cases:
            corrected = attempt_price_correction(invalid_price, product_code)

            if should_correct:
                assert corrected is not None, f"Should correct {invalid_price}"
                assert (
                    corrected != invalid_price
                ), f"Correction should change {invalid_price}"
            else:
                assert corrected is None, f"Should not correct {invalid_price}"

    def test_validates_corrected_prices(self):
        """Test that corrected prices pass validation"""
        # Start with invalid price
        invalid_price = "$0.00"
        product_code = "XS9826A"

        # Attempt correction
        corrected = attempt_price_correction(invalid_price, product_code)

        if corrected:
            # Corrected price should be valid
            is_valid = validate_price_extraction(
                corrected, product_code, "test context"
            )
            assert is_valid == True, f"Corrected price {corrected} should be valid"


class TestContextValidation:
    """Test context-aware validation functionality"""

    def test_identifies_discount_contexts(self):
        """Test identification of legitimate discount contexts"""
        discount_contexts = [
            ("Volume discount applied 50%", True),
            ("Bulk pricing promotion", True),
            ("Wholesale discount rates", True),
            ("Standard pricing applies", False),
            ("No special offers", False),
            ("", False),
        ]

        for context, expected_discount in discount_contexts:
            result = is_valid_discount_context(context)
            assert (
                result == expected_discount
            ), f"Discount context detection failed for: {context}"

    def test_validates_product_line_pricing(self):
        """Test product line specific pricing validation"""
        pricing_cases = [
            # XS product line
            ("XS9826A", 25.0, True),  # Within range
            ("XS9826A", 75.0, False),  # Too high
            ("XS9826A", 0.25, False),  # Too low
            # CF product line
            ("CF1234A", 50.0, True),  # Within range
            ("CF1234A", 150.0, False),  # Too high
            ("CF1234A", 0.50, False),  # Too low
            # CD product line
            ("CD9999B", 15.0, True),  # Within range
            ("CD9999B", 30.0, False),  # Too high
            ("CD9999B", 0.10, False),  # Too low
        ]

        for product_code, price_value, expected_valid in pricing_cases:
            result = validate_product_line_pricing(price_value, product_code)
            assert (
                result == expected_valid
            ), f"Product line validation failed for {product_code}: ${price_value}"


def main():
    """Run price validation tests"""
    print("🧪 Running Price Validation and Business Logic Tests - Task 203")
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
