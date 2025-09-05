#!/usr/bin/env python3
"""
Task 08: Integration test for CS003837319_Error 2.PDF processing
Tests the integration of multi-tier price extraction with Creative-Coop processing
"""

import csv
import json
import time

from main import detect_vendor_type, process_creative_coop_document


def load_cs_error2_document():
    """Load CS003837319_Error 2.PDF Document AI output for testing"""
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


def test_current_cs_error2_processing():
    """Test current CS Error 2 processing before integration"""
    print("🧪 Testing CS003837319_Error 2.PDF Current Processing")
    print("=" * 60)

    # Load document
    document = load_cs_error2_document()
    print(f"📄 Document loaded: {len(document.entities)} entities")

    # Test vendor detection
    vendor_type = detect_vendor_type(document.text)
    print(f"🏢 Vendor detection: {vendor_type}")

    # Test complete processing
    start_time = time.time()
    rows = process_creative_coop_document(document)
    end_time = time.time()

    processing_time = end_time - start_time
    print(f"⚡ Processing time: {processing_time:.2f} seconds")
    print(f"📊 Extracted rows: {len(rows)}")

    # Save current results
    output_file = "test_invoices/CS003837319_Error_2_current_processing.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"]
        )
        for row in rows:
            writer.writerow(row)
    print(f"💾 Results saved to: {output_file}")

    # Analyze results
    if len(rows) == 0:
        print(
            "❌ Current processing produces 0 rows - need to integrate new price extraction"
        )
        return False
    elif len(rows) < 20:
        print(
            f"⚠️  Current processing produces {len(rows)} rows - need improvement to reach 20+"
        )
        return False
    else:
        print(f"✅ Current processing produces {len(rows)} rows - meeting target!")
        return True


if __name__ == "__main__":
    test_current_cs_error2_processing()
