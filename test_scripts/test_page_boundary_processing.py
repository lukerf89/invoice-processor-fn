#!/usr/bin/env python3
"""
Test script for Page Boundary Processing Validation - Task 207
Implements comprehensive multi-page document processing validation for Creative-Coop invoices.

Engineering Principles Applied:
- Principle 4: Performance optimization
- Principle 6: Comprehensive coverage
- Principle 8: Context-aware extraction

This test file implements the RED phase of TDD for page boundary processing validation.
"""

import json
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# Try to import psutil for memory testing, skip memory tests if not available
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from main import (  # Functions to be implemented
    ensure_complete_document_coverage,
    extract_products_from_page,
    track_products_per_page,
    validate_entity_page_assignment,
    validate_multi_page_processing,
    validate_page_boundary_continuity,
)


def load_test_document(filename):
    """Load test document from test_invoices directory"""
    test_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_invoices", filename
    )
    if not os.path.exists(test_path):
        pytest.skip(f"Test document {filename} not found")

    with open(test_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to mock Document AI object
    class MockDocument:
        def __init__(self, data):
            self.text = data.get("text", "")
            self.pages = []
            for page_data in data.get("pages", []):
                mock_page = MockPage(page_data)
                self.pages.append(mock_page)

    class MockPage:
        def __init__(self, page_data):
            self.page_number = page_data.get("page_number", 1)
            # Add other page attributes as needed

    return MockDocument(data)


def create_incomplete_test_document(page_numbers):
    """Create a mock document with only specified page numbers"""

    class MockDocument:
        def __init__(self, page_numbers):
            self.text = "Sample incomplete document text"
            self.pages = []
            for page_num in page_numbers:
                mock_page = MockPage(page_num)
                self.pages.append(mock_page)

    class MockPage:
        def __init__(self, page_number):
            self.page_number = page_number

    return MockDocument(page_numbers)


def create_corrupted_test_document():
    """Create a mock document with corrupted page data"""

    class MockDocument:
        def __init__(self):
            self.text = "Corrupted document text"
            self.pages = [None, "invalid", MockPage(1)]  # Mixed corrupted data

    class MockPage:
        def __init__(self, page_number):
            self.page_number = page_number

    return MockDocument()


def create_document_with_empty_pages(empty_page_numbers):
    """Create a mock document with specific pages having no product data"""

    class MockDocument:
        def __init__(self, empty_pages):
            self.text = "Document with some empty pages"
            self.pages = []
            self.empty_page_numbers = empty_pages
            for i in range(1, 11):  # 10 pages total
                mock_page = MockPage(i, i in empty_pages)
                self.pages.append(mock_page)

    class MockPage:
        def __init__(self, page_number, is_empty=False):
            self.page_number = page_number
            self.is_empty = is_empty

    return MockDocument(empty_page_numbers)


def create_document_with_inconsistent_numbering():
    """Create a mock document with inconsistent page numbering"""

    class MockDocument:
        def __init__(self):
            self.text = "Document with inconsistent page numbering"
            self.pages = []
            # Inconsistent numbering: 1, 3, 2, 5, 4
            for page_num in [1, 3, 2, 5, 4]:
                mock_page = MockPage(page_num)
                self.pages.append(mock_page)

    class MockPage:
        def __init__(self, page_number):
            self.page_number = page_number

    return MockDocument()


class TestPageBoundaryProcessingHappyPath:
    """Test happy path scenarios for page boundary processing validation"""

    def test_validates_complete_15_page_document_processing(self):
        """Test that complete 15-page document processing is validated correctly"""
        # Arrange - Load full 15-page CS003837319 document
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Validate multi-page processing
        validation_result = validate_multi_page_processing(cs_document)

        # Assert - Should process all 15 pages successfully
        assert (
            validation_result["total_pages"] == 15
        ), f"Expected 15 pages, got {validation_result['total_pages']}"
        assert (
            validation_result["pages_processed"] == 15
        ), f"Expected 15 pages processed, got {validation_result['pages_processed']}"
        assert (
            validation_result["total_products"] >= 125
        ), f"Expected minimum 125 products, got {validation_result['total_products']}"
        assert (
            validation_result["processing_complete"] == True
        ), "Processing should be complete"

    def test_tracks_products_per_page_distribution(self):
        """Test that product distribution across pages is tracked correctly"""
        # Arrange - Load multi-page document
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Track product distribution across pages
        products_per_page, total_products = track_products_per_page(cs_document)

        # Assert - Validate realistic distribution
        assert (
            len(products_per_page) == 15
        ), f"Expected data for 15 pages, got {len(products_per_page)}"
        assert (
            len(total_products) >= 125
        ), f"Expected minimum 125 total products, got {len(total_products)}"

        # No single page should have 0 products (except possibly first/last page)
        pages_with_products = sum(
            1 for count in products_per_page.values() if count > 0
        )
        assert (
            pages_with_products >= 10
        ), f"Expected at least 10 pages with products, got {pages_with_products}"

    def test_validates_page_boundary_continuity(self):
        """Test that products don't get split or lost at page boundaries"""
        # Arrange - Test data with clear page boundaries
        multi_page_text = """
        Page 1:
        XS9826A 6"H Metal Ballerina Ornament
        Quantity: 12

        Page 2:
        XS8911A 4-3/4"L x 3-1/2"W Product
        Quantity: 24

        Page 3:
        XS9482 8.25"H Wood Shoe Ornament
        Quantity: 8
        """

        # Act - Validate continuity across page boundaries
        boundary_validation = validate_page_boundary_continuity(multi_page_text)

        # Assert - Should identify all products across pages
        assert (
            boundary_validation["products_found"] == 3
        ), f"Expected 3 products, got {boundary_validation['products_found']}"
        assert (
            "XS9826A" in boundary_validation["product_list"]
        ), "XS9826A should be found"
        assert (
            "XS8911A" in boundary_validation["product_list"]
        ), "XS8911A should be found"
        assert "XS9482" in boundary_validation["product_list"], "XS9482 should be found"
        assert (
            boundary_validation["missing_products"] == 0
        ), "No products should be missing"

    def test_ensures_complete_document_coverage(self):
        """Test comprehensive document coverage validation"""
        # Arrange - Load CS document for coverage testing
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Ensure complete coverage
        coverage_result = ensure_complete_document_coverage(cs_document)

        # Assert - Complete coverage validation
        assert (
            coverage_result["coverage_percentage"] >= 90.0
        ), f"Expected 90%+ coverage, got {coverage_result['coverage_percentage']}%"
        assert (
            coverage_result["pages_covered"] >= 14
        ), f"Expected 14+ pages covered, got {coverage_result['pages_covered']}"
        assert (
            coverage_result["products_processed"] >= 125
        ), f"Expected 125+ products processed, got {coverage_result['products_processed']}"
        assert coverage_result["missing_entities"] == 0, "No entities should be missing"


class TestPageBoundaryProcessingErrorHandling:
    """Test error handling scenarios for page boundary processing"""

    def test_handles_incomplete_document_pages(self):
        """Test handling when some pages are missing or corrupted"""
        # Arrange - Create incomplete document (missing pages 2,4,6,8,10+)
        incomplete_document = create_incomplete_test_document([1, 3, 5, 7, 9])

        # Act
        validation_result = validate_multi_page_processing(incomplete_document)

        # Assert - Should detect incomplete processing
        assert (
            validation_result["total_pages"] == 5
        ), f"Expected 5 pages, got {validation_result['total_pages']}"
        assert (
            validation_result["pages_processed"] == 5
        ), f"Expected 5 pages processed, got {validation_result['pages_processed']}"
        assert (
            validation_result["processing_complete"] == False
        ), "Processing should be incomplete"
        assert "error_pages" in validation_result, "Should track error pages"

    def test_handles_corrupted_page_data(self):
        """Test handling of corrupted or malformed page data"""
        # Arrange - Create corrupted document
        corrupted_document = create_corrupted_test_document()

        # Act & Assert - Should handle gracefully
        try:
            validation_result = validate_multi_page_processing(corrupted_document)

            # Should handle gracefully
            assert (
                validation_result is not None
            ), "Should return result even with corrupted data"
            assert "error_pages" in validation_result, "Should track error pages"
            assert (
                validation_result["processing_complete"] == False
            ), "Processing should be incomplete"
        except Exception as e:
            # Should not crash, but if it does, fail the test
            assert False, f"Should handle corrupted data gracefully, but got: {e}"

    def test_handles_empty_pages(self):
        """Test processing when some pages have no product data"""
        # Arrange - Create document with empty pages
        document_with_empty_pages = create_document_with_empty_pages([2, 5, 8])

        # Act
        products_per_page, total_products = track_products_per_page(
            document_with_empty_pages
        )

        # Assert - Should handle empty pages correctly
        assert products_per_page[2] == 0, "Page 2 should have 0 products (empty page)"
        assert products_per_page[5] == 0, "Page 5 should have 0 products (empty page)"
        assert products_per_page[8] == 0, "Page 8 should have 0 products (empty page)"
        assert len(total_products) >= 0, "Should still track total products"


class TestPageBoundaryProcessingEdgeCases:
    """Test edge case scenarios for page boundary processing"""

    def test_validates_large_document_memory_usage(self):
        """Test memory usage validation for large 15-page documents"""
        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available, skipping memory test")

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process large document
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")
        validation_result = validate_multi_page_processing(cs_document)

        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assert - Memory usage should be reasonable
        assert (
            memory_increase < 500
        ), f"Memory increase {memory_increase}MB should be < 500MB"
        assert (
            validation_result["processing_complete"] == True
        ), "Processing should complete successfully"

    def test_validates_processing_time_constraints(self):
        """Test that multi-page processing completes within timeout constraints"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Time the processing
        start_time = time.time()
        validation_result = validate_multi_page_processing(cs_document)
        end_time = time.time()

        processing_time = end_time - start_time

        # Assert - Should complete within reasonable time
        assert (
            processing_time < 120
        ), f"Processing time {processing_time}s should be < 120s"
        assert validation_result is not None, "Should return validation result"

    def test_handles_page_numbering_inconsistencies(self):
        """Test handling when page numbers are inconsistent or missing"""
        # Arrange
        inconsistent_document = create_document_with_inconsistent_numbering()

        # Act
        validation_result = validate_multi_page_processing(inconsistent_document)

        # Assert - Should handle inconsistencies gracefully
        assert validation_result is not None, "Should return validation result"
        assert validation_result["pages_processed"] > 0, "Should process some pages"
        assert "error_pages" in validation_result, "Should track error pages"

    def test_validates_entity_page_assignment(self):
        """Test that Document AI entities are correctly assigned to pages"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Validate entity-to-page assignment
        entity_page_map = validate_entity_page_assignment(cs_document)

        # Assert - All entities should be assigned to valid pages
        for entity_id, page_num in entity_page_map.items():
            assert (
                1 <= page_num <= 15
            ), f"Page number {page_num} should be in range 1-15"
            assert (
                page_num is not None
            ), f"Entity {entity_id} should have valid page assignment"

        # Should have reasonable number of entities mapped
        assert (
            len(entity_page_map) >= 125
        ), f"Expected minimum 125 entities, got {len(entity_page_map)}"


# Additional test class for integration testing
class TestPageBoundaryIntegration:
    """Integration tests combining multiple page boundary processing features"""

    def test_end_to_end_cs_document_validation(self):
        """Test complete end-to-end validation of CS003837319 document"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Run complete validation pipeline
        validation_result = validate_multi_page_processing(cs_document)
        products_per_page, total_products = track_products_per_page(cs_document)
        coverage_result = ensure_complete_document_coverage(cs_document)

        # Assert - Complete validation
        assert (
            validation_result["processing_complete"] == True
        ), "Validation should complete"
        assert len(products_per_page) == 15, "Should track all 15 pages"
        assert (
            coverage_result["coverage_percentage"] >= 90.0
        ), "Should have 90%+ coverage"
        assert len(total_products) >= 125, "Should process 125+ products"

    def test_validates_processing_consistency(self):
        """Test that repeated processing produces consistent results"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error 2_docai_output.json")

        # Act - Run validation multiple times
        result1 = validate_multi_page_processing(cs_document)
        result2 = validate_multi_page_processing(cs_document)
        result3 = validate_multi_page_processing(cs_document)

        # Assert - Results should be consistent
        assert (
            result1["total_pages"] == result2["total_pages"] == result3["total_pages"]
        )
        assert (
            result1["total_products"]
            == result2["total_products"]
            == result3["total_products"]
        )
        assert (
            result1["processing_complete"]
            == result2["processing_complete"]
            == result3["processing_complete"]
        )


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
