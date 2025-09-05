## Task 07: Multi-Tier Quantity Extraction Integration - Creative-Coop

### TDD Cycle Overview
**RED**: Write failing tests for multi-tier fallback quantity extraction system
**GREEN**: Integrate tabular parser with existing pattern-based extraction
**REFACTOR**: Optimize tier selection logic and eliminate code duplication

### Test Requirements
- [ ] Unit tests for tier prioritization and fallback logic
- [ ] Integration tests with both tabular and pattern-based Creative-Coop formats
- [ ] Error handling tests for tier failures and cascading fallbacks
- [ ] Performance tests ensuring minimal overhead for tier selection
- [ ] Backward compatibility tests with existing D-code Creative-Coop invoices
- [ ] Edge case tests for mixed format invoices with partial data

### Implementation Steps (Red-Green-Refactor)

#### Step 1: RED - Write Failing Tests
```python
# Test file: test_scripts/test_multi_tier_quantity_extraction.py
import pytest
from unittest.mock import Mock, patch
from main import extract_creative_coop_quantity_improved, extract_quantity_from_table_columns

def test_tier1_tabular_extraction_success():
    """Test Tier 1 (tabular) extraction succeeds and skips lower tiers"""
    # Arrange - tabular format should be detected and processed
    tabular_text = "XS9826A 191009727774 6\"H Metal Ballerina 24 0 0 24 each 2.00 1.60 38.40"
    
    # Act
    result = extract_creative_coop_quantity_improved(tabular_text, "XS9826A")
    
    # Assert
    assert result == 24

def test_tier2_pattern_fallback_when_tabular_fails():
    """Test Tier 2 (pattern-based) fallback when tabular parsing fails"""
    # Arrange - old Creative-Coop format that tabular parser can't handle
    pattern_text = "DF6802 8 0 lo each $12.50 $100.00 description continues..."
    
    # Act
    result = extract_creative_coop_quantity_improved(pattern_text, "DF6802")
    
    # Assert
    assert result == 8  # Should extract from "8 0 lo each" pattern

def test_tier3_context_fallback_when_patterns_fail():
    """Test Tier 3 (context-aware) fallback when both higher tiers fail"""
    # Arrange - complex format requiring context analysis
    context_text = """
    Product: XS9826A
    Description: 6"H Metal Ballerina Ornament
    Ordered: 24 units
    Status: Available
    """
    
    # Act
    result = extract_creative_coop_quantity_improved(context_text, "XS9826A")
    
    # Assert
    assert result == 24  # Should extract from "Ordered: 24 units"

def test_all_tiers_fail_returns_none():
    """Test that None is returned when all tiers fail"""
    # Arrange - text with no extractable quantity
    no_quantity_text = "XS9826A Some description without any numbers"
    
    # Act
    result = extract_creative_coop_quantity_improved(no_quantity_text, "XS9826A")
    
    # Assert
    assert result is None

def test_tier_performance_early_exit():
    """Test that successful tier exits early without trying lower tiers"""
    # Arrange
    mixed_text = """
    XS9826A 191009727774 Ballerina 24 0 0 24 each 2.00  # Tabular format
    DF6802 8 0 lo each $12.50  # Pattern format
    """
    
    # Mock lower tiers to track if they're called
    with patch('main.extract_quantity_from_patterns') as mock_patterns:
        with patch('main.extract_quantity_from_context') as mock_context:
            # Act
            result = extract_creative_coop_quantity_improved(mixed_text, "XS9826A")
            
            # Assert
            assert result == 24
            # Lower tiers should not be called since tabular succeeded
            mock_patterns.assert_not_called()
            mock_context.assert_not_called()

def test_backward_compatibility_existing_invoices():
    """Test that existing D-code Creative-Coop invoices still work"""
    # Arrange - existing working format from previous invoices
    existing_format = """
    DF6802 8 0 lo each $12.50 $100.00
    ST1234 6 0 Set $8.00 $48.00
    """
    
    # Act & Assert - both should work via pattern fallback
    assert extract_creative_coop_quantity_improved(existing_format, "DF6802") == 8
    assert extract_creative_coop_quantity_improved(existing_format, "ST1234") == 6

def test_cs_error2_specific_products():
    """Test specific products from CS003837319_Error 2.PDF"""
    cs_error2_sample = """
    XS9826A 191009727774 6"H Metal Ballerina Ornament, 24 0 0 24 each 2.00 1.60 38.40
    XS8911A 191009710615 4-3/4"L x 3-1/2"W x 10"H Metal 12 0 0 0 each 10.00 8.00 0.00
    XS9482 191009714712 8.25"H Wood Shoe Ornament 12 0 0 12 each 3.50 2.80 33.60
    """
    
    # Act & Assert
    assert extract_creative_coop_quantity_improved(cs_error2_sample, "XS9826A") == 24
    assert extract_creative_coop_quantity_improved(cs_error2_sample, "XS8911A") == 12
    assert extract_creative_coop_quantity_improved(cs_error2_sample, "XS9482") == 12

def test_integration_with_process_creative_coop_document():
    """Test integration with main Creative-Coop processing function"""
    # This test ensures the new quantity extraction works with the full pipeline
    # Will be implemented after integration is complete
    pass
```

#### Step 2: GREEN - Minimal Implementation
```python
# In main.py - Replace existing extract_creative_coop_quantity function
def extract_creative_coop_quantity_improved(text, product_code):
    """
    Multi-tier quantity extraction for Creative-Coop invoices.
    
    Tier 1: Tabular column parsing (NEW) - for structured CS003837319_Error 2.PDF format
    Tier 2: Pattern-based extraction (EXISTING) - for "8 0 lo each" format  
    Tier 3: Context-aware parsing - for complex mixed formats
    
    Args:
        text (str): Invoice text containing product information
        product_code (str): Product code to extract quantity for
        
    Returns:
        int: Extracted quantity, None if extraction fails
    """
    if product_code not in text:
        return None
    
    # Tier 1: Try tabular extraction first (handles CS003837319_Error 2.PDF)
    qty = extract_quantity_from_table_columns(text, product_code)
    if qty is not None:
        print(f"Tier 1 (Tabular): Extracted qty {qty} for {product_code}")
        return qty
    
    # Tier 2: Fallback to existing pattern-based extraction
    qty = extract_quantity_from_patterns(text, product_code)
    if qty is not None:
        print(f"Tier 2 (Pattern): Extracted qty {qty} for {product_code}")
        return qty
    
    # Tier 3: Context-aware extraction for complex cases
    qty = extract_quantity_from_context(text, product_code)
    if qty is not None:
        print(f"Tier 3 (Context): Extracted qty {qty} for {product_code}")
        return qty
    
    print(f"All tiers failed: No quantity found for {product_code}")
    return None

def extract_quantity_from_patterns(text, product_code):
    """
    Tier 2: Pattern-based quantity extraction (existing logic).
    
    Handles formats like:
    - "DF6802 8 0 lo each $12.50"
    - "ST1234 6 0 Set $8.00"
    """
    # Move existing extract_creative_coop_quantity logic here
    if product_code not in text:
        return None

    # Find the product code position
    product_pos = text.find(product_code)

    # Creative-Coop quantity patterns (existing patterns)
    qty_patterns = [
        r"\b(\d+)\s+\d+\s+lo\s+each\b",  # "8 0 lo each"
        r"\b(\d+)\s+\d+\s+Set\b",        # "6 0 Set"  
        r"\b(\d+)\s+\d+\s+each\b",       # "24 0 each"
    ]

    # Look for patterns near the product code
    search_window = text[product_pos:product_pos + 200]
    
    for pattern in qty_patterns:
        import re
        match = re.search(pattern, search_window)
        if match:
            return int(match.group(1))
    
    return None

def extract_quantity_from_context(text, product_code):
    """
    Tier 3: Context-aware quantity extraction for complex formats.
    
    Handles formats like:
    - "Product: XS9826A\nOrdered: 24 units"
    - Multi-line with quantity keywords
    """
    if product_code not in text:
        return None
    
    import re
    
    # Find product code position
    product_pos = text.find(product_code)
    
    # Search window around product code
    window_start = max(0, product_pos - 100)
    window_end = min(len(text), product_pos + 300)
    search_window = text[window_start:window_end]
    
    # Context patterns for quantity extraction
    context_patterns = [
        r"Ordered:\s*(\d+)",           # "Ordered: 24"
        r"Qty.*?:\s*(\d+)",            # "Qty Ord: 24"
        r"Quantity.*?(\d+)",           # "Quantity 24"
        r"\b(\d+)\s*units?\b",         # "24 units"
        r"\b(\d+)\s*pieces?\b",        # "24 pieces"
    ]
    
    for pattern in context_patterns:
        match = re.search(pattern, search_window, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None

# Update the main Creative-Coop processing to use new function
def process_creative_coop_document(document):
    """Update to use improved quantity extraction"""
    # ... existing code ...
    
    # Replace calls to extract_creative_coop_quantity with:
    # quantity = extract_creative_coop_quantity_improved(entity.mention_text, product_code)
    
    # ... rest of existing logic ...
```

#### Step 3: REFACTOR - Improve Design
```python
def extract_creative_coop_quantity_improved(text, product_code):
    """
    Multi-tier quantity extraction with improved error handling and performance.
    """
    if not text or not product_code or product_code not in text:
        return None
    
    # Define extraction strategies with metadata
    extraction_tiers = [
        {
            'name': 'Tabular',
            'function': extract_quantity_from_table_columns,
            'description': 'Column-based parsing for structured invoices'
        },
        {
            'name': 'Pattern', 
            'function': extract_quantity_from_patterns,
            'description': 'Regex pattern matching for formatted text'
        },
        {
            'name': 'Context',
            'function': extract_quantity_from_context, 
            'description': 'Context-aware extraction for complex formats'
        }
    ]
    
    # Try each tier in order
    for i, tier in enumerate(extraction_tiers, 1):
        try:
            qty = tier['function'](text, product_code)
            if qty is not None:
                print(f"Tier {i} ({tier['name']}): Extracted qty {qty} for {product_code}")
                return qty
        except Exception as e:
            print(f"Tier {i} ({tier['name']}) failed for {product_code}: {e}")
            continue
    
    print(f"All {len(extraction_tiers)} tiers failed: No quantity found for {product_code}")
    return None

# Add performance monitoring
def extract_quantity_with_timing(text, product_code):
    """Wrapper with performance monitoring"""
    import time
    start_time = time.time()
    
    result = extract_creative_coop_quantity_improved(text, product_code)
    
    end_time = time.time()
    processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"Quantity extraction for {product_code}: {result} in {processing_time:.2f}ms")
    return result
```

### Acceptance Criteria (Test-Driven)

- [ ] All unit tests pass for multi-tier extraction logic
- [ ] Integration tests verify tier fallback behavior works correctly
- [ ] Backward compatibility: All existing Creative-Coop invoices still work
- [ ] CS003837319_Error 2.PDF: Extract quantities via Tier 1 (tabular parsing)
- [ ] Performance: Tier selection adds <10ms overhead per product
- [ ] Error handling: Graceful degradation when individual tiers fail
- [ ] Logging: Clear indication of which tier succeeded for each product

### Engineering Principles Applied
- **Principle 7**: Multi-tier resilience with graceful fallback
- **Principle 8**: Context-aware processing adapts to invoice format
- **Principle 9**: Performance optimization with early exit strategies
- **Principle 10**: Comprehensive error handling and structured logging

### Code Review Checklist

- [ ] Tests written before implementation (TDD)
- [ ] All tier fallback scenarios covered by tests
- [ ] Error handling follows graceful degradation patterns
- [ ] Performance monitoring included for tier selection overhead
- [ ] Backward compatibility verified with existing invoice formats
- [ ] Integration with main Creative-Coop processing function tested
- [ ] Structured logging provides clear debugging information

### Integration Points
- **Update**: `process_creative_coop_document()` to use `extract_creative_coop_quantity_improved()`
- **Replace**: All calls to `extract_creative_coop_quantity()` with new multi-tier function  
- **Maintain**: Existing function signatures for backward compatibility
- **Add**: Performance monitoring and structured logging for tier usage analytics

### Success Metrics
- **CS003837319_Error 2.PDF**: 95%+ quantity extraction via Tier 1 (tabular)
- **Existing D-code invoices**: 100% backward compatibility via Tier 2 (patterns)
- **Performance**: <10ms additional overhead per product for tier selection
- **Reliability**: Graceful handling when individual tiers fail