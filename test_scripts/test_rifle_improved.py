#!/usr/bin/env python3
"""
Test improved Rifle invoice processing with fixes
"""
import json
import csv
from main import *

# Load the Rifle document
with open("test_invoices/Rifle_Invoice_3363053 (1)_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING IMPROVED RIFLE PROCESSING ===")

# Test vendor detection
vendor_type = detect_vendor_type(document.text)
print(f"Detected vendor type: {vendor_type}")

# Extract basic info
entities = {e.type_: e.mention_text for e in document.entities}
vendor = extract_best_vendor(document.entities)
invoice_number = entities.get("invoice_id", "")
invoice_date = format_date(entities.get("invoice_date", ""))

print(f"Vendor: '{vendor}'")
print(f"Invoice Number: '{invoice_number}'")
print(f"Invoice Date: '{invoice_date}'")

# Test improved processing
print(f"\n=== IMPROVED PROCESSING RESULTS ===")
rows = extract_line_items_from_entities(document, invoice_date, vendor, invoice_number)
print(f"Improved processing returned {len(rows)} rows")

# Expected results for validation
expected_descriptions = [
    "CAL094 - 2026 Flora Wall Calendar",
    "PLC011 - 2026 Dahlia 12-Month Softcover Spiral Planner",
    "CAL100 - 2026 Cheese Desk Calendar",
    "PLV001 - 2026 Gracie 12-Month Hardcover Planner with Pen",
    "CAL099 - 2026 Country Farm Kitchen Calendar (6x9)",
    "BMR002 - Cherry Farm Recipe Binder",
    "PLL002 - 2026 Wildwood 12-Month Embroidered Bookbound Planner",
    "CAL096 - 2026 Wildwood Appointment Calendar",
    "CAL098 - 2026 Strawberry Fields Kitchen Calendar (6x9)",
    "PLA013 - 2026 Dahlia 12-Month Appointment Notebook",
    "CAL097 - 2026 Dahlia Appointment Calendar",
]

print(f"\n=== VALIDATION RESULTS ===")
correct_count = 0
for i, row in enumerate(rows):
    if i < len(expected_descriptions):
        current_desc = row[4] if len(row) > 4 else "N/A"
        expected_desc = expected_descriptions[i]
        is_correct = expected_desc == current_desc
        if is_correct:
            correct_count += 1

        print(f"  {i+1}. {'✓' if is_correct else '✗'} Current:  {current_desc}")
        print(f"      Expected: {expected_desc}")
    else:
        print(f"  {i+1}. Extra: {row[4] if len(row) > 4 else 'N/A'}")

print(
    f"\n📊 Results: {correct_count}/{len(expected_descriptions)} descriptions correct ({correct_count/len(expected_descriptions)*100:.1f}%)"
)

# Export to CSV
csv_filename = "test_invoices/rifle_improved_output.csv"
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

# Check for filtered items
print(f"\n=== FILTERING CHECK ===")
all_line_items = [e for e in document.entities if e.type_ == "line_item"]
print(f"Original Document AI line items: {len(all_line_items)}")
print(f"Processed rows: {len(rows)}")
print(f"Filtered out: {len(all_line_items) - len(rows)} items")

# Show which items were filtered
print(f"\nFiltered items should include:")
print("- 'Not In Stock - cal102 oos qty 4.' (out of stock)")
print("- 'SHIP - 1ZV5633J0310215997' (shipping)")
