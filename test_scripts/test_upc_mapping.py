#!/usr/bin/env python3
"""
Test UPC mapping accuracy
"""
import csv
import json

from main import *

# Test with Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING UPC MAPPING ACCURACY ===")

# Extract basic info
entities = {e.type_: e.mention_text for e in document.entities}
vendor = extract_best_vendor(document.entities)
invoice_number = entities.get("invoice_id", "")
invoice_date = format_date(entities.get("invoice_date", ""))

# Test entity extraction (suppress debug output)
import sys
from io import StringIO

old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    rows = extract_line_items_from_entities(
        document, invoice_date, vendor, invoice_number
    )
finally:
    sys.stdout = old_stdout

print(f"✅ Extracted {len(rows)} rows")

# Create comparison data for key problem items
problem_items = {
    "DF5599": {
        "expected_upc": "0191009460954",
        "expected_desc": '6-1/4"L Stoneware Jug',
    },
    "DF6360": {
        "expected_upc": "0191009487548",
        "expected_desc": '16" Round Cotton Pillow w Pleats',
    },
    "DF6419A": {
        "expected_upc": "0191009488132",
        "expected_desc": '17"Sq Cotton Printed Pillow w Ditsy Floral Pattern, 4 Styles',
    },
    "DF6642": {
        "expected_upc": "0191009514312",
        "expected_desc": '12-1/4"H Stoneware Vase',
    },
    "DF6802": {
        "expected_upc": "0191009519157",
        "expected_desc": 'S/4 18" Sq Cotton Embroidered Napkins, Tied w Twill Tape',
    },
}

print("\n🔍 UPC Mapping Analysis:")
print("=" * 80)

found_items = {}
for row in rows:
    description = row[4]
    if " - UPC: " in description:
        parts = description.split(" - UPC: ")
        if len(parts) >= 2:
            product_code = parts[0]
            upc_and_desc = parts[1]
            upc = (
                upc_and_desc.split(" - ")[0] if " - " in upc_and_desc else upc_and_desc
            )
            found_items[product_code] = {"found_upc": upc, "full_desc": description}

for product_code, expected in problem_items.items():
    if product_code in found_items:
        found = found_items[product_code]
        upc_match = "✅" if found["found_upc"] == expected["expected_upc"] else "❌"
        print(f"{product_code}:")
        print(f"  Expected UPC: {expected['expected_upc']}")
        print(f"  Found UPC:    {found['found_upc']} {upc_match}")
        print(f"  Full desc:    {found['full_desc']}")
        print()
    else:
        print(f"{product_code}: ❌ NOT FOUND")
        print()

# Save results
csv_filename = "test_invoices/creative_coop_upc_test.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        [
            "Column A",
            "Date",
            "Vendor",
            "Invoice Number",
            "Description",
            "Unit Price",
            "Quantity",
        ]
    )
    for row in rows:
        writer.writerow(row)

print(f"📄 Results saved to: {csv_filename}")
