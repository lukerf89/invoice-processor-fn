# Test file: test_scripts/test_creative_coop_product_scope_expansion.py
import json
import re
from unittest.mock import Mock

import pytest

from main import (
    extract_creative_coop_product_mappings_corrected,
    process_creative_coop_document,
)


def test_current_processing_includes_placeholder_data():
    """Test that current implementation generates placeholder '$1.60, 24' entries - RED test"""
    # Load CS003837319_Error Document AI output
    with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
        doc_data = json.load(f)

    # Create mock document
    mock_document = Mock()
    mock_document.text = doc_data.get("text", "")
    mock_document.entities = []

    for entity_data in doc_data.get("entities", []):
        entity = Mock()
        entity.type_ = entity_data.get("type", "")
        entity.mention_text = entity_data.get("mentionText", "")
        mock_document.entities.append(entity)

    # Process with current implementation
    results = process_creative_coop_document(mock_document)

    # Count placeholder entries
    placeholder_count = 0
    price_patterns = {}
    quantity_patterns = {}

    for row in results:
        if len(row) >= 6:
            price = str(row[4]) if len(row) > 4 else ""
            quantity = str(row[5]) if len(row) > 5 else ""

            price_patterns[price] = price_patterns.get(price, 0) + 1
            quantity_patterns[quantity] = quantity_patterns.get(quantity, 0) + 1

            # Check for placeholder patterns
            if ("$1.60" in price or "$$1.60" in price) and quantity == "24":
                placeholder_count += 1

    print(f"Total results: {len(results)}")
    print(f"Placeholder entries ($*1.60, 24): {placeholder_count}")
    print(
        f"Top price patterns: {sorted(price_patterns.items(), key=lambda x: x[1], reverse=True)[:3]}"
    )

    # RED: Should find placeholder entries in current output
    assert (
        placeholder_count > 50
    ), f"Expected 50+ placeholder entries, found: {placeholder_count}"
    print(f"✅ RED: Found {placeholder_count} placeholder entries as expected")


def test_traditional_pattern_entries_exist():
    """Test that current output contains 'Traditional pattern' log entries - RED test"""
    # Process current CS003837319_Error
    with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
        doc_data = json.load(f)

    mock_document = Mock()
    mock_document.text = doc_data.get("text", "")
    mock_document.entities = []

    # Process the document to check for traditional pattern evidence
    results = process_creative_coop_document(mock_document)
    captured_output = None

    # Check for traditional pattern mentions in logs or result structure
    traditional_pattern_found = False
    if captured_output:
        output_text = captured_output.getvalue()
        if "Traditional pattern" in output_text:
            traditional_pattern_found = True
            print("✅ RED: Found 'Traditional pattern' in processing logs")

    # Also check if results show evidence of placeholder generation
    # (Many items with same price/quantity suggest algorithmic fallback)
    same_price_qty_count = 0
    for row in results:
        if len(row) >= 6:
            price = str(row[4])
            quantity = str(row[5])
            if ("$1.60" in price or "$$1.60" in price) and quantity == "24":
                same_price_qty_count += 1

    if same_price_qty_count > 50:
        traditional_pattern_found = True
        print(
            f"✅ RED: Found {same_price_qty_count} items with same price/quantity pattern"
        )

    # RED: Should find evidence of traditional pattern processing
    assert (
        traditional_pattern_found
    ), "Expected evidence of 'Traditional pattern' processing"


def test_product_code_extraction_finds_all_codes():
    """Test that product code extraction finds all 130+ codes in document"""
    with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
        doc_data = json.load(f)

    document_text = doc_data.get("text", "")

    # Extract all Creative-Coop product codes using current patterns
    # All known Creative-Coop patterns
    patterns = [
        r"\b(XS\d+[A-Z]?)\b",  # XS codes
        r"\b(CF\d+[A-Z]?)\b",  # CF codes
        r"\b(CD\d+[A-Z]?)\b",  # CD codes
        r"\b(HX\d+[A-Z]?)\b",  # HX codes
        r"\b(XT\d+[A-Z]?)\b",  # XT codes
    ]

    all_codes = set()
    for pattern in patterns:
        codes = re.findall(pattern, document_text)
        all_codes.update(codes)

    print(f"Document contains {len(all_codes)} unique product codes")

    # RED: Should find 120+ codes (current processing scope should handle this)
    assert (
        len(all_codes) >= 120
    ), f"Expected 120+ product codes, found: {len(all_codes)}"
    print(f"✅ RED: Document has sufficient product codes ({len(all_codes)})")


def test_algorithmic_vs_hardcoded_approach():
    """Test current approach uses algorithmic extraction (no hardcoded values)"""
    # This is more of a code review test - examine current mappings function
    import inspect

    source = inspect.getsource(extract_creative_coop_product_mappings_corrected)

    # Should not contain hardcoded product-specific values
    hardcoded_indicators = ["XS9826A", "1.60", "24"]

    found_hardcoded = []
    for indicator in hardcoded_indicators:
        if indicator in source:
            found_hardcoded.append(indicator)

    # Should pass - current implementation should be algorithmic
    assert len(found_hardcoded) == 0, f"Found hardcoded values: {found_hardcoded}"
    print("✅ RED: Current implementation is algorithmic (no hardcoded values)")


def test_unique_data_quality_issues():
    """Test that current implementation has data quality issues with duplicated patterns - RED test"""
    with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
        doc_data = json.load(f)

    mock_document = Mock()
    mock_document.text = doc_data.get("text", "")
    mock_document.entities = []

    for entity_data in doc_data.get("entities", []):
        entity = Mock()
        entity.type_ = entity_data.get("type", "")
        entity.mention_text = entity_data.get("mentionText", "")
        mock_document.entities.append(entity)

    results = process_creative_coop_document(mock_document)

    # Analyze data quality patterns
    price_quantity_pairs = {}
    for row in results:
        if len(row) >= 6:
            price = str(row[4])
            quantity = str(row[5])
            pair = (price, quantity)
            price_quantity_pairs[pair] = price_quantity_pairs.get(pair, 0) + 1

    # Find most common price/quantity combination
    most_common_pair = max(price_quantity_pairs.items(), key=lambda x: x[1])
    most_common_count = most_common_pair[1]

    print(
        f"Most common price/quantity pair: {most_common_pair[0]} ({most_common_count} occurrences)"
    )

    # RED: Should find significant duplication indicating placeholder data
    assert (
        most_common_count >= 50
    ), f"Expected 50+ duplicate entries, found: {most_common_count}"
    print(
        f"✅ RED: Found significant duplication ({most_common_count} identical entries)"
    )


def test_processing_scope_covers_all_product_types():
    """Test that processing covers all product code types (XS, CF, CD, HX, XT)"""
    with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
        doc_data = json.load(f)

    mock_document = Mock()
    mock_document.text = doc_data.get("text", "")
    mock_document.entities = []

    for entity_data in doc_data.get("entities", []):
        entity = Mock()
        entity.type_ = entity_data.get("type", "")
        entity.mention_text = entity_data.get("mentionText", "")
        mock_document.entities.append(entity)

    results = process_creative_coop_document(mock_document)

    # Extract product prefixes from results
    prefixes_found = set()
    for row in results:
        if len(row) >= 4:
            description = str(row[3])
            # Extract product code from description
            match = re.search(r"([A-Z]{2})\d+[A-Z]?", description)
            if match:
                prefixes_found.add(match.group(1))

    print(f"Product prefixes found in results: {sorted(prefixes_found)}")
    expected_prefixes = {"XS", "CF", "CD", "HX", "XT"}

    # Should find most/all expected prefixes
    found_count = len(prefixes_found.intersection(expected_prefixes))
    print(f"Found {found_count} of {len(expected_prefixes)} expected prefixes")

    # This should pass - current implementation should handle variety
    assert found_count >= 4, f"Expected 4+ prefix types, found: {found_count}"
    print("✅ RED: Processing covers diverse product types")


if __name__ == "__main__":
    # Run RED tests to demonstrate current limitations
    print("=== RED TESTS: Demonstrating Current Product Processing Limitations ===")

    print("\n1. Testing placeholder data generation...")
    try:
        test_current_processing_includes_placeholder_data()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n2. Testing traditional pattern processing...")
    try:
        test_traditional_pattern_entries_exist()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n3. Testing product code coverage...")
    try:
        test_product_code_extraction_finds_all_codes()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n4. Testing algorithmic approach...")
    try:
        test_algorithmic_vs_hardcoded_approach()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n5. Testing data quality issues...")
    try:
        test_unique_data_quality_issues()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n6. Testing product type coverage...")
    try:
        test_processing_scope_covers_all_product_types()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n=== RED TESTS COMPLETE ===")
    print("These tests demonstrate the current placeholder data generation issue")
