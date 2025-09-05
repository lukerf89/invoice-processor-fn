#!/usr/bin/env python3
"""Debug quantity extraction issues in CS Error 2 processing"""

import json

from main import (
    extract_creative_coop_quantity_from_price_context,
    extract_quantity_from_table_columns,
)


def load_cs_error2_text():
    """Load the CS Error 2 document text for testing"""
    json_file = "test_invoices/CS003837319_Error 2_docai_output.json"

    with open(json_file, "r") as f:
        doc_data = json.load(f)

    return doc_data.get("text", "")


def test_quantity_extraction():
    """Test quantity extraction for problematic products"""
    text = load_cs_error2_text()

    # Test products that showed incorrect quantities
    test_products = [
        ("XS3844", "Should be 4, got 191009722922"),
        ("XS5388A", "Should be 24, got 191009707608"),
        ("XS9826A", "Should be 24, got 24 - CORRECT"),
        ("XS8185", "Should be 16, got 16 - CORRECT"),
    ]

    print("🔍 Debugging Quantity Extraction Issues")
    print("=" * 50)

    for product_code, description in test_products:
        qty1 = extract_quantity_from_table_columns(text, product_code)
        qty2 = extract_creative_coop_quantity_from_price_context(text, product_code)
        print(f"{product_code}: table={qty1}, price_context={qty2} ({description})")

        # Show context around this product
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if product_code in line:
                print(f"  Context lines around {product_code}:")
                for j in range(max(0, i - 2), min(len(lines), i + 5)):
                    prefix = ">>>" if j == i else "   "
                    print(f"  {prefix} [{j:3d}] {lines[j][:100]}")
                print()
                break


if __name__ == "__main__":
    test_quantity_extraction()
