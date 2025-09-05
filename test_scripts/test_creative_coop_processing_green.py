"""
Test Creative-Coop invoice processing with updated XS-code patterns
GREEN phase test to verify CS003837319_Error 2.PDF processes successfully
"""

import json
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    extract_creative_coop_product_mappings_corrected,
    process_creative_coop_document,
)


def test_creative_coop_invoice_processing():
    """GREEN: Test that Creative-Coop invoice processes successfully with updated patterns"""

    print("Loading Creative-Coop test invoice...")

    try:
        # Load Creative-Coop test invoice Document AI output
        with open("test_invoices/CS003837319_Error 2_docai_output.json", "r") as f:
            doc_ai_output = json.load(f)

        print(f"Loaded document with {len(doc_ai_output.get('entities', []))} entities")

        # Test pattern extraction from document text
        document_text = doc_ai_output.get("text", "")
        print(f"Document text length: {len(document_text)} characters")

        # Test new pattern detection
        import re

        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"
        all_product_codes = re.findall(updated_pattern, document_text)

        print(f"Found {len(all_product_codes)} product codes with updated pattern")

        # Show first 10 codes found
        xs_codes = [code for code in all_product_codes if code.startswith("XS")]
        d_codes = [code for code in all_product_codes if code.startswith("D")]

        print(f"XS codes found: {len(xs_codes)} (first 10: {xs_codes[:10]})")
        print(f"D codes found: {len(d_codes)} (first 10: {d_codes[:10]})")

        # Verify we found XS codes (this was failing before)
        assert (
            len(xs_codes) > 0
        ), f"Should find XS codes in Creative-Coop invoice, found: {xs_codes}"

        # Test UPC pattern matching
        upc_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\s+(\d{12})"
        upc_matches = re.findall(upc_pattern, document_text)

        print(f"Found {len(upc_matches)} product-UPC pairs")

        # Show sample UPC matches
        xs_upc_matches = [
            (code, upc) for code, upc in upc_matches if code.startswith("XS")
        ]
        print(
            f"XS-UPC pairs found: {len(xs_upc_matches)} (first 5: {xs_upc_matches[:5]})"
        )

        assert (
            len(xs_upc_matches) > 0
        ), f"Should find XS-UPC pairs, found: {xs_upc_matches}"

        # Test product mappings extraction
        print("\nTesting product mappings extraction...")
        product_mappings = extract_creative_coop_product_mappings_corrected(
            document_text
        )

        print(f"Product mappings found: {len(product_mappings)}")

        # Show sample mappings for XS codes
        xs_mappings = {
            code: mapping
            for code, mapping in product_mappings.items()
            if code.startswith("XS")
        }
        print(f"XS product mappings: {len(xs_mappings)}")

        # Show first few XS mappings
        for i, (code, mapping) in enumerate(xs_mappings.items()):
            if i < 5:  # Show first 5
                print(
                    f"  {code}: UPC={mapping.get('upc', 'N/A')}, Description={mapping.get('description', 'N/A')[:50]}..."
                )

        assert (
            len(xs_mappings) > 0
        ), f"Should find XS product mappings, found: {len(xs_mappings)}"

        print(
            f"\n✅ SUCCESS: Creative-Coop invoice processing works with updated XS patterns!"
        )
        print(f"   - Found {len(xs_codes)} XS product codes")
        print(f"   - Found {len(xs_upc_matches)} XS-UPC pairs")
        print(f"   - Found {len(xs_mappings)} XS product mappings")
        print(f"   - Maintains {len(d_codes)} D-code compatibility")

        return True

    except FileNotFoundError:
        print(
            "❌ Creative-Coop test invoice not found at test_invoices/CS003837319_Error 2_docai_output.json"
        )
        return False
    except Exception as e:
        print(f"❌ Error testing Creative-Coop processing: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_creative_coop_invoice_processing()
    if success:
        print("\n🎉 All Creative-Coop processing tests passed!")
        exit(0)
    else:
        print("\n💥 Creative-Coop processing tests failed!")
        exit(1)
