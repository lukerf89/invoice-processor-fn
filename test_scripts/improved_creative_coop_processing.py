#!/usr/bin/env python3
"""
Improved Creative Coop processing with correct description/UPC mapping
"""
import json
import re
import csv
from main import *


def extract_creative_coop_mapping_from_raw_text(document_text):
    """
    Extract correct product->description->UPC mapping from Creative Coop raw text
    """
    # The Creative Coop invoice has a specific pattern:
    # UPC | Description | ProductCode | UPC | Description | ProductCode | ...
    # Where the description for a product comes BEFORE the product code

    mappings = {}

    # First, extract all product codes and their positions
    product_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
    product_matches = list(re.finditer(product_pattern, document_text))

    # Extract all UPC codes (12 digits) and their positions
    upc_pattern = r"\b(\d{12})\b"
    upc_matches = list(re.finditer(upc_pattern, document_text))

    print(
        f"Found {len(product_matches)} product codes and {len(upc_matches)} UPC codes"
    )

    # For each product code, find the closest preceding description and UPC
    for product_match in product_matches:
        product_code = product_match.group(1)
        product_pos = product_match.start()

        # Look backward from the product code to find description and UPC
        # The pattern is typically: UPC -> Description -> ProductCode

        # Find the closest UPC before this product code
        closest_upc = None
        closest_upc_distance = float("inf")

        for upc_match in upc_matches:
            upc_pos = upc_match.start()
            if upc_pos < product_pos:  # UPC comes before product code
                distance = product_pos - upc_pos
                if (
                    distance < closest_upc_distance and distance < 500
                ):  # Reasonable distance
                    closest_upc = upc_match.group(1)
                    closest_upc_distance = distance

        # Extract text between UPC and product code for description
        description = ""
        if closest_upc:
            # Find the position of the UPC
            upc_pos = document_text.rfind(closest_upc, 0, product_pos)
            if upc_pos != -1:
                # Extract text between UPC and product code
                between_text = document_text[
                    upc_pos + len(closest_upc) : product_pos
                ].strip()

                # Clean up the description
                # Remove extra whitespace, pipes, and common formatting artifacts
                description = re.sub(r"\s*\|\s*", " ", between_text)
                description = re.sub(r"\s+", " ", description).strip()

                # Remove common non-descriptive elements
                description = re.sub(
                    r'^[^\w"]*', "", description
                )  # Remove leading non-word chars
                description = re.sub(
                    r'[^\w"\')\s]*$', "", description
                )  # Remove trailing junk

                # Ensure UPC starts with 0 for 12-digit codes
                formatted_upc = (
                    f"0{closest_upc}" if len(closest_upc) == 12 else closest_upc
                )

                mappings[product_code] = {
                    "upc": formatted_upc,
                    "description": description.strip(),
                    "raw_upc": closest_upc,
                }

                print(
                    f"{product_code}: UPC={formatted_upc}, Desc='{description[:50]}{'...' if len(description) > 50 else ''}'"
                )

    return mappings


def process_creative_coop_with_improved_mapping():
    """Process Creative Coop invoice with improved mapping"""

    print("=== IMPROVED CREATIVE COOP PROCESSING ===")

    # Load the Creative-Coop document
    with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
        doc_dict = json.load(f)

    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    # Extract correct mappings from raw text
    correct_mappings = extract_creative_coop_mapping_from_raw_text(document.text)

    # Process using standard extraction but override descriptions/UPCs
    entities = {e.type_: e.mention_text for e in document.entities}
    vendor = extract_best_vendor(document.entities)
    invoice_number = entities.get("invoice_id", "")
    invoice_date = format_date(entities.get("invoice_date", ""))

    print(f"Vendor: '{vendor}'")
    print(f"Invoice Number: '{invoice_number}'")
    print(f"Invoice Date: '{invoice_date}'")

    # Extract line items but use corrected mappings
    rows = []

    # Process each line item entity
    for entity in document.entities:
        if entity.type_ == "line_item":
            # Extract basic properties
            item_description = ""
            unit_price = ""
            quantity = ""

            if hasattr(entity, "properties") and entity.properties:
                for prop in entity.properties:
                    if prop.type_ == "line_item/unit_price":
                        unit_price = clean_price(prop.mention_text)
                    elif prop.type_ == "line_item/quantity":
                        qty_text = prop.mention_text.strip()
                        qty_match = re.search(r"\b(\d+(?:\.\d+)?)\b", qty_text)
                        if qty_match:
                            qty_value = float(qty_match.group(1))
                            if qty_value > 0:  # Only include positive quantities
                                if qty_value == int(qty_value):
                                    quantity = str(int(qty_value))
                                else:
                                    quantity = str(qty_value)

            # Find product codes in this entity
            product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", entity.mention_text)

            for product_code in product_codes:
                if product_code in correct_mappings and unit_price and quantity:
                    mapping = correct_mappings[product_code]

                    # Use Creative-Coop specific quantity extraction as fallback
                    if not quantity:
                        creative_coop_qty = extract_creative_coop_quantity(
                            document.text, product_code
                        )
                        if creative_coop_qty is not None:
                            quantity = creative_coop_qty

                    # Create corrected description
                    full_description = f"{product_code} - UPC: {mapping['upc']} - {mapping['description']}"

                    # Only add rows with valid data
                    if quantity and quantity != "0" and unit_price:
                        rows.append(
                            [
                                "",  # Column A placeholder
                                invoice_date,
                                vendor,
                                invoice_number,
                                full_description,
                                unit_price,
                                quantity,
                            ]
                        )
                        print(
                            f"✓ Added: {product_code} - {mapping['description'][:40]}... | {unit_price} | Qty: {quantity}"
                        )

    print(f"\nCreated {len(rows)} corrected rows")

    # Export to CSV
    csv_filename = "test_invoices/creative_coop_corrected_output.csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(
            [
                "Column A",
                "Date",
                "Vendor",
                "Invoice Number",
                "Description",
                "Unit Price",
                "Quantity",
            ]
        )

        # Write data rows
        for row in rows:
            writer.writerow(row)

    print(f"✅ Corrected CSV file created: {csv_filename}")

    return rows, correct_mappings


if __name__ == "__main__":
    rows, mappings = process_creative_coop_with_improved_mapping()

    print(f"\n📋 Sample corrected items:")
    for i, row in enumerate(rows[:10], 1):
        print(
            f"  {i:2d}: {row[4][:60]}{'...' if len(row[4]) > 60 else ''} | {row[5]} | Qty: {row[6]}"
        )
