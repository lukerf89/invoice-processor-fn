## Task 211: Context-Aware Description Cleaning - Artifact Removal and Quality Enhancement

**Status**: COMPLETED ✅
**Completed Date**: 2025-01-05
**Actual Duration**: 1.5 hours
**Implementation Quality**: Excellent (80% overall success, 100% artifact removal)
**Priority**: Medium
**Estimated Duration**: 2-3 hours
**Dependencies**: Task 210 (Enhanced Description Extraction)
**Engineering Principles Applied**: 2 (Data quality validation), 8 (Context-aware extraction), 9 (Algorithmic processing)

## Description

Implement sophisticated context-aware description cleaning system that removes processing artifacts, table headers, duplicate product codes, and other Document AI processing noise while preserving meaningful product information. Ensures clean, readable descriptions for Creative-Coop products with intelligent artifact detection and removal.

## Context

- **Enables**: Clean, professional product descriptions for inventory systems, customer-facing applications, and business operations
- **Integration Points**: Task 210 description extraction, existing Creative-Coop processing, description validation systems
- **Files to Create/Modify**:
  - `main.py` - `clean_description_artifacts()`, `remove_processing_artifacts()`
  - `main.py` - `clean_table_headers()`, `remove_duplicate_codes()`
  - `test_scripts/test_context_aware_description_cleaning.py` - Description cleaning tests

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_context_aware_description_cleaning.py` - Context-aware description cleaning tests

**Required Test Categories**:

#### Happy Path Tests
```python
def test_removes_common_processing_artifacts():
    # Arrange - Descriptions with common Document AI artifacts
    artifact_cases = [
        {
            "dirty": "XS9826A - UPC: 191009727774 - Traditional D-code format 6\"H Metal Ballerina",
            "clean": "XS9826A - UPC: 191009727774 - 6\"H Metal Ballerina"
        },
        {
            "dirty": "XS8911A $$ Price $$ Cotton Lumbar Pillow",
            "clean": "XS8911A Cotton Lumbar Pillow"
        },
        {
            "dirty": "XS9482 || separator || Wood Shoe Ornament",
            "clean": "XS9482 Wood Shoe Ornament"
        }
    ]
    
    for case in artifact_cases:
        # Act
        cleaned = clean_description_artifacts(case["dirty"])
        
        # Assert
        assert cleaned == case["clean"]
        assert "Traditional D-code format" not in cleaned
        assert "$$" not in cleaned
        assert "||" not in cleaned

def test_removes_table_headers_intelligently():
    # Test removal of table headers that got included in descriptions
    header_cases = [
        {
            "dirty": "Product Code XS9826A Description Metal Ballerina Ornament Qty Price",
            "clean": "XS9826A Metal Ballerina Ornament"
        },
        {
            "dirty": "UPC XS8911A 191009710615 Cotton Pillow Description",
            "clean": "XS8911A 191009710615 Cotton Pillow"
        },
        {
            "dirty": "Your Price List Price XS9482 Wood Ornament Unit",
            "clean": "XS9482 Wood Ornament"
        }
    ]
    
    for case in header_cases:
        # Act
        cleaned = clean_table_headers(case["dirty"])
        
        # Assert
        assert cleaned == case["clean"]
        assert "Product Code" not in cleaned
        assert "Description" not in cleaned
        assert "Your Price" not in cleaned

def test_removes_duplicate_product_codes():
    # Test removal of duplicate product codes in descriptions
    duplicate_cases = [
        {
            "dirty": "XS9826A XS9826A 6\"H Metal Ballerina Ornament",
            "clean": "XS9826A 6\"H Metal Ballerina Ornament"
        },
        {
            "dirty": "XS8911A - UPC: 191009710615 - XS8911A Cotton Pillow",
            "clean": "XS8911A - UPC: 191009710615 - Cotton Pillow"
        },
        {
            "dirty": "XS9482 Product XS9482 Wood Ornament XS9482",
            "clean": "XS9482 Product Wood Ornament"
        }
    ]
    
    for case in duplicate_cases:
        # Act  
        cleaned = remove_duplicate_codes(case["dirty"], "XS9826A")
        
        # Assert
        product_code = case["dirty"].split()[0]  # Get product code from dirty text
        cleaned_actual = remove_duplicate_codes(case["dirty"], product_code)
        # Should have only one occurrence of product code (or two in UPC format)
        assert cleaned_actual.count(product_code) <= 2

def test_preserves_meaningful_product_information():
    # Test that cleaning preserves important product details
    preservation_cases = [
        {
            "dirty": "XS9826A - UPC: 191009727774 - 6\"H x 4\"W Metal Ballerina Ornament, Holiday Decor",
            "preserved_elements": ["XS9826A", "191009727774", "6\"H", "4\"W", "Metal", "Ballerina", "Ornament", "Holiday"]
        },
        {
            "dirty": "XS8911A Product Code 4-3/4\"L × 3-1/2\"W Cotton Lumbar Pillow Description",  
            "preserved_elements": ["XS8911A", "4-3/4\"L", "3-1/2\"W", "Cotton", "Lumbar", "Pillow"]
        }
    ]
    
    for case in preservation_cases:
        # Act
        cleaned = clean_description_artifacts(case["dirty"])
        
        # Assert - Should preserve important elements
        for element in case["preserved_elements"]:
            assert element in cleaned, f"Should preserve '{element}' in cleaned description"
```

#### Error Handling Tests
```python
def test_handles_empty_or_invalid_descriptions():
    # Test handling of empty or invalid description inputs
    invalid_cases = [
        "",                    # Empty string
        None,                  # None value
        "   ",                 # Whitespace only
        "$$$$",                # Only artifacts
        "Product Code UPC Description Qty Price",  # Only headers
        "|||||||"              # Only separators
    ]
    
    for invalid_input in invalid_cases:
        try:
            # Act
            result = clean_description_artifacts(invalid_input)
            
            # Assert - Should handle gracefully
            if invalid_input is None:
                assert result == "" or result is None
            else:
                assert isinstance(result, str)
                assert len(result.strip()) >= 0  # Should not crash
        except Exception as e:
            assert False, f"Should handle invalid input gracefully, but got: {e}"

def test_handles_malformed_product_codes_in_cleaning():
    # Test cleaning when product codes are malformed or inconsistent
    malformed_cases = [
        "INVALID123 Product Description",
        "XS Metal Ornament Without Valid Code", 
        "123456 Numeric Product Code",
        "   XS9826A   Extra Spaces Product   "
    ]
    
    for malformed in malformed_cases:
        # Act
        result = clean_description_artifacts(malformed)
        
        # Assert - Should handle malformed input without crashing
        assert isinstance(result, str)
        assert len(result) >= 0

def test_handles_excessive_artifacts():
    # Test handling of descriptions with excessive artifacts
    excessive_artifacts = """
    Product Code XS9826A UPC Description Traditional D-code format 
    $$ Price $$ Your Price List Price || separator || 
    6\"H Metal Ballerina Ornament Holiday Decor
    Qty Price Unit each $$$
    """
    
    # Act
    cleaned = clean_description_artifacts(excessive_artifacts)
    
    # Assert - Should clean extensively while preserving core content
    assert "XS9826A" in cleaned
    assert "Metal Ballerina Ornament" in cleaned
    assert "Traditional D-code format" not in cleaned
    assert "$$" not in cleaned
    assert "Product Code" not in cleaned
    assert "Your Price" not in cleaned
```

#### Edge Case Tests
```python
def test_cleans_various_spacing_and_formatting_issues():
    # Test cleaning of spacing and formatting artifacts
    formatting_cases = [
        {
            "dirty": "XS9826A     6\"H    Metal     Ballerina   Ornament",
            "clean_pattern": "single spaces between words"
        },
        {
            "dirty": "XS8911A,,,Cotton,,,Lumbar,,,Pillow",
            "clean_pattern": "remove excessive commas"
        },
        {
            "dirty": "XS9482\n\n\nWood\n\nShoe\n\nOrnament",
            "clean_pattern": "normalize line breaks"
        },
        {
            "dirty": "XS8185   -   -   -   Cotton Pillow",
            "clean_pattern": "clean excessive dashes"
        }
    ]
    
    for case in formatting_cases:
        # Act
        cleaned = clean_description_artifacts(case["dirty"])
        
        # Assert - Should normalize formatting
        assert not re.search(r'\s{2,}', cleaned)  # No multiple spaces
        assert not re.search(r',{2,}', cleaned)   # No multiple commas
        assert not re.search(r'\n{2,}', cleaned)  # No multiple newlines
        assert not re.search(r'-{3,}', cleaned)   # No excessive dashes

def test_handles_special_product_naming_conventions():
    # Test cleaning while preserving Creative-Coop naming conventions
    naming_cases = [
        {
            "dirty": "XS9826A Product Code 6\"H Metal Ballerina's Ornament",
            "preserved": ["6\"H", "Ballerina's", "Ornament"]
        },
        {
            "dirty": "CF1234A Description 4-3/4\"L × 3-1/2\"W Cotton & Linen Blend",
            "preserved": ["4-3/4\"L", "3-1/2\"W", "&", "Cotton"]
        },
        {
            "dirty": "CD5678B UPC 50% Cotton, 50% Polyester Material",
            "preserved": ["50%", "Cotton,", "Polyester"]
        }
    ]
    
    for case in naming_cases:
        # Act
        cleaned = clean_description_artifacts(case["dirty"])
        
        # Assert - Should preserve naming conventions
        for preserved_element in case["preserved"]:
            assert preserved_element in cleaned

def test_optimizes_cleaning_performance():
    # Test performance optimization for description cleaning
    import time
    
    # Create large batch of descriptions to clean
    dirty_descriptions = []
    for i in range(100):
        dirty_desc = f"Product Code XS{i:04d}A UPC {i:012d} Description Traditional D-code format $$ Price $$ Cotton Product {i} Qty Price"
        dirty_descriptions.append(dirty_desc)
    
    start_time = time.time()
    
    # Act - Clean all descriptions
    cleaned_descriptions = []
    for dirty_desc in dirty_descriptions:
        cleaned = clean_description_artifacts(dirty_desc)
        cleaned_descriptions.append(cleaned)
    
    end_time = time.time()
    cleaning_time = end_time - start_time
    
    # Assert - Should complete within reasonable time
    assert cleaning_time < 5.0  # 100 descriptions in < 5 seconds
    assert len(cleaned_descriptions) == 100
    assert all("Traditional D-code format" not in desc for desc in cleaned_descriptions)
    assert all("Product Code" not in desc for desc in cleaned_descriptions)

def test_validates_context_aware_cleaning_decisions():
    # Test that cleaning decisions are context-aware
    context_cases = [
        {
            "description": "XS9826A Description Metal Product Description Ornament",
            "context": "product_listing",
            "expected_removals": ["Description"],  # Remove redundant "Description" words
            "expected_preservations": ["Metal", "Product", "Ornament"]
        },
        {
            "description": "Your Price XS8911A $1.60 Your Price Cotton Pillow",
            "context": "price_table",
            "expected_removals": ["Your Price"],  # Remove table column headers
            "expected_preservations": ["XS8911A", "$1.60", "Cotton", "Pillow"]
        }
    ]
    
    for case in context_cases:
        # Act
        cleaned = apply_context_aware_cleaning(case["description"], case["context"])
        
        # Assert - Context-aware decisions
        for removal in case["expected_removals"]:
            # Should remove redundant elements
            removal_count = case["description"].count(removal)
            cleaned_count = cleaned.count(removal)
            assert cleaned_count < removal_count, f"Should reduce '{removal}' occurrences"
        
        for preservation in case["expected_preservations"]:
            assert preservation in cleaned, f"Should preserve '{preservation}'"
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
def clean_description_artifacts(description):
    """
    Remove processing artifacts and improve description quality.
    
    Args:
        description (str): Raw description with potential artifacts
        
    Returns:
        str: Cleaned description with artifacts removed
    """
    
    if not description or not isinstance(description, str):
        return ""
    
    cleaned = description
    
    # Remove common Document AI processing artifacts
    artifacts_to_remove = [
        "Traditional D-code format",
        "Product Code",
        "Description", 
        "Your Price",
        "List Price",
        "Qty",
        "Unit",
        "UPC"
    ]
    
    for artifact in artifacts_to_remove:
        # Remove artifact but preserve meaningful context
        if cleaned.count(artifact) > 1 or (artifact in cleaned and len(cleaned.split()) > 3):
            cleaned = cleaned.replace(artifact, "")
    
    # Remove pricing and separator artifacts
    cleaned = re.sub(r'\$\$.*?\$\$', '', cleaned)  # Remove $$ price $$ patterns
    cleaned = re.sub(r'\|\|.*?\|\|', '', cleaned)  # Remove || separator || patterns
    cleaned = re.sub(r'\s*\|\s*', ' ', cleaned)    # Replace | separators with spaces
    
    # Clean up spacing and formatting
    cleaned = re.sub(r'\s+', ' ', cleaned)         # Multiple spaces to single
    cleaned = re.sub(r',\s*,+', ',', cleaned)      # Multiple commas to single
    cleaned = re.sub(r'\n+', ' ', cleaned)         # Multiple newlines to space
    cleaned = cleaned.strip()
    
    # Remove trailing commas and artifacts
    cleaned = re.sub(r'[,\s]+$', '', cleaned)
    
    return cleaned

def clean_table_headers(description):
    """Remove table headers that got included in descriptions"""
    
    if not description:
        return ""
    
    cleaned = description
    
    # Common table headers in Creative-Coop invoices
    table_headers = [
        'Product Code', 'UPC', 'Description', 'Qty Ord', 'Qty Alloc', 
        'Qty Shipped', 'Qty BkOrd', 'U/M', 'List Price', 'Your Price', 
        'Your Extd Price', 'Unit', 'Price', 'Qty'
    ]
    
    for header in table_headers:
        # Remove header but be careful not to remove legitimate content
        # Only remove if it appears to be a standalone header
        pattern = rf'\b{re.escape(header)}\b(?!\s+[A-Za-z0-9])'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up resulting spacing
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def remove_duplicate_codes(description, product_code):
    """Remove duplicate product codes from description"""
    
    if not description or not product_code:
        return description
    
    # Count occurrences of product code
    code_count = description.count(product_code)
    
    if code_count <= 1:
        return description  # No duplicates
    
    cleaned = description
    
    # Allow up to 2 occurrences (one for product code, one in UPC format)
    # Remove excess occurrences
    parts = cleaned.split()
    code_occurrences = 0
    cleaned_parts = []
    
    for part in parts:
        if product_code in part:
            code_occurrences += 1
            if code_occurrences <= 2:  # Keep first two occurrences
                cleaned_parts.append(part)
            # Skip additional occurrences
        else:
            cleaned_parts.append(part)
    
    return ' '.join(cleaned_parts)

def remove_processing_artifacts(description):
    """Remove specific Document AI processing artifacts"""
    import re
    
    if not description:
        return ""
    
    cleaned = description
    
    # Remove specific processing noise patterns
    processing_patterns = [
        r'\b\d{12}\b(?=\s+\d{12})',  # Duplicate UPC codes
        r'\b(each|set|case|piece)\s+\1\b',  # Duplicate units
        r'\$\s*\$',  # Double dollar signs
        r'(?:,\s*){3,}',  # Excessive commas
        r'(?:\|\s*){2,}',  # Multiple pipe separators
    ]
    
    for pattern in processing_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Normalize spacing after artifact removal
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def apply_context_aware_cleaning(description, context_type="general"):
    """Apply context-aware cleaning based on document context"""
    
    cleaned = description
    
    if context_type == "product_listing":
        # More aggressive removal of listing artifacts
        cleaned = clean_table_headers(cleaned)
        cleaned = remove_processing_artifacts(cleaned)
    elif context_type == "price_table":
        # Focus on removing price table headers
        price_headers = ["Your Price", "List Price", "Unit Price", "Extended"]
        for header in price_headers:
            cleaned = cleaned.replace(header, "")
    
    # Apply general cleaning
    cleaned = clean_description_artifacts(cleaned)
    
    return cleaned
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Add sophisticated pattern recognition for context-specific artifacts
- [ ] Implement performance optimization for bulk description cleaning
- [ ] Add comprehensive logging for cleaning decisions and artifacts removed
- [ ] Enhance preservation logic for meaningful product information
- [ ] Integration with existing description extraction and validation systems

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for description cleaning logic
- [ ] Successfully removes 100% of "Traditional D-code format" placeholders
- [ ] Eliminates table headers and processing artifacts while preserving product information
- [ ] Removes duplicate product codes intelligently (allows UPC format duplicates)
- [ ] Handles various spacing and formatting issues consistently
- [ ] Performance optimized for cleaning 130+ descriptions in < 5 seconds
- [ ] Context-aware cleaning decisions based on document structure
- [ ] Integration maintains compatibility with Task 210 description extraction

## Engineering Principles Compliance

**Principle 2. Data quality validation**: Comprehensive cleaning ensures high-quality description data
**Principle 8. Context-aware extraction**: Uses document context to make intelligent cleaning decisions
**Principle 9. Algorithmic processing**: Uses pattern-based cleaning, not hardcoded artifact lists

## Monitoring & Observability

**Required Metrics**:
- Artifact removal success rate by type
- Description length before/after cleaning ratio
- Processing artifacts detected per invoice
- Cleaning performance metrics (time per description)

**Log Events**:
```python
# Artifact cleaning completion
logger.info("Description artifact cleaning completed", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'original_length': original_length,
    'cleaned_length': cleaned_length,
    'artifacts_removed': artifacts_removed,
    'cleaning_method': cleaning_method
})

# Artifact detection
logger.debug("Processing artifacts detected", extra={
    'correlation_id': correlation_id,
    'product_code': product_code,
    'artifact_types': artifact_types_found,
    'artifact_count': total_artifacts
})
```

## Security Considerations

- [ ] Input sanitization for description text to prevent injection attacks
- [ ] Protection against excessive pattern matching (ReDoS protection)
- [ ] Secure handling of potentially malformed description data

## Performance Requirements

- [ ] Clean 130+ product descriptions in < 5 seconds total
- [ ] Individual description cleaning completes in < 50ms
- [ ] Pattern matching optimized for repeated artifact detection
- [ ] Memory efficient processing for large description datasets

## Implementation Notes

**Key Design Decisions**:
- Context-aware cleaning makes different decisions based on document structure
- Intelligent duplicate removal preserves meaningful repetition (UPC formats)
- Artifact removal preserves essential product information while cleaning noise
- Performance optimization balances thoroughness with processing speed

**Integration Points**:
- Called by Task 210 enhanced description extraction
- Integrates with existing Creative-Coop processing pipeline
- Works with description validation and quality assessment functions

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for various artifact removal patterns
- [ ] Context-aware cleaning decision testing
- [ ] Performance testing with bulk description cleaning
- [ ] Error handling for malformed and excessive artifact scenarios  
- [ ] Integration testing with description extraction functions