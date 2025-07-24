#!/usr/bin/env python3
"""
Document AI Explorer - Comprehensive output viewer for Google Document AI

This script processes a PDF invoice through Document AI and displays
all available extracted information in a structured format.
"""

import json
import os

from google.cloud import documentai


def setup_client():
    """Initialize Document AI client with project configuration."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us")
    processor_id = os.getenv("DOCUMENT_AI_PROCESSOR_ID")

    if not project_id or not processor_id:
        raise ValueError(
            "Missing required environment variables: "
            "GOOGLE_CLOUD_PROJECT_ID and DOCUMENT_AI_PROCESSOR_ID"
        )

    client = documentai.DocumentProcessorServiceClient()
    processor_name = client.processor_path(project_id, location, processor_id)

    return client, processor_name


def display_entities(document):
    """Display all extracted entities with confidence scores."""
    print("\n" + "=" * 60)
    print("DOCUMENT ENTITIES")
    print("=" * 60)

    if not document.entities:
        print("No entities found.")
        return

    for i, entity in enumerate(document.entities, 1):
        print(f"\n[{i}] Entity: {entity.type_}")
        print(f"    Text: {entity.mention_text}")
        print(f"    Confidence: {entity.confidence:.3f}")

        if entity.normalized_value:
            print(f"    Normalized: {entity.normalized_value.text}")

        if hasattr(entity, "properties") and entity.properties:
            print("    Properties:")
            for prop in entity.properties:
                print(
                    f"      {prop.type_}: {prop.mention_text} (conf: {prop.confidence:.3f})"
                )


def display_form_fields(document):
    """Display form fields found in the document."""
    print("\n" + "=" * 60)
    print("FORM FIELDS")
    print("=" * 60)

    form_fields_found = False

    for page in document.pages:
        if hasattr(page, "form_fields") and page.form_fields:
            form_fields_found = True
            for i, field in enumerate(page.form_fields, 1):
                field_name = (
                    get_text_from_layout(field.field_name, document.text)
                    if field.field_name
                    else "Unknown"
                )
                field_value = (
                    get_text_from_layout(field.field_value, document.text)
                    if field.field_value
                    else "No value"
                )

                print(f"\n[{i}] {field_name}: {field_value}")
                if hasattr(field, "confidence"):
                    print(f"    Confidence: {field.confidence:.3f}")

    if not form_fields_found:
        print("No form fields found.")


def display_tables(document):
    """Display all tables found in the document."""
    print("\n" + "=" * 60)
    print("TABLES")
    print("=" * 60)

    tables_found = False

    for page_num, page in enumerate(document.pages, 1):
        if hasattr(page, "tables") and page.tables:
            tables_found = True
            for table_num, table in enumerate(page.tables, 1):
                print(f"\n--- Page {page_num}, Table {table_num} ---")

                # Extract table data
                table_data = []
                for row in table.table_rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = get_text_from_layout(cell.layout, document.text)
                        row_data.append(cell_text.strip())
                    table_data.append(row_data)

                # Display table
                if table_data:
                    # Calculate column widths
                    col_widths = []
                    if table_data:
                        max_cols = max(len(row) for row in table_data)
                        for col in range(max_cols):
                            max_width = max(
                                len(str(row[col])) if col < len(row) else 0
                                for row in table_data
                            )
                            col_widths.append(min(max_width, 30))  # Cap at 30 chars

                    # Print table rows
                    for row_num, row in enumerate(table_data):
                        row_str = " | ".join(
                            (
                                str(cell)[:30].ljust(col_widths[i])
                                if i < len(col_widths)
                                else str(cell)[:30]
                            )
                            for i, cell in enumerate(row)
                        )
                        print(f"  {row_str}")

                        # Add separator after header row
                        if row_num == 0 and len(table_data) > 1:
                            separator = "-+-".join("-" * width for width in col_widths)
                            print(f"  {separator}")

    if not tables_found:
        print("No tables found.")


def display_raw_text(document):
    """Display the raw extracted text."""
    print("\n" + "=" * 60)
    print("RAW EXTRACTED TEXT")
    print("=" * 60)
    print(document.text)


def display_page_info(document):
    """Display page-level information."""
    print("\n" + "=" * 60)
    print("PAGE INFORMATION")
    print("=" * 60)

    for i, page in enumerate(document.pages, 1):
        print(f"\nPage {i}:")
        print(f"  Dimensions: {page.dimension.width:.1f} x {page.dimension.height:.1f}")
        print(f"  Unit: {page.dimension.unit}")

        if hasattr(page, "blocks") and page.blocks:
            print(f"  Text blocks: {len(page.blocks)}")

        if hasattr(page, "paragraphs") and page.paragraphs:
            print(f"  Paragraphs: {len(page.paragraphs)}")

        if hasattr(page, "lines") and page.lines:
            print(f"  Lines: {len(page.lines)}")

        if hasattr(page, "tokens") and page.tokens:
            print(f"  Tokens: {len(page.tokens)}")


def get_text_from_layout(layout, document_text: str) -> str:
    """Extract text from layout object using text segments."""
    if not layout or not layout.text_anchor:
        return ""

    text_segments = []
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index) if segment.start_index else 0
        end_index = int(segment.end_index) if segment.end_index else len(document_text)
        text_segments.append(document_text[start_index:end_index])

    return "".join(text_segments)


def save_full_output(document, output_file: str):
    """Save complete document structure to JSON file."""
    # Convert document to dict format for JSON serialization
    doc_dict = documentai.Document.to_dict(document)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(doc_dict, f, indent=2, ensure_ascii=False)

    print(f"\nFull document structure saved to: {output_file}")


def process_invoice(file_path: str, save_json: bool = False):
    """Process invoice and display comprehensive output."""
    try:
        # Setup
        client, processor_name = setup_client()

        # Read file
        with open(file_path, "rb") as file:
            file_content = file.read()

        # Process document
        raw_document = documentai.RawDocument(
            content=file_content, mime_type="application/pdf"
        )

        request = documentai.ProcessRequest(
            name=processor_name, raw_document=raw_document
        )

        print(f"Processing: {file_path}")
        print(f"Processor: {processor_name}")

        result = client.process_document(request=request)
        document = result.document

        # Display all information
        display_page_info(document)
        display_entities(document)
        display_form_fields(document)
        display_tables(document)
        display_raw_text(document)

        # Save JSON if requested
        if save_json:
            json_filename = f"{os.path.splitext(file_path)[0]}_docai_output.json"
            save_full_output(document, json_filename)

        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error processing document: {e}")
        raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python document_ai_explorer.py <pdf_file_path> [--save-json]")
        print("\nEnvironment variables required:")
        print("  GOOGLE_CLOUD_PROJECT_ID")
        print("  DOCUMENT_AI_PROCESSOR_ID")
        print("  GOOGLE_CLOUD_LOCATION (optional, defaults to 'us')")
        sys.exit(1)

    pdf_path = sys.argv[1]
    save_json = "--save-json" in sys.argv

    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    process_invoice(pdf_path, save_json)
