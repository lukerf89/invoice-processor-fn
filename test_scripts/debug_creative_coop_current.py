#!/usr/bin/env python3
"""
Debug current Creative-Coop processing to see filtering behavior
"""
import json
from main import *

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== DEBUGGING CURRENT CREATIVE-COOP PROCESSING ===")

# Test vendor detection
vendor_type = detect_vendor_type(document.text)
print(f"Detected vendor type: {vendor_type}")

# Test current main.py processing
print(f"\n=== CURRENT MAIN.PY PROCESSING ===")
rows = process_creative_coop_document(document)
print(f"Main.py processing returned {len(rows)} rows")

print(f"\n=== ALL RETURNED ITEMS ===")
for i, row in enumerate(rows, 1):
    description = row[4] if len(row) > 4 else "N/A"
    print(f"  {i:2d}. {description}")

# Expected results for validation
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

print(f"\n=== MISSING ITEMS ANALYSIS ===")
print(f"Expected: {len(expected_product_codes)} items")
print(f"Found: {len(rows)} items")

# Extract product codes from current results
current_codes = []
for row in rows:
    desc = row[4] if len(row) > 4 else ""
    if " - " in desc:
        code = desc.split(" - ")[0]
        current_codes.append(code)

missing_codes = []
for expected_code in expected_product_codes:
    if expected_code not in current_codes:
        missing_codes.append(expected_code)

print(f"\nMissing codes ({len(missing_codes)}):")
for code in missing_codes:
    print(f"  - {code}")

print(f"\nFound codes ({len(current_codes)}):")
for code in current_codes:
    print(f"  - {code}")
