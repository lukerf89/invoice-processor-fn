#!/usr/bin/env python3
"""
Task 06 - RED Phase: Failing tests for tabular quantity column parser
Creative-Coop CS003837319_Error 2.PDF format

This implements TDD RED phase with comprehensive failing tests for the new
tabular quantity extraction algorithm.
"""

import time
from unittest.mock import Mock, patch

import pytest


def test_extract_quantity_from_table_columns_basic_case():
    """Test basic quantity extraction from tabular Creative-Coop format"""
    # Arrange - Sample from CS003837319_Error 2.PDF
    sample_text = """
    XS9826A   191009727774   6"H Metal Ballerina Ornament,   24  0  0  24  each  2.00  1.60  38.40
    XS8911A   191009710615   4-3/4"L x 3-1/2"W x 10"H Metal  12  0  0  0   each  10.00 8.00  0.00
    """

    # Import the function we need to implement
    from main import extract_quantity_from_table_columns

    # Act & Assert - These will fail initially (RED phase)
    assert extract_quantity_from_table_columns(sample_text, "XS9826A") == 24
    assert extract_quantity_from_table_columns(sample_text, "XS8911A") == 12


def test_extract_quantity_handles_zero_quantities():
    """Test handling of products with zero ordered quantities"""
    sample_text = """
    XS8911A   191009710615   4-3/4"L x 3-1/2"W x 10"H Metal  0   0  0  0   each  10.00 8.00  0.00
    XS9482    191009714712   8.25"H Wood Shoe Ornament        12  0  0  12  each  3.50  2.80  33.60
    """

    from main import extract_quantity_from_table_columns

    assert extract_quantity_from_table_columns(sample_text, "XS8911A") == 0
    assert extract_quantity_from_table_columns(sample_text, "XS9482") == 12


def test_extract_quantity_multiline_descriptions():
    """Test products with multi-line descriptions that break column alignment"""
    sample_text = """
    XS9840A   191009727910   2-1/2"H 3-1/4"H Metal &          24  14  0  24  each  3.50  2.80  67.20
                             Tariff Surcharge
    XS8185    191009721666   20"Lx12"H Cotton Lumbar Pillow   16  0   0  16  each  15.00 12.00 192.00
    """

    from main import extract_quantity_from_table_columns

    assert extract_quantity_from_table_columns(sample_text, "XS9840A") == 24
    assert extract_quantity_from_table_columns(sample_text, "XS8185") == 16


def test_extract_quantity_product_not_found():
    """Test behavior when product code is not in text"""
    sample_text = (
        "XS9826A   191009727774   Description   24  0  0  24  each  2.00  1.60  38.40"
    )

    from main import extract_quantity_from_table_columns

    assert extract_quantity_from_table_columns(sample_text, "NOTFOUND") is None


def test_extract_quantity_malformed_table():
    """Test error handling for malformed table data"""
    sample_text = """
    XS9826A   incomplete row data
    XS8911A   191009710615   Description but missing numbers
    """

    from main import extract_quantity_from_table_columns

    assert extract_quantity_from_table_columns(sample_text, "XS9826A") is None
    assert extract_quantity_from_table_columns(sample_text, "XS8911A") is None


def test_extract_quantity_performance_large_invoice():
    """Test performance with large invoice text (>20KB)"""
    # Create large sample with 100+ products
    large_text = ""
    for i in range(100):
        large_text += f"XS{i:04d}A   191009727{i:03d}   Test Product {i}   {i+1}  0  0  {i+1}  each  2.00  1.60  38.40\n"

    from main import extract_quantity_from_table_columns

    start_time = time.time()
    result = extract_quantity_from_table_columns(large_text, "XS0050A")
    end_time = time.time()

    assert result == 51  # i=50, quantity = i+1 = 51
    assert (end_time - start_time) < 0.5  # Less than 500ms


def test_extract_quantity_real_cs_error2_format():
    """Test with actual CS003837319_Error 2.PDF format patterns"""
    actual_format = """
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

    from main import extract_quantity_from_table_columns

    # Should extract 24 as the ordered quantity
    assert extract_quantity_from_table_columns(actual_format, "XS9826A") == 24


def test_extract_quantity_mixed_single_and_multiline():
    """Test mixed format with both single-line and multi-line products"""
    mixed_text = """
    XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
    XS9649A
    191009725688
    3"H - 3-1/4"H Paper Mache
    24
    0
    0
    24
    each
    3.50
    2.80
    67.20
    XS9482 191009714712 8.25"H Wood Shoe Ornament 12 0 0 12 each 3.50 2.80 33.60
    """

    from main import extract_quantity_from_table_columns

    # All three formats should work
    assert (
        extract_quantity_from_table_columns(mixed_text, "XS9826A") == 24
    )  # Single line
    assert (
        extract_quantity_from_table_columns(mixed_text, "XS9649A") == 24
    )  # Multi-line
    assert (
        extract_quantity_from_table_columns(mixed_text, "XS9482") == 12
    )  # Single line


def test_extract_quantity_cs_error2_specific_products():
    """Test specific products that appear in CS003837319_Error 2.PDF"""
    cs_error2_sample = """
    Creative Co-Op Seasonal
    XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
    Tariff Surcharge 5.76
    XS8911A 191009710615 12 0 0 0 each 10.00 8.00 0.00
    4-3/4"L x 3-1/2"W x 10"H Metal
    Tariff Surcharge 0.00
    XS9482 191009714712 12 0 0 12 each 3.50 2.80 33.60
    8.25"H Wood Shoe Ornament
    Tariff Surcharge 5.04
    XS9840A 191009727910 24 14 0 24 each 3.50 2.80 67.20
    2-1/2"H 3-1/4"H Metal &
    Tariff Surcharge 10.08
    XS8185 191009721666 20"Lx12"H Cotton Lumbar Pillow 16 0 0 16 each 15.00 12.00 192.00
    Tariff Surcharge 28.80
    """

    from main import extract_quantity_from_table_columns

    # Test critical products from the actual invoice
    assert extract_quantity_from_table_columns(cs_error2_sample, "XS9826A") == 24
    assert extract_quantity_from_table_columns(cs_error2_sample, "XS8911A") == 12
    assert extract_quantity_from_table_columns(cs_error2_sample, "XS9482") == 12
    assert extract_quantity_from_table_columns(cs_error2_sample, "XS9840A") == 24
    assert extract_quantity_from_table_columns(cs_error2_sample, "XS8185") == 16


def test_extract_quantity_edge_cases():
    """Test edge cases for robust parsing"""
    edge_cases = """
    # Very long description wrapping
    XS7529 191009690856 14" Rd Metal Leaves & Flowers Extra Long Description That Spans Multiple Words 18 0 0 18 each 10.00 8.00 144.00

    # Numbers in description
    XS3350 191009571414 S/3 28"L x 18"W Cotton Tea Towels with 12 Patterns 12 0 0 12 Set 10.00 8.00 96.00

    # Decimal quantities (should still extract as integer)
    XS8838 191009709855 4" Rd x 8"H Glass Canister 6.0 0 0 6 each 7.00 5.60 33.60
    """

    from main import extract_quantity_from_table_columns

    assert extract_quantity_from_table_columns(edge_cases, "XS7529") == 18
    assert (
        extract_quantity_from_table_columns(edge_cases, "XS3350") == 12
    )  # Should get quantity, not description number
    assert (
        extract_quantity_from_table_columns(edge_cases, "XS8838") == 6
    )  # Should handle decimal


def test_extract_quantity_boundary_conditions():
    """Test boundary conditions and error scenarios"""
    from main import extract_quantity_from_table_columns

    # Empty text
    assert extract_quantity_from_table_columns("", "XS9826A") is None

    # None text
    assert extract_quantity_from_table_columns(None, "XS9826A") is None

    # Empty product code
    sample_text = "XS9826A 191009727774 Description 24 0 0 24 each 2.00 1.60 38.40"
    assert extract_quantity_from_table_columns(sample_text, "") is None

    # None product code
    assert extract_quantity_from_table_columns(sample_text, None) is None


if __name__ == "__main__":
    # Run specific test to verify RED phase (should fail)
    print("🔴 Running Task 06 RED Phase Tests - Should FAIL until GREEN implementation")
    print("=" * 70)

    try:
        test_extract_quantity_from_table_columns_basic_case()
        print("❌ Basic case test should have failed (function not implemented)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Basic case test failed as expected - {e}")

    try:
        test_extract_quantity_cs_error2_specific_products()
        print("❌ CS Error 2 test should have failed (function not implemented)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: CS Error 2 test failed as expected - {e}")

    print(
        "\n🎯 Task 06 RED Phase Complete: All tests should fail until GREEN implementation"
    )
