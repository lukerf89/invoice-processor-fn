#!/usr/bin/env python3
"""
Debug the exact layout for split line items to understand positioning
"""
import re

# This is the actual document text pattern for DF5599 and DF6360
test_text = """
DF0716
191009197164
6"L x 8"H Bone Photo Frame (Holds 4" x 6" Photo)
DF4987
191009436263
6-1/4"L Stoneware Jug
DF5599
191009460954
16" Round Cotton Pillow w Pleats
DF6360
191009487548
S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer
12
0
each
4.00
0
6
each
15.00
TRF-CCOI
3.20
38.40
5.76
12.00
0.00
0
4
each
10.00
8.00
0.00
8
0
lo
each
7.50
6
0
Set
18.50
"""

print("=== DEBUGGING SPLIT LINE ITEM LAYOUT ===\n")

# Find positions of product codes
products = ["DF0716", "DF4987", "DF5599", "DF6360"]
product_positions = {}

for product in products:
    pos = test_text.find(product)
    if pos != -1:
        product_positions[product] = pos
        print(f"{product} found at position {pos}")

print()

# Find all quantity patterns in the text
qty_pattern = r"\b(\d+)\s+(\d+)\s+((?:lo\s+)?each|Set)\b"
matches = list(re.finditer(qty_pattern, test_text, re.IGNORECASE))

print(f"Found {len(matches)} quantity patterns:")
for i, match in enumerate(matches):
    shipped = match.group(1)
    back = match.group(2)
    unit = match.group(3)
    print(
        f"  Pattern {i+1}: '{shipped} {back} {unit}' at position {match.start()}-{match.end()}"
    )

    # Show which product this is closest to
    closest_product = None
    closest_distance = float("inf")
    for product, product_pos in product_positions.items():
        if match.start() > product_pos:  # Pattern comes after product
            distance = match.start() - product_pos
            if distance < closest_distance:
                closest_distance = distance
                closest_product = product

    if closest_product:
        print(
            f"    -> Closest to {closest_product} (distance: {closest_distance} chars)"
        )
    print()

print("=== EXPECTED ASSIGNMENTS ===")
print("DF5599 should get 8 from '8 0 lo each'")
print("DF6360 should get 6 from '6 0 Set'")
print("But current algorithm may assign the wrong patterns...")


# Test current algorithm behavior
def test_current_algorithm(text, product_code):
    if product_code in text:
        product_pos = text.find(product_code)
        after_product = text[
            product_pos + len(product_code) : product_pos + len(product_code) + 300
        ]

        print(f"\nTesting {product_code}:")
        print(f"  Product position: {product_pos}")
        print(
            f"  Search window: positions {product_pos + len(product_code)} to {product_pos + len(product_code) + 300}"
        )
        print(f"  Window text: {repr(after_product[:100])}...")

        qty_patterns = [
            r"\b(\d+)\s+\d+\s+(?:each|lo\s+each|Set)\b",
            r"\b(\d+)\s+\d+\b(?=\s+(?:each|lo|Set))",
        ]

        closest_match = None
        closest_distance = float("inf")

        for pattern in qty_patterns:
            for match in re.finditer(pattern, after_product, re.IGNORECASE):
                distance = match.start()
                print(
                    f"  Found pattern '{match.group(0)}' at relative position {distance}"
                )
                if distance < closest_distance:
                    closest_distance = distance
                    closest_match = match

        if closest_match:
            result = closest_match.group(1)
            print(f"  -> Returns: {result}")
            return result
    return None


for product in ["DF5599", "DF6360"]:
    test_current_algorithm(test_text, product)
