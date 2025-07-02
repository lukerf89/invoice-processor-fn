# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Google Cloud Function that processes invoices using Document AI. The function receives webhook requests from Trello containing PDF URLs, downloads the PDFs, processes them through Google's Document AI service, and returns extracted text data.

## Architecture

**Single Function Design**: The entire application consists of one HTTP-triggered Cloud Function (`process_invoice`) in `main.py` that handles the complete workflow:

1. **Webhook Processing**: Receives Trello webhook with `file_url` parameter
2. **File Download**: Downloads PDF from the provided URL using requests
3. **Document AI Integration**: Processes PDF through Google Cloud Document AI service
4. **Response**: Returns extracted text as JSON

**Google Cloud Configuration**:
- Uses environment variables for secure credential management
- Default location: `us` (configurable via `GOOGLE_CLOUD_LOCATION`)
- Processor Type: Invoice processing (inferred from usage)

## Development Commands

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Local Development:**
```bash
functions-framework --target=process_invoice --debug
```

**Deploy to Google Cloud:**
```bash
gcloud functions deploy process_invoice --runtime python39 --trigger-http --allow-unauthenticated
```

**Test Locally:**
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/invoice.pdf"}'
```

## Key Implementation Details

- **Error Handling**: Function returns appropriate HTTP status codes (400 for missing parameters, 500 for processing errors)
- **Content Type**: Expects PDF files with MIME type `application/pdf`
- **Authentication**: Uses Google Cloud default credentials for Document AI access
- **Response Format**: Returns JSON with extracted text in `text` field

## Required Environment Variables

**Required:**
- `GOOGLE_CLOUD_PROJECT_ID`: Google Cloud project ID
- `DOCUMENT_AI_PROCESSOR_ID`: Document AI processor ID for invoice processing

**Optional:**
- `GOOGLE_CLOUD_LOCATION`: Document AI location (defaults to 'us')

**Authentication:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file (for local development)
- For Cloud deployment, uses default Google Cloud authentication