#!/usr/bin/env python3
"""
Improved algorithmic solution for Creative Coop mapping
"""
import json
import re


def extract_creative_coop_mappings_improved(document_text):
    """
    Improved Creative-Coop product mappings using the actual document structure
    """

    # Focus on the main invoice table area
    table_start = document_text.find("Extended | Amount |")
    if table_start == -1:
        table_start = 0

    # Get a substantial portion that includes all products
    table_section = document_text[table_start : table_start + 3000]

    print(f"Analyzing table section of {len(table_section)} characters")

    # Find all UPCs and product codes with positions in the table section
    upc_pattern = r"\b(\d{12})\b"
    product_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

    upc_matches = list(re.finditer(upc_pattern, table_section))
    product_matches = list(re.finditer(product_pattern, table_section))

    print(f"In table section: {len(upc_matches)} UPCs, {len(product_matches)} products")

    # The key insight: let's extract sequences and match them properly
    mappings = {}

    # Method: For each product, find the closest PRECEDING UPC and description
    for product_match in product_matches:
        product_code = product_match.group(1)
        product_pos = product_match.start()

        # Find the closest UPC that comes BEFORE this product code
        closest_upc = None
        closest_upc_pos = -1
        min_distance = float("inf")

        for upc_match in upc_matches:
            upc_pos = upc_match.start()
            if upc_pos < product_pos:  # UPC comes before product
                distance = product_pos - upc_pos
                if distance < min_distance:
                    min_distance = distance
                    closest_upc = upc_match.group(1)
                    closest_upc_pos = upc_pos

        if closest_upc and closest_upc_pos != -1:
            # Extract description between UPC and product code
            between_text = table_section[closest_upc_pos + 12 : product_pos]
            description = extract_description_from_between_text(between_text)

            if description:
                # Add leading zero to UPC if needed
                formatted_upc = (
                    f"0{closest_upc}" if len(closest_upc) == 12 else closest_upc
                )

                mappings[product_code] = {
                    "upc": formatted_upc,
                    "description": description,
                }

                print(
                    f"{product_code}: UPC={formatted_upc}, Desc='{description[:50]}{'...' if len(description) > 50 else ''}'"
                )

    return mappings


def extract_description_from_between_text(text):
    """Extract the best description from text between UPC and product code"""

    # Clean the text
    text = text.strip()

    # Split by common delimiters
    lines = re.split(r"[\n|]+", text)

    candidates = []
    for line in lines:
        line = line.strip()

        # Good description characteristics:
        # - Contains quotes (dimensions) or descriptive words
        # - Not just numbers or table formatting
        # - Reasonable length
        if (
            line
            and len(line) > 10
            and not re.match(r"^[\d\s\.\-]+$", line)  # Not just numbers
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
            and (
                '"' in line
                or any(
                    word in line.lower()
                    for word in [
                        "cotton",
                        "stoneware",
                        "frame",
                        "pillow",
                        "glass",
                        "wood",
                        "resin",
                    ]
                )
            )
        ):

            candidates.append(line)

    if candidates:
        # Return the longest candidate as it's likely the most complete description
        return max(candidates, key=len)

    # Fallback: return the first non-empty, non-numeric line
    for line in lines:
        line = line.strip()
        if line and len(line) > 5 and not re.match(r"^[\d\s\.\-]+$", line):
            return line

    return ""


# Test the improved algorithm
if __name__ == "__main__":
    print("=== TESTING IMPROVED ALGORITHMIC CREATIVE COOP MAPPING ===")

    # Load the Creative-Coop document
    with open("test_invoices/Creative-Coop_CI004848705_docai_output.json", "r") as f:
        doc_dict = json.load(f)

    from google.cloud import documentai_v1 as documentai

    document = documentai.Document(doc_dict)

    mappings = extract_creative_coop_mappings_improved(document.text)

    print(f"\nExtracted {len(mappings)} mappings algorithmically")

    # Test against expected results
    expected_upcs = {
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

    expected_descriptions = {
        "DA4315": '3-1/4" Rnd x 4"H 12 oz. Embossed Drinking Glass, Green',
        "DF0716": '6"L x 8"H Bone Photo Frame (Holds 4" x 6" Photo)',
        "DF4987": '6-1/4"L Stoneware Jug',
        "DF5599": '16" Round Cotton Pillow w Pleats',
        "DF6360": 'S/3 4-1/4"H Stoneware Sugar Pot w/ Lid, Spoon & Creamer',
        "DF6419A": '17"Sq Cotton Printed Pillow w Ditsy Floral Pattern, 4 Styles',
        "DF6642": '12-1/4"H Stoneware Vase',
        "DF9887A": '6" Rnd Hand-Painted Stoneware Plate w Image, Multi, 4 Styles',
        "DG1278": '6-1/2"L x 8-1/2"H Resin Striped Photo Frame',
    }

    print(f"\n=== VALIDATION ===")
    correct_upcs = 0
    correct_descriptions = 0

    for product in expected_upcs.keys():
        if product in mappings:
            actual_upc = mappings[product]["upc"]
            actual_desc = mappings[product]["description"]
            expected_upc = expected_upcs[product]
            expected_desc = expected_descriptions[product]

            upc_match = actual_upc == expected_upc
            desc_match = expected_desc.lower() in actual_desc.lower()

            if upc_match:
                correct_upcs += 1
            if desc_match:
                correct_descriptions += 1

            print(f"{product}:")
            print(
                f"  UPC: Expected {expected_upc}, Got {actual_upc} {'✓' if upc_match else '✗'}"
            )
            print(f"  Desc: {'✓' if desc_match else '✗'} {actual_desc[:60]}...")
        else:
            print(f"{product}: Missing from algorithmic extraction ✗")

    print(
        f"\nResults: {correct_upcs}/{len(expected_upcs)} UPCs correct, {correct_descriptions}/{len(expected_descriptions)} descriptions correct"
    )
