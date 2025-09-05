#!/usr/bin/env python3
"""
Quick test of Google Sheets integration with Harpercollins invoice
"""
import json

from main import *

# Load the Harpercollins Document AI output
with open("test_invoices/Harpercollins_04-29-2025_docai_output.json", "r") as f:
    doc_dict = json.load(f)

# Convert back to Document AI format
from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== GOOGLE SHEETS INTEGRATION TEST ===")

# Extract basic data
entities = {e.type_: e.mention_text for e in document.entities}
vendor = extract_best_vendor(document.entities)
invoice_number = entities.get("invoice_id", "")
invoice_date = format_date(entities.get("invoice_date", ""))

if not invoice_number:
    invoice_number = extract_order_number(document.text)
if not invoice_date:
    invoice_date = extract_order_date(document.text)

print(f"Vendor: {vendor}")
print(f"Date: {invoice_date}")
print(f"Invoice: {invoice_number}")

# Extract line items using the main function
rows = extract_line_items_from_entities(document, invoice_date, vendor, invoice_number)
print(f"\nExtracted {len(rows)} line items")

# Write to Google Sheets
try:
    from google.auth import default
    from googleapiclient.discovery import build

    credentials, _ = default()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = (
        sheet.values()
        .append(
            spreadsheetId="1cYfpnM_CjgdV1j9hlY-2l0QJMYDWB_hCeXb9KGbgwEo",
            range="TEST",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": rows},
        )
        .execute()
    )

    print(f"✅ SUCCESS: Added {len(rows)} rows to Google Sheets")
    print(f'Updated range: {result.get("updates", {}).get("updatedRange", "Unknown")}')

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    if rows:
        print("\nFirst row that would be added:")
        print(f"  {rows[0]}")
