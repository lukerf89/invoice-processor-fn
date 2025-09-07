#!/usr/bin/env python3
"""
Test Context-Aware Description Cleaning - Artifact Removal and Quality Enhancement

Tests for Task 211: Sophisticated description cleaning system for Creative-Coop
invoices that removes processing artifacts, table headers, and Document AI noise
while preserving meaningful product information.

TDD Test Implementation (RED Phase):
- All tests will initially fail
- Tests define expected behavior for context-aware description cleaning
- Tests cover happy path, error handling, and edge cases
"""

import json
import os
import re
import sys
import time
import unittest
from unittest.mock import MagicMock, Mock

# Add parent directory to path to import main functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import (
        apply_context_aware_cleaning,
        clean_description_artifacts,
        clean_table_headers,
        remove_duplicate_codes,
        remove_processing_artifacts,
    )
except ImportError:
    # Functions don't exist yet - this is expected in RED phase
    pass


def load_test_document(filename):
    """Load test document for description cleaning testing"""
    test_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_invoices", filename
    )

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file not found: {test_file_path}")

    with open(test_file_path, "r", encoding="utf-8") as f:
        doc_data = json.load(f)

    return doc_data.get("text", "")


class TestContextAwareDescriptionCleaning(unittest.TestCase):
    """Test cases for context-aware description cleaning and artifact removal"""

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

    def test_removes_common_processing_artifacts(self):
        """Test removal of common Document AI processing artifacts"""
        # Arrange - Descriptions with common Document AI artifacts
        artifact_cases = [
            {
                "dirty": 'XS9826A - UPC: 191009727774 - Traditional D-code format 6"H Metal Ballerina',
                "clean": 'XS9826A - UPC: 191009727774 - 6"H Metal Ballerina',
            },
            {
                "dirty": "XS8911A $$ Price $$ Cotton Lumbar Pillow",
                "clean": "XS8911A Cotton Lumbar Pillow",
            },
            {
                "dirty": "XS9482 || separator || Wood Shoe Ornament",
                "clean": "XS9482 Wood Shoe Ornament",
            },
            {
                "dirty": "XS8185 Product Code Description Cotton Pillow",
                "clean": "XS8185 Cotton Pillow",
            },
        ]

        for i, case in enumerate(artifact_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = clean_description_artifacts(case["dirty"])

                # Assert
                self.assertEqual(
                    cleaned, case["clean"], f"Artifact cleaning failed for case {i}"
                )
                self.assertNotIn("Traditional D-code format", cleaned)
                self.assertNotIn("$$", cleaned)
                self.assertNotIn("||", cleaned)

    def test_removes_table_headers_intelligently(self):
        """Test intelligent removal of table headers from descriptions"""
        # Test removal of table headers that got included in descriptions
        header_cases = [
            {
                "dirty": "Product Code XS9826A Description Metal Ballerina Ornament Qty Price",
                "clean": "XS9826A Metal Ballerina Ornament",
            },
            {
                "dirty": "UPC XS8911A 191009710615 Cotton Pillow Description",
                "clean": "XS8911A 191009710615 Cotton Pillow",
            },
            {
                "dirty": "Your Price List Price XS9482 Wood Ornament Unit",
                "clean": "XS9482 Wood Ornament",
            },
            {
                "dirty": "Qty Ord Qty Shipped XS8185 Cotton Lumbar Pillow",
                "clean": "XS8185 Cotton Lumbar Pillow",
            },
        ]

        for i, case in enumerate(header_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = clean_table_headers(case["dirty"])

                # Assert
                self.assertEqual(
                    cleaned, case["clean"], f"Header cleaning failed for case {i}"
                )
                self.assertNotIn("Product Code", cleaned)
                self.assertNotIn("Description", cleaned)
                self.assertNotIn("Your Price", cleaned)

    def test_removes_duplicate_product_codes(self):
        """Test removal of duplicate product codes in descriptions"""
        duplicate_cases = [
            {
                "dirty": 'XS9826A XS9826A 6"H Metal Ballerina Ornament',
                "product_code": "XS9826A",
                "clean": 'XS9826A 6"H Metal Ballerina Ornament',
            },
            {
                "dirty": "XS8911A - UPC: 191009710615 - XS8911A Cotton Pillow",
                "product_code": "XS8911A",
                "clean": "XS8911A - UPC: 191009710615 - Cotton Pillow",
            },
            {
                "dirty": "XS9482 Product XS9482 Wood Ornament XS9482",
                "product_code": "XS9482",
                "clean": "XS9482 Product Wood Ornament",
            },
        ]

        for i, case in enumerate(duplicate_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = remove_duplicate_codes(case["dirty"], case["product_code"])

                # Assert
                self.assertEqual(
                    cleaned, case["clean"], f"Duplicate removal failed for case {i}"
                )
                # Should have only one or two occurrences of product code (UPC format allowed)
                self.assertLessEqual(
                    cleaned.count(case["product_code"]),
                    2,
                    f"Should have ≤2 occurrences of {case['product_code']}",
                )

    def test_preserves_meaningful_product_information(self):
        """Test that cleaning preserves important product details"""
        preservation_cases = [
            {
                "dirty": 'XS9826A - UPC: 191009727774 - 6"H x 4"W Metal Ballerina Ornament, Holiday Decor',
                "preserved_elements": [
                    "XS9826A",
                    "191009727774",
                    '6"H',
                    '4"W',
                    "Metal",
                    "Ballerina",
                    "Ornament",
                    "Holiday",
                ],
            },
            {
                "dirty": 'XS8911A Product Code 4-3/4"L × 3-1/2"W Cotton Lumbar Pillow Description',
                "preserved_elements": [
                    "XS8911A",
                    '4-3/4"L',
                    '3-1/2"W',
                    "Cotton",
                    "Lumbar",
                    "Pillow",
                ],
            },
            {
                "dirty": "XS9482 Traditional D-code format Wood Shoe Ornament Holiday",
                "preserved_elements": ["XS9482", "Wood", "Shoe", "Ornament", "Holiday"],
            },
        ]

        for i, case in enumerate(preservation_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = clean_description_artifacts(case["dirty"])

                # Assert - Should preserve important elements
                for element in case["preserved_elements"]:
                    self.assertIn(
                        element,
                        cleaned,
                        f"Should preserve '{element}' in cleaned description for case {i}",
                    )

                # Should not contain artifacts
                self.assertNotIn("Traditional D-code format", cleaned)
                self.assertNotIn("Product Code", cleaned)
                self.assertNotIn("Description", cleaned)

    def test_processes_creative_coop_descriptions_comprehensively(self):
        """Test comprehensive cleaning of actual Creative-Coop descriptions"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Test cleaning of actual descriptions from the document
        test_products = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS8185"]

        for product_code in test_products:
            with self.subTest(product_code=product_code):
                # Extract a sample description from the document
                # Look for lines containing the product code
                lines = self.cs_document_text.split("\n")
                product_lines = [
                    line
                    for line in lines
                    if product_code in line and len(line.strip()) > 10
                ]

                if product_lines:
                    original_description = product_lines[0]

                    # Act
                    cleaned = clean_description_artifacts(original_description)

                    # Assert
                    self.assertIsInstance(cleaned, str)
                    self.assertIn(product_code, cleaned)
                    self.assertNotIn("Traditional D-code format", cleaned)

                    # Should be cleaner (remove redundant/noise elements)
                    self.assertNotIn("Product Code", cleaned)
                    self.assertNotIn("Description", cleaned)

    # =================================================================
    # ERROR HANDLING TESTS
    # =================================================================

    def test_handles_empty_or_invalid_descriptions(self):
        """Test handling of empty or invalid description inputs"""
        invalid_cases = [
            "",  # Empty string
            None,  # None value
            "   ",  # Whitespace only
            "$$$$",  # Only artifacts
            "Product Code UPC Description Qty Price",  # Only headers
            "|||||||",  # Only separators
        ]

        for i, invalid_input in enumerate(invalid_cases):
            with self.subTest(case_index=i, input=str(invalid_input)):
                try:
                    # Act
                    result = clean_description_artifacts(invalid_input)

                    # Assert - Should handle gracefully
                    if invalid_input is None:
                        self.assertTrue(result == "" or result is None)
                    else:
                        self.assertIsInstance(result, str)
                        self.assertGreaterEqual(
                            len(result.strip()), 0, "Should not crash"
                        )

                        # For pure artifacts, result should be empty or minimal
                        if invalid_input in ["$$$$", "|||||||"]:
                            self.assertEqual(result.strip(), "")

                except Exception as e:
                    self.fail(
                        f"Should handle invalid input gracefully, but got: {e} for input: {invalid_input}"
                    )

    def test_handles_malformed_product_codes_in_cleaning(self):
        """Test cleaning when product codes are malformed or inconsistent"""
        malformed_cases = [
            "INVALID123 Product Description",
            "XS Metal Ornament Without Valid Code",
            "123456 Numeric Product Code",
            "   XS9826A   Extra Spaces Product   ",
            "",  # Empty string
            "NoProductCodeHere Description",
        ]

        for i, malformed in enumerate(malformed_cases):
            with self.subTest(case_index=i, description=malformed):
                # Act
                result = clean_description_artifacts(malformed)

                # Assert - Should handle malformed input without crashing
                self.assertIsInstance(result, str)
                self.assertGreaterEqual(len(result), 0)

    def test_handles_excessive_artifacts(self):
        """Test handling of descriptions with excessive artifacts"""
        excessive_artifacts = """
        Product Code XS9826A UPC Description Traditional D-code format
        $$ Price $$ Your Price List Price || separator ||
        6"H Metal Ballerina Ornament Holiday Decor
        Qty Price Unit each $$$
        """

        # Act
        cleaned = clean_description_artifacts(excessive_artifacts)

        # Assert - Should clean extensively while preserving core content
        self.assertIn("XS9826A", cleaned)
        self.assertIn("Metal Ballerina Ornament", cleaned)
        self.assertIn("Holiday Decor", cleaned)
        self.assertNotIn("Traditional D-code format", cleaned)
        self.assertNotIn("$$", cleaned)
        self.assertNotIn("Product Code", cleaned)
        self.assertNotIn("Your Price", cleaned)

    # =================================================================
    # EDGE CASE TESTS
    # =================================================================

    def test_cleans_various_spacing_and_formatting_issues(self):
        """Test cleaning of spacing and formatting artifacts"""
        formatting_cases = [
            {
                "dirty": 'XS9826A     6"H    Metal     Ballerina   Ornament',
                "clean_pattern": "single spaces between words",
            },
            {
                "dirty": "XS8911A,,,Cotton,,,Lumbar,,,Pillow",
                "clean_pattern": "remove excessive commas",
            },
            {
                "dirty": "XS9482\n\n\nWood\n\nShoe\n\nOrnament",
                "clean_pattern": "normalize line breaks",
            },
            {
                "dirty": "XS8185   -   -   -   Cotton Pillow",
                "clean_pattern": "clean excessive dashes",
            },
        ]

        for i, case in enumerate(formatting_cases):
            with self.subTest(case_index=i, pattern=case["clean_pattern"]):
                # Act
                cleaned = clean_description_artifacts(case["dirty"])

                # Assert - Should normalize formatting
                self.assertFalse(
                    re.search(r"\s{2,}", cleaned), "Should not have multiple spaces"
                )  # No multiple spaces
                self.assertFalse(
                    re.search(r",{2,}", cleaned), "Should not have multiple commas"
                )  # No multiple commas
                self.assertFalse(
                    re.search(r"\n{2,}", cleaned), "Should not have multiple newlines"
                )  # No multiple newlines
                self.assertFalse(
                    re.search(r"-{3,}", cleaned), "Should not have excessive dashes"
                )  # No excessive dashes

    def test_handles_special_product_naming_conventions(self):
        """Test cleaning while preserving Creative-Coop naming conventions"""
        naming_cases = [
            {
                "dirty": "XS9826A Product Code 6\"H Metal Ballerina's Ornament",
                "preserved": ['6"H', "Ballerina's", "Ornament"],
            },
            {
                "dirty": 'CF1234A Description 4-3/4"L × 3-1/2"W Cotton & Linen Blend',
                "preserved": ['4-3/4"L', '3-1/2"W', "&", "Cotton"],
            },
            {
                "dirty": "CD5678B UPC 50% Cotton, 50% Polyester Material",
                "preserved": ["50%", "Cotton,", "Polyester"],
            },
        ]

        for i, case in enumerate(naming_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = clean_description_artifacts(case["dirty"])

                # Assert - Should preserve naming conventions
                for preserved_element in case["preserved"]:
                    self.assertIn(
                        preserved_element,
                        cleaned,
                        f"Should preserve '{preserved_element}' for case {i}",
                    )

    def test_optimizes_cleaning_performance(self):
        """Test performance optimization for description cleaning"""
        # Create large batch of descriptions to clean
        dirty_descriptions = []
        for i in range(100):
            dirty_desc = f"Product Code XS{i:04d}A UPC {i:012d} Description Traditional D-code format $$ Price $$ Cotton Product {i} Qty Price"
            dirty_descriptions.append(dirty_desc)

        start_time = time.time()

        # Act - Clean all descriptions
        cleaned_descriptions = []
        for dirty_desc in dirty_descriptions:
            cleaned = clean_description_artifacts(dirty_desc)
            cleaned_descriptions.append(cleaned)

        end_time = time.time()
        cleaning_time = end_time - start_time

        # Assert - Should complete within reasonable time
        self.assertLess(
            cleaning_time, 5.0, "100 descriptions should clean in < 5 seconds"
        )
        self.assertEqual(len(cleaned_descriptions), 100)
        self.assertTrue(
            all(
                "Traditional D-code format" not in desc for desc in cleaned_descriptions
            )
        )
        self.assertTrue(
            all("Product Code" not in desc for desc in cleaned_descriptions)
        )

        print(f"✓ Performance test: Cleaned 100 descriptions in {cleaning_time:.2f}s")

    def test_validates_context_aware_cleaning_decisions(self):
        """Test that cleaning decisions are context-aware"""
        context_cases = [
            {
                "description": "XS9826A Description Metal Product Description Ornament",
                "context": "product_listing",
                "expected_removals": [
                    "Description"
                ],  # Remove redundant "Description" words
                "expected_preservations": ["Metal", "Product", "Ornament"],
            },
            {
                "description": "Your Price XS8911A $1.60 Your Price Cotton Pillow",
                "context": "price_table",
                "expected_removals": ["Your Price"],  # Remove table column headers
                "expected_preservations": ["XS8911A", "$1.60", "Cotton", "Pillow"],
            },
        ]

        for i, case in enumerate(context_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = apply_context_aware_cleaning(
                    case["description"], case["context"]
                )

                # Assert - Context-aware decisions
                for removal in case["expected_removals"]:
                    # Should reduce redundant elements
                    removal_count = case["description"].count(removal)
                    cleaned_count = cleaned.count(removal)
                    self.assertLess(
                        cleaned_count,
                        removal_count,
                        f"Should reduce '{removal}' occurrences for case {i}",
                    )

                for preservation in case["expected_preservations"]:
                    self.assertIn(
                        preservation,
                        cleaned,
                        f"Should preserve '{preservation}' for case {i}",
                    )

    def test_removes_processing_artifacts_specifically(self):
        """Test removal of specific Document AI processing artifacts"""
        processing_cases = [
            {
                "dirty": "XS9826A 191009727774 191009727774 Metal Ornament",  # Duplicate UPC
                "expected_single_upc": True,
            },
            {
                "dirty": "XS8911A Cotton each each Pillow",  # Duplicate units
                "expected_single_unit": True,
            },
            {
                "dirty": "XS9482 $ $ Wood Ornament Price",  # Double dollar signs
                "expected_no_double_dollar": True,
            },
            {
                "dirty": "XS8185,,,,Cotton,,,Pillow",  # Excessive commas
                "expected_normalized_commas": True,
            },
        ]

        for i, case in enumerate(processing_cases):
            with self.subTest(case_index=i):
                # Act
                cleaned = remove_processing_artifacts(case["dirty"])

                # Assert - Specific artifact removal
                if case.get("expected_single_upc"):
                    upc_pattern = r"\b\d{12}\b"
                    upc_matches = re.findall(upc_pattern, cleaned)
                    self.assertLessEqual(
                        len(upc_matches), 1, "Should have at most one UPC code"
                    )

                if case.get("expected_single_unit"):
                    self.assertLessEqual(
                        cleaned.count("each"), 1, "Should have at most one 'each'"
                    )

                if case.get("expected_no_double_dollar"):
                    self.assertNotIn(
                        "$ $", cleaned, "Should not have double dollar signs"
                    )

                if case.get("expected_normalized_commas"):
                    self.assertFalse(
                        re.search(r",{3,}", cleaned),
                        "Should not have excessive commas",
                    )

    def test_integrates_with_enhanced_description_extraction(self):
        """Test integration with Task 210 enhanced description extraction"""
        # Simulate descriptions from enhanced extraction that need cleaning
        enhanced_descriptions = [
            'XS9826A - UPC: 191009727774 - Traditional D-code format 6"H Metal Ballerina Ornament',
            "XS8911A - UPC: 191009710615 - Product Code Cotton Lumbar Pillow Description",
            "XS9649A - UPC: 191009725688 - Your Price Paper Mache Ornament List Price",
        ]

        for i, description in enumerate(enhanced_descriptions):
            with self.subTest(case_index=i, product=description.split()[0]):
                # Act - Apply cleaning to enhanced description
                cleaned = clean_description_artifacts(description)

                # Assert - Should maintain enhanced format while cleaning artifacts
                product_code = description.split()[0]
                self.assertIn(product_code, cleaned)
                self.assertIn("UPC:", cleaned)  # Should preserve UPC format
                self.assertNotIn("Traditional D-code format", cleaned)
                self.assertNotIn("Product Code", cleaned)
                self.assertNotIn("Your Price", cleaned)
                self.assertNotIn("List Price", cleaned)


if __name__ == "__main__":
    print("🔴 RED PHASE: Running Context-Aware Description Cleaning Tests")
    print("⚠️  Expected: All tests should FAIL - functions not implemented yet")
    print("=" * 70)

    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)
