#!/usr/bin/env python3
"""
Test Enhanced Description Extraction - UPC Integration and Quality Enhancement

Tests for Task 210: Sophisticated description extraction system for Creative-Coop
invoices that integrates UPC codes with product descriptions to achieve 95% completeness.

TDD Test Implementation (RED Phase):
- All tests will initially fail
- Tests define the expected behavior for enhanced description extraction
- Tests cover happy path, error handling, and edge cases
"""

import json
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, Mock

# Add parent directory to path to import main functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import (
        clean_description_artifacts,
        enhance_description_completeness,
        extract_description_from_product_context,
        extract_enhanced_product_description,
        extract_upc_for_product,
        integrate_upc_with_description,
        validate_description_quality,
    )
except ImportError:
    # Functions don't exist yet - this is expected in RED phase
    pass


def load_test_document(filename):
    """Load test document for description extraction testing"""
    test_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_invoices", filename
    )

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file not found: {test_file_path}")

    with open(test_file_path, "r", encoding="utf-8") as f:
        doc_data = json.load(f)

    return doc_data.get("text", "")


def generate_large_document_with_products(num_products):
    """Generate large document text with specified number of products for performance testing"""
    document_parts = []

    for i in range(num_products):
        product_code = f"XS{i:04d}A"
        upc_code = f"19100{i:07d}"
        description = f"Test Product {i} Description for performance testing"

        document_parts.append(f"{product_code} {upc_code} {description}")

    return "\n".join(document_parts)


class TestEnhancedDescriptionExtraction(unittest.TestCase):
    """Test cases for enhanced description extraction with UPC integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.cs_doc_filename = "CS003837319_Error 2_docai_output.json"

        # Load the Creative-Coop test document if it exists
        try:
            self.cs_document_text = load_test_document(self.cs_doc_filename)
            self.document_available = True
        except FileNotFoundError:
            print(
                f"⚠️ Test document {self.cs_doc_filename} not found. Some tests will be skipped."
            )
            self.document_available = False
            self.cs_document_text = ""

    # =================================================================
    # HAPPY PATH TESTS
    # =================================================================

    def test_extracts_enhanced_descriptions_with_upc_integration(self):
        """Test enhanced description extraction with UPC integration"""
        # Arrange - Document text with product and UPC information
        document_text = """
        XS9826A 191009727774 6"H Metal Ballerina Ornament
        Product details and pricing information
        XS8911A 191009710615 4-3/4"L x 3-1/2"W Cotton Lumbar Pillow
        Additional product information
        """

        # Act - Extract enhanced descriptions with UPC integration
        desc_xs9826a = extract_enhanced_product_description(
            document_text, "XS9826A", "191009727774"
        )
        desc_xs8911a = extract_enhanced_product_description(
            document_text, "XS8911A", "191009710615"
        )

        # Assert - Should integrate UPC with description
        self.assertIn("XS9826A", desc_xs9826a)
        self.assertIn("191009727774", desc_xs9826a)  # UPC integrated
        self.assertIn("Metal Ballerina Ornament", desc_xs9826a)

        self.assertIn("XS8911A", desc_xs8911a)
        self.assertIn("191009710615", desc_xs8911a)  # UPC integrated
        self.assertIn("Cotton Lumbar Pillow", desc_xs8911a)

    def test_processes_cs003837319_descriptions_comprehensively(self):
        """Test comprehensive description processing of CS003837319 document"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Test specific known products for description quality
        test_products = {
            "XS9826A": {
                "expected_upc": "191009727774",
                "expected_keywords": ["Metal", "Ballerina", "Ornament"],
                "expected_format_contains": [
                    "XS9826A",
                    "191009727774",
                    "Metal",
                    "Ballerina",
                ],
            },
            "XS9649A": {
                "expected_upc": "191009725688",
                "expected_keywords": ["Paper", "Mache"],
                "expected_format_contains": ["XS9649A", "191009725688", "Paper"],
            },
        }

        for product_code, expectations in test_products.items():
            with self.subTest(product_code=product_code):
                # Act
                description = extract_enhanced_product_description(
                    self.cs_document_text, product_code, expectations["expected_upc"]
                )

                # Assert - Should meet quality standards
                self.assertNotEqual(
                    description,
                    "Traditional D-code format",
                    f"Should not return placeholder for {product_code}",
                )
                self.assertIn(
                    product_code,
                    description,
                    f"Description should contain product code {product_code}",
                )
                self.assertIn(
                    expectations["expected_upc"],
                    description,
                    f"Description should contain UPC for {product_code}",
                )

                # Should contain expected keywords
                for keyword in expectations["expected_keywords"]:
                    self.assertIn(
                        keyword,
                        description,
                        f"Description for {product_code} should contain keyword '{keyword}'",
                    )

    def test_integrates_upc_with_description_correctly(self):
        """Test UPC integration with various description formats"""
        integration_cases = [
            {
                "document_text": "XS9826A Beautiful Metal Ornament for holidays",
                "product_code": "XS9826A",
                "upc_code": "191009727774",
                "expected": "XS9826A - UPC: 191009727774 - Beautiful Metal Ornament for holidays",
            },
            {
                "document_text": "CF1234A Premium Cotton Product",
                "product_code": "CF1234A",
                "upc_code": "123456789012",
                "expected": "CF1234A - UPC: 123456789012 - Premium Cotton Product",
            },
        ]

        for i, case in enumerate(integration_cases):
            with self.subTest(case_index=i):
                # Act
                result = integrate_upc_with_description(
                    case["document_text"], case["product_code"], case["upc_code"]
                )

                # Assert
                self.assertEqual(
                    result, case["expected"], f"UPC integration failed for case {i}"
                )

    def test_enhances_description_completeness(self):
        """Test description completeness enhancement"""
        incomplete_description = "XS9826A Metal"
        document_context = """
        XS9826A 191009727774 6"H Metal Ballerina Ornament
        Beautiful decorative piece for holiday display
        Premium quality construction
        """

        # Act - Enhance description completeness
        enhanced = enhance_description_completeness(
            incomplete_description, "XS9826A", document_context
        )

        # Assert - Should be more complete
        self.assertGreater(
            len(enhanced),
            len(incomplete_description),
            "Enhanced description should be longer",
        )

        # Should contain more detailed information
        enhanced_lower = enhanced.lower()
        contains_ballerina = "ballerina" in enhanced_lower
        contains_ornament = "ornament" in enhanced_lower
        contains_height = '6"h' in enhanced_lower or "6" in enhanced_lower

        self.assertTrue(
            contains_ballerina or contains_ornament or contains_height,
            "Enhanced description should contain more detailed product information",
        )

    # =================================================================
    # ERROR HANDLING TESTS
    # =================================================================

    def test_handles_missing_upc_codes_gracefully(self):
        """Test when UPC codes are not available"""
        document_text = 'XS9826A 6"H Metal Ballerina Ornament without UPC'

        # Act - Extract description without UPC
        description = extract_enhanced_product_description(
            document_text, "XS9826A", None
        )

        # Assert - Should provide description without UPC
        self.assertIn("XS9826A", description)
        self.assertIn("Metal Ballerina Ornament", description)
        self.assertNotIn(
            "UPC:", description, "Should not include UPC section when not available"
        )

    def test_handles_malformed_description_data(self):
        """Test handling of malformed or incomplete description data"""
        malformed_cases = [
            "XS9826A |||||| corrupted data",  # Corrupted separators
            "XS9826A \n\n\n incomplete",  # Excessive whitespace
            "XS9826A 123 abc def ghi",  # Random characters
            "",  # Empty string
        ]

        for i, malformed_text in enumerate(malformed_cases):
            with self.subTest(case_index=i, malformed_text=malformed_text):
                # Act
                result = extract_enhanced_product_description(
                    malformed_text, "XS9826A", "191009727774"
                )

                # Assert - Should handle gracefully
                if malformed_text:
                    self.assertIn(
                        "XS9826A", result, f"Should include product code for case {i}"
                    )
                    self.assertGreater(
                        len(result), 0, f"Should not be empty for case {i}"
                    )
                else:
                    expected = "XS9826A - UPC: 191009727774 - Product description not available"
                    self.assertEqual(
                        result, expected, "Should handle empty string gracefully"
                    )

    def test_handles_special_characters_in_descriptions(self):
        """Test handling of special characters and formatting"""
        special_char_cases = [
            ("XS9826A 6\"H Metal Ballerina's Ornament", "quotes and apostrophes"),
            ('XS8911A 4-3/4"L × 3-1/2"W Product', "fractions and symbols"),
            ("CF1234A Café & Müller Brand", "accented characters"),
            ("CD5678B 50% Off Special Product", "percentage symbols"),
        ]

        for i, (text_with_special, description_type) in enumerate(special_char_cases):
            with self.subTest(case_index=i, description_type=description_type):
                product_code = text_with_special.split()[0]

                # Act
                result = extract_enhanced_product_description(
                    text_with_special, product_code, "123456789012"
                )

                # Assert - Should preserve special characters
                self.assertIn(product_code, result)
                self.assertIn("123456789012", result)
                # Should handle special characters without crashing
                self.assertGreater(len(result), 0)

    def test_handles_extremely_long_descriptions(self):
        """Test handling of very long product descriptions"""
        long_description = (
            "XS9826A " + "Very long product description " * 50
        )  # ~1500 characters

        # Act
        result = extract_enhanced_product_description(
            long_description, "XS9826A", "191009727774"
        )

        # Assert - Should handle long descriptions appropriately
        self.assertIn("XS9826A", result)
        self.assertIn("191009727774", result)
        # Should truncate or handle long descriptions reasonably
        self.assertLessEqual(
            len(result),
            500,
            "Should handle long descriptions with reasonable length limit",
        )

    # =================================================================
    # EDGE CASE TESTS
    # =================================================================

    def test_extracts_descriptions_from_various_document_contexts(self):
        """Test description extraction from different document contexts"""
        context_cases = [
            {
                "context": 'Tabular format: XS9826A | 191009727774 | 6"H Metal Ballerina Ornament | 24 | $1.60',
                "product": "XS9826A",
                "expected": "Metal Ballerina Ornament",
            },
            {
                "context": 'Multi-line format:\nXS8911A\n191009710615\n4-3/4"L x 3-1/2"W Cotton Pillow',
                "product": "XS8911A",
                "expected": "Cotton Pillow",
            },
            {
                "context": 'Paragraph format: The XS9482 (UPC: 191009714712) is an 8.25"H Wood Shoe Ornament',
                "product": "XS9482",
                "expected": "Wood Shoe Ornament",
            },
        ]

        for i, case in enumerate(context_cases):
            with self.subTest(case_index=i, product=case["product"]):
                # Act
                description = extract_description_from_product_context(
                    case["context"], case["product"]
                )

                # Assert
                self.assertIn(
                    case["expected"],
                    description,
                    f"Should extract '{case['expected']}' from context case {i}",
                )

    def test_validates_description_quality_standards(self):
        """Test description quality validation"""
        quality_test_cases = [
            (
                'XS9826A - UPC: 191009727774 - 6"H Metal Ballerina Ornament',
                True,
            ),  # High quality
            ("XS9826A Metal Ornament", False),  # Missing UPC, too short
            ("Traditional D-code format", False),  # Placeholder
            (
                "XS9826A - UPC: 191009727774 - Complete Product Description",
                True,
            ),  # Complete
            ("", False),  # Empty
            (
                "XS9826A - Product with meaningful detailed description content",
                True,
            ),  # Good without UPC
        ]

        for i, (description, expected_quality) in enumerate(quality_test_cases):
            with self.subTest(case_index=i, description=description[:50]):
                # Act
                is_quality = validate_description_quality(description, "XS9826A")

                # Assert
                self.assertEqual(
                    is_quality,
                    expected_quality,
                    f"Quality validation failed for case {i}: '{description[:50]}...'",
                )

    def test_handles_upc_extraction_from_document(self):
        """Test automatic UPC extraction when not provided"""
        document_with_upcs = """
        Product Listing:
        XS9826A 191009727774 6"H Metal Ballerina Ornament
        XS8911A 191009710615 Cotton Lumbar Pillow
        XS9482 191009714712 Wood Shoe Ornament
        """

        # Act - Extract description with automatic UPC finding
        description = extract_enhanced_product_description(
            document_with_upcs, "XS9826A", None
        )

        # Assert - Should find and integrate UPC automatically
        self.assertIn("XS9826A", description)
        self.assertIn(
            "191009727774", description, "Should find UPC automatically from document"
        )
        self.assertIn("Metal Ballerina Ornament", description)

    def test_optimizes_description_extraction_performance(self):
        """Test performance optimization for description extraction"""
        # Create large document text
        large_document = generate_large_document_with_products(500)  # 500 products

        start_time = time.time()

        # Act - Extract descriptions for multiple products
        descriptions = []
        for i in range(10):  # Test 10 products
            product_code = f"XS{i:04d}A"
            description = extract_enhanced_product_description(
                large_document, product_code, None
            )
            descriptions.append(description)

        end_time = time.time()
        extraction_time = end_time - start_time

        # Assert - Should complete within reasonable time
        self.assertLess(
            extraction_time, 5.0, "10 descriptions should extract in < 5 seconds"
        )
        self.assertEqual(len(descriptions), 10)
        self.assertTrue(
            all(desc for desc in descriptions), "All descriptions should have content"
        )

        print(
            f"✓ Performance test: Extracted 10 descriptions in {extraction_time:.2f}s"
        )

    def test_extracts_upc_for_product_correctly(self):
        """Test UPC extraction for specific products"""
        document_with_multiple_upcs = """
        XS9826A 191009727774 6"H Metal Ballerina Ornament
        XS8911A 191009710615 Cotton Lumbar Pillow
        XS9482 191009714712 Wood Shoe Ornament
        CF1234A 123456789012 Premium Cotton Product
        """

        upc_test_cases = [
            ("XS9826A", "191009727774"),
            ("XS8911A", "191009710615"),
            ("XS9482", "191009714712"),
            ("CF1234A", "123456789012"),
        ]

        for product_code, expected_upc in upc_test_cases:
            with self.subTest(product_code=product_code):
                # Act
                extracted_upc = extract_upc_for_product(
                    document_with_multiple_upcs, product_code
                )

                # Assert
                self.assertEqual(
                    extracted_upc,
                    expected_upc,
                    f"Should extract UPC {expected_upc} for {product_code}",
                )

    def test_cleans_description_artifacts(self):
        """Test cleaning of description artifacts and formatting issues"""
        artifact_test_cases = [
            (
                "XS9826A - UPC: 191009727774 - Description|||||||",
                "XS9826A - UPC: 191009727774 - Description",
            ),
            (
                "XS9826A - UPC: 191009727774 -   Extra    Spaces   ",
                "XS9826A - UPC: 191009727774 - Extra Spaces",
            ),
            (
                "XS9826A - UPC: 191009727774 - \n\n\nMultiple\n\nNewlines\n\n",
                "XS9826A - UPC: 191009727774 - Multiple Newlines",
            ),
            (
                "XS9826A - UPC: 191009727774 - Description\t\t\tTabs",
                "XS9826A - UPC: 191009727774 - Description Tabs",
            ),
        ]

        for i, (dirty_description, expected_clean) in enumerate(artifact_test_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = clean_description_artifacts(dirty_description)

                # Assert
                self.assertEqual(
                    cleaned, expected_clean, f"Should clean artifacts for case {i}"
                )

    def test_handles_empty_or_none_inputs(self):
        """Test handling of empty or None inputs"""
        # Test None inputs
        result1 = extract_enhanced_product_description(None, "XS9826A", "191009727774")
        self.assertIn("Product description not available", result1)

        # Test empty product code
        result2 = extract_enhanced_product_description("Some text", "", "191009727774")
        self.assertIn("Product description not available", result2)

        # Test empty document text
        result3 = extract_enhanced_product_description("", "XS9826A", "191009727774")
        self.assertIn("Product description not available", result3)

    def test_comprehensive_cs003837319_integration(self):
        """Test comprehensive integration with CS003837319 document for multiple products"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Test multiple products from the Creative-Coop document
        test_products = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS8185"]

        successful_extractions = 0
        total_tests = len(test_products)

        for product_code in test_products:
            with self.subTest(product_code=product_code):
                # Act - Extract enhanced description
                description = extract_enhanced_product_description(
                    self.cs_document_text, product_code, None
                )

                # Assert - Basic quality checks
                self.assertIsInstance(description, str)
                self.assertGreater(
                    len(description),
                    10,
                    f"Description for {product_code} should be meaningful",
                )
                self.assertIn(
                    product_code,
                    description,
                    f"Should contain product code {product_code}",
                )

                # Check if it's not a placeholder
                if (
                    "Traditional D-code format" not in description
                    and "not available" not in description
                ):
                    successful_extractions += 1

        # Calculate success rate
        success_rate = (successful_extractions / total_tests) * 100
        print(
            f"✓ Description extraction success rate: {success_rate:.1f}% ({successful_extractions}/{total_tests})"
        )

        # Should achieve reasonable success rate (aim for improvement)
        self.assertGreaterEqual(
            success_rate,
            60,
            "Should achieve at least 60% success rate in description extraction",
        )


if __name__ == "__main__":
    print("🔴 RED PHASE: Running Enhanced Description Extraction Tests")
    print("⚠️  Expected: All tests should FAIL - functions not implemented yet")
    print("=" * 70)

    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)
