#!/usr/bin/env python3
"""
Test suite for quantity validation and business logic (Task 206)

Tests comprehensive quantity validation for Creative-Coop invoices including
placeholder detection, business rule validation, and quality assurance.

TDD Phase: RED (Failing Tests)
Author: Claude Code
Date: 2024-01-15
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions to test (these don't exist yet - will cause failures)
try:
    from main import (
        apply_backorder_logic,
        apply_quantity_business_logic,
        detect_placeholder_quantities,
        validate_case_pack_logic,
        validate_quantity_against_product_line,
        validate_quantity_distribution,
        validate_quantity_extraction,
        validate_quantity_with_context,
    )
except ImportError:
    # Functions don't exist yet - expected in RED phase
    def validate_quantity_extraction(quantity, product_code, context):
        raise NotImplementedError("Function not implemented yet")

    def apply_quantity_business_logic(quantity, product_code):
        raise NotImplementedError("Function not implemented yet")

    def detect_placeholder_quantities(quantity_dict):
        raise NotImplementedError("Function not implemented yet")

    def validate_quantity_distribution(distribution):
        raise NotImplementedError("Function not implemented yet")

    def validate_quantity_against_product_line(quantity, product_code, business_rules):
        raise NotImplementedError("Function not implemented yet")

    def validate_case_pack_logic(quantity, product_code):
        raise NotImplementedError("Function not implemented yet")

    def apply_backorder_logic(ordered, shipped, backordered):
        raise NotImplementedError("Function not implemented yet")

    def validate_quantity_with_context(quantity, product_code, context):
        raise NotImplementedError("Function not implemented yet")


class TestQuantityValidationBusinessLogic(unittest.TestCase):
    """Test quantity validation and business logic functionality"""

    def setUp(self):
        """Set up test data"""
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), "..", "test_invoices"
        )
        self.maxDiff = None

    # Happy Path Tests

    def test_validates_normal_quantity_ranges(self):
        """Test validation of normal quantity ranges"""
        # Arrange - Valid quantity ranges for different product types
        valid_quantity_cases = [
            ("XS9826A", 12, True),  # Normal quantity
            ("XS8911A", 48, True),  # Bulk quantity
            ("XS9482", 6, True),  # Small quantity
            ("XS8185", 24, True),  # Standard case quantity
            ("CF1234A", 1, True),  # Single unit order
            ("CD5678B", 144, True),  # Large bulk order
        ]

        for product_code, quantity, expected_valid in valid_quantity_cases:
            with self.subTest(product_code=product_code, quantity=quantity):
                # Act
                is_valid = validate_quantity_extraction(
                    quantity, product_code, "standard_context"
                )

                # Assert
                self.assertEqual(is_valid, expected_valid)
                if is_valid:
                    business_qty = apply_quantity_business_logic(quantity, product_code)
                    self.assertEqual(
                        business_qty, quantity
                    )  # No modification needed for valid quantities

    def test_applies_creative_coop_quantity_standards(self):
        """Test Creative-Coop specific business rules for quantity validation"""
        # Creative-Coop specific business rules for quantity validation
        business_rules = {
            "product_lines": {
                "XS": {"typical_min": 6, "typical_max": 72, "case_size": 12},
                "CF": {"typical_min": 1, "typical_max": 48, "case_size": 6},
                "CD": {"typical_min": 12, "typical_max": 144, "case_size": 24},
                "HX": {"typical_min": 4, "typical_max": 36, "case_size": 6},
            }
        }

        # Test product line specific validation
        self.assertEqual(
            validate_quantity_against_product_line(36, "XS9826A", business_rules), True
        )
        self.assertEqual(
            validate_quantity_against_product_line(200, "XS9826A", business_rules),
            False,
        )  # Too high for XS

        self.assertEqual(
            validate_quantity_against_product_line(24, "CF1234A", business_rules), True
        )
        self.assertEqual(
            validate_quantity_against_product_line(100, "CF1234A", business_rules),
            False,
        )  # Too high for CF

    def test_detects_case_pack_multiples(self):
        """Test validation against expected case pack sizes"""
        # Test validation against expected case pack sizes
        case_pack_tests = [
            ("XS9826A", 12, True),  # Exact case pack
            ("XS9826A", 24, True),  # 2 case packs
            ("XS9826A", 7, False),  # Partial case pack (suspicious)
            ("CF1234A", 6, True),  # CF case pack
            ("CF1234A", 18, True),  # 3 CF case packs
            ("CF1234A", 5, False),  # Partial CF case pack
        ]

        for product_code, quantity, expected_valid in case_pack_tests:
            with self.subTest(product_code=product_code, quantity=quantity):
                result = validate_case_pack_logic(quantity, product_code)
                self.assertEqual(result, expected_valid)

    # Error Handling Tests

    def test_detects_and_rejects_placeholder_quantities(self):
        """Test detection and rejection of placeholder quantities"""
        # Arrange - Simulate scenario where all products have same quantity (placeholder pattern)
        placeholder_scenario = {
            "XS9826A": 24,
            "XS8911A": 24,
            "XS9482": 24,
            "XS8185": 24,
            "CF1234A": 24,
            "CD5678B": 24,
        }

        # Act - Detect placeholder pattern
        is_placeholder_pattern = detect_placeholder_quantities(placeholder_scenario)

        # Assert - Should detect suspicious uniform quantities
        self.assertEqual(is_placeholder_pattern, True)

        # Individual quantities should be flagged for review
        for product_code, quantity in placeholder_scenario.items():
            with self.subTest(product_code=product_code):
                is_valid = validate_quantity_extraction(
                    quantity, product_code, "uniform_context"
                )
                self.assertEqual(is_valid, False)  # Should be marked as suspicious

    def test_handles_malformed_quantity_values(self):
        """Test handling of various malformed quantity inputs"""
        # Test various malformed quantity inputs
        malformed_quantities = [
            (-5, "XS9826A"),  # Negative quantity
            (0, "XS9826A"),  # Zero quantity (could be valid for backorders)
            (10000, "XS9826A"),  # Unrealistically high
            (None, "XS9826A"),  # None value
            ("abc", "XS9826A"),  # Non-numeric
            (1.5, "XS9826A"),  # Non-integer (should be converted)
        ]

        for quantity, product_code in malformed_quantities:
            with self.subTest(quantity=quantity, product_code=product_code):
                try:
                    result = validate_quantity_extraction(
                        quantity, product_code, "test_context"
                    )

                    if quantity == 0:
                        self.assertEqual(
                            result, True
                        )  # Zero can be valid (backordered)
                    elif quantity == 1.5:
                        self.assertEqual(result, True)  # Should convert to integer
                    else:
                        self.assertEqual(
                            result, False
                        )  # Other malformed values should be rejected
                except (ValueError, TypeError):
                    # Should handle gracefully without crashing
                    self.assertTrue(True)

    def test_handles_missing_context_gracefully(self):
        """Test validation when context is missing"""
        # Test validation when context is missing
        context_cases = [
            (12, None, "missing_product_code"),
            (12, "", "empty_product_code"),
            (12, "XS9826A", None),  # Missing context
            (12, "XS9826A", ""),  # Empty context
            (None, None, None),  # Everything missing
        ]

        for quantity, product_code, context in context_cases:
            with self.subTest(
                quantity=quantity, product_code=product_code, context=context
            ):
                result = validate_quantity_extraction(quantity, product_code, context)
                # Should handle gracefully without crashing
                self.assertTrue(isinstance(result, bool) or result is None)

    # Edge Case Tests

    def test_validates_backorder_scenarios(self):
        """Test validation for backorder quantity scenarios"""
        # Test validation for backorder quantity scenarios
        backorder_cases = [
            # (ordered, shipped, backordered, expected_final_quantity, should_be_valid)
            (24, 0, 24, 24, True),  # Full backorder - use ordered
            (48, 12, 36, 12, True),  # Partial shipment - use shipped
            (12, 12, 0, 12, True),  # Complete shipment
            (0, 0, 0, 0, True),  # Nothing ordered (valid scenario)
            (24, -5, 24, 0, False),  # Invalid shipped quantity
        ]

        for (
            ordered,
            shipped,
            backordered,
            expected_qty,
            should_be_valid,
        ) in backorder_cases:
            with self.subTest(
                ordered=ordered, shipped=shipped, backordered=backordered
            ):
                context = f"Ordered: {ordered}, Shipped: {shipped}, Backordered: {backordered}"

                # Simulate the business logic decision making
                final_qty = apply_backorder_logic(ordered, shipped, backordered)
                is_valid = validate_quantity_extraction(final_qty, "XS9826A", context)

                self.assertEqual(final_qty, expected_qty)
                self.assertEqual(is_valid, should_be_valid)

    def test_validates_quantity_distribution_patterns(self):
        """Test for realistic quantity distribution across invoice"""
        # Test for realistic quantity distribution across invoice
        quantity_distributions = [
            # Realistic distribution - varied quantities
            {
                "XS9826A": 12,
                "XS8911A": 6,
                "XS9482": 24,
                "XS8185": 18,
            },  # Should pass
            # Suspicious uniform distribution
            {
                "XS9826A": 24,
                "XS8911A": 24,
                "XS9482": 24,
                "XS8185": 24,
            },  # Should fail
            # Mixed realistic distribution
            {
                "XS9826A": 6,
                "XS8911A": 12,
                "XS9482": 36,
                "XS8185": 6,
            },  # Should pass
        ]

        for i, distribution in enumerate(quantity_distributions):
            with self.subTest(distribution_index=i):
                is_realistic = validate_quantity_distribution(distribution)

                if i == 1:  # Uniform distribution should be flagged
                    self.assertEqual(is_realistic, False)
                else:  # Varied distributions should pass
                    self.assertEqual(is_realistic, True)

    def test_applies_seasonal_and_context_adjustments(self):
        """Test quantity validation with seasonal/contextual business logic"""
        # Test quantity validation with seasonal/contextual business logic
        seasonal_contexts = [
            (
                "holiday_order",
                "XS9826A",
                72,
                True,
            ),  # Higher holiday quantities acceptable
            (
                "regular_order",
                "XS9826A",
                72,
                False,
            ),  # Same quantity suspicious for regular order
            (
                "clearance_order",
                "XS9826A",
                144,
                True,
            ),  # Large clearance quantities acceptable
            (
                "sample_order",
                "XS9826A",
                2,
                True,
            ),  # Small sample quantities acceptable
        ]

        for order_type, product_code, quantity, expected_valid in seasonal_contexts:
            with self.subTest(order_type=order_type, quantity=quantity):
                context = f"Order Type: {order_type}"
                result = validate_quantity_with_context(quantity, product_code, context)
                self.assertEqual(result, expected_valid)

    # Integration Tests

    def test_quantity_validation_integration(self):
        """Test integration of all quantity validation functions"""
        # Test complete validation pipeline
        test_invoice_data = {
            "XS9826A": {"ordered": 24, "shipped": 18, "backordered": 6},
            "XS8911A": {"ordered": 12, "shipped": 12, "backordered": 0},
            "CF1234A": {"ordered": 6, "shipped": 0, "backordered": 6},
        }

        successful_validations = 0
        for product_code, quantities in test_invoice_data.items():
            try:
                # Apply backorder logic
                final_qty = apply_backorder_logic(
                    quantities["ordered"],
                    quantities["shipped"],
                    quantities["backordered"],
                )

                # Validate the result
                is_valid = validate_quantity_extraction(
                    final_qty, product_code, "integration_test"
                )

                if is_valid:
                    successful_validations += 1

            except Exception as e:
                print(f"Integration test failed for {product_code}: {e}")

        # Should validate at least 2 out of 3 products successfully
        self.assertGreaterEqual(successful_validations, 2)

    # Performance Tests

    def test_validation_performance(self):
        """Test performance of quantity validation for large datasets"""
        import time

        # Create large dataset for performance testing
        large_dataset = {}
        for i in range(100):
            product_code = f"XS{9000+i:04d}A"
            large_dataset[product_code] = 12 + (i % 20) * 6  # Varied quantities

        start_time = time.time()

        # Test distribution validation
        is_realistic = validate_quantity_distribution(large_dataset)

        # Test individual validations
        valid_count = 0
        for product_code, quantity in large_dataset.items():
            if validate_quantity_extraction(quantity, product_code, "performance_test"):
                valid_count += 1

        processing_time = time.time() - start_time

        # Should complete within reasonable time
        self.assertLess(processing_time, 1.0, "Validation took too long")
        self.assertIsInstance(is_realistic, bool)
        self.assertGreater(valid_count, 80)  # Most should be valid


class TestQuantityValidationBusinessRules(unittest.TestCase):
    """Test specific business rules for quantity validation"""

    def test_product_line_classification(self):
        """Test product line classification for validation"""
        product_line_tests = [
            ("XS9826A", "XS"),
            ("CF1234A", "CF"),
            ("CD5678B", "CD"),
            ("HX9999X", "HX"),
            ("UNKNOWN123", None),  # Unknown product line
        ]

        for product_code, expected_line in product_line_tests:
            with self.subTest(product_code=product_code):
                # This will test internal product line detection logic
                business_rules = {
                    "product_lines": {
                        "XS": {"typical_min": 6, "typical_max": 72, "case_size": 12},
                        "CF": {"typical_min": 1, "typical_max": 48, "case_size": 6},
                        "CD": {"typical_min": 12, "typical_max": 144, "case_size": 24},
                        "HX": {"typical_min": 4, "typical_max": 36, "case_size": 6},
                    }
                }

                # Test with a reasonable quantity
                if expected_line:
                    result = validate_quantity_against_product_line(
                        24, product_code, business_rules
                    )
                    self.assertIsInstance(result, bool)
                else:
                    # Unknown product lines should handle gracefully
                    result = validate_quantity_against_product_line(
                        24, product_code, business_rules
                    )
                    self.assertIsInstance(result, bool)

    def test_suspicious_pattern_detection(self):
        """Test detection of suspicious quantity patterns"""
        suspicious_patterns = [
            # All same quantity
            {"XS1": 24, "XS2": 24, "XS3": 24, "XS4": 24},
            # All multiples of specific number
            {"XS1": 12, "XS2": 24, "XS3": 36, "XS4": 48},
            # Unrealistic high quantities
            {"XS1": 1000, "XS2": 2000, "XS3": 3000},
        ]

        realistic_patterns = [
            # Varied realistic quantities
            {"XS1": 6, "XS2": 12, "XS3": 18, "XS4": 24},
            # Mixed case pack sizes
            {"XS1": 12, "CF1": 6, "CD1": 24, "HX1": 4},
        ]

        for pattern in suspicious_patterns:
            with self.subTest(pattern=pattern):
                is_realistic = validate_quantity_distribution(pattern)
                self.assertEqual(is_realistic, False)

        for pattern in realistic_patterns:
            with self.subTest(pattern=pattern):
                is_realistic = validate_quantity_distribution(pattern)
                self.assertEqual(is_realistic, True)


if __name__ == "__main__":
    # Run the tests
    print("=" * 80)
    print("TASK 206: Quantity Validation and Business Logic - TDD RED Phase")
    print("=" * 80)
    print("Running failing tests to establish requirements...")
    print()

    # Create a custom test runner that shows more detail
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)

    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("RED PHASE SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures or result.errors:
        print("\n✅ RED phase successful - Tests are failing as expected")
        print("Next: Implement minimal functions to make tests pass (GREEN phase)")
    else:
        print("\n❌ RED phase failed - Tests should be failing initially")

    print("=" * 80)
