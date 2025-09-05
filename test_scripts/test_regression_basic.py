"""
Basic regression test to verify existing vendor processing still works
after Creative-Coop XS-code pattern updates
"""

import sys
import os
import re

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    extract_creative_coop_product_codes,
    extract_creative_coop_product_upc_pairs,
    CREATIVE_COOP_PRODUCT_CODE_PATTERN,
    CREATIVE_COOP_PRODUCT_UPC_PATTERN,
)


def test_d_code_compatibility():
    """Test that existing D-code functionality still works"""
    print("Testing D-code compatibility...")

    # Test D-codes that should still work
    d_code_text = "DA1234A DB5678B DG9999C DH1111"

    # Using new helper function
    d_codes = extract_creative_coop_product_codes(d_code_text)
    print(f"Found D-codes with helper: {d_codes}")

    # Using pattern constant directly
    direct_matches = re.findall(CREATIVE_COOP_PRODUCT_CODE_PATTERN, d_code_text)
    print(f"Found D-codes with pattern: {direct_matches}")

    expected_d_codes = ["DA1234A", "DB5678B", "DG9999C", "DH1111"]

    assert set(d_codes) == set(
        expected_d_codes
    ), f"Helper function should find D-codes: {d_codes}"
    assert set(direct_matches) == set(
        expected_d_codes
    ), f"Pattern should find D-codes: {direct_matches}"

    print("✅ D-code compatibility maintained")


def test_xs_code_functionality():
    """Test that XS-code functionality works"""
    print("Testing XS-code functionality...")

    # Test XS-codes
    xs_code_text = "XS9826A XS8911A XS9649A XS9482"

    # Using new helper function
    xs_codes = extract_creative_coop_product_codes(xs_code_text)
    print(f"Found XS-codes with helper: {xs_codes}")

    # Using pattern constant directly
    direct_matches = re.findall(CREATIVE_COOP_PRODUCT_CODE_PATTERN, xs_code_text)
    print(f"Found XS-codes with pattern: {direct_matches}")

    expected_xs_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482"]

    assert set(xs_codes) == set(
        expected_xs_codes
    ), f"Helper function should find XS-codes: {xs_codes}"
    assert set(direct_matches) == set(
        expected_xs_codes
    ), f"Pattern should find XS-codes: {direct_matches}"

    print("✅ XS-code functionality working")


def test_upc_pattern_functionality():
    """Test that UPC pattern functionality works for both D and XS codes"""
    print("Testing UPC pattern functionality...")

    # Test mixed UPC patterns
    mixed_upc_text = "DA1234A 123456789012 Product XS9826A 191009727774 Ornament"

    # Using helper function
    upc_pairs = extract_creative_coop_product_upc_pairs(mixed_upc_text)
    print(f"Found UPC pairs with helper: {upc_pairs}")

    # Using pattern constant directly
    direct_pairs = re.findall(CREATIVE_COOP_PRODUCT_UPC_PATTERN, mixed_upc_text)
    print(f"Found UPC pairs with pattern: {direct_pairs}")

    expected_pairs = [("DA1234A", "123456789012"), ("XS9826A", "191009727774")]

    assert (
        upc_pairs == expected_pairs
    ), f"Helper should find mixed UPC pairs: {upc_pairs}"
    assert (
        direct_pairs == expected_pairs
    ), f"Pattern should find mixed UPC pairs: {direct_pairs}"

    print("✅ UPC pattern functionality working for both D and XS codes")


def test_non_creative_coop_patterns_unaffected():
    """Test that non-Creative-Coop patterns are unaffected"""
    print("Testing non-Creative-Coop patterns...")

    # These patterns should NOT match our Creative-Coop patterns
    non_cc_text = "ABC123 SKU456 ISBN789 PROD001"

    cc_matches = extract_creative_coop_product_codes(non_cc_text)
    print(f"Creative-Coop pattern matches in non-CC text: {cc_matches}")

    assert (
        len(cc_matches) == 0
    ), f"Creative-Coop patterns should not match non-CC codes: {cc_matches}"

    print("✅ Non-Creative-Coop patterns unaffected")


def test_pattern_performance():
    """Test that pattern performance is still good"""
    print("Testing pattern performance...")

    import time

    # Large text with mixed patterns
    large_text = " ".join(
        [
            f"DA{i:04d}A 12345678{i:04d} Product{i} XS{i:04d}B 19100972{i:04d} Item{i}"
            for i in range(100)
        ]
    )

    # Test product codes extraction
    start_time = time.time()
    codes = extract_creative_coop_product_codes(large_text)
    end_time = time.time()

    processing_time = (end_time - start_time) * 1000
    print(f"Product codes extraction: {processing_time:.2f}ms for 200 codes")

    assert (
        processing_time < 100
    ), f"Should complete in under 100ms, took: {processing_time:.2f}ms"
    assert (
        len(codes) == 200
    ), f"Should find 200 codes (100 D + 100 XS), found: {len(codes)}"

    # Test UPC pairs extraction
    start_time = time.time()
    pairs = extract_creative_coop_product_upc_pairs(large_text)
    end_time = time.time()

    processing_time = (end_time - start_time) * 1000
    print(f"UPC pairs extraction: {processing_time:.2f}ms for 200 pairs")

    assert (
        processing_time < 100
    ), f"Should complete in under 100ms, took: {processing_time:.2f}ms"
    assert len(pairs) == 200, f"Should find 200 UPC pairs, found: {len(pairs)}"

    print("✅ Pattern performance maintained")


if __name__ == "__main__":
    print("🧪 Running Basic Regression Tests...")
    print("=" * 50)

    try:
        test_d_code_compatibility()
        test_xs_code_functionality()
        test_upc_pattern_functionality()
        test_non_creative_coop_patterns_unaffected()
        test_pattern_performance()

        print("\n" + "=" * 50)
        print("🎉 ALL REGRESSION TESTS PASSED!")
        print("✅ Creative-Coop XS-code patterns work correctly")
        print("✅ Existing D-code functionality maintained")
        print("✅ Performance requirements met")
        print("✅ No interference with other vendor patterns")

    except Exception as e:
        print(f"\n❌ REGRESSION TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
