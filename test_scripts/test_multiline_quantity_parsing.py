#!/usr/bin/env python3
"""
Test suite for multi-line quantity parsing enhancement (Task 205)

Tests multi-line quantity extraction for Creative-Coop invoices with complex
"shipped back unit unit_price wholesale amount" formats across multiple lines.

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
        extract_quantity_context_lines,
        extract_quantity_from_multiline_enhanced,
        parse_multiline_quantity_patterns,
    )
except ImportError:
    # Functions don't exist yet - expected in RED phase
    def extract_quantity_from_multiline_enhanced(text, product_code):
        raise NotImplementedError("Function not implemented yet")

    def parse_multiline_quantity_patterns(context_lines):
        raise NotImplementedError("Function not implemented yet")

    def extract_quantity_context_lines(text, product_code):
        raise NotImplementedError("Function not implemented yet")


class TestMultiLineQuantityParsing(unittest.TestCase):
    """Test multi-line quantity parsing functionality"""

    def setUp(self):
        """Set up test data"""
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), "..", "test_invoices"
        )
        self.maxDiff = None

    def load_test_document(self, filename):
        """Helper to load test document JSON"""
        try:
            filepath = os.path.join(self.test_data_dir, filename)
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    # Happy Path Tests

    def test_parses_standard_multiline_quantity_format(self):
        """Test parsing standard Creative-Coop multi-line format from Document AI"""
        # Arrange - Standard Creative-Coop multi-line format from Document AI
        multiline_text = """
        XS9826A
        191009727774
        6"H Metal Ballerina Ornament,
        24
        0
        0
        24
        each
        2.00
        1.60
        38.40
        """

        # Act - Extract quantity from multi-line format
        result = extract_quantity_from_multiline_enhanced(multiline_text, "XS9826A")

        # Assert - Should extract shipped quantity (3rd number) = 0, so use ordered (1st number) = 24
        self.assertEqual(result, 24)

    def test_parses_shipped_back_unit_format(self):
        """Test parsing shipped-back-unit format"""
        # Arrange - "shipped back unit" format parsing
        shipped_back_text = """
        XS9826A Product Description
        12 shipped
        12 back
        each unit
        $1.60 wholesale
        $19.20 amount
        """

        # Act
        result = extract_quantity_from_multiline_enhanced(shipped_back_text, "XS9826A")

        # Assert - Should prioritize shipped quantity (12)
        self.assertEqual(result, 12)

    def test_parses_complex_multiline_with_context(self):
        """Test parsing complex multi-line with various quantity references"""
        # Arrange - Complex multi-line with various quantity references
        complex_text = """
        Product: XS9826A
        Description: 6"H Metal Ballerina Ornament
        Quantities:
        - Ordered: 48
        - Allocated: 24  
        - Shipped: 18
        - Backordered: 30
        Unit: each
        """

        # Act
        result = extract_quantity_from_multiline_enhanced(complex_text, "XS9826A")

        # Assert - Should prioritize shipped (18) over ordered
        self.assertEqual(result, 18)

    def test_processes_cs003837319_multiline_products(self):
        """Test processing actual CS003837319 multi-line entities"""
        # Load actual CS003837319 multi-line entities
        cs_document_data = self.load_test_document(
            "CS003837319_Error_2_docai_output.json"
        )

        if not cs_document_data:
            self.skipTest("CS003837319 test document not available")

        cs_document_text = json.dumps(cs_document_data)

        # Test products known to have multi-line quantity formats
        multiline_products = ["XS9826A", "XS9649A", "XS9482", "XS8185"]

        successful_extractions = 0
        for product_code in multiline_products:
            try:
                quantity = extract_quantity_from_multiline_enhanced(
                    cs_document_text, product_code
                )
                if quantity > 0 and quantity != 24:  # Valid, non-placeholder
                    successful_extractions += 1
            except Exception as e:
                print(f"Failed to extract quantity for {product_code}: {e}")

        # Should successfully parse at least 75% of multi-line products
        success_rate = (
            successful_extractions / len(multiline_products)
            if multiline_products
            else 0
        )
        self.assertGreaterEqual(
            success_rate,
            0.75,
            f"Multi-line parsing success rate {success_rate:.2%} below 75% threshold",
        )

    # Error Handling Tests

    def test_handles_incomplete_multiline_data(self):
        """Test handling incomplete multi-line data gracefully"""
        # Arrange - Missing quantity information in multi-line format
        incomplete_cases = [
            # Missing shipped quantity
            "XS9826A\nProduct\n24\n0\n\n12\neach",
            # Non-numeric quantity data
            "XS9826A\nProduct\nN/A\nInvalid\n0\n12\neach",
            # Truncated multi-line data
            "XS9826A\nProduct\n24",
        ]

        for incomplete_text in incomplete_cases:
            # Act
            result = extract_quantity_from_multiline_enhanced(
                incomplete_text, "XS9826A"
            )

            # Assert - Should handle gracefully, fallback or return 0
            self.assertGreaterEqual(result, 0, "Should not crash or return negative")
            self.assertIsInstance(result, int, "Should return integer")

    def test_handles_malformed_multiline_structure(self):
        """Test handling various malformed multi-line structures"""
        # Test various malformed multi-line structures
        malformed_text = """
        XS9826A|||Product|||Description
        |||24|||0|||0|||24|||each|||
        Price|||Information|||Here
        """

        result = extract_quantity_from_multiline_enhanced(malformed_text, "XS9826A")
        # Should attempt to extract meaningful data or return fallback
        self.assertIn(
            result, [0, 24], "Should return either fallback or extracted ordered qty"
        )

    def test_handles_context_lines_extraction_failure(self):
        """Test when context line extraction fails"""
        # Test when context line extraction fails
        minimal_text = "XS9826A"

        result = extract_quantity_from_multiline_enhanced(minimal_text, "XS9826A")
        # Should return 0 when insufficient context
        self.assertEqual(result, 0, "Should return 0 when insufficient context")

    # Edge Case Tests

    def test_parses_various_multiline_layouts(self):
        """Test different multi-line layouts and formats"""
        # Test different multi-line layouts and formats
        layout_cases = [
            # Vertical layout
            ("XS9826A\n24\n0\n12\n12\neach", "XS9826A", 12),  # Shipped = 12
            # Horizontal with separators
            ("XS9826A | 24 | 0 | 18 | 6 | each", "XS9826A", 18),  # Shipped = 18
            # Mixed format with labels
            (
                "XS9826A\nOrdered: 24\nShipped: 15\nUnit: each",
                "XS9826A",
                15,
            ),  # Shipped = 15
        ]

        for text_layout, product_code, expected_qty in layout_cases:
            with self.subTest(layout=text_layout[:20], expected=expected_qty):
                result = extract_quantity_from_multiline_enhanced(
                    text_layout, product_code
                )
                self.assertEqual(result, expected_qty)

    def test_validates_multiline_quantity_ranges(self):
        """Test quantity validation in multi-line context"""
        # Test quantity validation in multi-line context
        range_test_cases = [
            ("XS9826A\n500\n0\n300\n200\neach", "XS9826A", 300),  # Normal range
            ("XS9826A\n5000\n0\n2000\n3000\neach", "XS9826A", 0),  # Too high, reject
            (
                "XS9826A\n-10\n0\n5\n-15\neach",
                "XS9826A",
                5,
            ),  # Ignore negative, use positive
        ]

        for text, product_code, expected in range_test_cases:
            with self.subTest(text=text[:20], expected=expected):
                result = extract_quantity_from_multiline_enhanced(text, product_code)
                self.assertEqual(result, expected)

    def test_handles_unit_variations_in_multiline(self):
        """Test various unit formats in multi-line context"""
        # Test various unit formats in multi-line context
        unit_cases = [
            ("XS9826A\n24\n0\n12\n12\neach", "XS9826A", 12),
            ("XS9826A\n24\n0\n12\n12\nset", "XS9826A", 12),
            ("XS9826A\n24\n0\n12\n12\npiece", "XS9826A", 12),
            ("XS9826A\n24\n0\n12\n12\ncase", "XS9826A", 12),
        ]

        for text, product_code, expected in unit_cases:
            with self.subTest(unit=text.split("\n")[-1], expected=expected):
                result = extract_quantity_from_multiline_enhanced(text, product_code)
                self.assertEqual(result, expected)

    # Helper Function Tests

    def test_extract_quantity_context_lines(self):
        """Test context line extraction functionality"""
        test_text = """Line 1
        Line 2
        XS9826A Product Line
        Line 4
        Line 5
        Line 6
        Line 7
        Line 8
        Line 9
        Line 10"""

        result = extract_quantity_context_lines(test_text, "XS9826A")

        # Should return lines starting from product code line
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(any("XS9826A" in line for line in result))

    def test_parse_multiline_quantity_patterns(self):
        """Test multi-line quantity pattern parsing"""
        test_lines = [
            "XS9826A",
            "Product Description",
            "24",  # Ordered
            "0",  # Allocated
            "18",  # Shipped
            "6",  # Backordered
            "each",
        ]

        result = parse_multiline_quantity_patterns(test_lines)

        # Should return dictionary with quantity types
        self.assertIsInstance(result, dict)
        expected_keys = ["ordered", "allocated", "shipped", "backordered"]
        for key in expected_keys:
            if key in result:
                self.assertIsInstance(result[key], int)

    # Performance Tests

    def test_performance_multiline_processing(self):
        """Test performance of multi-line quantity processing"""
        import time

        # Create large multi-line text
        large_text = "\n".join(
            [
                f"XS9826A Product {i}" if i % 10 == 0 else f"Line {i}"
                for i in range(1000)
            ]
        )

        start_time = time.time()
        result = extract_quantity_from_multiline_enhanced(large_text, "XS9826A")
        processing_time = time.time() - start_time

        # Should complete within 300ms
        self.assertLess(
            processing_time,
            0.3,
            f"Processing took {processing_time:.3f}s, should be < 0.3s",
        )


class TestMultiLineQuantityIntegration(unittest.TestCase):
    """Integration tests for multi-line quantity parsing"""

    def setUp(self):
        """Set up integration test environment"""
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), "..", "test_invoices"
        )

    def test_integration_with_creative_coop_processing(self):
        """Test integration with existing Creative-Coop processing"""
        # This test will verify that multi-line parsing integrates properly
        # with the existing Creative-Coop processing pipeline

        # For now, just verify the functions can be called without errors
        try:
            result = extract_quantity_from_multiline_enhanced(
                "XS9826A\n24\n0\n12", "XS9826A"
            )
            self.assertIsInstance(result, int)
        except NotImplementedError:
            # Expected in RED phase
            pass

    def test_fallback_integration_with_existing_methods(self):
        """Test that multi-line parsing works as fallback to existing methods"""
        # Test case where standard methods fail but multi-line succeeds
        complex_multiline_text = """
        Complex invoice format
        XS9826A detailed product information
        Ordered quantity: 48
        Allocated: 24
        Shipped: 30
        Back ordered: 18
        """

        try:
            result = extract_quantity_from_multiline_enhanced(
                complex_multiline_text, "XS9826A"
            )
            # Should prioritize shipped quantity (30)
            self.assertEqual(result, 30)
        except NotImplementedError:
            # Expected in RED phase
            pass


if __name__ == "__main__":
    # Run the tests
    print("=" * 80)
    print("TASK 205: Multi-Line Quantity Parsing - TDD RED Phase")
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
