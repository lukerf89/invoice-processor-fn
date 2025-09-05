#!/usr/bin/env python3
"""
Validate Creative Coop mappings against expected output
"""
from improved_creative_coop_processing import *

# Expected mappings from the user's corrections
expected_mapping = {
    "DA4315": {
        "upc": "0807472767956",
        "description": '3-1/4" Rnd x 4"H 12 oz. Embossed Drinking Glass, Green',
    },
    "DF0716": {
        "upc": "6191009197164",
        "description": '6"L x 8"H Bone Photo Frame (Holds 4" x 6" Photo)',
    },
    "DF4987": {"upc": "4191009436263", "description": '6-1/4"L Stoneware Jug'},
    "DF5599": {
        "upc": "0191009460954",
        "description": '16" Round Cotton Pillow w Pleats',
    },
    "DF6360": {
        "upc": "0191009487548",
        "description": 'S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer',
    },
    "DF6419A": {
        "upc": "0191009488132",
        "description": '17"Sq Cotton Printed Pillow w Ditsy Floral Pattern, 4 Styles',
    },
    "DF6642": {"upc": "0191009514312", "description": '12-1/4"H Stoneware Vase'},
    "DF9887A": {
        "upc": "0191009675723",
        "description": '6" Rnd Hand-Painted Stoneware Plate w Image, Multi, 4 Styles',
    },
    "DG1278": {
        "upc": "0191009786054",
        "description": '6-1/2"L x 8-1/2"H Resin Striped Photo Frame',
    },
}

print("=== VALIDATING CREATIVE COOP MAPPINGS ===")

# Get our current mappings
_, current_mappings = process_creative_coop_with_improved_mapping()

print("\n=== COMPARISON ===")
for product_code, expected in expected_mapping.items():
    current = current_mappings.get(product_code, {})

    print(f"\n{product_code}:")
    print(f"  Expected UPC: {expected['upc']}")
    print(f"  Current UPC:  {current.get('upc', 'MISSING')}")
    print(f"  Expected Desc: {expected['description']}")
    print(
        f"  Current Desc:  {current.get('description', 'MISSING')[:80]}{'...' if len(current.get('description', '')) > 80 else ''}"
    )

    upc_match = expected["upc"] == current.get("upc", "")
    desc_match = expected["description"] in current.get("description", "")

    print(f"  UPC Match: {'✓' if upc_match else '✗'}")
    print(f"  Desc Match: {'✓' if desc_match else '✗'}")

print(f"\n=== ANALYSIS ===")
print("The issue appears to be in the order of UPC->Description->ProductCode mapping.")
print("Let me analyze the raw text structure more carefully...")

# Load document to analyze raw text
with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
    doc_dict = json.load(f)

from google.cloud import documentai_v1 as documentai

document = documentai.Document(doc_dict)

# Look at the specific area where these products appear
text = document.text
for product_code in ["DA4315", "DF0716", "DF4987", "DF5599", "DF6360"]:
    pos = text.find(product_code)
    if pos != -1:
        start = max(0, pos - 100)
        end = min(len(text), pos + 100)
        context = text[start:end].replace("\n", " | ")
        print(f"\n{product_code} context: ...{context}...")

print(f"\n=== PATTERN ANALYSIS ===")
# The Creative Coop invoice appears to follow this pattern:
# UPC | Description | ProductCode | UPC | Description | ProductCode | ...
# But the description for ProductCode[N] comes BETWEEN ProductCode[N-1] and ProductCode[N]

# Let's try to manually map the first few to understand the pattern
sample_area = text[text.find("UPC") : text.find("DF7212A")]
print("Sample invoice area:")
print(sample_area.replace("\n", " | ")[:500] + "...")
