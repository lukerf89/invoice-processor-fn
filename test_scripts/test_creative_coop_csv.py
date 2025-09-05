#!/usr/bin/env python3
"""
Test Creative-Coop invoice processing and export to CSV
"""
import csv
import json

from main import *

# Test with Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING CREATIVE-COOP PROCESSING AND EXPORTING TO CSV ===")

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

    print(f"Entity extraction returned {len(rows)} rows")

    # Filter out items with quantity = 0
    filtered_rows = []
    for row in rows:
        quantity = str(row[6]).strip() if len(row) > 6 else ""
        if quantity and quantity != "0":
            filtered_rows.append(row)

    print(f"After filtering out quantity=0 items: {len(filtered_rows)} rows")

    # Create CSV file in test_invoices folder
    csv_filename = "test_invoices/creative_coop_filtered_output.csv"

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

        # Write data rows (filtered)
        for row in filtered_rows:
            writer.writerow(row)

    print(f"✅ CSV file created: {csv_filename}")
    print(f"📊 Total rows exported: {len(filtered_rows)}")
    print(f"🚫 Filtered out: {len(rows) - len(filtered_rows)} rows with quantity=0")

    # Show first 10 rows as preview
    print("\n📋 First 10 rows preview:")
    for i, row in enumerate(filtered_rows[:10], 1):
        print(
            f"  {i:2d}: {row[4][:60]}{'...' if len(row[4]) > 60 else ''} | {row[5]} | Qty: {row[6]}"
        )

    if len(filtered_rows) > 10:
        print(f"  ... and {len(filtered_rows) - 10} more rows")

print(f"\n🎯 CSV file saved as: {csv_filename}")
