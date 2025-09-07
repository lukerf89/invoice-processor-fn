## Task 210: Enhanced Description Extraction - UPC Integration and Quality Enhancement

**Status**: Pending
**Priority**: High
**Estimated Duration**: 3-4 hours
**Dependencies**: Phase 01 description processing foundation, UPC extraction capabilities
**Engineering Principles Applied**: 2 (Data quality validation), 8 (Context-aware extraction), 9 (Algorithmic processing)

## Description

Implement sophisticated description extraction system for Creative-Coop invoices that integrates UPC codes with product descriptions to achieve 95% completeness. Focuses on eliminating "Traditional D-code format" placeholders and providing comprehensive product information by combining multiple data sources.

## Context

- **Enables**: Complete product descriptions for inventory management, customer service, and business operations
- **Integration Points**: Existing Creative-Coop processing, UPC extraction functions, description cleaning logic
- **Files to Create/Modify**:
  - `main.py` - `extract_enhanced_product_description()`, `integrate_upc_with_description()`
  - `main.py` - `extract_description_from_product_context()`, `enhance_description_completeness()`
  - `test_scripts/test_enhanced_description_extraction.py` - Enhanced description extraction tests

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_enhanced_description_extraction.py` - Enhanced description extraction tests

**Required Test Categories**:

#### Happy Path Tests
```python
def test_extracts_enhanced_descriptions_with_upc_integration():
    # Arrange - Document text with product and UPC information
    document_text = """
    XS9826A 191009727774 6"H Metal Ballerina Ornament
    Product details and pricing information
    XS8911A 191009710615 4-3/4"L x 3-1/2"W Cotton Lumbar Pillow
    Additional product information
    """

    # Act - Extract enhanced descriptions with UPC integration
    desc_xs9826a = extract_enhanced_product_description(document_text, "XS9826A", "191009727774")
    desc_xs8911a = extract_enhanced_product_description(document_text, "XS8911A", "191009710615")

    # Assert - Should integrate UPC with description
    assert "XS9826A" in desc_xs9826a
    assert "191009727774" in desc_xs9826a  # UPC integrated
    assert "Metal Ballerina Ornament" in desc_xs9826a

    assert "XS8911A" in desc_xs8911a
    assert "191009710615" in desc_xs8911a  # UPC integrated
    assert "Cotton Lumbar Pillow" in desc_xs8911a

def test_processes_cs003837319_descriptions_comprehensively():
    # Load CS003837319_Error 2.PDF test data
    cs_document_text = load_test_document('CS003837319_Error_2_docai_output.json')

    # Test specific known products for description quality
    test_products = {
        "XS9826A": {
            "expected_upc": "191009727774",
            "expected_keywords": ["Metal", "Ballerina", "Ornament"],
            "expected_format": "XS9826A - UPC: 191009727774 - 6\"H Metal Ballerina Ornament"
        },
        "XS9649A": {
            "expected_upc": "191009725688",
            "expected_keywords": ["Paper", "Mache", "8\"H"],
            "expected_format": "XS9649A - UPC: 191009725688 - 8\"H x 6.5\"W x 4\"D Paper Mache"
        }
    }

    for product_code, expectations in test_products.items():
        # Act
        description = extract_enhanced_product_description(
            cs_document_text,
            product_code,
            expectations["expected_upc"]
        )

        # Assert - Should meet quality standards
        assert description != "Traditional D-code format"  # No placeholder
        assert product_code in description  # Product code included
        assert expectations["expected_upc"] in description  # UPC included

        # Should contain expected keywords
        for keyword in expectations["expected_keywords"]:
            assert keyword in description

def test_integrates_upc_with_description_correctly():
    # Test UPC integration with various description formats
    integration_cases = [
        {
            "document_text": "XS9826A Beautiful Metal Ornament for holidays",
            "product_code": "XS9826A",
            "upc_code": "191009727774",
            "expected": "XS9826A - UPC: 191009727774 - Beautiful Metal Ornament for holidays"
        },
        {
            "document_text": "CF1234A Premium Cotton Product",
            "product_code": "CF1234A",
            "upc_code": "123456789012",
            "expected": "CF1234A - UPC: 123456789012 - Premium Cotton Product"
        }
    ]

    for case in integration_cases:
        # Act
        result = integrate_upc_with_description(
            case["document_text"],
            case["product_code"],
            case["upc_code"]
        )

        # Assert
        assert result == case["expected"]

def test_enhances_description_completeness():
    # Test description completeness enhancement
    incomplete_description = "XS9826A Metal"
    document_context = """
    XS9826A 191009727774 6"H Metal Ballerina Ornament
    Beautiful decorative piece for holiday display
    Premium quality construction
    """

    # Act - Enhance description completeness
    enhanced = enhance_description_completeness(incomplete_description, "XS9826A", document_context)

    # Assert - Should be more complete
    assert len(enhanced) > len(incomplete_description)
    assert "Ballerina" in enhanced
    assert "Ornament" in enhanced
    assert "6\"H" in enhanced or "Metal" in enhanced
```

#### Error Handling Tests
```python
def test_handles_missing_upc_codes_gracefully():
    # Test when UPC codes are not available
    document_text = "XS9826A 6\"H Metal Ballerina Ornament without UPC"

    # Act - Extract description without UPC
    description = extract_enhanced_product_description(document_text, "XS9826A", None)

    # Assert - Should provide description without UPC
    assert "XS9826A" in description
    assert "Metal Ballerina Ornament" in description
    assert "UPC:" not in description  # No UPC section when not available

def test_handles_malformed_description_data():
    # Test handling of malformed or incomplete description data
    malformed_cases = [
        "XS9826A |||||| corrupted data",  # Corrupted separators
        "XS9826A \n\n\n incomplete",      # Excessive whitespace
        "XS9826A 123 abc def ghi",        # Random characters
        ""                                # Empty string
    ]

    for malformed_text in malformed_cases:
        # Act
        result = extract_enhanced_product_description(malformed_text, "XS9826A", "191009727774")

        # Assert - Should handle gracefully
        if malformed_text:
            assert "XS9826A" in result  # Should at least include product code
            assert len(result) > 0      # Should not be empty
        else:
            assert result == "XS9826A - UPC: 191009727774 - Product description not available"

def test_handles_special_characters_in_descriptions():
    # Test handling of special characters and formatting
    special_char_cases = [
        ('XS9826A 6"H Metal Ballerina\'s Ornament', "quotes and apostrophes"),
        ('XS8911A 4-3/4"L × 3-1/2"W Product', "fractions and symbols"),
        ('CF1234A Café & Müller Brand', "accented characters"),
        ('CD5678B 50% Off Special Product', "percentage symbols")
    ]

    for text_with_special, description in special_char_cases:
        product_code = text_with_special.split()[0]

        # Act
        result = extract_enhanced_product_description(text_with_special, product_code, "123456789012")

        # Assert - Should preserve special characters
        assert product_code in result
        assert "123456789012" in result
        # Should handle special characters without crashing
        assert len(result) > 0

def test_handles_extremely_long_descriptions():
    # Test handling of very long product descriptions
    long_description = "XS9826A " + "Very long product description " * 50  # ~1500 characters

    # Act
    result = extract_enhanced_product_description(long_description, "XS9826A", "191009727774")

    # Assert - Should handle long descriptions appropriately
    assert "XS9826A" in result
    assert "191009727774" in result
    # Should truncate or handle long descriptions reasonably
    assert len(result) <= 500  # Reasonable maximum length
```

#### Edge Case Tests
```python
def test_extracts_descriptions_from_various_document_contexts():
    # Test description extraction from different document contexts
    context_cases = [
        {
            "context": "Tabular format: XS9826A | 191009727774 | 6\"H Metal Ballerina Ornament | 24 | $1.60",
            "product": "XS9826A",
            "expected": "Metal Ballerina Ornament"
        },
        {
            "context": "Multi-line format:\nXS8911A\n191009710615\n4-3/4\"L x 3-1/2\"W Cotton Pillow",
            "product": "XS8911A",
            "expected": "Cotton Pillow"
        },
        {
            "context": "Paragraph format: The XS9482 (UPC: 191009714712) is an 8.25\"H Wood Shoe Ornament",
            "product": "XS9482",
            "expected": "Wood Shoe Ornament"
        }
    ]

    for case in context_cases:
        # Act
        description = extract_description_from_product_context(case["context"], case["product"])

        # Assert
        assert case["expected"] in description

def test_validates_description_quality_standards():
    # Test description quality validation
    quality_test_cases = [
        ("XS9826A - UPC: 191009727774 - 6\"H Metal Ballerina Ornament", True),   # High quality
        ("XS9826A Metal Ornament", False),                                      # Missing UPC
        ("Traditional D-code format", False),                                   # Placeholder
        ("XS9826A - UPC: 191009727774 - Complete Product Description", True),  # Complete
        ("", False)                                                            # Empty
    ]

    for description, expected_quality in quality_test_cases:
        # Act
        is_quality = validate_description_quality(description, "XS9826A")

        # Assert
        assert is_quality == expected_quality

def test_handles_upc_extraction_from_document():
    # Test automatic UPC extraction when not provided
    document_with_upcs = """
    Product Listing:
    XS9826A 191009727774 6"H Metal Ballerina Ornament
    XS8911A 191009710615 Cotton Lumbar Pillow
    XS9482 191009714712 Wood Shoe Ornament
    """

    # Act - Extract description with automatic UPC finding
    description = extract_enhanced_product_description(document_with_upcs, "XS9826A", None)

    # Assert - Should find and integrate UPC automatically
    assert "XS9826A" in description
    assert "191009727774" in description  # Should find UPC automatically
    assert "Metal Ballerina Ornament" in description

def test_optimizes_description_extraction_performance():
    # Test performance optimization for description extraction
    import time

    # Create large document text
    large_document = generate_large_document_with_products(500)  # 500 products

    start_time = time.time()

    # Act - Extract descriptions for multiple products
    descriptions = []
    for i in range(10):  # Test 10 products
        product_code = f"XS{i:04d}A"
        description = extract_enhanced_product_description(large_document, product_code, None)
        descriptions.append(description)

    end_time = time.time()
    extraction_time = end_time - start_time

    # Assert - Should complete within reasonable time
    assert extraction_time < 5.0  # 10 descriptions in < 5 seconds
    assert len(descriptions) == 10
    assert all(desc for desc in descriptions)  # All should have content
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
def extract_enhanced_product_description(document_text, product_code, upc_code=None):
    """
    Extract complete product descriptions with UPC integration for Creative-Coop invoices.

    Args:
        document_text (str): Full document text containing product information
        product_code (str): Product code to find description for (e.g., "XS9826A")
        upc_code (str, optional): UPC code to integrate with description

    Returns:
        str: Enhanced description with UPC integration
    """

    if not document_text or not product_code:
        return f"{product_code} - Product description not available"

    # Primary extraction: Find description in product context
    description = extract_description_from_product_context(document_text, product_code)

    # If no UPC provided, try to find it in document
    if not upc_code:
        upc_code = extract_upc_for_product(document_text, product_code)

    # Integrate UPC with description
    if upc_code:
        enhanced_description = f"{product_code} - UPC: {upc_code} - {description}"
    else:
        enhanced_description = f"{product_code} - {description}"

    # Clean and validate description
    cleaned_description = clean_description_artifacts(enhanced_description)

    # Enhance completeness if needed
    if len(cleaned_description) < 20 or "Traditional D-code format" in cleaned_description:
        cleaned_description = enhance_description_completeness(cleaned_description, product_code, document_text)

    return cleaned_description

def extract_description_from_product_context(document_text, product_code):
    """Extract product description from various document contexts"""
    import re

    # Pattern 1: Tabular format with separators
    tabular_pattern = rf"{re.escape(product_code)}\s*[|\s]+[\d\s]*\s*([A-Za-z0-9\"'\-\s/&×]+)"
    tabular_match = re.search(tabular_pattern, document_text)
    if tabular_match:
        description = tabular_match.group(1).strip()
        # Clean up common tabular artifacts
        description = re.sub(r'\s*\|\s*$', '', description)  # Remove trailing separator
        description = re.sub(r'^\s*\|\s*', '', description)  # Remove leading separator
        if len(description) > 5:  # Reasonable description length
            return description

    # Pattern 2: Direct product line format
    direct_pattern = rf"{re.escape(product_code)}\s+\d+\s+([A-Za-z0-9\"'\-\s/&×]+)"
    direct_match = re.search(direct_pattern, document_text)
    if direct_match:
        description = direct_match.group(1).strip()
        # Remove trailing numbers and prices
        description = re.sub(r'\s+[\d\.\$]+.*$', '', description)
        if len(description) > 5:
            return description

    # Pattern 3: Multi-line format
    lines = document_text.split('\n')
    for i, line in enumerate(lines):
        if product_code in line:
            # Look for description in next few lines
            for j in range(1, min(4, len(lines) - i)):
                potential_desc = lines[i + j].strip()
                # Skip lines that are just numbers or UPC codes
                if potential_desc and not re.match(r'^\d+$', potential_desc):
                    # Check if it looks like a product description
                    if re.match(r'^[A-Za-z0-9\"\'.\-\s/&×]+$', potential_desc) and len(potential_desc) > 5:
                        return potential_desc

    return "Product description not available"

def integrate_upc_with_description(document_text, product_code, upc_code):
    """Integrate UPC code with product description"""

    description = extract_description_from_product_context(document_text, product_code)

    if upc_code:
        return f"{product_code} - UPC: {upc_code} - {description}"
    else:
        return f"{product_code} - {description}"

def enhance_description_completeness(description, product_code, document_context):
    """Enhance description completeness using document context"""
    import re

    if "Traditional D-code format" in description:
        # Replace placeholder with actual description
        description = f"{product_code} - Enhanced product description"

    # Look for additional context around product code
    context_pattern = rf"{re.escape(product_code)}[^\n]*([A-Za-z0-9\"'\-\s/&×]*)"
    context_matches = re.findall(context_pattern, document_context)

    if context_matches:
        # Find the longest meaningful context
        best_context = max(context_matches, key=len) if context_matches else ""
        if len(best_context) > len(description.split(' - ')[-1]):
            # Replace description part with better context
            parts = description.split(' - ')
            if len(parts) >= 3:  # Has product code, UPC, and description
                description = f"{parts[0]} - {parts[1]} - {best_context.strip()}"
            else:
                description = f"{parts[0]} - {best_context.strip()}"

    return description

def extract_upc_for_product(document_text, product_code):
    """Extract UPC code for specific product from document"""
    import re

    # Look for UPC near product code
    upc_pattern = rf"{re.escape(product_code)}\s+(\d{{12}})"
    upc_match = re.search(upc_pattern, document_text)

    if upc_match:
        return upc_match.group(1)

    return None

def validate_description_quality(description, product_code):
    """Validate description meets quality standards"""

    if not description or len(description) < 10:
        return False

    # Check for placeholder content
    if "Traditional D-code format" in description:
        return False

    # Should contain product code
    if product_code not in description:
        return False

    # Should have meaningful content beyond just product code
    meaningful_content = description.replace(product_code, "").replace("UPC:", "").replace("-", "")
    if len(meaningful_content.strip()) < 10:
        return False

    return True
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Add sophisticated context-aware description enhancement
- [ ] Implement performance optimization for bulk description processing
- [ ] Add comprehensive logging for description extraction process
- [ ] Enhance UPC integration with validation and error handling
- [ ] Integration with existing Creative-Coop processing pipeline

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for enhanced description extraction logic
- [ ] Description completeness improves from 30% to 95% on CS003837319
- [ ] Successfully integrates UPC codes with product descriptions where available
- [ ] Eliminates "Traditional D-code format" placeholder entries completely
- [ ] Handles various document formats (tabular, multi-line, paragraph) correctly
- [ ] Performance optimized for processing 130+ product descriptions
- [ ] Quality validation ensures meaningful description content
- [ ] Integration maintains compatibility with existing Creative-Coop processing

## Engineering Principles Compliance

**Principle 2. Data quality validation**: Comprehensive validation ensures high-quality description data
**Principle 8. Context-aware extraction**: Uses document context to enhance description completeness
**Principle 9. Algorithmic processing**: Uses pattern-based extraction, not hardcoded descriptions

## Monitoring & Observability

**Required Metrics**:
- Description completeness percentage per invoice
- UPC integration success rate
- Placeholder elimination rate (Traditional D-code format)
- Description quality score distribution

**Log Events**:
```python
# Description extraction success
logger.info("Enhanced description extraction completed", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'description_length': len(description),
    'upc_integrated': bool(upc_code),
    'quality_score': quality_score,
    'extraction_method': method_used
})

# Description enhancement
logger.debug("Description enhanced", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'original_length': original_length,
    'enhanced_length': enhanced_length,
    'enhancement_type': enhancement_type
})
```

## Security Considerations

- [ ] Input sanitization for description text to prevent injection attacks
- [ ] UPC code format validation to ensure data integrity
- [ ] Protection against excessive text processing (DoS protection)

## Performance Requirements

- [ ] Extract enhanced descriptions for 130+ products in < 45 seconds total
- [ ] Individual description extraction completes in < 300ms
- [ ] UPC integration processing in < 100ms per product
- [ ] Memory efficient processing for large document text analysis

## Implementation Notes

**Key Design Decisions**:
- Multi-pattern extraction supports various Creative-Coop document formats
- UPC integration provides comprehensive product identification
- Quality validation ensures meaningful content beyond basic product codes
- Context-aware enhancement uses document text to improve completeness

**Integration Points**:
- Integrates with existing Creative-Coop processing pipeline
- Uses Document AI text processing capabilities
- Compatible with UPC extraction and product code identification functions

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for various description extraction patterns
- [ ] UPC integration and automatic UPC finding scenarios
- [ ] Description quality validation and enhancement testing
- [ ] Performance testing with large document processing
- [ ] Error handling for malformed and incomplete description data
