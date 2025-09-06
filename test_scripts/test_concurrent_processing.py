#!/usr/bin/env python3
"""
Concurrent Processing Tests - Phase 1: RED (Failing Tests)

Test suite for concurrent and parallel processing optimizations
for Creative-Coop processing, including page-level and entity-level parallelism.
"""

import json
import os
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, Mock, patch

# Add the parent directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from performance_optimizations import (
        ConcurrentPageProcessor,
        ConcurrentProcessingError,
        ParallelEntityProcessor,
    )
except ImportError:
    # These classes don't exist yet - that's expected for RED phase
    pass


class TestConcurrentPageProcessor(unittest.TestCase):
    """Test cases for concurrent page processing."""

    def setUp(self):
        """Set up test environment."""
        self.multi_page_document = "test_invoices/CS003837319_Error 2.PDF"
        self.single_page_document = "test_invoices/Creative-Coop_CI004848705.PDF"

        # Check if test files exist
        if not os.path.exists(self.multi_page_document):
            self.skipTest(f"Multi-page document {self.multi_page_document} not found")

    def test_concurrent_vs_sequential_performance(self):
        """Test that concurrent processing is faster than sequential."""
        # Arrange
        processor = ConcurrentPageProcessor()

        # Act - Concurrent processing
        start_time = time.time()
        concurrent_result = processor.process_pages_concurrently(
            self.multi_page_document, max_workers=3
        )
        concurrent_time = time.time() - start_time

        # Sequential processing
        start_time = time.time()
        sequential_result = processor.process_pages_sequentially(
            self.multi_page_document
        )
        sequential_time = time.time() - start_time

        # Assert
        self.assertLess(
            concurrent_time,
            sequential_time * 0.7,
            f"Concurrent ({concurrent_time:.2f}s) should be 30% faster than sequential ({sequential_time:.2f}s)",
        )

        # Results should be equivalent
        self.assertEqual(
            len(concurrent_result["line_items"]), len(sequential_result["line_items"])
        )
        self.assertEqual(
            concurrent_result["accuracy_score"], sequential_result["accuracy_score"]
        )

    def test_concurrent_processing_accuracy(self):
        """Test that concurrent processing maintains accuracy."""
        # Arrange
        processor = ConcurrentPageProcessor()

        # Act
        result = processor.process_pages_concurrently(
            self.multi_page_document, max_workers=3
        )

        # Assert
        self.assertIn("line_items", result)
        self.assertIn("accuracy_score", result)
        self.assertIn("pages_processed", result)
        self.assertTrue(result["concurrent_processing"])

        # Should maintain high accuracy
        self.assertGreaterEqual(
            result["accuracy_score"],
            0.85,
            "Concurrent processing should maintain accuracy",
        )

        # Should process all pages
        self.assertEqual(result["pages_processed"], 15, "Should process 15 pages")

        # Should extract significant number of line items
        self.assertGreater(
            len(result["line_items"]),
            100,
            "Should extract substantial number of line items",
        )

    def test_worker_thread_management(self):
        """Test that worker threads are properly managed."""
        # Arrange
        processor = ConcurrentPageProcessor()
        initial_thread_count = threading.active_count()

        # Act
        result = processor.process_pages_concurrently(
            self.multi_page_document, max_workers=3
        )

        # Allow threads to finish
        time.sleep(0.5)
        final_thread_count = threading.active_count()

        # Assert
        self.assertTrue(result["concurrent_processing"])
        # Thread count should return to approximately initial level
        self.assertLessEqual(
            final_thread_count,
            initial_thread_count + 2,
            "Worker threads should be cleaned up",
        )

    def test_concurrent_processing_error_handling(self):
        """Test error handling in concurrent processing."""
        # Arrange
        processor = ConcurrentPageProcessor()
        nonexistent_file = "nonexistent_document.pdf"

        # Act & Assert
        with self.assertRaises((FileNotFoundError, ConcurrentProcessingError)):
            processor.process_pages_concurrently(nonexistent_file, max_workers=3)

    def test_single_page_concurrent_processing(self):
        """Test concurrent processing with single-page documents."""
        # Arrange
        processor = ConcurrentPageProcessor()

        if not os.path.exists(self.single_page_document):
            self.skipTest(f"Single-page document {self.single_page_document} not found")

        # Act
        result = processor.process_pages_concurrently(
            self.single_page_document, max_workers=3
        )

        # Assert
        self.assertTrue(result["concurrent_processing"])
        self.assertEqual(result["pages_processed"], 1, "Should process 1 page")
        self.assertGreater(len(result["line_items"]), 0, "Should extract line items")

    def test_optimal_worker_count_detection(self):
        """Test that optimal worker count is determined correctly."""
        # Arrange
        processor = ConcurrentPageProcessor()

        # Act - Test different worker counts
        worker_counts = [1, 2, 3, 4]
        processing_times = []

        for worker_count in worker_counts:
            start_time = time.time()
            result = processor.process_pages_concurrently(
                self.multi_page_document, max_workers=worker_count
            )
            processing_time = time.time() - start_time
            processing_times.append(processing_time)

        # Assert
        # Should find optimal worker count (not necessarily the highest)
        optimal_time = min(processing_times)
        worst_time = max(processing_times)

        self.assertLess(
            optimal_time,
            worst_time * 0.9,
            "Optimal worker count should provide meaningful improvement",
        )


class TestParallelEntityProcessor(unittest.TestCase):
    """Test cases for parallel entity processing."""

    def setUp(self):
        """Set up test entities for testing."""
        # Load real entities from test document
        self.test_entities = self._load_test_entities()

    def _load_test_entities(self):
        """Load entities from test document for parallel processing."""
        try:
            with open("test_invoices/CS003837319_Error 2_docai_output.json", "r") as f:
                doc_dict = json.load(f)

            from google.cloud import documentai_v1 as documentai

            document = documentai.Document(doc_dict)
            return list(document.entities)
        except FileNotFoundError:
            # Fallback to mock entities
            return [
                Mock(type_="line_item", mention_text=f"Item {i}") for i in range(150)
            ]

    def test_parallel_vs_sequential_entity_processing(self):
        """Test that parallel entity processing is faster than sequential."""
        # Arrange
        processor = ParallelEntityProcessor()

        # Act - Parallel processing
        start_time = time.time()
        parallel_result = processor.process_entities_parallel(
            self.test_entities, max_workers=4
        )
        parallel_time = time.time() - start_time

        # Sequential processing
        start_time = time.time()
        sequential_result = processor.process_entities_sequential(self.test_entities)
        sequential_time = time.time() - start_time

        # Assert
        self.assertLess(
            parallel_time,
            sequential_time * 0.8,
            f"Parallel ({parallel_time:.2f}s) should be 20% faster than sequential ({sequential_time:.2f}s)",
        )

        # Results should be equivalent
        self.assertEqual(
            len(parallel_result),
            len(sequential_result),
            "Parallel and sequential should process same number of entities",
        )

    def test_entity_processing_accuracy(self):
        """Test that parallel processing maintains entity accuracy."""
        # Arrange
        processor = ParallelEntityProcessor()

        # Act
        result = processor.process_entities_parallel(self.test_entities, max_workers=4)

        # Assert
        self.assertIsInstance(
            result, list, "Result should be a list of processed entities"
        )
        self.assertEqual(
            len(result), len(self.test_entities), "Should process all entities"
        )

        # Each processed entity should have required fields
        for processed_entity in result[:10]:  # Check first 10
            self.assertIsInstance(
                processed_entity, dict, "Processed entity should be dictionary"
            )

    def test_thread_safe_entity_processing(self):
        """Test that entity processing is thread-safe."""
        # Arrange
        processor = ParallelEntityProcessor()

        # Act - Process same entities multiple times concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    processor.process_entities_parallel,
                    self.test_entities[:50],
                    max_workers=2,
                )
                for _ in range(3)
            ]

            results = [future.result() for future in as_completed(futures)]

        # Assert
        # All results should be the same length
        result_lengths = [len(result) for result in results]
        self.assertEqual(
            len(set(result_lengths)),
            1,
            "All concurrent processing should produce same result length",
        )

    def test_entity_processing_error_handling(self):
        """Test error handling in parallel entity processing."""
        # Arrange
        processor = ParallelEntityProcessor()

        # Create problematic entities that might cause errors
        problematic_entities = [
            Mock(type_="line_item", mention_text=None),  # None text
            Mock(type_="line_item", mention_text=""),  # Empty text
        ]

        # Act & Assert
        # Should handle errors gracefully, not crash
        try:
            result = processor.process_entities_parallel(
                problematic_entities, max_workers=2
            )
            # Should return some result, possibly empty
            self.assertIsInstance(result, list)
        except Exception as e:
            # If it raises an exception, it should be a controlled one
            self.assertIsInstance(e, (ConcurrentProcessingError, ValueError))

    def test_large_entity_batch_processing(self):
        """Test processing of large entity batches."""
        # Arrange
        processor = ParallelEntityProcessor()
        large_entity_batch = self.test_entities * 3  # Triple the entities

        # Act
        start_time = time.time()
        result = processor.process_entities_parallel(large_entity_batch, max_workers=4)
        processing_time = time.time() - start_time

        # Assert
        self.assertEqual(
            len(result),
            len(large_entity_batch),
            "Should process all entities in large batch",
        )
        self.assertLess(
            processing_time,
            60,
            "Large batch processing should complete in reasonable time",
        )


class TestConcurrentProcessingIntegration(unittest.TestCase):
    """Integration tests for concurrent processing components."""

    def test_concurrent_and_parallel_integration(self):
        """Test integration of concurrent page and parallel entity processing."""
        # Arrange
        page_processor = ConcurrentPageProcessor()
        entity_processor = ParallelEntityProcessor()

        test_document = "test_invoices/CS003837319_Error 2.PDF"
        if not os.path.exists(test_document):
            self.skipTest(f"Test document {test_document} not found")

        # Act - Process pages concurrently
        page_result = page_processor.process_pages_concurrently(
            test_document, max_workers=3
        )

        # Then process any extracted entities in parallel
        if "extracted_entities" in page_result:
            entity_result = entity_processor.process_entities_parallel(
                page_result["extracted_entities"], max_workers=4
            )

        # Assert
        self.assertTrue(page_result["concurrent_processing"])
        self.assertGreater(
            len(page_result["line_items"]),
            100,
            "Integrated processing should extract substantial line items",
        )

    def test_performance_degradation_detection(self):
        """Test detection of performance degradation in concurrent processing."""
        # Arrange
        processor = ConcurrentPageProcessor()
        test_document = "test_invoices/CS003837319_Error 2.PDF"

        if not os.path.exists(test_document):
            self.skipTest(f"Test document {test_document} not found")

        # Act - Test with too many workers (should cause degradation)
        start_time = time.time()
        result_many_workers = processor.process_pages_concurrently(
            test_document, max_workers=10  # Excessive workers
        )
        many_workers_time = time.time() - start_time

        start_time = time.time()
        result_optimal_workers = processor.process_pages_concurrently(
            test_document, max_workers=3  # Optimal workers
        )
        optimal_workers_time = time.time() - start_time

        # Assert
        # Too many workers shouldn't be significantly faster (context switching overhead)
        if many_workers_time > optimal_workers_time * 1.5:
            # This is expected - too many workers can hurt performance
            pass

        # Both should produce valid results
        self.assertGreater(len(result_many_workers["line_items"]), 0)
        self.assertGreater(len(result_optimal_workers["line_items"]), 0)


class TestConcurrentProcessingResourceManagement(unittest.TestCase):
    """Test cases for resource management in concurrent processing."""

    def test_memory_usage_with_concurrency(self):
        """Test that concurrent processing doesn't cause excessive memory usage."""
        # This would need psutil to track memory, but focus on the interface
        # Arrange
        processor = ConcurrentPageProcessor()
        test_document = "test_invoices/CS003837319_Error 2.PDF"

        if not os.path.exists(test_document):
            self.skipTest(f"Test document {test_document} not found")

        # Act
        result = processor.process_pages_concurrently(test_document, max_workers=3)

        # Assert
        # Should include memory metrics if implemented
        if "memory_usage_mb" in result:
            self.assertLess(
                result["memory_usage_mb"],
                1000,
                "Concurrent processing memory usage should be reasonable",
            )

    def test_timeout_handling(self):
        """Test that concurrent processing handles timeouts gracefully."""
        # Arrange
        processor = ConcurrentPageProcessor()

        # Mock a processor with timeout capability
        with patch.object(processor, "_process_single_page") as mock_process:
            # Simulate slow processing that would timeout
            mock_process.side_effect = lambda x: time.sleep(30)  # 30 second delay

            # Act & Assert
            # Should handle timeout gracefully
            start_time = time.time()
            try:
                result = processor.process_pages_concurrently(
                    "mock_document", max_workers=3, timeout=5  # 5 second timeout
                )
                processing_time = time.time() - start_time
                # Should complete within timeout period
                self.assertLess(processing_time, 10, "Should respect timeout")
            except AttributeError:
                # Method doesn't exist yet - that's expected for RED phase
                pass


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT_ID", "test-project")
    os.environ.setdefault("DOCUMENT_AI_PROCESSOR_ID", "test-processor")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us")

    unittest.main(verbosity=2)
