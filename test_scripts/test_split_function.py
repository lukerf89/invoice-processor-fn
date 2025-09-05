#!/usr/bin/env python3
"""
Test the split function with Creative-Coop combined line items
"""
import re

from main import split_combined_line_item

# Test with the problematic line item
test_line = """6-1/4"L Stoneware Jug
DF5599 191009460954
16" Round Cotton Pillow w Pleats
DF6360 191009487548
S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer 8 0
lo each 7.50 6 0 Set 18.50 6.00 48.00 TRF-CCOI 7.20 14.80 88.80"""

print("=== TESTING SPLIT FUNCTION ===")
print(f"Original line: {test_line}")
print()

# Find product codes
product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", test_line)
print(f"Found product codes: {product_codes}")
print()


# Test the split function
class MockEntity:
    pass


entity = MockEntity()
split_items = split_combined_line_item(test_line, entity)

print(f"Split into {len(split_items)} items:")
for i, item in enumerate(split_items, 1):
    print(
        f"  {i}: {item['description']} | ${item['unit_price']} | Qty: {item.get('quantity', 'N/A')}"
    )
