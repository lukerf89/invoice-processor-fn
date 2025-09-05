#!/usr/bin/env python3
"""
Debug script to test CS003837319_Error 2.PDF processing and check column alignment
"""
import csv
import json
import os
import sys

# Add the parent directory to sys.path to import main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    detect_vendor_type,
    extract_line_items,
    extract_line_items_from_entities,
    extract_line_items_from_text,
    format_date,
    process_creative_coop_document,
)


def test_cs_error2_processing():
    """Test the CS003837319_Error 2.PDF processing and analyze column structure"""

    # Load the Document AI JSON for CS003837319_Error 2.PDF
    json_file = "test_invoices/CS003837319_Error 2_docai_output.json"

    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        print(
            "Please run: python document_ai_explorer.py 'test_invoices/CS003837319_Error 2.PDF' --save-json"
        )
        return

    print(f"📄 Loading Document AI output from: {json_file}")

    with open(json_file, "r") as f:
        doc_data = json.load(f)

    # Create a mock document object
    class MockDocument:
        def __init__(self, doc_data):
            self.text = doc_data.get("text", "")
            self.entities = []

            # Parse entities
            for entity_data in doc_data.get("entities", []):
                entity = type("Entity", (), {})()
                entity.type_ = entity_data.get("type", "")
                entity.mention_text = entity_data.get("mentionText", "")
                entity.confidence = entity_data.get("confidence", 0.0)

                # Add properties if they exist
                entity.properties = []
                if "properties" in entity_data:
                    for prop_data in entity_data["properties"]:
                        prop = type("Property", (), {})()
                        prop.type_ = prop_data.get("type", "")
                        prop.mention_text = prop_data.get("mentionText", "")
                        prop.confidence = prop_data.get("confidence", 0.0)
                        entity.properties.append(prop)

                self.entities.append(entity)

    document = MockDocument(doc_data)

    print(
        f"📊 Document loaded: {len(document.entities)} entities, text length: {len(document.text)}"
    )

    # Test vendor detection
    vendor_type = detect_vendor_type(document.text)
    print(f"🏢 Detected vendor type: {vendor_type}")

    # Test Creative-Coop processing specifically
    if vendor_type == "Creative-Coop":
        print("\n🔍 Testing Creative-Coop specific processing...")
        rows = process_creative_coop_document(document)
        print(f"✅ Creative-Coop processing returned: {len(rows)} rows")

        # Analyze column structure
        print("\n📋 Column Structure Analysis:")
        if rows:
            first_row = rows[0]
            print(f"   Number of columns: {len(first_row)}")
            print(f"   Column structure: {first_row}")
            print(
                f"   Column headers should be: [Invoice Date, Vendor, Invoice#, Description, Price, Qty]"
            )

            # Check if this matches expected B:G structure
            expected_columns = 6
            if len(first_row) == expected_columns:
                print("   ✅ Correct number of columns (6) for B:G range")
            else:
                print(
                    f"   ❌ Wrong number of columns. Expected: {expected_columns}, Got: {len(first_row)}"
                )

        # Save results to CSV for analysis
        output_file = "test_invoices/CS003837319_Error_2_debug_output.csv"
        print(f"\n💾 Saving results to: {output_file}")

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write header (this represents what would go in columns B:G)
            writer.writerow(
                ["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"]
            )

            # Write data rows
            for row in rows:
                writer.writerow(row)

        print(f"✅ Saved {len(rows)} rows to {output_file}")

        # Show first few rows for inspection
        print("\n🔍 First 3 rows for inspection:")
        for i, row in enumerate(rows[:3]):
            print(f"   Row {i+1}: {row}")

    else:
        print(f"❌ Expected Creative-Coop vendor type, got: {vendor_type}")
        print("Testing fallback processing methods...")

        # Test fallback methods
        entities_dict = {e.type_: e.mention_text for e in document.entities}

        # Try entity extraction
        entity_rows = extract_line_items_from_entities(
            document.entities, document.text, "", "", ""
        )
        print(f"🔄 Entity extraction returned: {len(entity_rows)} rows")

        # Try table extraction
        table_rows = extract_line_items(document.text, "", "", "")
        print(f"🔄 Table extraction returned: {len(table_rows)} rows")

        # Try text extraction
        text_rows = extract_line_items_from_text(document.text, "", "", "")
        print(f"🔄 Text extraction returned: {len(text_rows)} rows")


if __name__ == "__main__":
    print("🧪 CS003837319_Error 2.PDF Column Alignment Debug Test")
    print("=" * 60)
    test_cs_error2_processing()
    print("=" * 60)
    print("✅ Debug test completed!")
