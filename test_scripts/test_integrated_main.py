#!/usr/bin/env python3
"""
Test the integrated main.py with HarperCollins processing
"""
import json

from main import *

# Test with HarperCollins document
with open("test_invoices/Harpercollins_04-29-2025_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

print("=== TESTING INTEGRATED MAIN.PY ===")

# Test vendor detection
vendor_type = detect_vendor_type(document.text)
print(f"Detected vendor type: {vendor_type}")

# Test HarperCollins processing
if vendor_type == "HarperCollins":
    rows = process_harpercollins_document(document)
    print(f"\\nHarperCollins processing returned {len(rows)} rows")

    print("\\nFirst 3 rows:")
    for i, row in enumerate(rows[:3], 1):
        print(f"  {i}: {', '.join(str(x) for x in row)}")

    print("\\nLast 3 rows:")
    for i, row in enumerate(rows[-3:], len(rows) - 2):
        print(f"  {i}: {', '.join(str(x) for x in row)}")
else:
    print("Not detected as HarperCollins - would use generic processing")
