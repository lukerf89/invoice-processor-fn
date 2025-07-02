import functions_framework
import requests
import os
import re
from datetime import datetime
from google.cloud import documentai_v1 as documentai
from googleapiclient.discovery import build
from google.auth import default
from flask import jsonify

@functions_framework.http
def process_invoice(request):
    request_json = request.get_json(silent=True)
    
    # Step 1: Extract PDF URL from Trello webhook
    file_url = request_json.get('file_url') if request_json else None
    if not file_url:
        return jsonify({"error": "Missing file_url"}), 400

    # Step 2: Download the PDF from Trello
    try:
        response = requests.get(file_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download PDF: {str(e)}"}), 500

    pdf_content = response.content

    # Step 3: Get configuration from environment variables
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us')
    processor_id = os.environ.get('DOCUMENT_AI_PROCESSOR_ID')
    spreadsheet_id = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID')
    sheet_name = os.environ.get('GOOGLE_SHEETS_SHEET_NAME', 'Sheet1')
    
    if not project_id or not processor_id or not spreadsheet_id:
        return jsonify({"error": "Missing required environment variables: GOOGLE_CLOUD_PROJECT_ID, DOCUMENT_AI_PROCESSOR_ID, GOOGLE_SHEETS_SPREADSHEET_ID"}), 500
    
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # Step 4: Prepare document and send to Document AI
    raw_document = documentai.RawDocument(content=pdf_content, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    
    try:
        result = client.process_document(request=request)
    except Exception as e:
        return jsonify({"error": f"Document AI processing failed: {str(e)}"}), 500

    # Step 5: Extract key fields from Document AI response
    document = result.document
    entities = {e.type_: e.mention_text for e in document.entities}
    
    vendor = entities.get("supplier_name", "").replace('\n', ' ').strip()
    invoice_number = entities.get("invoice_id", "")
    invoice_date = format_date(entities.get("invoice_date", ""))
    
    # Step 6: Extract line items from tables
    rows = extract_line_items(document, invoice_date, vendor, invoice_number)
    
    # Step 6b: If no table data found, try text-based parsing
    if not rows:
        rows = extract_line_items_from_text(document.text, invoice_date, vendor, invoice_number)
    
    if not rows:
        return jsonify({"warning": "No line items found in invoice", "text": document.text}), 200
    
    # Step 7: Write to Google Sheets
    try:
        credentials, _ = default()
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!B:G",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": rows}
        ).execute()
        
        return jsonify({
            "message": "Invoice processed and added to sheet",
            "rows_added": len(rows),
            "vendor": vendor,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to write to Google Sheets: {str(e)}"}), 500

def format_date(raw_date):
    """Format date to MM/DD/YYYY format"""
    if not raw_date:
        return ""
    try:
        parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
        return parsed_date.strftime("%m/%d/%Y")
    except Exception:
        return raw_date

def clean_price(value):
    """Extract numeric price from string and format as currency"""
    if not value:
        return ""
    # Extract numeric value
    numeric_price = re.sub(r'[^0-9.-]', '', str(value))
    if numeric_price:
        try:
            # Convert to float and format as currency
            price_float = float(numeric_price)
            return f"${price_float:.2f}"
        except ValueError:
            return ""
    return ""

def extract_line_items(document, invoice_date, vendor, invoice_number):
    """Extract line items from document tables"""
    rows = []
    
    # Debug: print table count
    table_count = sum(len(page.tables) for page in document.pages)
    print(f"Found {table_count} tables in document")
    
    for page in document.pages:
        for table_idx, table in enumerate(page.tables):
            print(f"Processing table {table_idx + 1}")
            if not table.header_rows:
                continue
                
            # Get headers and find relevant columns
            headers = []
            for cell in table.header_rows[0].cells:
                if hasattr(cell.layout, 'text_anchor') and cell.layout.text_anchor:
                    headers.append(cell.layout.text_anchor.content.strip().lower())
                else:
                    headers.append("")
            
            # Check for relevant columns with broader matching
            has_item_column = any(keyword in h for h in headers for keyword in 
                                ["description", "item", "product", "sku", "code"])
            has_price_column = any(keyword in h for h in headers for keyword in 
                                 ["price", "amount", "cost", "total", "extended"])
            
            if not has_item_column or not has_price_column:
                continue
            
            # Process each row
            for row in table.body_rows:
                cells = []
                for cell in row.cells:
                    if hasattr(cell.layout, 'text_anchor') and cell.layout.text_anchor:
                        cells.append(cell.layout.text_anchor.content.strip())
                    else:
                        cells.append("")
                
                # Extract item description and price
                item_description = ""
                wholesale_price = ""
                
                for idx, header in enumerate(headers):
                    if idx < len(cells):
                        # Match item/product columns
                        if any(keyword in header for keyword in ["description", "item", "product", "sku", "code"]):
                            if not item_description or len(cells[idx]) > len(item_description):
                                item_description = cells[idx]
                        # Match price columns (prefer "your price" over "list price")
                        elif any(keyword in header for keyword in ["your price", "unit price", "price", "extended", "amount", "cost"]):
                            if not wholesale_price or "your" in header or "unit" in header:
                                wholesale_price = clean_price(cells[idx])
                
                # Only add row if we have meaningful data
                if item_description or wholesale_price:
                    rows.append([
                        invoice_date,
                        vendor,
                        invoice_number,
                        item_description,
                        wholesale_price
                    ])
    
    return rows

def extract_line_items_from_text(text, invoice_date, vendor, invoice_number):
    """Extract line items from raw text when no tables are detected"""
    rows = []
    lines = text.split('\n')
    
    # Look for product codes (pattern: 2+ letters followed by digits)
    product_pattern = r'^[A-Z]{2,}\d+'
    
    for i, line in enumerate(lines):
        line = line.strip()
        if re.match(product_pattern, line):
            # Found a product code, try to extract item data
            product_code = line
            
            # Look ahead for description, quantity, and price data in a larger window
            description = ""
            price = ""
            quantity = ""
            
            # Check next several lines for description, quantity and price info
            for j in range(i + 1, min(i + 8, len(lines))):
                next_line = lines[j].strip()
                
                # Skip empty lines
                if not next_line:
                    continue
                    
                # Look for quantity (small numbers that aren't UPCs or prices)
                if (re.match(r'^\d{1,3}$', next_line) and 
                    int(next_line) <= 100 and 
                    int(next_line) > 0 and 
                    not quantity):
                    quantity = next_line
                
                # Skip lines that are just numbers/identifiers we don't want
                if next_line in ['0', 'each', 'Set'] or re.match(r'^\d{12,}$', next_line):
                    continue
                    
                # Look for description (longer text with product details)
                if (len(next_line) > 10 and 
                    any(char.isalpha() for char in next_line) and 
                    not re.match(r'^\d+\.\d{2}$', next_line) and
                    not description):
                    description = next_line
                
                # Look for price (decimal number, prefer prices that look reasonable)
                price_match = re.search(r'\b(\d+\.\d{2})\b', next_line)
                if price_match:
                    found_price = price_match.group(1)
                    # Prefer prices that are reasonable (not 0.00, not quantities like 191009...)
                    if float(found_price) > 0 and float(found_price) < 1000 and not price:
                        price = clean_price(found_price)
            
            # Add row even if we only have product code (better to have incomplete data)
            if product_code:
                rows.append([
                    invoice_date,
                    vendor,
                    invoice_number,
                    f"{product_code} - {description}".strip(' -') if description else product_code,
                    quantity if quantity else "",
                    price if price else ""
                ])
    
    return rows
