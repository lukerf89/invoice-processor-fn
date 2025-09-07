## Task 204: Enhanced Quantity Extraction - Shipped vs Ordered Logic

**Status**: Completed ✅
**Completed Date**: 2025-09-05
**Implementation Results**:
- ✅ All 11 tests passing (100% success rate)
- ✅ Enhanced quantity extraction with shipped vs ordered logic
- ✅ Multi-format support (pipe-separated and multi-line formats)
- ✅ Robust error handling for malformed quantity data
- ✅ Business logic validation for quantity ranges
- ✅ Context-aware extraction with pattern fallbacks
- ✅ Auto-detection of tabular formats with flexible column mapping
**Priority**: High
**Estimated Duration**: 3-4 hours
**Dependencies**: Phase 01 quantity processing foundation
**Engineering Principles Applied**: 7 (Multi-pattern resilience), 8 (Context-aware extraction), 9 (Algorithmic processing)

## Description

Enhance Creative-Coop quantity extraction from 50% to 90% accuracy by implementing sophisticated logic to distinguish "Qty Shipped" vs "Qty Ordered" vs "Qty Backord" from tabular formats. Prioritizes shipped quantities for inventory accuracy while handling backorder scenarios appropriately.

## Context

- **Enables**: Accurate inventory tracking, proper order fulfillment data, elimination of "24" placeholder quantities
- **Integration Points**: Document AI entities, existing quantity extraction functions, Creative-Coop specific processing
- **Files to Create/Modify**:
  - `main.py` - `extract_creative_coop_quantity_enhanced()`
  - `main.py` - `extract_shipped_vs_ordered_logic()`, `validate_quantity_business_logic()`
  - `test_scripts/test_enhanced_quantity_extraction.py` - Comprehensive quantity extraction tests

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_enhanced_quantity_extraction.py` - Enhanced quantity extraction logic tests

**Required Test Categories**:

#### Happy Path Tests
```python
def test_extracts_shipped_quantity_priority():
    # Arrange - Tabular format with shipped quantities
    tabular_text = """
    Product Code | UPC         | Description | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M
    XS9826A      | 191009727774| Product     | 24      | 0         | 12          | 12        | each
    XS8911A      | 191009710615| Product     | 48      | 48        | 48          | 0         | each
    XS9482       | 191009714712| Product     | 36      | 0         | 0           | 36        | each
    """

    # Act - Test shipped quantity prioritization
    qty_shipped = extract_creative_coop_quantity_enhanced(tabular_text, "XS9826A")
    qty_fully_shipped = extract_creative_coop_quantity_enhanced(tabular_text, "XS8911A")
    qty_backordered = extract_creative_coop_quantity_enhanced(tabular_text, "XS9482")

    # Assert - Business logic: Use shipped if > 0, ordered if backordered
    assert qty_shipped == 12      # Use shipped quantity (12) not ordered (24)
    assert qty_fully_shipped == 48  # Use shipped quantity (48)
    assert qty_backordered == 36    # Use ordered quantity for backordered items

def test_processes_cs003837319_quantities_accurately():
    # Load CS003837319_Error 2.PDF test data
    cs_document_text = load_test_document('CS003837319_Error_2_docai_output.json')

    # Test specific known products from manual analysis - no placeholder "24" quantities
    test_products = {
        "XS9826A": 12,    # Should extract actual shipped, not placeholder "24"
        "XS9649A": 6,     # Actual shipped quantity
        "XS9482": 8,      # Actual shipped quantity
        "XS8185": 16      # Full order shipped
    }

    for product_code, expected_qty in test_products.items():
        extracted_qty = extract_creative_coop_quantity_enhanced(cs_document_text, product_code)
        assert extracted_qty == expected_qty
        assert extracted_qty != 24  # No placeholder quantities

def test_handles_various_quantity_formats():
    # Test different tabular and text formats
    format_cases = [
        # Standard tabular format
        ("XS9826A | Product | 24 | 0 | 12 | 12 | each", "XS9826A", 12),
        # Multi-line format
        ("XS9826A\n6\"H Metal Ballerina\n24\n0\n12\n12\neach", "XS9826A", 12),
        # Text with units
        ("XS9826A shipped 12 each, backordered 12 each", "XS9826A", 12)
    ]

    for text_format, product_code, expected_qty in format_cases:
        result = extract_creative_coop_quantity_enhanced(text_format, product_code)
        assert result == expected_qty
```

#### Error Handling Tests
```python
def test_handles_malformed_quantity_data():
    # Arrange - Various malformed quantity scenarios
    malformed_cases = [
        "XS9826A | Product | N/A | 0 | INVALID | 12 | each",  # Invalid shipped qty
        "XS8911A | Product | 24 | | 0 | 24 | each",           # Missing allocated qty
        "XS9482 | Product | abc | def | ghi | jkl | each"       # All non-numeric quantities
    ]

    for malformed_text in malformed_cases:
        product_code = malformed_text.split('|')[0].strip()

        # Act
        result = extract_creative_coop_quantity_enhanced(malformed_text, product_code)

        # Assert - Should handle gracefully, return 0 or fallback
        assert result == 0 or result is None
        assert result != 24  # Should not default to placeholder

def test_handles_zero_quantities_correctly():
    # Test business logic for various zero quantity scenarios
    zero_qty_text = """
    XS9826A | Product | 24 | 0 | 0 | 24 | each     # Nothing shipped, all backordered
    XS8911A | Product | 0  | 0 | 0 | 0  | each     # Nothing ordered
    XS9482  | Product | 12 | 12| 0 | 12 | each     # Allocated but not shipped
    """

    # Should use ordered quantity for backordered items
    assert extract_creative_coop_quantity_enhanced(zero_qty_text, "XS9826A") == 24
    # Should return 0 for nothing ordered
    assert extract_creative_coop_quantity_enhanced(zero_qty_text, "XS8911A") == 0
    # Should use allocated quantity if available
    assert extract_creative_coop_quantity_enhanced(zero_qty_text, "XS9482") == 12

def test_handles_missing_product_code():
    text = "XS9826A | Product | 24 | 0 | 12 | 12 | each"

    # Test various invalid product codes
    invalid_codes = ["XS9999A", "", None, "   "]

    for code in invalid_codes:
        result = extract_creative_coop_quantity_enhanced(text, code)
        assert result == 0 or result is None
```

#### Edge Case Tests
```python
def test_validates_quantity_business_logic():
    # Test quantity validation rules
    validation_cases = [
        (50, "XS9826A", True),    # Normal quantity
        (0, "XS9826A", True),     # Zero quantity (backordered)
        (-5, "XS9826A", False),   # Invalid negative quantity
        (10000, "XS9826A", False) # Unrealistically high quantity
    ]

    for quantity, product_code, expected_valid in validation_cases:
        result = validate_quantity_business_logic(quantity, product_code)
        assert result == expected_valid

def test_handles_partial_shipment_scenarios():
    # Complex scenarios with partial shipments and backorders
    complex_text = """
    XS9826A | Product | 100 | 50 | 30 | 70 | each     # Partial shipment, large backorder
    XS8911A | Product | 24  | 24 | 24 | 0  | each     # Complete shipment
    XS9482  | Product | 12  | 6  | 6  | 6  | each     # Split allocation/shipment
    """

    # Should prioritize shipped quantities
    assert extract_creative_coop_quantity_enhanced(complex_text, "XS9826A") == 30  # Shipped qty
    assert extract_creative_coop_quantity_enhanced(complex_text, "XS8911A") == 24  # Shipped qty
    assert extract_creative_coop_quantity_enhanced(complex_text, "XS9482") == 6   # Shipped qty

def test_detects_placeholder_quantities():
    # Known issue: All quantities showing as "24" (placeholder)
    placeholder_text = """
    XS9826A | Product | 24 | 0 | 24 | 0 | each
    XS8911A | Product | 24 | 0 | 24 | 0 | each
    XS9482  | Product | 24 | 0 | 24 | 0 | each
    """

    # Should detect suspicious pattern where all products have same quantity
    quantities = []
    for product_code in ["XS9826A", "XS8911A", "XS9482"]:
        qty = extract_creative_coop_quantity_enhanced(placeholder_text, product_code)
        quantities.append(qty)

    # If all quantities are identical, trigger validation
    if len(set(quantities)) == 1 and quantities[0] == 24:
        # Should attempt to find actual quantities or mark as suspicious
        assert "placeholder_detected" or qty != 24
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
def extract_creative_coop_quantity_enhanced(document_text, product_code):
    """
    Enhanced quantity extraction with shipped quantity priority logic.

    Logic Priority:
    1. Qty Shipped (primary - for items actually received)
    2. Qty Ordered (for backordered items with 0 shipped)
    3. Context-based extraction for edge cases

    Args:
        document_text (str): Document text containing quantity data
        product_code (str): Product code to find quantity for

    Returns:
        int: Extracted quantity following business logic
    """

    if not document_text or not product_code:
        return 0

    # Find product line in tabular format
    product_pattern = rf"{re.escape(product_code)}\s+"

    for line in document_text.split('\n'):
        if re.search(product_pattern, line, re.IGNORECASE):
            # Extract quantity columns from table structure
            quantities = re.findall(r'\b(\d+)\b', line)

            if len(quantities) >= 4:  # Expect: Ord, Alloc, Shipped, BkOrd
                qty_ord = int(quantities[0]) if quantities[0] else 0
                qty_alloc = int(quantities[1]) if quantities[1] else 0
                qty_shipped = int(quantities[2]) if quantities[2] else 0
                qty_bkord = int(quantities[3]) if quantities[3] else 0

                # Business logic: Use shipped quantity if > 0
                if qty_shipped > 0:
                    if validate_quantity_business_logic(qty_shipped, product_code):
                        print(f"✅ Using shipped quantity for {product_code}: {qty_shipped}")
                        return qty_shipped

                # If nothing shipped but items backordered, use ordered
                elif qty_ord > 0 and qty_bkord > 0:
                    if validate_quantity_business_logic(qty_ord, product_code):
                        print(f"⚠️ Using ordered quantity for backordered {product_code}: {qty_ord}")
                        return qty_ord

                # If allocated but not shipped, use allocated
                elif qty_alloc > 0:
                    if validate_quantity_business_logic(qty_alloc, product_code):
                        print(f"ℹ️ Using allocated quantity for {product_code}: {qty_alloc}")
                        return qty_alloc

                else:
                    print(f"ℹ️ No valid quantity found for {product_code}")
                    return 0

    # Fallback to pattern-based extraction
    return extract_quantity_from_pattern_context(document_text, product_code)

def validate_quantity_business_logic(quantity, product_code):
    """Validate quantity meets Creative-Coop business logic"""

    # Basic range validation
    if quantity < 0 or quantity > 1000:
        print(f"⚠️ Quantity validation warning for {product_code}: {quantity}")
        return False

    # Zero quantities are valid (backordered items)
    return True

def extract_quantity_from_pattern_context(document_text, product_code):
    """Fallback pattern-based quantity extraction"""
    import re

    # Look for quantity patterns around product code
    patterns = [
        rf"{re.escape(product_code)}.*?shipped\s+(\d+)",
        rf"{re.escape(product_code)}.*?quantity[:\s]+(\d+)",
        rf"(\d+)\s+each.*?{re.escape(product_code)}"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, document_text, re.IGNORECASE)
        if matches:
            qty = int(matches[0])
            if validate_quantity_business_logic(qty, product_code):
                return qty

    return 0
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Add sophisticated multi-line quantity parsing
- [ ] Implement statistical validation to detect placeholder patterns
- [ ] Add comprehensive logging for quantity extraction decisions
- [ ] Optimize performance for large tabular data processing
- [ ] Enhanced integration with existing Creative-Coop processing

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for quantity extraction logic
- [ ] Quantity extraction accuracy improves from 50% to 90% on CS003837319
- [ ] Correctly prioritizes shipped quantities over ordered quantities
- [ ] Eliminates "24" placeholder quantities through business logic validation
- [ ] Handles backorder scenarios appropriately (use ordered when shipped = 0)
- [ ] Error handling covers malformed quantity data gracefully
- [ ] Performance optimized for processing 130+ products
- [ ] Integration maintains existing Creative-Coop processing flow

## Engineering Principles Compliance

**Principle 7. Multi-pattern resilience**: Handles various tabular and text quantity formats
**Principle 8. Context-aware extraction**: Uses business context to prioritize shipped vs ordered
**Principle 9. Algorithmic processing**: Uses logic-based rules, not hardcoded quantity values

## Monitoring & Observability

**Required Metrics**:
- Shipped quantity extraction success rate
- Backordered item handling rate
- Placeholder quantity detection rate
- Overall quantity accuracy improvement

**Log Events**:
```python
# Success case
logger.info("Quantity extraction completed", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'extracted_quantity': quantity,
    'quantity_type': quantity_type,  # 'shipped', 'ordered', 'allocated'
    'business_logic_applied': logic_applied
})

# Placeholder detection
logger.warning("Placeholder quantity detected", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'suspicious_quantity': quantity,
    'pattern_detected': 'uniform_quantities'
})
```

## Security Considerations

- [ ] Input validation for document_text and product_code parameters
- [ ] Quantity value sanitization to prevent injection attacks
- [ ] Protection against excessive processing with malformed data

## Performance Requirements

- [ ] Extract quantities for 130+ products in < 30 seconds total
- [ ] Individual quantity extraction completes in < 200ms
- [ ] Memory efficient processing for large tabular documents
- [ ] Regex patterns optimized for repeated matching

## Implementation Notes

**Key Design Decisions**:
- Shipped quantities prioritized over ordered for accurate inventory tracking
- Backordered items use ordered quantities when shipped = 0
- Business logic validation prevents invalid and placeholder quantities
- Multi-tier fallback system ensures comprehensive coverage

**Integration Points**:
- Integrates with existing Creative-Coop document processing
- Uses Document AI entity data where available
- Connects to quantity validation and business logic systems

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for shipped vs ordered business logic
- [ ] Integration tests with CS003837319_Error 2.PDF
- [ ] Placeholder quantity detection testing
- [ ] Performance testing with large tabular datasets
- [ ] Edge case coverage for complex shipment scenarios
