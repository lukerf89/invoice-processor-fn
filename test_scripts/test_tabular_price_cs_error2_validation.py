#!/usr/bin/env python3
"""
Validation Test for Tabular Price Column Parser with CS003837319_Error 2.PDF

This test validates that extract_price_from_table_columns() works correctly
with the actual CS003837319_Error 2 Document AI output to extract wholesale prices.
"""

import json
import os
import sys

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    extract_creative_coop_product_codes,
    extract_creative_coop_product_upc_pairs,
    extract_price_from_table_columns,
)


def test_cs_error2_tabular_price_extraction():
    """Test tabular price extraction on actual CS Error 2 document"""

    # Load the actual Document AI output
    docai_path = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    with open(docai_path, "r") as f:
        docai_data = json.load(f)

    # Extract full text from Document AI output
    full_text = docai_data["text"]

    print("=== CS Error 2 Tabular Price Extraction Test ===\n")

    # First, let's find the product codes in the document
    product_codes = extract_creative_coop_product_codes(full_text)
    print(
        f"Found {len(product_codes)} product codes: {product_codes[:10]}..."
    )  # Show first 10

    # Extract product-UPC pairs
    product_upc_pairs = extract_creative_coop_product_upc_pairs(full_text)
    print(f"Found {len(product_upc_pairs)} product-UPC pairs")

    # Test tabular price extraction for key products
    test_products = [
        "XS9826A",  # 6"H Metal Ballerina Ornament
        "XS9649A",  # Paper Mache item
        "XS9482",  # Wood Shoe Ornament
        "XS8185",  # Cotton Lumbar Pillow
        "XS9515A",  # Another product
    ]

    successful_extractions = 0
    total_tests = 0

    print("\n=== Tabular Price Extraction Results ===")

    for product_code in test_products:
        if product_code in full_text:
            total_tests += 1
            price = extract_price_from_table_columns(full_text, product_code)

            if price is not None:
                successful_extractions += 1
                print(f"✓ {product_code}: ${price:.2f}")
            else:
                print(f"✗ {product_code}: No price extracted")

    # Test with all detected product codes
    print(f"\n=== Testing All Detected Product Codes ===")
    all_successful = 0
    all_total = 0

    for product_code in product_codes:
        all_total += 1
        price = extract_price_from_table_columns(full_text, product_code)

        if price is not None:
            all_successful += 1

    print(
        f"Successfully extracted prices for {all_successful}/{all_total} products ({all_successful/all_total*100:.1f}%)"
    )

    # Success rate analysis
    if successful_extractions >= 3:  # At least 3 out of test products should work
        print(
            f"\n✓ VALIDATION PASSED: Extracted prices for {successful_extractions}/{total_tests} test products"
        )
    else:
        print(
            f"\n✗ VALIDATION FAILED: Only extracted prices for {successful_extractions}/{total_tests} test products"
        )

    return successful_extractions, total_tests, all_successful, all_total


def check_tabular_structure_in_document():
    """Check if the document contains proper tabular structure"""

    docai_path = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    with open(docai_path, "r") as f:
        docai_data = json.load(f)

    full_text = docai_data["text"]

    print("\n=== Document Structure Analysis ===")

    # Look for tabular indicators
    pipe_lines = [
        line
        for line in full_text.split("\n")
        if "|" in line and len(line.split("|")) > 5
    ]
    print(f"Found {len(pipe_lines)} lines with pipe separators (potential table rows)")

    # Show first few tabular lines
    if pipe_lines:
        print("\nFirst few tabular lines:")
        for i, line in enumerate(pipe_lines[:5]):
            columns = [col.strip() for col in line.split("|")]
            print(f"  Line {i+1}: {len(columns)} columns - {line[:100]}...")

    # Look for key column headers
    header_indicators = ["Product Code", "UPC", "Your Price", "List Price"]
    found_headers = []

    for indicator in header_indicators:
        if indicator in full_text:
            found_headers.append(indicator)

    print(f"\nFound table headers: {found_headers}")

    return len(pipe_lines) > 0, found_headers


if __name__ == "__main__":
    """Run validation test for CS Error 2 tabular price extraction"""

    print("Validating tabular price extraction with CS003837319_Error 2.PDF...\n")

    # Check document structure
    has_tables, headers = check_tabular_structure_in_document()

    if has_tables:
        print("✓ Document contains tabular structure")
    else:
        print("✗ Document may not contain proper tabular structure")

    # Test price extraction
    successful, total_test, all_successful, all_total = (
        test_cs_error2_tabular_price_extraction()
    )

    print(f"\n=== FINAL VALIDATION RESULTS ===")
    print(
        f"Test Products: {successful}/{total_test} ({successful/total_test*100:.1f}%) successful extractions"
    )
    print(
        f"All Products: {all_successful}/{all_total} ({all_successful/all_total*100:.1f}%) successful extractions"
    )

    if successful >= 3 and all_successful >= 20:
        print("✓ VALIDATION PASSED: Tabular price extraction is working correctly")
        exit(0)
    elif successful >= 3:
        print(
            "⚠️  PARTIAL SUCCESS: Test products working, but overall extraction rate may be low"
        )
        exit(0)
    else:
        print("✗ VALIDATION FAILED: Tabular price extraction needs improvement")
        exit(1)
