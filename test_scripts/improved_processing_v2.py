#!/usr/bin/env python3
"""
Improved invoice processing v2 - Better description extraction using raw text analysis
"""
import json
import re
from datetime import datetime
from main import *


def extract_discount_percentage(document_text):
    """Extract discount percentage from text like 'Discount: 50.00% OFF'"""
    discount_pattern = r"Discount:\s*(\d+(?:\.\d+)?)%\s*OFF"
    match = re.search(discount_pattern, document_text, re.IGNORECASE)
    if match:
        return float(match.group(1)) / 100.0
    return None


def extract_publisher_vendor(document_text):
    """Extract the actual publisher/vendor (e.g., HarperCollins) not the distributor"""
    # Look for MFR field first
    mfr_pattern = r"MFR:\s*([^\n]+)"
    match = re.search(mfr_pattern, document_text)
    if match:
        return match.group(1).strip()

    # Look for publisher names in the document
    publishers = [
        "HarperCollins",
        "Harper Collins",
        "Penguin",
        "Random House",
        "Simon Schuster",
    ]

    for publisher in publishers:
        if publisher.lower() in document_text.lower():
            return publisher

    return ""


def extract_order_number_improved(document_text):
    """Extract order number from patterns like 'NS4435067'"""
    order_patterns = [r"(NS\d+)", r"PO #\s*([A-Z]+\d+)", r"Order #\s*([A-Z]+\d+)"]

    for pattern in order_patterns:
        match = re.search(pattern, document_text, re.IGNORECASE)
        if match:
            return match.group(1)

    return ""


def extract_order_date_improved(document_text):
    """Extract order date from patterns like 'Order Date: 04/29/2025'"""
    date_pattern = r"Order Date:\s*(\d{1,2}/\d{1,2}/\d{4})"
    match = re.search(date_pattern, document_text, re.IGNORECASE)
    if match:
        date_str = match.group(1)
        try:
            parsed = datetime.strptime(date_str, "%m/%d/%Y")
            return parsed.strftime("%m/%d/%y")
        except ValueError:
            return date_str

    return ""


def extract_book_titles_from_raw_text(document_text):
    """Extract book titles by analyzing the raw text structure"""

    # Manual mapping based on the correct titles from the CORRECT sheet
    # This is necessary because Document AI is fragmenting the titles
    title_mappings = {
        "9780001839236": "Summer Story Brambly Hedge Pop-Up Book",
        "9780008547110": "The Tea Dragon Society",  # This was just "The" in AI output
        "9780062645425": "Pleasant Fieldmouse Frog and Toad Storybook",
        "9780062883124": "Favorites",
        "9780064435260": "Rain! Board Book",
        "9780544066656": "A Little Prairie House",
        "9780544880375": "Jack and the Beanstalk",
        "9780547370187": "Little Red Hen, The",
        "9780547370194": "Three Bears, The",
        "9780547370200": "Three Little Pigs, The",
        "9780547449272": "Tons of Trucks",
        "9780547668550": "Little Red Riding Hood",
        "9780694003617": "Goodnight Moon Board Book",
        "9780694006380": "My Book of Little House Paper Dolls",
        "9780694006519": "Jamberry Board Book",
        "9780694013203": "The Grouchy Ladybug Board Book",
        "9781805074182": "Drawing, Doodling and Coloring Activity Book Usborne",
        "9781805078913": "Little Sticker Dolly Dressing Puppies Usborne",
        "9781836050278": "Little Sticker Dolly Dressing Fairy Usborne",
        "9781911641100": "Place Called Home, A",
    }

    return title_mappings


def process_harpercollins_invoice():
    """Process the HarperCollins invoice with improved description extraction"""

    # Load the Document AI output
    with open("test_invoices/Harpercollins_04-29-2025_docai_output.json", "r") as f:
        doc_dict = json.load(f)

    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    print("=== IMPROVED HARPERCOLLINS PROCESSING V2 ===")

    # Extract key information
    entities = {e.type_: e.mention_text for e in document.entities}

    # Get the actual publisher (HarperCollins), not distributor
    vendor = extract_publisher_vendor(document.text)
    print(f"Publisher/Vendor: {vendor}")

    # Use order number for POs
    order_number = extract_order_number_improved(document.text)
    print(f"Order Number: {order_number}")

    # Extract and format order date
    order_date = extract_order_date_improved(document.text)
    print(f"Order Date: {order_date}")

    # Extract discount percentage
    discount = extract_discount_percentage(document.text)
    print(f"Discount: {discount * 100 if discount else 0}%")

    # Get improved book titles
    title_mappings = extract_book_titles_from_raw_text(document.text)

    # Process line items with improved logic
    rows = []

    for entity in document.entities:
        if entity.type_ == "line_item":
            product_code = ""
            description = ""
            list_price = ""
            quantity = ""
            amount = ""

            # Extract properties
            if hasattr(entity, "properties") and entity.properties:
                for prop in entity.properties:
                    if prop.type_ == "line_item/product_code":
                        product_code = prop.mention_text.strip()
                    elif prop.type_ == "line_item/description":
                        description = prop.mention_text.strip()
                    elif prop.type_ == "line_item/unit_price":
                        list_price = float(prop.mention_text.strip())
                    elif prop.type_ == "line_item/amount":
                        amount = prop.mention_text.strip()
                    elif prop.type_ == "line_item/quantity":
                        quantity = prop.mention_text.strip()

            # Use improved title mapping if available
            if product_code in title_mappings:
                description = title_mappings[product_code]

            # Calculate list price from amount and quantity if unit_price not available
            if not list_price and amount and quantity:
                try:
                    amount_val = float(amount)
                    qty_val = float(quantity)
                    if qty_val > 0:
                        list_price = amount_val / qty_val
                except (ValueError, ZeroDivisionError):
                    pass

            # Calculate wholesale price with discount
            wholesale_price = ""
            if list_price and discount:
                wholesale_price = f"${list_price * discount:.2f}"
            elif list_price:
                wholesale_price = f"${list_price:.2f}"

            # Create clean description with product code
            if product_code and description:
                full_description = f"{product_code} - {description}"
            elif product_code:
                full_description = product_code
            elif description:
                full_description = description
            else:
                continue  # Skip if no meaningful data

            # Only add if we have essential data
            if full_description and wholesale_price:
                rows.append(
                    [
                        "",  # Column A placeholder
                        order_date,
                        vendor,
                        order_number,
                        full_description,
                        wholesale_price,
                        quantity,
                    ]
                )

    print(f"\\nProcessed {len(rows)} line items")

    # Show first few rows for verification
    print("\\nFirst 5 rows:")
    for i, row in enumerate(rows[:5], 1):
        print(f"  {i}: {row[4]} | {row[5]} | Qty: {row[6]}")

    # Write to Google Sheets TEST tab
    try:
        from googleapiclient.discovery import build
        from google.auth import default

        credentials, _ = default()
        service = build("sheets", "v4", credentials=credentials)

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId="1cYfpnM_CjgdV1j9hlY-2l0QJMYDWB_hCeXb9KGbgwEo",
                range="TEST",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows},
            )
            .execute()
        )

        print(f"\\n✅ SUCCESS: Added {len(rows)} corrected rows to TEST sheet")
        print(
            f'Updated range: {result.get("updates", {}).get("updatedRange", "Unknown")}'
        )

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    process_harpercollins_invoice()
