#!/usr/bin/env python3
"""
CS003837319_Error 2.PDF End-to-End Validation Test Suite

TDD RED Phase - Comprehensive end-to-end tests validating complete CS003837319_Error 2.PDF
processing pipeline with 90%+ accuracy target.

Test Requirements:
- End-to-end integration tests for complete CS003837319_Error 2.PDF processing
- Validation tests comparing extracted data against manual PDF verification
- Data quality tests ensuring all extracted information is accurate and complete
- Performance tests for complete pipeline within Zapier timeout constraints
- Output format tests validating Google Sheets B:G column structure
- Accuracy benchmark tests with target 90%+ success rate
"""

import csv
import json
import os
import sys
import time
from unittest.mock import Mock

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import detect_vendor_type, process_creative_coop_document

# Expected results from manual PDF analysis of CS003837319_Error 2.PDF
# These 20 products should be extracted with correct quantities and prices
EXPECTED_CS_ERROR2_RESULTS = [
    {
        "code": "XS9826A",
        "upc": "191009727774",
        "qty": 24,
        "price": 1.60,
        "desc_contains": "Metal Ballerina",
    },
    {
        "code": "XS9649A",
        "upc": "191009725688",
        "qty": 24,
        "price": 2.80,
        "desc_contains": "Paper Mache",
    },
    {
        "code": "XS9482",
        "upc": "191009714712",
        "qty": 12,
        "price": 2.80,
        "desc_contains": "Wood Shoe",
    },
    {
        "code": "XS9840A",
        "upc": "191009727910",
        "qty": 24,
        "price": 2.80,
        "desc_contains": "Metal",
    },
    {
        "code": "XS8185",
        "upc": "191009721666",
        "qty": 16,
        "price": 12.00,
        "desc_contains": "Cotton Lumbar Pillow",
    },
    {
        "code": "XS9357",
        "upc": "191009713470",
        "qty": 12,
        "price": 4.00,
        "desc_contains": "Metal Bow Tree",
    },
    {
        "code": "XS7529",
        "upc": "191009690856",
        "qty": 18,
        "price": 8.00,
        "desc_contains": "Metal Leaves",
    },
    {
        "code": "XS7653A",
        "upc": "191009689553",
        "qty": 24,
        "price": 4.00,
        "desc_contains": "Stoneware",
    },
    {
        "code": "XS8109",
        "upc": "191009720799",
        "qty": 12,
        "price": 12.80,
        "desc_contains": "Wool Felt",
    },
    {
        "code": "XS8379A",
        "upc": "191009705277",
        "qty": 24,
        "price": 4.00,
        "desc_contains": "Stoneware Mug",
    },
    {
        "code": "XS5747A",
        "upc": "191009635727",
        "qty": 24,
        "price": 3.20,
        "desc_contains": "Cotton",
    },
    {
        "code": "XS8838",
        "upc": "191009709855",
        "qty": 6,
        "price": 5.60,
        "desc_contains": "Glass Canister",
    },
    {
        "code": "XS8837",
        "upc": "191009709848",
        "qty": 6,
        "price": 6.40,
        "desc_contains": "Glass Canister",
    },
    {
        "code": "XS3350",
        "upc": "191009571414",
        "qty": 12,
        "price": 8.00,
        "desc_contains": "Cotton Tea",
    },
    {
        "code": "XS3844",
        "upc": "191009582816",
        "qty": 4,
        "price": 18.80,
        "desc_contains": "Acrylic",
    },
    {
        "code": "XS8714",
        "upc": "191009722922",
        "qty": 4,
        "price": 18.80,
        "desc_contains": "Acrylic Throw",
    },
    {
        "code": "XS5692A",
        "upc": "191009636038",
        "qty": 24,
        "price": 3.20,
        "desc_contains": "Stoneware Mug",
    },
    {
        "code": "XS9082",
        "upc": "191009723929",
        "qty": 12,
        "price": 4.00,
        "desc_contains": "Cotton PotHolder",
    },
    {
        "code": "XS7793A",
        "upc": "191009717706",
        "qty": 24,
        "price": 3.00,
        "desc_contains": "Paper",
    },
    {
        "code": "XS8978",
        "upc": "191009723592",
        "qty": 4,
        "price": 17.20,
        "desc_contains": "Cotton Table",
    },
    # Products with zero ordered quantity should be filtered out:
    # XS8911A (qty=0), XS8912A (qty=0), XS9089 (qty=0) should NOT appear in final output
]


def load_cs_error2_document():
    """Load CS003837319_Error 2.PDF Document AI output for testing"""
    json_file = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    try:
        with open(json_file, "r") as f:
            doc_data = json.load(f)
    except FileNotFoundError:
        pytest.skip(f"CS Error 2 JSON file not found: {json_file}")

    # Create mock document object compatible with main.py expectations
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
    """Test that CS003837319_Error 2.PDF is correctly identified as Creative-Coop"""
    document = load_cs_error2_document()
    vendor_type = detect_vendor_type(document.text)

    assert vendor_type == "Creative-Coop", f"Expected Creative-Coop, got {vendor_type}"


def test_cs_error2_complete_pipeline():
    """Test complete end-to-end processing pipeline"""
    document = load_cs_error2_document()

    # Time the complete processing
    start_time = time.time()
    rows = process_creative_coop_document(document)
    end_time = time.time()

    processing_time = end_time - start_time

    # Basic validation
    assert len(rows) >= 20, f"Expected at least 20 rows, got {len(rows)}"
    assert len(rows) <= 50, f"Expected at most 50 rows, got {len(rows)} (sanity check)"
    assert (
        processing_time < 30
    ), f"Processing took {processing_time:.2f}s, expected < 30s"

    # Validate Google Sheets B:G format (6 columns)
    for i, row in enumerate(rows):
        assert len(row) == 6, f"Row {i} has {len(row)} columns, expected 6 (B:G format)"

        # Basic data type validation
        invoice_date, vendor, invoice_num, description, price, qty = row
        assert isinstance(invoice_date, str), f"Invoice date should be string"
        assert isinstance(vendor, str), f"Vendor should be string"
        assert isinstance(description, str), f"Description should be string"

        # Price and quantity should be convertible to numbers
        try:
            # Clean price string (remove $ sign)
            price_str = str(price).replace("$", "") if price else "0"
            price_val = float(price_str)
            qty_val = int(qty) if qty else 0
            assert price_val >= 0, f"Price should be non-negative: {price_val}"
            assert qty_val > 0, f"Quantity should be positive: {qty_val}"
        except (ValueError, TypeError) as e:
            pytest.fail(
                f"Row {i} has invalid price/qty format: price={price}, qty={qty}, error={e}"
            )


def test_cs_error2_accuracy_validation():
    """Test extraction accuracy against expected results"""
    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Convert rows to searchable format
    extracted_products = {}
    for row in rows:
        if len(row) >= 6:
            description = row[3]
            # Clean price string (remove $ sign)
            price_str = str(row[4]).replace("$", "") if row[4] else "0"
            price = float(price_str)
            qty = int(row[5]) if row[5] else 0

            # Extract product code from description (should be first part)
            product_code = description.split()[0] if description else ""
            if product_code:
                extracted_products[product_code] = {
                    "qty": qty,
                    "price": price,
                    "description": description,
                }

    # Calculate accuracy metrics
    total_expected = len(EXPECTED_CS_ERROR2_RESULTS)
    correct_extractions = 0
    quantity_matches = 0
    price_matches = 0

    missing_products = []
    incorrect_extractions = []

    for expected in EXPECTED_CS_ERROR2_RESULTS:
        product_code = expected["code"]
        expected_qty = expected["qty"]
        expected_price = expected["price"]

        if product_code in extracted_products:
            extracted = extracted_products[product_code]

            qty_correct = extracted["qty"] == expected_qty
            price_correct = abs(extracted["price"] - expected_price) < 0.01

            if qty_correct:
                quantity_matches += 1
            if price_correct:
                price_matches += 1
            if qty_correct and price_correct:
                correct_extractions += 1
            else:
                incorrect_extractions.append(
                    {
                        "code": product_code,
                        "expected": {"qty": expected_qty, "price": expected_price},
                        "extracted": {
                            "qty": extracted["qty"],
                            "price": extracted["price"],
                        },
                    }
                )
        else:
            missing_products.append(product_code)

    # Calculate success rates
    overall_accuracy = correct_extractions / total_expected
    quantity_accuracy = quantity_matches / total_expected
    price_accuracy = price_matches / total_expected

    print(f"\n📊 CS003837319_Error 2.PDF Accuracy Results:")
    print(
        f"Overall Accuracy: {correct_extractions}/{total_expected} ({overall_accuracy:.1%})"
    )
    print(
        f"Quantity Accuracy: {quantity_matches}/{total_expected} ({quantity_accuracy:.1%})"
    )
    print(f"Price Accuracy: {price_matches}/{total_expected} ({price_accuracy:.1%})")

    if missing_products:
        print(
            f"❌ Missing Products ({len(missing_products)}): {missing_products[:5]}..."
        )

    if incorrect_extractions:
        print(f"❌ Incorrect Extractions ({len(incorrect_extractions)}):")
        for error in incorrect_extractions[:3]:  # Show first 3 errors
            print(
                f"   {error['code']}: Expected qty={error['expected']['qty']}, price=${error['expected']['price']}, Got qty={error['extracted']['qty']}, price=${error['extracted']['price']}"
            )

    # Acceptance criteria
    assert (
        overall_accuracy >= 0.90
    ), f"Overall accuracy {overall_accuracy:.1%} below target 90%"
    assert (
        quantity_accuracy >= 0.95
    ), f"Quantity accuracy {quantity_accuracy:.1%} below target 95%"
    assert (
        price_accuracy >= 0.90
    ), f"Price accuracy {price_accuracy:.1%} below target 90%"


def test_cs_error2_zero_quantity_filtering():
    """Test that products with zero ordered quantities are correctly filtered out"""
    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Products that should be filtered out (have 0 ordered quantity)
    zero_qty_products = ["XS8911A", "XS8912A", "XS9089"]

    extracted_codes = []
    for row in rows:
        if len(row) >= 4:
            description = row[3]
            product_code = description.split()[0] if description else ""
            extracted_codes.append(product_code)

    for zero_product in zero_qty_products:
        assert (
            zero_product not in extracted_codes
        ), f"Product {zero_product} with 0 qty should be filtered out"


def test_cs_error2_data_quality():
    """Test comprehensive data quality of extracted information"""
    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    data_quality_issues = []
    valid_rows = 0

    for i, row in enumerate(rows):
        if len(row) >= 6:
            invoice_date, vendor, invoice_num, description, price, qty = row[:6]

            # Check for empty critical fields
            if not invoice_date:
                data_quality_issues.append(f"Row {i}: Empty invoice date")
            if not vendor:
                data_quality_issues.append(f"Row {i}: Empty vendor")
            if not description:
                data_quality_issues.append(f"Row {i}: Empty description")

            # Check vendor consistency
            if vendor and vendor != "Creative-Coop":
                data_quality_issues.append(
                    f"Row {i}: Incorrect vendor '{vendor}', expected 'Creative-Coop'"
                )

            # Check description format (should start with product code)
            if description:
                parts = description.split()
                if not parts or not parts[0].startswith("XS"):
                    data_quality_issues.append(
                        f"Row {i}: Description doesn't start with XS product code: '{description[:50]}'"
                    )

            # Check price and quantity formats
            try:
                # Clean price string (remove $ sign)
                price_str = str(price).replace("$", "") if price else "0"
                price_val = float(price_str)
                qty_val = int(qty) if qty else 0

                if price_val <= 0:
                    data_quality_issues.append(f"Row {i}: Invalid price: {price_val}")
                if qty_val <= 0:
                    data_quality_issues.append(f"Row {i}: Invalid quantity: {qty_val}")

                valid_rows += 1

            except (ValueError, TypeError):
                data_quality_issues.append(
                    f"Row {i}: Invalid price/qty format: price='{price}', qty='{qty}'"
                )

    # Report data quality results
    if data_quality_issues:
        print(f"\n⚠️  Data Quality Issues ({len(data_quality_issues)}):")
        for issue in data_quality_issues[:10]:  # Show first 10 issues
            print(f"   {issue}")

    # Quality acceptance criteria
    assert (
        len(data_quality_issues) == 0
    ), f"Found {len(data_quality_issues)} data quality issues"
    assert valid_rows >= 20, f"Only {valid_rows} valid rows, expected at least 20"


def test_cs_error2_csv_output_generation():
    """Test CSV output generation for manual verification"""
    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Generate CSV output for manual verification
    output_file = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error_2_end_to_end_output.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(
            ["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"]
        )

        # Write data rows
        for row in rows:
            writer.writerow(row)

    # Validate CSV file
    assert os.path.exists(output_file), f"CSV output file not created: {output_file}"

    # Read and validate CSV structure
    with open(output_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data_rows = list(reader)

        assert header == [
            "Invoice Date",
            "Vendor",
            "Invoice#",
            "Description",
            "Price",
            "Qty",
        ]
        assert (
            len(data_rows) >= 20
        ), f"CSV contains {len(data_rows)} rows, expected at least 20"

    print(f"\n💾 CSV output generated: {output_file}")
    print(f"📊 CSV contains {len(data_rows)} data rows")


def test_cs_error2_performance_benchmarks():
    """Test performance benchmarks for production deployment"""
    document = load_cs_error2_document()

    # Run multiple processing iterations to get average performance
    processing_times = []

    for iteration in range(5):
        start_time = time.time()
        rows = process_creative_coop_document(document)
        end_time = time.time()

        processing_times.append(end_time - start_time)

    avg_time = sum(processing_times) / len(processing_times)
    max_time = max(processing_times)
    min_time = min(processing_times)

    print(f"\n⚡ Performance Benchmarks:")
    print(f"Average processing time: {avg_time:.2f}s")
    print(f"Maximum processing time: {max_time:.2f}s")
    print(f"Minimum processing time: {min_time:.2f}s")
    print(f"Rows extracted per second: {len(rows)/avg_time:.1f}")

    # Performance acceptance criteria
    assert avg_time < 15.0, f"Average processing time {avg_time:.2f}s exceeds 15s limit"
    assert max_time < 30.0, f"Maximum processing time {max_time:.2f}s exceeds 30s limit"
    assert len(rows) >= 20, f"Should extract at least 20 rows, got {len(rows)}"


def test_cs_error2_integration_with_existing_system():
    """Test integration with existing Creative-Coop processing system"""
    document = load_cs_error2_document()

    # Test that vendor detection works correctly
    vendor_type = detect_vendor_type(document.text)
    assert vendor_type == "Creative-Coop"

    # Test that processing routes to Creative-Coop specific logic
    rows = process_creative_coop_document(document)

    # Validate that Creative-Coop specific processing was applied
    for row in rows:
        if len(row) >= 6:
            vendor = row[1]
            description = row[3]

            assert vendor == "Creative-Coop"
            # Creative-Coop products should have XS codes
            assert any(
                part.startswith("XS") for part in description.split()
            ), f"No XS code found in description: {description}"


if __name__ == "__main__":
    # Run all tests when executed directly
    pytest.main([__file__, "-v"])
