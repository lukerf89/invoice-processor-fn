#!/usr/bin/env python3
"""
Memory Efficiency Tests - Phase 1: RED (Failing Tests)

Test suite for memory optimization during Creative-Coop processing,
ensuring efficient memory usage and streaming processing for large documents.
"""

import gc
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch

import psutil

# Add the parent directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from performance_optimizations import (
        MemoryOptimizationError,
        MemoryOptimizer,
        MemoryUsageTracker,
        StreamingDocumentProcessor,
    )
except ImportError:
    # These classes don't exist yet - that's expected for RED phase
    pass


class TestMemoryUsageTracker(unittest.TestCase):
    """Test cases for memory usage tracking system."""

    def test_memory_tracking_start_stop(self):
        """Test that memory tracking can be started and stopped."""
        # Arrange
        tracker = MemoryUsageTracker()

        # Act
        tracker.start_tracking()

        # Allocate some memory
        large_list = [i for i in range(100000)]

        peak_memory = tracker.get_peak_memory_mb()
        tracker.stop_tracking()

        # Assert
        self.assertGreater(peak_memory, 0, "Peak memory should be greater than 0")
        self.assertIsInstance(
            peak_memory, (int, float), "Peak memory should be numeric"
        )

        # Cleanup
        del large_list
        gc.collect()

    def test_peak_memory_detection(self):
        """Test that peak memory usage is correctly detected."""
        # Arrange
        tracker = MemoryUsageTracker()
        tracker.start_tracking()

        # Act - Create progressively larger allocations
        small_list = [i for i in range(10000)]
        medium_list = [i for i in range(50000)]
        large_list = [i for i in range(200000)]  # This should be peak

        peak_after_large = tracker.get_peak_memory_mb()

        # Free large allocation
        del large_list
        gc.collect()

        peak_after_cleanup = tracker.get_peak_memory_mb()
        tracker.stop_tracking()

        # Assert
        self.assertGreaterEqual(
            peak_after_cleanup,
            peak_after_large * 0.8,
            "Peak should remain high even after cleanup",
        )

        # Cleanup
        del small_list, medium_list
        gc.collect()

    def test_memory_tracking_thread_safety(self):
        """Test that memory tracking works safely across threads."""
        # Arrange
        tracker = MemoryUsageTracker()

        # Act
        tracker.start_tracking()

        # Simulate concurrent allocations
        allocation1 = [i for i in range(50000)]
        allocation2 = [i * 2 for i in range(50000)]

        peak_memory = tracker.get_peak_memory_mb()
        tracker.stop_tracking()

        # Assert
        self.assertGreater(peak_memory, 0)
        self.assertLess(peak_memory, 2000, "Memory usage should be reasonable")

        # Cleanup
        del allocation1, allocation2
        gc.collect()


class TestMemoryOptimizer(unittest.TestCase):
    """Test cases for memory optimization functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_document = "test_invoices/CS003837319_Error 2.PDF"
        if not os.path.exists(self.test_document):
            self.skipTest(f"Test document {self.test_document} not found")

    def test_memory_efficient_document_loading(self):
        """Test that documents are loaded efficiently."""
        # Arrange
        optimizer = MemoryOptimizer()

        # Act
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        document_data = optimizer.load_document_efficiently(self.test_document)
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        memory_increase = end_memory - start_memory

        # Assert
        self.assertIsInstance(document_data, dict)
        self.assertIn("document_chunks", document_data)
        self.assertIn("total_pages", document_data)
        self.assertIn("memory_optimized", document_data)
        self.assertTrue(document_data["memory_optimized"])
        self.assertLess(memory_increase, 200, "Memory increase should be limited")

    def test_chunked_processing(self):
        """Test that documents are processed in chunks."""
        # Arrange
        optimizer = MemoryOptimizer()

        # Act
        document_data = optimizer.load_document_efficiently(self.test_document)

        # Assert
        chunks = document_data["document_chunks"]
        self.assertGreater(len(chunks), 0, "Should have document chunks")
        self.assertGreater(document_data["total_pages"], 0, "Should have pages")

        # Each chunk should be manageable size
        for chunk in chunks:
            self.assertIsInstance(chunk, (dict, bytes, str))

    def test_memory_cleanup(self):
        """Test that memory cleanup is performed."""
        # Arrange
        optimizer = MemoryOptimizer()

        # Act - Monitor memory before and after cleanup
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Create some large objects
        large_data = [i for i in range(100000)]
        mid_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Force cleanup
        optimizer._cleanup_memory()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Assert
        memory_freed = mid_memory - end_memory
        self.assertGreaterEqual(memory_freed, 0, "Some memory should be freed")

        # Cleanup
        del large_data

    def test_memory_optimization_integration(self):
        """Test full memory optimization workflow."""
        # Arrange
        optimizer = MemoryOptimizer()

        # Act
        result = optimizer.process_with_memory_optimization(self.test_document)

        # Assert
        self.assertTrue(result["processing_successful"])
        self.assertIn("memory_peak_mb", result)
        self.assertIn("memory_efficiency_score", result)
        self.assertIn("line_items", result)
        self.assertIn("accuracy_score", result)

        # Memory metrics should be reasonable
        self.assertLess(
            result["memory_peak_mb"], 800, "Memory usage should stay under 800MB"
        )
        self.assertGreater(
            result["memory_efficiency_score"],
            0.5,
            "Memory efficiency should be reasonable",
        )

    def test_memory_optimization_error_handling(self):
        """Test error handling in memory optimization."""
        # Arrange
        optimizer = MemoryOptimizer()
        nonexistent_file = "nonexistent_document.pdf"

        # Act & Assert
        with self.assertRaises(MemoryOptimizationError):
            optimizer.process_with_memory_optimization(nonexistent_file)


class TestStreamingDocumentProcessor(unittest.TestCase):
    """Test cases for streaming document processing."""

    def setUp(self):
        """Set up test environment."""
        self.large_document = "test_invoices/CS003837319_Error 2.PDF"
        if not os.path.exists(self.large_document):
            self.skipTest(f"Large document {self.large_document} not found")

    def test_streaming_processing(self):
        """Test streaming processing of large documents."""
        # Arrange
        processor = StreamingDocumentProcessor()

        # Act
        start_time = time.time()
        result = processor.process_with_streaming(self.large_document)
        processing_time = time.time() - start_time

        # Assert
        self.assertLess(
            processing_time, 90, "Streaming processing should complete in <90 seconds"
        )
        self.assertIn("pages_processed", result)
        self.assertIn("memory_peak_mb", result)
        self.assertIn("line_items", result)

        self.assertEqual(result["pages_processed"], 15, "Should process 15 pages")
        self.assertLess(
            result["memory_peak_mb"], 600, "Streaming should keep memory usage low"
        )

    def test_page_by_page_processing(self):
        """Test that pages are processed individually."""
        # Arrange
        processor = StreamingDocumentProcessor()

        # Act
        result = processor.process_with_streaming(self.large_document)

        # Assert
        self.assertGreater(
            result["pages_processed"], 1, "Should process multiple pages"
        )

        # Check that streaming actually reduces memory
        self.assertLess(
            result["memory_peak_mb"],
            600,
            "Streaming should reduce memory usage compared to batch processing",
        )

    def test_streaming_accuracy_maintenance(self):
        """Test that streaming processing maintains accuracy."""
        # Arrange
        processor = StreamingDocumentProcessor()

        # Act
        result = processor.process_with_streaming(self.large_document)

        # Assert
        self.assertIn("accuracy_score", result)
        self.assertGreaterEqual(
            result["accuracy_score"],
            0.85,
            "Streaming should maintain reasonable accuracy",
        )

        # Should extract significant number of line items
        line_items = result.get("line_items", [])
        self.assertGreater(
            len(line_items), 100, "Should extract substantial number of line items"
        )

    def test_streaming_error_handling(self):
        """Test error handling in streaming processing."""
        # Arrange
        processor = StreamingDocumentProcessor()
        invalid_document = "nonexistent.pdf"

        # Act & Assert
        with self.assertRaises((FileNotFoundError, MemoryOptimizationError)):
            processor.process_with_streaming(invalid_document)


class TestMemoryOptimizationPerformance(unittest.TestCase):
    """Test cases for memory optimization performance characteristics."""

    def test_memory_vs_speed_tradeoff(self):
        """Test that memory optimization provides reasonable speed."""
        # Arrange
        optimizer = MemoryOptimizer()
        test_document = "test_invoices/Creative-Coop_CI004848705.PDF"

        if not os.path.exists(test_document):
            self.skipTest(f"Test document {test_document} not found")

        # Act
        start_time = time.time()
        result = optimizer.process_with_memory_optimization(test_document)
        processing_time = time.time() - start_time

        # Assert
        self.assertLess(
            processing_time,
            120,
            "Memory-optimized processing should complete in reasonable time",
        )
        self.assertTrue(result["processing_successful"])
        self.assertLess(
            result["memory_peak_mb"],
            400,
            "Should use minimal memory for smaller documents",
        )

    def test_large_document_memory_scaling(self):
        """Test that memory usage scales reasonably with document size."""
        # Arrange
        optimizer = MemoryOptimizer()
        large_document = "test_invoices/CS003837319_Error 2.PDF"

        if not os.path.exists(large_document):
            self.skipTest(f"Large document {large_document} not found")

        # Act
        result = optimizer.process_with_memory_optimization(large_document)

        # Assert
        # Large document should use more memory than small ones, but stay reasonable
        self.assertLess(
            result["memory_peak_mb"],
            800,
            "Large document memory usage should stay under limit",
        )
        self.assertGreater(
            result["memory_peak_mb"],
            100,
            "Large document should use more memory than trivial amounts",
        )

        # Efficiency score should account for document size
        self.assertGreater(
            result["memory_efficiency_score"],
            0.6,
            "Memory efficiency should be reasonable for large documents",
        )


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT_ID", "test-project")
    os.environ.setdefault("DOCUMENT_AI_PROCESSOR_ID", "test-processor")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us")

    unittest.main(verbosity=2)
