#!/usr/bin/env python3
"""
Task 11: Multi-Tier Price Extraction Integration - Creative-Coop
RED Phase - Write failing tests for multi-tier price extraction integration
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for importing main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import extract_price_from_table_columns, extract_wholesale_price


def test_tier_1_tabular_price_extraction():
    """Test Tier 1: Tabular column parsing for structured invoices"""

    tabular_text = """
    Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
    XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
    XS8911A      | 191009710615| 4-3/4"L x 3-1/2"W...   | 12      | 0         | 0           | 0         | each | 10.00      | 8.00       | 0.00
    """

    # Test the existing tabular extraction directly (this should pass)
    assert extract_price_from_table_columns(tabular_text, "XS9826A") == 1.60
    assert extract_price_from_table_columns(tabular_text, "XS8911A") == 8.00


def test_tier_2_pattern_based_fallback():
    """Test Tier 2: Pattern-based extraction for formatted text (existing logic)"""

    pattern_text = """
    Creative-Coop Product Listing
    XS9826A Blue Metal Ornament 24 0 lo each $2.50 wholesale $60.00
    DF6802 Ceramic Vase 8 0 Set $12.50 $100.00
    ST1234 Cotton Throw 6 0 each $8.00 retail
    """

    # Test existing pattern-based extraction (this should pass for existing implementation)
    price_xs = extract_wholesale_price(pattern_text)
    assert price_xs is not None, "Should extract some price from pattern text"


def test_multi_tier_fallback_sequence():
    """Test that tiers are tried in correct sequence with proper fallback"""

    # This test will FAIL initially because extract_creative_coop_price_improved doesn't exist yet
    try:
        from main import extract_creative_coop_price_improved

        # Mock the individual tier functions to control their behavior
        with patch("main.extract_price_from_table_columns") as mock_tier1, patch(
            "main.extract_wholesale_price"
        ) as mock_tier2, patch("main.extract_price_from_context") as mock_tier3:

            # Test Tier 1 success (should not call other tiers)
            mock_tier1.return_value = 1.60
            price = extract_creative_coop_price_improved("test text", "XS9826A")
            assert price == 1.60
            mock_tier1.assert_called_once()
            mock_tier2.assert_not_called()
            mock_tier3.assert_not_called()

    except ImportError:
        # Expected to fail in RED phase
        pytest.fail(
            "extract_creative_coop_price_improved not implemented yet (RED phase expected)"
        )


def test_tier_3_context_aware_extraction():
    """Test Tier 3: Context-aware parsing for complex formats"""

    # This test will FAIL initially because extract_price_from_context doesn't exist yet
    try:
        from main import extract_price_from_context

        complex_text = """
        Order Summary for XS9826A
        Product: Metal Ballerina Ornament
        Wholesale Price: $1.60 each
        Retail Price: $2.00 each
        Quantity Ordered: 24

        Item: DF6802
        Description: Blue Ceramic Vase
        Price per unit: $12.50
        Order quantity: 8 pieces
        """

        # Should fall back to Tier 3 for context-aware extraction
        price_xs = extract_price_from_context(complex_text, "XS9826A")
        price_df = extract_price_from_context(complex_text, "DF6802")

        assert price_xs == 1.60
        assert price_df == 12.50

    except ImportError:
        # Expected to fail in RED phase
        pytest.fail(
            "extract_price_from_context not implemented yet (RED phase expected)"
        )


def test_mixed_format_document():
    """Test document containing multiple price format types"""

    mixed_text = """
    Invoice: CS003837319

    Tabular Section:
    Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
    XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40

    Pattern Section:
    DF6802 Ceramic Vase 8 0 Set $12.50 wholesale $100.00

    Context Section:
    Product ST1234:
    Cotton Throw Blanket
    Unit Price: $8.00 wholesale
    Quantity: 6 pieces
    """

    # This test will FAIL initially because extract_creative_coop_price_improved doesn't exist
    try:
        from main import extract_creative_coop_price_improved

        # Each product should be extracted using the appropriate tier
        price_xs = extract_creative_coop_price_improved(mixed_text, "XS9826A")  # Tier 1
        price_df = extract_creative_coop_price_improved(mixed_text, "DF6802")  # Tier 2
        price_st = extract_creative_coop_price_improved(mixed_text, "ST1234")  # Tier 3

        assert price_xs == 1.60
        assert price_df == 12.50
        assert price_st == 8.00

    except ImportError:
        # Expected to fail in RED phase
        pytest.fail(
            "extract_creative_coop_price_improved not implemented yet (RED phase expected)"
        )


def test_price_extraction_performance():
    """Test performance of multi-tier approach doesn't degrade significantly"""
    import time

    # Create large mixed format text
    large_text_parts = []

    # Add tabular section
    large_text_parts.append(
        "Product Code | UPC | Description | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M | List Price | Your Price | Your Extd Price"
    )
    for i in range(100):
        large_text_parts.append(
            f"XS{i:04d}A | 191009{i:06d} | Product {i} | {i+10} | 0 | 0 | {i+10} | each | {2.00+i*0.01:.2f} | {1.60+i*0.008:.2f} | {(i+10)*(1.60+i*0.008):.2f}"
        )

    # Add pattern section
    for i in range(100, 200):
        large_text_parts.append(
            f"DF{i:04d} Product {i} {i+5} 0 Set ${2.00+i*0.01:.2f} wholesale ${(i+5)*(2.00+i*0.01):.2f}"
        )

    large_text = "\n".join(large_text_parts)

    # Test performance for tabular extraction (this should work)
    test_products = ["XS0050A", "XS0099A"]  # Tabular products

    start_time = time.time()

    for product in test_products:
        price = extract_price_from_table_columns(large_text, product)
        assert price is not None, f"Should extract price for {product}"

    end_time = time.time()
    extraction_time = end_time - start_time

    assert (
        extraction_time < 2.0
    ), f"Tabular extraction took {extraction_time:.3f}s, expected < 2.0s"


def test_error_handling_tier_failures():
    """Test error handling when individual tiers fail"""

    # Test with malformed data that might break individual tiers
    malformed_text = """
    Corrupted tabular data:
    XS9826A | | | | | | | | corrupted_price |

    Corrupted pattern data:
    XS9827A invalid format no price

    Empty context:
    XS9828A:
    """

    # Test that existing functions handle failures gracefully
    for product in ["XS9826A", "XS9827A", "XS9828A"]:
        price_tabular = extract_price_from_table_columns(malformed_text, product)
        price_pattern = extract_wholesale_price(malformed_text)

        # Should either return a valid price or None, but not crash
        assert price_tabular is None or isinstance(price_tabular, (int, float))
        assert price_pattern is None or isinstance(price_pattern, (int, float))


def test_cs_error2_integration():
    """Test integration with actual CS003837319_Error 2.PDF format"""

    # Sample from CS Error 2 document (multi-line format)
    cs_error2_sample = """
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

    XS9649A
    191009725688
    8"H x 6.5"W x 4"D Paper Mache
    24
    0
    0
    24
    each
    3.50
    2.80
    67.20
    """

    expected_prices = {
        "XS9826A": 1.60,
        "XS9649A": 2.80,
    }

    # Test existing tabular extraction (this should work based on Task 10)
    for product_code, expected_price in expected_prices.items():
        extracted_price = extract_price_from_table_columns(
            cs_error2_sample, product_code
        )
        assert extracted_price == pytest.approx(
            expected_price, abs=0.01
        ), f"{product_code}: Expected ${expected_price}, got ${extracted_price}"


def test_logging_and_debugging():
    """Test that multi-tier approach provides useful logging for debugging"""

    # This test will FAIL initially because extract_creative_coop_price_improved doesn't exist
    try:
        import io
        import sys
        from contextlib import redirect_stdout

        from main import extract_creative_coop_price_improved

        text = """
        XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | 1.60 | 38.40
        """

        log_output = io.StringIO()

        with redirect_stdout(log_output):
            price = extract_creative_coop_price_improved(text, "XS9826A")

        log_content = log_output.getvalue()

        # Should log which tier was used
        assert "Tier 1" in log_content or "tabular" in log_content.lower()
        assert price == 1.60

    except ImportError:
        # Expected to fail in RED phase
        pytest.fail(
            "extract_creative_coop_price_improved not implemented yet (RED phase expected)"
        )


if __name__ == "__main__":
    print("🔴 RED Phase - Multi-Tier Price Integration Tests")
    print("=" * 60)

    # Run tests that should pass (existing functionality)
    try:
        print("✅ Testing existing tabular extraction...")
        test_tier_1_tabular_price_extraction()
        print("   Tabular extraction: PASS")
    except Exception as e:
        print(f"   Tabular extraction: FAIL - {e}")

    try:
        print("✅ Testing existing pattern extraction...")
        test_tier_2_pattern_based_fallback()
        print("   Pattern extraction: PASS")
    except Exception as e:
        print(f"   Pattern extraction: FAIL - {e}")

    try:
        print("✅ Testing performance...")
        test_price_extraction_performance()
        print("   Performance: PASS")
    except Exception as e:
        print(f"   Performance: FAIL - {e}")

    try:
        print("✅ Testing CS Error 2 integration...")
        test_cs_error2_integration()
        print("   CS Error 2 integration: PASS")
    except Exception as e:
        print(f"   CS Error 2 integration: FAIL - {e}")

    # Run tests that should fail (new functionality)
    print("\n🔴 Expected failures (new functionality not yet implemented):")

    failure_count = 0

    try:
        test_multi_tier_fallback_sequence()
        print("   Multi-tier fallback: UNEXPECTED PASS")
    except Exception:
        print("   Multi-tier fallback: EXPECTED FAIL ✓")
        failure_count += 1

    try:
        test_tier_3_context_aware_extraction()
        print("   Context-aware extraction: UNEXPECTED PASS")
    except Exception:
        print("   Context-aware extraction: EXPECTED FAIL ✓")
        failure_count += 1

    try:
        test_mixed_format_document()
        print("   Mixed format document: UNEXPECTED PASS")
    except Exception:
        print("   Mixed format document: EXPECTED FAIL ✓")
        failure_count += 1

    try:
        test_logging_and_debugging()
        print("   Logging and debugging: UNEXPECTED PASS")
    except Exception:
        print("   Logging and debugging: EXPECTED FAIL ✓")
        failure_count += 1

    print(f"\n🎯 RED Phase Results:")
    print(f"   Expected failures: {failure_count}/4")
    print(f"   Ready for GREEN phase implementation!")
