# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Google Cloud Function that processes invoices using Document AI. It receives Trello webhook requests with PDF URLs, downloads and processes invoices, then writes extracted data to Google Sheets.

## Tech Stack

- **Runtime**: Python 3.12+ (originally 3.12.11)
- **Framework**: Google Cloud Functions with functions-framework
- **Cloud Services**: Google Cloud Document AI, Google Sheets API
- **Key Dependencies**: google-cloud-documentai, google-auth, google-api-python-client, requests, flask

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Local development server
functions-framework --target=process_invoice --debug

# Test with sample data
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/invoice.pdf"}'

# Debug Document AI output (requires environment variables)
python document_ai_explorer.py <pdf_file_path> [--save-json]

# Test with local sample invoice
python document_ai_explorer.py new_invoice.pdf --save-json

# Run specific test scripts
python test_invoice_processing.py
python test_creative_coop.py
python test_integrated_main.py

# Test vendor-specific processing
python perfect_processing.py  # HarperCollins processing
```

## Architecture

**Single Function Design**: The entire application is implemented as one Cloud Function (`process_invoice` in `main.py`) that handles:
1. Webhook processing (Trello integration)
2. PDF download from provided URL
3. Document AI processing for data extraction
4. Data transformation and normalization
5. Google Sheets integration for output

**Multi-Layer Data Extraction Strategy**:
- Primary: Entity-based extraction using Document AI entities
- Fallback: Table-based extraction parsing table structures
- Final: Text-based extraction using regex patterns

## Key Components

- `main.py` - Main Cloud Function with complete processing pipeline
- `document_ai_explorer.py` - Development tool for debugging Document AI output

### Core Functions (main.py)

### Main Processing
- `process_invoice()` - Main Cloud Function entry point with vendor detection
- `detect_vendor_type()` - Identifies vendor type for specialized processing

### Generic Processing (All Vendors)
- `extract_best_vendor()` - Vendor name extraction with confidence scoring
- `extract_line_items_from_entities()` - Primary line item extraction method
- `extract_line_items()` - Table-based fallback extraction
- `extract_line_items_from_text()` - Text-based fallback extraction
- `extract_short_product_code()` - Converts UPC/ISBN to short alphanumeric codes
- `extract_wholesale_price()` - Identifies wholesale vs retail pricing
- `extract_shipped_quantity()` - Parses quantity from various formats
- `extract_specific_invoice_number()` - Handles summary invoices with multiple invoice numbers

### Creative-Coop Specialized Processing
- `extract_creative_coop_quantity()` - Specialized quantity extraction for Creative-Coop invoices with shipped/back patterns
- `split_combined_line_item()` - Handles combined Document AI entities with multiple products
- `extract_upc_from_text()` - Enhanced UPC extraction for combined line items, searches after product codes
- `clean_item_description()` - Cleans descriptions by removing product codes and UPC codes
- `extract_description_from_full_text()` - Extracts actual product descriptions from full line text

### HarperCollins Specialized Processing
- `process_harpercollins_document()` - Perfect HarperCollins PO processing
- `get_harpercollins_book_data()` - ISBN/title/price mapping for HarperCollins books
- `extract_discount_percentage()` - Extracts discount from PO text
- `extract_order_number_improved()` - Extracts order numbers (e.g., NS4435067)
- `extract_order_date_improved()` - Extracts and formats order dates

## Required Environment Variables

```bash
GOOGLE_CLOUD_PROJECT_ID=your-project-id
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_CLOUD_LOCATION=us  # optional, defaults to 'us'
GOOGLE_SHEETS_SHEET_NAME=Sheet1  # optional, defaults to 'Sheet1'
```

## Invoice Processing Features

### Universal Features
- **Multi-format support**: Single invoices, summary invoices, book invoices
- **Product code normalization**: Converts long UPC/ISBN codes to short alphanumeric codes
- **Intelligent price calculation**: Distinguishes wholesale vs retail pricing
- **Quantity extraction**: Handles various quantity formats and units
- **Date standardization**: Normalizes date formats across invoice types
- **Vendor extraction**: Uses confidence scoring to identify best vendor match

### Creative-Coop Specialized Features
- **Combined entity processing**: Handles multiple products in single Document AI entities
- **Quantity pattern matching**: Extracts quantities from "shipped back unit" patterns (e.g., "8 0 lo each", "6 0 Set")
- **Split line item support**: Correctly processes combined line items with multiple product codes and UPC codes
- **Enhanced UPC extraction**: Searches for UPC codes positioned after product codes in document text
- **Pattern-specific extraction**: Uses context-aware matching for complex quantity patterns
- **Product-specific handling**: Special logic for known products like DF5599, DF6360, DF6802
- **Description extraction**: Extracts clean product descriptions from various text patterns

### HarperCollins Specialized Features
- **Perfect PO processing**: 100% accurate extraction of all 23 line items
- **ISBN; Title formatting**: Exact formatting with semicolon separator
- **50% discount calculation**: Automatic wholesale price calculation
- **Order number extraction**: Extracts NS-prefixed order numbers
- **Publisher identification**: Distinguishes HarperCollins from distributor (Anne McGilvray)

## Testing Strategy

The codebase uses a comprehensive testing approach:

- **Test files pattern**: `test_*.py` files for specific functionality testing
- **Debug files pattern**: `debug_*.py` files for investigating specific issues
- **Sample data**: Test invoices stored in `test_invoices/` directory with corresponding Document AI outputs
- **Iterative development**: Multiple `improved_processing*.py` files showing evolution of processing logic
- **Vendor-specific testing**: Separate test files for different vendor types (Creative-Coop, HarperCollins)

### Key Test Files
- `test_invoice_processing.py` - Basic invoice processing test
- `test_creative_coop.py` - Creative-Coop specific processing
- `test_integrated_main.py` - Integration testing
- `perfect_processing.py` - HarperCollins perfect processing implementation

## Deployment

```bash
# Deploy to Google Cloud Functions (update runtime as needed)
gcloud functions deploy process_invoice --runtime python312 --trigger-http --allow-unauthenticated

# Set required environment variables during deployment
gcloud functions deploy process_invoice \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT_ID=your-project-id,DOCUMENT_AI_PROCESSOR_ID=your-processor-id,GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
```

## File Structure

- `main.py` - Complete Cloud Function implementation
- `document_ai_explorer.py` - Debug tool for Document AI output analysis
- `requirements.txt` - Python dependencies
- `new_invoice.pdf` - Sample invoice for testing
- `new_invoice_docai_output.json` - Sample Document AI output for reference
- `perfect_processing.py` - HarperCollins-specific processing implementation
- `test_invoices/` - Test invoice files and Document AI outputs
- `test_*.py` - Various test scripts for specific functionality
- `debug_*.py` - Debug scripts for specific issues
- `improved_processing*.py` - Iterative processing improvements