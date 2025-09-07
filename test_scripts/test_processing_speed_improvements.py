#!/usr/bin/env python3
"""
Processing Speed Improvements Tests - Phase 1: RED (Failing Tests)

Test suite for algorithm optimizations, caching systems, and speed improvements
for Creative-Coop processing, including regex caching and early termination.
"""

import os
import re
import sys
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add the parent directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from performance_optimizations import (
        AlgorithmicOptimizationError,
        EarlyTerminationPatternFinder,
        IntelligentCachingSystem,
        OptimizedPatternCache,
        OptimizedProductCodeSearch,
    )
except ImportError:
    # These classes don't exist yet - that's expected for RED phase
    pass


class TestOptimizedPatternCache(unittest.TestCase):
    """Test cases for regex pattern caching optimization."""

    def test_pattern_compilation_caching(self):
        """Test that regex patterns are compiled and cached."""
        # Arrange
        cache = OptimizedPatternCache()
        test_pattern = r"(\w+)\s+(\d+)\s+(\d+)\s+\w+\s+each\s+\$(\d+\.\d{2})"

        # Act - First access should compile and cache
        start_time = time.time()
        pattern1 = cache.get_compiled_pattern(test_pattern)
        first_time = time.time() - start_time

        # Second access should be from cache
        start_time = time.time()
        pattern2 = cache.get_compiled_pattern(test_pattern)
        cached_time = time.time() - start_time

        # Assert
        self.assertIs(pattern1, pattern2, "Same pattern object should be returned")
        self.assertLess(
            cached_time, first_time * 0.1, "Cached access should be 10x faster"
        )
        self.assertTrue(
            hasattr(pattern1, "match"), "Should return compiled regex pattern"
        )

    def test_multiple_pattern_caching(self):
        """Test caching of multiple different patterns."""
        # Arrange
        cache = OptimizedPatternCache()
        patterns = [
            r"INVOICE\s+#:\s*(\w+)",
            r"UPC:\s*(\d{12})",
            r"(\d+)\s+(\d+)\s+\w+\s+each",
            r"Date:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Total:\s*\$(\d+\.\d{2})",
        ]

        # Act
        compiled_patterns = []
        for pattern in patterns:
            compiled_patterns.append(cache.get_compiled_pattern(pattern))

        # Access again to test caching
        cached_patterns = []
        for pattern in patterns:
            cached_patterns.append(cache.get_compiled_pattern(pattern))

        # Assert
        self.assertEqual(len(compiled_patterns), 5, "Should compile all patterns")
        for i, (original, cached) in enumerate(zip(compiled_patterns, cached_patterns)):
            self.assertIs(original, cached, f"Pattern {i} should be cached")

    def test_cache_statistics(self):
        """Test cache statistics collection."""
        # Arrange
        cache = OptimizedPatternCache()
        patterns = [r"test\d+", r"another\w+", r"third.*pattern"]

        # Act
        for pattern in patterns:
            cache.get_compiled_pattern(pattern)  # First access
            cache.get_compiled_pattern(pattern)  # Second access (cache hit)

        stats = cache.get_cache_stats()

        # Assert
        self.assertIn("cached_patterns", stats)
        self.assertIn("total_accesses", stats)
        self.assertIn("cache_hit_rate", stats)

        self.assertEqual(stats["cached_patterns"], 3, "Should have 3 cached patterns")
        self.assertEqual(stats["total_accesses"], 6, "Should have 6 total accesses")
        self.assertGreater(
            stats["cache_hit_rate"], 0.4, "Should have reasonable hit rate"
        )

    def test_pattern_cache_memory_efficiency(self):
        """Test that pattern cache doesn't consume excessive memory."""
        # Arrange
        cache = OptimizedPatternCache()

        # Act - Cache many patterns
        patterns = [f"test_pattern_{i}\\d+" for i in range(100)]
        for pattern in patterns:
            cache.get_compiled_pattern(pattern)

        stats = cache.get_cache_stats()

        # Assert
        self.assertEqual(stats["cached_patterns"], 100, "Should cache all patterns")
        # Memory usage test would require more complex setup


class TestOptimizedProductCodeSearch(unittest.TestCase):
    """Test cases for optimized product code search algorithms."""

    def setUp(self):
        """Set up test data."""
        # Create realistic Creative-Coop document text
        self.test_text = (
            """
        DF6802 8 0 lo each $12.50
        ST1234 6 2 Set $8.75
        AB9876 12 0 pc $5.25
        XY5432 4 1 box $15.00
        """
            * 50
        )  # Multiply to create larger text

        self.large_test_text = self.test_text * 20  # Even larger for performance tests

    def test_product_code_search_accuracy(self):
        """Test that product code search finds all valid codes."""
        # Arrange
        search = OptimizedProductCodeSearch()

        # Act
        product_codes = search.find_all_product_codes(self.test_text)

        # Assert
        expected_codes = ["DF6802", "ST1234", "AB9876", "XY5432"]
        for expected_code in expected_codes:
            self.assertIn(
                expected_code,
                product_codes,
                f"Should find product code {expected_code}",
            )

        # Should find all instances (50 copies of each)
        code_counts = {}
        for code in product_codes:
            code_counts[code] = code_counts.get(code, 0) + 1

        for expected_code in expected_codes:
            self.assertEqual(
                code_counts[expected_code],
                50,
                f"Should find 50 instances of {expected_code}",
            )

    def test_search_performance(self):
        """Test that optimized search completes within time limits."""
        # Arrange
        search = OptimizedProductCodeSearch()

        # Act
        start_time = time.time()
        product_codes = search.find_all_product_codes(self.large_test_text)
        search_time = time.time() - start_time

        # Assert
        self.assertLess(
            search_time, 5, "Optimized search should complete in <5 seconds"
        )
        self.assertGreater(len(product_codes), 0, "Should find product codes")

    def test_search_algorithm_optimization(self):
        """Test that search uses optimized algorithms."""
        # Arrange
        search = OptimizedProductCodeSearch()

        # Act - Compare optimized vs naive search
        start_time = time.time()
        optimized_result = search.find_all_product_codes(self.test_text)
        optimized_time = time.time() - start_time

        start_time = time.time()
        naive_result = search.find_all_product_codes_naive(self.test_text)
        naive_time = time.time() - start_time

        # Assert
        self.assertEqual(
            len(optimized_result),
            len(naive_result),
            "Optimized should find same number of codes as naive",
        )
        self.assertLess(
            optimized_time,
            naive_time * 0.5,
            "Optimized should be at least 2x faster than naive",
        )

    def test_search_with_complex_patterns(self):
        """Test search with complex Creative-Coop specific patterns."""
        # Arrange
        search = OptimizedProductCodeSearch()
        complex_text = """
        Product DF6802: 8 0 lo each $12.50 wholesale amount
        Item ST1234: 6 2 Set $8.75 ordered back unit
        Code AB9876: 12 0 pc $5.25 shipped
        UPC: 123456789012 XY5432: 4 1 box $15.00
        """

        # Act
        product_codes = search.find_all_product_codes(complex_text)

        # Assert
        expected_codes = ["DF6802", "ST1234", "AB9876", "XY5432"]
        for code in expected_codes:
            self.assertIn(code, product_codes, f"Should find {code} in complex text")


class TestEarlyTerminationPatternFinder(unittest.TestCase):
    """Test cases for early termination pattern finding optimization."""

    def test_early_termination_performance(self):
        """Test that early termination improves search performance."""
        # Arrange
        finder = EarlyTerminationPatternFinder()
        test_text = "DF6802 8 0 lo each $12.50 found_pattern " + "filler_text " * 1000
        patterns = ["quantity_pattern", "price_pattern", "upc_pattern"]

        # Act
        start_time = time.time()
        result = finder.find_first_matching_pattern(test_text, patterns)
        search_time = time.time() - start_time

        # Assert
        self.assertLess(search_time, 0.1, "Early termination should be very fast")
        self.assertIn("pattern_found", result)
        self.assertIn("match_position", result)
        self.assertLess(result["match_position"], 50, "Should find pattern early")

    def test_first_match_priority(self):
        """Test that first matching pattern is returned."""
        # Arrange
        finder = EarlyTerminationPatternFinder()
        test_text = "quantity: 8 price: $12.50 upc: 123456"
        patterns = ["quantity_pattern", "price_pattern", "upc_pattern"]

        # Act
        result = finder.find_first_matching_pattern(test_text, patterns)

        # Assert
        self.assertEqual(
            result["pattern_found"],
            "quantity_pattern",
            "Should find first pattern in order",
        )

    def test_no_match_handling(self):
        """Test handling when no patterns match."""
        # Arrange
        finder = EarlyTerminationPatternFinder()
        test_text = "no matching patterns here"
        patterns = ["quantity_pattern", "price_pattern"]

        # Act
        result = finder.find_first_matching_pattern(test_text, patterns)

        # Assert
        self.assertIsNone(result["pattern_found"], "Should return None when no match")
        self.assertEqual(
            result["match_position"], -1, "Position should be -1 when no match"
        )

    def test_pattern_priority_order(self):
        """Test that pattern priority order is respected."""
        # Arrange
        finder = EarlyTerminationPatternFinder()
        # Text has price before quantity
        test_text = "price: $12.50 then quantity: 8"
        patterns = ["quantity_pattern", "price_pattern"]  # quantity first in list

        # Act - Should still find quantity first due to priority
        result = finder.find_first_matching_pattern(test_text, patterns)

        # Assert - Depends on implementation - could be either based on priority or position
        self.assertIn(result["pattern_found"], patterns)


class TestIntelligentCachingSystem(unittest.TestCase):
    """Test cases for intelligent caching system performance."""

    def test_cache_performance_improvement(self):
        """Test that caching provides significant performance improvement."""
        # Arrange
        caching_system = IntelligentCachingSystem()
        test_key = "performance_test"

        # Mock expensive computation
        def expensive_computation():
            time.sleep(0.1)  # Simulate 100ms computation
            return {"result": "expensive_data", "timestamp": time.time()}

        # Act - First access (cache miss)
        start_time = time.time()
        if not caching_system.get_cached_data(test_key):
            result = expensive_computation()
            caching_system.set_cached_data(test_key, result)
        first_access_time = time.time() - start_time

        # Second access (cache hit)
        start_time = time.time()
        cached_result = caching_system.get_cached_data(test_key)
        cache_access_time = time.time() - start_time

        # Assert
        self.assertIsNotNone(cached_result)
        self.assertLess(
            cache_access_time,
            first_access_time * 0.1,
            "Cache access should be 10x faster",
        )

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        # Arrange
        caching_system = IntelligentCachingSystem()
        test_keys = ["key1", "key2", "key3"]

        # Act - Prime cache
        for key in test_keys:
            caching_system.set_cached_data(key, f"data_{key}")

        # Mix of hits and misses
        cache_hits = 0
        total_requests = 10
        for i in range(total_requests):
            key = test_keys[i % len(test_keys)] if i < 6 else f"missing_key_{i}"
            result = caching_system.get_cached_data(key)
            if result:
                cache_hits += 1

        hit_rate = caching_system.cache_hit_rate()

        # Assert
        expected_hit_rate = 6 / total_requests  # 6 hits out of 10 requests
        self.assertAlmostEqual(hit_rate, expected_hit_rate, places=2)

    def test_cache_memory_efficiency(self):
        """Test that cache doesn't grow unbounded."""
        # Arrange
        caching_system = IntelligentCachingSystem(max_cache_size=10)

        # Act - Add more items than cache size
        for i in range(20):
            caching_system.set_cached_data(f"key_{i}", f"data_{i}")

        # Assert - Should implement LRU or similar eviction
        cache_size = (
            len(caching_system._cache) if hasattr(caching_system, "_cache") else 0
        )
        if hasattr(caching_system, "max_cache_size"):
            self.assertLessEqual(cache_size, 10, "Cache should not exceed maximum size")

    def test_ttl_expiration(self):
        """Test time-to-live cache expiration."""
        # Arrange
        caching_system = IntelligentCachingSystem(cache_ttl=0.5)  # 0.5 second TTL
        test_key = "ttl_test"
        test_data = {"value": "expires_quickly"}

        # Act
        caching_system.set_cached_data(test_key, test_data)

        # Immediate access should work
        immediate_result = caching_system.get_cached_data(test_key)
        self.assertEqual(immediate_result, test_data)

        # Wait for expiration
        time.sleep(0.6)

        expired_result = caching_system.get_cached_data(test_key)

        # Assert
        self.assertIsNone(expired_result, "Expired data should return None")
        self.assertTrue(caching_system.is_cache_expired(test_key))


class TestAlgorithmicOptimizations(unittest.TestCase):
    """Test cases for general algorithmic optimizations."""

    def test_compiled_regex_vs_string_patterns(self):
        """Test performance difference between compiled and string regex."""
        # Arrange
        pattern_string = r"(\w+)\s+(\d+)\s+(\d+)\s+\w+\s+each\s+\$(\d+\.\d{2})"
        compiled_pattern = re.compile(pattern_string)
        test_text = "DF6802 8 0 lo each $12.50\n" * 1000

        # Act - String pattern (recompiled each time)
        start_time = time.time()
        string_matches = re.findall(pattern_string, test_text)
        string_time = time.time() - start_time

        # Compiled pattern (compiled once)
        start_time = time.time()
        compiled_matches = compiled_pattern.findall(test_text)
        compiled_time = time.time() - start_time

        # Assert
        self.assertEqual(
            len(string_matches),
            len(compiled_matches),
            "Should find same number of matches",
        )
        self.assertLess(
            compiled_time,
            string_time * 0.8,
            "Compiled pattern should be at least 20% faster",
        )

    def test_search_algorithm_scaling(self):
        """Test that search algorithms scale well with document size."""
        # Arrange
        search = OptimizedProductCodeSearch()
        small_text = "DF6802 8 0 lo each $12.50\n" * 100
        large_text = small_text * 10  # 10x larger

        # Act
        start_time = time.time()
        small_result = search.find_all_product_codes(small_text)
        small_time = time.time() - start_time

        start_time = time.time()
        large_result = search.find_all_product_codes(large_text)
        large_time = time.time() - start_time

        # Assert
        self.assertEqual(
            len(large_result),
            len(small_result) * 10,
            "Large text should find 10x more codes",
        )
        # Time should scale reasonably (not exponentially)
        self.assertLess(
            large_time, small_time * 15, "Large text processing should scale reasonably"
        )

    def test_memory_efficient_processing(self):
        """Test that optimized processing uses memory efficiently."""
        # This test would require memory profiling tools
        # For now, test that processing completes without memory errors

        # Arrange
        large_text = "DF6802 8 0 lo each $12.50\n" * 10000  # Large text
        cache = OptimizedPatternCache()
        search = OptimizedProductCodeSearch()

        # Act - Process large amount of data
        try:
            pattern = cache.get_compiled_pattern(r"(\w+)\s+(\d+)\s+(\d+)")
            codes = search.find_all_product_codes(large_text)

            # Assert
            self.assertGreater(len(codes), 0, "Should process large text successfully")

        except MemoryError:
            self.fail("Memory-efficient processing should not cause MemoryError")


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT_ID", "test-project")
    os.environ.setdefault("DOCUMENT_AI_PROCESSOR_ID", "test-processor")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us")

    unittest.main(verbosity=2)
