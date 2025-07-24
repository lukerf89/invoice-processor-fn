#!/bin/bash

# Invoice Testing Workflow Shortcut
# Usage: ./test_invoice.sh InvoiceName
# Example: ./test_invoice.sh Rifle_Paper_INV_J7XM9XQ3HB

if [ $# -eq 0 ]; then
    echo "Usage: $0 <InvoiceName>"
    echo "Example: $0 Rifle_Paper_INV_J7XM9XQ3HB"
    echo ""
    echo "This script will:"
    echo "1. Generate JSON from PDF using document_ai_explorer.py"
    echo "2. Process JSON to CSV using main.py functions"
    echo "3. Save both files in test_invoices/ directory"
    exit 1
fi

INVOICE_NAME=$1
PDF_FILE="test_invoices/${INVOICE_NAME}.pdf"
JSON_FILE="test_invoices/${INVOICE_NAME}_docai_output.json"
CSV_FILE="test_invoices/${INVOICE_NAME}_processed_output.csv"

echo "🧾 Invoice Testing Workflow"
echo "=========================="
echo "Invoice: $INVOICE_NAME"
echo "PDF: $PDF_FILE"
echo ""

# Check if PDF exists
if [ ! -f "$PDF_FILE" ]; then
    echo "❌ Error: PDF file not found: $PDF_FILE"
    echo "Please ensure the PDF file exists in the test_invoices/ directory"
    exit 1
fi

# Set required environment variables
export GOOGLE_CLOUD_PROJECT_ID="freckled-hen-analytics"
export DOCUMENT_AI_PROCESSOR_ID="be53c6e3a199a473"
export GOOGLE_CLOUD_LOCATION="us"

echo "📄 Step 1: Generating JSON from PDF..."
echo "Running: document_ai_explorer.py $PDF_FILE --save-json"
python document_ai_explorer.py "$PDF_FILE" --save-json

if [ ! -f "$JSON_FILE" ]; then
    echo "❌ Error: Failed to generate JSON file"
    exit 1
fi

echo ""
echo "✅ JSON file created: $JSON_FILE"
echo ""

echo "⚙️  Step 2: Processing JSON to CSV..."

# Create a temporary processing script
TEMP_SCRIPT=$(mktemp /tmp/process_invoice_XXXXXX.py)

cat > "$TEMP_SCRIPT" << EOF
#!/usr/bin/env python3
import json
import csv
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import main
sys.path.append('.')
from main import *

def process_invoice():
    invoice_name = "$INVOICE_NAME"
    json_file = "$JSON_FILE"
    csv_file = "$CSV_FILE"

    print(f"Processing: {json_file}")

    with open(json_file, 'r') as f:
        doc_dict = json.load(f)

    # Convert back to Document AI format
    from google.cloud import documentai_v1 as documentai
    document = documentai.Document(doc_dict)

    # Extract key information
    entities = {e.type_: e.mention_text for e in document.entities}

    # Extract basic invoice information
    vendor = entities.get('supplier_name', 'Unknown Vendor')
    invoice_date = format_date(entities.get('invoice_date', ''))
    if not invoice_date:
        invoice_date = datetime.now().strftime("%m/%d/%Y")

    # Try to extract invoice number from filename or text
    invoice_number = invoice_name.split('_')[-1] if '_' in invoice_name else invoice_name

    print(f"Vendor: {vendor}")
    print(f"Invoice Date: {invoice_date}")
    print(f"Invoice Number: {invoice_number}")

    # Extract line items using the main processing functions
    rows = extract_line_items_from_entities(document, invoice_date, vendor, invoice_number)
    if not rows:
        rows = extract_line_items(document, invoice_date, vendor, invoice_number)
    if not rows:
        rows = extract_line_items_from_text(document.text, invoice_date, vendor, invoice_number)

    print(f"\\nExtracted {len(rows)} line items")

    # Save to CSV file
    if rows:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Date', 'Vendor', 'Invoice Number', 'Product Code', 'Description', 'Quantity', 'Price'])
            # Write data rows
            writer.writerows(rows)

        print(f"✅ CSV output saved to: {csv_file}")
        return len(rows)
    else:
        print("❌ No line items found to save")
        return 0

if __name__ == "__main__":
    rows_count = process_invoice()
    print(f"\\n🎉 Processing complete! {rows_count} items processed.")
EOF

# Run the processing script
python "$TEMP_SCRIPT"
PROCESS_EXIT_CODE=$?

# Clean up temp script
rm "$TEMP_SCRIPT"

if [ $PROCESS_EXIT_CODE -eq 0 ] && [ -f "$CSV_FILE" ]; then
    echo ""
    echo "🎉 Workflow Complete!"
    echo "===================="
    echo "✅ JSON: $JSON_FILE"
    echo "✅ CSV:  $CSV_FILE"
    echo ""
    echo "📊 Files ready for analysis in test_invoices/ directory"
else
    echo "❌ Error: Processing failed"
    exit 1
fi
