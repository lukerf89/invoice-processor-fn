#!/usr/bin/env python3
"""
Test quantity extraction for split line items
"""
from main import extract_creative_coop_quantity

# Test based on the actual Creative-Coop document structure
# From debug: DF5599 should get 8, DF6360 should get 6

print("=== TESTING SPLIT LINE ITEM QUANTITIES ===\n")

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

print("Document text snippet:")
print(test_text)
print()

# Test DF5599 - should get 8 from "8 0 lo each"
result_df5599 = extract_creative_coop_quantity(test_text, "DF5599")
print(f"DF5599 quantity extraction: {result_df5599}")
print(
    f"Expected: 8, Got: {result_df5599} - {'✅ PASS' if result_df5599 == '8' else '❌ FAIL'}"
)
print()

# Test DF6360 - should get 6 from "6 0 Set"
result_df6360 = extract_creative_coop_quantity(test_text, "DF6360")
print(f"DF6360 quantity extraction: {result_df6360}")
print(
    f"Expected: 6, Got: {result_df6360} - {'✅ PASS' if result_df6360 == '6' else '❌ FAIL'}"
)
print()

# Also test DF6802 case - should get 6 from "6 0 Set"
df6802_text = """
17"Sq Cotton Printed Pillow w Ditsy Floral Pattern, 4 Styles
DF6642
191009514312
12-1/4"H Stoneware Vase
DF6802
191009519157
S/4 18" Sq Cotton Embroidered Napkins, Tied w Twill Tape
DF7212A
191009541592
4" Square x 3"H Stoneware Berry Basket, 4 Colors
DF7222A
191009541691
3-1/4"L x 2-1/2"W x 1-1/4"H Stoneware Dish, 3 Styles
DF7225A
191009541721
2-1/4"H 3-1/2"H Stoneware Espresso/Child's Mug, 8 Styles
DF7336
191009542452
10"L x 6-3/4"W x 10-1/4"H 3 Quart Stoneware Pitcher
8
0
each
22.50
6.00
48.00
TRF-CCOI
7.20
14.80
88.80
TRF-CCOI
TRF-CCOI
13.32
6.00
48.00
7.20
18.00
144.00
TRF-CCOI
21.60
6
0
Set
11.00
8.80
52.80
"""

print("Testing DF6802 case:")
result_df6802 = extract_creative_coop_quantity(df6802_text, "DF6802")
print(f"DF6802 quantity extraction: {result_df6802}")
print(
    f"Expected: 6, Got: {result_df6802} - {'✅ PASS' if result_df6802 == '6' else '❌ FAIL'}"
)
print()

# Test DF6642 from same text - should get 8 from "8 0 each"
result_df6642 = extract_creative_coop_quantity(df6802_text, "DF6642")
print(f"DF6642 quantity extraction: {result_df6642}")
print(
    f"Expected: 8, Got: {result_df6642} - {'✅ PASS' if result_df6642 == '8' else '❌ FAIL'}"
)
