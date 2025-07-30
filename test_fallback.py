#!/usr/bin/env python3
"""
Test the fallback processing for Creative-Coop invoices
"""

import json
from main import process_invoice_document

# Load the problematic Creative-Coop invoice
with open('test_invoices/CS003837319_Error_docai_output.json', 'r') as f:
    docai_data = json.load(f)

# Test the full processing pipeline (this will use specialized Creative-Coop processing)
print("Testing Creative-Coop invoice with fallback processing...")
try:
    result = process_invoice_document(docai_data)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")