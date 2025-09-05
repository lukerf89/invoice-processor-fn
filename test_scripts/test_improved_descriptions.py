#!/usr/bin/env python3
"""
Test improved description formatting
"""
import json
import csv
from main import *

# Test with Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING IMPROVED DESCRIPTION FORMATTING ===")

# Extract basic info
entities = {e.type_: e.mention_text for e in document.entities}
vendor = extract_best_vendor(document.entities)
invoice_number = entities.get("invoice_id", "")
invoice_date = format_date(entities.get("invoice_date", ""))

print(f"Vendor: '{vendor}'")
print(f"Invoice Number: '{invoice_number}'")
print(f"Invoice Date: '{invoice_date}'")

# Test entity extraction (suppress debug output)
import sys
from io import StringIO

# Capture stdout to suppress debug output
old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    rows = extract_line_items_from_entities(
        document, invoice_date, vendor, invoice_number
    )
finally:
    sys.stdout = old_stdout

print(f"Extracted {len(rows)} rows with improved descriptions")

# Create CSV file
csv_filename = "test_invoices/creative_coop_improved_descriptions.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # Write header
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

    # Write data rows
    for row in rows:
        writer.writerow(row)

print(f"✅ CSV file created: {csv_filename}")

# Show first 10 descriptions for comparison
print("\n📋 First 10 improved descriptions:")
for i, row in enumerate(rows[:10], 1):
    print(f"  {i:2d}: {row[4]}")

print(f"\n🎯 CSV file saved with improved descriptions!")
