#!/usr/bin/env python3
"""
CS003837319_Error 2.PDF Complete Integration Validation

GREEN Phase - Complete integration implementation validating full pipeline
processing for CS003837319_Error 2.PDF with comprehensive metrics.

This script runs the complete end-to-end validation of Creative-Coop processing
and provides production-readiness assessment.
"""

import csv
import json
import os
import sys
import time

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import detect_vendor_type, process_creative_coop_document

# Expected results from manual PDF analysis of CS003837319_Error 2.PDF
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
]


def load_cs_error2_document():
    """Load CS003837319_Error 2.PDF Document AI output for testing"""
    json_file = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    try:
        with open(json_file, "r") as f:
            doc_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ CS Error 2 JSON file not found: {json_file}")
        print(
            "Please run: python document_ai_explorer.py 'test_invoices/CS003837319_Error 2.PDF' --save-json"
        )
        sys.exit(1)

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


def run_cs_error2_end_to_end_validation():
    """Run complete end-to-end validation of CS003837319_Error 2.PDF processing"""

    print("🧪 CS003837319_Error 2.PDF End-to-End Validation")
    print("=" * 70)

    start_time = time.time()

    # Load document
    document = load_cs_error2_document()
    print(
        f"📄 Document loaded: {len(document.entities)} entities, {len(document.text)} characters"
    )

    # Test vendor detection
    vendor_type = detect_vendor_type(document.text)
    print(f"🏢 Vendor detection: {vendor_type}")

    if vendor_type != "Creative-Coop":
        print(f"❌ CRITICAL: Expected Creative-Coop vendor, got {vendor_type}")
        return False

    # Process complete document
    processing_start = time.time()
    rows = process_creative_coop_document(document)
    processing_end = time.time()

    processing_time = processing_end - processing_start
    print(f"⚡ Processing time: {processing_time:.2f} seconds")
    print(f"📊 Extracted rows: {len(rows)}")

    # Validate results
    validation_results = validate_extraction_results(rows)

    # Generate output files
    output_files = generate_validation_outputs(rows)

    # Performance metrics
    print_performance_metrics(processing_time, len(rows))

    # Data quality check
    quality_results = validate_data_quality(rows)

    # Success summary
    total_time = time.time() - start_time
    print(f"\n✅ End-to-end validation completed in {total_time:.2f} seconds")

    # Overall success determination
    success = (
        validation_results["success"]
        and quality_results["success"]
        and processing_time < 30
        and len(rows) >= 20
    )

    if success:
        print("🎉 CS003837319_Error 2.PDF processing is PRODUCTION READY!")
        return True
    else:
        print("⚠️  Issues found that need attention before production deployment.")
        return False


def validate_extraction_results(rows):
    """Validate extracted results against expected data"""

    print("\n🔍 Validating extraction results...")

    # Convert rows to analysis format
    extracted_data = {}
    for row in rows:
        if len(row) >= 6:
            description = row[3]
            product_code = description.split()[0] if description else ""
            if product_code:
                # Clean price string (remove $ sign)
                price_str = str(row[4]).replace("$", "") if row[4] else "0"
                extracted_data[product_code] = {
                    "qty": int(row[5]) if row[5] else 0,
                    "price": float(price_str),
                    "description": description,
                    "vendor": row[1],
                    "invoice_date": row[0],
                }

    # Accuracy analysis
    total_expected = len(EXPECTED_CS_ERROR2_RESULTS)
    correctly_extracted = 0
    quantity_matches = 0
    price_matches = 0

    print(f"Expected products: {total_expected}")
    print(f"Extracted products: {len(extracted_data)}")

    missing_products = []
    incorrect_data = []

    for expected in EXPECTED_CS_ERROR2_RESULTS:
        product_code = expected["code"]
        if product_code in extracted_data:
            extracted = extracted_data[product_code]

            qty_match = extracted["qty"] == expected["qty"]
            price_match = abs(extracted["price"] - expected["price"]) < 0.01

            if qty_match:
                quantity_matches += 1
            if price_match:
                price_matches += 1
            if qty_match and price_match:
                correctly_extracted += 1
            else:
                incorrect_data.append(
                    {
                        "code": product_code,
                        "qty_match": qty_match,
                        "price_match": price_match,
                        "expected": expected,
                        "extracted": extracted,
                    }
                )
        else:
            missing_products.append(product_code)

    accuracy = correctly_extracted / total_expected
    quantity_accuracy = quantity_matches / total_expected
    price_accuracy = price_matches / total_expected

    print(
        f"✅ Correctly extracted: {correctly_extracted}/{total_expected} ({accuracy:.1%})"
    )
    print(
        f"📊 Quantity accuracy: {quantity_matches}/{total_expected} ({quantity_accuracy:.1%})"
    )
    print(f"💰 Price accuracy: {price_matches}/{total_expected} ({price_accuracy:.1%})")

    if missing_products:
        print(f"❌ Missing products: {len(missing_products)}")
        for missing in missing_products[:5]:
            print(f"   - {missing}")
        if len(missing_products) > 5:
            print(f"   ... and {len(missing_products) - 5} more")

    if incorrect_data:
        print(f"⚠️  Incorrect data: {len(incorrect_data)}")
        for error in incorrect_data[:3]:
            exp = error["expected"]
            ext = error["extracted"]
            print(
                f"   - {error['code']}: Expected qty={exp['qty']}, price=${exp['price']:.2f}"
            )
            print(f"     Got qty={ext['qty']}, price=${ext['price']:.2f}")
        if len(incorrect_data) > 3:
            print(f"   ... and {len(incorrect_data) - 3} more errors")

    return {
        "success": accuracy >= 0.90,
        "accuracy": accuracy,
        "quantity_accuracy": quantity_accuracy,
        "price_accuracy": price_accuracy,
        "correctly_extracted": correctly_extracted,
        "missing_products": missing_products,
        "incorrect_data": incorrect_data,
    }


def validate_data_quality(rows):
    """Validate data quality of all extracted rows"""

    print("\n🔬 Validating data quality...")

    quality_issues = []
    valid_rows = 0

    for i, row in enumerate(rows):
        if len(row) >= 6:
            invoice_date, vendor, invoice_num, description, price, qty = row[:6]

            # Check for empty critical fields
            if not invoice_date:
                quality_issues.append(f"Row {i}: Empty invoice date")
            if not vendor:
                quality_issues.append(f"Row {i}: Empty vendor")
            if not description:
                quality_issues.append(f"Row {i}: Empty description")

            # Check vendor consistency
            if vendor and vendor != "Creative-Coop":
                quality_issues.append(f"Row {i}: Wrong vendor '{vendor}'")

            # Validate description format
            if description:
                parts = description.split()
                if not parts or not parts[0].startswith("XS"):
                    quality_issues.append(
                        f"Row {i}: Invalid product code in '{description[:30]}'"
                    )

            # Validate price/quantity
            try:
                # Clean price string (remove $ sign)
                price_str = str(price).replace("$", "") if price else "0"
                price_val = float(price_str)
                qty_val = int(qty) if qty else 0

                if price_val <= 0:
                    quality_issues.append(f"Row {i}: Invalid price: ${price_val}")
                if qty_val <= 0:
                    quality_issues.append(f"Row {i}: Invalid quantity: {qty_val}")

                valid_rows += 1

            except (ValueError, TypeError):
                quality_issues.append(
                    f"Row {i}: Cannot parse price/qty: '{price}'/'{qty}'"
                )

    if quality_issues:
        print(f"⚠️  Data quality issues found: {len(quality_issues)}")
        for issue in quality_issues[:5]:
            print(f"   - {issue}")
        if len(quality_issues) > 5:
            print(f"   ... and {len(quality_issues) - 5} more issues")
    else:
        print("✅ All data quality checks passed")

    print(f"📊 Valid rows: {valid_rows}/{len(rows)}")

    return {
        "success": len(quality_issues) == 0 and valid_rows >= 20,
        "quality_issues": quality_issues,
        "valid_rows": valid_rows,
        "total_rows": len(rows),
    }


def generate_validation_outputs(rows):
    """Generate output files for manual verification"""

    print("\n💾 Generating validation outputs...")

    base_path = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices"

    # CSV output
    csv_file = f"{base_path}/CS003837319_Error_2_validation_output.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"]
        )
        for row in rows:
            writer.writerow(row)

    # Summary report
    report_file = f"{base_path}/CS003837319_Error_2_validation_report.txt"
    with open(report_file, "w", encoding="utf-8") as report:
        report.write("CS003837319_Error 2.PDF Processing Validation Report\n")
        report.write("=" * 50 + "\n\n")
        report.write(f"Processing Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Total Rows Extracted: {len(rows)}\n")

        report.write("\nExtracted Products:\n")
        for row in rows:
            if len(row) >= 6:
                description = row[3]
                price = row[4]
                qty = row[5]
                report.write(f"- {description}: ${price} x {qty}\n")

    print(f"📄 CSV output: {csv_file}")
    print(f"📋 Report: {report_file}")

    return {"csv_file": csv_file, "report_file": report_file}


def print_performance_metrics(processing_time, rows_extracted):
    """Print performance metrics for production readiness"""

    print("\n📈 Performance Metrics:")
    print(f"Processing time: {processing_time:.2f}s")
    print(f"Rows extracted: {rows_extracted}")
    print(f"Extraction rate: {rows_extracted/processing_time:.1f} rows/second")
    print(
        f"Zapier timeout compliance: {'✅ PASS' if processing_time < 160 else '❌ FAIL'} ({processing_time:.1f}s < 160s)"
    )
    print(
        f"Production target: {'✅ PASS' if processing_time < 30 else '⚠️ SLOW'} ({processing_time:.1f}s < 30s)"
    )


def main():
    """Main validation execution"""
    success = run_cs_error2_end_to_end_validation()

    print("\n" + "=" * 70)
    if success:
        print("🎯 VALIDATION RESULT: SUCCESS - Ready for production deployment!")
    else:
        print("❌ VALIDATION RESULT: FAILURE - Needs improvements before production")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
