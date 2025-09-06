#!/usr/bin/env python3
"""
Test script for Memory-Efficient Large Document Processing - Task 208
Implements comprehensive memory optimization testing for 15-page Creative-Coop invoices.

Engineering Principles Applied:
- Principle 4: Performance optimization
- Principle 5: Error resilience
- Principle 6: Comprehensive coverage

This test file implements the RED phase of TDD for memory-efficient processing.
"""

import gc
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
    cleanup_processed_chunks,
    optimize_memory_usage,
    process_document_chunk,
    process_large_creative_coop_document,
)


def load_test_document(filename):
    """Load test document from test_invoices directory"""
    test_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_invoices", filename
    )
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test document {filename} not found at {test_path}")

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


def create_memory_intensive_test_document():
    """Create a mock document that simulates memory pressure"""

    class MockDocument:
        def __init__(self):
            # Create large text to simulate memory pressure
            self.text = "Large document text " * 100000  # ~2MB of text
            self.pages = []
            for i in range(20):  # More pages than usual
                mock_page = MockPage(i + 1)
                self.pages.append(mock_page)

    class MockPage:
        def __init__(self, page_number):
            self.page_number = page_number
            # Simulate page with memory-intensive data
            self.large_data = ["product_data"] * 1000

    return MockDocument()


class TestMemoryEfficientProcessingHappyPath:
    """Test happy path scenarios for memory-efficient processing"""

    def test_processes_15_page_document_within_memory_limit(self):
        """Test that 15-page document processing stays within memory limits"""
        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available, skipping memory test")

        # Arrange - Load full 15-page CS003837319 document
        try:
            cs_document = load_test_document("CS003837319_Error_2_docai_output.json")
        except FileNotFoundError:
            pytest.skip("Test document CS003837319_Error_2_docai_output.json not found")
        process = psutil.Process(os.getpid())

        # Get baseline memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Act - Process large document with memory optimization
        results = process_large_creative_coop_document(cs_document)

        # Check memory usage during processing
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = peak_memory - initial_memory

        # Assert - Should stay within reasonable memory bounds
        assert memory_used < 800, f"Memory usage {memory_used}MB should be < 800MB"
        assert len(results) >= 125, f"Expected 125+ products, got {len(results)}"
        assert all(
            "product_code" in item for item in results
        ), "All items should have product_code"

    def test_processes_document_in_chunks_successfully(self):
        """Test that chunked processing functionality works correctly"""
        # Arrange - Load test document
        try:
            cs_document = load_test_document("CS003837319_Error_2_docai_output.json")
        except FileNotFoundError:
            pytest.skip("Test document CS003837319_Error_2_docai_output.json not found")

        # Act - Process in 5-page chunks
        chunk_size = 5
        all_results = []

        total_pages = len(cs_document.pages)
        for chunk_start in range(0, total_pages, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_pages)
            chunk_pages = cs_document.pages[chunk_start:chunk_end]

            chunk_results = process_document_chunk(chunk_pages, cs_document.text)
            all_results.extend(chunk_results)

        # Assert - Chunked processing should be complete
        assert (
            len(all_results) >= 125
        ), f"Expected 125+ products, got {len(all_results)}"

        # Verify unique products (allowing for some overlap in chunked processing)
        unique_products = len(set(item["product_code"] for item in all_results))
        assert (
            unique_products >= 100
        ), f"Expected 100+ unique products, got {unique_products}"

    def test_optimizes_memory_usage_during_processing(self):
        """Test that memory optimization functions work correctly"""
        # Arrange - Load test document
        try:
            cs_document = load_test_document("CS003837319_Error_2_docai_output.json")
        except FileNotFoundError:
            pytest.skip("Test document CS003837319_Error_2_docai_output.json not found")

        # Act - Apply memory optimization
        optimized_document = optimize_memory_usage(cs_document)

        # Assert - Should maintain functionality while reducing memory footprint
        assert hasattr(optimized_document, "pages"), "Should preserve pages"
        assert hasattr(optimized_document, "text"), "Should preserve text"
        assert len(optimized_document.pages) == len(
            cs_document.pages
        ), "Should preserve page count"

        # Memory usage should be optimized (functionality preserved)
        assert optimized_document is not None, "Should return optimized document"

    def test_cleanup_processed_chunks_frees_memory(self):
        """Test that memory cleanup functionality works"""
        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available, skipping memory test")

        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Create and process chunks
        try:
            cs_document = load_test_document("CS003837319_Error_2_docai_output.json")
        except FileNotFoundError:
            pytest.skip("Test document CS003837319_Error_2_docai_output.json not found")
        processed_chunks = []

        for i in range(3):  # Process 3 chunks
            chunk_start = i * 5
            chunk_end = min(chunk_start + 5, len(cs_document.pages))
            chunk_pages = cs_document.pages[chunk_start:chunk_end]
            chunk_result = process_document_chunk(chunk_pages, cs_document.text)
            processed_chunks.append(chunk_result)

        memory_after_processing = process.memory_info().rss / 1024 / 1024

        # Act - Cleanup processed chunks
        cleanup_processed_chunks(processed_chunks)
        gc.collect()  # Force garbage collection

        memory_after_cleanup = process.memory_info().rss / 1024 / 1024

        # Assert - Memory should be managed appropriately
        memory_freed = memory_after_processing - memory_after_cleanup
        assert (
            memory_freed >= -50
        ), f"Memory should not increase significantly: {memory_freed}MB"  # Allow some variation


class TestMemoryEfficientProcessingErrorHandling:
    """Test error handling scenarios for memory-efficient processing"""

    def test_handles_memory_pressure_gracefully(self):
        """Test behavior when approaching memory limits"""
        # Arrange - Create memory-intensive document
        large_document = create_memory_intensive_test_document()

        try:
            # Act - Process under memory pressure
            results = process_large_creative_coop_document(large_document)

            # Assert - Should complete or fail gracefully
            assert results is not None, "Should return results or handle gracefully"

        except MemoryError:
            # Should implement graceful degradation, not crash
            assert (
                False
            ), "Should handle memory pressure gracefully, not crash with MemoryError"
        except Exception as e:
            # Other exceptions should be handled appropriately
            error_msg = str(e).lower()
            acceptable_errors = ["memory", "timeout", "too large", "limit exceeded"]
            assert any(
                keyword in error_msg for keyword in acceptable_errors
            ), f"Unexpected error type: {e}"

    def test_handles_corrupted_chunk_processing(self):
        """Test handling when some chunks are corrupted"""
        # Arrange - Create corrupted chunks
        cs_document = load_test_document("CS003837319_Error_2_docai_output.json")

        # Create mix of good and corrupted chunks
        good_chunk = cs_document.pages[0:5]
        corrupted_chunk = [
            None,
            "invalid",
            cs_document.pages[10],
        ]  # Mixed corrupted data

        # Act & Assert - Should handle corrupted chunks gracefully
        try:
            good_results = process_document_chunk(good_chunk, cs_document.text)
            assert len(good_results) > 0, "Should process good chunk successfully"

            corrupted_results = process_document_chunk(
                corrupted_chunk, cs_document.text
            )
            # Should return empty results or partial results, not crash
            assert isinstance(
                corrupted_results, list
            ), "Should return list even with corrupted data"

        except Exception as e:
            # Should handle gracefully, not crash unexpectedly
            error_msg = str(e).lower()
            acceptable_errors = [
                "invalid",
                "corrupted",
                "malformed",
                "processing error",
            ]
            assert any(
                keyword in error_msg for keyword in acceptable_errors
            ), f"Unexpected error handling corrupted chunk: {e}"

    def test_handles_empty_chunks(self):
        """Test processing when chunks are empty"""
        # Arrange - Empty chunk
        empty_chunk = []
        document_text = "Sample document text"

        # Act
        results = process_document_chunk(empty_chunk, document_text)

        # Assert - Should handle empty chunks gracefully
        assert isinstance(results, list), "Should return empty list for empty chunk"
        assert len(results) == 0, "Empty chunk should produce no results"

    def test_handles_chunk_size_variations(self):
        """Test processing with different chunk sizes"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error_2_docai_output.json")

        chunk_sizes = [1, 3, 7, 15, 20]  # Various sizes including larger than document

        for chunk_size in chunk_sizes:
            # Act - Process with different chunk sizes
            all_results = []
            total_pages = len(cs_document.pages)

            for chunk_start in range(0, total_pages, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_pages)
                chunk_pages = cs_document.pages[chunk_start:chunk_end]

                chunk_results = process_document_chunk(chunk_pages, cs_document.text)
                all_results.extend(chunk_results)

            # Assert - Should work with any reasonable chunk size
            assert (
                len(all_results) >= 100
            ), f"Chunk size {chunk_size} should produce reasonable results"


class TestMemoryEfficientProcessingEdgeCases:
    """Test edge case scenarios for memory-efficient processing"""

    def test_handles_very_large_document_text(self):
        """Test processing documents with very large text content"""

        # Arrange - Create document with large text
        class MockLargeDocument:
            def __init__(self):
                # Create very large document text (simulate OCR output)
                base_text = load_test_document(
                    "CS003837319_Error_2_docai_output.json"
                ).text
                self.text = base_text * 5  # 5x larger text
                self.pages = []
                for i in range(15):
                    mock_page = MockPage(i + 1)
                    self.pages.append(mock_page)

        class MockPage:
            def __init__(self, page_number):
                self.page_number = page_number

        large_document = MockLargeDocument()

        # Act - Process large text document
        results = process_large_creative_coop_document(large_document)

        # Assert - Should handle large text without issues
        assert len(results) >= 100, "Should extract products from large document"
        assert isinstance(results, list), "Should return list of results"

    def test_validates_processing_consistency_across_chunks(self):
        """Test that chunked processing produces consistent results"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error_2_docai_output.json")

        # Act - Process with different chunk sizes
        results_chunk_3 = []
        for chunk_start in range(0, len(cs_document.pages), 3):
            chunk_end = min(chunk_start + 3, len(cs_document.pages))
            chunk_pages = cs_document.pages[chunk_start:chunk_end]
            chunk_results = process_document_chunk(chunk_pages, cs_document.text)
            results_chunk_3.extend(chunk_results)

        results_chunk_5 = []
        for chunk_start in range(0, len(cs_document.pages), 5):
            chunk_end = min(chunk_start + 5, len(cs_document.pages))
            chunk_pages = cs_document.pages[chunk_start:chunk_end]
            chunk_results = process_document_chunk(chunk_pages, cs_document.text)
            results_chunk_5.extend(chunk_results)

        # Assert - Results should be reasonably consistent
        products_3 = set(item["product_code"] for item in results_chunk_3)
        products_5 = set(item["product_code"] for item in results_chunk_5)

        # Allow for some variation due to chunking boundaries
        overlap = len(products_3.intersection(products_5))
        total_unique = len(products_3.union(products_5))
        consistency_ratio = overlap / total_unique if total_unique > 0 else 0

        assert (
            consistency_ratio >= 0.8
        ), f"Results should be 80%+ consistent, got {consistency_ratio:.2%}"

    def test_processes_single_page_chunks(self):
        """Test processing when chunks are single pages"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error_2_docai_output.json")

        # Act - Process one page at a time
        all_results = []
        for page in cs_document.pages:
            chunk_results = process_document_chunk([page], cs_document.text)
            all_results.extend(chunk_results)

        # Assert - Single-page chunks should work
        assert len(all_results) >= 100, "Single-page chunks should produce results"
        assert all(
            "product_code" in item for item in all_results
        ), "All items should have product codes"


# Integration test class for complete workflow
class TestMemoryEfficientIntegration:
    """Integration tests for complete memory-efficient processing workflow"""

    def test_end_to_end_memory_optimized_processing(self):
        """Test complete memory-optimized processing workflow"""
        # Arrange
        cs_document = load_test_document("CS003837319_Error_2_docai_output.json")

        # Act - Complete workflow
        optimized_document = optimize_memory_usage(cs_document)
        results = process_large_creative_coop_document(optimized_document)

        # Assert - Complete workflow should succeed
        assert len(results) >= 125, "Should process expected number of products"
        assert all(
            isinstance(item, dict) for item in results
        ), "Results should be dictionaries"
        assert all(
            "product_code" in item for item in results
        ), "All items should have product codes"

    def test_validates_memory_cleanup_throughout_processing(self):
        """Test that memory cleanup works throughout the processing pipeline"""
        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available, skipping memory test")

        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Act - Process multiple documents to test cleanup
        for i in range(3):  # Process same document 3 times
            cs_document = load_test_document("CS003837319_Error_2_docai_output.json")
            optimized_document = optimize_memory_usage(cs_document)
            results = process_large_creative_coop_document(optimized_document)

            # Explicit cleanup
            del cs_document, optimized_document, results
            gc.collect()

        # Check final memory
        final_memory = process.memory_info().rss / 1024 / 1024
        total_memory_increase = final_memory - initial_memory

        # Assert - Memory should not continuously grow
        assert (
            total_memory_increase < 500
        ), f"Memory increase {total_memory_increase}MB should be reasonable"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
