#!/usr/bin/env python3
"""
Test final Creative-Coop processing to generate the expected output
"""
import csv
import json

from main import *

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING FINAL CREATIVE-COOP PROCESSING ===")

# Test current processing
rows = process_creative_coop_document(document)
print(f"\nProcessing returned {len(rows)} rows")

# Export to CSV for comparison
csv_filename = "test_invoices/creative_coop_final_output.csv"
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

print(f"✅ CSV file created: {csv_filename}")

# Show comparison with expected user output
expected_products = [
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

# Extract found product codes
found_products = []
for row in rows:
    desc = row[4] if len(row) > 4 else ""
    if " - " in desc:
        code = desc.split(" - ")[0]
        found_products.append(code)

print(f"\n=== FINAL COMPARISON ===")
print(f"Expected: {len(expected_products)} items")
print(f"Found: {len(found_products)} items")

matching = []
missing = []
extra = []

for expected in expected_products:
    if expected in found_products:
        matching.append(expected)
    else:
        missing.append(expected)

for found in found_products:
    if found not in expected_products:
        extra.append(found)

print(f"\n✅ Matching ({len(matching)}): {matching}")
print(f"\n❌ Missing ({len(missing)}): {missing}")
print(f"\n➕ Extra ({len(extra)}): {extra}")

print(
    f"\n📊 Accuracy: {len(matching)}/{len(expected_products)} = {len(matching)/len(expected_products)*100:.1f}%"
)

# Show first few rows for format verification
print(f"\n=== SAMPLE OUTPUT ===")
for i, row in enumerate(rows[:5]):
    desc = row[4] if len(row) > 4 else "N/A"
    price = row[5] if len(row) > 5 else "N/A"
    qty = row[6] if len(row) > 6 else "N/A"
    print(f"  {i+1}. {desc[:60]}... | {price} | Qty: {qty}")
