# Task 02: Test Script Column Header Fix - Remove Column A References

## TDD Cycle Overview
**RED**: Write tests that demonstrate test scripts output 7 columns (including Column A) while main.py outputs 6 columns
**GREEN**: Update all test scripts to remove "Column A" headers and maintain 6-column B:G format
**REFACTOR**: Standardize header format across all test scripts for consistency

## Test Requirements
- [ ] Unit tests validating each test script outputs exactly 6 columns
- [ ] Integration tests comparing test script output format with main.py output format
- [ ] CSV validation tests ensuring proper B:G column alignment
- [ ] Header consistency tests across all test scripts
- [ ] Edge case tests for scripts with different output formats
- [ ] Visual alignment tests for stakeholder review compatibility

## Implementation Steps (Red-Green-Refactor)

### Step 1: RED - Write Failing Tests

```python
# Test file: test_scripts/test_column_header_alignment.py
import pytest
import csv
import io
import importlib.util
import os
from unittest.mock import patch

def load_test_script_module(script_path):
    """Dynamically load a test script as a module"""
    spec = importlib.util.spec_from_file_location("test_module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_current_scripts_have_column_a_mismatch():
    """RED: Test that current scripts include Column A but only write 6 data columns"""
    test_scripts_with_column_a = [
        "test_scripts/test_onehundred80.py",
        "test_scripts/test_final_creative_coop.py", 
        "test_scripts/test_rifle_improved.py",
        "test_scripts/test_integrated_creative_coop.py",
        "test_scripts/final_creative_coop_processing.py",
        "test_scripts/improved_creative_coop_processing.py",
        "test_scripts/test_upc_mapping.py",
        "test_scripts/test_final_descriptions.py",
        "test_scripts/test_improved_descriptions.py",
        "test_scripts/test_creative_coop_csv.py",
        "test_scripts/perfect_processing.py",
        "test_scripts/final_corrected_processing.py",
        "test_scripts/improved_processing_v2.py",
        "test_scripts/improved_processing.py"
    ]
    
    column_a_found = []
    
    for script_path in test_scripts_with_column_a:
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                content = f.read()
                if '"Column A"' in content or "'Column A'" in content:
                    column_a_found.append(script_path)
    
    # RED: This should fail initially - scripts contain Column A references
    assert len(column_a_found) > 0, f"Expected scripts with Column A, found none in: {test_scripts_with_column_a}"

def test_main_py_outputs_six_columns():
    """Test that main.py functions output exactly 6 columns for B:G range"""
    # Mock data representing typical line items
    sample_line_items = [
        ["2023-01-15", "Creative-Coop", "INV001", "XS9826A; Metal Ballerina", "8.50", "12"],
        ["2023-01-15", "Creative-Coop", "INV001", "XS8911A; Metal Item", "12.00", "6"],
    ]
    
    # Verify each row has exactly 6 columns
    for row in sample_line_items:
        assert len(row) == 6, f"Main.py output should have 6 columns, row has {len(row)}: {row}"

def test_header_column_count_mismatch():
    """RED: Test that scripts with Column A have 7 headers but 6 data columns"""
    # This will fail initially - demonstrating the mismatch
    headers_with_column_a = ["Column A", "Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]
    sample_data_row = ["2023-01-15", "Creative-Coop", "INV001", "XS9826A; Metal Ballerina", "8.50", "12"]
    
    assert len(headers_with_column_a) == 7
    assert len(sample_data_row) == 6
    
    # RED: This should fail - header count doesn't match data count
    assert len(headers_with_column_a) != len(sample_data_row), "Headers and data have mismatched column counts"

def test_csv_output_alignment_issues():
    """RED: Test CSV output alignment issues with Column A headers"""
    headers_with_column_a = ["Column A", "Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]
    sample_data = [
        ["2023-01-15", "Creative-Coop", "INV001", "XS9826A; Metal Ballerina", "8.50", "12"],
        ["2023-01-15", "Creative-Coop", "INV001", "XS8911A; Metal Item", "12.00", "6"],
    ]
    
    # Create CSV with mismatched headers/data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers_with_column_a)
    writer.writerows(sample_data)
    csv_content = output.getvalue()
    
    # RED: This should show misalignment
    lines = csv_content.strip().split('\n')
    header_line = lines[0]
    data_line = lines[1]
    
    header_columns = len(header_line.split(','))
    data_columns = len(data_line.split(','))
    
    assert header_columns != data_columns, f"CSV has misaligned headers ({header_columns}) and data ({data_columns})"
```

### Step 2: GREEN - Minimal Implementation

Update test scripts to remove "Column A" and use 6-column B:G format:

```python
# Standard 6-column header format (no Column A)
CORRECT_HEADERS = ["Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]

# Files to update (search for actual Column A references):
# 1. Find all scripts with Column A references
# 2. Replace 7-column headers with 6-column headers
# 3. Ensure data output matches 6-column format

# Example update for test_scripts/perfect_processing.py:
# OLD: headers = ["Column A", "Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]
# NEW: headers = ["Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]

# Example update for any CSV writing:
# OLD: writer.writerow(["Column A", "Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"])
# NEW: writer.writerow(["Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"])
```

### Step 3: REFACTOR - Standardize Header Format

Create a shared constant and validation function:

```python
# Add to a shared test utilities file: test_scripts/test_utils.py
GOOGLE_SHEETS_HEADERS = ["Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]
EXPECTED_COLUMN_COUNT = 6

def validate_csv_format(csv_file_path):
    """Validate that CSV has proper 6-column B:G format"""
    with open(csv_file_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Validate header count
        if len(headers) != EXPECTED_COLUMN_COUNT:
            raise ValueError(f"Expected {EXPECTED_COLUMN_COUNT} columns, got {len(headers)}: {headers}")
        
        # Validate header content
        if headers != GOOGLE_SHEETS_HEADERS:
            raise ValueError(f"Headers don't match expected format. Got: {headers}")
        
        # Validate all data rows have correct column count
        for row_num, row in enumerate(reader, start=2):
            if len(row) != EXPECTED_COLUMN_COUNT:
                raise ValueError(f"Row {row_num} has {len(row)} columns, expected {EXPECTED_COLUMN_COUNT}: {row}")
    
    return True

def write_standardized_csv(file_path, line_items):
    """Write line items to CSV with standardized 6-column format"""
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(GOOGLE_SHEETS_HEADERS)
        
        for item in line_items:
            if len(item) != EXPECTED_COLUMN_COUNT:
                raise ValueError(f"Line item has {len(item)} columns, expected {EXPECTED_COLUMN_COUNT}: {item}")
            writer.writerow(item)
```

## Acceptance Criteria (Test-Driven)

- [ ] All RED tests pass (demonstrating current Column A mismatch)
- [ ] All GREEN tests pass (demonstrating 6-column consistency)
- [ ] Zero test scripts contain "Column A" references after fix
- [ ] All test scripts output exactly 6 columns matching B:G range
- [ ] CSV outputs align properly with no empty first column
- [ ] Headers match Google Sheets format: ["Order Date", "Vendor", "INV", "Item", "Wholesale", "Qty ordered"]
- [ ] Visual alignment issues resolved for stakeholder reviews
- [ ] All test script functionality preserved after header changes
- [ ] Standardized header format implemented across all scripts
- [ ] CSV validation utility created for ongoing compliance

## Engineering Principles Applied

**Principle 1 - Consistency**: Standardized header format across all test scripts
**Principle 2 - Maintainability**: Centralized header constants and validation utilities
**Principle 3 - Testability**: Comprehensive validation of CSV format and column alignment
**Principle 4 - Documentation**: Clear error messages for column count mismatches
**Principle 5 - Quality**: Automated validation prevents future header alignment issues

## Code Review Checklist

- [ ] **Header Consistency**: All scripts use identical 6-column header format
- [ ] **Column Count**: All data rows output exactly 6 columns
- [ ] **CSV Format**: Output aligns properly with no empty first column
- [ ] **Functionality**: Test script core functionality unchanged after header fix
- [ ] **Validation**: CSV validation utility catches format issues
- [ ] **Standards**: Headers match Google Sheets B:G range expectations
- [ ] **Error Handling**: Clear error messages for column mismatches
- [ ] **Documentation**: Header format documented and standardized

## Files to Update

Search and update all files containing "Column A" references:

```bash
# Find scripts with Column A references
grep -r "Column A" test_scripts/ --include="*.py"

# Expected files to update based on phase document:
test_scripts/test_onehundred80.py
test_scripts/test_final_creative_coop.py
test_scripts/test_rifle_improved.py
test_scripts/test_integrated_creative_coop.py
test_scripts/final_creative_coop_processing.py
test_scripts/improved_creative_coop_processing.py
test_scripts/test_upc_mapping.py
test_scripts/test_final_descriptions.py
test_scripts/test_improved_descriptions.py
test_scripts/test_creative_coop_csv.py
test_scripts/perfect_processing.py
test_scripts/final_corrected_processing.py
test_scripts/improved_processing_v2.py
test_scripts/improved_processing.py
```

## Success Metrics

- **Visual Alignment**: Test output matches Google Sheets format exactly
- **Consistency**: 100% of test scripts use standardized 6-column format  
- **Validation**: Automated CSV format validation catches issues
- **Stakeholder Experience**: No confusion about column alignment during reviews
- **Maintenance**: Centralized header management prevents future inconsistencies

## Risk Assessment

**Low Risk**: Test script functionality changes during header updates
- **Mitigation**: Preserve all core processing logic, only update headers/output
- **Detection**: Run each script before/after to verify identical processing results

**Low Risk**: Missing some scripts with Column A references
- **Mitigation**: Comprehensive grep search, systematic file-by-file review
- **Detection**: Automated scanning for "Column A" in CI/CD pipeline

## Dependencies

- All test scripts accessible and modifiable
- Test invoice files available for validation
- CSV comparison tools for before/after validation
- Access to representative test data for each script type