## Task 06: Tabular Quantity Column Parser - Creative-Coop

### TDD Cycle Overview
**RED**: Write failing tests for column-based quantity extraction from Creative-Coop tabular format
**GREEN**: Implement minimal tabular parsing algorithm to extract quantities by column position
**REFACTOR**: Optimize parsing logic and handle edge cases

### Test Requirements
- [ ] Unit tests for tabular column parsing with known product-quantity mappings
- [ ] Integration tests with CS003837319_Error 2.PDF text format
- [ ] Error handling tests for malformed table data
- [ ] Edge case tests for missing columns, extra whitespace, multi-line descriptions
- [ ] Performance tests ensuring <500ms parsing time for large invoices
- [ ] Boundary tests for empty quantities, zero quantities, and non-numeric values

### Implementation Steps (Red-Green-Refactor)

#### Step 1: RED - Write Failing Tests
```python
# Test file: test_scripts/test_tabular_quantity_parser.py
import pytest
from unittest.mock import Mock, patch
from main import extract_quantity_from_table_columns

def test_extract_quantity_from_table_columns_basic_case():
    """Test basic quantity extraction from tabular Creative-Coop format"""
    # Arrange
    sample_text = """
    XS9826A   191009727774   6"H Metal Ballerina Ornament,   24  0  0  24  each  2.00  1.60  38.40
    XS8911A   191009710615   4-3/4"L x 3-1/2"W x 10"H Metal  12  0  0  0   each  10.00 8.00  0.00
    """
    
    # Act & Assert
    assert extract_quantity_from_table_columns(sample_text, "XS9826A") == 24
    assert extract_quantity_from_table_columns(sample_text, "XS8911A") == 12

def test_extract_quantity_handles_zero_quantities():
    """Test handling of products with zero ordered quantities"""
    sample_text = """
    XS8911A   191009710615   4-3/4"L x 3-1/2"W x 10"H Metal  0   0  0  0   each  10.00 8.00  0.00
    XS9482    191009714712   8.25"H Wood Shoe Ornament        12  0  0  12  each  3.50  2.80  33.60
    """
    
    assert extract_quantity_from_table_columns(sample_text, "XS8911A") == 0
    assert extract_quantity_from_table_columns(sample_text, "XS9482") == 12

def test_extract_quantity_multiline_descriptions():
    """Test products with multi-line descriptions that break column alignment"""
    sample_text = """
    XS9840A   191009727910   2-1/2"H 3-1/4"H Metal &          24  14  0  24  each  3.50  2.80  67.20
                             Tariff Surcharge                   
    XS8185    191009721666   20"Lx12"H Cotton Lumbar Pillow   16  0   0  16  each  15.00 12.00 192.00
    """
    
    assert extract_quantity_from_table_columns(sample_text, "XS9840A") == 24
    assert extract_quantity_from_table_columns(sample_text, "XS8185") == 16

def test_extract_quantity_product_not_found():
    """Test behavior when product code is not in text"""
    sample_text = "XS9826A   191009727774   Description   24  0  0  24  each  2.00  1.60  38.40"
    
    assert extract_quantity_from_table_columns(sample_text, "NOTFOUND") is None

def test_extract_quantity_malformed_table():
    """Test error handling for malformed table data"""
    sample_text = """
    XS9826A   incomplete row data
    XS8911A   191009710615   Description but missing numbers
    """
    
    assert extract_quantity_from_table_columns(sample_text, "XS9826A") is None
    assert extract_quantity_from_table_columns(sample_text, "XS8911A") is None

def test_extract_quantity_performance_large_invoice():
    """Test performance with large invoice text (>20KB)"""
    # Create large sample with 100+ products
    large_text = ""
    for i in range(100):
        large_text += f"XS{i:04d}A   191009727{i:03d}   Test Product {i}   {i+1}  0  0  {i+1}  each  2.00  1.60  38.40\n"
    
    import time
    start_time = time.time()
    result = extract_quantity_from_table_columns(large_text, "XS0050A")
    end_time = time.time()
    
    assert result == 51  # i=50, quantity = i+1 = 51
    assert (end_time - start_time) < 0.5  # Less than 500ms

def test_extract_quantity_real_cs_error2_format():
    """Test with actual CS003837319_Error 2.PDF format patterns"""
    actual_format = """
    XS9826A
    191009727774
    6"H Metal Ballerina Ornament,
    24
    0
    0
    24
    each
    2.00
    1.60
    38.40
    """
    
    # Should extract 24 as the ordered quantity
    assert extract_quantity_from_table_columns(actual_format, "XS9826A") == 24
```

#### Step 2: GREEN - Minimal Implementation
```python
# In main.py
def extract_quantity_from_table_columns(text, product_code):
    """
    Extract quantity from tabular Creative-Coop format by column position.
    
    Expected format after UPC:
    [Product_Code] [UPC] [Description...] [Qty_Ord] [Qty_Alloc] [Qty_Shipped] [Qty_BkOrd] [Unit] [Prices...]
    
    Args:
        text (str): Invoice text containing product line
        product_code (str): Product code to find (e.g., "XS9826A")
        
    Returns:
        int: Ordered quantity, None if not found or parsing fails
    """
    if product_code not in text:
        return None
    
    try:
        # Find the line containing the product code
        lines = text.split('\n')
        product_line = None
        
        for line in lines:
            if product_code in line:
                product_line = line
                break
        
        if not product_line:
            return None
        
        # Split by whitespace and find quantity after UPC
        parts = product_line.split()
        
        # Find product code position
        product_index = -1
        for i, part in enumerate(parts):
            if product_code == part:
                product_index = i
                break
        
        if product_index == -1:
            return None
        
        # Look for UPC (12-digit number) after product code
        upc_index = -1
        for i in range(product_index + 1, len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 12:
                upc_index = i
                break
        
        if upc_index == -1:
            return None
        
        # Quantity should be first numeric value after description
        # Skip description parts and find first integer
        for i in range(upc_index + 1, len(parts)):
            if parts[i].isdigit():
                return int(parts[i])
        
        return None
        
    except (ValueError, IndexError):
        return None
```

#### Step 3: REFACTOR - Improve Design
```python
def extract_quantity_from_table_columns(text, product_code):
    """
    Extract quantity from Creative-Coop tabular format with improved parsing.
    
    Handles multiple formats:
    1. Single line: "XS9826A 191009727774 Description 24 0 0 24 each 2.00 1.60 38.40"
    2. Multi-line: Product code and data on separate lines
    3. Wrapped descriptions: Handle text wrapping in descriptions
    """
    if product_code not in text:
        return None
    
    try:
        # Strategy 1: Try single-line parsing first
        qty = _parse_single_line_quantity(text, product_code)
        if qty is not None:
            return qty
        
        # Strategy 2: Try multi-line parsing for formatted invoices
        return _parse_multiline_quantity(text, product_code)
        
    except Exception as e:
        # Log parsing error but don't fail completely
        print(f"Warning: Quantity parsing failed for {product_code}: {e}")
        return None

def _parse_single_line_quantity(text, product_code):
    """Parse quantity from single line format"""
    lines = text.split('\n')
    for line in lines:
        if product_code in line and len(line.split()) >= 8:  # Minimum expected columns
            parts = line.split()
            # Find quantity pattern: first integer after UPC that's followed by more integers
            return _extract_quantity_from_parts(parts, product_code)
    return None

def _parse_multiline_quantity(text, product_code):
    """Parse quantity from multi-line Creative-Coop format"""
    lines = text.split('\n')
    product_line_index = -1
    
    # Find product code line
    for i, line in enumerate(lines):
        if product_code == line.strip():
            product_line_index = i
            break
    
    if product_line_index == -1:
        return None
    
    # Look for quantity in next 10 lines
    for i in range(product_line_index + 1, min(product_line_index + 10, len(lines))):
        line = lines[i].strip()
        if line.isdigit() and int(line) > 0:  # First positive integer is likely quantity
            return int(line)
    
    return None

def _extract_quantity_from_parts(parts, product_code):
    """Extract quantity from split line parts"""
    try:
        product_index = parts.index(product_code)
        
        # Find UPC (12-digit number) after product code
        upc_index = -1
        for i in range(product_index + 1, len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 12:
                upc_index = i
                break
        
        if upc_index == -1:
            return None
        
        # Find first integer after UPC (skipping description words)
        for i in range(upc_index + 1, len(parts)):
            if parts[i].isdigit():
                return int(parts[i])
        
        return None
        
    except (ValueError, IndexError):
        return None
```

### Acceptance Criteria (Test-Driven)

- [ ] All unit tests pass (RED → GREEN achieved)
- [ ] Code coverage ≥ 95% for new quantity parsing functions
- [ ] Integration tests verify CS003837319_Error 2.PDF quantity extraction
- [ ] Performance tests confirm <500ms parsing time for large invoices
- [ ] Error handling tested for malformed table data, missing columns
- [ ] Edge cases handled: zero quantities, multi-line descriptions, extra whitespace
- [ ] Logging includes structured data for parsing success/failure rates

### Engineering Principles Applied
- **Principle 1**: Algorithmic pattern recognition (no hardcoded product-quantity mappings)
- **Principle 2**: TDD methodology with comprehensive test coverage
- **Principle 3**: Graceful error handling with detailed logging
- **Principle 4**: Performance optimization with early exit patterns
- **Principle 7**: Multi-strategy parsing (single-line, multi-line fallbacks)
- **Principle 8**: Context-aware parsing based on column position

### Code Review Checklist

- [ ] Tests written before implementation (TDD)
- [ ] All acceptance criteria covered by tests
- [ ] Error handling follows graceful degradation patterns
- [ ] Logging is structured and includes parsing context
- [ ] No hardcoded product-quantity values (algorithmic extraction only)
- [ ] Performance benchmarks included for large invoice processing
- [ ] Edge cases tested: malformed data, missing columns, zero quantities
- [ ] Integration compatibility with existing Creative-Coop processing functions

### Success Metrics
- **CS003837319_Error 2.PDF**: Extract quantities for XS9826A (24), XS8911A (12), XS9482 (12), etc.
- **Performance**: Process 100+ product invoice in <500ms
- **Accuracy**: 95%+ quantity extraction success rate on test dataset
- **Reliability**: Graceful handling of edge cases without breaking invoice processing