#!/usr/bin/env python3
"""
Debug the position-based mapping for Creative-Coop quantities
"""
import re

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

print("=== POSITION-BASED MAPPING DEBUG ===\n")

# Find all product codes in order
product_pattern = r"\b(D[A-Z]\d{4}A?)\b"
product_matches = list(re.finditer(product_pattern, test_text))

print("Product codes found (in order):")
for i, match in enumerate(product_matches):
    print(f"  {i}: {match.group(1)} at position {match.start()}")

print()

# Find all quantity patterns - use same pattern as main code
qty_pattern = r"\b(\d+)\s+\d+\s+(?:lo\s+)?(?:each|Set)\b"

all_quantities = []
seen_positions = set()

for match in re.finditer(qty_pattern, test_text, re.IGNORECASE):
    position = match.start()
    if position not in seen_positions:
        shipped_qty = int(match.group(1))
        all_quantities.append(
            {
                "position": position,
                "shipped": shipped_qty,
                "match_text": match.group(0).replace("\n", " "),
            }
        )
        seen_positions.add(position)

# Sort quantities by position
all_quantities.sort(key=lambda x: x["position"])

print("Quantity patterns found (in order):")
for i, qty in enumerate(all_quantities):
    print(
        f"  {i}: '{qty['match_text']}' -> shipped={qty['shipped']} at position {qty['position']}"
    )

print()

# Expected mapping based on user feedback
expected_mapping = {
    "DF0716": 0,  # should be 0 according to user
    "DF4987": 0,  # should be 0 according to user
    "DF5599": 8,  # should be 8 from "8 0 lo each"
    "DF6360": 6,  # should be 6 from "6 0 Set"
}

print("=== ANALYSIS ===")
print("Product order vs Quantity order:")

for i, product_match in enumerate(product_matches):
    product_code = product_match.group(1)
    expected = expected_mapping.get(product_code, "?")

    if i < len(all_quantities):
        actual_qty = all_quantities[i]["shipped"]
        qty_pattern = all_quantities[i]["match_text"]
        status = "✅ MATCH" if actual_qty == expected else "❌ MISMATCH"
        print(
            f"  Product {i}: {product_code} -> Expected: {expected}, Position-based: {actual_qty} ('{qty_pattern}') {status}"
        )
    else:
        print(
            f"  Product {i}: {product_code} -> Expected: {expected}, Position-based: NO QUANTITY"
        )

print(f"\nTotal products: {len(product_matches)}")
print(f"Total quantities: {len(all_quantities)}")

print("\n=== MANUAL INSPECTION ===")
print("Looking at the text structure...")
print("After the descriptions, we have this quantity section:")

# Find where quantity section starts (after all product descriptions)
desc_end = test_text.find('S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer')
if desc_end != -1:
    qty_section = test_text[desc_end + 60 :]  # Skip the last description
    print(f"Quantity section: {repr(qty_section[:200])}")

    # The issue might be that some patterns are prices/other numbers, not quantities
    print("\nBreaking down each number sequence:")
    lines = qty_section.split("\n")
    for i, line in enumerate(lines[:20]):  # Look at first 20 lines
        line = line.strip()
        if line:
            print(f"  Line {i}: '{line}'")
