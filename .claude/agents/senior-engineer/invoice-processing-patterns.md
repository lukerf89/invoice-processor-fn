# Invoice Processing Patterns for TDD

## Common Test Patterns

### Document AI Testing
```python
# Pattern for Document AI processing
import pytest
from unittest.mock import Mock, patch
import json

def test_document_ai_extracts_line_items_successfully():
    # Arrange
    mock_document_response = load_fixture('test_invoices/creative_coop_docai_output.json')
    expected_items = [
        {'product_code': 'DF6802', 'description': 'Test Product', 'quantity': 8, 'price': 12.50}
    ]

    # Act
    with patch('google.cloud.documentai.DocumentProcessorServiceClient') as mock_client:
        mock_client.return_value.process_document.return_value = mock_document_response
        result = extract_line_items_from_entities(mock_document_response)

    # Assert
    assert len(result) == len(expected_items)
    assert all(item.get('product_code') for item in result)
    assert all(isinstance(item.get('quantity'), int) for item in result)

def test_handles_document_ai_service_failure():
    # Arrange
    error_response = Mock()
    error_response.side_effect = Exception("Document AI service unavailable")

    # Act & Assert
    with patch('google.cloud.documentai.DocumentProcessorServiceClient') as mock_client:
        mock_client.return_value.process_document = error_response
        with pytest.raises(DocumentAIError):
            process_invoice_with_document_ai('test.pdf')

def test_document_ai_timeout_handling():
    # Arrange
    timeout_error = TimeoutError("Document AI timeout")

    # Act & Assert
    with patch('google.cloud.documentai.DocumentProcessorServiceClient') as mock_client:
        mock_client.return_value.process_document.side_effect = timeout_error
        result = process_invoice_with_fallback('test.pdf')
        # Should fall back to text parsing
        assert result is not None
```

### Vendor-Specific Pattern Testing
```python
# Pattern for Creative-Coop processing
def test_creative_coop_quantity_extraction():
    # Arrange
    text_snippet = "DF6802 8 0 lo each $12.50 $100.00"
    expected_quantity = 8

    # Act
    quantity = extract_creative_coop_quantity(text_snippet)

    # Assert
    assert quantity == expected_quantity

def test_creative_coop_wholesale_price_extraction():
    # Arrange
    text_snippet = "DF6802 8 0 lo each $12.50 $100.00"  # wholesale is $12.50 (4th number)
    expected_price = 12.50

    # Act
    price = extract_wholesale_price(text_snippet)

    # Assert
    assert abs(price - expected_price) < 0.01

def test_harpercollins_isbn_title_formatting():
    # Arrange
    raw_text = "9780062315007 The Great Book Title"
    expected_format = "9780062315007; The Great Book Title"

    # Act
    result = format_harpercollins_book_data(raw_text)

    # Assert
    assert result == expected_format

def test_onehundred80_upc_extraction():
    # Arrange
    description_text = "Product Name 123456789012 Additional Info"
    expected_upc = "123456789012"

    # Act
    upc = extract_upc_from_description(description_text)

    # Assert
    assert upc == expected_upc
    assert len(upc) == 12
```

### Google Sheets Integration Testing
```python
# Pattern for Google Sheets operations
def test_writes_invoice_data_to_sheets():
    # Arrange
    line_items = [
        ['INV123', '2023-01-01', 'DF6802', 'Test Product', 8, 12.50]
    ]
    mock_service = Mock()
    mock_service.spreadsheets().values().append.return_value.execute.return_value = {'updates': 1}

    # Act
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_build.return_value = mock_service
        result = write_to_sheet(line_items, 'TestSheet')

    # Assert
    mock_service.spreadsheets().values().append.assert_called_once()
    call_args = mock_service.spreadsheets().values().append.call_args
    assert 'B:G' in call_args[1]['range']  # Verify correct range

def test_handles_sheets_api_rate_limit():
    # Arrange
    from googleapiclient.errors import HttpError
    rate_limit_error = HttpError(
        Mock(status=429),
        "Rate Limit Exceeded"
    )

    # Act & Assert
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_service = Mock()
        mock_service.spreadsheets().values().append.side_effect = [
            rate_limit_error,  # First attempt fails
            Mock(execute=Mock(return_value={'updates': 1}))  # Second succeeds
        ]
        mock_build.return_value = mock_service

        result = write_to_sheet_with_retry([['test']], 'TestSheet')
        assert result is not None
        assert mock_service.spreadsheets().values().append.call_count == 2

def test_sheets_data_formatting():
    # Arrange
    raw_line_items = [
        {
            'invoice_number': 'INV123',
            'date': '2023-01-01',
            'product_code': 'DF6802',
            'description': 'Test Product',
            'quantity': 8,
            'price': 12.50
        }
    ]
    expected_format = [
        ['INV123', '2023-01-01', 'DF6802', 'Test Product', 8, 12.50]
    ]

    # Act
    formatted_data = format_for_sheets(raw_line_items)

    # Assert
    assert formatted_data == expected_format
    assert all(isinstance(row, list) for row in formatted_data)
```

### Performance Testing Patterns
```python
# Pattern for performance validation
import time
import psutil

@pytest.mark.performance
def test_invoice_processing_within_timeout_limits():
    # Arrange
    large_invoice_path = 'test_invoices/large_creative_coop.pdf'
    timeout_limit = 160  # Zapier timeout limit

    # Act
    start_time = time.time()
    result = process_invoice_from_file(large_invoice_path)
    processing_time = time.time() - start_time

    # Assert
    assert processing_time < timeout_limit
    assert len(result) > 0
    assert all('product_code' in item for item in result)

def test_memory_usage_stays_within_limits():
    # Test memory consumption during processing
    process = psutil.Process()

    initial_memory = process.memory_info().rss
    process_large_invoice('test_invoices/complex_invoice.pdf')
    peak_memory = process.memory_info().rss

    # Should not exceed reasonable limits
    memory_increase = peak_memory - initial_memory
    assert memory_increase < 500 * 1024 * 1024  # Less than 500MB increase

@pytest.mark.performance
def test_concurrent_processing():
    # Test multiple invoice processing
    import concurrent.futures

    invoice_files = [
        'test_invoices/creative_coop.pdf',
        'test_invoices/harpercollins.pdf',
        'test_invoices/onehundred80.pdf'
    ]

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_invoice_from_file, invoice_files))

    total_time = time.time() - start_time
    assert total_time < 90  # Should complete in under 90 seconds
    assert all(len(result) > 0 for result in results)
```

### Algorithmic Pattern Testing
```python
# Pattern for testing algorithmic extraction (no hardcoding)
def test_extract_quantity_uses_algorithmic_pattern():
    # Test various quantity patterns
    test_cases = [
        ("8 0 lo each", 8),
        ("12 5 Set", 12),
        ("1 0 Case", 1),
        ("25 10 Kit", 25)
    ]

    for text, expected_qty in test_cases:
        result = extract_quantity_algorithmic(text)
        assert result == expected_qty, f"Failed for: {text}"

def test_product_code_normalization():
    # Test product code extraction and normalization
    test_cases = [
        ("DF6802", "DF6802"),  # Already short
        ("123456789012", "123456789012"),  # UPC - keep as is
        ("9780062315007", "9780062315007"),  # ISBN - keep as is
        ("VERY-LONG-PRODUCT-CODE-123456", "VERYLONGPR123456")  # Shortened
    ]

    for input_code, expected in test_cases:
        result = normalize_product_code(input_code)
        assert result == expected

def test_vendor_detection_algorithm():
    # Test vendor detection without hardcoding
    test_cases = [
        ("Creative Coop LLC\nInvoice", "creative-coop"),
        ("HarperCollins Publishers", "harpercollins"),
        ("OneHundred80 Design", "onehundred80"),
        ("Rifle Paper Co.", "rifle-paper")
    ]

    for invoice_text, expected_vendor in test_cases:
        result = detect_vendor_type(invoice_text)
        assert result == expected_vendor
```

### Error Recovery Testing
```python
# Pattern for testing error recovery
def test_graceful_degradation_when_gemini_fails():
    # Arrange
    with patch('process_with_gemini_first') as mock_gemini:
        mock_gemini.side_effect = TimeoutError("Gemini timeout")

        with patch('extract_line_items_from_entities') as mock_docai:
            mock_docai.return_value = [{'product_code': 'TEST', 'quantity': 1}]

            # Act
            result = process_invoice_with_fallback('test.pdf')

            # Assert
            assert len(result) > 0
            assert mock_gemini.called
            assert mock_docai.called

def test_handles_corrupted_document_ai_response():
    # Arrange
    corrupted_response = {"pages": [{"blocks": "invalid structure"}]}

    # Act & Assert
    try:
        result = extract_line_items_from_entities(corrupted_response)
        # Should return empty list, not crash
        assert isinstance(result, list)
    except Exception as e:
        pytest.fail(f"Should handle corrupted response gracefully, but raised: {e}")

def test_partial_data_extraction():
    # Test that system continues processing even with some failures
    mock_entities = [
        {"type": "line_item", "properties": {"product_code": "VALID1", "quantity": "5"}},
        {"type": "line_item", "properties": {"product_code": "", "quantity": "invalid"}},  # Malformed
        {"type": "line_item", "properties": {"product_code": "VALID2", "quantity": "3"}}
    ]

    result = extract_line_items_from_entities_safe(mock_entities)

    # Should extract valid items and skip invalid ones
    assert len(result) == 2
    assert result[0]['product_code'] == 'VALID1'
    assert result[1]['product_code'] == 'VALID2'
```

## Test Data Management

### Fixture Organization
```python
# conftest.py patterns
@pytest.fixture
def creative_coop_docai_response():
    """Load Creative-Coop Document AI response for testing"""
    with open('test_invoices/Creative-Coop_CI004848705_docai_output.json') as f:
        return json.load(f)

@pytest.fixture
def sample_invoice_text():
    """Sample invoice text for pattern testing"""
    return """
    Invoice Number: INV123
    Date: 2023-01-01

    DF6802 8 0 lo each $12.50 $100.00
    ST1234 5 2 Set $8.00 $40.00
    """

@pytest.fixture
def mock_google_sheets_service():
    """Mock Google Sheets service for testing"""
    mock_service = Mock()
    mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
        'updates': {'updatedRows': 1}
    }
    return mock_service
```

### Integration Test Patterns
```python
# Full pipeline integration testing
def test_end_to_end_creative_coop_processing():
    # Arrange
    invoice_path = 'test_invoices/Creative-Coop_CI004848705.PDF'
    expected_items = load_expected_output('test_invoices/Creative-Coop_CI004848705_processed_output.csv')

    # Act
    result = process_invoice_end_to_end(invoice_path)

    # Assert
    assert len(result) >= len(expected_items) * 0.8  # Allow for 80% accuracy
    assert all('product_code' in item for item in result)
    assert all('quantity' in item for item in result)
    assert all('price' in item for item in result)

def test_multi_vendor_processing_consistency():
    # Test that same patterns work across vendors
    vendor_files = {
        'creative-coop': 'test_invoices/Creative-Coop_CI004848705.PDF',
        'harpercollins': 'test_invoices/Harpercollins_04-29-2025.pdf',
        'onehundred80': 'test_invoices/ONEHUNDRED80-7-1-2025-1T25194476NCHR.pdf'
    }

    results = {}
    for vendor, file_path in vendor_files.items():
        results[vendor] = process_invoice_from_file(file_path)

    # All should succeed
    assert all(len(result) > 0 for result in results.values())

    # All should have consistent structure
    for vendor, result in results.items():
        assert all('product_code' in item for item in result), f"Missing product_code in {vendor}"
        assert all('quantity' in item for item in result), f"Missing quantity in {vendor}"
```
