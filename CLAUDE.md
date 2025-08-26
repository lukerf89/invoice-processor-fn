# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL CODING PRINCIPLE

**NEVER hard-code solutions in main.py. ALWAYS find a logic method that produces the correct output.**

When processing invoices, you may encounter edge cases or specific formatting issues. The correct approach is to:
- ✅ Use regex patterns and logical rules
- ✅ Extract information from document text using pattern matching
- ✅ Create reusable functions that work across different invoices
- ✅ Implement context-aware processing that adapts to document structure

❌ **DO NOT:** Create if/else statements that check for specific product codes and manually assign values
❌ **DO NOT:** Hard-code expected outputs for specific items
❌ **DO NOT:** Use product-specific logic that won't work for other invoices

The goal is maintainable, scalable code that can handle new invoices without modification.

## Project Overview

This is a Google Cloud Function that processes invoices using Document AI. It receives webhook requests from Zapier (or legacy Trello) with PDF files or URLs, processes invoices, then writes extracted data to Google Sheets.

## Tech Stack

- **Runtime**: Python 3.12+ (originally 3.12.11)
- **Framework**: Google Cloud Functions with functions-framework
- **Cloud Services**: Google Cloud Document AI, Google Sheets API
- **Key Dependencies**: google-cloud-documentai, google-auth, google-api-python-client, requests, flask

## Development Commands

```bash
# Setup virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for development
pip install -r requirements.dev.txt

# Install only production dependencies
pip install -r requirements.txt

# Format code with Black and isort
black .
isort .

# Local development server
functions-framework --target=process_invoice --debug

# Test with sample data (JSON method)
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/invoice.pdf"}'

# Test with form data (Zapier method)
curl -X POST http://localhost:8080 \
  -F "file_url=https://example.com/invoice.pdf"

# Test with file upload (Zapier method)
curl -X POST http://localhost:8080 \
  -F "invoice_file=@/path/to/invoice.pdf"

# Debug Document AI output (requires environment variables)
python document_ai_explorer.py <pdf_file_path> [--save-json]

# Test with local sample invoice
python document_ai_explorer.py new_invoice.pdf --save-json

# Run specific test scripts
python test_scripts/test_invoice_processing.py
python test_scripts/test_creative_coop.py
python test_scripts/test_integrated_main.py

# Test vendor-specific processing
python test_scripts/perfect_processing.py  # HarperCollins processing
python test_scripts/test_final_creative_coop.py  # Creative-Coop final testing
python test_scripts/test_onehundred80.py  # OneHundred80 testing

# Run all vendor-specific tests
python test_scripts/test_final_creative_coop.py && python test_scripts/perfect_processing.py && python test_scripts/test_onehundred80.py

# Run tests with pytest
pytest

# Run tests in watch mode (re-runs on file changes)
pytest-watch

# Setup pre-commit hooks
pre-commit install

# Run pre-commit hooks manually
pre-commit run --all-files
```

## Architecture

**Single Function Design**: The entire application is implemented as one Cloud Function (`process_invoice` in `main.py`) that handles:
1. Webhook processing (Zapier integration with multiple input methods)
2. PDF file processing (direct upload or URL download)
3. Document AI processing for data extraction
4. Data transformation and normalization
5. Google Sheets integration for output

**Multi-Layer Data Extraction Strategy**:
- Primary: Entity-based extraction using Document AI entities
- Fallback: Table-based extraction parsing table structures
- Final: Text-based extraction using regex patterns

**Testing Philosophy**: 
- All processing logic must be algorithmic and pattern-based
- Test scripts validate logic works across different invoice formats
- Debug scripts help identify patterns for new invoice types
- No hardcoded product mappings or vendor-specific values

## Key Components

- `main.py` - Main Cloud Function with complete processing pipeline
- `document_ai_explorer.py` - Development tool for debugging Document AI output

### Core Functions (main.py)

### Main Processing
- `process_invoice()` - Main Cloud Function entry point with multi-input webhook support and vendor detection
- `detect_vendor_type()` - Identifies vendor type for specialized processing (HarperCollins, Creative-Coop, OneHundred80)

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
- `process_creative_coop_document()` - Comprehensive Creative-Coop processing with multi-tier pattern matching for wholesale pricing and ordered quantities
- `extract_creative_coop_product_mappings_corrected()` - Algorithmic product-to-UPC-to-description mapping with expanded search scope (8000 characters)
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

### OneHundred80 Specialized Processing
- `process_onehundred80_document()` - Logic-based OneHundred80 processing with UPC codes and date extraction
- `extract_oneHundred80_product_description()` - Extracts fuller product descriptions from document text using pattern matching

## Required Environment Variables

```bash
GOOGLE_CLOUD_PROJECT_ID=freckled-hen-analytics
DOCUMENT_AI_PROCESSOR_ID=be53c6e3a199a473
GOOGLE_CLOUD_LOCATION=us
GOOGLE_SHEETS_SPREADSHEET_ID=1PdnZGPZwAV6AHXEeByhOlaEeGObxYWppwLcq0gdvs0E
GOOGLE_SHEETS_SHEET_NAME=Update 20230525
```

## Webhook Integration

The Cloud Function supports three input methods for maximum Zapier compatibility:

1. **File Upload**: Direct PDF file upload via `invoice_file` form field
2. **Form Data**: PDF URL via `file_url` or `invoice_file` form fields
3. **JSON**: Legacy support for JSON payload with `file_url` field

### URL Download Features
- **Enhanced Trello authentication**: Multi-strategy approach with fallback methods for accessing Trello attachments
  - Session establishment by visiting Trello card page first
  - Browser-like headers with Sec-Fetch headers and referrer
  - URL manipulation fallbacks (removing /download/filename)
  - Auth header clearing as final fallback
  - Helpful error messages with suggestions for 401 errors
- **PDF validation**: Verifies downloaded content is actually a PDF file
- **Timeout protection**: 30-second timeout to prevent hanging requests
- **Redirect handling**: Supports automatic redirects for Trello URLs

All methods process the PDF through Document AI and output to Google Sheets.

## Invoice Processing Features

### Universal Features
- **Multi-input webhook support**: Handles file uploads, form data, and JSON URLs from Zapier
- **Enhanced Trello authentication**: Multi-strategy fallback system for accessing Trello attachments with comprehensive error handling
- **Multi-format support**: Single invoices, summary invoices, book invoices
- **Product code normalization**: Converts long UPC/ISBN codes to short alphanumeric codes
- **Intelligent price calculation**: Distinguishes wholesale vs retail pricing
- **Quantity extraction**: Handles various quantity formats and units
- **Date standardization**: Normalizes date formats across invoice types
- **Vendor extraction**: Uses confidence scoring to identify best vendor match

### Creative-Coop Specialized Features
- **Multi-tier pattern matching**: Three-tier system for extracting wholesale prices and ordered quantities from "ordered back unit unit_price wholesale amount" format
- **Systematic product processing**: Processes ALL products found in invoice mappings rather than selective processing
- **Wholesale price extraction**: Correctly identifies wholesale prices (4th number) vs unit prices (3rd number) in invoice patterns
- **Ordered quantity filtering**: Filters output to include only items with ordered quantities > 0
- **Combined entity processing**: Handles multiple products in single Document AI entities
- **Enhanced search scope**: Expanded search range to 8000 characters for comprehensive product mapping
- **Dynamic processing**: Uses actual invoice data rather than hardcoded product lists
- **85.7% accuracy**: Achieves 24/28 expected items with comprehensive pattern matching
- **Quantity pattern matching**: Extracts quantities from "shipped back unit" patterns (e.g., "8 0 lo each", "6 0 Set")
- **Split line item support**: Correctly processes combined line items with multiple product codes and UPC codes
- **Enhanced UPC extraction**: Searches for UPC codes positioned after product codes in document text
- **Pattern-specific extraction**: Uses context-aware matching for complex quantity patterns
- **Description extraction**: Extracts clean product descriptions from various text patterns

### HarperCollins Specialized Features
- **Perfect PO processing**: 100% accurate extraction of all 23 line items
- **ISBN; Title formatting**: Exact formatting with semicolon separator
- **50% discount calculation**: Automatic wholesale price calculation
- **Order number extraction**: Extracts NS-prefixed order numbers
- **Publisher identification**: Distinguishes HarperCollins from distributor (Anne McGilvray)

### OneHundred80 Specialized Features
- **Logic-based processing**: Uses pattern matching and regex for description enhancement (no hardcoded values)
- **UPC code extraction**: Automatically extracts and formats UPC codes from 12-digit patterns
- **Order date extraction**: Extracts order dates from document text using multiple patterns
- **Purchase order handling**: Uses purchase order number as invoice identifier
- **Multi-line description processing**: Intelligently merges multi-line descriptions while filtering table headers
- **Dimension formatting**: Fixes common formatting issues like "575"" → "5-5.75""
- **Context-aware extraction**: Pulls fuller descriptions from document text when Document AI descriptions are incomplete
- **Artifact removal**: Removes table headers, double commas, and other document processing artifacts

## Development Workflow

The codebase follows an iterative development pattern with extensive testing and debugging:

### File Patterns (in test_scripts/)
- **`test_*.py`**: Test scripts for specific functionality or vendor processing
- **`debug_*.py`**: Debug scripts for investigating specific issues with detailed output
- **`improved_*.py`**: Iterative improvements showing evolution of processing logic
- **`analyze_*.py`**: Analysis scripts for understanding invoice patterns and data
- **`validate_*.py`**: Validation scripts for checking processing accuracy

### Development Process
1. **Analyze**: Use `test_scripts/analyze_*.py` scripts to understand invoice patterns
2. **Debug**: Use `test_scripts/debug_*.py` scripts to investigate specific processing issues
3. **Test**: Use `test_scripts/test_*.py` scripts to validate processing logic
4. **Improve**: Create `test_scripts/improved_*.py` files for iterative enhancements
5. **Validate**: Use `test_scripts/validate_*.py` scripts to ensure accuracy

### Working with Test Data
- Test invoices are stored in `test_invoices/` directory
- Each invoice has a corresponding `*_docai_output.json` file with Document AI results
- CSV outputs are generated for analysis and validation
- Use `document_ai_explorer.py` to generate new Document AI outputs for testing

### Local Testing Workflow
1. **Test with existing sample**: `python test_scripts/test_invoice_processing.py`
2. **Test new invoice**: `python document_ai_explorer.py path/to/invoice.pdf --save-json`
3. **Test vendor-specific processing**: Run appropriate `test_scripts/test_*.py` script
4. **Debug issues**: Use corresponding `test_scripts/debug_*.py` script with detailed output
5. **Validate accuracy**: Compare results with expected output files

### Complete Invoice Testing Workflow

#### **Quick Shortcut (Recommended)**
Use the automated testing script for any invoice:
```bash
# One-command testing workflow
python test_invoice.py InvoiceName

# Example
python test_invoice.py Rifle_Paper_INV_J7XM9XQ3HB

# Alternative: Use bash script version
./test_invoice.sh InvoiceName
```

This automatically:
1. Sets required environment variables
2. Generates JSON from PDF using Document AI (if not already exists)
3. Processes JSON through main.py functions
4. Saves CSV output with extracted line items
5. Provides detailed processing summary with metrics

#### **Manual Step-by-Step Process**
For testing new invoices manually, follow this standardized process:

1. **Export PDF to JSON**:
   ```bash
   export GOOGLE_CLOUD_PROJECT_ID="freckled-hen-analytics"
   export DOCUMENT_AI_PROCESSOR_ID="be53c6e3a199a473"
   export GOOGLE_CLOUD_LOCATION="us"
   python document_ai_explorer.py test_invoices/InvoiceName.pdf --save-json
   ```
   This creates: `test_invoices/InvoiceName_docai_output.json`

2. **Process JSON to CSV**:
   Create a test script in `test_scripts/` or use existing processing functions:
   ```python
   # Load JSON, process through main.py functions, save as CSV
   # Example: test_scripts/test_rifle_paper_processing.py
   ```
   This creates: `test_invoices/InvoiceName_processed_output.csv`

3. **Verify Results**:
   - Check extracted line items match PDF content
   - Verify product codes, descriptions, quantities, and prices
   - Confirm vendor detection and invoice information

## Testing Strategy

The codebase uses a comprehensive testing approach:

### Key Test Files (in test_scripts/)
- `test_invoice_processing.py` - Basic invoice processing test
- `test_creative_coop.py` - Creative-Coop specific processing
- `test_integrated_main.py` - Integration testing
- `test_final_creative_coop.py` - Final Creative-Coop testing with accuracy metrics
- `test_onehundred80.py` - OneHundred80 specialized processing test
- `perfect_processing.py` - HarperCollins perfect processing implementation

### Debug Files (in test_scripts/)
- `debug_creative_coop_prices_qtys.py` - Debug tool for Creative-Coop pricing and quantity patterns
- `debug_quantities.py` - Debug quantity extraction logic
- `debug_descriptions.py` - Debug description extraction
- `debug_position_mapping.py` - Debug product position mapping

## Code Quality & Linting

The project uses automated code formatting and quality checks:

- **Black**: Code formatter with line length 88 (Python standard)
- **isort**: Import sorting, configured to work with Black
- **Pre-commit hooks**: Automated checks on commit including:
  - pytest tests
  - Conventional commits format
  - Trailing whitespace removal
  - End of file fixer
  - Large file checks
  - Black and isort formatting

**GitHub Actions**: CI/CD pipeline runs Black and isort checks on push/PR

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
- `test_invoice.py` - **Automated testing workflow shortcut script**
- `test_invoice.sh` - Bash version of automated testing workflow
- `requirements.txt` - Python dependencies
- `CLAUDE.md` - Project documentation and guidance
- `new_invoice.pdf` - Sample invoice for testing
- `new_invoice_docai_output.json` - Sample Document AI output for reference
- `test_invoices/` - Test invoice files and Document AI outputs
- `test_scripts/` - All testing, debugging, and development scripts
  - `test_*.py` - Various test scripts for specific functionality
  - `debug_*.py` - Debug scripts for specific issues
  - `improved_*.py` - Iterative processing improvements
  - `analyze_*.py` - Analysis scripts for understanding patterns
  - `validate_*.py` - Validation scripts for accuracy checking
  - `perfect_processing.py` - HarperCollins-specific processing implementation
