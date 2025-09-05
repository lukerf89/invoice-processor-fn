#!/usr/bin/env python3
"""
Debug description extraction to see why we're getting incomplete titles
"""
import json

from google.cloud import documentai_v1 as documentai

with open("test_invoices/Harpercollins_04-29-2025_docai_output.json", "r") as f:
    doc_dict = json.load(f)

document = documentai.Document(doc_dict)

# Check the raw text around specific ISBNs to see full titles
text = document.text
target_isbn = "9780008547110"
pos = text.find(target_isbn)
if pos != -1:
    # Show context around this ISBN
    start = max(0, pos - 100)
    end = min(len(text), pos + 200)
    context = text[start:end]
    print(f"Context around {target_isbn}:")
    print(repr(context))
    print()

# Check what Document AI extracted for line items
count = 0
for entity in document.entities:
    if entity.type_ == "line_item":
        count += 1
        print(f"\nLine item {count}:")
        print(f"  Full entity text: {repr(entity.mention_text[:100])}...")

        if hasattr(entity, "properties") and entity.properties:
            for prop in entity.properties:
                if prop.type_ == "line_item/product_code":
                    print(f"  Product code: {repr(prop.mention_text)}")
                elif prop.type_ == "line_item/description":
                    print(f"  Description: {repr(prop.mention_text)}")

        if count >= 5:  # Just check first 5
            break

# Look for full book titles in the raw text
print("\n=== FULL TITLES IN RAW TEXT ===")
import re

# Look for patterns like "ISBN Title" in the raw text
isbn_patterns = [r"9780008547110[^\n]*", r"9780062645425[^\n]*", r"9780001839236[^\n]*"]

for pattern in isbn_patterns:
    matches = re.findall(pattern, text)
    for match in matches:
        if len(match) > 20:  # Only show substantial matches
            print(f"Found: {match}")
