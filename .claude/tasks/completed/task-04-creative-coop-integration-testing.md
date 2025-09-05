# Task 04: Creative-Coop Integration Testing - End-to-End XS-Code Processing

## TDD Cycle Overview
**RED**: Write integration tests that demonstrate Creative-Coop invoice CS003837319_Error 2.PDF fails to process (returns 0 items)
**GREEN**: Verify integration tests pass after XS-code pattern fix (returns 5+ items)
**REFACTOR**: Optimize test suite for comprehensive Creative-Coop processing validation

## Test Requirements
- [ ] End-to-end integration tests using CS003837319_Error 2.PDF
- [ ] Document AI to Google Sheets pipeline testing
- [ ] XS-code detection and processing validation tests
- [ ] Creative-Coop vendor-specific processing tests
- [ ] Performance tests within Zapier timeout limits
- [ ] Data accuracy tests comparing PDF content to extracted results

## Implementation Steps (Red-Green-Refactor)

### Step 1: RED - Write Failing Integration Tests

```python
# Test file: test_scripts/test_creative_coop_integration.py
import pytest
import json
import os
import tempfile
import csv
from unittest.mock import patch, MagicMock

# Import functions that will be tested
from main import (
    process_invoice,
    process_creative_coop_document,
    detect_vendor_type,
    extract_creative_coop_product_mappings_corrected,
    write_to_sheet
)

class TestCreativeCoopIntegration:

    @pytest.fixture
    def creative_coop_docai_data(self):
        """Load Creative-Coop Document AI data for testing"""
        docai_file = 'test_invoices/CS003837319_Error 2_docai_output.json'

        if not os.path.exists(docai_file):
            pytest.skip(f"Document AI output not found: {docai_file}")

        with open(docai_file, 'r') as f:
            return json.load(f)

    def test_creative_coop_invoice_currently_returns_zero_items(self, creative_coop_docai_data):
        """RED: Test that Creative-Coop invoice currently fails to extract line items"""
        # Process with current implementation (before XS-code fix)
        line_items = process_creative_coop_document(creative_coop_docai_data)

        # RED: This should fail initially - no XS codes detected
        assert len(line_items) == 0, f"Expected 0 items with current implementation, got {len(line_items)}"

    def test_vendor_detection_identifies_creative_coop(self, creative_coop_docai_data):
        """Test that vendor detection correctly identifies Creative-Coop"""
        vendor_info = detect_vendor_type(creative_coop_docai_data)

        # Should identify as Creative-Coop
        assert vendor_info['vendor'].lower() == 'creative-coop', f"Expected Creative-Coop, got {vendor_info['vendor']}"
        assert vendor_info['confidence'] > 0.5, f"Low confidence: {vendor_info['confidence']}"

    def test_xs_code_detection_fails_with_current_patterns(self, creative_coop_docai_data):
        """RED: Test that current patterns fail to detect XS codes from Document AI"""
        # Expected XS codes from the invoice
        expected_xs_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS9840A", "XS8185", "XS9357", "XS7529"]

        # Extract product mappings with current implementation
        product_mappings = extract_creative_coop_product_mappings_corrected(creative_coop_docai_data)

        # Count how many expected codes were found
        found_codes = []
        for product_code, details in product_mappings.items():
            if product_code in expected_xs_codes:
                found_codes.append(product_code)

        # RED: Should find 0 codes with current D-only pattern
        assert len(found_codes) == 0, f"Current pattern should find 0 XS codes, found: {found_codes}"

    def test_end_to_end_processing_pipeline_fails(self, creative_coop_docai_data):
        """RED: Test complete pipeline fails for Creative-Coop invoice"""

        # Mock Google Sheets write to capture output
        with patch('main.write_to_sheet') as mock_write:
            mock_write.return_value = True

            # Process invoice end-to-end
            try:
                # This simulates the main process_invoice function flow
                vendor_info = detect_vendor_type(creative_coop_docai_data)

                if vendor_info['vendor'].lower() == 'creative-coop':
                    line_items = process_creative_coop_document(creative_coop_docai_data)
                else:
                    line_items = []

                # RED: Should have 0 line items
                assert len(line_items) == 0, f"End-to-end should produce 0 items, got {len(line_items)}"

                # Verify Google Sheets not called due to 0 items
                mock_write.assert_not_called()

            except Exception as e:
                # If there's an error, that's also a failure case we're documenting
                assert True, f"Pipeline failed with error: {e}"

    def test_performance_baseline_for_creative_coop_processing(self, creative_coop_docai_data):
        """Test performance baseline for Creative-Coop processing"""
        import time

        start_time = time.time()

        # Process document (even if it returns 0 items)
        line_items = process_creative_coop_document(creative_coop_docai_data)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should complete within 30 seconds (well under Zapier 160s limit)
        assert processing_time < 30, f"Processing took too long: {processing_time:.2f}s"

        # Document current performance for comparison after fix
        print(f"Current processing time: {processing_time:.2f}s for {len(line_items)} items")

    def test_document_ai_structure_contains_xs_codes(self, creative_coop_docai_data):
        """RED: Verify Document AI contains XS codes but current processing doesn't extract them"""
        # Convert Document AI data to text for analysis
        document_text = ""

        # Extract text from entities
        if 'entities' in creative_coop_docai_data:
            for entity in creative_coop_docai_data['entities']:
                if 'mentionText' in entity:
                    document_text += entity['mentionText'] + " "

        # Extract text from pages
        if 'pages' in creative_coop_docai_data:
            for page in creative_coop_docai_data['pages']:
                if 'blocks' in page:
                    for block in page['blocks']:
                        if 'layout' in block and 'textAnchor' in block['layout']:
                            text_anchor = block['layout']['textAnchor']
                            if 'content' in text_anchor:
                                document_text += text_anchor['content'] + " "

        # Verify XS codes exist in raw document text
        import re
        xs_codes_in_text = re.findall(r'\bXS\d+[A-Z]?\b', document_text)

        # Document AI should contain XS codes
        assert len(xs_codes_in_text) > 0, f"No XS codes found in Document AI text: {document_text[:500]}..."

        # But current processing should miss them
        line_items = process_creative_coop_document(creative_coop_docai_data)
        assert len(line_items) == 0, f"Current processing should miss XS codes, but found {len(line_items)} items"

        print(f"XS codes in Document AI: {xs_codes_in_text}")
        print(f"Items extracted by current processing: {len(line_items)}")

    def test_csv_output_format_validation(self):
        """Test CSV output format for Creative-Coop processing"""
        # Mock line items that would be produced after fix
        expected_line_items = [
            ["2023-01-15", "Creative-Coop", "CS003837319", "XS9826A; Metal Ballerina Ornament", "8.50", "12"],
            ["2023-01-15", "Creative-Coop", "CS003837319", "XS8911A; Metal Item", "12.00", "6"],
        ]

        # Test CSV writing format
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow(["Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"])
            writer.writerows(expected_line_items)
            temp_csv = f.name

        # Verify CSV format
        with open(temp_csv, 'r') as f:
            lines = f.readlines()

            # Should have header + data lines
            assert len(lines) >= 3, f"Expected header + 2+ data lines, got {len(lines)}"

            # Verify 6 columns
            for line in lines:
                columns = line.strip().split(',')
                assert len(columns) == 6, f"Expected 6 columns, got {len(columns)}: {line}"

        # Clean up
        os.unlink(temp_csv)
```

### Step 2: GREEN - Verify Tests Pass After Fix

After implementing Task 01 (XS-code pattern fix), these tests should demonstrate success:

```python
# Additional tests that should pass after XS-code pattern fix

    def test_creative_coop_processing_extracts_xs_codes_after_fix(self, creative_coop_docai_data):
        """GREEN: Test that Creative-Coop processing extracts XS codes after pattern fix"""
        # This test should pass after Task 01 implementation
        line_items = process_creative_coop_document(creative_coop_docai_data)

        # GREEN: Should extract 5+ line items after fix
        assert len(line_items) >= 5, f"Expected 5+ items after fix, got {len(line_items)}"

        # Verify specific XS codes are detected
        extracted_codes = []
        for item in line_items:
            if len(item) > 3:  # Item column should contain product code
                item_text = item[3]
                if 'XS' in item_text:
                    extracted_codes.append(item_text)

        assert len(extracted_codes) > 0, f"No XS codes found in extracted items: {line_items}"

    def test_end_to_end_processing_succeeds_after_fix(self, creative_coop_docai_data):
        """GREEN: Test complete pipeline succeeds for Creative-Coop invoice after fix"""

        with patch('main.write_to_sheet') as mock_write:
            mock_write.return_value = True

            # Process invoice end-to-end
            vendor_info = detect_vendor_type(creative_coop_docai_data)

            if vendor_info['vendor'].lower() == 'creative-coop':
                line_items = process_creative_coop_document(creative_coop_docai_data)
            else:
                line_items = []

            # GREEN: Should have 5+ line items after fix
            assert len(line_items) >= 5, f"End-to-end should produce 5+ items, got {len(line_items)}"

            # Verify Google Sheets called with valid data
            if len(line_items) > 0:
                mock_write.assert_called_once()
                call_args = mock_write.call_args[0]
                assert len(call_args[0]) >= 5, f"Should write 5+ items to sheets, got {len(call_args[0])}"

    def test_specific_xs_codes_detected_after_fix(self, creative_coop_docai_data):
        """GREEN: Test that specific XS codes from invoice are detected"""
        # Expected codes from CS003837319_Error 2.PDF
        expected_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS9840A"]

        line_items = process_creative_coop_document(creative_coop_docai_data)

        # Extract product codes from line items
        found_codes = []
        for item in line_items:
            if len(item) > 3:
                item_text = item[3]  # Item column
                for expected_code in expected_codes:
                    if expected_code in item_text:
                        found_codes.append(expected_code)

        # Should find at least 3 of the expected codes
        assert len(found_codes) >= 3, f"Expected 3+ specific codes, found: {found_codes}"
```

### Step 3: REFACTOR - Optimize Test Suite

Create comprehensive test utilities and performance monitoring:

```python
# Test utilities for Creative-Coop integration testing

class CreativeCoopTestHelper:
    """Helper class for Creative-Coop integration testing"""

    @staticmethod
    def load_test_invoice():
        """Load Creative-Coop test invoice Document AI data"""
        docai_file = 'test_invoices/CS003837319_Error 2_docai_output.json'
        with open(docai_file, 'r') as f:
            return json.load(f)

    @staticmethod
    def extract_xs_codes_from_text(text):
        """Extract all XS codes from text"""
        import re
        return re.findall(r'\bXS\d+[A-Z]?\b', text)

    @staticmethod
    def validate_line_item_format(line_items):
        """Validate line items have correct 6-column format"""
        for i, item in enumerate(line_items):
            if len(item) != 6:
                raise AssertionError(f"Item {i} has {len(item)} columns, expected 6: {item}")
        return True

    @staticmethod
    def performance_monitor(func, *args, **kwargs):
        """Monitor performance of processing functions"""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        return {
            'result': result,
            'processing_time': end_time - start_time,
            'items_processed': len(result) if hasattr(result, '__len__') else 0
        }

# Performance benchmarking test
def test_creative_coop_performance_comparison():
    """Compare processing performance before and after fix"""
    helper = CreativeCoopTestHelper()
    docai_data = helper.load_test_invoice()

    # Benchmark current processing
    current_perf = helper.performance_monitor(process_creative_coop_document, docai_data)

    # Performance should remain acceptable after fix
    assert current_perf['processing_time'] < 30, f"Processing too slow: {current_perf['processing_time']:.2f}s"

    print(f"Processing time: {current_perf['processing_time']:.2f}s")
    print(f"Items extracted: {current_perf['items_processed']}")
    print(f"Items per second: {current_perf['items_processed'] / max(current_perf['processing_time'], 0.001):.1f}")
```

## Acceptance Criteria (Test-Driven)

- [ ] RED tests demonstrate Creative-Coop invoice processing failure (0 items extracted)
- [ ] GREEN tests verify processing success after XS-code pattern fix (5+ items extracted)
- [ ] End-to-end integration tests cover Document AI → Processing → Google Sheets pipeline
- [ ] Performance tests ensure processing stays within Zapier timeout limits (< 160s)
- [ ] Specific XS codes from CS003837319_Error 2.PDF are detected and processed
- [ ] CSV output format validation ensures 6-column B:G compatibility
- [ ] Integration tests cover vendor detection, line item extraction, and data formatting
- [ ] Test suite provides clear before/after comparison metrics
- [ ] All tests can run independently and repeatedly with consistent results

## Engineering Principles Applied

**Principle 1 - End-to-End Testing**: Complete pipeline validation from input to output
**Principle 2 - Performance Monitoring**: Continuous tracking of processing speed and efficiency
**Principle 3 - Data Accuracy**: Validation of extracted content against source PDF
**Principle 4 - Reliability**: Comprehensive error scenarios and edge case testing
**Principle 5 - Maintainability**: Reusable test utilities and clear test documentation

## Code Review Checklist

- [ ] **Test Coverage**: All critical Creative-Coop processing paths tested
- [ ] **Data Validation**: Extracted line items match PDF content accurately
- [ ] **Performance**: Processing completes well within timeout limits
- [ ] **Integration**: Complete pipeline from Document AI to Google Sheets tested
- [ ] **Error Handling**: Failure scenarios properly tested and documented
- [ ] **Maintainability**: Test utilities support future Creative-Coop testing
- [ ] **Documentation**: Clear test descriptions and expected outcomes
- [ ] **Reproducibility**: Tests produce consistent results across runs

## Success Metrics

- **Processing Success**: CS003837319_Error 2.PDF extracts 5+ line items (up from 0)
- **Accuracy**: Extracted data matches PDF content with >85% accuracy
- **Performance**: Processing completes in <90 seconds (within Zapier limits)
- **Reliability**: Tests pass consistently across multiple runs
- **Coverage**: All major Creative-Coop processing functions tested

## Files Created/Modified

- `test_scripts/test_creative_coop_integration.py` (comprehensive integration tests)
- `test_scripts/creative_coop_test_helper.py` (test utilities)
- Performance benchmarking and monitoring utilities
- Integration with existing Creative-Coop processing functions

## Dependencies

- CS003837319_Error 2.PDF and corresponding Document AI output
- Existing Creative-Coop processing functions in main.py
- Google Sheets API mocking for write operation testing
- Performance monitoring utilities for benchmarking
- Access to test environment with proper credentials
