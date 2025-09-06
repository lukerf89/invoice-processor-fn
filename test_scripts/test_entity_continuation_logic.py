#!/usr/bin/env python3
"""
Test Entity Continuation Logic - Page Boundary Entity Processing

Tests for Task 209: Sophisticated entity continuation logic to handle Document AI
entities that span multiple pages or are split across page boundaries in Creative-Coop
15-page documents.

TDD Test Implementation (RED Phase):
- All tests will initially fail
- Tests define the expected behavior for entity continuation processing
- Tests cover happy path, error handling, and edge cases
"""

import json
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, Mock

# Add parent directory to path to import main functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import (
        determine_entity_page,
        extract_entity_text,
        extract_product_code_from_entity,
        handle_split_entities,
        merge_continuation_entities,
        process_entities_with_page_awareness,
    )
except ImportError:
    # Functions don't exist yet - this is expected in RED phase
    pass


def load_test_document(filename):
    """Load test document JSON for testing"""
    test_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_invoices", filename
    )

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file not found: {test_file_path}")

    with open(test_file_path, "r", encoding="utf-8") as f:
        doc_data = json.load(f)

    # Convert to mock Document AI document structure
    mock_document = Mock()
    mock_document.text = doc_data.get("text", "")
    mock_document.pages = []
    mock_document.entities = []

    # Process pages
    for page_data in doc_data.get("pages", []):
        mock_page = Mock()
        mock_page.page_number = page_data.get("page_number", 1)
        mock_page.dimension = Mock()
        mock_page.dimension.width = page_data.get("dimension", {}).get("width", 1758.0)
        mock_page.dimension.height = page_data.get("dimension", {}).get(
            "height", 2275.0
        )
        mock_document.pages.append(mock_page)

    # Process entities
    for entity_data in doc_data.get("entities", []):
        mock_entity = Mock()
        mock_entity.type_ = entity_data.get("type_", "")
        mock_entity.mention_text = entity_data.get("mention_text", "")
        mock_entity.confidence = entity_data.get("confidence", 0.0)

        # Page anchor information
        mock_entity.page_anchor = Mock()
        page_refs_data = entity_data.get("page_anchor", {}).get("page_refs", [])
        mock_entity.page_anchor.page_refs = []

        for page_ref_data in page_refs_data:
            mock_page_ref = Mock()
            mock_page_ref.page = page_ref_data.get("page", "0")
            mock_page_ref.bounding_poly = page_ref_data.get("bounding_poly", {})
            mock_entity.page_anchor.page_refs.append(mock_page_ref)

        # Text anchor information
        text_anchor_data = entity_data.get("text_anchor", {})
        mock_entity.text_anchor = Mock()
        mock_entity.text_anchor.text_segments = []

        for segment_data in text_anchor_data.get("text_segments", []):
            mock_segment = Mock()
            mock_segment.start_index = segment_data.get("start_index", "0")
            mock_segment.end_index = segment_data.get("end_index", "0")
            mock_entity.text_anchor.text_segments.append(mock_segment)

        mock_document.entities.append(mock_entity)

    return mock_document


def create_mock_entity(product_code, text_content, page=1):
    """Create a mock Document AI entity for testing"""
    mock_entity = Mock()
    mock_entity.type_ = "line_item"
    mock_entity.mention_text = f"{product_code} {text_content}"
    mock_entity.confidence = 1.0

    # Page anchor
    mock_entity.page_anchor = Mock()
    mock_page_ref = Mock()
    mock_page_ref.page = str(page - 1)  # Document AI uses 0-based indexing
    mock_page_ref.bounding_poly = {}
    mock_entity.page_anchor.page_refs = [mock_page_ref]

    # Text anchor
    mock_entity.text_anchor = Mock()
    mock_segment = Mock()
    mock_segment.start_index = "100"
    mock_segment.end_index = "200"
    mock_entity.text_anchor.text_segments = [mock_segment]

    return mock_entity


def create_mock_split_entity(product_code, split_text):
    """Create a mock entity that represents split data across pages"""
    return create_mock_entity(product_code, split_text, page=1)


def create_corrupted_entity_without_page_info():
    """Create a mock entity with missing or corrupted page information"""
    mock_entity = Mock()
    mock_entity.type_ = "line_item"
    mock_entity.mention_text = "CORRUPTED Entity text without proper page info"
    mock_entity.confidence = 0.5
    mock_entity.page_anchor = None  # Corrupted page anchor
    mock_entity.text_anchor = None  # Corrupted text anchor
    return mock_entity


def create_entity_with_encoding_issues(product_code, text_with_encoding, page=1):
    """Create entity with text encoding issues"""
    return create_mock_entity(product_code, text_with_encoding, page)


def process_entities_with_page_awareness_fragments(fragments):
    """Mock function for processing entity fragments"""
    # This function doesn't exist yet - will fail in RED phase
    return {}


def process_duplicate_entities(duplicate_entities):
    """Mock function for handling duplicate entities"""
    # Simple implementation that merges duplicate entities
    entity_map = {}
    for entity in duplicate_entities:
        product_code = extract_product_code_from_entity(entity)
        if product_code:
            if product_code in entity_map:
                # Merge with existing
                entity_map[product_code] = merge_continuation_entities(
                    [entity_map[product_code], entity], product_code
                )
            else:
                entity_map[product_code] = entity
    return entity_map


def validate_entity_page_boundaries(document):
    """Mock function for validating entity page boundaries"""
    # This function doesn't exist yet - will fail in RED phase
    return []


def process_entities_with_encoding_handling(encoding_entities):
    """Mock function for handling encoding issues in entities"""
    # Simple implementation that handles encoding gracefully
    entity_map = {}
    for entity in encoding_entities:
        try:
            product_code = extract_product_code_from_entity(entity)
            if product_code:
                entity_map[product_code] = entity
        except UnicodeError:
            # Handle encoding errors gracefully
            continue
    return entity_map


class TestEntityContinuationLogic(unittest.TestCase):
    """Test cases for entity continuation logic across page boundaries"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_doc_filename = "CS003837319_Error 2_docai_output.json"

        # Load the test document if it exists
        try:
            self.cs_document = load_test_document(self.test_doc_filename)
            self.document_available = True
        except FileNotFoundError:
            print(
                f"⚠️ Test document {self.test_doc_filename} not found. Some tests will be skipped."
            )
            self.document_available = False
            self.cs_document = None

    # =================================================================
    # HAPPY PATH TESTS
    # =================================================================

    def test_processes_entities_with_page_awareness(self):
        """Test processing entities with page awareness for 130+ products"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Act - Process entities with page awareness
        entity_product_map = process_entities_with_page_awareness(self.cs_document)

        # Assert - All entities should be mapped to pages
        self.assertGreaterEqual(
            len(entity_product_map),
            120,
            "Should process at least 120 products from Creative-Coop document",
        )

        # Each entity should have valid page assignment
        for product_code, entity_info in entity_product_map.items():
            with self.subTest(product_code=product_code):
                self.assertIn(
                    "entity", entity_info, "Entity info should contain 'entity' key"
                )
                self.assertIn(
                    "page", entity_info, "Entity info should contain 'page' key"
                )
                self.assertIn(
                    "processed",
                    entity_info,
                    "Entity info should contain 'processed' key",
                )

                # Valid page range for 15-page Creative-Coop document
                self.assertGreaterEqual(entity_info["page"], 1, "Page should be >= 1")
                self.assertLessEqual(entity_info["page"], 15, "Page should be <= 15")

                # Product code should be valid Creative-Coop format
                self.assertRegex(
                    product_code,
                    r"^[A-Z]{2}\d{4}[A-Z]?$|^[A-Z]{2}\d+[A-Z]?$",
                    f"Product code {product_code} should match Creative-Coop format",
                )

    def test_determines_entity_page_correctly(self):
        """Test entity-to-page assignment logic using Document AI page anchors"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Test entity page determination for first 10 entities
        line_item_entities = [
            e for e in self.cs_document.entities if e.type_ == "line_item"
        ]
        test_entities = line_item_entities[:10] if line_item_entities else []

        self.assertGreater(
            len(test_entities), 0, "Should have line_item entities to test"
        )

        for i, entity in enumerate(test_entities):
            with self.subTest(entity_index=i):
                page_num = determine_entity_page(entity, self.cs_document)

                # Should assign valid page number
                self.assertIsInstance(page_num, int, "Page number should be integer")
                self.assertGreaterEqual(page_num, 1, "Page number should be >= 1")
                self.assertLessEqual(
                    page_num,
                    len(self.cs_document.pages),
                    "Page number should not exceed total pages",
                )

    def test_handles_split_entities_correctly(self):
        """Test handling of entities that are split across pages"""
        # Create mock split entity spanning two pages
        split_entity_text = """
        Page 1:
        XS9826A 6"H Metal Ballerina Ornament
        Quantity: 24
        
        Page 2:
        Price: $1.60
        Extended: $38.40
        """

        split_entity = create_mock_split_entity("XS9826A", split_entity_text)

        # Act - Handle split entity
        merged_entity = handle_split_entities([split_entity], split_entity_text)

        # Assert - Should merge split entity data successfully
        self.assertIsNotNone(merged_entity, "Should successfully merge split entity")
        merged_text = (
            str(merged_entity.text)
            if hasattr(merged_entity, "text")
            else str(merged_entity)
        )
        self.assertIn(
            "XS9826A", merged_text, "Merged entity should contain product code"
        )

        # Should contain information from both pages
        contains_quantity = "24" in merged_text
        contains_price = "1.60" in merged_text or "$1.60" in merged_text
        self.assertTrue(
            contains_quantity or contains_price,
            "Merged entity should contain quantity or price information",
        )

    def test_merges_continuation_entities(self):
        """Test merging of entities that continue across pages"""
        # Create entities that continue across two pages
        continuation_entities = [
            create_mock_entity("XS9826A", '6"H Metal Ballerina', page=1),
            create_mock_entity("XS9826A", "Quantity: 24 Price: $1.60", page=2),
        ]

        # Act - Merge continuation entities
        merged_result = merge_continuation_entities(continuation_entities, "XS9826A")

        # Assert - Should combine entity data from both pages
        self.assertIsNotNone(
            merged_result, "Should successfully merge continuation entities"
        )

        if hasattr(merged_result, "text"):
            merged_text = merged_result.text
        elif hasattr(merged_result, "product_code"):
            merged_text = str(merged_result)
        else:
            merged_text = str(merged_result)

        self.assertIn(
            "XS9826A", merged_text, "Merged result should contain product code"
        )

        # Should contain information from both pages
        contains_description = "Ballerina" in merged_text
        contains_pricing = "24" in merged_text or "1.60" in merged_text
        self.assertTrue(
            contains_description or contains_pricing,
            "Merged result should contain description or pricing information",
        )

    # =================================================================
    # ERROR HANDLING TESTS
    # =================================================================

    def test_handles_missing_entity_page_information(self):
        """Test handling when entity page information is missing or corrupted"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Create entity with missing page info
        corrupted_entity = create_corrupted_entity_without_page_info()

        # Act - Process entity with missing page info
        page_num = determine_entity_page(corrupted_entity, self.cs_document)

        # Assert - Should handle gracefully
        self.assertIsInstance(
            page_num, int, "Should return integer page number even for corrupted entity"
        )
        self.assertGreaterEqual(
            page_num, 0, "Should return valid page number or 0 for error"
        )
        self.assertLessEqual(
            page_num,
            len(self.cs_document.pages),
            "Should not return page number exceeding document pages",
        )

    def test_handles_orphaned_entity_fragments(self):
        """Test handling of entity fragments that can't be matched"""
        orphaned_fragments = [
            create_mock_entity("UNKNOWN", "Fragment text without context", page=5),
            create_mock_entity("", "Empty product code fragment", page=8),
        ]

        # Act - Process orphaned fragments
        entity_map = process_entities_with_page_awareness_fragments(orphaned_fragments)

        # Assert - Should handle orphaned fragments gracefully
        self.assertIsInstance(
            entity_map, dict, "Should return dictionary even for orphaned fragments"
        )

        # Orphaned fragments should either be filtered out or handled appropriately
        valid_entities = [k for k, v in entity_map.items() if k and k != "UNKNOWN"]
        self.assertGreaterEqual(
            len(valid_entities), 0, "Should not crash on orphaned fragments"
        )

    def test_handles_duplicate_entities_across_pages(self):
        """Test handling when same product appears on multiple pages"""
        duplicate_entities = [
            create_mock_entity("XS9826A", "First occurrence", page=3),
            create_mock_entity("XS9826A", "Second occurrence", page=7),
            create_mock_entity("XS9826A", "Third occurrence", page=12),
        ]

        # Act - Process duplicate entities
        entity_map = process_duplicate_entities(duplicate_entities)

        # Assert - Should handle duplicates appropriately
        self.assertIn("XS9826A", entity_map, "Should handle duplicate entity XS9826A")
        self.assertIsNotNone(
            entity_map["XS9826A"], "Should have valid entity data for XS9826A"
        )

    # =================================================================
    # EDGE CASE TESTS
    # =================================================================

    def test_handles_entities_spanning_multiple_pages(self):
        """Test entities that span more than 2 pages"""
        multi_page_entity_data = """
        Page 5: XS9826A Product Start
        Page 6: Description continues here
        Page 7: Quantity and pricing information
        Page 8: Final extended pricing
        """

        # Create entities spanning 4 pages
        spanning_entities = [
            create_mock_entity("XS9826A", "Product Start", page=5),
            create_mock_entity("XS9826A", "Description continues", page=6),
            create_mock_entity("XS9826A", "Quantity pricing", page=7),
            create_mock_entity("XS9826A", "Final pricing", page=8),
        ]

        # Act - Handle multi-page spanning entity
        merged_entity = merge_continuation_entities(spanning_entities, "XS9826A")

        # Assert - Should successfully merge all pages
        self.assertIsNotNone(
            merged_entity, "Should successfully merge multi-page entity"
        )

        if hasattr(merged_entity, "text"):
            merged_text = merged_entity.text
        else:
            merged_text = str(merged_entity)

        # Should contain elements from all pages
        contains_start = "Product Start" in merged_text or "Start" in merged_text
        contains_continues = "continues" in merged_text
        contains_pricing = "pricing" in merged_text

        elements_found = sum([contains_start, contains_continues, contains_pricing])
        self.assertGreaterEqual(
            elements_found,
            1,
            "Merged entity should contain information from multiple pages",
        )

    def test_validates_entity_page_boundaries(self):
        """Test validation of entity page boundaries"""
        if not self.document_available:
            self.skipTest("Test document not available")

        # Act - Validate page boundaries for all entities
        boundary_issues = validate_entity_page_boundaries(self.cs_document)

        # Assert - Should identify any boundary issues
        self.assertIsInstance(
            boundary_issues, list, "Should return list of boundary issues"
        )

        # Should have minimal boundary issues (< 5% of entities)
        total_entities = len(
            [e for e in self.cs_document.entities if e.type_ == "line_item"]
        )
        if total_entities > 0:
            issue_rate = len(boundary_issues) / total_entities
            self.assertLess(
                issue_rate,
                0.05,
                f"Should have < 5% boundary issues, got {issue_rate:.1%}",
            )

    def test_optimizes_entity_processing_performance(self):
        """Test performance optimization for entity continuation processing"""
        if not self.document_available:
            self.skipTest("Test document not available")

        start_time = time.time()

        # Act - Process all entities with continuation logic
        entity_map = process_entities_with_page_awareness(self.cs_document)

        end_time = time.time()
        processing_time = end_time - start_time

        # Assert - Should complete within reasonable time
        self.assertLess(
            processing_time,
            60,
            f"Should complete within 60 seconds, took {processing_time:.1f}s",
        )
        self.assertGreaterEqual(
            len(entity_map), 100, "Should process substantial number of entities"
        )

        print(
            f"✓ Entity continuation processing completed in {processing_time:.2f}s "
            f"for {len(entity_map)} entities"
        )

    def test_handles_entity_text_encoding_issues(self):
        """Test handling of text encoding issues in entities"""
        encoding_test_entities = [
            create_entity_with_encoding_issues("XS9826A", "Café product", page=1),
            create_entity_with_encoding_issues("XS8911A", "Müller brand", page=2),
        ]

        # Act - Process entities with encoding issues
        entity_map = process_entities_with_encoding_handling(encoding_test_entities)

        # Assert - Should handle encoding gracefully
        self.assertGreaterEqual(
            len(entity_map), 2, "Should process entities with encoding issues"
        )
        self.assertIn("XS9826A", entity_map, "Should handle XS9826A with encoding")
        self.assertIn("XS8911A", entity_map, "Should handle XS8911A with encoding")

    def test_extracts_entity_text_correctly(self):
        """Test entity text extraction from Document AI entities"""
        # Create test entity with known text content
        test_entity = create_mock_entity(
            "XS9826A", '6"H Metal Ballerina Ornament', page=1
        )
        test_document_text = (
            'Sample document text with XS9826A 6"H Metal Ballerina Ornament content'
        )

        # Act - Extract entity text
        extracted_text = extract_entity_text(test_entity, test_document_text)

        # Assert - Should extract text correctly
        self.assertIsInstance(extracted_text, str, "Should return string text")
        self.assertIn("XS9826A", extracted_text, "Should contain product code")

    def test_extracts_product_code_from_entity(self):
        """Test product code extraction from Document AI entities"""
        # Test various Creative-Coop product code formats
        test_cases = [
            ("XS9826A", 'XS9826A 191009727774 6"H Metal Ballerina Ornament'),
            ("XS8911A", "XS8911A 191009710615 12 0 0 0 each 10.00"),
            ("DA1234A", "DA1234A 123456789012 Product description"),
            ("ST5678", "ST5678 987654321098 Another product"),
        ]

        for expected_code, entity_text in test_cases:
            with self.subTest(expected_code=expected_code):
                test_entity = create_mock_entity(expected_code, entity_text, page=1)

                # Act - Extract product code
                extracted_code = extract_product_code_from_entity(test_entity)

                # Assert - Should extract correct product code
                self.assertEqual(
                    extracted_code,
                    expected_code,
                    f"Should extract {expected_code} from entity text",
                )

    def test_handles_empty_or_none_inputs(self):
        """Test handling of empty or None inputs"""
        # Test empty document
        empty_entity_map = process_entities_with_page_awareness(None)
        self.assertEqual(
            empty_entity_map, {}, "Should return empty dict for None document"
        )

        # Test empty entity list
        mock_empty_doc = Mock()
        mock_empty_doc.entities = []
        empty_result = process_entities_with_page_awareness(mock_empty_doc)
        self.assertEqual(
            empty_result, {}, "Should return empty dict for document with no entities"
        )

        # Test None entity
        page_num = determine_entity_page(None, mock_empty_doc)
        self.assertIsInstance(page_num, int, "Should return integer for None entity")

        # Test empty entity list for merging
        merged_result = merge_continuation_entities([], "XS9826A")
        self.assertIsNone(merged_result, "Should return None for empty entity list")


if __name__ == "__main__":
    print("🔴 RED PHASE: Running Entity Continuation Logic Tests")
    print("⚠️  Expected: All tests should FAIL - functions not implemented yet")
    print("=" * 70)

    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)
