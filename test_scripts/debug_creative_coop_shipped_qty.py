#!/usr/bin/env python3
"""
Debug Creative-Coop processing to check shipped quantities for all items
"""
import json
import re

from main import *

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== DEBUGGING CREATIVE-COOP SHIPPED QUANTITIES ===")

# Expected product codes from user's list
expected_product_codes = [
    "DA4315",
    "DF5599",
    "DF6360",
    "DF6419A",
    "DF6642",
    "DF6802",
    "DF7753A",
    "DF7838A",
    "DF8071A",
    "DF8323A",
    "DF8592A",
    "DF8611",
    "DF8637A",
    "DF8649",
    "DF8667A",
    "DF8805A",
    "DF9407",
    "DF9505",
    "DF9751A",
    "DF9879",
    "DF9880",
    "DF9887A",
    "DG0217A",
    "DG0509",
    "DG0635A",
    "DG1278",
    "DG1281",
    "DG1378",
]

print(f"Expected product codes: {len(expected_product_codes)}")

# Analyze all line items in Document AI
print(f"\n=== ANALYZING ALL DOCUMENT AI LINE ITEMS ===")
line_items = [e for e in document.entities if e.type_ == "line_item"]
print(f"Found {len(line_items)} Document AI line items")

found_products = {}

for i, entity in enumerate(line_items):
    entity_text = entity.mention_text
    print(f"\nEntity {i+1}: {entity_text[:100]}...")

    # Find all product codes in this entity
    product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", entity_text)

    # Extract quantities from properties
    shipped_qty = None
    back_qty = None
    unit_price = None

    if hasattr(entity, "properties") and entity.properties:
        for prop in entity.properties:
            if prop.type_ == "line_item/quantity":
                qty_text = prop.mention_text.strip()
                print(f"  Quantity property: '{qty_text}'")
                # Try to extract shipped quantity (first number)
                qty_match = re.search(r"^(\d+)", qty_text)
                if qty_match:
                    shipped_qty = int(qty_match.group(1))
            elif prop.type_ == "line_item/unit_price":
                unit_price = prop.mention_text.strip()

    # Also try to extract shipped quantity from the entity text using patterns
    if shipped_qty is None:
        # Look for "shipped back" patterns like "8 0 lo each", "6 0 Set"
        qty_patterns = [
            r"\b(\d+)\s+\d+\s+lo\s+each\b",  # "8 0 lo each"
            r"\b(\d+)\s+\d+\s+Set\b",  # "6 0 Set"
            r"\b(\d+)\s+\d+\s+each\b",  # "24 0 each"
        ]

        for pattern in qty_patterns:
            match = re.search(pattern, entity_text, re.IGNORECASE)
            if match:
                shipped_qty = int(match.group(1))
                print(
                    f"  Extracted quantity from text pattern '{pattern}': {shipped_qty}"
                )
                break

    # Record all products found in this entity
    for product_code in product_codes:
        found_products[product_code] = {
            "entity_index": i,
            "shipped_qty": shipped_qty,
            "unit_price": unit_price,
            "entity_text": (
                entity_text[:200] + "..." if len(entity_text) > 200 else entity_text
            ),
        }
        print(f"  Product: {product_code}, Shipped: {shipped_qty}, Price: {unit_price}")

print(f"\n=== SUMMARY: FOUND vs EXPECTED ===")
print(f"Found products: {len(found_products)}")
print(f"Expected products: {len(expected_product_codes)}")

print(f"\n=== SHIPPED QUANTITY ANALYSIS ===")
should_include = []
should_exclude = []

for code in expected_product_codes:
    if code in found_products:
        product_info = found_products[code]
        shipped = product_info["shipped_qty"]
        if shipped is not None and shipped > 0:
            should_include.append(code)
            print(f"✓ INCLUDE {code}: shipped={shipped}")
        else:
            should_exclude.append(code)
            print(f"✗ EXCLUDE {code}: shipped={shipped}")
    else:
        print(f"? MISSING {code}: not found in Document AI")

print(f"\n=== FINAL RESULTS ===")
print(f"Should include ({len(should_include)}): {should_include}")
print(f"Should exclude ({len(should_exclude)}): {should_exclude}")
print(
    f"Missing from Document AI: {[code for code in expected_product_codes if code not in found_products]}"
)
