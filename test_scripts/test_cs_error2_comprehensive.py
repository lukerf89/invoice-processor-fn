#!/usr/bin/env python3
"""
Task 08 - RED Phase: Failing tests for complete CS003837319_Error 2.PDF processing
Creative-Coop end-to-end validation with expected 20+ output rows

This implements TDD RED phase with comprehensive failing tests for the complete
CS003837319_Error 2.PDF processing pipeline, validating data quality, accuracy, and format.
"""

import pytest
import json
import csv
import time
from unittest.mock import Mock


# Expected data from manual PDF analysis of CS003837319_Error 2.PDF
EXPECTED_CS_ERROR2_PRODUCTS = [
    {
        "code": "XS9826A",
        "qty": 24,
        "price": 1.60,
        "upc": "191009727774",
        "desc_contains": "Metal Ballerina",
    },
    {
        "code": "XS9649A",
        "qty": 24,
        "price": 2.80,
        "upc": "191009725688",
        "desc_contains": "Paper Mache",
    },
    {
        "code": "XS9482",
        "qty": 12,
        "price": 2.80,
        "upc": "191009714712",
        "desc_contains": "Wood Shoe",
    },
    {
        "code": "XS9840A",
        "qty": 24,
        "price": 2.80,
        "upc": "191009727910",
        "desc_contains": "Metal",
    },
    {
        "code": "XS8185",
        "qty": 16,
        "price": 12.00,
        "upc": "191009721666",
        "desc_contains": "Cotton Lumbar Pillow",
    },
    {
        "code": "XS9357",
        "qty": 12,
        "price": 4.00,
        "upc": "191009713470",
        "desc_contains": "Metal Bow Tree",
    },
    {
        "code": "XS7529",
        "qty": 18,
        "price": 8.00,
        "upc": "191009690856",
        "desc_contains": "Metal Leaves",
    },
    {
        "code": "XS7653A",
        "qty": 24,
        "price": 4.00,
        "upc": "191009689553",
        "desc_contains": "Stoneware",
    },
    {
        "code": "XS8109",
        "qty": 12,
        "price": 12.80,
        "upc": "191009720799",
        "desc_contains": "Wool Felt",
    },
    {
        "code": "XS8379A",
        "qty": 24,
        "price": 4.00,
        "upc": "191009705277",
        "desc_contains": "Stoneware Mug",
    },
    {
        "code": "XS5747A",
        "qty": 24,
        "price": 3.20,
        "upc": "191009635727",
        "desc_contains": "Cotton",
    },
    {
        "code": "XS8838",
        "qty": 6,
        "price": 5.60,
        "upc": "191009709855",
        "desc_contains": "Glass Canister",
    },
    {
        "code": "XS8837",
        "qty": 6,
        "price": 6.40,
        "upc": "191009709848",
        "desc_contains": "Glass Canister",
    },
    {
        "code": "XS3350",
        "qty": 12,
        "price": 8.00,
        "upc": "191009571414",
        "desc_contains": "Cotton Tea",
    },
    {
        "code": "XS3844",
        "qty": 4,
        "price": 18.80,
        "upc": "191009582816",
        "desc_contains": "Acrylic",
    },
    {
        "code": "XS8714",
        "qty": 4,
        "price": 18.80,
        "upc": "191009722922",
        "desc_contains": "Acrylic Throw",
    },
    {
        "code": "XS5692A",
        "qty": 24,
        "price": 3.20,
        "upc": "191009636038",
        "desc_contains": "Stoneware Mug",
    },
    {
        "code": "XS9082",
        "qty": 12,
        "price": 4.00,
        "upc": "191009723929",
        "desc_contains": "Cotton PotHolder",
    },
    {
        "code": "XS7793A",
        "qty": 24,
        "price": 3.00,
        "upc": "191009717706",
        "desc_contains": "Paper",
    },
    {
        "code": "XS8978",
        "qty": 4,
        "price": 17.20,
        "upc": "191009723592",
        "desc_contains": "Cotton Table",
    },
    # Add more expected products based on actual PDF content...
]


def load_cs_error2_document():
    """Load CS003837319_Error 2.PDF Document AI output for testing"""
    json_file = "test_invoices/CS003837319_Error 2_docai_output.json"

    try:
        with open(json_file, "r") as f:
            doc_data = json.load(f)
    except FileNotFoundError:
        pytest.skip(f"Test data file not found: {json_file}")

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


def test_cs_error2_vendor_detection():
    """Test that CS003837319_Error 2.PDF is correctly detected as Creative-Coop"""
    from main import detect_vendor_type

    document = load_cs_error2_document()
    vendor_type = detect_vendor_type(document.text)
    assert vendor_type == "Creative-Coop"


def test_cs_error2_complete_processing():
    """Test complete processing of CS003837319_Error 2.PDF"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()

    # Process the document
    rows = process_creative_coop_document(document)

    # Basic validation - THIS SHOULD FAIL initially (RED phase)
    assert len(rows) >= 20, f"Expected at least 20 rows, got {len(rows)}"
    assert len(rows) <= 50, f"Expected at most 50 rows, got {len(rows)} (sanity check)"

    # Validate each row has correct structure (6 columns for B:G)
    for i, row in enumerate(rows):
        assert len(row) == 6, f"Row {i} has {len(row)} columns, expected 6 (B:G format)"


def test_cs_error2_specific_products_extracted():
    """Test that specific expected products are correctly extracted"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Convert rows to searchable format
    extracted_products = {}
    for row in rows:
        if len(row) >= 6:
            # Assuming format: [Invoice Date, Vendor, Invoice#, Description, Price, Qty]
            description = row[3]
            price = row[4] if row[4] else 0.0
            qty = row[5] if row[5] else 0

            # Extract product code from description (first part)
            product_code = description.split()[0] if description else ""
            extracted_products[product_code] = {
                "qty": int(qty) if isinstance(qty, str) and qty.isdigit() else qty,
                "price": (
                    float(price)
                    if isinstance(price, str) and price.replace(".", "").isdigit()
                    else price
                ),
                "description": description,
            }

    # Check specific expected products - THIS SHOULD FAIL initially
    critical_products = ["XS9826A", "XS9482", "XS9840A", "XS8185", "XS9357"]

    for expected in EXPECTED_CS_ERROR2_PRODUCTS[
        :10
    ]:  # Check first 10 expected products
        product_code = expected["code"]
        expected_qty = expected["qty"]
        expected_price = expected["price"]

        assert (
            product_code in extracted_products
        ), f"Product {product_code} not found in extracted data"

        extracted = extracted_products[product_code]
        assert (
            extracted["qty"] == expected_qty
        ), f"{product_code}: Expected qty {expected_qty}, got {extracted['qty']}"
        assert (
            abs(float(extracted["price"]) - expected_price) < 0.01
        ), f"{product_code}: Price mismatch"


def test_cs_error2_data_quality():
    """Test data quality of extracted information"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    valid_rows = 0
    for row in rows:
        if len(row) >= 6:
            invoice_date, vendor, invoice_num, description, price, qty = row[:6]

            # Data quality checks
            assert invoice_date, "Invoice date should not be empty"
            assert vendor, "Vendor should not be empty"
            assert description, "Description should not be empty"

            # Price and quantity should be valid numbers
            try:
                price_val = float(price) if price else 0.0
                qty_val = int(qty) if qty else 0
                assert price_val >= 0, f"Price should be non-negative: {price_val}"
                assert qty_val >= 0, f"Quantity should be non-negative: {qty_val}"
                valid_rows += 1
            except (ValueError, TypeError):
                pytest.fail(
                    f"Invalid price or quantity format: price={price}, qty={qty}"
                )

    # THIS SHOULD FAIL initially - expecting 20+ valid rows
    assert valid_rows >= 20, f"Expected at least 20 valid rows, got {valid_rows}"


def test_cs_error2_performance():
    """Test that processing completes within reasonable time"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()

    start_time = time.time()
    rows = process_creative_coop_document(document)
    end_time = time.time()

    processing_time = end_time - start_time
    assert (
        processing_time < 30
    ), f"Processing took {processing_time:.2f}s, expected < 30s"
    assert len(rows) > 0, "Should extract at least some rows within time limit"


def test_cs_error2_zero_quantity_handling():
    """Test handling of products with zero ordered quantities"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Some products in the invoice have 0 ordered quantity and should be filtered out
    zero_qty_products = [
        "XS8911A",
        "XS8912A",
        "XS9089",
    ]  # These have 0 ordered quantity

    extracted_codes = []
    for row in rows:
        if len(row) >= 4:
            description = row[3]
            product_code = description.split()[0] if description else ""
            extracted_codes.append(product_code)

    # Products with 0 quantity should not appear in final output
    for zero_product in zero_qty_products:
        assert (
            zero_product not in extracted_codes
        ), f"Product {zero_product} with 0 qty should be filtered out"


def test_cs_error2_csv_output_format():
    """Test CSV output format matches expected Google Sheets structure"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Save to CSV and validate format
    output_file = "test_invoices/CS003837319_Error_2_test_output.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"]
        )

        for row in rows:
            writer.writerow(row)

    # Validate CSV structure
    with open(output_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        assert header == [
            "Invoice Date",
            "Vendor",
            "Invoice#",
            "Description",
            "Price",
            "Qty",
        ]

        data_rows = list(reader)
        # THIS SHOULD FAIL initially - expecting 20+ rows
        assert len(data_rows) >= 20, f"Expected at least 20 data rows in CSV"


def test_cs_error2_accuracy_benchmark():
    """Test accuracy against expected results (benchmark for improvements)"""
    from main import process_creative_coop_document

    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Convert to comparable format
    extracted_data = {}
    for row in rows:
        if len(row) >= 6:
            description = row[3]
            product_code = description.split()[0] if description else ""
            if product_code:
                extracted_data[product_code] = {
                    "qty": int(row[5]) if row[5] and str(row[5]).isdigit() else 0,
                    "price": (
                        float(row[4])
                        if row[4] and str(row[4]).replace(".", "").isdigit()
                        else 0.0
                    ),
                }

    # Calculate accuracy metrics
    total_expected = len(EXPECTED_CS_ERROR2_PRODUCTS)
    correctly_extracted = 0

    for expected in EXPECTED_CS_ERROR2_PRODUCTS:
        product_code = expected["code"]
        if product_code in extracted_data:
            extracted = extracted_data[product_code]
            if (
                extracted["qty"] == expected["qty"]
                and abs(extracted["price"] - expected["price"]) < 0.01
            ):
                correctly_extracted += 1

    accuracy = correctly_extracted / total_expected
    print(f"Accuracy: {correctly_extracted}/{total_expected} = {accuracy:.1%}")

    # Benchmark target: 90% accuracy - THIS SHOULD FAIL initially
    assert accuracy >= 0.90, f"Accuracy {accuracy:.1%} below target 90%"


def test_cs_error2_tier_usage_validation():
    """Test that the new multi-tier extraction is being used"""
    from main import extract_creative_coop_quantity_improved
    import io
    import sys
    from contextlib import redirect_stdout

    # Sample products from CS Error 2 in tabular format
    tabular_sample = 'XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40'

    # Capture tier usage logs
    log_output = io.StringIO()
    with redirect_stdout(log_output):
        result = extract_creative_coop_quantity_improved(tabular_sample, "XS9826A")

    log_content = log_output.getvalue()

    # Should use Tier 1 (Tabular) for CS Error 2 format
    assert (
        "Tier 1 (Tabular)" in log_content
    ), "Should use Tier 1 for tabular CS Error 2 format"
    assert result == 24, f"Should extract correct quantity: expected 24, got {result}"


def test_cs_error2_integration_with_existing_system():
    """Test integration with existing Creative-Coop processing system"""
    from main import detect_vendor_type, process_creative_coop_document

    document = load_cs_error2_document()

    # Should be detected as Creative-Coop
    vendor_type = detect_vendor_type(document.text)
    assert vendor_type == "Creative-Coop"

    # Should route to Creative-Coop processing
    rows = process_creative_coop_document(document)

    # Should produce structured output
    assert isinstance(rows, list), "Should return list of rows"
    if rows:  # Only test structure if rows exist
        assert len(rows[0]) == 6, "Each row should have 6 columns (B:G format)"


if __name__ == "__main__":
    # Run specific test to verify RED phase (should fail)
    print("🔴 Running Task 08 RED Phase Tests - Should FAIL until GREEN implementation")
    print("=" * 70)

    try:
        test_cs_error2_complete_processing()
        print("❌ Complete processing test should have failed (insufficient rows)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Complete processing test failed as expected - {e}")

    try:
        test_cs_error2_specific_products_extracted()
        print("❌ Specific products test should have failed (products not found)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Specific products test failed as expected - {e}")

    try:
        test_cs_error2_accuracy_benchmark()
        print("❌ Accuracy benchmark test should have failed (low accuracy)")
    except (ImportError, AttributeError, AssertionError) as e:
        print(f"✅ RED Phase: Accuracy benchmark test failed as expected - {e}")

    print(
        "\n🎯 Task 08 RED Phase Complete: All tests should fail until implementation improves CS Error 2 processing"
    )
