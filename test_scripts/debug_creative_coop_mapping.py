#!/usr/bin/env python3
"""
Debug Creative Coop invoice processing to understand the data structure better
"""
import json
import re
from main import *

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== CREATIVE COOP DATA STRUCTURE ANALYSIS ===")

# Analyze the raw text structure first
raw_text = document.text
print("Raw text structure around key products:")

# Find specific products and their context
problem_products = [
    "DA4315",
    "DF0716",
    "DF4987",
    "DF5599",
    "DF6360",
    "DF6419A",
    "DF6642",
    "DF9887A",
    "DG1278",
]

for product in problem_products:
    product_pos = raw_text.find(product)
    if product_pos != -1:
        # Get 200 characters before and after the product code
        start = max(0, product_pos - 200)
        end = min(len(raw_text), product_pos + 200)
        context = raw_text[start:end]

        print(f"\n--- {product} Context ---")
        print(context.replace("\n", " | "))
        print()

print("\n=== DOCUMENT AI ENTITIES ANALYSIS ===")

# Analyze Document AI entities structure
line_items = [e for e in document.entities if e.type_ == "line_item"]
print(f"Total line_item entities: {len(line_items)}")

for i, entity in enumerate(line_items[:10]):  # Look at first 10
    print(f"\n--- Line Item {i+1} ---")
    print(f"Entity text: {repr(entity.mention_text[:100])}...")

    if hasattr(entity, "properties") and entity.properties:
        for prop in entity.properties:
            print(
                f"  {prop.type_}: {repr(prop.mention_text)} (conf: {prop.confidence:.3f})"
            )

    # Look for product codes in this entity
    product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", entity.mention_text)
    if product_codes:
        print(f"  Found product codes: {product_codes}")

        # For each product code, try to find its UPC and description
        for code in product_codes:
            # Find UPC
            upc_matches = re.findall(r"\b(\d{12,13})\b", entity.mention_text)
            print(f"    {code} - UPC candidates: {upc_matches}")

            # Try to extract description
            lines = entity.mention_text.split("\n")
            for line in lines:
                if code in line and len(line) > 20:
                    print(f"    {code} - Line with description: {repr(line)}")

print("\n=== EXPECTED MAPPING ANALYSIS ===")

# Create the expected mapping based on the corrections provided
expected_mapping = {
    "DA4315": {
        "upc": "0807472767956",
        "description": '3-1/4" Rnd x 4"H 12 oz. Embossed Drinking Glass, Green',
    },
    "DF0716": {
        "upc": "6191009197164",
        "description": '6"L x 8"H Bone Photo Frame (Holds 4" x 6" Photo)',
    },
    "DF4987": {"upc": "4191009436263", "description": '6-1/4"L Stoneware Jug'},
    "DF5599": {
        "upc": "0191009460954",
        "description": '16" Round Cotton Pillow w Pleats',
    },
    "DF6360": {
        "upc": "0191009487548",
        "description": 'S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer',
    },
    "DF6419A": {
        "upc": "0191009488132",
        "description": '17"Sq Cotton Printed Pillow w Ditsy Floral Pattern, 4 Styles',
    },
    "DF6642": {"upc": "0191009514312", "description": '12-1/4"H Stoneware Vase'},
    "DF9887A": {
        "upc": "0191009675723",
        "description": '6" Rnd Hand-Painted Stoneware Plate w Image, Multi, 4 Styles',
    },
    "DG1278": {
        "upc": "0191009786054",
        "description": '6-1/2"L x 8-1/2"H Resin Striped Photo Frame',
    },
}

print("Expected vs Found in raw text:")
for code, expected in expected_mapping.items():
    expected_upc = expected["upc"]
    expected_desc = expected["description"]

    # Check if UPC and description appear in raw text
    upc_in_text = expected_upc in raw_text
    desc_in_text = expected_desc in raw_text

    print(f"{code}:")
    print(f"  UPC {expected_upc} in text: {upc_in_text}")
    print(f"  Description in text: {desc_in_text}")

    if desc_in_text:
        desc_pos = raw_text.find(expected_desc)
        code_pos = raw_text.find(code)
        print(
            f"  Distance: {abs(desc_pos - code_pos) if desc_pos != -1 and code_pos != -1 else 'N/A'} chars"
        )
