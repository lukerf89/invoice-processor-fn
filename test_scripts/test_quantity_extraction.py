#!/usr/bin/env python3
"""
Test Creative-Coop quantity extraction
"""
import json
import re

from main import extract_creative_coop_quantity

# Test cases based on the debug output
test_cases = [
    {
        "product_code": "DF7753A",
        "text": 'DF7753A 191009544173 5" Square Stoneware Plate w Insect/Bird & Flowers, 4 Sty 24 0 each 3.00 2.40 57.60',
        "expected": "24",
        "description": 'Should extract 24 (shipped) from "24 0 each"',
    },
    {
        "product_code": "DF7838A",
        "text": 'DF7838A 191009577355 6-1/2"H Plush Animal in Clothes, Multi Color, 6 Styles 24 0 each 6.00 115.20',
        "expected": "24",
        "description": 'Should extract 24 (shipped) from "24 0 each"',
    },
    {
        "product_code": "DF8071A",
        "text": 'DF8071A 191009597674 4"H Stoneware Mug w Reactive Glaze, 4 Styles 12 0 each 7.50 72.00',
        "expected": "12",
        "description": 'Should extract 12 (shipped) from "12 0 each"',
    },
    {
        "product_code": "DF7222A",
        "text": "DF7222A 191009541691 0 24 each 3.50 0.00",
        "expected": "0",
        "description": 'Should extract 0 (shipped) from "0 24 each" - not the backorder',
    },
    {
        "product_code": "DF6802",
        "text": 'DF6802 S/4 18" Sq Cotton Embroidered Napkins, Tied w Twill Tape 8 0 each 22.50 TRF-CCOI 7.20 144.00 TRF-CCOI 21.60 6 0 Set 11.00 52.80',
        "expected": "8",
        "description": 'Should extract 8 (shipped) from "8 0 each" in combined line',
    },
    {
        "product_code": "DF5599",
        "text": 'S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer 8 0\nlo each 7.50 6 0 Set 18.50',
        "expected": "8",
        "description": 'Should extract 8 (shipped) from "8 0 lo each"',
    },
]

print("=== TESTING CREATIVE-COOP QUANTITY EXTRACTION ===\n")

for i, test_case in enumerate(test_cases, 1):
    print(f"Test {i}: {test_case['description']}")
    print(f"Product: {test_case['product_code']}")
    print(f"Text: {test_case['text']}")

    result = extract_creative_coop_quantity(
        test_case["text"], test_case["product_code"]
    )
    expected = test_case["expected"]

    if result == expected:
        print(f"✅ PASS: Got '{result}', expected '{expected}'")
    else:
        print(f"❌ FAIL: Got '{result}', expected '{expected}'")
    print()

print("🎯 Testing edge cases:")

# Edge case tests
edge_cases = [
    {
        "product_code": "DF9999",
        "text": "Some text without the product code",
        "expected": None,
        "description": "Product code not found in text",
    },
    {
        "product_code": "DF1234",
        "text": "DF1234 some description without quantity pattern",
        "expected": None,
        "description": "No quantity pattern found",
    },
]

for i, test_case in enumerate(edge_cases, 1):
    print(f"Edge case {i}: {test_case['description']}")
    result = extract_creative_coop_quantity(
        test_case["text"], test_case["product_code"]
    )
    expected = test_case["expected"]

    if result == expected:
        print(f"✅ PASS: Got '{result}', expected '{expected}'")
    else:
        print(f"❌ FAIL: Got '{result}', expected '{expected}'")
    print()
