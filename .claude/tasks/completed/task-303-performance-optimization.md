# Task 303: Performance Optimization System for Creative-Coop Processing

**Status**: Pending
**Priority**: High
**Estimated Duration**: 4 hours
**Dependencies**: Task 302 (Live Environment Deployment), Phase 02 processing enhancements
**Engineering Principles Applied**: 2 (Scalability), 8 (Simplicity), 6 (Resilience & Fault Tolerance)

## Description

Create a comprehensive performance optimization system for Creative-Coop processing that achieves <60 second average processing time through memory efficiency improvements, algorithm optimization, intelligent caching, and concurrent processing enhancements. This system ensures production-grade performance for large Creative-Coop documents while maintaining 90%+ accuracy.

## Context

- **Enables**: Sub-60 second Creative-Coop processing, production performance excellence
- **Integration Points**: Document AI, memory management, caching systems, concurrent processing
- **Files to Create/Modify**:
  - `main.py` - Performance-optimized Creative-Coop processing functions
  - `performance_optimizations.py` - Performance optimization utilities
  - `test_scripts/performance_validation.py` - Performance testing framework
  - `test_scripts/benchmark_creative_coop_performance.py` - Benchmarking suite

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_performance_optimization_system.py` - Performance optimization tests
- `test_scripts/test_memory_efficiency.py` - Memory optimization validation
- `test_scripts/test_processing_speed_improvements.py` - Speed optimization tests
- `test_scripts/test_concurrent_processing.py` - Concurrent processing tests

**Required Test Categories**:

#### Performance Target Validation Tests
```python
def test_creative_coop_processing_time_under_60_seconds():
    # Arrange
    test_invoice = "test_invoices/CS003837319.pdf"  # Large 15-page document
    performance_optimizer = CreativeCoopPerformanceOptimizer()
    target_time = 60  # seconds

    # Act
    start_time = time.time()
    result = performance_optimizer.process_optimized(test_invoice)
    processing_time = time.time() - start_time

    # Assert
    assert processing_time < target_time, f"Processing took {processing_time:.2f}s, target: {target_time}s"
    assert result['accuracy_score'] >= 0.90, "Accuracy must be maintained during optimization"
    assert len(result['line_items']) >= 130, "All line items must be processed"

def test_memory_usage_optimization():
    # Test that memory usage stays within optimized limits
    test_invoice = "test_invoices/CS003837319.pdf"
    memory_optimizer = MemoryOptimizer()

    memory_tracker = MemoryUsageTracker()
    memory_tracker.start_tracking()

    result = memory_optimizer.process_with_memory_optimization(test_invoice)

    peak_memory = memory_tracker.get_peak_memory_mb()
    memory_tracker.stop_tracking()

    assert peak_memory < 800, f"Memory usage {peak_memory}MB exceeds optimized target of 800MB"
    assert result['processing_successful'] == True
    assert result['memory_efficiency_score'] >= 0.85

def test_large_document_streaming_processing():
    # Test streaming processing for large documents
    large_document = "test_invoices/CS003837319.pdf"  # 15 pages
    streaming_processor = StreamingDocumentProcessor()

    start_time = time.time()
    result = streaming_processor.process_with_streaming(large_document)
    processing_time = time.time() - start_time

    assert processing_time < 90, "Large document streaming should complete in <90 seconds"
    assert result['pages_processed'] == 15
    assert result['memory_peak_mb'] < 600, "Streaming should reduce memory usage"
```

#### Algorithm Optimization Tests
```python
def test_optimized_regex_pattern_caching():
    # Test that compiled regex patterns are cached for performance
    pattern_cache = OptimizedPatternCache()
    test_patterns = [
        r'(\w+)\s+(\d+)\s+(\d+)\s+\w+\s+each\s+\$(\d+\.\d{2})',
        r'INVOICE\s+#:\s*(\w+)',
        r'UPC:\s*(\d{12})'
    ]

    # First compilation should cache patterns
    start_time = time.time()
    compiled_patterns = [pattern_cache.get_compiled_pattern(p) for p in test_patterns]
    first_compilation_time = time.time() - start_time

    # Second access should be from cache (much faster)
    start_time = time.time()
    cached_patterns = [pattern_cache.get_compiled_pattern(p) for p in test_patterns]
    cache_access_time = time.time() - start_time

    assert cache_access_time < first_compilation_time * 0.1, "Cached access should be 10x faster"
    assert all(p1 is p2 for p1, p2 in zip(compiled_patterns, cached_patterns)), "Same pattern objects should be returned"

def test_optimized_product_code_search():
    # Test optimized search algorithms for product codes
    document_text = load_large_creative_coop_text()
    optimized_search = OptimizedProductCodeSearch()

    start_time = time.time()
    product_codes = optimized_search.find_all_product_codes(document_text)
    search_time = time.time() - start_time

    assert search_time < 5, "Optimized search should complete in <5 seconds"
    assert len(product_codes) >= 130, "Should find all product codes"
    assert all(len(code) >= 6 for code in product_codes), "Valid product codes found"

def test_early_termination_optimization():
    # Test early termination for found patterns
    test_text = "DF6802 8 0 lo each $12.50 found_pattern more_text..."
    pattern_finder = EarlyTerminationPatternFinder()

    start_time = time.time()
    result = pattern_finder.find_first_matching_pattern(test_text, ['quantity_pattern', 'price_pattern'])
    search_time = time.time() - start_time

    assert result['pattern_found'] == 'quantity_pattern'
    assert result['match_position'] < 50, "Should find pattern early in text"
    assert search_time < 0.1, "Early termination should be very fast"
```

#### Concurrent Processing Tests
```python
def test_concurrent_page_processing():
    # Test concurrent processing of multiple pages
    multi_page_document = "test_invoices/CS003837319.pdf"
    concurrent_processor = ConcurrentPageProcessor()

    start_time = time.time()
    result = concurrent_processor.process_pages_concurrently(multi_page_document, max_workers=3)
    concurrent_time = time.time() - start_time

    # Test sequential processing for comparison
    start_time = time.time()
    sequential_result = concurrent_processor.process_pages_sequentially(multi_page_document)
    sequential_time = time.time() - start_time

    assert concurrent_time < sequential_time * 0.7, "Concurrent processing should be 30% faster"
    assert result['accuracy_score'] == sequential_result['accuracy_score'], "Accuracy should be maintained"
    assert len(result['line_items']) == len(sequential_result['line_items']), "Same number of items processed"

def test_parallel_entity_processing():
    # Test parallel processing of Document AI entities
    entities = load_test_entities('CS003837319')
    parallel_processor = ParallelEntityProcessor()

    start_time = time.time()
    parallel_result = parallel_processor.process_entities_parallel(entities, max_workers=4)
    parallel_time = time.time() - start_time

    start_time = time.time()
    sequential_result = parallel_processor.process_entities_sequential(entities)
    sequential_time = time.time() - start_time

    assert parallel_time < sequential_time * 0.8, "Parallel processing should be 20% faster"
    assert len(parallel_result) == len(sequential_result), "Same number of entities processed"
```

#### Caching System Tests
```python
def test_intelligent_caching_system():
    # Test intelligent caching for frequently accessed data
    caching_system = IntelligentCachingSystem()
    test_invoice_id = "CS003837319"

    # First access should cache the result
    start_time = time.time()
    first_result = caching_system.get_processed_data(test_invoice_id)
    first_access_time = time.time() - start_time

    # Second access should be from cache
    start_time = time.time()
    cached_result = caching_system.get_processed_data(test_invoice_id)
    cache_access_time = time.time() - start_time

    assert cache_access_time < first_access_time * 0.1, "Cached access should be 10x faster"
    assert first_result == cached_result, "Cached result should match original"
    assert caching_system.cache_hit_rate() > 0.5, "Cache hit rate should be reasonable"

def test_cache_expiration_and_refresh():
    # Test cache expiration and refresh mechanisms
    caching_system = IntelligentCachingSystem(cache_ttl=1)  # 1 second TTL
    test_key = "test_data"

    # Store data in cache
    original_data = {"test": "data", "timestamp": time.time()}
    caching_system.set_cached_data(test_key, original_data)

    # Immediate access should return cached data
    cached_data = caching_system.get_cached_data(test_key)
    assert cached_data == original_data

    # Wait for cache expiration
    time.sleep(1.1)

    # Access after expiration should return None or trigger refresh
    expired_data = caching_system.get_cached_data(test_key)
    assert expired_data is None or caching_system.is_cache_expired(test_key)
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
class CreativeCoopPerformanceOptimizer:
    """Main performance optimization system for Creative-Coop processing."""

    def __init__(self):
        self.memory_optimizer = MemoryOptimizer()
        self.pattern_cache = OptimizedPatternCache()
        self.concurrent_processor = ConcurrentPageProcessor()
        self.caching_system = IntelligentCachingSystem()

    def process_optimized(self, invoice_path):
        """
        Process Creative-Coop invoice with comprehensive performance optimizations.

        Args:
            invoice_path (str): Path to invoice PDF file

        Returns:
            dict: Processing result with performance metrics

        Raises:
            PerformanceError: If processing exceeds time/memory limits
        """
        start_time = time.time()
        performance_metrics = {'optimizations_applied': []}

        try:
            # Check cache first
            cache_key = self._generate_cache_key(invoice_path)
            cached_result = self.caching_system.get_cached_data(cache_key)
            if cached_result:
                performance_metrics['cache_hit'] = True
                performance_metrics['processing_time'] = time.time() - start_time
                return {**cached_result, 'performance_metrics': performance_metrics}

            # Memory-optimized document loading
            document_data = self.memory_optimizer.load_document_efficiently(invoice_path)
            performance_metrics['optimizations_applied'].append('memory_efficient_loading')

            # Concurrent page processing
            if self._should_use_concurrent_processing(document_data):
                processing_result = self.concurrent_processor.process_pages_concurrently(
                    document_data, max_workers=3
                )
                performance_metrics['optimizations_applied'].append('concurrent_processing')
            else:
                processing_result = self._process_sequential_optimized(document_data)
                performance_metrics['optimizations_applied'].append('sequential_optimized')

            # Optimized pattern extraction
            optimized_result = self._apply_pattern_optimizations(processing_result)
            performance_metrics['optimizations_applied'].append('pattern_optimization')

            # Cache result for future use
            final_result = {
                'line_items': optimized_result['line_items'],
                'accuracy_score': optimized_result['accuracy_score'],
                'invoice_number': optimized_result['invoice_number'],
                'processing_successful': True
            }

            self.caching_system.set_cached_data(cache_key, final_result)

            processing_time = time.time() - start_time
            performance_metrics['processing_time'] = processing_time

            if processing_time >= 60:
                raise PerformanceError(f"Processing time {processing_time:.2f}s exceeds 60s target")

            return {**final_result, 'performance_metrics': performance_metrics}

        except Exception as e:
            raise PerformanceError(f"Performance optimization failed: {str(e)}")

class MemoryOptimizer:
    """Optimizes memory usage during Creative-Coop processing."""

    def load_document_efficiently(self, document_path):
        """Load document with memory-efficient streaming."""
        try:
            # Use streaming to avoid loading entire document into memory
            with open(document_path, 'rb') as f:
                # Process document in chunks
                document_chunks = self._process_in_chunks(f)

            # Implement garbage collection at key points
            self._cleanup_memory()

            return {
                'document_chunks': document_chunks,
                'total_pages': len(document_chunks),
                'memory_optimized': True
            }
        except Exception as e:
            raise MemoryOptimizationError(f"Memory-efficient loading failed: {str(e)}")

    def process_with_memory_optimization(self, invoice_path):
        """Process with comprehensive memory optimization."""
        memory_tracker = MemoryUsageTracker()
        memory_tracker.start_tracking()

        try:
            # Load document efficiently
            document_data = self.load_document_efficiently(invoice_path)

            # Process each page separately to limit memory usage
            processed_pages = []
            for page_chunk in document_data['document_chunks']:
                page_result = self._process_page_memory_efficient(page_chunk)
                processed_pages.append(page_result)

                # Cleanup after each page
                self._cleanup_memory()

            # Combine results efficiently
            combined_result = self._combine_results_efficiently(processed_pages)

            peak_memory = memory_tracker.get_peak_memory_mb()
            memory_tracker.stop_tracking()

            return {
                'processing_successful': True,
                'memory_peak_mb': peak_memory,
                'memory_efficiency_score': min(1.0, 800 / peak_memory) if peak_memory > 0 else 1.0,
                'line_items': combined_result.get('line_items', []),
                'accuracy_score': combined_result.get('accuracy_score', 0.0)
            }

        except Exception as e:
            memory_tracker.stop_tracking()
            raise MemoryOptimizationError(f"Memory optimization failed: {str(e)}")

    def _cleanup_memory(self):
        """Force garbage collection to free memory."""
        import gc
        gc.collect()

class OptimizedPatternCache:
    """Caches compiled regex patterns for performance."""

    def __init__(self):
        self._pattern_cache = {}
        self._access_count = {}

    def get_compiled_pattern(self, pattern_string):
        """Get compiled regex pattern from cache or compile and cache."""
        if pattern_string not in self._pattern_cache:
            import re
            self._pattern_cache[pattern_string] = re.compile(pattern_string)
            self._access_count[pattern_string] = 0

        self._access_count[pattern_string] += 1
        return self._pattern_cache[pattern_string]

    def get_cache_stats(self):
        """Get cache performance statistics."""
        return {
            'cached_patterns': len(self._pattern_cache),
            'total_accesses': sum(self._access_count.values()),
            'cache_hit_rate': len(self._pattern_cache) / max(1, sum(self._access_count.values()))
        }

class ConcurrentPageProcessor:
    """Handles concurrent processing of document pages."""

    def process_pages_concurrently(self, document_data, max_workers=3):
        """Process pages concurrently for improved performance."""
        import concurrent.futures
        import threading

        pages = document_data.get('document_chunks', [])
        processing_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all pages for concurrent processing
            future_to_page = {
                executor.submit(self._process_single_page, page): page_idx
                for page_idx, page in enumerate(pages)
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_page):
                page_idx = future_to_page[future]
                try:
                    page_result = future.result()
                    processing_results.append({
                        'page_index': page_idx,
                        'result': page_result
                    })
                except Exception as e:
                    print(f"Page {page_idx} processing failed: {e}")

        # Combine results from all pages
        combined_result = self._combine_concurrent_results(processing_results)

        return {
            'line_items': combined_result.get('line_items', []),
            'accuracy_score': combined_result.get('accuracy_score', 0.0),
            'pages_processed': len(pages),
            'concurrent_processing': True
        }

    def _process_single_page(self, page_data):
        """Process a single page of the document."""
        # Implement single page processing logic
        # This would call existing Creative-Coop processing functions
        try:
            page_text = self._extract_text_from_page(page_data)
            page_entities = self._extract_entities_from_page(page_data)

            # Apply Creative-Coop processing to page
            line_items = self._extract_creative_coop_items_from_page(page_text, page_entities)

            return {
                'line_items': line_items,
                'processing_successful': True,
                'page_text_length': len(page_text)
            }
        except Exception as e:
            return {
                'line_items': [],
                'processing_successful': False,
                'error': str(e)
            }

class IntelligentCachingSystem:
    """Intelligent caching system for processed data."""

    def __init__(self, cache_ttl=3600):  # 1 hour default TTL
        self._cache = {}
        self._access_times = {}
        self._cache_ttl = cache_ttl
        self._cache_hits = 0
        self._cache_misses = 0

    def get_cached_data(self, cache_key):
        """Get data from cache if available and not expired."""
        if cache_key in self._cache:
            if not self.is_cache_expired(cache_key):
                self._cache_hits += 1
                return self._cache[cache_key]
            else:
                # Remove expired data
                del self._cache[cache_key]
                del self._access_times[cache_key]

        self._cache_misses += 1
        return None

    def set_cached_data(self, cache_key, data):
        """Store data in cache with timestamp."""
        self._cache[cache_key] = data
        self._access_times[cache_key] = time.time()

    def is_cache_expired(self, cache_key):
        """Check if cached data has expired."""
        if cache_key not in self._access_times:
            return True

        return time.time() - self._access_times[cache_key] > self._cache_ttl

    def cache_hit_rate(self):
        """Calculate cache hit rate."""
        total_requests = self._cache_hits + self._cache_misses
        return self._cache_hits / total_requests if total_requests > 0 else 0.0
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Extract reusable performance optimization utilities
- [ ] Optimize memory management algorithms
- [ ] Improve concurrent processing efficiency
- [ ] Add comprehensive performance monitoring
- [ ] Enhance caching strategies and intelligence

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for performance optimization system
- [ ] Creative-Coop processing completes in <60 seconds average
- [ ] Memory usage optimized to <800MB peak for large documents
- [ ] Concurrent processing provides 20-30% performance improvement
- [ ] Pattern caching reduces regex compilation overhead by 90%
- [ ] Intelligent caching achieves >50% cache hit rate
- [ ] Streaming processing reduces memory footprint for large documents
- [ ] Error handling tested for all performance optimization failures
- [ ] Performance monitoring tracks optimization effectiveness
- [ ] Logging includes structured performance metrics
- [ ] Integration tests verify optimizations don't affect accuracy
- [ ] Documentation includes performance optimization strategies

## Engineering Principles Compliance

**Principle 2. Scalability**: Performance optimizations enable system to handle larger volumes and concurrent processing efficiently

**Principle 8. Simplicity**: Optimizations maintain code clarity while improving performance through focused improvements

**Principle 6. Resilience & Fault Tolerance**: Performance system includes fallbacks and error handling for optimization failures

## Monitoring & Observability

**Required Metrics**:
- `creative_coop_processing_time_seconds`: Creative-Coop processing duration
- `memory_peak_usage_mb`: Peak memory usage during processing
- `cache_hit_rate`: Percentage of cache hits vs misses
- `concurrent_processing_speedup`: Performance improvement from concurrency

**Log Events**:
```python
# Performance optimization success
logger.info("Creative-Coop performance optimization completed", extra={
    'correlation_id': correlation_id,
    'processing_time_seconds': processing_time,
    'memory_peak_mb': peak_memory,
    'optimizations_applied': optimizations_list,
    'cache_hit_rate': cache_hit_rate
})

# Performance target missed
logger.warning("Performance target missed", extra={
    'correlation_id': correlation_id,
    'processing_time_seconds': processing_time,
    'target_time_seconds': 60,
    'performance_degradation_percent': degradation_percent
})
```

## Security Considerations

- [ ] Ensure concurrent processing doesn't expose data between threads
- [ ] Validate cached data integrity and prevent cache poisoning
- [ ] Secure handling of document data during streaming processing

## Performance Requirements

- [ ] Creative-Coop processing average time <60 seconds
- [ ] Memory usage peak <800MB for large documents
- [ ] Concurrent processing improvement ≥20% over sequential
- [ ] Cache hit rate ≥50% for frequently processed invoices
- [ ] Pattern compilation overhead reduced by ≥90%

## Implementation Notes

**Key Design Decisions**:
- Use concurrent processing for multi-page documents to leverage multiple cores
- Implement intelligent caching to avoid reprocessing identical invoices
- Apply streaming processing for memory efficiency with large documents
- Cache compiled regex patterns to eliminate compilation overhead

**Integration Points**:
- Integration with existing Creative-Coop processing functions in `main.py`
- Connection to Document AI processing workflows
- Compatibility with Google Cloud Functions memory and timeout limits
- Integration with monitoring and alerting systems

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for each performance optimization component
- [ ] Integration tests for end-to-end optimized processing
- [ ] Performance benchmarking against baseline implementations
- [ ] Memory usage testing under various document sizes
- [ ] Concurrent processing testing with different worker counts
- [ ] Edge case testing for optimization failure scenarios
