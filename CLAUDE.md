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

This is an **Enterprise-Grade Invoice Processing Platform** built as a highly optimized Google Cloud Function. The system processes PDF invoices through multi-tier AI extraction (Gemini AI → Document AI → Fallbacks) and outputs structured data to Google Sheets.

Key capabilities:
- **Multi-vendor support**: HarperCollins, Creative-Coop, OneHundred80, Rifle Paper
- **85.7% accuracy** for Creative-Coop invoices with advanced pattern matching
- **Sub-60 second processing guarantee** with <800MB memory optimization
- **Zapier webhook integration** with 160-second timeout compatibility
- **Real-time monitoring** with business KPI tracking and automated alerts

## Development Commands

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.dev.txt  # Development
pip install -r requirements.txt       # Production only

# Format code
black .
isort . --profile black

# Run tests
pytest                                            # All tests
pytest test_scripts/test_invoice_processing.py   # Single test file
pytest-watch                                      # Watch mode

# Local development server
functions-framework --target=process_invoice --debug

# Test with sample data
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/invoice.pdf"}'

# Quick invoice testing workflow
python test_invoice.py InvoiceName     # Automated testing
./test_invoice.sh InvoiceName          # Bash alternative

# Debug Document AI output
export GOOGLE_CLOUD_PROJECT_ID="freckled-hen-analytics"
export DOCUMENT_AI_PROCESSOR_ID="be53c6e3a199a473"
export GOOGLE_CLOUD_LOCATION="us"
python document_ai_explorer.py test_invoices/InvoiceName.pdf --save-json

# Pre-commit hooks
pre-commit install                     # Setup hooks
pre-commit run --all-files            # Manual run
```

## Architecture

The system implements a **single Cloud Function** (`process_invoice` in `main.py`) with:

### Processing Pipeline
1. **Webhook Input**: Accepts PDF files via direct upload, form data, or JSON URLs from Zapier
2. **Vendor Detection**: Identifies vendor type for specialized processing
3. **Multi-tier Extraction**:
   - **Tier 1**: Gemini AI (currently disabled due to timeout)
   - **Tier 2**: Document AI Entities extraction
   - **Tier 3**: Document AI Tables processing  
   - **Tier 4**: Regex-based text extraction
4. **Data Output**: Writes to Google Sheets starting at column B

### Key Functions in main.py

**Main Processing**
- `process_invoice()` - Cloud Function entry point
- `detect_vendor_type()` - Vendor identification
- `process_with_gemini_first()` - Gemini AI processing (disabled)

**Vendor-Specific Processing**
- `process_creative_coop_document()` - Creative-Coop with multi-tier patterns
- `process_harpercollins_document()` - HarperCollins PO processing
- `process_onehundred80_document()` - OneHundred80 logic-based processing

**Data Extraction**
- `extract_line_items_from_entities()` - Primary extraction from Document AI
- `extract_line_items()` - Table-based fallback
- `extract_line_items_from_text()` - Regex-based fallback
- `extract_best_vendor()` - Vendor name with confidence scoring
- `extract_wholesale_price()` - Price type identification
- `extract_shipped_quantity()` - Quantity parsing

**Creative-Coop Enhanced Functions**
- `extract_creative_coop_product_mappings_corrected()` - Product-to-UPC mapping
- `extract_tabular_price_creative_coop()` - Tabular price extraction
- `extract_multi_tier_quantity_creative_coop()` - Multi-tier quantity parsing
- `split_combined_line_item()` - Handles combined Document AI entities

## Testing Strategy

### Quick Testing
```bash
# One-command invoice testing
python test_invoice.py InvoiceName

# Vendor-specific tests
python test_scripts/test_final_creative_coop.py
python test_scripts/perfect_processing.py        # HarperCollins
python test_scripts/test_onehundred80.py
```

### Test Categories
- **Core Tests** (`test_*.py`): Functionality and vendor processing
- **Validation** (`validate_*.py`): Production readiness and accuracy
- **Debug Scripts** (`debug_*.py`): Detailed issue investigation
- **Analysis** (`analyze_*.py`): Invoice pattern understanding

## Deployment

### Quick Production Deployment
```bash
# Pre-deployment validation
python test_scripts/production_deployment_final_check.py

# Deploy to Google Cloud Functions
gcloud functions deploy process_invoice \
    --gen2 \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=1GiB \
    --timeout=540s \
    --region=us-central1 \
    --entry-point=process_invoice \
    --source=. \
    --set-env-vars="GOOGLE_CLOUD_PROJECT_ID=freckled-hen-analytics,DOCUMENT_AI_PROCESSOR_ID=be53c6e3a199a473,GOOGLE_CLOUD_LOCATION=us,GOOGLE_SHEETS_SPREADSHEET_ID=1PdnZGPZwAV6AHXEeByhOlaEeGObxYWppwLcq0gdvs0E,GOOGLE_SHEETS_SHEET_NAME=Update 20230525" \
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"

# Post-deployment validation
python test_scripts/validate_production_deployment_readiness.py
```

### Environment Variables
```bash
GOOGLE_CLOUD_PROJECT_ID=freckled-hen-analytics
DOCUMENT_AI_PROCESSOR_ID=be53c6e3a199a473
GOOGLE_CLOUD_LOCATION=us
GOOGLE_SHEETS_SPREADSHEET_ID=1PdnZGPZwAV6AHXEeByhOlaEeGObxYWppwLcq0gdvs0E
GOOGLE_SHEETS_SHEET_NAME=Update 20230525
GEMINI_API_KEY=<stored in Secret Manager>
```

## Code Quality

- **Formatting**: Black (88 char line length) + isort with `--profile black`
- **Pre-commit hooks**: pytest, conventional commits, formatting, YAML validation
- **Testing**: 140+ test scripts with production validation suite

```bash
# Manual formatting
black . && isort . --profile black

# Run pre-commit hooks
pre-commit run --all-files
```

## Current Status

### ✅ Production Ready
- **Zapier Integration**: Fully functional with 160-second timeout handling
- **Document AI Processing**: Reliable multi-tier fallback system
- **Multi-vendor Support**: All major vendors working with pattern-based logic
- **Creative-Coop**: 85.7% accuracy with advanced multi-tier processing
- **Performance**: Sub-60 second processing with <800MB memory usage

### 🚧 Temporarily Disabled
- **Gemini AI**: Disabled due to Zapier timeout issues, falls back to Document AI immediately
- **Future Plan**: Two-tier architecture documented in `two-tier-fallback-plan.md`

### Known Issues
- **Cody Foster invoices**: Occasional date parsing failures (non-critical)
- **Large PDFs**: May take 60-90 seconds but complete successfully
- **Credential warnings**: Harmless metadata validation errors in logs

## File Structure

```
/
├── main.py                    # Cloud Function implementation
├── document_ai_explorer.py    # Document AI debug tool
├── test_invoice.py/.sh        # Automated testing scripts
├── requirements.txt           # Production dependencies
├── requirements.dev.txt       # Development dependencies
├── .pre-commit-config.yaml    # Pre-commit hooks config
├── .claude/                   # Claude Code configurations
│   ├── agents/               # Specialized agent instructions
│   └── tasks/                # Task tracking records
├── docs/                      # Documentation
│   ├── phases/               # Development phases
│   └── prds/                 # Product requirements
├── test_invoices/             # Sample PDFs and outputs
└── test_scripts/              # 140+ testing scripts
    ├── test_*.py             # Functionality tests
    ├── validate_*.py         # Production validation
    ├── debug_*.py            # Debugging tools
    └── analyze_*.py          # Pattern analysis
```

## Development Workflow

1. **Analyze invoice patterns**: Use `document_ai_explorer.py` and `analyze_*.py` scripts
2. **Implement logic-based solution**: Never hardcode values, use pattern matching
3. **Test with sample data**: Use `python test_invoice.py InvoiceName`
4. **Debug issues**: Use appropriate `debug_*.py` script
5. **Validate accuracy**: Compare with expected outputs in `test_invoices/`
6. **Run production validation**: Execute `validate_production_readiness.py`

## Important Notes

- **Always use algorithmic patterns**, never hardcode vendor-specific values
- **Prioritize Zapier compatibility** (160s timeout) over feature completeness
- **Test across multiple invoice formats** to ensure pattern robustness
- **Document AI is primary processor** since Gemini is temporarily disabled
- **Google Sheets output starts at column B** (no column A placeholder)
- **Service account needs `roles/secretmanager.secretAccessor`** for Gemini API key