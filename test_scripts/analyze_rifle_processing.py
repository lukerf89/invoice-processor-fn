#!/usr/bin/env python3
"""
Analyze Rifle invoice processing to identify and fix the issues
"""
import json
from main import *

# Load the Rifle document
with open("test_invoices/Rifle_Invoice_3363053 (1)_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== ANALYZING RIFLE INVOICE PROCESSING ===")

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

# Analyze line items from Document AI
print(f"\n=== DOCUMENT AI LINE ITEMS ===")
line_items = [e for e in document.entities if e.type_ == "line_item"]
print(f"Found {len(line_items)} line items")

for i, entity in enumerate(line_items, 1):
    print(f"\nLine Item {i}:")
    print(f"  Full text: {entity.mention_text}")

    if hasattr(entity, "properties") and entity.properties:
        for prop in entity.properties:
            print(
                f"    {prop.type_}: '{prop.mention_text}' (conf: {prop.confidence:.3f})"
            )

# Test current processing
print(f"\n=== CURRENT PROCESSING RESULTS ===")
rows = extract_line_items_from_entities(document, invoice_date, vendor, invoice_number)
print(f"Current processing returned {len(rows)} rows")

print(f"\nCurrent vs Expected:")
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

for i, row in enumerate(rows):
    if i < len(expected_descriptions):
        current_desc = row[4] if len(row) > 4 else "N/A"
        expected_desc = expected_descriptions[i]
        print(f"  {i+1}. Current: {current_desc}")
        print(f"     Expected: {expected_desc}")
        print(f"     Match: {'✓' if expected_desc in current_desc else '✗'}")
    else:
        print(f"  {i+1}. Extra: {row[4] if len(row) > 4 else 'N/A'}")

print(f"\n=== ISSUES IDENTIFIED ===")
print("1. Descriptions being truncated - missing '2026' and other details")
print("2. Need to filter out 'Not In Stock' and 'SHIP' items")
print("3. Current generic processing not preserving full Document AI descriptions")
