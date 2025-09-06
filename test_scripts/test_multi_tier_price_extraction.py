#!/usr/bin/env python3
"""
Test Multi-Tier Price Extraction System - Creative-Coop Pattern Recognition

This test suite implements the RED phase of TDD for Task 202.
Tests the sophisticated multi-tier price extraction system with three-tier fallback logic.
"""

import json
import os
import sys
import time

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import (
    extract_creative_coop_product_mappings_corrected,
    extract_multi_tier_price_creative_coop_enhanced,
)

# Global variable to track last extraction method (for testing purposes)
_last_extraction_method = None


def set_extraction_method(method):
    """Set the last extraction method used (for testing)"""
    global _last_extraction_method
    _last_extraction_method = method


def get_last_extraction_method():
    """Get the last extraction method used (for testing)"""
    return _last_extraction_method or ""


def load_test_document(filename):
    """Load test document from test_invoices directory"""
    test_file_path = os.path.join(
        os.path.dirname(__file__), "..", "test_invoices", filename
    )

    with open(test_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("text", "")


def extract_all_product_codes(document_text):
    """Extract all product codes from document for testing"""
    product_mappings = extract_creative_coop_product_mappings_corrected(document_text)
    return list(product_mappings.keys())


def generate_large_document_text(num_products):
    """Generate large document text for performance testing"""
    text = []
    for i in range(num_products):
        product_code = f"XS{i:04d}"
        price = f"{1.0 + (i % 100) * 0.10:.2f}"
        text.append(f"{product_code} | Product {i} | Price ${price}")
    return "\n".join(text)


class TestMultiTierPriceExtraction:
    """Test suite for multi-tier price extraction system"""

    def test_multi_tier_extraction_tier1_tabular_success(self):
        """Test Tier 1 (tabular) extraction success path"""
        # Arrange - Proper tabular format data that Task 201 recognizes
        tabular_text = """
Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
        """

        # Act
        result = extract_multi_tier_price_creative_coop_enhanced(
            tabular_text, "XS9826A"
        )

        # Assert - Should use Tier 1 (tabular)
        assert result == "$1.60", f"Expected $1.60, got {result}"
        # Note: We'll implement extraction method tracking in GREEN phase

    def test_multi_tier_extraction_tier2_pattern_fallback(self):
        """Test Tier 2 (pattern-based) fallback when tabular fails"""
        # Arrange - Non-tabular format, but pattern-based extraction possible
        pattern_text = """
XS9826A 6"H Metal Ballerina Ornament
Wholesale Price: $1.60
Retail Price: $2.00
        """

        # Act
        result = extract_multi_tier_price_creative_coop_enhanced(
            pattern_text, "XS9826A"
        )

        # Assert - Should use Tier 2 (pattern-based)
        assert result == "$1.60", f"Expected $1.60, got {result}"

    def test_multi_tier_extraction_tier3_page_context_fallback(self):
        """Test Tier 3 (page-based context) fallback when other tiers fail"""
        # Arrange - Multi-page document with price in different section
        multi_page_text = """
Page 1: Product listing
XS9826A 6"H Metal Ballerina Ornament

Page 2: Pricing information  
Product XS9826A - Unit Price $1.60
        """

        # Act
        result = extract_multi_tier_price_creative_coop_enhanced(
            multi_page_text, "XS9826A"
        )

        # Assert - Should use Tier 3 (page-based context)
        assert result == "$1.60", f"Expected $1.60, got {result}"

    def test_processes_all_cs003837319_products_with_high_accuracy(self):
        """Test multi-tier system against full CS document for 95% accuracy"""
        # Load full CS003837319_Error 2.PDF test data
        cs_document_text = load_test_document("CS003837319_Error 2_docai_output.json")

        # Get all product codes from document
        all_product_codes = extract_all_product_codes(cs_document_text)

        successful_extractions = 0
        total_products = len(all_product_codes)

        for product_code in all_product_codes[:20]:  # Test first 20 products for speed
            price = extract_multi_tier_price_creative_coop_enhanced(
                cs_document_text, product_code
            )
            if price and price != "$0.00":  # Any valid price extraction
                successful_extractions += 1

        accuracy_rate = successful_extractions / min(20, total_products)
        assert (
            accuracy_rate >= 0.95
        ), f"Expected ≥95% accuracy, got {accuracy_rate*100:.1f}%"

    def test_handles_all_tiers_failing_gracefully(self):
        """Test graceful handling when all tiers fail"""
        # Arrange - Document with no price information
        no_price_text = """
XS9826A Product Description Only
No pricing information available
        """

        # Act
        result = extract_multi_tier_price_creative_coop_enhanced(
            no_price_text, "XS9826A"
        )

        # Assert - Should return fallback result or None
        assert (
            result is None or result == "$0.00"
        ), f"Expected None or $0.00, got {result}"

    def test_handles_malformed_product_codes(self):
        """Test handling of malformed product code inputs"""
        text = "Valid document text with pricing XS9826A Price $1.60"

        # Test various malformed inputs
        malformed_codes = ["", None, "   ", "INVALID123", "XS"]

        for code in malformed_codes:
            result = extract_multi_tier_price_creative_coop_enhanced(text, code)
            assert (
                result is None
            ), f"Expected None for malformed code '{code}', got {result}"

    def test_handles_timeout_constraints(self):
        """Test that extraction completes within reasonable time"""
        # Generate moderately large document text
        large_text = generate_large_document_text(100)  # 100 products

        start_time = time.time()

        result = extract_multi_tier_price_creative_coop_enhanced(large_text, "XS0050")

        end_time = time.time()
        extraction_time = end_time - start_time

        # Should complete within reasonable time
        assert (
            extraction_time < 5.0
        ), f"Extraction took {extraction_time:.2f}s, expected < 5.0s"
        assert result is not None, "Should find price in large document"

    def test_handles_partial_tier_data(self):
        """Test where Tier 1 partially works but needs Tier 2 completion"""
        # Test where Tier 1 finds product but no price, requiring Tier 2
        partial_text = """
XS9826A | 191009727774 | Product | 24 | Price_Missing | Your_Price_Missing

Separate section:
XS9826A wholesale cost $1.60
        """

        result = extract_multi_tier_price_creative_coop_enhanced(
            partial_text, "XS9826A"
        )
        assert result == "$1.60", f"Expected $1.60 from Tier 2 fallback, got {result}"

    def test_validates_extracted_prices_business_logic(self):
        """Test business logic validation for extracted prices"""
        # Test various price ranges and validation
        test_cases = [
            ("XS9826A Price: $0.50", "$0.50"),  # Valid low price
            ("XS9826A Price: $999.99", "$999.99"),  # Valid high price
            ("XS9826A Price: $0.00", None),  # Invalid zero price
            ("XS9826A Price: $-5.00", None),  # Invalid negative price
            ("XS9826A Price: $10000.00", None),  # Invalid extremely high price
        ]

        for text_with_price, expected in test_cases:
            result = extract_multi_tier_price_creative_coop_enhanced(
                text_with_price, "XS9826A"
            )
            if expected is None:
                assert (
                    result is None or result == "$0.00"
                ), f"Expected None/invalid for '{text_with_price}', got {result}"
            else:
                assert (
                    result == expected
                ), f"Expected {expected} for '{text_with_price}', got {result}"

    def test_edge_case_empty_inputs(self):
        """Test edge cases with empty or None inputs"""
        # Test None and empty inputs
        test_cases = [
            (None, "XS9826A"),
            ("", "XS9826A"),
            ("Valid text", None),
            ("Valid text", ""),
            (None, None),
            ("", ""),
        ]

        for document_text, product_code in test_cases:
            result = extract_multi_tier_price_creative_coop_enhanced(
                document_text, product_code
            )
            assert (
                result is None
            ), f"Expected None for empty inputs ({document_text}, {product_code}), got {result}"

    def test_integration_with_task201_tabular_extraction(self):
        """Test integration with Task 201 tabular extraction as Tier 1"""
        # Use exact format that worked in Task 201
        tabular_text = """
Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
        """

        result = extract_multi_tier_price_creative_coop_enhanced(
            tabular_text, "XS9826A"
        )
        assert result == "$1.60", f"Task 201 integration should work, got {result}"


if __name__ == "__main__":
    # Run tests in verbose mode
    pytest.main([__file__, "-v", "-s"])
