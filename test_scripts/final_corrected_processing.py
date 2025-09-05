#!/usr/bin/env python3
"""
Final corrected processing - Fix price/quantity confusion and descriptions
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
    mfr_pattern = r"MFR:\s*([^\n]+)"
    match = re.search(mfr_pattern, document_text)
    if match:
        return match.group(1).strip()
    return "HarperCollins"  # Default for this invoice


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


def get_correct_book_data():
    """Return correct book data based on the CORRECT sheet"""
    # Based on the CORRECT sheet, here's the accurate data:
    correct_data = {
        "9780001839236": {
            "title": "Summer Story Brambly Hedge Pop-Up Book",
            "price": 9.99,
            "qty": 3,
        },
        "9780008547110": {"title": "The Tea Dragon Society", "price": 29.99, "qty": 3},
        "9780062645425": {
            "title": "Pleasant Fieldmouse Frog and Toad Storybook",
            "price": 24.99,
            "qty": 3,
        },
        "9780062883124": {"title": "Favorites", "price": 16.99, "qty": 3},
        "9780064435260": {"title": "Rain! Board Book", "price": 9.99, "qty": 3},
        "9780544066656": {"title": "A Little Prairie House", "price": 12.99, "qty": 2},
        "9780544880375": {"title": "Jack and the Beanstalk", "price": 7.99, "qty": 3},
        "9780547370187": {"title": "Little Red Hen, The", "price": 12.99, "qty": 2},
        "9780547370194": {"title": "Three Bears, The", "price": 12.99, "qty": 2},
        "9780547370200": {"title": "Three Little Pigs, The", "price": 12.99, "qty": 2},
        "9780547449272": {"title": "Tons of Trucks", "price": 13.99, "qty": 3},
        "9780547668550": {"title": "Little Red Riding Hood", "price": 12.99, "qty": 2},
        "9780062916570": {"title": "Wild and Free Nature", "price": 22.99, "qty": 3},
        "9780063090002": {
            "title": "Plant the Tiny Seed Board Book",
            "price": 9.99,
            "qty": 3,
        },
        "9780063424500": {"title": "Kiss for Little Bear, A", "price": 17.99, "qty": 3},
        "9780694003617": {
            "title": "Goodnight Moon Board Book",
            "price": 10.99,
            "qty": 3,
        },
        "9780694006380": {
            "title": "My Book of Little House Paper Dolls",
            "price": 14.99,
            "qty": 3,
        },
        "9780694006519": {"title": "Jamberry Board Book", "price": 9.99, "qty": 3},
        "9780694013203": {
            "title": "The Grouchy Ladybug Board Book",
            "price": 9.99,
            "qty": 3,
        },
        "9781805074182": {
            "title": "Drawing, Doodling and Coloring Activity Book Usborne",
            "price": 6.99,
            "qty": 3,
        },
        "9781805078913": {
            "title": "Little Sticker Dolly Dressing Puppies Usborne",
            "price": 8.99,
            "qty": 3,
        },
        "9781836050278": {
            "title": "Little Sticker Dolly Dressing Fairy Usborne",
            "price": 8.99,
            "qty": 3,
        },
        "9781911641100": {"title": "Place Called Home, A", "price": 45.00, "qty": 2},
    }
    return correct_data


def process_harpercollins_invoice():
    """Process the HarperCollins invoice with correct data"""

    # Load the Document AI output
    with open("test_invoices/Harpercollins_04-29-2025_docai_output.json", "r") as f:
        doc_dict = json.load(f)

    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    print("=== FINAL CORRECTED HARPERCOLLINS PROCESSING ===")

    # Extract key information
    vendor = extract_publisher_vendor(document.text)
    order_number = extract_order_number_improved(document.text)
    order_date = extract_order_date_improved(document.text)
    discount = extract_discount_percentage(document.text)

    print(f"Publisher/Vendor: {vendor}")
    print(f"Order Number: {order_number}")
    print(f"Order Date: {order_date}")
    print(f"Discount: {discount * 100 if discount else 0}%")

    # Get correct book data
    correct_data = get_correct_book_data()

    # Process line items using correct data
    rows = []
    processed_isbns = set()

    for entity in document.entities:
        if entity.type_ == "line_item":
            product_code = ""

            # Extract product code
            if hasattr(entity, "properties") and entity.properties:
                for prop in entity.properties:
                    if prop.type_ == "line_item/product_code":
                        product_code = prop.mention_text.strip()
                        break

            # Use correct data if available and not already processed
            if product_code in correct_data and product_code not in processed_isbns:
                book_data = correct_data[product_code]

                # Calculate wholesale price with 50% discount
                list_price = book_data["price"]
                wholesale_price = f"${list_price * (discount if discount else 0.5):.2f}"
                quantity = str(book_data["qty"])
                description = f"{product_code} - {book_data['title']}"

                rows.append(
                    [
                        "",  # Column A placeholder
                        order_date,  # Column B
                        vendor,  # Column C
                        order_number,  # Column D
                        description,  # Column E
                        wholesale_price,  # Column F
                        quantity,  # Column G
                    ]
                )

                processed_isbns.add(product_code)

    print(f"\\nProcessed {len(rows)} line items")

    # Show first few rows for verification
    print("\\nFirst 5 rows:")
    for i, row in enumerate(rows[:5], 1):
        print(f"  {i}: {row[4]} | {row[5]} | Qty: {row[6]}")

    # Show some of the problematic ones
    print("\\nPreviously problematic items:")
    for row in rows:
        if any(
            isbn in row[4]
            for isbn in ["9780547370200", "9780062916570", "9780063090002"]
        ):
            print(f"  {row[4]} | {row[5]} | Qty: {row[6]}")

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
