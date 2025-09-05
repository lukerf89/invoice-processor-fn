#!/usr/bin/env python3
"""
Debug multi-tier price extraction issues
"""

import os
import sys

# Add parent directory to path for importing main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import (
    extract_creative_coop_price_improved,
    extract_price_from_context,
    extract_price_from_table_columns,
    extract_wholesale_price,
)


def test_tabular_extraction_debug():
    """Debug tabular price extraction issues"""

    print("🔍 Testing tabular extraction...")

    # Test the pipe-separated format first
    tabular_text = """
    Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
    XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
    XS8911A      | 191009710615| 4-3/4"L x 3-1/2"W...   | 12      | 0         | 0           | 0         | each | 10.00      | 8.00       | 0.00
    """

    print(f"Tabular text format:")
    print(tabular_text[:200] + "...")
    print()

    price1 = extract_price_from_table_columns(tabular_text, "XS9826A")
    price2 = extract_price_from_table_columns(tabular_text, "XS8911A")

    print(f"XS9826A price: {price1} (expected: 1.60)")
    print(f"XS8911A price: {price2} (expected: 8.00)")
    print()

    # Test the multi-line format from CS Error 2
    cs_error2_text = """
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

    print("CS Error 2 multi-line format:")
    print(cs_error2_text)
    print()

    price3 = extract_price_from_table_columns(cs_error2_text, "XS9826A")
    print(f"XS9826A price from CS Error 2: {price3} (expected: 1.60)")
    print()


def test_multi_tier_debug():
    """Debug multi-tier integration"""

    print("🔍 Testing multi-tier integration...")

    # Test with tabular format
    tabular_text = """
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

    print("Testing multi-tier with tabular format:")
    price = extract_creative_coop_price_improved(tabular_text, "XS9826A")
    print(f"Result: {price}")
    print()

    # Test with pattern format
    pattern_text = """
    Creative-Coop Product Listing
    XS9826A Blue Metal Ornament 24 0 lo each $2.50 wholesale $60.00
    """

    print("Testing multi-tier with pattern format:")
    price = extract_creative_coop_price_improved(pattern_text, "XS9826A")
    print(f"Result: {price}")
    print()

    # Test with context format
    context_text = """
    Order Summary for XS9826A
    Product: Metal Ballerina Ornament
    Wholesale Price: $1.60 each
    Retail Price: $2.00 each
    Quantity Ordered: 24
    """

    print("Testing multi-tier with context format:")
    price = extract_creative_coop_price_improved(context_text, "XS9826A")
    print(f"Result: {price}")
    print()


def test_performance_issue():
    """Debug performance test issue"""

    print("🔍 Testing performance issue...")

    # Create large tabular data like in the test
    large_text_parts = []
    large_text_parts.append(
        "Product Code | UPC | Description | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M | List Price | Your Price | Your Extd Price"
    )

    for i in range(10):  # Start with smaller dataset
        large_text_parts.append(
            f"XS{i:04d}A | 191009{i:06d} | Product {i} | {i+10} | 0 | 0 | {i+10} | each | {2.00+i*0.01:.2f} | {1.60+i*0.008:.2f} | {(i+10)*(1.60+i*0.008):.2f}"
        )

    large_text = "\n".join(large_text_parts)

    print(f"Large text sample (first few lines):")
    print("\n".join(large_text.split("\n")[:5]))
    print("...")
    print()

    # Test with specific products
    test_products = ["XS0005A", "XS0009A"]

    for product in test_products:
        print(f"Testing {product}...")
        price = extract_price_from_table_columns(large_text, product)
        print(f"Price: {price}")

        if price is None:
            print("Let's debug why this failed...")
            lines = large_text.split("\n")
            for i, line in enumerate(lines):
                if product in line:
                    print(f"Found {product} at line {i}: {line}")
            print()


if __name__ == "__main__":
    test_tabular_extraction_debug()
    test_multi_tier_debug()
    test_performance_issue()
