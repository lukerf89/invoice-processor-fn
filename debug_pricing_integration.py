#!/usr/bin/env python3
"""
Debug script to understand why pricing integration is failing in CS Error 2 processing
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    process_creative_coop_document,
    extract_creative_coop_quantity_improved,
    extract_wholesale_price,
    extract_creative_coop_product_mappings_corrected,
)


def load_cs_error2_document():
    """Load CS Error 2 Document AI output"""
    json_file = "test_invoices/CS003837319_Error 2_docai_output.json"

    with open(json_file, "r") as f:
        doc_data = json.load(f)

    # Create mock document object
    class MockDocument:
        def __init__(self, doc_data):
            self.text = doc_data.get("text", "")
            self.entities = []

            for entity_data in doc_data.get("entities", []):
                entity = type("Entity", (), {})()
                entity.type_ = entity_data.get("type", "")
                entity.mention_text = entity_data.get("mentionText", "")
                entity.confidence = entity_data.get("confidence", 0.0)
                entity.properties = []

                if "properties" in entity_data:
                    for prop_data in entity_data["properties"]:
                        prop = type("Property", (), {})()
                        prop.type_ = prop_data.get("type", "")
                        prop.mention_text = prop_data.get("mentionText", "")
                        prop.confidence = prop_data.get("confidence", 0.0)
                        entity.properties.append(prop)

                self.entities.append(entity)

    return MockDocument(doc_data)


def debug_single_product_processing():
    """Debug a single product to understand the pricing pipeline"""

    document = load_cs_error2_document()
    print("🔍 Debugging single product processing pipeline")
    print("=" * 60)

    # Test with XS9826A which should have qty=24, price=1.60
    test_product = "XS9826A"
    test_line = 'XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40'

    print(f"Test Product: {test_product}")
    print(f"Sample Line: {test_line}")
    print()

    # Step 1: Test multi-tier quantity extraction
    print("🔧 Testing multi-tier quantity extraction...")
    qty_result = extract_creative_coop_quantity_improved(test_line, test_product)
    print(f"Quantity Result: {qty_result}")
    print()

    # Step 2: Test wholesale price extraction
    print("🔧 Testing wholesale price extraction...")
    price_result = extract_wholesale_price(test_line)
    print(f"Price Result: {price_result}")
    print()

    # Step 3: Test product mapping
    print("🔧 Testing product mappings...")
    mappings = extract_creative_coop_product_mappings_corrected(document.text)
    if test_product in mappings:
        mapping = mappings[test_product]
        print(f"Mapping found: {mapping}")
    else:
        print("❌ No mapping found for test product")
    print()

    # Step 4: Test full processing pipeline
    print("🔧 Testing full Creative-Coop processing...")
    rows = process_creative_coop_document(document)
    print(f"Total rows produced: {len(rows)}")

    # Find our test product in results
    found_test_product = False
    for i, row in enumerate(rows):
        if len(row) >= 4 and test_product in str(row[3]):
            print(f"Found {test_product} in row {i}: {row}")
            found_test_product = True
            break

    if not found_test_product:
        print(f"❌ {test_product} not found in final output")

    print()
    print("=" * 60)


def debug_pricing_extraction_patterns():
    """Debug why price extraction is failing for tabular format"""

    print("🔍 Debugging price extraction patterns")
    print("=" * 60)

    # Test cases from CS Error 2 actual data
    test_cases = [
        {
            "product": "XS9826A",
            "line": 'XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40',
            "expected_price": 1.60,
        },
        {
            "product": "XS9482",
            "line": 'XS9482 191009714712 8.25"H Wood Shoe Ornament 12 0 0 12 each 3.50 2.80 33.60',
            "expected_price": 2.80,
        },
        {
            "product": "XS8185",
            "line": 'XS8185 191009721666 20"Lx12"H Cotton Lumbar Pillow 16 0 0 16 each 15.00 12.00 192.00',
            "expected_price": 12.00,
        },
    ]

    for test in test_cases:
        print(f"Testing: {test['product']}")
        print(f"Line: {test['line']}")

        extracted_price = extract_wholesale_price(test["line"])
        print(f"Extracted Price: {extracted_price}")
        print(f"Expected Price: {test['expected_price']}")

        if extracted_price == test["expected_price"]:
            print("✅ CORRECT")
        else:
            print("❌ INCORRECT")

            # Debug the price pattern matching
            import re

            price_pattern = r"\b(\d+\.\d{2})\b"
            prices = re.findall(price_pattern, test["line"])
            print(f"All prices found: {prices}")

        print("-" * 40)


def debug_entity_processing():
    """Debug how Document AI entities are processed"""

    document = load_cs_error2_document()
    print("🔍 Debugging Document AI entity processing")
    print("=" * 60)

    line_item_entities = [e for e in document.entities if e.type_ == "line_item"]
    print(f"Found {len(line_item_entities)} line_item entities")

    # Look at first few entities
    for i, entity in enumerate(line_item_entities[:3]):
        print(f"\nEntity {i+1}:")
        print(f"Text: {entity.mention_text[:200]}...")
        print(f"Length: {len(entity.mention_text)}")

        # Test if our products are in this entity
        test_products = ["XS9826A", "XS9482", "XS8185"]
        for product in test_products:
            if product in entity.mention_text:
                print(f"  Contains {product}: YES")

                # Test quantity extraction on this entity
                qty = extract_creative_coop_quantity_improved(
                    entity.mention_text, product
                )
                print(f"  Extracted qty for {product}: {qty}")

                # Test price extraction
                price = extract_wholesale_price(entity.mention_text)
                print(f"  Extracted price for {product}: {price}")
            else:
                print(f"  Contains {product}: NO")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("🐛 CS Error 2 Pricing Integration Debug")
    print("=" * 70)

    debug_single_product_processing()
    debug_pricing_extraction_patterns()
    debug_entity_processing()

    print("\n✅ Debug analysis complete")
