#!/usr/bin/env python3
"""
Test integrated Creative Coop processing in main.py
"""
import csv
import json

from main import *

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING INTEGRATED CREATIVE COOP PROCESSING ===")

# Test vendor detection
vendor_type = detect_vendor_type(document.text)
print(f"Detected vendor type: {vendor_type}")

if vendor_type == "Creative-Coop":
    # Use the new Creative-Coop specific processing
    rows = process_creative_coop_document(document)
    print(f"\nCreative-Coop processing returned {len(rows)} rows")

    # Export to CSV for verification
    csv_filename = "test_invoices/creative_coop_integrated_output.csv"

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

    print(f"✅ Integrated CSV file created: {csv_filename}")

    # Show results
    print(f"\n📋 Results (first 10 items):")
    for i, row in enumerate(rows[:10], 1):
        if len(row) >= 6:
            qty = row[5] if len(row) > 5 else "N/A"
            price = row[4] if len(row) > 4 else "N/A"
            description = row[3] if len(row) > 3 else "N/A"
            print(
                f"  {i:2d}: {description[:60]}{'...' if len(str(description)) > 60 else ''} | Price: ${price} | Qty: {qty}"
            )
        else:
            print(f"  {i:2d}: Row has {len(row)} columns: {row}")

    if len(rows) > 10:
        print(f"  ... and {len(rows) - 10} more items")

    # Validation against expected results
    expected_products = [
        "DA4315",
        "DF0716",
        "DF4987",
        "DF5599",
        "DF6360",
        "DF6419A",
        "DF6642",
        "DF9887A",
        "DG1278",
    ]
    found_products = []

    for row in rows:
        desc = row[4]
        for product in expected_products:
            if desc.startswith(product):
                found_products.append(product)
                break

    print(
        f"\n✅ Validation: Found {len(found_products)}/{len(expected_products)} expected products"
    )
    print(f"Found: {found_products}")
    missing = [p for p in expected_products if p not in found_products]
    if missing:
        print(f"Missing: {missing}")

else:
    print("❌ Vendor type not detected as Creative-Coop")
    print(f"   Detected as: {vendor_type}")
