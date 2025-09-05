#!/usr/bin/env python3
"""
Test script to process Rifle Paper invoice JSON and save CSV output
"""
import json
import csv
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import *


def test_rifle_paper_processing():
    # Load the pre-generated Document AI output
    json_file = "test_invoices/Rifle_Paper_INV_J7XM9XQ3HB_docai_output.json"
    csv_file = "test_invoices/Rifle_Paper_INV_J7XM9XQ3HB_processed_output.csv"

    with open(json_file, "r") as f:
        doc_dict = json.load(f)

    # Convert back to Document AI format
    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    # Extract key information
    entities = {e.type_: e.mention_text for e in document.entities}
    print(f"Document AI detected entities: {entities}")

    # Detect vendor type and get basic info
    vendor_type = detect_vendor_type(document.text)
    print(f"Detected vendor type: {vendor_type}")

    # Extract basic invoice information
    vendor = entities.get("supplier_name", "Unknown Vendor")
    invoice_date = format_date(entities.get("invoice_date", ""))
    if not invoice_date:
        invoice_date = datetime.now().strftime("%m/%d/%Y")

    # Extract invoice number from text
    invoice_number = "J7XM9XQ3HB"  # From the order number in the document

    print(f"Vendor: {vendor}")
    print(f"Invoice Date: {invoice_date}")
    print(f"Invoice Number: {invoice_number}")

    # Extract line items based on vendor type
    if vendor_type == "rifle":
        # Use generic processing since Rifle Paper doesn't have specialized processing
        rows = extract_line_items_from_entities(
            document, invoice_date, vendor, invoice_number
        )
        if not rows:
            rows = extract_line_items(document, invoice_date, vendor, invoice_number)
        if not rows:
            rows = extract_line_items_from_text(
                document.text, invoice_date, vendor, invoice_number
            )
    else:
        # Fallback to generic processing
        rows = extract_line_items_from_entities(
            document, invoice_date, vendor, invoice_number
        )
        if not rows:
            rows = extract_line_items(document, invoice_date, vendor, invoice_number)
        if not rows:
            rows = extract_line_items_from_text(
                document.text, invoice_date, vendor, invoice_number
            )

    print(f"Extracted {len(rows)} line items:")
    for i, row in enumerate(rows, 1):
        print(f"  {i}. {row}")

    # Save to CSV file
    if rows:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(
                [
                    "Date",
                    "Vendor",
                    "Invoice Number",
                    "Product Code",
                    "Description",
                    "Quantity",
                    "Price",
                ]
            )
            # Write data rows
            writer.writerows(rows)

        print(f"\nCSV output saved to: {csv_file}")
        print(f"Total rows processed: {len(rows)}")
    else:
        print("No line items found to save")

    return rows


if __name__ == "__main__":
    test_rifle_paper_processing()
