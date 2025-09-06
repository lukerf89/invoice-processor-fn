#!/usr/bin/env python3
"""
Simple Phase 02 Integration Test

Tests the basic functionality of Phase 02 enhanced functions.
"""

import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


def load_test_document():
    """Load CS003837319_Error 2 test document"""
    test_file_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "test_invoices",
        "CS003837319_Error 2_docai_output.json",
    )

    with open(test_file_path, "r", encoding="utf-8") as f:
        document_data = json.load(f)

    # Create mock document object
    class MockDocument:
        def __init__(self, data):
            self.text = data.get("text", "")
            self.pages = data.get("pages", [])

            # Convert dict entities to mock entity objects
            entities_list = []
            for entity_data in data.get("entities", []):
                if isinstance(entity_data, dict):
                    mock_entity = type(
                        "MockEntity",
                        (),
                        {
                            "type_": entity_data.get("type_", "unknown"),
                            "mention_text": entity_data.get("mention_text", ""),
                        },
                    )()
                    entities_list.append(mock_entity)
                else:
                    entities_list.append(entity_data)

            self.entities = entities_list

    return MockDocument(document_data)


def test_phase_02_enhanced_function():
    """Test Phase 02 enhanced function basic functionality"""
    print("🧪 Testing Phase 02 enhanced function...")

    # Load test document
    document = load_test_document()
    print(f"✅ Loaded document with {len(document.text)} characters")

    # Test Phase 02 enhanced function
    results = main.process_creative_coop_document_phase_02_enhanced(document)
    print(f"✅ Processed {len(results)} line items")

    # Basic validation
    if len(results) > 0:
        sample_item = results[0]
        print(f"📋 Sample item: {sample_item}")

        # Check for required fields
        required_fields = ["product_code", "price", "quantity", "description"]
        has_fields = [field for field in required_fields if field in sample_item]
        print(f"✅ Sample item has fields: {has_fields}")

    return results


def test_success_criteria_validation():
    """Test success criteria validation function"""
    print("\n🧪 Testing success criteria validation...")

    # Create mock results for testing
    mock_results = [
        {
            "product_code": "XS0001A",
            "price": "$12.99",
            "quantity": 8,
            "description": "Enhanced product description with UPC integration",
        },
        {
            "product_code": "XS0002A",
            "price": "$24.50",
            "quantity": 12,
            "description": "Complete product description without placeholders",
        },
    ]

    # Test validation function
    validation_result = main.validate_phase_02_success_criteria(mock_results)
    print(f"✅ Validation result: {validation_result}")

    return validation_result


def main_test():
    """Main test runner"""
    print("🚀 Starting Simple Phase 02 Integration Test")
    print("=" * 60)

    try:
        # Test enhanced function
        results = test_phase_02_enhanced_function()

        # Test validation
        validation = test_success_criteria_validation()

        print("\n" + "=" * 60)
        print("🎯 Test Summary:")
        print(f"   Results processed: {len(results)}")
        print(f"   Validation success: {validation.get('success', False)}")

        if len(results) > 0:
            print("✅ Phase 02 enhanced function is working!")
        else:
            print("⚠️  Phase 02 enhanced function returned empty results")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)
