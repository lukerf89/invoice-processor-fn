#!/usr/bin/env python3
"""
Debug script to analyze CS Error 2 document format for tabular price extraction
"""

import json
import re
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import extract_price_from_table_columns


def analyze_cs_error2_format():
    """Analyze the actual format of CS Error 2 document"""

    # Load the actual Document AI output
    docai_path = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    with open(docai_path, "r") as f:
        docai_data = json.load(f)

    # Extract full text from Document AI output
    full_text = docai_data["text"]

    print("=== CS Error 2 Format Analysis ===\n")

    # Find specific product codes and analyze their context
    test_products = ["XS9826A", "XS9649A", "XS9482", "XS8185"]

    for product_code in test_products:
        print(f"\n--- Analyzing {product_code} ---")

        lines = full_text.split("\n")

        for i, line in enumerate(lines):
            if product_code in line and line.strip():
                print(f"Line {i}: {line}")

                # Look at surrounding lines for context
                print("Context:")
                for j in range(max(0, i - 2), min(len(lines), i + 3)):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j}: {lines[j]}")

                # Extract prices from this line
                price_pattern = r"\b(\d+\.\d{2})\b"
                prices = re.findall(price_pattern, line)
                print(f"Found prices in line: {prices}")

                # Test our function on this specific line
                extracted_price = extract_price_from_table_columns(
                    full_text, product_code
                )
                print(f"Extracted price: {extracted_price}")

                break

    # Look for patterns of multi-line products
    print(f"\n=== Multi-line Product Pattern Analysis ===")

    # Find where XS9826A appears and show more context
    xs9826a_pos = full_text.find("XS9826A")
    if xs9826a_pos != -1:
        context = full_text[xs9826a_pos - 100 : xs9826a_pos + 300]
        print("XS9826A Context:")
        print(context)
        print("\n" + "=" * 50)

    # Look for price patterns near products
    print(f"\n=== Price Pattern Analysis ===")

    # Find typical price sequences
    price_sequences = re.findall(
        r"(\d+\.\d{2})\s+(\d+\.\d{2})\s+(\d+\.\d{2})", full_text
    )
    print(f"Found {len(price_sequences)} three-price sequences:")
    for i, seq in enumerate(price_sequences[:5]):  # Show first 5
        print(f"  {i+1}: {seq[0]} -> {seq[1]} -> {seq[2]}")

    # Check for specific XS9826A price pattern
    xs9826a_section = full_text[
        full_text.find("XS9826A") : full_text.find("XS9826A") + 200
    ]
    prices_in_section = re.findall(r"\b(\d+\.\d{2})\b", xs9826a_section)
    print(f"\nPrices near XS9826A: {prices_in_section}")


if __name__ == "__main__":
    analyze_cs_error2_format()
