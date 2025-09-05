## Task 08: Creative-Coop Comprehensive Testing - CS003837319_Error 2.PDF

### TDD Cycle Overview
**RED**: Write failing tests for complete CS003837319_Error 2.PDF processing with expected 20+ output rows ✅ COMPLETED
**GREEN**: Validate end-to-end Creative-Coop processing with correct quantities and data ⚠️ BLOCKED
**REFACTOR**: Optimize accuracy and performance based on comprehensive test results ⏸️ PENDING

## Phase 02 Implementation: Tabular Format Price Extraction

**Date**: January 5, 2025
**Status**: GREEN Phase - Implementing Tabular Price Extraction
**Next Steps**: Complete pricing extraction for CS003837319_Error 2.PDF tabular format

### Progress Update

The multi-tier quantity extraction system (Tasks 06 & 07) is working perfectly:
- ✅ **Task 06**: Tabular quantity column parser completed (RED-GREEN-REFACTOR)
- ✅ **Task 07**: Multi-tier quantity integration completed (RED-GREEN-REFACTOR)
- ✅ **Quantity Extraction**: Successfully finds 41 products with correct quantities (XS9826A=24, XS8185=16, etc.)

### Current Implementation Focus

Based on Phase 02 analysis, CS003837319_Error 2.PDF uses a structured tabular format:

```
Product Code | UPC         | Description              | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
XS9826A      | 191009727774| 6"H Metal Ballerina... | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
XS8911A      | 191009710615| 4-3/4"L x 3-1/2"W...   | 12      | 0         | 0           | 0         | each | 10.00      | 8.00       | 0.00
```

**Implementation Strategy**: Create tabular price extraction to complement the working quantity extraction.

### Next Implementation Tasks

1. **Tabular Price Column Parser**: Extract "Your Price" from 10th column after UPC
2. **Multi-tier Price Integration**: Integrate with existing `extract_wholesale_price()` fallback logic
3. **Complete End-to-End Testing**: Validate full CS003837319_Error 2.PDF processing pipeline

### Test Requirements
- [ ] Integration tests for complete CS003837319_Error 2.PDF processing pipeline
- [ ] Accuracy tests comparing extracted data vs manual verification of PDF content
- [ ] Performance tests ensuring processing completes within Zapier timeout constraints
- [ ] Edge case tests for products with 0 quantities, missing data, formatting variations
- [ ] Data quality tests validating UPC codes, descriptions, prices, and quantities
- [ ] Output format tests ensuring Google Sheets B:G column alignment

### Implementation Steps (Red-Green-Refactor)

#### Step 1: RED - Write Failing Tests
```python
# Test file: test_scripts/test_cs_error2_comprehensive.py
import pytest
import json
import csv
from unittest.mock import Mock
from main import process_creative_coop_document, detect_vendor_type

# Expected data from manual PDF analysis
EXPECTED_CS_ERROR2_PRODUCTS = [
    {"code": "XS9826A", "qty": 24, "price": 1.60, "upc": "191009727774", "desc_contains": "Metal Ballerina"},
    {"code": "XS9649A", "qty": 24, "price": 2.80, "upc": "191009725688", "desc_contains": "Paper Mache"},
    {"code": "XS9482", "qty": 12, "price": 2.80, "upc": "191009714712", "desc_contains": "Wood Shoe"},
    {"code": "XS9840A", "qty": 24, "price": 2.80, "upc": "191009727910", "desc_contains": "Metal"},
    {"code": "XS8185", "qty": 16, "price": 12.00, "upc": "191009721666", "desc_contains": "Cotton Lumbar Pillow"},
    {"code": "XS9357", "qty": 12, "price": 4.00, "upc": "191009713470", "desc_contains": "Metal Bow Tree"},
    {"code": "XS7529", "qty": 18, "price": 8.00, "upc": "191009690856", "desc_contains": "Metal Leaves"},
    {"code": "XS7653A", "qty": 24, "price": 4.00, "upc": "191009689553", "desc_contains": "Stoneware"},
    {"code": "XS8109", "qty": 12, "price": 12.80, "upc": "191009720799", "desc_contains": "Wool Felt"},
    {"code": "XS8379A", "qty": 24, "price": 4.00, "upc": "191009705277", "desc_contains": "Stoneware Mug"},
    {"code": "XS5747A", "qty": 24, "price": 3.20, "upc": "191009635727", "desc_contains": "Cotton"},
    {"code": "XS8838", "qty": 6, "price": 5.60, "upc": "191009709855", "desc_contains": "Glass Canister"},
    {"code": "XS8837", "qty": 6, "price": 6.40, "upc": "191009709848", "desc_contains": "Glass Canister"},
    {"code": "XS3350", "qty": 12, "price": 8.00, "upc": "191009571414", "desc_contains": "Cotton Tea"},
    {"code": "XS3844", "qty": 4, "price": 18.80, "upc": "191009582816", "desc_contains": "Acrylic"},
    {"code": "XS8714", "qty": 4, "price": 18.80, "upc": "191009722922", "desc_contains": "Acrylic Throw"},
    {"code": "XS5692A", "qty": 24, "price": 3.20, "upc": "191009636038", "desc_contains": "Stoneware Mug"},
    {"code": "XS9082", "qty": 12, "price": 4.00, "upc": "191009723929", "desc_contains": "Cotton PotHolder"},
    {"code": "XS7793A", "qty": 24, "price": 3.00, "upc": "191009717706", "desc_contains": "Paper"},
    {"code": "XS8978", "qty": 4, "price": 17.20, "upc": "191009723592", "desc_contains": "Cotton Table"},
    # Add more expected products based on actual PDF content...
]

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

def test_cs_error2_vendor_detection():
    """Test that CS003837319_Error 2.PDF is correctly detected as Creative-Coop"""
    document = load_cs_error2_document()
    vendor_type = detect_vendor_type(document.text)
    assert vendor_type == "Creative-Coop"

def test_cs_error2_complete_processing():
    """Test complete processing of CS003837319_Error 2.PDF"""
    document = load_cs_error2_document()

    # Process the document
    rows = process_creative_coop_document(document)

    # Basic validation
    assert len(rows) >= 20, f"Expected at least 20 rows, got {len(rows)}"
    assert len(rows) <= 50, f"Expected at most 50 rows, got {len(rows)} (sanity check)"

    # Validate each row has correct structure (6 columns for B:G)
    for i, row in enumerate(rows):
        assert len(row) == 6, f"Row {i} has {len(row)} columns, expected 6 (B:G format)"

def test_cs_error2_specific_products_extracted():
    """Test that specific expected products are correctly extracted"""
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
                "qty": qty,
                "price": price,
                "description": description
            }

    # Check specific expected products
    critical_products = ["XS9826A", "XS9482", "XS9840A", "XS8185", "XS9357"]

    for expected in EXPECTED_CS_ERROR2_PRODUCTS[:10]:  # Check first 10 expected products
        product_code = expected["code"]
        expected_qty = expected["qty"]
        expected_price = expected["price"]

        assert product_code in extracted_products, f"Product {product_code} not found in extracted data"

        extracted = extracted_products[product_code]
        assert extracted["qty"] == expected_qty, f"{product_code}: Expected qty {expected_qty}, got {extracted['qty']}"
        assert abs(float(extracted["price"]) - expected_price) < 0.01, f"{product_code}: Price mismatch"

def test_cs_error2_data_quality():
    """Test data quality of extracted information"""
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
                pytest.fail(f"Invalid price or quantity format: price={price}, qty={qty}")

    assert valid_rows >= 20, f"Expected at least 20 valid rows, got {valid_rows}"

def test_cs_error2_performance():
    """Test that processing completes within reasonable time"""
    import time

    document = load_cs_error2_document()

    start_time = time.time()
    rows = process_creative_coop_document(document)
    end_time = time.time()

    processing_time = end_time - start_time
    assert processing_time < 30, f"Processing took {processing_time:.2f}s, expected < 30s"
    assert len(rows) > 0, "Should extract at least some rows within time limit"

def test_cs_error2_zero_quantity_handling():
    """Test handling of products with zero ordered quantities"""
    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Some products in the invoice have 0 ordered quantity and should be filtered out
    zero_qty_products = ["XS8911A", "XS8912A", "XS9089"]  # These have 0 ordered quantity

    extracted_codes = []
    for row in rows:
        if len(row) >= 4:
            description = row[3]
            product_code = description.split()[0] if description else ""
            extracted_codes.append(product_code)

    # Products with 0 quantity should not appear in final output
    for zero_product in zero_qty_products:
        assert zero_product not in extracted_codes, f"Product {zero_product} with 0 qty should be filtered out"

def test_cs_error2_csv_output_format():
    """Test CSV output format matches expected Google Sheets structure"""
    document = load_cs_error2_document()
    rows = process_creative_coop_document(document)

    # Save to CSV and validate format
    output_file = "test_invoices/CS003837319_Error_2_test_output.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"])

        for row in rows:
            writer.writerow(row)

    # Validate CSV structure
    with open(output_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        assert header == ["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"]

        data_rows = list(reader)
        assert len(data_rows) >= 20, f"Expected at least 20 data rows in CSV"

def test_cs_error2_accuracy_benchmark():
    """Test accuracy against expected results (benchmark for improvements)"""
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
                    "qty": int(row[5]) if row[5] else 0,
                    "price": float(row[4]) if row[4] else 0.0
                }

    # Calculate accuracy metrics
    total_expected = len(EXPECTED_CS_ERROR2_PRODUCTS)
    correctly_extracted = 0

    for expected in EXPECTED_CS_ERROR2_PRODUCTS:
        product_code = expected["code"]
        if product_code in extracted_data:
            extracted = extracted_data[product_code]
            if (extracted["qty"] == expected["qty"] and
                abs(extracted["price"] - expected["price"]) < 0.01):
                correctly_extracted += 1

    accuracy = correctly_extracted / total_expected
    print(f"Accuracy: {correctly_extracted}/{total_expected} = {accuracy:.1%}")

    # Benchmark target: 90% accuracy
    assert accuracy >= 0.90, f"Accuracy {accuracy:.1%} below target 90%"
```

#### Step 2: GREEN - Validate Complete Processing
```python
# Test script to run comprehensive validation
# test_scripts/validate_cs_error2_end_to_end.py

def run_comprehensive_cs_error2_test():
    """Run complete end-to-end test of CS003837319_Error 2.PDF processing"""

    print("🧪 CS003837319_Error 2.PDF Comprehensive Testing")
    print("=" * 60)

    # Load document
    document = load_cs_error2_document()
    print(f"📄 Document loaded: {len(document.entities)} entities")

    # Test vendor detection
    vendor_type = detect_vendor_type(document.text)
    print(f"🏢 Vendor detection: {vendor_type}")
    assert vendor_type == "Creative-Coop"

    # Test complete processing
    import time
    start_time = time.time()

    rows = process_creative_coop_document(document)

    end_time = time.time()
    processing_time = end_time - start_time

    print(f"⚡ Processing time: {processing_time:.2f} seconds")
    print(f"📊 Extracted rows: {len(rows)}")

    # Validate minimum requirements
    assert len(rows) >= 20, f"FAIL: Expected ≥20 rows, got {len(rows)}"

    # Save results for manual inspection
    save_test_results(rows)

    # Calculate accuracy
    accuracy = calculate_accuracy(rows)
    print(f"🎯 Accuracy: {accuracy:.1%}")

    print("✅ All tests passed!")
    return rows

def save_test_results(rows):
    """Save test results to CSV for manual inspection"""
    output_file = "test_invoices/CS003837319_Error_2_comprehensive_output.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Invoice Date", "Vendor", "Invoice#", "Description", "Price", "Qty"])

        for row in rows:
            writer.writerow(row)

    print(f"💾 Results saved to: {output_file}")

def calculate_accuracy(rows):
    """Calculate extraction accuracy against expected results"""
    extracted_products = {}

    for row in rows:
        if len(row) >= 6:
            description = row[3]
            product_code = description.split()[0] if description else ""
            if product_code:
                extracted_products[product_code] = {
                    "qty": int(row[5]) if row[5] else 0,
                    "price": float(row[4]) if row[4] else 0.0,
                    "description": description
                }

    # Compare against expected
    matches = 0
    total = len(EXPECTED_CS_ERROR2_PRODUCTS)

    for expected in EXPECTED_CS_ERROR2_PRODUCTS:
        product_code = expected["code"]
        if product_code in extracted_products:
            extracted = extracted_products[product_code]
            if (extracted["qty"] == expected["qty"] and
                abs(extracted["price"] - expected["price"]) < 0.01):
                matches += 1
                print(f"✓ {product_code}: qty={extracted['qty']}, price=${extracted['price']}")
            else:
                print(f"❌ {product_code}: Expected qty={expected['qty']}, price=${expected['price']}, got qty={extracted['qty']}, price=${extracted['price']}")
        else:
            print(f"❌ {product_code}: Not found in extracted data")

    return matches / total

if __name__ == "__main__":
    run_comprehensive_cs_error2_test()
```

#### Step 3: REFACTOR - Optimize Based on Results
```python
# Based on test results, optimize the processing logic

def optimize_creative_coop_processing():
    """
    Apply optimizations based on comprehensive test results:

    1. Improve quantity extraction accuracy
    2. Enhance UPC code matching
    3. Optimize description cleaning
    4. Fine-tune price extraction
    """

    # Example optimizations that might be needed:

    # 1. Enhanced tabular parsing for edge cases
    def extract_quantity_from_table_columns_optimized(text, product_code):
        """Optimized version based on CS Error 2 analysis"""
        # Implementation based on test failure patterns
        pass

    # 2. Better handling of multi-line descriptions
    def clean_item_description_enhanced(description, product_code, upc):
        """Enhanced description cleaning based on test results"""
        # Implementation based on description quality analysis
        pass

    # 3. Improved price extraction for edge cases
    def extract_wholesale_price_optimized(text, product_code):
        """Optimized price extraction based on test failures"""
        # Implementation based on price accuracy analysis
        pass
```

### Acceptance Criteria (Test-Driven)

- [ ] **Primary Goal**: CS003837319_Error 2.PDF processing produces ≥20 output rows (vs current 0)
- [ ] **Accuracy Target**: ≥90% of expected products extracted with correct quantities and prices
- [ ] **Performance**: Complete processing within 30 seconds (well within Zapier 160s limit)
- [ ] **Data Quality**: All rows have valid invoice date, vendor, description, price, and quantity
- [ ] **Format Compliance**: Output matches Google Sheets B:G column structure (6 columns)
- [ ] **Zero Quantity Handling**: Products with 0 ordered quantity are correctly filtered out
- [ ] **CSV Output**: Generated CSV file is valid and human-readable for verification

### Engineering Principles Applied
- **Principle 2**: Comprehensive TDD with end-to-end integration tests
- **Principle 3**: Data quality validation and error detection
- **Principle 4**: Performance benchmarking within business constraints
- **Principle 5**: Structured testing with accuracy metrics and benchmarks
- **Principle 6**: Production-ready validation with real invoice processing

### Code Review Checklist

- [ ] Tests written to validate specific CS003837319_Error 2.PDF requirements
- [ ] Integration tests cover complete processing pipeline
- [ ] Performance tests ensure Zapier timeout compliance
- [ ] Data quality tests validate all extracted information
- [ ] Accuracy benchmarks established for future improvements
- [ ] CSV output format verified for Google Sheets compatibility
- [ ] Error handling tested for edge cases and malformed data

### Success Metrics
- **Functional Success**: CS003837319_Error 2.PDF → 20+ extracted rows (vs current 0)
- **Accuracy Success**: ≥90% of expected products correctly extracted
- **Performance Success**: Processing time <30 seconds
- **Quality Success**: All data validation tests pass
- **Integration Success**: End-to-end pipeline produces valid CSV output

### Expected Test Results (After Implementation)
```
🧪 CS003837319_Error 2.PDF Comprehensive Testing
============================================================
📄 Document loaded: 302 entities
🏢 Vendor detection: Creative-Coop
⚡ Processing time: 8.45 seconds
📊 Extracted rows: 28
🎯 Accuracy: 92.5%
💾 Results saved to: test_invoices/CS003837319_Error_2_comprehensive_output.csv
✅ All tests passed!
```
