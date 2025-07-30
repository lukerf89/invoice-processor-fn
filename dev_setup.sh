#!/bin/bash
# dev_setup.sh - Development environment configuration for test-invoice-processor-fn

echo "🚀 Setting up development environment for invoice processor testing..."
echo "=================================================="

# Development environment variables (TEST ENVIRONMENT)
export GOOGLE_CLOUD_PROJECT_ID="freckled-hen-analytics"
export DOCUMENT_AI_PROCESSOR_ID="be53c6e3a199a473"
export GOOGLE_CLOUD_LOCATION="us"
export GOOGLE_SHEETS_SPREADSHEET_ID="1cYfpnM_CjgdV1j9hlY-2l0QJMYDWB_hCeXb9KGbgwEo"
export GOOGLE_SHEETS_SHEET_NAME="TEST"

echo "✅ Development environment configured!"
echo "Project ID: $GOOGLE_CLOUD_PROJECT_ID"
echo "Processor ID: $DOCUMENT_AI_PROCESSOR_ID"  
echo "Spreadsheet ID: $GOOGLE_SHEETS_SPREADSHEET_ID"
echo "Sheet Name: $GOOGLE_SHEETS_SHEET_NAME"
echo ""
echo "🔗 Test Spreadsheet: https://docs.google.com/spreadsheets/d/1cYfpnM_CjgdV1j9hlY-2l0QJMYDWB_hCeXb9KGbgwEo/edit"
echo ""
echo "🧪 Ready for testing! Try:"
echo "  python test_invoice.py InvoiceName"
echo "  python test_scripts/test_final_creative_coop.py"
echo "=================================================="