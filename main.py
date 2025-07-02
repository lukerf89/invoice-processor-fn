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
    
    vendor = entities.get("supplier_name", "")
    invoice_number = entities.get("invoice_id", "")
    invoice_date = format_date(entities.get("invoice_date", ""))
    
    # Step 6: Extract line items from tables
    rows = extract_line_items(document, invoice_date, vendor, invoice_number)
    
    if not rows:
        return jsonify({"warning": "No line items found in invoice", "text": document.text}), 200
    
    # Step 7: Write to Google Sheets
    try:
        credentials, _ = default()
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
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
    """Extract numeric price from string"""
    if not value:
        return ""
    return re.sub(r'[^0-9.-]', '', str(value))

def extract_line_items(document, invoice_date, vendor, invoice_number):
    """Extract line items from document tables"""
    rows = []
    
    for page in document.pages:
        for table in page.tables:
            if not table.header_rows:
                continue
                
            # Get headers and find relevant columns
            headers = []
            for cell in table.header_rows[0].cells:
                if hasattr(cell.layout, 'text_anchor') and cell.layout.text_anchor:
                    headers.append(cell.layout.text_anchor.content.strip().lower())
                else:
                    headers.append("")
            
            # Skip if no relevant headers found
            if not any("description" in h or "item" in h for h in headers) or not any("price" in h for h in headers):
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
                        if "description" in header or "item" in header:
                            item_description = cells[idx]
                        elif "price" in header or "amount" in header:
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
