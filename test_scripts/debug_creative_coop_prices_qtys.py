#!/usr/bin/env python3
"""
Debug Creative-Coop pricing and quantity extraction to understand the invoice format
"""
import json
import re

from main import *

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== DEBUGGING CREATIVE-COOP PRICING AND QUANTITIES ===")

# Expected results with wholesale prices and ordered quantities
expected_results = {
    "DA4315": {"wholesale_price": "$3.20", "ordered_qty": "12"},
    "DF5599": {"wholesale_price": "$6.00", "ordered_qty": "8"},
    "DF6360": {"wholesale_price": "$14.80", "ordered_qty": "6"},
    "DF6419A": {"wholesale_price": "$6.00", "ordered_qty": "8"},
    "DF6642": {"wholesale_price": "$18.00", "ordered_qty": "8"},
    "DF6802": {"wholesale_price": "$8.80", "ordered_qty": "6"},
    "DF7753A": {"wholesale_price": "$2.40", "ordered_qty": "24"},
    "DF7838A": {"wholesale_price": "$4.80", "ordered_qty": "24"},
    "DF8071A": {"wholesale_price": "$6.00", "ordered_qty": "12"},
    "DF8323A": {"wholesale_price": "$18.00", "ordered_qty": "4"},
    "DF8592A": {"wholesale_price": "$3.60", "ordered_qty": "12"},
    "DF8611": {"wholesale_price": "$22.80", "ordered_qty": "2"},
    "DF8637A": {"wholesale_price": "$5.20", "ordered_qty": "12"},
    "DF8649": {"wholesale_price": "$12.80", "ordered_qty": "6"},
    "DF8667A": {"wholesale_price": "$3.60", "ordered_qty": "12"},
    "DF8805A": {"wholesale_price": "$6.00", "ordered_qty": "24"},
    "DF9407": {"wholesale_price": "$12.00", "ordered_qty": "4"},
    "DF9505": {"wholesale_price": "$28.00", "ordered_qty": "4"},
    "DF9751A": {"wholesale_price": "$4.00", "ordered_qty": "16"},
    "DF9879": {"wholesale_price": "$7.60", "ordered_qty": "6"},
    "DF9880": {"wholesale_price": "$8.00", "ordered_qty": "6"},
    "DF9887A": {"wholesale_price": "$3.00", "ordered_qty": "24"},
    "DG0217A": {"wholesale_price": "$9.20", "ordered_qty": "6"},
    "DG0509": {"wholesale_price": "$20.00", "ordered_qty": "4"},
    "DG0635A": {"wholesale_price": "$2.00", "ordered_qty": "12"},
    "DG1278": {"wholesale_price": "$7.60", "ordered_qty": "6"},
    "DG1281": {"wholesale_price": "$7.20", "ordered_qty": "6"},
    "DG1378": {"wholesale_price": "$17.20", "ordered_qty": "4"},
}

print(f"Expected items: {len(expected_results)}")

# Analyze line items containing these products
print(f"\n=== ANALYZING DOCUMENT AI FOR EXPECTED PRODUCTS ===")
line_items = [e for e in document.entities if e.type_ == "line_item"]

found_analysis = {}

for entity in line_items:
    entity_text = entity.mention_text

    # Find product codes in this entity
    product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", entity_text)

    if not product_codes:
        continue

    print(f"\nEntity: {entity_text[:150]}...")

    # Extract all numbers that could be prices or quantities
    numbers = re.findall(r"\b\d+(?:\.\d{1,2})?\b", entity_text)
    print(f"  Numbers found: {numbers}")

    # Extract properties
    props = {}
    if hasattr(entity, "properties") and entity.properties:
        for prop in entity.properties:
            props[prop.type_] = prop.mention_text.strip()
            print(f"  Property {prop.type_}: '{prop.mention_text.strip()}'")

    # Analyze each product in this entity
    for product_code in product_codes:
        if product_code in expected_results:
            expected = expected_results[product_code]
            print(f"\n  *** ANALYZING {product_code} ***")
            print(
                f"  Expected wholesale: {expected['wholesale_price']}, ordered qty: {expected['ordered_qty']}"
            )

            # Try to find the wholesale price and ordered quantity in the text
            # Creative-Coop invoices typically have: shipped back unit price wholesale_price amount
            # Look for patterns like "8 0 lo each 7.50 6.00 48.00" where:
            # 8 = ordered, 0 = back/not shipped, 7.50 = unit price, 6.00 = wholesale, 48.00 = amount

            wholesale_candidates = []
            qty_candidates = []

            # Pattern for "ordered back unit_price wholesale amount"
            pattern = r"(\d+)\s+(\d+)\s+(?:lo\s+)?(?:each|Set)\s+(\d+\.\d{2})\s+(\d+\.\d{2})\s+(\d+\.\d{2})"
            matches = re.findall(pattern, entity_text, re.IGNORECASE)

            for match in matches:
                ordered, back, unit_price, wholesale, amount = match
                print(
                    f"  Pattern match: ordered={ordered}, back={back}, unit={unit_price}, wholesale={wholesale}, amount={amount}"
                )

                # Check if this matches expected values
                if (
                    ordered == expected["ordered_qty"]
                    and f"${wholesale}" == expected["wholesale_price"]
                ):
                    print(f"  ✓ MATCH FOUND: ordered={ordered}, wholesale=${wholesale}")
                    wholesale_candidates.append(wholesale)
                    qty_candidates.append(ordered)

            found_analysis[product_code] = {
                "entity_text": entity_text,
                "wholesale_candidates": wholesale_candidates,
                "qty_candidates": qty_candidates,
                "expected_wholesale": expected["wholesale_price"],
                "expected_qty": expected["ordered_qty"],
            }

print(f"\n=== ANALYSIS SUMMARY ===")
for product_code, analysis in found_analysis.items():
    print(f"\n{product_code}:")
    print(
        f"  Expected: wholesale={analysis['expected_wholesale']}, qty={analysis['expected_qty']}"
    )
    print(
        f"  Found: wholesale_candidates={analysis['wholesale_candidates']}, qty_candidates={analysis['qty_candidates']}"
    )
    if analysis["wholesale_candidates"] and analysis["qty_candidates"]:
        print(f"  ✓ Can extract correct values")
    else:
        print(f"  ✗ Need better extraction logic")
        print(f"  Entity: {analysis['entity_text'][:200]}...")
