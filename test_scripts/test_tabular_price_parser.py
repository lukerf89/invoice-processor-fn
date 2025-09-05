#!/usr/bin/env python3
"""
RED Phase - TDD Implementation for Tabular Price Column Parser
Tests for extract_price_from_table_columns() function

This file implements comprehensive failing tests for Creative-Coop
tabular format price extraction as specified in Task 10.
"""

import os
import sys
import time
from unittest.mock import Mock

import pytest

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function we're testing (will fail initially - RED phase)
try:
    from main import extract_price_from_table_columns
except ImportError:
    # Function doesn't exist yet - this is expected in RED phase
    def extract_price_from_table_columns(text, product_code):
        raise NotImplementedError(
            "extract_price_from_table_columns not implemented yet"
        )


def test_extract_price_from_basic_tabular_format():
    """Test basic tabular price extraction from structured columns"""

    # Sample tabular format from CS003837319_Error 2.PDF
    tabular_text = """
    Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
    XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
    XS8911A      | 191009710615| 4-3/4"L x 3-1/2"W...   | 12      | 0         | 0           | 0         | each | 10.00      | 8.00       | 0.00
    XS9482       | 191009714712| 8.25"H Wood Shoe...     | 12      | 0         | 0           | 12        | each | 3.50       | 2.80       | 33.60
    """

    # Test price extraction for each product
    assert extract_price_from_table_columns(tabular_text, "XS9826A") == 1.60
    assert extract_price_from_table_columns(tabular_text, "XS8911A") == 8.00
    assert extract_price_from_table_columns(tabular_text, "XS9482") == 2.80


def test_extract_price_handles_currency_symbols():
    """Test price extraction with various currency symbol formats"""

    text_with_currency = """
    XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | $2.00 | $1.60 | $38.40
    XS8911A | 191009710615 | Product | 12 | 0 | 0 | 0  | each | 10.00 | 8.00  | 0.00
    XS9482  | 191009714712 | Product | 12 | 0 | 0 | 12 | each | €3.50 | €2.80 | €33.60
    """

    assert extract_price_from_table_columns(text_with_currency, "XS9826A") == 1.60
    assert extract_price_from_table_columns(text_with_currency, "XS8911A") == 8.00
    assert extract_price_from_table_columns(text_with_currency, "XS9482") == 2.80


def test_extract_price_handles_malformed_data():
    """Test price extraction with malformed or missing price data"""

    malformed_text = """
    XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | N/A | 38.40
    XS8911A | 191009710615 | Product | 12 | 0 | 0 | 0  | each | 10.00 |     | 0.00
    XS9482  | 191009714712 | Product | 12 | 0 | 0 | 12 | each | 3.50 | Invalid | 33.60
    """

    # Should return None or 0.0 for invalid prices
    assert extract_price_from_table_columns(malformed_text, "XS9826A") is None
    assert extract_price_from_table_columns(malformed_text, "XS8911A") is None
    assert extract_price_from_table_columns(malformed_text, "XS9482") is None


def test_extract_price_handles_whitespace_variations():
    """Test price extraction with various whitespace and formatting variations"""

    whitespace_text = """
    XS9826A    |   191009727774  | Product Name           |  24  |   0   |    0    |  24   | each |  2.00  |  1.60  |  38.40
      XS8911A  | 191009710615    | Another Product        |  12  |   0   |    0    |   0   | each | 10.00  |  8.00  |   0.00
    XS9482     |191009714712     |Third Product           | 12   | 0     | 0       | 12    |each  |3.50    |2.80    |33.60
    """

    assert extract_price_from_table_columns(whitespace_text, "XS9826A") == 1.60
    assert extract_price_from_table_columns(whitespace_text, "XS8911A") == 8.00
    assert extract_price_from_table_columns(whitespace_text, "XS9482") == 2.80


def test_extract_price_handles_zero_prices():
    """Test price extraction for products with zero wholesale prices"""

    zero_price_text = """
    XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | 0.00 | 0.00
    XS8911A | 191009710615 | Product | 12 | 0 | 0 | 0  | each | 10.00 | 0    | 0
    """

    assert extract_price_from_table_columns(zero_price_text, "XS9826A") == 0.00
    assert extract_price_from_table_columns(zero_price_text, "XS8911A") == 0.00


def test_extract_price_product_not_found():
    """Test price extraction when product code is not found in text"""

    text = """
    XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | 1.60 | 38.40
    """

    assert extract_price_from_table_columns(text, "XS9999A") is None
    assert extract_price_from_table_columns(text, "") is None
    assert extract_price_from_table_columns("", "XS9826A") is None


def test_extract_price_performance():
    """Test price extraction performance with large tabular data"""

    # Generate large tabular data
    large_text_lines = []
    for i in range(1000):
        large_text_lines.append(
            f"XS{i:04d}A | 191009{i:06d} | Product {i} | {i+10} | 0 | 0 | {i+10} | each | {2.00+i*0.1:.2f} | {1.60+i*0.08:.2f} | {(i+10)*(1.60+i*0.08):.2f}"
        )

    large_text = "\n".join(large_text_lines)

    start_time = time.time()
    price = extract_price_from_table_columns(large_text, "XS0500A")
    end_time = time.time()

    extraction_time = end_time - start_time
    assert (
        extraction_time < 1.0
    ), f"Extraction took {extraction_time:.3f}s, expected < 1.0s"
    assert price == pytest.approx(41.60, abs=0.01)


def test_extract_price_cs_error2_specific_products():
    """Test price extraction for specific products from CS003837319_Error 2.PDF"""

    # Load actual CS Error 2 document for testing
    cs_error2_text = """
    XS9826A | 191009727774 | 6"H Metal Ballerina Ornament | 24 | 0 | 0 | 24 | each | 2.00 | 1.60 | 38.40
    XS9649A | 191009725688 | 8"H x 6.5"W x 4"D Paper Mache | 24 | 0 | 0 | 24 | each | 3.50 | 2.80 | 67.20
    XS9482  | 191009714712 | 8.25"H Wood Shoe Ornament | 12 | 0 | 0 | 12 | each | 3.50 | 2.80 | 33.60
    XS8185  | 191009721666 | 18"L x 12"W Cotton Lumbar Pillow | 16 | 0 | 0 | 16 | each | 15.00 | 12.00 | 192.00
    """

    # Test specific expected prices from manual PDF analysis
    expected_prices = {
        "XS9826A": 1.60,
        "XS9649A": 2.80,
        "XS9482": 2.80,
        "XS8185": 12.00,
    }

    for product_code, expected_price in expected_prices.items():
        extracted_price = extract_price_from_table_columns(cs_error2_text, product_code)
        assert extracted_price == pytest.approx(
            expected_price, abs=0.01
        ), f"{product_code}: Expected ${expected_price}, got ${extracted_price}"


def test_extract_price_edge_cases_various_formats():
    """Test edge cases with various price formatting scenarios"""

    edge_case_text = """
    XS1001 | 191009000001 | Product 1 | 10 | 0 | 0 | 10 | each | 5.99  | 4.79   | 47.90
    XS1002 | 191009000002 | Product 2 | 20 | 0 | 0 | 20 | each | 12.50 | 10.00  | 200.00
    XS1003 | 191009000003 | Product 3 | 5  | 0 | 0 | 5  | each | 99.99 | 79.99  | 399.95
    """

    assert extract_price_from_table_columns(edge_case_text, "XS1001") == 4.79
    assert extract_price_from_table_columns(edge_case_text, "XS1002") == 10.00
    assert extract_price_from_table_columns(edge_case_text, "XS1003") == 79.99


def test_extract_price_handles_mixed_separators():
    """Test price extraction with mixed column separators and formats"""

    mixed_separator_text = """
    XS2001|191009000011|Product A|5|0|0|5|each|3.25|2.60|13.00
    XS2002 | 191009000012 | Product B | 8 | 0 | 0 | 8 | each | 7.50 | 6.00 | 48.00
    XS2003    |    191009000013    |    Product C    |    12    |    0    |    0    |    12    |    each    |    10.75    |    8.60    |    103.20
    """

    assert extract_price_from_table_columns(mixed_separator_text, "XS2001") == 2.60
    assert extract_price_from_table_columns(mixed_separator_text, "XS2002") == 6.00
    assert extract_price_from_table_columns(mixed_separator_text, "XS2003") == 8.60


if __name__ == "__main__":
    """Run tests directly to demonstrate RED phase failures"""
    print("=== TDD RED PHASE - Running Tests (Expected to FAIL) ===\n")

    # Run tests and expect them to fail since extract_price_from_table_columns doesn't exist yet
    try:
        test_extract_price_from_basic_tabular_format()
        print("✗ test_extract_price_from_basic_tabular_format UNEXPECTEDLY PASSED")
    except Exception as e:
        print(f"✓ test_extract_price_from_basic_tabular_format FAILED as expected: {e}")

    try:
        test_extract_price_handles_currency_symbols()
        print("✗ test_extract_price_handles_currency_symbols UNEXPECTEDLY PASSED")
    except Exception as e:
        print(f"✓ test_extract_price_handles_currency_symbols FAILED as expected: {e}")

    try:
        test_extract_price_handles_malformed_data()
        print("✗ test_extract_price_handles_malformed_data UNEXPECTEDLY PASSED")
    except Exception as e:
        print(f"✓ test_extract_price_handles_malformed_data FAILED as expected: {e}")

    try:
        test_extract_price_cs_error2_specific_products()
        print("✗ test_extract_price_cs_error2_specific_products UNEXPECTEDLY PASSED")
    except Exception as e:
        print(
            f"✓ test_extract_price_cs_error2_specific_products FAILED as expected: {e}"
        )

    print(f"\n=== RED PHASE COMPLETE ===")
    print("All tests failed as expected. Ready for GREEN phase implementation.")
