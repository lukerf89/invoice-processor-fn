#!/usr/bin/env python3
"""
Debug quantity extraction issues
"""
import json
import re

from google.cloud import documentai_v1 as documentai

from main import *

# Test with Creative-Coop document
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

document = documentai.Document(doc_dict)

print("=== DEBUGGING QUANTITY EXTRACTION ===")

# Problem items from the user's table
problem_items = {
    "DF5599": {"current": 6, "correct": 8},
    "DF6802": {"current": 8, "correct": 6},
    "DF7753A": {"current": 0, "correct": 24},
    "DF7838A": {"current": 0, "correct": 24},
    "DF8071A": {"current": 0, "correct": 12},
    "DF7222A": {"current": 24, "correct": 0},
    "DF7225A": {"current": 60, "correct": 0},
    "DF7336": {"current": 60, "correct": 0},
}

# Find the entities containing these problem items
for i, entity in enumerate(document.entities):
    if entity.type_ == "line_item":
        entity_text = entity.mention_text

        # Check if this entity contains any problem items
        found_codes = []
        for code in problem_items.keys():
            if code in entity_text:
                found_codes.append(code)

        if found_codes:
            print(f"\n📋 Entity {i} contains: {found_codes}")
            print(f"Entity text: {entity_text}")

            # Show entity properties
            if hasattr(entity, "properties") and entity.properties:
                print(f"Entity properties:")
                for prop in entity.properties:
                    print(
                        f"  {prop.type_} = '{prop.mention_text}' (confidence: {prop.confidence:.3f})"
                    )

            # Show lines
            lines = entity_text.split("\n")
            print(f"Entity lines:")
            for line_idx, line in enumerate(lines):
                print(f"  {line_idx}: '{line}'")

                # Look for quantity patterns in each line
                qty_patterns = [
                    r"\b(\d+)\s+(\d+)\s+(?:each|lo|Set)\b",  # "8 0 each", "24 0 Set"
                    r"\b(\d+)\s+(\d+)\b",  # "8 0", "24 24"
                ]

                for pattern in qty_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    if matches:
                        print(f"    Quantity pattern found: {matches}")
            print()

print("\n🔍 Looking for quantity patterns in document text around problem items:")

# Search for each problem item in the raw document text
for product_code, info in problem_items.items():
    print(
        f"\n--- {product_code} (Current: {info['current']}, Should be: {info['correct']}) ---"
    )

    if product_code in document.text:
        # Find position and extract context
        pos = document.text.find(product_code)
        context_start = max(0, pos - 100)
        context_end = min(len(document.text), pos + 200)
        context = document.text[context_start:context_end]

        print(f"Context: ...{context}...")

        # Look for quantity patterns around this product code
        lines = context.split("\n")
        for line_idx, line in enumerate(lines):
            if product_code in line:
                print(f"  Line with {product_code}: '{line}'")

                # Look ahead a few lines for quantity info
                for ahead_idx in range(line_idx + 1, min(len(lines), line_idx + 4)):
                    ahead_line = lines[ahead_idx].strip()
                    if ahead_line:
                        print(f"    +{ahead_idx - line_idx}: '{ahead_line}'")

                        # Check for quantity patterns
                        qty_match = re.search(
                            r"\b(\d+)\s+(\d+)\s+(?:each|lo|Set)\b",
                            ahead_line,
                            re.IGNORECASE,
                        )
                        if qty_match:
                            print(f"      🎯 Quantity pattern: {qty_match.groups()}")
                break
