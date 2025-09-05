#!/usr/bin/env python3
"""
Debug DF6802 missing issue
"""
import json
import re

from google.cloud import documentai_v1 as documentai

from main import *

# Test with Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

document = documentai.Document(doc_dict)

print("=== DEBUGGING DF6802 MISSING ISSUE ===")

# Search for DF6802 in the raw text
print("1. Searching for DF6802 in raw document text:")
if "DF6802" in document.text:
    print("✅ DF6802 found in document text")
    # Find context around DF6802
    pos = document.text.find("DF6802")
    context_start = max(0, pos - 100)
    context_end = min(len(document.text), pos + 200)
    context = document.text[context_start:context_end]
    print(f"Context: ...{context}...")
else:
    print("❌ DF6802 NOT found in document text")

# Search for DF6802 in entities
print("\n2. Searching for DF6802 in entities:")
found_in_entities = False
for i, entity in enumerate(document.entities):
    if entity.type_ == "line_item" and "DF6802" in entity.mention_text:
        print(f"✅ DF6802 found in entity {i}:")
        print(f"   Type: {entity.type_}")
        print(f"   Text: {entity.mention_text}")
        print(f"   Confidence: {entity.confidence}")
        found_in_entities = True

        # Check if this entity has multiple product codes
        product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", entity.mention_text)
        print(f"   Product codes found: {product_codes}")

        # Show the entity structure line by line
        print(f"   Entity text lines:")
        lines = entity.mention_text.split("\n")
        for idx, line in enumerate(lines):
            print(f"      {idx}: '{line}'")

        # Check for UPC codes in the entity
        upc_codes = re.findall(r"\b(\d{12,13})\b", entity.mention_text)
        print(f"   UPC codes found: {upc_codes}")

        if len(product_codes) > 1:
            print("   -> This is a combined line item")

            # Debug DF6802 specific processing
            print("\n   -> Debugging DF6802 line processing:")
            lines = entity.mention_text.split("\n")
            for line_idx, line in enumerate(lines):
                if "DF6802" in line:
                    print(f"      Line {line_idx} with DF6802: '{line}'")
                    product_pos = line.find("DF6802")
                    after_product = line[product_pos + 6 :].strip()  # 6 = len("DF6802")
                    print(f"      Text after DF6802: '{after_product}'")

                    # Test regex
                    import re

                    desc_match = re.search(
                        r"^\s*(.+?)(?:\s+\d+\s+\d+\s+(?:each|lo|Set)|\s+TRF)",
                        after_product,
                    )
                    if desc_match:
                        print(
                            f"      Current regex match: '{desc_match.group(1).strip()}'"
                        )
                        # Test alternative regex
                        desc_match2 = re.search(
                            r"^(\S.+?)(?:\s+\d+\s+\d+\s+(?:each|lo|Set)|\s+TRF)",
                            after_product,
                        )
                        if desc_match2:
                            print(
                                f"      Alternative regex match: '{desc_match2.group(1).strip()}'"
                            )
                    else:
                        print(f"      Regex NO MATCH")

            # Test the split function
            split_items = split_combined_line_item(
                entity.mention_text, entity, document.text
            )
            print(f"\n   -> Split into {len(split_items)} items:")
            for j, item in enumerate(split_items):
                print(
                    f"      {j+1}. {item.get('description', 'NO DESC')} - {item.get('unit_price', 'NO PRICE')}"
                )
                if "DF6802" in item.get("description", ""):
                    print(f"         ✅ DF6802 found in split item!")

if not found_in_entities:
    print("❌ DF6802 NOT found in any entities")

print("\n3. Expected UPC for DF6802: 0191009519157")
print("   Searching for this UPC in document:")
if "191009519157" in document.text:
    print("✅ UPC 0191009519157 found in document text")
    upc_pos = document.text.find("191009519157")
    upc_context_start = max(0, upc_pos - 50)
    upc_context_end = min(len(document.text), upc_pos + 50)
    upc_context = document.text[upc_context_start:upc_context_end]
    print(f"UPC Context: ...{upc_context}...")
else:
    print("❌ UPC 0191009519157 NOT found in document text")
