#!/usr/bin/env python3
"""
Test script to process the OneHundred80 invoice and create JSON output
"""
import json
from datetime import datetime
from main import *

def test_onehundred80_processing():
    # Load the Document AI output for OneHundred80
    with open('test_invoices/ONEHUNDRED80-7-1-2025-1T25194476NCHR_docai_output.json', 'r') as f:
        doc_dict = json.load(f)
    
    # Convert back to Document AI format
    from google.cloud import documentai_v1 as documentai
    document = documentai.Document(doc_dict)
    
    print("=== ONEHUNDRED80 INVOICE PROCESSING ===")
    
    # Test entity extraction
    entities = {e.type_: e.mention_text for e in document.entities}
    print(f"Document AI detected entities: {entities}")
    
    # Detect vendor type
    vendor_type = detect_vendor_type(document.text)
    print(f"Detected vendor type: {vendor_type}")
    
    # Extract basic info
    vendor = extract_best_vendor(document.entities)
    invoice_number = entities.get("invoice_id", "")
    purchase_order = entities.get("purchase_order", "")
    invoice_date = format_date(entities.get("invoice_date", ""))
    total_amount = entities.get("total_amount", "")
    
    print(f"Extracted Info:")
    print(f"  Vendor: '{vendor}'")
    print(f"  Invoice#: '{invoice_number}'")
    print(f"  Purchase Order: '{purchase_order}'")
    print(f"  Date: '{invoice_date}'")
    print(f"  Total: '{total_amount}'")
    
    # Extract line items
    if vendor_type == "OneHundred80":
        rows = process_onehundred80_document(document)
    elif vendor_type == "Generic":
        rows = extract_line_items_from_entities(document, invoice_date, vendor, purchase_order or invoice_number)
    else:
        print(f"Using specialized processing for {vendor_type}")
        rows = []
    
    print(f"\nExtracted {len(rows)} line items:")
    
    # Create JSON output
    output_data = {
        "vendor": vendor,
        "invoice_number": invoice_number,
        "purchase_order": purchase_order,
        "invoice_date": invoice_date,
        "total_amount": total_amount,
        "vendor_type": vendor_type,
        "line_items": []
    }
    
    # Process each row
    for i, row in enumerate(rows, 1):
        line_item = {
            "row_number": i,
            "column_a": row[0] if len(row) > 0 else "",
            "date": row[1] if len(row) > 1 else "",
            "vendor": row[2] if len(row) > 2 else "",
            "invoice_number": row[3] if len(row) > 3 else "",
            "description": row[4] if len(row) > 4 else "",
            "unit_price": row[5] if len(row) > 5 else "",
            "quantity": row[6] if len(row) > 6 else ""
        }
        output_data["line_items"].append(line_item)
        
        print(f"  Row {i}: {row[4][:60]}{'...' if len(row[4]) > 60 else ''} | ${row[5]} | Qty: {row[6]}")
    
    # Save JSON output
    json_filename = 'test_invoices/onehundred80_processed_output.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"\n✅ JSON output saved to: {json_filename}")
    
    # Also save CSV for comparison
    csv_filename = 'test_invoices/onehundred80_processed_output.csv'
    import csv
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Column A', 'Date', 'Vendor', 'Invoice Number', 'Description', 'Unit Price', 'Quantity'])
        for row in rows:
            writer.writerow(row)
    
    print(f"✅ CSV output saved to: {csv_filename}")
    
    return output_data

if __name__ == "__main__":
    test_onehundred80_processing()