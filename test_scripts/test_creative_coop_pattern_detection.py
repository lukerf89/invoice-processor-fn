"""
Test Creative-Coop product code pattern detection (D-codes and XS-codes)
Implements TDD approach for fixing XS-code detection issues

RED phase: These tests demonstrate current pattern failures with XS codes
GREEN phase: Will be updated after pattern fixes
REFACTOR phase: Will test centralized pattern functions
"""

import pytest
import re
import json
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    extract_creative_coop_product_mappings_corrected,
    process_creative_coop_document,
    extract_line_items_from_entities,
    split_combined_line_item,
    extract_upc_from_text,
)


class TestCreativeCoopPatternDetection:
    """Test Creative-Coop product code pattern detection for both D-codes and XS-codes"""

    def test_xs_code_detection_fails_with_current_pattern(self):
        """RED: Test that current D-code pattern fails to detect XS codes"""
        # Current pattern from main.py line 979
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

        # Creative-Coop XS codes from CS003837319_Error 2.PDF
        xs_codes = [
            "XS9826A",
            "XS8911A",
            "XS9649A",
            "XS9482",
            "XS9840A",
            "XS8185",
            "XS9357",
            "XS7529",
        ]

        test_text = " ".join(xs_codes)
        matches = re.findall(current_pattern, test_text)

        # RED: This should fail with current pattern
        assert (
            len(matches) == 0
        ), f"Current pattern should not match XS codes, but found: {matches}"

    def test_d_code_detection_works_with_current_pattern(self):
        """Test that current pattern correctly detects D codes"""
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

        # Existing D codes from other vendors
        d_codes = ["DA1234A", "DB5678B", "DG9999C", "DH1111"]

        test_text = " ".join(d_codes)
        matches = re.findall(current_pattern, test_text)

        assert len(matches) == len(d_codes)
        assert set(matches) == set(d_codes)

    def test_creative_coop_invoice_patterns_fail_in_text(self):
        """RED: Test Creative-Coop patterns fail in actual invoice text"""
        # Sample text from CS003837319_Error 2.PDF containing XS codes
        invoice_text = """
        Creative Co-Op Seasonal
        XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
        XS8911A 191009710615 4-3/4"L x 3-1/2"W x 10"H Metal 12 0 0 0 each 10.00 8.00 0.00
        XS9649A 191009725688 3"H - 3-1/4"H Paper Mache 24 0 0 24 each 3.50 2.80 67.20
        XS9482 191009714712 8.25"H Wood Shoe Ornament 12 0 0 12 each 3.50 2.80 33.60
        """

        # Current D-code pattern should find no matches
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
        matches = re.findall(current_pattern, invoice_text)

        # RED: Should find no XS codes with current D-pattern
        assert (
            len(matches) == 0
        ), f"Current D-pattern should not match XS codes in invoice text, found: {matches}"

        # But the text clearly contains XS codes that should be detected
        xs_pattern = r"\b(XS\d+[A-Z]?)\b"
        xs_matches = re.findall(xs_pattern, invoice_text)
        assert len(xs_matches) > 0, "Invoice text should contain XS codes"

    def test_xs_code_extraction_from_entity_text(self):
        """RED: Test XS code extraction from entity text fails with current pattern"""
        entity_text = (
            "Product XS9826A Metal Ballerina Ornament UPC: 191009727774 Price: $1.60"
        )

        # Current pattern from line 2203
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
        product_codes = re.findall(current_pattern, entity_text)

        # RED: Should find no matches with current pattern
        assert (
            len(product_codes) == 0
        ), f"Should find no XS codes with D-pattern, found: {product_codes}"

    def test_product_upc_pattern_fails_for_xs_codes(self):
        """RED: Test product-UPC pattern extraction fails for XS codes"""
        line_text = 'XS9826A 191009727774 6"H Metal Ballerina Ornament'

        # Current pattern from line 1780
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\s+(\d{12})"
        matches = re.findall(current_pattern, line_text)

        # RED: Should find no matches
        assert (
            len(matches) == 0
        ), f"Should find no XS-UPC pairs with D-pattern, found: {matches}"

    def test_split_combined_line_item_now_works_for_xs_codes(self):
        """GREEN: Test split_combined_line_item now works for XS codes after pattern updates"""
        combined_text = "XS9826A 191009727774 Metal Ballerina Ornament\nXS8911A 191009710615 Metal Tree"

        # Mock entity object
        class MockEntity:
            def __init__(self, text):
                self.mention_text = text

        mock_entity = MockEntity(combined_text)

        # This should now return split items since patterns are updated
        split_items = split_combined_line_item(combined_text, mock_entity, "")

        # GREEN: Should now return items with updated patterns
        assert (
            len(split_items) > 0
        ), f"Should return split items for XS codes with updated patterns, got: {len(split_items)}"

        # Verify that XS codes are detected in the split items
        descriptions = [item.get("description", "") for item in split_items]
        xs_found = any("XS9826A" in desc or "XS8911A" in desc for desc in descriptions)
        assert xs_found, f"Should find XS codes in descriptions: {descriptions}"

    def test_extract_upc_from_text_fails_for_xs_codes(self):
        """RED: Test extract_upc_from_text fails to find XS codes"""
        document_text = "XS9826A 191009727774 Metal Ballerina Ornament $1.60"
        product_code = "XS9826A"

        # This should return None due to pattern mismatch
        upc_code = extract_upc_from_text(product_code, document_text)

        # RED: Should return None with current patterns
        assert (
            upc_code is None
        ), f"Should return None for XS code UPC extraction, got: {upc_code}"

    def test_comprehensive_xs_code_list_from_invoice(self):
        """RED: Test comprehensive list of XS codes from actual invoice"""
        xs_codes_in_invoice = [
            "XS9826A",
            "XS8911A",
            "XS8912A",
            "XS9089",
            "XS9649A",
            "XS9482",
            "XS9840A",
            "XS8185",
            "XS9357",
            "XS7529",
            "XS7653A",
            "XS8109",
            "XS8379A",
            "XS5747A",
            "XS8838",
            "XS8837",
            "XS3350",
            "XS3844",
            "XS8714",
            "XS5692A",
            "XS9082",
            "XS8694",
            "XS7793A",
            "XS8978",
            "XS9851",
            "XS7604",
            "XS9150",
            "XS9110",
            "XS9665A",
            "XS5388A",
            "XS8571",
            "XS6924",
            "XS6926",
            "XS6929",
            "XS4556",
            "XS1939",
            "XS8622A",
            "XS8385",
            "XS8384",
            "XS6000",
            "XS8531A",
            "XS8708",
            "XS7690",
            "XS7691",
            "XS9105",
            "XS9120",
            "XS5725",
            "XS6032",
            "XS9134A",
            "XS8678",
            "XS6692A",
            "XS8742",
            "XS8741",
            "XS8117",
            "XS6557A",
            "XS5568A",
            "XS9365",
            "XS9366",
            "XS6413A",
            "XS8623A",
            "XS9130",
            "XS9683A",
            "XS6204",
            "XS8855A",
            "XS8840",
            "XS7923A",
            "XS7921A",
            "XS8795",
            "XS8706",
            "XS1304",
            "XS6008A",
            "XS3805",
            "XS9146",
            "XS8119",
            "XS8575A",
            "XS7022A",
            "XS4516A",
            "XS7019",
            "XS9651A",
            "XS7750",
            "XS7544",
            "XS7557",
            "XS7559",
            "XS8161",
            "XS7517",
            "XS7818",
            "XS7819",
            "XS8895",
            "XS7753",
            "XS7756",
            "XS9792",
            "XS5981",
            "XS9279",
            "XS0442",
            "XS5250A",
        ]

        # Current D-code pattern should match none of these
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

        for xs_code in xs_codes_in_invoice:
            matches = re.findall(current_pattern, xs_code)
            # RED: Each XS code should not match current pattern
            assert (
                len(matches) == 0
            ), f"XS code {xs_code} should not match D-pattern, but found: {matches}"

    def test_mixed_d_and_xs_codes_pattern_detection(self):
        """RED: Test mixed D-codes and XS-codes - only D-codes should match currently"""
        mixed_text = "DA1234A XS9826A DB5678B XS8911A DG9999C XS9649A"

        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
        matches = re.findall(current_pattern, mixed_text)

        # Should only match D-codes
        expected_d_codes = ["DA1234A", "DB5678B", "DG9999C"]
        assert len(matches) == 3, f"Should match 3 D-codes, found: {len(matches)}"
        assert set(matches) == set(
            expected_d_codes
        ), f"Should match D-codes only, found: {matches}"


class TestPatternPerformance:
    """Test pattern matching performance to ensure timeout compliance"""

    def test_current_pattern_performance(self):
        """Test current pattern performance baseline"""
        import time

        # Large text with many potential matches
        large_text = " ".join([f"DA{i:04d}A XS{i:04d}A" for i in range(1000)])
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

        start_time = time.time()
        matches = re.findall(current_pattern, large_text)
        end_time = time.time()

        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Should complete within 5ms per entity requirement
        assert (
            processing_time < 50
        ), f"Pattern matching took {processing_time:.2f}ms, should be under 50ms for large text"

        # Should find 1000 D-codes
        assert len(matches) == 1000, f"Should find 1000 D-codes, found: {len(matches)}"


# GREEN phase tests - verify updated patterns work
class TestUpdatedPatternDetection:
    """GREEN: Tests for updated pattern detection after pattern fixes"""

    def test_updated_pattern_detects_both_d_and_xs_codes(self):
        """GREEN: Test updated pattern detects both D-codes and XS-codes"""
        # Updated pattern should match both D-codes and XS-codes
        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"

        # Test D-codes
        d_codes = ["DA1234A", "DB5678B", "DG9999C", "DH1111"]
        d_text = " ".join(d_codes)
        d_matches = re.findall(updated_pattern, d_text)

        assert len(d_matches) == len(
            d_codes
        ), f"Should match all D-codes, found: {d_matches}"
        assert set(d_matches) == set(
            d_codes
        ), f"D-code matches should be exact, found: {d_matches}"

        # Test XS-codes
        xs_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS9840A"]
        xs_text = " ".join(xs_codes)
        xs_matches = re.findall(updated_pattern, xs_text)

        assert len(xs_matches) == len(
            xs_codes
        ), f"Should match all XS-codes, found: {xs_matches}"
        assert set(xs_matches) == set(
            xs_codes
        ), f"XS-code matches should be exact, found: {xs_matches}"

        # Test mixed codes
        mixed_text = "DA1234A XS9826A DB5678B XS8911A"
        mixed_matches = re.findall(updated_pattern, mixed_text)

        expected_mixed = ["DA1234A", "XS9826A", "DB5678B", "XS8911A"]
        assert (
            len(mixed_matches) == 4
        ), f"Should match all mixed codes, found: {mixed_matches}"
        assert set(mixed_matches) == set(
            expected_mixed
        ), f"Mixed matches should include both types, found: {mixed_matches}"

    def test_updated_pattern_detects_xs_codes_in_invoice_text(self):
        """GREEN: Test updated pattern detects XS codes in actual invoice text"""
        # Sample text from CS003837319_Error 2.PDF containing XS codes
        invoice_text = """
        Creative Co-Op Seasonal
        XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
        XS8911A 191009710615 4-3/4"L x 3-1/2"W x 10"H Metal 12 0 0 0 each 10.00 8.00 0.00
        XS9649A 191009725688 3"H - 3-1/4"H Paper Mache 24 0 0 24 each 3.50 2.80 67.20
        XS9482 191009714712 8.25"H Wood Shoe Ornament 12 0 0 12 each 3.50 2.80 33.60
        """

        # Updated pattern should find XS codes
        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"
        matches = re.findall(updated_pattern, invoice_text)

        expected_xs_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482"]
        assert len(matches) >= len(
            expected_xs_codes
        ), f"Should find at least {len(expected_xs_codes)} XS codes, found: {matches}"

        for expected_code in expected_xs_codes:
            assert (
                expected_code in matches
            ), f"Should find {expected_code} in invoice text, found: {matches}"

    def test_updated_product_upc_pattern_detects_xs_codes(self):
        """GREEN: Test updated product-UPC pattern detects XS codes"""
        line_text = "XS9826A 191009727774 Metal Ballerina Ornament"

        # Updated pattern should match XS-UPC pairs
        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\s+(\d{12})"
        matches = re.findall(updated_pattern, line_text)

        # Should find XS-UPC pair
        assert len(matches) == 1, f"Should find 1 XS-UPC pair, found: {matches}"
        assert matches[0] == (
            "XS9826A",
            "191009727774",
        ), f"Should match XS9826A with UPC, found: {matches[0]}"

    def test_comprehensive_xs_codes_detection(self):
        """GREEN: Test comprehensive XS codes detection from invoice"""
        xs_codes_in_invoice = [
            "XS9826A",
            "XS8911A",
            "XS8912A",
            "XS9089",
            "XS9649A",
            "XS9482",
            "XS9840A",
            "XS8185",
            "XS9357",
            "XS7529",
            "XS7653A",
            "XS8109",
        ]

        # Updated pattern should match all XS codes
        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"

        test_text = " ".join(xs_codes_in_invoice)
        matches = re.findall(updated_pattern, test_text)

        assert len(matches) == len(
            xs_codes_in_invoice
        ), f"Should match all XS codes, found {len(matches)} of {len(xs_codes_in_invoice)}"
        assert set(matches) == set(
            xs_codes_in_invoice
        ), f"Should match exact XS codes, found: {matches}"

    def test_pattern_maintains_backward_compatibility(self):
        """GREEN: Test pattern maintains backward compatibility with D-codes"""
        # Existing D-codes should still work
        existing_d_codes = [
            "DA1234A",
            "DB5678B",
            "DG9999C",
            "DH1111",
            "DF6802",
            "DA7891",
        ]

        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"

        test_text = " ".join(existing_d_codes)
        matches = re.findall(updated_pattern, test_text)

        assert len(matches) == len(
            existing_d_codes
        ), f"Should maintain D-code compatibility, found: {matches}"
        assert set(matches) == set(
            existing_d_codes
        ), f"Should match all existing D-codes, found: {matches}"


# REFACTOR phase tests - verify centralized helper functions
class TestCentralizedHelperFunctions:
    """REFACTOR: Tests for centralized pattern constants and helper functions"""

    def test_extract_creative_coop_product_codes_helper(self):
        """REFACTOR: Test centralized extract_creative_coop_product_codes helper function"""
        from main import extract_creative_coop_product_codes

        # Test mixed D-codes and XS-codes
        mixed_text = "DA1234A XS9826A DB5678B XS8911A DG9999 XS9482"
        codes = extract_creative_coop_product_codes(mixed_text)

        expected_codes = [
            "DA1234A",
            "XS9826A",
            "DB5678B",
            "XS8911A",
            "DG9999",
            "XS9482",
        ]
        assert len(codes) == len(
            expected_codes
        ), f"Should find all product codes, found: {codes}"
        assert set(codes) == set(
            expected_codes
        ), f"Should match expected codes, found: {codes}"

        # Test empty text
        empty_codes = extract_creative_coop_product_codes("")
        assert (
            empty_codes == []
        ), f"Should return empty list for empty text, got: {empty_codes}"

        # Test no matches
        no_match_codes = extract_creative_coop_product_codes("ABC123 RANDOM TEXT")
        assert (
            no_match_codes == []
        ), f"Should return empty list for no matches, got: {no_match_codes}"

    def test_extract_creative_coop_product_upc_pairs_helper(self):
        """REFACTOR: Test centralized extract_creative_coop_product_upc_pairs helper function"""
        from main import extract_creative_coop_product_upc_pairs

        # Test XS-UPC pairs
        xs_text = "XS9826A 191009727774 Metal Ballerina XS8911A 191009710615 Metal Tree"
        xs_pairs = extract_creative_coop_product_upc_pairs(xs_text)

        expected_xs_pairs = [("XS9826A", "191009727774"), ("XS8911A", "191009710615")]
        assert len(xs_pairs) == len(
            expected_xs_pairs
        ), f"Should find XS-UPC pairs, found: {xs_pairs}"
        assert (
            xs_pairs == expected_xs_pairs
        ), f"Should match expected XS-UPC pairs, found: {xs_pairs}"

        # Test D-UPC pairs
        d_text = (
            "DA1234A 123456789012 Product Name DB5678B 987654321098 Another Product"
        )
        d_pairs = extract_creative_coop_product_upc_pairs(d_text)

        expected_d_pairs = [("DA1234A", "123456789012"), ("DB5678B", "987654321098")]
        assert len(d_pairs) == len(
            expected_d_pairs
        ), f"Should find D-UPC pairs, found: {d_pairs}"
        assert (
            d_pairs == expected_d_pairs
        ), f"Should match expected D-UPC pairs, found: {d_pairs}"

        # Test mixed pairs
        mixed_text = "XS9826A 191009727774 Metal DA1234A 123456789012 Product"
        mixed_pairs = extract_creative_coop_product_upc_pairs(mixed_text)

        expected_mixed_pairs = [
            ("XS9826A", "191009727774"),
            ("DA1234A", "123456789012"),
        ]
        assert len(mixed_pairs) == len(
            expected_mixed_pairs
        ), f"Should find mixed pairs, found: {mixed_pairs}"
        assert (
            mixed_pairs == expected_mixed_pairs
        ), f"Should match expected mixed pairs, found: {mixed_pairs}"

    def test_centralized_pattern_constants(self):
        """REFACTOR: Test centralized pattern constants"""
        from main import (
            CREATIVE_COOP_PRODUCT_CODE_PATTERN,
            CREATIVE_COOP_PRODUCT_UPC_PATTERN,
        )
        import re

        # Test product code pattern
        test_text = "XS9826A DA1234A XS8911 DB5678B"
        product_matches = re.findall(CREATIVE_COOP_PRODUCT_CODE_PATTERN, test_text)

        expected_products = ["XS9826A", "DA1234A", "XS8911", "DB5678B"]
        assert len(product_matches) == len(
            expected_products
        ), f"Pattern should match all codes, found: {product_matches}"
        assert set(product_matches) == set(
            expected_products
        ), f"Pattern should match expected codes, found: {product_matches}"

        # Test product-UPC pattern
        upc_text = "XS9826A 191009727774 Product DA1234A 123456789012 Item"
        upc_matches = re.findall(CREATIVE_COOP_PRODUCT_UPC_PATTERN, upc_text)

        expected_upc_pairs = [("XS9826A", "191009727774"), ("DA1234A", "123456789012")]
        assert len(upc_matches) == len(
            expected_upc_pairs
        ), f"UPC pattern should match pairs, found: {upc_matches}"
        assert (
            upc_matches == expected_upc_pairs
        ), f"UPC pattern should match expected pairs, found: {upc_matches}"

    def test_helper_functions_performance(self):
        """REFACTOR: Test helper functions performance"""
        from main import (
            extract_creative_coop_product_codes,
            extract_creative_coop_product_upc_pairs,
        )
        import time

        # Large text with many codes
        large_text = " ".join(
            [f"XS{i:04d}A 19100972{i:04d} Product{i}" for i in range(100)]
        )

        # Test product codes extraction performance
        start_time = time.time()
        codes = extract_creative_coop_product_codes(large_text)
        end_time = time.time()

        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert (
            processing_time < 50
        ), f"Product codes extraction took {processing_time:.2f}ms, should be under 50ms"
        assert len(codes) == 100, f"Should extract 100 codes, found: {len(codes)}"

        # Test UPC pairs extraction performance
        start_time = time.time()
        pairs = extract_creative_coop_product_upc_pairs(large_text)
        end_time = time.time()

        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert (
            processing_time < 50
        ), f"UPC pairs extraction took {processing_time:.2f}ms, should be under 50ms"
        assert len(pairs) == 100, f"Should extract 100 UPC pairs, found: {len(pairs)}"


if __name__ == "__main__":
    # Run RED phase tests to demonstrate current failures
    pytest.main(
        [
            __file__,
            "-v",
            "-k",
            "test_xs_code_detection_fails or test_creative_coop_invoice_returns_zero",
        ]
    )
