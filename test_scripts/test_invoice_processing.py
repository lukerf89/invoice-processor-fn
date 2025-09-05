#!/usr/bin/env python3
"""
Test script to process the new_invoice.pdf and see what data would be extracted
"""
import json
from datetime import datetime
from main import *


def test_invoice_processing():
    # Load the pre-generated Document AI output
    with open("new_invoice_docai_output.json", "r") as f:
        doc_dict = json.load(f)

    # Convert back to Document AI format
    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    # Test entity extraction
    entities = {e.type_: e.mention_text for e in document.entities}
    print(f"Document AI detected entities: {entities}")

    # Extract vendor using confidence-based selection
    vendor = extract_best_vendor(document.entities)
    invoice_number = entities.get("invoice_id", "")
    invoice_date = format_date(entities.get("invoice_date", ""))

    # Fallback extraction for missing invoice number (look for order number)
    if not invoice_number:
        invoice_number = extract_order_number(document.text)

    # Fallback extraction for missing invoice date (look for order date)
    if not invoice_date:
        invoice_date = extract_order_date(document.text)

    print(
        f"Extracted - Vendor: '{vendor}', Invoice#: '{invoice_number}', Date: '{invoice_date}'"
    )

    # Extract line items from Document AI entities first
    rows = extract_line_items_from_entities(
        document, invoice_date, vendor, invoice_number
    )
    print(f"Entity extraction returned {len(rows)} rows")

    # Print the extracted rows
    for i, row in enumerate(rows, 1):
        print(f"Row {i}: {row}")

    return rows


if __name__ == "__main__":
    test_invoice_processing()
