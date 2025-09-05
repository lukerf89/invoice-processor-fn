#!/usr/bin/env python3
"""
Analyze Creative Coop pattern to find algorithmic solution without manual corrections
"""
import json
import re

# Load the Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== ANALYZING CREATIVE COOP PATTERN ===")

# Let's look at the raw text structure more carefully
text = document.text

# Find the invoice table area
table_start = text.find("UPC | Customer | Item | Shipped")
if table_start != -1:
    # Extract the table area (first 1500 chars should cover most products)
    table_area = text[table_start : table_start + 1500]

    print("Table area structure:")
    print("=" * 50)
    print(table_area[:800].replace("\n", "\n"))
    print("=" * 50)

    # Split by pipe and analyze the pattern
    parts = [p.strip() for p in table_area.split("|") if p.strip()]

    print(f"\nFound {len(parts)} table parts")

    # Look for the exact pattern
    product_codes = []
    upcs = []
    descriptions = []

    for i, part in enumerate(parts):
        # Check if this is a UPC (12 digits)
        if re.match(r"^\d{12}$", part):
            upcs.append((i, part))
            print(f"UPC at position {i}: {part}")

        # Check if this is a product code
        elif re.match(r"^D[A-Z]\d{4}[A-Z]?$", part):
            product_codes.append((i, part))
            print(f"Product code at position {i}: {part}")

        # Check if this looks like a description (contains quotes or dimensions)
        elif len(part) > 20 and ('"' in part or "x" in part or part[0].isupper()):
            descriptions.append((i, part))
            print(f"Description at position {i}: {part[:50]}...")

    print(f"\nPattern analysis:")
    print(
        f"Found {len(upcs)} UPCs, {len(product_codes)} product codes, {len(descriptions)} descriptions"
    )

    # Try to match them by proximity
    print(f"\nProximity matching:")
    for prod_i, prod_code in product_codes[:5]:  # First 5 for analysis
        # Find closest preceding UPC and description
        closest_upc = None
        closest_desc = None
        closest_upc_dist = float("inf")
        closest_desc_dist = float("inf")

        for upc_i, upc in upcs:
            if upc_i < prod_i:  # UPC comes before product code
                dist = prod_i - upc_i
                if dist < closest_upc_dist:
                    closest_upc_dist = dist
                    closest_upc = upc

        for desc_i, desc in descriptions:
            if desc_i < prod_i:  # Description comes before product code
                dist = prod_i - desc_i
                if dist < closest_desc_dist:
                    closest_desc_dist = dist
                    closest_desc = desc

        print(f"{prod_code}:")
        print(f"  Closest UPC: {closest_upc} (distance: {closest_upc_dist})")
        print(
            f"  Closest desc: {closest_desc[:50] if closest_desc else None}... (distance: {closest_desc_dist})"
        )
        print()

# Let's also look at the pattern in a different way - sequential analysis
print("\n=== SEQUENTIAL PATTERN ANALYSIS ===")

# Find sequences of UPC -> Description -> Product Code
upc_pattern = r"\b(\d{12})\b"
product_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

upc_matches = list(re.finditer(upc_pattern, text))
product_matches = list(re.finditer(product_pattern, text))

print(
    f"Found {len(upc_matches)} UPCs and {len(product_matches)} product codes in full text"
)

# For each product code, find the text between it and the previous UPC
for i, product_match in enumerate(product_matches[:5]):
    product_code = product_match.group(1)
    product_pos = product_match.start()

    # Find the closest preceding UPC
    closest_upc = None
    closest_upc_pos = -1

    for upc_match in reversed(upc_matches):
        upc_pos = upc_match.start()
        if upc_pos < product_pos:
            closest_upc = upc_match.group(1)
            closest_upc_pos = upc_pos
            break

    if closest_upc:
        # Extract text between UPC and product code
        between_text = text[closest_upc_pos + 12 : product_pos].strip()

        # Clean and extract description
        # Remove table formatting and keep meaningful text
        lines = between_text.split("\n")
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not re.match(r"^[\d\s\.]+$", line):
                clean_lines.append(line)

        if clean_lines:
            description = clean_lines[0]  # Take the first meaningful line

            print(f"{product_code}:")
            print(f"  UPC: 0{closest_upc}")  # Add leading zero
            print(f"  Description: {description[:60]}...")
            print(f"  Raw between text: {repr(between_text[:100])}")
            print()
