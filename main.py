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
    
    # Debug: Log all detected entities
    print(f"Document AI detected entities: {entities}")
    
    # Extract vendor using confidence-based selection
    vendor = extract_best_vendor(document.entities)
    invoice_number = entities.get("invoice_id", "")
    invoice_date = format_date(entities.get("invoice_date", ""))
    
    print(f"Extracted - Vendor: '{vendor}', Invoice#: '{invoice_number}', Date: '{invoice_date}'")
    
    # Step 6: Extract line items from Document AI entities first
    rows = extract_line_items_from_entities(document, invoice_date, vendor, invoice_number)
    
    # Step 6b: If no entity data found, try table parsing
    if not rows:
        rows = extract_line_items(document, invoice_date, vendor, invoice_number)
    
    # Step 6c: Final fallback to text-based parsing
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
            range=f"{sheet_name}!A:G",
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

def extract_short_product_code(full_text, description_text=""):
    """Extract product code from various formats"""
    # Combine both texts to search in
    search_text = f"{description_text} {full_text}"
    
    # Pattern 1: Numbers + letters (like "006 AR", "008 TIN", "012 AR")
    # Look for this pattern at the start of the text
    number_letter_pattern = r'\b(\d{3}\s+[A-Z]{2,4})\b'
    matches = re.findall(number_letter_pattern, full_text)
    if matches:
        return matches[0]  # Return first match like "006 AR"
    
    # Pattern 2: Traditional product codes (like DF8011, DG0110A) 
    # 2-4 letters followed by 2-8 digits, possibly with letters at end
    short_code_pattern = r'\b([A-Z]{2,4}\d{2,8}[A-Z]?)\b'
    matches = re.findall(short_code_pattern, search_text)
    
    if matches:
        # Filter out UPCs (too long) and prefer shorter codes
        valid_codes = []
        for match in matches:
            # Skip if it's likely a UPC (long numeric after letters)
            if len(match) <= 10:  # Reasonable product code length
                valid_codes.append(match)
        
        if valid_codes:
            # Return the first valid match
            return valid_codes[0]
    
    return None

def extract_wholesale_price(full_text):
    """Extract wholesale price (typically the second price in a sequence)"""
    # Find all price patterns in the text
    price_pattern = r'\b(\d+\.\d{2})\b'
    prices = re.findall(price_pattern, full_text)
    
    if len(prices) >= 2:
        # When we have multiple prices like "8.50 6.80 40.80"
        # The second price is typically the wholesale price
        wholesale_price = prices[1]
        
        # Validate it's a reasonable price (not a total amount)
        try:
            price_val = float(wholesale_price)
            if 0.01 <= price_val <= 500.00:  # Reasonable price range
                return f"${price_val:.2f}"
        except ValueError:
            pass
    
    elif len(prices) == 1:
        # Only one price found, use it
        try:
            price_val = float(prices[0])
            if 0.01 <= price_val <= 500.00:
                return f"${price_val:.2f}"
        except ValueError:
            pass
    
    return None

def extract_shipped_quantity(full_text):
    """Extract shipped quantity from patterns like '8 00' or '24\n24'"""
    # Remove product codes and descriptions first to focus on numbers
    # Look for the pattern after product code but before prices
    
    # Split by spaces and newlines to get individual tokens
    tokens = re.split(r'[\s\n]+', full_text)
    
    quantities = []
    found_product_code = False
    
    for i, token in enumerate(tokens):
        # Skip the product code part (like "006", "AR")
        if re.match(r'^\d{3}$', token) or re.match(r'^[A-Z]{2,4}$', token):
            found_product_code = True
            continue
        
        # Look for pure numbers that could be quantities
        if re.match(r'^\d+$', token):
            num = int(token)
            # Filter reasonable quantities (1-999, not prices like 16.50 or amounts like 132.00)
            if 1 <= num <= 999 and len(token) <= 3:
                # Skip if it looks like part of a price (next token might be decimal)
                if i + 1 < len(tokens) and re.match(r'^\d{2}$', tokens[i + 1]):
                    continue  # This is likely "16.50" split as "16" "50"
                quantities.append(str(num))
    
    if quantities:
        # Return the first valid quantity after product code
        return quantities[0]
    
    # Fallback: look for any reasonable quantity
    for token in tokens:
        if re.match(r'^\d+$', token):
            num = int(token)
            if 1 <= num <= 999 and len(token) <= 3:
                return str(num)
    
    return None

def extract_best_vendor(entities):
    """Extract vendor name using confidence scores and priority order"""
    # Priority order of vendor-related entity types
    vendor_fields = [
        "remit_to_name",
        "supplier_name", 
        "vendor_name",
        "bill_from_name"
    ]
    
    vendor_candidates = []
    
    # Collect all vendor-related entities with their confidence scores
    for entity in entities:
        if entity.type_ in vendor_fields and entity.mention_text.strip():
            vendor_candidates.append({
                'type': entity.type_,
                'text': entity.mention_text.replace('\n', ' ').strip(),
                'confidence': entity.confidence
            })
    
    print(f"Vendor candidates: {vendor_candidates}")
    
    if not vendor_candidates:
        return ""
    
    # If we have multiple candidates, prefer by confidence first, then by priority
    if len(vendor_candidates) > 1:
        # Sort by confidence (descending), then by priority order
        vendor_candidates.sort(key=lambda x: (
            -x['confidence'],  # Higher confidence first
            vendor_fields.index(x['type']) if x['type'] in vendor_fields else 999  # Lower index = higher priority
        ))
        
        print(f"Selected vendor: {vendor_candidates[0]['text']} (type: {vendor_candidates[0]['type']}, confidence: {vendor_candidates[0]['confidence']:.3f})")
    
    return vendor_candidates[0]['text']

def extract_line_items_from_entities(document, invoice_date, vendor, invoice_number):
    """Extract line items from Document AI entities"""
    rows = []
    
    # Debug: Log all entity types and their properties
    print("=== Document AI Entity Analysis ===")
    line_item_count = 0
    
    for i, entity in enumerate(document.entities):
        print(f"Entity {i}: {entity.type_} = '{entity.mention_text}' (confidence: {entity.confidence:.3f})")
        
        if entity.type_ == "line_item":
            line_item_count += 1
            # Extract line item properties
            item_description = ""
            product_code = ""
            unit_price = ""
            quantity = ""
            line_total = ""
            
            # Store the full line item text for advanced parsing
            full_line_text = entity.mention_text.strip()
            
            # Process properties of the line item
            if hasattr(entity, 'properties') and entity.properties:
                print(f"  Line item {line_item_count} properties:")
                for prop in entity.properties:
                    print(f"    {prop.type_} = '{prop.mention_text}' (confidence: {prop.confidence:.3f})")
                    
                    if prop.type_ == "line_item/description":
                        item_description = prop.mention_text.strip()
                    elif prop.type_ == "line_item/product_code":
                        # Store the UPC/long code as fallback
                        candidate_code = prop.mention_text.strip()
                        if not product_code:
                            product_code = candidate_code
                    elif prop.type_ == "line_item/unit_price":
                        # Store the price (we'll parse multiple prices from full text later)
                        unit_price = clean_price(prop.mention_text)
                    elif prop.type_ == "line_item/quantity":
                        # Store the quantity (we'll parse multiple quantities from full text later)
                        quantity = prop.mention_text.strip()
                    elif prop.type_ == "line_item/amount":
                        line_total = clean_price(prop.mention_text)
            
            # Advanced parsing of the full line item text
            print(f"  Full line text: '{full_line_text}'")
            
            # 1. Extract the correct product code (short alphanumeric code)
            short_product_code = extract_short_product_code(full_line_text, item_description)
            if short_product_code:
                product_code = short_product_code
                print(f"  -> Found short product code: '{product_code}'")
            
            # 2. Use Document AI unit_price if available, otherwise try to extract from text
            if not unit_price:
                # Try to extract wholesale price from text if Document AI didn't find it
                wholesale_price = extract_wholesale_price(full_line_text)
                if wholesale_price:
                    unit_price = wholesale_price
                    print(f"  -> Found wholesale price from text: '{unit_price}'")
            else:
                print(f"  -> Using Document AI unit_price: '{unit_price}'")
            
            # 3. Extract shipped quantity - prioritize Document AI property first
            if hasattr(entity, 'properties') and entity.properties:
                for prop in entity.properties:
                    if prop.type_ == "line_item/quantity":
                        # Clean the quantity from Document AI property
                        qty_text = prop.mention_text.strip()
                        # Extract first non-zero number from patterns like "8 00"
                        qty_numbers = re.findall(r'\b(\d+)\b', qty_text)
                        if qty_numbers:
                            for num in qty_numbers:
                                if int(num) > 0:
                                    quantity = num
                                    print(f"  -> Found quantity from property: '{quantity}'")
                                    break
                        break
            
            # Fallback to text parsing if no quantity found
            if not quantity:
                shipped_quantity = extract_shipped_quantity(full_line_text)
                if shipped_quantity:
                    quantity = shipped_quantity
                    print(f"  -> Found shipped quantity from text: '{quantity}'")
            
            # If no description but we have the main entity text, use that
            if not item_description and entity.mention_text:
                item_description = entity.mention_text.strip()
            
            # Create a complete description with product code if available
            full_description = ""
            if product_code and item_description:
                # If product code is just a UPC (long number), put it at the end
                if product_code.isdigit() and len(product_code) > 8:
                    full_description = f"{item_description} (UPC: {product_code})"
                else:
                    full_description = f"{product_code} - {item_description}"
            elif item_description:
                full_description = item_description
            elif product_code:
                full_description = product_code
            
            # Only add row if we have a meaningful description AND either price or quantity
            # This filters out incomplete/malformed line items
            if (full_description and len(full_description) > 5 and 
                (unit_price or quantity)):
                
                # Skip rows with zero amounts unless they have valid quantity
                skip_row = False
                if line_total == "$0.00" and not quantity:
                    skip_row = True
                
                if not skip_row:
                    rows.append([
                        "",  # Column A placeholder
                        invoice_date,
                        vendor, 
                        invoice_number,
                        full_description,
                        unit_price if unit_price else "",
                        quantity if quantity else ""
                    ])
                    print(f"  -> Added row: {full_description}, {unit_price}, Qty: {quantity}")
                else:
                    print(f"  -> Skipped row (zero amount, no qty): {full_description}")
            else:
                print(f"  -> Skipped row (insufficient data): desc='{full_description}', price='{unit_price}', qty='{quantity}'")
    
    print(f"Found {line_item_count} line_item entities, created {len(rows)} rows")
    return rows

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
                        "",  # Empty placeholder for column A
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
            full_line_context = line
            
            # Gather context from surrounding lines
            for j in range(i + 1, min(i + 8, len(lines))):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                
                # Add to context for advanced parsing
                full_line_context += f" {next_line}"
                
                # Look for description (longer text with product details)
                if (len(next_line) > 10 and 
                    any(char.isalpha() for char in next_line) and 
                    not re.match(r'^\d+\.\d{2}$', next_line) and
                    not description):
                    description = next_line
            
            # Use advanced parsing functions
            short_product_code = extract_short_product_code(full_line_context, description)
            if short_product_code:
                product_code = short_product_code
            
            wholesale_price = extract_wholesale_price(full_line_context)
            price = wholesale_price if wholesale_price else ""
            
            shipped_quantity = extract_shipped_quantity(full_line_context)
            quantity = shipped_quantity if shipped_quantity else ""
            
            # Add row even if we only have product code (better to have incomplete data)
            if product_code:
                rows.append([
                    "",  # Empty placeholder for column A
                    invoice_date,
                    vendor,
                    invoice_number,
                    f"{product_code} - {description}".strip(' -') if description else product_code,
                    price if price else "",  # Column F: Wholesale Price
                    quantity if quantity else ""  # Column G: Quantity
                ])
    
    return rows
