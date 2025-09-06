#!/usr/bin/env python3
"""
Performance Optimization System Tests - Phase 1: RED (Failing Tests)

Test suite for Creative-Coop performance optimization system targeting <60 second processing
with memory efficiency, algorithm optimization, caching, and concurrent processing.
"""

import json
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add the parent directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from performance_optimizations import (
        ConcurrentPageProcessor,
        CreativeCoopPerformanceOptimizer,
        EarlyTerminationPatternFinder,
        IntelligentCachingSystem,
        MemoryOptimizationError,
        MemoryOptimizer,
        MemoryUsageTracker,
        OptimizedPatternCache,
        OptimizedProductCodeSearch,
        ParallelEntityProcessor,
        PerformanceError,
        StreamingDocumentProcessor,
    )
except ImportError:
    # These classes don't exist yet - that's expected for RED phase
    pass


class TestPerformanceOptimizationSystem(unittest.TestCase):
    """Test cases for the main performance optimization system."""

    def setUp(self):
        """Set up test environment."""
        self.test_invoice_small = "test_invoices/Creative-Coop_CI004848705.PDF"
        self.test_invoice_large = "test_invoices/CS003837319_Error 2.PDF"

        # Check if test files exist
        if not os.path.exists(self.test_invoice_small):
            self.skipTest(f"Test invoice {self.test_invoice_small} not found")
        if not os.path.exists(self.test_invoice_large):
            self.skipTest(f"Test invoice {self.test_invoice_large} not found")

    def test_creative_coop_processing_time_under_60_seconds(self):
        """Test that Creative-Coop processing completes within 60 seconds."""
        # Arrange
        performance_optimizer = CreativeCoopPerformanceOptimizer()
        target_time = 60  # seconds

        # Act
        start_time = time.time()
        result = performance_optimizer.process_optimized(self.test_invoice_large)
        processing_time = time.time() - start_time

        # Assert
        self.assertLess(
            processing_time,
            target_time,
            f"Processing took {processing_time:.2f}s, target: {target_time}s",
        )
        self.assertGreaterEqual(
            result["accuracy_score"],
            0.90,
            "Accuracy must be maintained during optimization",
        )
        self.assertGreaterEqual(
            len(result["line_items"]), 130, "All line items must be processed"
        )
        self.assertTrue(result["processing_successful"])

    def test_memory_usage_optimization(self):
        """Test that memory usage stays within optimized limits."""
        # Arrange
        memory_optimizer = MemoryOptimizer()
        memory_tracker = MemoryUsageTracker()

        # Act
        memory_tracker.start_tracking()
        result = memory_optimizer.process_with_memory_optimization(
            self.test_invoice_large
        )
        peak_memory = memory_tracker.get_peak_memory_mb()
        memory_tracker.stop_tracking()

        # Assert
        self.assertLess(
            peak_memory,
            800,
            f"Memory usage {peak_memory}MB exceeds optimized target of 800MB",
        )
        self.assertTrue(result["processing_successful"])
        self.assertGreaterEqual(result["memory_efficiency_score"], 0.85)

    def test_large_document_streaming_processing(self):
        """Test streaming processing for large documents."""
        # Arrange
        streaming_processor = StreamingDocumentProcessor()

        # Act
        start_time = time.time()
        result = streaming_processor.process_with_streaming(self.test_invoice_large)
        processing_time = time.time() - start_time

        # Assert
        self.assertLess(
            processing_time,
            90,
            "Large document streaming should complete in <90 seconds",
        )
        self.assertEqual(result["pages_processed"], 15)
        self.assertLess(
            result["memory_peak_mb"], 600, "Streaming should reduce memory usage"
        )

    def test_performance_optimization_failure_handling(self):
        """Test that performance optimization failures are handled gracefully."""
        # Arrange
        performance_optimizer = CreativeCoopPerformanceOptimizer()
        nonexistent_file = "nonexistent_invoice.pdf"

        # Act & Assert
        with self.assertRaises(PerformanceError):
            performance_optimizer.process_optimized(nonexistent_file)

    def test_performance_metrics_collection(self):
        """Test that performance metrics are properly collected."""
        # Arrange
        performance_optimizer = CreativeCoopPerformanceOptimizer()

        # Act
        result = performance_optimizer.process_optimized(self.test_invoice_small)

        # Assert
        self.assertIn("performance_metrics", result)
        metrics = result["performance_metrics"]
        self.assertIn("processing_time", metrics)
        self.assertIn("optimizations_applied", metrics)
        self.assertIsInstance(metrics["optimizations_applied"], list)
        self.assertGreater(len(metrics["optimizations_applied"]), 0)


class TestAlgorithmOptimization(unittest.TestCase):
    """Test cases for algorithm optimization components."""

    def test_optimized_regex_pattern_caching(self):
        """Test that compiled regex patterns are cached for performance."""
        # Arrange
        pattern_cache = OptimizedPatternCache()
        test_patterns = [
            r"(\w+)\s+(\d+)\s+(\d+)\s+\w+\s+each\s+\$(\d+\.\d{2})",
            r"INVOICE\s+#:\s*(\w+)",
            r"UPC:\s*(\d{12})",
        ]

        # Act - First compilation should cache patterns
        start_time = time.time()
        compiled_patterns = [
            pattern_cache.get_compiled_pattern(p) for p in test_patterns
        ]
        first_compilation_time = time.time() - start_time

        # Second access should be from cache (much faster)
        start_time = time.time()
        cached_patterns = [pattern_cache.get_compiled_pattern(p) for p in test_patterns]
        cache_access_time = time.time() - start_time

        # Assert
        self.assertLess(
            cache_access_time,
            first_compilation_time * 0.1,
            "Cached access should be 10x faster",
        )

        # Verify same pattern objects are returned
        for p1, p2 in zip(compiled_patterns, cached_patterns):
            self.assertIs(p1, p2, "Same pattern objects should be returned")

    def test_optimized_product_code_search(self):
        """Test optimized search algorithms for product codes."""
        # Arrange
        document_text = self._load_large_creative_coop_text()
        optimized_search = OptimizedProductCodeSearch()

        # Act
        start_time = time.time()
        product_codes = optimized_search.find_all_product_codes(document_text)
        search_time = time.time() - start_time

        # Assert
        self.assertLess(
            search_time, 5, "Optimized search should complete in <5 seconds"
        )
        self.assertGreaterEqual(
            len(product_codes), 130, "Should find all product codes"
        )
        for code in product_codes:
            self.assertGreaterEqual(len(code), 6, f"Valid product code found: {code}")

    def test_early_termination_optimization(self):
        """Test early termination for found patterns."""
        # Arrange
        test_text = "DF6802 8 0 lo each $12.50 found_pattern more_text..."
        pattern_finder = EarlyTerminationPatternFinder()

        # Act
        start_time = time.time()
        result = pattern_finder.find_first_matching_pattern(
            test_text, ["quantity_pattern", "price_pattern"]
        )
        search_time = time.time() - start_time

        # Assert
        self.assertEqual(result["pattern_found"], "quantity_pattern")
        self.assertLess(
            result["match_position"], 50, "Should find pattern early in text"
        )
        self.assertLess(search_time, 0.1, "Early termination should be very fast")

    def _load_large_creative_coop_text(self):
        """Load large Creative-Coop document text for testing."""
        # Mock large text content for testing
        return "DF6802 8 0 lo each $12.50\n" * 1000 + "ST1234 6 2 Set $8.75\n" * 500


class TestConcurrentProcessing(unittest.TestCase):
    """Test cases for concurrent processing optimization."""

    def setUp(self):
        """Set up test environment."""
        self.multi_page_document = "test_invoices/CS003837319_Error 2.PDF"
        if not os.path.exists(self.multi_page_document):
            self.skipTest(f"Multi-page document {self.multi_page_document} not found")

    def test_concurrent_page_processing(self):
        """Test concurrent processing of multiple pages."""
        # Arrange
        concurrent_processor = ConcurrentPageProcessor()

        # Act - Concurrent processing
        start_time = time.time()
        result = concurrent_processor.process_pages_concurrently(
            self.multi_page_document, max_workers=3
        )
        concurrent_time = time.time() - start_time

        # Sequential processing for comparison
        start_time = time.time()
        sequential_result = concurrent_processor.process_pages_sequentially(
            self.multi_page_document
        )
        sequential_time = time.time() - start_time

        # Assert
        self.assertLess(
            concurrent_time,
            sequential_time * 0.7,
            "Concurrent processing should be 30% faster",
        )
        self.assertEqual(
            result["accuracy_score"],
            sequential_result["accuracy_score"],
            "Accuracy should be maintained",
        )
        self.assertEqual(
            len(result["line_items"]),
            len(sequential_result["line_items"]),
            "Same number of items processed",
        )

    def test_parallel_entity_processing(self):
        """Test parallel processing of Document AI entities."""
        # Arrange
        entities = self._load_test_entities("CS003837319")
        parallel_processor = ParallelEntityProcessor()

        # Act - Parallel processing
        start_time = time.time()
        parallel_result = parallel_processor.process_entities_parallel(
            entities, max_workers=4
        )
        parallel_time = time.time() - start_time

        # Sequential processing for comparison
        start_time = time.time()
        sequential_result = parallel_processor.process_entities_sequential(entities)
        sequential_time = time.time() - start_time

        # Assert
        self.assertLess(
            parallel_time,
            sequential_time * 0.8,
            "Parallel processing should be 20% faster",
        )
        self.assertEqual(
            len(parallel_result),
            len(sequential_result),
            "Same number of entities processed",
        )

    def _load_test_entities(self, invoice_id):
        """Load test entities for parallel processing tests."""
        # Mock entities for testing
        return [{"type": "line_item", "text": f"Item {i}"} for i in range(100)]


class TestIntelligentCaching(unittest.TestCase):
    """Test cases for intelligent caching system."""

    def test_intelligent_caching_system(self):
        """Test intelligent caching for frequently accessed data."""
        # Arrange
        caching_system = IntelligentCachingSystem()
        test_invoice_id = "CS003837319"

        # Act - First access should cache the result
        start_time = time.time()
        first_result = caching_system.get_processed_data(test_invoice_id)
        first_access_time = time.time() - start_time

        # Second access should be from cache
        start_time = time.time()
        cached_result = caching_system.get_processed_data(test_invoice_id)
        cache_access_time = time.time() - start_time

        # Assert
        self.assertLess(
            cache_access_time,
            first_access_time * 0.1,
            "Cached access should be 10x faster",
        )
        self.assertEqual(
            first_result, cached_result, "Cached result should match original"
        )
        self.assertGreater(
            caching_system.cache_hit_rate(), 0.5, "Cache hit rate should be reasonable"
        )

    def test_cache_expiration_and_refresh(self):
        """Test cache expiration and refresh mechanisms."""
        # Arrange
        caching_system = IntelligentCachingSystem(cache_ttl=1)  # 1 second TTL
        test_key = "test_data"

        # Act - Store data in cache
        original_data = {"test": "data", "timestamp": time.time()}
        caching_system.set_cached_data(test_key, original_data)

        # Immediate access should return cached data
        cached_data = caching_system.get_cached_data(test_key)
        self.assertEqual(cached_data, original_data)

        # Wait for cache expiration
        time.sleep(1.1)

        # Access after expiration should return None or trigger refresh
        expired_data = caching_system.get_cached_data(test_key)

        # Assert
        self.assertTrue(
            expired_data is None or caching_system.is_cache_expired(test_key)
        )


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT_ID", "test-project")
    os.environ.setdefault("DOCUMENT_AI_PROCESSOR_ID", "test-processor")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us")

    unittest.main(verbosity=2)
