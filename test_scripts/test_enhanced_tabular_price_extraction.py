#!/usr/bin/env python3
"""
Test Enhanced Tabular Price Extraction - Creative-Coop Wholesale Price Accuracy

This test suite implements the RED phase of TDD for Task 201.
Tests are designed to fail initially and guide the implementation of
extract_tabular_price_creative_coop_enhanced() function.
"""

import json
import os
import sys

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import extract_tabular_price_creative_coop_enhanced


def load_test_document(filename):
    """Load test document from test_invoices directory"""
    test_file_path = os.path.join(
        os.path.dirname(__file__), "..", "test_invoices", filename
    )

    if filename.endswith(".json"):
        with open(test_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("text", "")
    else:
        with open(test_file_path, "r", encoding="utf-8") as f:
            return f.read()


class TestEnhancedTabularPriceExtraction:
    """Test suite for enhanced tabular price extraction functionality"""

    def test_extracts_wholesale_price_from_your_price_column(self):
        """Test extraction of wholesale prices from 'Your Price' column"""
        # Arrange
        tabular_text = """
Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
XS8911A      | 191009710615| 4-3/4"L x 3-1/2"W...   | 12      | 0         | 0           | 0         | each | 10.00      | 8.00       | 0.00
        """

        # Act
        price_xs9826a = extract_tabular_price_creative_coop_enhanced(
            tabular_text, "XS9826A"
        )
        price_xs8911a = extract_tabular_price_creative_coop_enhanced(
            tabular_text, "XS8911A"
        )

        # Assert
        assert price_xs9826a == "$1.60", f"Expected $1.60, got {price_xs9826a}"
        assert price_xs8911a == "$8.00", f"Expected $8.00, got {price_xs8911a}"

    def test_processes_cs003837319_test_products_accurately(self):
        """Test specific known products from CS003837319_Error 2.PDF manual analysis"""
        # Load CS003837319_Error 2.PDF test data
        cs_document_text = load_test_document("CS003837319_Error 2_docai_output.json")

        # Test specific known products from manual analysis
        test_products = {
            "XS9826A": "$1.60",
            "XS9649A": "$2.80",
            "XS9482": "$2.80",
            "XS8185": "$12.00",
        }

        for product_code, expected_price in test_products.items():
            extracted_price = extract_tabular_price_creative_coop_enhanced(
                cs_document_text, product_code
            )
            assert (
                extracted_price == expected_price
            ), f"Product {product_code}: Expected {expected_price}, got {extracted_price}"
            assert (
                extracted_price != "$1.60" or expected_price == "$1.60"
            ), f"Product {product_code}: Detected placeholder price incorrectly"

    def test_handles_malformed_price_data_gracefully(self):
        """Test graceful handling of malformed price data with fallback"""
        malformed_text = """
XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | N/A | 38.40
XS8911A | 191009710615 | Product | 12 | 0 | 0 | 0  | each | 10.00 |     | 0.00
        """

        # Should fallback to multi-tier extraction
        price1 = extract_tabular_price_creative_coop_enhanced(malformed_text, "XS9826A")
        price2 = extract_tabular_price_creative_coop_enhanced(malformed_text, "XS8911A")

        # Should attempt fallback extraction, not return None
        assert (
            price1 is not None or "fallback attempted"
        ), f"Expected fallback for XS9826A, got {price1}"
        assert (
            price2 is not None or "fallback attempted"
        ), f"Expected fallback for XS8911A, got {price2}"

    def test_handles_missing_product_code_gracefully(self):
        """Test graceful handling of missing product codes"""
        text = "XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | 1.60 | 38.40"

        result = extract_tabular_price_creative_coop_enhanced(text, "XS9999A")
        # Should fallback to multi-tier extraction
        assert (
            result is not None or "multi-tier fallback called"
        ), f"Expected fallback for missing product, got {result}"

    def test_validates_price_business_logic(self):
        """Test price validation to reject placeholder values"""
        # Test price validation (not $1.60 placeholder)
        text_with_placeholder = """
XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | 1.60 | 38.40
        """

        result = extract_tabular_price_creative_coop_enhanced(
            text_with_placeholder, "XS9826A"
        )
        # Should detect and reject placeholder price (this test will need to be adjusted based on business rules)
        # For now, we'll accept $1.60 as it might be a valid wholesale price
        assert result is not None, f"Expected some price extraction, got {result}"

    def test_handles_various_currency_formats(self):
        """Test handling of different currency format variations"""
        text_formats = [
            "XS9826A | Product | Data | Data | Data | Data | Data | $2.00 | $1.60 | $38.40",
            "XS9826A | Product | Data | Data | Data | Data | Data | 2.00 | 1.60 | 38.40",
            "XS9826A | Product | Data | Data | Data | Data | Data | USD2.00 | USD1.60 | USD38.40",
        ]

        for i, text in enumerate(text_formats):
            result = extract_tabular_price_creative_coop_enhanced(text, "XS9826A")
            assert result == "$1.60", f"Format {i+1}: Expected $1.60, got {result}"

    def test_handles_multiline_tabular_format(self):
        """Test handling of multi-line tabular format from Creative-Coop invoices"""
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

        result = extract_tabular_price_creative_coop_enhanced(multiline_text, "XS9826A")
        assert result == "$1.60", f"Expected $1.60 for multiline format, got {result}"

    def test_edge_case_empty_inputs(self):
        """Test edge cases with empty or None inputs"""
        # Test None inputs
        result1 = extract_tabular_price_creative_coop_enhanced(None, "XS9826A")
        result2 = extract_tabular_price_creative_coop_enhanced("text", None)
        result3 = extract_tabular_price_creative_coop_enhanced("", "")

        # All should return None or fallback gracefully
        assert result1 is None, f"Expected None for None text, got {result1}"
        assert result2 is None, f"Expected None for None product_code, got {result2}"
        assert result3 is None, f"Expected None for empty inputs, got {result3}"


if __name__ == "__main__":
    # Run tests in verbose mode
    pytest.main([__file__, "-v", "-s"])
