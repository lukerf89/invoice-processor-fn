# Test file: test_scripts/test_creative_coop_invoice_number_extraction.py
import json
import re
from unittest.mock import Mock

import pytest

from main import process_creative_coop_document


def test_order_no_pattern_fails_with_current_extraction():
    """Test that current extraction fails to find ORDER NO: CS003837319 - RED test"""
    # Simulate Document AI document with ORDER NO format
    mock_document = Mock()
    mock_document.text = """
    Creative Coop Invoice Processing
    ORDER NO: CS003837319
    Date: 09/05/2025
    Product listings...
    """
    mock_document.entities = [
        Mock(type_="invoice_id", mention_text=""),  # Empty - should fail
        Mock(type_="invoice_date", mention_text="09/05/2025"),
    ]

    # Current pattern from main.py line 2852-2856
    current_pattern = r"Invoice\s*#?\s*:\s*([A-Z0-9]+)"
    match = re.search(current_pattern, mock_document.text, re.IGNORECASE)

    # RED: This should fail with current pattern
    assert (
        match is None
    ), f"Current pattern should not match ORDER NO format, but found: {match}"


def test_extract_cs003837319_returns_empty_currently():
    """Test that CS003837319 invoice number extraction currently fails - RED test"""
    # Load actual CS003837319_Error Document AI output

    with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
        doc_data = json.load(f)

    # Create mock document from actual data
    mock_document = Mock()
    mock_document.text = doc_data.get("text", "")
    mock_document.entities = []

    # Add entities without invoice_id to simulate current failure
    for entity_data in doc_data.get("entities", []):
        entity = Mock()
        entity.type_ = entity_data.get("type", "")
        entity.mention_text = entity_data.get("mentionText", "")
        mock_document.entities.append(entity)

    # Process with current implementation
    results = process_creative_coop_document(mock_document)

    # RED: Should demonstrate current invoice number extraction failure
    # Check if any row contains empty invoice number
    has_empty_invoice = any(not row[1] for row in results if len(row) > 1)
    assert (
        has_empty_invoice
    ), "Current implementation should fail to extract CS003837319"


def test_invoice_hash_pattern_still_works():
    """Test that existing Invoice # pattern continues working"""
    mock_document = Mock()
    mock_document.text = "Invoice #: ABC123456"
    mock_document.entities = [Mock(type_="invoice_id", mention_text="")]

    current_pattern = r"Invoice\s*#?\s*:\s*([A-Z0-9]+)"
    match = re.search(current_pattern, mock_document.text, re.IGNORECASE)

    assert match is not None
    assert match.group(1) == "ABC123456"


def test_empty_document_handling():
    """Test handling of edge cases with missing text"""
    mock_document = Mock()
    mock_document.text = ""
    mock_document.entities = []

    results = process_creative_coop_document(mock_document)

    # Should handle gracefully without crashing
    assert isinstance(results, list)


# Additional RED tests for edge cases
def test_order_no_with_various_spacing_patterns():
    """Test that ORDER NO patterns with different spacing fail with current implementation"""
    test_cases = [
        "ORDER NO: CS003837319",
        "ORDER NO:CS003837319",
        "ORDER NO :CS003837319",
        "Order No: CS003837319",
        "Order Number: CS003837319",
    ]

    current_pattern = r"Invoice\s*#?\s*:\s*([A-Z0-9]+)"

    for test_text in test_cases:
        match = re.search(current_pattern, test_text, re.IGNORECASE)
        assert (
            match is None
        ), f"Current pattern should not match '{test_text}' but found: {match}"


def test_malformed_invoice_numbers_with_current_pattern():
    """Test edge cases with malformed invoice numbers"""
    mock_document = Mock()
    mock_document.text = "ORDER NO: "  # Empty invoice number
    mock_document.entities = [Mock(type_="invoice_id", mention_text="")]

    current_pattern = r"Invoice\s*#?\s*:\s*([A-Z0-9]+)"
    match = re.search(current_pattern, mock_document.text, re.IGNORECASE)

    # Should not match malformed patterns
    assert match is None, "Should not match empty invoice number"


if __name__ == "__main__":
    # Run specific RED tests to demonstrate current failures
    print("=== RED TESTS: Demonstrating Current Invoice Number Extraction Failures ===")

    print("\n1. Testing ORDER NO pattern with current implementation...")
    try:
        test_order_no_pattern_fails_with_current_extraction()
        print("✅ PASS: Current pattern correctly fails to match ORDER NO format")
    except AssertionError as e:
        print(f"❌ FAIL: {e}")

    print("\n2. Testing CS003837319 extraction with current implementation...")
    try:
        test_extract_cs003837319_returns_empty_currently()
        print("✅ PASS: Current implementation correctly fails to extract CS003837319")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n3. Verifying existing Invoice # pattern still works...")
    try:
        test_invoice_hash_pattern_still_works()
        print("✅ PASS: Existing Invoice # pattern continues to work")
    except AssertionError as e:
        print(f"❌ FAIL: {e}")

    print("\n4. Testing various ORDER NO spacing patterns...")
    try:
        test_order_no_with_various_spacing_patterns()
        print(
            "✅ PASS: All ORDER NO patterns correctly fail with current implementation"
        )
    except AssertionError as e:
        print(f"❌ FAIL: {e}")

    print("\n=== RED TESTS COMPLETE ===")
    print("These failing tests demonstrate the need for ORDER NO: pattern support")
