# Task 03: Column Alignment Validation - Proactive Monitoring

## TDD Cycle Overview
**RED**: Write tests that demonstrate current lack of column validation allows misaligned data
**GREEN**: Implement validation functions to catch column misalignment before Google Sheets writes
**REFACTOR**: Integrate validation seamlessly into existing processing pipeline

## Test Requirements
- [ ] Unit tests for column validation with various row formats
- [ ] Integration tests for validation in Google Sheets write pipeline
- [ ] Error handling tests for malformed data detection
- [ ] Performance tests ensuring validation doesn't impact processing speed
- [ ] Edge case tests for empty rows, partial data, and oversized rows
- [ ] Alert/monitoring tests for proactive issue detection

## Implementation Steps (Red-Green-Refactor)

### Step 1: RED - Write Failing Tests

```python
# Test file: test_scripts/test_column_alignment_validation.py
import pytest
from unittest.mock import patch, MagicMock
import logging

# Functions to be implemented
from main import (
    validate_column_alignment,
    validate_row_format, 
    write_to_sheet_with_validation,
    log_column_alignment_error
)

def test_validation_detects_wrong_column_count():
    """RED: Test that validation catches rows with incorrect column counts"""
    # Test data with various column count issues
    test_cases = [
        # Too few columns
        {
            "rows": [["2023-01-15", "Creative-Coop", "INV001", "Item"]],  # 4 columns, need 6
            "expected_valid": False,
            "expected_error": "Row 0 has 4 columns, expected 6"
        },
        # Too many columns  
        {
            "rows": [["", "2023-01-15", "Creative-Coop", "INV001", "Item", "8.50", "12", "Extra"]],  # 8 columns
            "expected_valid": False,
            "expected_error": "Row 0 has 8 columns, expected 6"
        },
        # Mixed column counts
        {
            "rows": [
                ["2023-01-15", "Creative-Coop", "INV001", "Item", "8.50", "12"],  # 6 columns (correct)
                ["2023-01-15", "HarperCollins", "INV002", "Book"]  # 4 columns (wrong)
            ],
            "expected_valid": False,
            "expected_error": "Row 1 has 4 columns, expected 6"
        }
    ]
    
    for case in test_cases:
        # This should fail initially - validation function doesn't exist
        with pytest.raises(NameError):
            result = validate_column_alignment(case["rows"])

def test_validation_allows_correct_column_format():
    """Test that validation passes for correctly formatted 6-column data"""
    correct_rows = [
        ["2023-01-15", "Creative-Coop", "INV001", "XS9826A; Metal Ballerina", "8.50", "12"],
        ["2023-01-15", "Creative-Coop", "INV001", "XS8911A; Metal Item", "12.00", "6"],
        ["2023-01-16", "HarperCollins", "PO123", "ISBN123; Book Title", "15.00", "8"]
    ]
    
    # This should fail initially - function doesn't exist
    with pytest.raises(NameError):
        result = validate_column_alignment(correct_rows)
        assert result is True

def test_google_sheets_write_without_validation_allows_bad_data():
    """RED: Test that current Google Sheets write allows misaligned data"""
    # Mock Google Sheets API
    with patch('main.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Bad data with wrong column count
        bad_rows = [
            ["2023-01-15", "Creative-Coop", "INV001"]  # Only 3 columns
        ]
        
        # Current implementation should allow this bad data through
        # This test demonstrates the current problem - no validation
        
        # Import current write function (should exist)
        from main import write_to_sheet
        
        # This should succeed but write bad data (the problem we're fixing)
        try:
            write_to_sheet(bad_rows, "test-sheet", "B:G")
            # If this passes, it shows current lack of validation
            assert True, "Current implementation allows bad data through"
        except Exception as e:
            # If it fails, it might already have some validation
            pytest.fail(f"Unexpected error: {e}")

def test_error_logging_captures_column_issues():
    """RED: Test that error logging for column issues doesn't exist yet"""
    # This should fail initially - logging function doesn't exist
    with pytest.raises(NameError):
        log_column_alignment_error("Test sheet", 0, ["bad", "data"], 6)

def test_performance_impact_of_validation():
    """Test that validation doesn't significantly impact processing speed"""
    import time
    
    # Large dataset to test performance
    large_dataset = []
    for i in range(1000):
        large_dataset.append([
            f"2023-01-{i%30+1:02d}", 
            "Creative-Coop", 
            f"INV{i:04d}", 
            f"XS{i}A; Test Item {i}", 
            f"{(i%100)+1}.50", 
            str(i%50+1)
        ])
    
    # This will fail initially - function doesn't exist
    with pytest.raises(NameError):
        start_time = time.time()
        result = validate_column_alignment(large_dataset)
        end_time = time.time()
        
        # Should complete validation in under 100ms for 1000 rows
        assert (end_time - start_time) < 0.1, f"Validation too slow: {end_time - start_time:.3f}s"
        assert result is True
```

### Step 2: GREEN - Minimal Implementation

Add validation functions to main.py:

```python
# Add to main.py - Column validation functions

import logging

# Configure logging for column alignment issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_column_alignment(rows, expected_columns=6):
    """
    Validate that all rows have exactly the expected number of columns for B:G range.
    
    Args:
        rows: List of row data (each row is a list)
        expected_columns: Expected number of columns (default 6 for B:G)
    
    Returns:
        bool: True if all rows have correct column count, False otherwise
    """
    if not rows:
        return True
    
    for i, row in enumerate(rows):
        if len(row) != expected_columns:
            error_msg = f"⚠️ COLUMN ALIGNMENT ERROR: Row {i} has {len(row)} columns, expected {expected_columns}"
            logger.error(error_msg)
            logger.error(f"Row data: {row}")
            return False
    
    return True

def validate_row_format(row, row_index=0, expected_columns=6):
    """
    Validate a single row format.
    
    Args:
        row: Single row data (list)
        row_index: Row index for error reporting
        expected_columns: Expected number of columns
    
    Returns:
        dict: Validation result with success status and error message
    """
    if len(row) != expected_columns:
        return {
            "valid": False,
            "error": f"Row {row_index} has {len(row)} columns, expected {expected_columns}",
            "row_data": row
        }
    
    return {"valid": True, "error": None, "row_data": row}

def log_column_alignment_error(sheet_name, row_index, row_data, expected_columns):
    """
    Log detailed column alignment error information.
    
    Args:
        sheet_name: Name of the sheet being written to
        row_index: Index of the problematic row
        row_data: The actual row data
        expected_columns: Expected number of columns
    """
    error_msg = (
        f"COLUMN ALIGNMENT ERROR in sheet '{sheet_name}': "
        f"Row {row_index} has {len(row_data)} columns, expected {expected_columns}. "
        f"Data: {row_data}"
    )
    logger.error(error_msg)
    
    # Additional context logging
    logger.error(f"Expected format: 6 columns for Google Sheets B:G range")
    logger.error(f"Actual data types: {[type(item).__name__ for item in row_data]}")

def write_to_sheet_with_validation(line_items, sheet_name=None, range_name="B:G"):
    """
    Write line items to Google Sheet with column validation.
    
    Args:
        line_items: List of line item data
        sheet_name: Google Sheets sheet name
        range_name: Cell range (default B:G for 6 columns)
    
    Returns:
        bool: Success status
    """
    # Validate column alignment before writing
    if not validate_column_alignment(line_items):
        log_column_alignment_error(sheet_name or "Unknown", -1, line_items, 6)
        raise ValueError("Column alignment validation failed. See logs for details.")
    
    # If validation passes, proceed with existing write logic
    return write_to_sheet(line_items, sheet_name, range_name)
```

### Step 3: REFACTOR - Integrate into Processing Pipeline

Update existing Google Sheets write functions to include validation:

```python
# Modify existing write_to_sheet function in main.py
def write_to_sheet(line_items, sheet_name=None, range_name=None):
    """Enhanced write_to_sheet with built-in validation"""
    
    # Add validation at the beginning
    if not validate_column_alignment(line_items):
        # Don't write invalid data - fail fast
        raise ValueError("Invalid column alignment detected. Aborting write operation.")
    
    # Log successful validation
    logger.info(f"Column validation passed for {len(line_items)} rows")
    
    # Proceed with existing Google Sheets write logic...
    # [existing implementation remains unchanged]

# Add validation to other write functions
def append_to_sheet(line_items, sheet_name=None, range_name=None):
    """Enhanced append with validation"""
    if not validate_column_alignment(line_items):
        raise ValueError("Invalid column alignment for append operation")
    
    # Proceed with existing append logic...

# Create monitoring function for proactive detection
def validate_processing_pipeline(vendor_type, line_items):
    """
    Validate the entire processing pipeline output before final write.
    
    Args:
        vendor_type: Type of vendor (Creative-Coop, HarperCollins, etc.)
        line_items: Processed line items
    
    Returns:
        dict: Validation report
    """
    report = {
        "vendor_type": vendor_type,
        "total_rows": len(line_items),
        "column_alignment_valid": False,
        "issues": []
    }
    
    # Column alignment validation
    if validate_column_alignment(line_items):
        report["column_alignment_valid"] = True
    else:
        report["issues"].append("Column alignment validation failed")
    
    # Additional validations
    for i, row in enumerate(line_items):
        validation_result = validate_row_format(row, i)
        if not validation_result["valid"]:
            report["issues"].append(f"Row {i}: {validation_result['error']}")
    
    # Log validation report
    if report["issues"]:
        logger.warning(f"Validation issues for {vendor_type}: {report['issues']}")
    else:
        logger.info(f"All validations passed for {vendor_type} ({len(line_items)} rows)")
    
    return report
```

## Acceptance Criteria (Test-Driven)

- [ ] All RED tests pass (demonstrating current lack of validation)
- [ ] All GREEN tests pass (demonstrating validation catches issues)
- [ ] Column validation catches rows with wrong column counts (< 6 or > 6)
- [ ] Validation allows correctly formatted 6-column data to pass through
- [ ] Google Sheets writes fail fast when column alignment is wrong
- [ ] Detailed error logging captures problematic rows and context
- [ ] Performance impact is minimal (< 10ms for 100 rows)
- [ ] Integration with existing write_to_sheet functions is seamless
- [ ] Validation report provides actionable information for debugging
- [ ] Proactive monitoring detects issues before they reach Google Sheets

## Engineering Principles Applied

**Principle 1 - Fail Fast**: Validation catches issues immediately, preventing bad data writes
**Principle 2 - Observability**: Comprehensive logging and monitoring for troubleshooting
**Principle 3 - Testability**: Every validation function has comprehensive test coverage
**Principle 4 - Performance**: Efficient validation that doesn't impact processing speed
**Principle 5 - Maintainability**: Clear error messages and centralized validation logic

## Code Review Checklist

- [ ] **Validation Logic**: Correctly identifies column count mismatches
- [ ] **Error Handling**: Graceful failure with detailed error messages
- [ ] **Performance**: Validation completes quickly for large datasets
- [ ] **Integration**: Seamlessly integrates with existing Google Sheets write functions
- [ ] **Logging**: Structured logging with actionable error information
- [ ] **Test Coverage**: Comprehensive test cases for all validation scenarios
- [ ] **Monitoring**: Proactive detection of alignment issues
- [ ] **Documentation**: Clear documentation of validation requirements

## Risk Assessment

**Low Risk**: Performance impact from validation overhead
- **Mitigation**: Efficient validation algorithms, performance benchmarking
- **Detection**: Processing time monitoring, timeout alerts

**Medium Risk**: Validation being too strict and blocking valid data
- **Mitigation**: Comprehensive test cases, flexible validation parameters
- **Detection**: User reports of blocked processing, validation failure logs

**Low Risk**: Integration issues with existing write functions
- **Mitigation**: Gradual rollout, backward compatibility preservation
- **Detection**: Regression testing, monitoring write success rates

## Success Metrics

- **Issue Prevention**: Zero column alignment issues reach Google Sheets
- **Detection Speed**: Issues caught within 1ms of occurrence  
- **Error Quality**: 100% of validation errors include actionable information
- **Performance**: < 5% overhead for validation processing
- **Monitoring**: Proactive alerts for all column alignment issues

## Files Modified

- `/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/main.py` (validation functions)
- `test_scripts/test_column_alignment_validation.py` (new test file)
- Existing Google Sheets write functions (validation integration)
- Logging configuration for alignment monitoring

## Dependencies

- Python logging module for error tracking
- Existing Google Sheets write functions for integration
- Performance testing framework for benchmarking
- Test data with various column count scenarios