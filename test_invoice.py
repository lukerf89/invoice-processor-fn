#!/usr/bin/env python3
"""
Invoice Testing Workflow Shortcut
Usage: python test_invoice.py InvoiceName
Example: python test_invoice.py Rifle_Paper_INV_J7XM9XQ3HB

This script automates the complete testing workflow:
1. Generate JSON from PDF using document_ai_explorer.py
2. Process JSON to CSV using main.py functions
3. Save both files in test_invoices/ directory
"""

import csv
import json
import os
import subprocess
import sys
from datetime import datetime


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_invoice.py <InvoiceName>")
        print("Example: python test_invoice.py Rifle_Paper_INV_J7XM9XQ3HB")
        print("")
        print("This script will:")
        print("1. Generate JSON from PDF using document_ai_explorer.py")
        print("2. Process JSON to CSV using main.py functions")
        print("3. Save both files in test_invoices/ directory")
        sys.exit(1)

    invoice_name = sys.argv[1]
    pdf_file = f"test_invoices/{invoice_name}.pdf"
    json_file = f"test_invoices/{invoice_name}_docai_output.json"
    csv_file = f"test_invoices/{invoice_name}_processed_output.csv"

    print("🧾 Invoice Testing Workflow")
    print("==========================")
    print(f"Invoice: {invoice_name}")
    print(f"PDF: {pdf_file}")
    print("")

    # Check if PDF exists
    if not os.path.exists(pdf_file):
        print(f"❌ Error: PDF file not found: {pdf_file}")
        print("Please ensure the PDF file exists in the test_invoices/ directory")
        sys.exit(1)

    # Set required environment variables
    os.environ["GOOGLE_CLOUD_PROJECT_ID"] = "freckled-hen-analytics"
    os.environ["DOCUMENT_AI_PROCESSOR_ID"] = "be53c6e3a199a473"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us"

    # Step 1: Generate JSON from PDF
    print("📄 Step 1: Generating JSON from PDF...")
    print(f"Running: document_ai_explorer.py {pdf_file} --save-json")

    try:
        result = subprocess.run(
            [sys.executable, "document_ai_explorer.py", pdf_file, "--save-json"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Error: document_ai_explorer.py failed")
            print(f"Error output: {result.stderr}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error running document_ai_explorer.py: {e}")
        sys.exit(1)

    if not os.path.exists(json_file):
        print("❌ Error: Failed to generate JSON file")
        sys.exit(1)

    print(f"✅ JSON file created: {json_file}")
    print("")

    # Step 2: Process JSON to CSV
    print("⚙️  Step 2: Processing JSON to CSV...")

    try:
        from google.cloud import documentai_v1 as documentai

        from main import (
            extract_line_items,
            extract_line_items_from_entities,
            extract_line_items_from_text,
            format_date,
        )

        print(f"Processing: {json_file}")

        with open(json_file, "r") as f:
            doc_dict = json.load(f)

        # Convert back to Document AI format
        document = documentai.Document(doc_dict)

        # Extract key information
        entities = {e.type_: e.mention_text for e in document.entities}

        # Extract basic invoice information
        vendor = entities.get("supplier_name", "Unknown Vendor")
        invoice_date = format_date(entities.get("invoice_date", ""))
        if not invoice_date:
            invoice_date = datetime.now().strftime("%m/%d/%Y")

        # Try to extract invoice number from filename or text
        invoice_number = (
            invoice_name.split("_")[-1] if "_" in invoice_name else invoice_name
        )

        print(f"Vendor: {vendor}")
        print(f"Invoice Date: {invoice_date}")
        print(f"Invoice Number: {invoice_number}")

        # Extract line items using the main processing functions
        rows = extract_line_items_from_entities(
            document, invoice_date, vendor, invoice_number
        )
        if not rows:
            rows = extract_line_items(document, invoice_date, vendor, invoice_number)
        if not rows:
            rows = extract_line_items_from_text(
                document.text, invoice_date, vendor, invoice_number
            )

        print(f"\nExtracted {len(rows)} line items")

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

            print(f"✅ CSV output saved to: {csv_file}")
            rows_count = len(rows)
        else:
            print("❌ No line items found to save")
            rows_count = 0

    except Exception as e:
        print(f"❌ Error processing invoice: {e}")
        sys.exit(1)

    # Final summary
    print("")
    print("🎉 Workflow Complete!")
    print("====================")
    print(f"✅ JSON: {json_file}")
    print(f"✅ CSV:  {csv_file}")
    print("")
    print(f"📊 {rows_count} items processed and ready for analysis")


if __name__ == "__main__":
    main()
