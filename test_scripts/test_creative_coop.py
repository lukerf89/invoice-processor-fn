#!/usr/bin/env python3
"""
Test Creative-Coop invoice processing
"""
import json
from main import *

# Test with Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING CREATIVE-COOP PROCESSING ===")

# Test vendor detection
vendor_type = detect_vendor_type(document.text)
print(f"Detected vendor type: {vendor_type}")

# Since it's not HarperCollins, it should use generic processing
if vendor_type != "HarperCollins":
    # Extract basic info first
    entities = {e.type_: e.mention_text for e in document.entities}
    vendor = extract_best_vendor(document.entities)
    invoice_number = entities.get("invoice_id", "")
    invoice_date = format_date(entities.get("invoice_date", ""))

    print(f"Vendor: '{vendor}'")
    print(f"Invoice Number: '{invoice_number}'")
    print(f"Invoice Date: '{invoice_date}'")

    # Test entity extraction
    rows = extract_line_items_from_entities(
        document, invoice_date, vendor, invoice_number
    )
    print(f"\nEntity extraction returned {len(rows)} rows")

    if rows:
        print("\nFirst 5 rows:")
        for i, row in enumerate(rows[:5], 1):
            print(f"  {i}: {', '.join(str(x) for x in row)}")
    else:
        print("No rows from entity extraction - would try fallback methods")

print(f"\nTotal entities detected: {len(document.entities)}")
line_items = [e for e in document.entities if e.type_ == "line_item"]
print(f"Line item entities: {len(line_items)}")
