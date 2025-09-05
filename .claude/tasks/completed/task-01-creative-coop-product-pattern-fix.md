# Task 01: Creative-Coop Product Code Pattern Fix - XS-Code Detection

## TDD Cycle Overview
**RED**: Write failing tests that demonstrate XS-prefixed codes are not detected by current patterns
**GREEN**: Update regex patterns in 5 locations to detect both D-codes and XS-codes
**REFACTOR**: Optimize patterns for performance and maintainability

## Test Requirements
- [ ] Unit tests for XS-code pattern detection (XS9826A, XS8911A, etc.)
- [ ] Unit tests for existing D-code pattern preservation (DB1234A, DG5678B, etc.)
- [ ] Integration tests using CS003837319_Error 2.PDF (Creative-Coop test invoice)
- [ ] Regression tests for existing vendors (HarperCollins, OneHundred80, Rifle Paper)
- [ ] Performance tests ensuring pattern matching stays within timeout limits
- [ ] Edge case tests for malformed product codes and boundary conditions

## Implementation Steps (Red-Green-Refactor)

### Step 1: RED - Write Failing Tests

```python
# Test file: test_scripts/test_creative_coop_pattern_detection.py
import pytest
import re
from main import (
    extract_creative_coop_product_mappings_corrected,
    process_creative_coop_document,
    extract_line_items_from_entities
)

def test_xs_code_detection_fails_with_current_pattern():
    """Test that current D-code pattern fails to detect XS codes - RED test"""
    # Current pattern from main.py line 979
    current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
    
    # Creative-Coop XS codes from CS003837319_Error 2.PDF
    xs_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS9840A", "XS8185", "XS9357", "XS7529"]
    
    test_text = " ".join(xs_codes)
    matches = re.findall(current_pattern, test_text)
    
    # RED: This should fail with current pattern
    assert len(matches) == 0, f"Current pattern should not match XS codes, but found: {matches}"

def test_d_code_detection_works_with_current_pattern():
    """Test that current pattern correctly detects D codes"""
    current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
    
    # Existing D codes from other vendors
    d_codes = ["DA1234A", "DB5678B", "DG9999C", "DH1111"]
    
    test_text = " ".join(d_codes)
    matches = re.findall(current_pattern, test_text)
    
    assert len(matches) == len(d_codes)
    assert set(matches) == set(d_codes)

def test_creative_coop_invoice_returns_zero_items_currently():
    """Test that Creative-Coop invoice currently returns 0 items - RED test"""
    # Load Creative-Coop test invoice Document AI output
    import json
    
    with open('test_invoices/CS003837319_Error 2_docai_output.json', 'r') as f:
        doc_ai_output = json.load(f)
    
    # Process with current implementation
    line_items = extract_line_items_from_entities(doc_ai_output)
    
    # RED: Should fail - currently returns 0 items
    assert len(line_items) == 0, f"Creative-Coop should return 0 items currently, got: {len(line_items)}"

def test_xs_code_extraction_from_entity_text():
    """Test XS code extraction from entity text fails with current pattern"""
    entity_text = "Product XS9826A Metal Ballerina Ornament UPC: 123456789012 Price: $8.50"
    
    # Current pattern from line 2203
    current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
    product_codes = re.findall(current_pattern, entity_text)
    
    # RED: Should find no matches with current pattern
    assert len(product_codes) == 0, f"Should find no XS codes with D-pattern, found: {product_codes}"

def test_product_upc_pattern_fails_for_xs_codes():
    """Test product-UPC pattern extraction fails for XS codes"""
    line_text = "XS9826A 123456789012 Metal Ballerina Ornament"
    
    # Current pattern from line 1780
    current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\s+(\d{12})"
    matches = re.findall(current_pattern, line_text)
    
    # RED: Should find no matches
    assert len(matches) == 0, f"Should find no XS-UPC pairs with D-pattern, found: {matches}"
```

### Step 2: GREEN - Minimal Implementation

Update the 5 regex patterns in main.py to support both D-codes and XS-codes:

```python
# Location 1 - Line 979: extract_creative_coop_product_mappings_corrected
# OLD: creative_coop_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", full_line_text)
# NEW: 
creative_coop_codes = re.findall(r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b", full_line_text)

# Location 2 - Line 1780: extract_creative_coop_product_mappings_corrected  
# OLD: product_upc_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\s+(\d{12})"
# NEW:
product_upc_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\s+(\d{12})"

# Location 3 - Line 1784: extract_creative_coop_product_mappings_corrected
# OLD: all_product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", full_line_text)
# NEW:
all_product_codes = re.findall(r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b", full_line_text)

# Location 4 - Line 2203: split_combined_line_item
# OLD: product_codes = re.findall(r"\b(D[A-Z]\d{4}[A-Z]?)\b", entity_text)
# NEW:
product_codes = re.findall(r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b", entity_text)

# Location 5 - Line 2381: extract_upc_from_text
# OLD: product_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"
# NEW:
product_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"
```

### Step 3: REFACTOR - Improve Design

Create a centralized pattern constant and helper function for maintainability:

```python
# Add to main.py constants section
CREATIVE_COOP_PRODUCT_CODE_PATTERN = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"
CREATIVE_COOP_PRODUCT_UPC_PATTERN = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\s+(\d{12})"

def extract_creative_coop_product_codes(text):
    """Extract Creative-Coop product codes (D-codes and XS-codes) from text"""
    return re.findall(CREATIVE_COOP_PRODUCT_CODE_PATTERN, text)

def extract_creative_coop_product_upc_pairs(text):
    """Extract Creative-Coop product-UPC pairs from text"""
    return re.findall(CREATIVE_COOP_PRODUCT_UPC_PATTERN, text)
```

## Acceptance Criteria (Test-Driven)

- [ ] All RED tests pass (demonstrating current failure with XS codes)
- [ ] All GREEN tests pass (demonstrating fix works for both D-codes and XS-codes)
- [ ] CS003837319_Error 2.PDF extracts 5+ line items (currently returns 0)
- [ ] XS9826A, XS8911A, XS9649A, XS9482, XS9840A codes are detected
- [ ] Existing D-code detection continues working (no regression)
- [ ] Pattern matching performance remains under 5ms per entity
- [ ] All 5 regex locations updated consistently
- [ ] Code coverage ≥ 95% for pattern matching functions
- [ ] Integration tests verify end-to-end Creative-Coop processing
- [ ] Processing completes within Zapier 160s timeout

## Engineering Principles Applied

**Principle 1 - Testability**: Every pattern change is verified with specific test cases
**Principle 2 - Maintainability**: Centralized pattern constants for easier future updates  
**Principle 3 - Performance**: Optimized regex patterns to avoid backtracking
**Principle 4 - Reliability**: Comprehensive edge case testing for malformed codes
**Principle 5 - Backward Compatibility**: Preserves existing D-code functionality

## Code Review Checklist

- [ ] **Pattern Accuracy**: All 5 locations updated with identical pattern logic
- [ ] **Test Coverage**: Both positive and negative test cases for D-codes and XS-codes
- [ ] **Performance**: Regex patterns avoid catastrophic backtracking
- [ ] **Maintainability**: Pattern constants centralized and well-documented
- [ ] **Integration**: End-to-end tests verify Creative-Coop invoice processing
- [ ] **Regression Prevention**: All existing vendor tests continue passing
- [ ] **Error Handling**: Graceful fallback for pattern matching failures
- [ ] **Documentation**: Pattern changes documented with examples

## Risk Assessment

**High Risk**: Breaking existing D-code processing for other vendors
- **Mitigation**: Comprehensive regression testing, additive pattern approach
- **Detection**: Automated tests for HarperCollins, OneHundred80, Rifle Paper

**Medium Risk**: Performance degradation from complex regex patterns
- **Mitigation**: Performance benchmarking, pattern optimization
- **Detection**: Processing time monitoring, timeout alerts

**Low Risk**: XS-code pattern edge cases not covered
- **Mitigation**: Comprehensive test cases, multiple Creative-Coop invoices
- **Detection**: Pattern matching accuracy monitoring

## Success Metrics

- **Primary**: CS003837319_Error 2.PDF processes successfully (0 → 5+ line items)
- **Secondary**: All existing vendor processing maintains 100% accuracy
- **Performance**: Pattern matching completes in <5ms per entity
- **Quality**: Zero production incidents related to product code detection
- **Business**: Staff confidence in automation restored for Creative-Coop invoices

## Files Modified

- `/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/main.py` (5 regex pattern updates)
- `test_scripts/test_creative_coop_pattern_detection.py` (new test file)
- Pattern constants and helper functions (refactor improvements)

## Dependencies

- Document AI output for CS003837319_Error 2.PDF available
- Test environment with Google Cloud credentials configured  
- Existing vendor test invoices for regression testing
- Performance monitoring baseline established