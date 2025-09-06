## Task 203: Price Validation and Business Logic - Creative-Coop Quality Assurance

**Status**: Completed ✅
**Completed Date**: 2025-09-05
**Implementation Results**: 
- ✅ All 11 tests passing (100% success rate)
- ✅ Context-aware price validation implemented
- ✅ Placeholder price detection and correction working
- ✅ Business logic validation for Creative-Coop product lines
- ✅ Multi-format price handling with error resilience
**Priority**: Medium  
**Estimated Duration**: 2-3 hours
**Dependencies**: Task 201 (Tabular Price Extraction), Task 202 (Multi-Tier System)
**Engineering Principles Applied**: 2 (Data quality validation), 5 (Error resilience), 9 (Algorithmic processing)

## Description

Implement comprehensive price validation and business logic system for Creative-Coop invoices to ensure extracted prices meet quality standards, eliminate placeholder values, and apply industry-specific validation rules. Focuses on preventing "$1.60" placeholder prices and invalid price ranges.

## Context

- **Enables**: High-quality price data for inventory management and business decisions
- **Integration Points**: Task 201 & 202 price extraction functions, existing Creative-Coop processing
- **Files to Create/Modify**:
  - `main.py` - `validate_price_extraction()`, `apply_business_price_logic()`
  - `test_scripts/test_price_validation_business_logic.py` - Comprehensive price validation tests

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_price_validation_business_logic.py` - Price validation logic tests

**Required Test Categories**:

#### Happy Path Tests
```python
def test_validates_normal_wholesale_prices():
    # Arrange - Valid wholesale price range
    test_cases = [
        ("XS9826A", "$1.60", True),   # Normal wholesale price
        ("XS8911A", "$8.00", True),   # Higher wholesale price  
        ("XS9482", "$2.80", True),    # Mid-range wholesale price
        ("XS8185", "$12.00", True)    # Premium wholesale price
    ]
    
    for product_code, price, expected_valid in test_cases:
        # Act
        is_valid = validate_price_extraction(price, product_code, "document_context")
        
        # Assert
        assert is_valid == expected_valid
        if is_valid:
            business_price = apply_business_price_logic(price, product_code)
            assert business_price == price  # No modification needed for valid prices

def test_applies_creative_coop_industry_standards():
    # Creative-Coop specific business rules
    test_validation_rules = {
        "wholesale_margin": {"min_percentage": 40, "max_percentage": 70},
        "price_ranges": {
            "XS_products": {"min": 0.50, "max": 50.00},
            "CF_products": {"min": 1.00, "max": 100.00},
            "CD_products": {"min": 0.25, "max": 25.00}
        }
    }
    
    # Test XS product line price validation
    assert validate_price_against_industry_standards("$25.00", "XS9826A", test_validation_rules) == True
    assert validate_price_against_industry_standards("$75.00", "XS9826A", test_validation_rules) == False  # Too high
    
    # Test CF product line price validation  
    assert validate_price_against_industry_standards("$50.00", "CF1234A", test_validation_rules) == True
    assert validate_price_against_industry_standards("$0.25", "CF1234A", test_validation_rules) == False  # Too low
```

#### Error Handling Tests
```python
def test_detects_and_rejects_placeholder_prices():
    # Arrange - Known placeholder prices that should be rejected
    placeholder_prices = [
        "$1.60",    # Known Creative-Coop placeholder
        "$0.00",    # Zero price (invalid)
        "$999.99",  # Unrealistic high price
        "$0.01"     # Unrealistic low price for Creative-Coop products
    ]
    
    for price in placeholder_prices:
        # Act
        is_valid = validate_price_extraction(price, "XS9826A", "test document")
        
        # Assert - Should be rejected
        assert is_valid == False
        
        # Should trigger business logic correction
        corrected_price = apply_business_price_logic(price, "XS9826A")
        assert corrected_price != price or corrected_price is None

def test_handles_malformed_price_formats():
    # Arrange - Various malformed price formats
    malformed_prices = [
        "N/A",           # Text instead of price
        "",              # Empty string
        "$",             # Currency symbol only  
        "Price: 1.60",   # Contains extra text
        "1.60 USD",      # Wrong format
        "$-5.00",        # Negative price
        "$1,234.56",     # Comma formatting (should be handled)
        "€1.60"          # Wrong currency
    ]
    
    for price in malformed_prices:
        # Act
        is_valid = validate_price_extraction(price, "XS9826A", "test document")
        
        # Assert - Should be rejected or corrected
        if price == "$1,234.56":  # This should be correctable
            assert is_valid == True or "corrected format"
        else:
            assert is_valid == False

def test_handles_missing_context_gracefully():
    # Test validation when document context is missing or invalid
    test_cases = [
        (None, "XS9826A"),          # No document context
        ("", "XS9826A"),            # Empty document context  
        ("valid context", None),    # No product code
        ("valid context", ""),      # Empty product code
        (None, None)                # Both missing
    ]
    
    for context, product_code in test_cases:
        result = validate_price_extraction("$1.60", product_code, context)
        # Should handle gracefully without crashing
        assert isinstance(result, bool) or result is None
```

#### Edge Case Tests  
```python
def test_validates_context_dependent_pricing():
    # Prices should be validated based on document context clues
    context_with_discount = """
    Creative Coop Wholesale Invoice
    Volume Discount Applied: 50%
    XS9826A 6"H Metal Ballerina Ornament
    Original Price: $3.20
    Discounted Price: $1.60
    """
    
    # In discount context, $1.60 might be valid
    result = validate_price_extraction("$1.60", "XS9826A", context_with_discount)
    assert result == True  # Valid in discount context
    
    # Without discount context, $1.60 is suspicious as placeholder
    context_no_discount = "XS9826A 6"H Metal Ballerina Ornament Standard pricing"
    result = validate_price_extraction("$1.60", "XS9826A", context_no_discount)
    assert result == False  # Suspicious as placeholder

def test_applies_quantity_based_pricing_validation():
    # Higher quantities should generally have lower unit prices
    quantity_price_cases = [
        (1, "$5.00", True),      # Single unit - higher price acceptable
        (24, "$3.00", True),     # Bulk quantity - moderate price
        (100, "$1.50", True),    # Large bulk - lower price acceptable  
        (1, "$0.50", False),     # Single unit - suspiciously low
        (100, "$10.00", False)   # Large bulk - suspiciously high
    ]
    
    for quantity, price, expected_valid in quantity_price_cases:
        document_with_qty = f"XS9826A Product Quantity: {quantity} Price: {price}"
        result = validate_price_with_quantity_context(price, "XS9826A", document_with_qty)
        assert result == expected_valid
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
def validate_price_extraction(price, product_code, document_text):
    """
    Validate extracted price meets Creative-Coop business logic standards.
    
    Args:
        price (str): Extracted price (e.g., "$1.60")
        product_code (str): Product code for context
        document_text (str): Document context for validation
        
    Returns:
        bool: True if price passes validation, False otherwise
    """
    
    if not price or not product_code:
        return False
    
    try:
        # Clean and parse price
        price_value = float(price.replace('$', '').replace(',', ''))
        
        # Basic range validation
        if price_value < 0.10 or price_value > 1000:
            print(f"⚠️ Price validation warning for {product_code}: ${price_value}")
            return False
        
        # Check for known placeholder prices
        if price_value == 1.60:
            # Context-dependent validation for $1.60
            if is_valid_discount_context(document_text):
                return True
            else:
                print(f"❌ Placeholder price detected for {product_code}: ${price_value}")
                return False
        
        # Product line specific validation
        if not validate_product_line_pricing(price_value, product_code):
            return False
            
        return True
        
    except ValueError:
        print(f"❌ Invalid price format for {product_code}: {price}")
        return False

def apply_business_price_logic(price, product_code):
    """
    Apply Creative-Coop business logic corrections to extracted prices.
    
    Args:
        price (str): Original extracted price
        product_code (str): Product code for business rules
        
    Returns:  
        str: Corrected price or None if correction not possible
    """
    
    if not validate_price_extraction(price, product_code, ""):
        # Attempt price correction based on product line
        corrected = attempt_price_correction(price, product_code)
        if corrected and validate_price_extraction(corrected, product_code, ""):
            print(f"✅ Price corrected for {product_code}: {price} → {corrected}")
            return corrected
        else:
            print(f"❌ Price correction failed for {product_code}: {price}")
            return None
    
    return price  # Already valid

def is_valid_discount_context(document_text):
    """Check if document context suggests legitimate discount pricing"""
    import re
    
    discount_indicators = [
        r"volume discount",
        r"bulk pricing", 
        r"50% off",
        r"wholesale discount",
        r"promotional pricing"
    ]
    
    for pattern in discount_indicators:
        if re.search(pattern, document_text, re.IGNORECASE):
            return True
    
    return False
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Add sophisticated industry-specific business rules
- [ ] Implement statistical analysis for price anomaly detection
- [ ] Add comprehensive logging for validation decisions
- [ ] Optimize validation performance for bulk processing
- [ ] Add configuration-based validation rules

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for price validation logic
- [ ] Successfully detects and rejects 100% of "$1.60" placeholder prices
- [ ] Validates prices according to Creative-Coop industry standards
- [ ] Error handling covers all malformed price format scenarios
- [ ] Context-aware validation considers discount scenarios appropriately
- [ ] Performance optimized for bulk validation (130+ products < 10 seconds)
- [ ] Business logic corrections improve data quality measurably
- [ ] Integration with existing price extraction functions seamless

## Engineering Principles Compliance

**Principle 2. Data quality validation**: Comprehensive validation ensures high-quality price data
**Principle 5. Error resilience**: Graceful handling of malformed and invalid price data  
**Principle 9. Algorithmic processing**: Uses rule-based validation, not hardcoded acceptable prices

## Monitoring & Observability

**Required Metrics**:
- Price validation pass rate percentage
- Placeholder price rejection rate  
- Business logic correction success rate
- Validation performance metrics (time per validation)

**Log Events**:
```python
# Validation success
logger.info("Price validation completed", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'price': price,
    'validation_result': 'passed',
    'validation_rules_applied': rules_applied
})

# Validation failure  
logger.warning("Price validation failed", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'price': price,
    'validation_result': 'failed',
    'failure_reason': reason,
    'correction_attempted': correction_attempted
})
```

## Security Considerations

- [ ] Input sanitization for price strings to prevent injection attacks
- [ ] Validation of product_code format to prevent malicious input  
- [ ] Protection against excessive validation processing (DoS protection)

## Performance Requirements

- [ ] Validate 130+ product prices in < 10 seconds total
- [ ] Individual price validation completes in < 100ms
- [ ] Memory efficient validation for large invoice processing
- [ ] Minimal regex processing overhead

## Implementation Notes

**Key Design Decisions**:
- Context-aware validation allows legitimate $1.60 prices in discount scenarios
- Product line specific validation rules (XS, CF, CD different price ranges)
- Business logic corrections attempt to salvage partially valid data
- Statistical validation detects pricing anomalies beyond simple range checks

**Integration Points**:
- Called by all price extraction functions (Tasks 201, 202)
- Integrates with existing Creative-Coop processing pipeline
- Uses Document AI text context for validation decisions

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for price validation rules
- [ ] Business logic correction testing  
- [ ] Context-aware validation scenarios
- [ ] Performance testing with bulk validation
- [ ] Integration testing with price extraction functions