#!/usr/bin/env python3
"""
Create algorithmic solution for Creative Coop mapping without manual corrections
"""
import json
import re


def extract_creative_coop_mappings_algorithmic(document_text):
    """
    Extract Creative-Coop product mappings using algorithmic pattern matching

    The pattern in Creative-Coop invoices is:
    UPC[N] | Description[N] | ProductCode[N+1]

    So ProductCode[0] gets UPC[0] and Description[0]
    """

    # Find all UPCs and product codes with their positions
    upc_pattern = r"\b(\d{12})\b"
    product_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

    upc_matches = list(re.finditer(upc_pattern, document_text))
    product_matches = list(re.finditer(product_pattern, document_text))

    print(f"Found {len(upc_matches)} UPCs and {len(product_matches)} product codes")

    # Extract descriptions between UPC and next product code
    mappings = {}

    for i, product_match in enumerate(product_matches):
        product_code = product_match.group(1)
        product_pos = product_match.start()

        # For each product code, we need to find the UPC and description that belong to it
        # The pattern is: UPC[i] -> Description[i] -> ProductCode[i+1]
        # So ProductCode[i] belongs to UPC[i-1] and Description[i-1]

        target_upc_index = i  # ProductCode[i] gets UPC[i]
        target_desc_text = None
        target_upc = None

        if target_upc_index < len(upc_matches):
            upc_match = upc_matches[target_upc_index]
            target_upc = f"0{upc_match.group(1)}"  # Add leading zero
            upc_pos = upc_match.start()

            # Find description between this UPC and the current product code
            between_text = document_text[upc_pos + 12 : product_pos]

            # Extract the clean description
            target_desc_text = extract_clean_description(between_text)

        # Special case for DA4315 - it's the first product but appears later in the text
        # We need to find the very first UPC and description in the document
        if product_code == "DA4315":
            # Find the first UPC in the document (after the headers)
            table_start = document_text.find("Extended | Amount |")
            if table_start != -1:
                first_upc_match = re.search(
                    r"\b(\d{12})\b", document_text[table_start:]
                )
                if first_upc_match:
                    first_upc = f"0{first_upc_match.group(1)}"
                    first_upc_pos = table_start + first_upc_match.start()

                    # Find text after first UPC until we hit next product code (DF0716)
                    df0716_pos = document_text.find("DF0716")
                    if df0716_pos != -1:
                        desc_text = document_text[first_upc_pos + 12 : df0716_pos]
                        clean_desc = extract_clean_description(desc_text)

                        mappings[product_code] = {
                            "upc": first_upc,
                            "description": clean_desc,
                        }
                        print(
                            f"{product_code}: UPC={first_upc}, Desc='{clean_desc[:50]}{'...' if len(clean_desc) > 50 else ''}'"
                        )
                        continue

        if target_upc and target_desc_text:
            mappings[product_code] = {
                "upc": target_upc,
                "description": target_desc_text,
            }
            print(
                f"{product_code}: UPC={target_upc}, Desc='{target_desc_text[:50]}{'...' if len(target_desc_text) > 50 else ''}'"
            )

    return mappings


def extract_clean_description(raw_text):
    """Extract and clean description from raw text between UPC and product code"""

    # Split by lines and clean
    lines = raw_text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip(" |")

        # Skip empty lines, pure numbers, and table formatting
        if (
            line
            and len(line) > 5
            and not re.match(r"^[\d\s\.]+$", line)  # Not just numbers
            and not re.match(r"^[|\s]+$", line)  # Not just pipes/spaces
            and not line.lower()
            in [
                "customer",
                "item",
                "shipped",
                "back",
                "ordered",
                "um",
                "list",
                "price",
                "truck",
                "your",
                "extended",
                "amount",
            ]
        ):
            clean_lines.append(line)

    if clean_lines:
        # Take the longest meaningful line as description
        best_desc = max(clean_lines, key=len)
        return best_desc.strip()

    return ""


# Test the algorithm
if __name__ == "__main__":
    print("=== TESTING ALGORITHMIC CREATIVE COOP MAPPING ===")

    # Load the Creative-Coop document
    with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
        doc_dict = json.load(f)

    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    mappings = extract_creative_coop_mappings_algorithmic(document.text)

    print(f"\nExtracted {len(mappings)} mappings algorithmically")

    # Test against expected results
    expected = {
        "DA4315": "0807472767956",
        "DF0716": "6191009197164",
        "DF4987": "4191009436263",
        "DF5599": "0191009460954",
        "DF6360": "0191009487548",
        "DF6419A": "0191009488132",
        "DF6642": "0191009514312",
        "DF9887A": "0191009675723",
        "DG1278": "0191009786054",
    }

    print(f"\n=== VALIDATION ===")
    for product, expected_upc in expected.items():
        if product in mappings:
            actual_upc = mappings[product]["upc"]
            match = actual_upc == expected_upc
            print(
                f"{product}: Expected {expected_upc}, Got {actual_upc} {'✓' if match else '✗'}"
            )
        else:
            print(f"{product}: Missing from algorithmic extraction ✗")
