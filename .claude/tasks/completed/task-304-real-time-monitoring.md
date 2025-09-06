# Task 304: Real-Time Accuracy and Performance Monitoring System

**Status**: Pending
**Priority**: High
**Estimated Duration**: 3-4 hours
**Dependencies**: Task 302 (Live Environment Deployment), Task 303 (Performance Optimization)
**Engineering Principles Applied**: 5 (Observability), 1 (Reliability), 4 (Maintainability)

## Description

Create a comprehensive real-time monitoring system that tracks Creative-Coop processing accuracy, performance metrics, error rates, and quality scores in production environment. This system provides immediate visibility into processing health with detailed metrics collection, trend analysis, and business KPI tracking.

## Context

- **Enables**: Production quality visibility, proactive issue detection, performance tracking
- **Integration Points**: Google Cloud Monitoring, production logging, business metrics
- **Files to Create/Modify**:
  - `monitoring/real_time_metrics.py` - Core monitoring system
  - `monitoring/accuracy_tracking.py` - Accuracy metrics collection
  - `monitoring/performance_monitoring.py` - Performance metrics tracking
  - `monitoring/business_kpi_dashboard.py` - Business KPI tracking system

## TDD Implementation Cycle

### Phase 1: RED - Write Failing Tests

**Test Files to Create**:
- `test_scripts/test_real_time_monitoring_system.py` - Core monitoring tests
- `test_scripts/test_accuracy_metrics_collection.py` - Accuracy tracking tests
- `test_scripts/test_performance_metrics_tracking.py` - Performance monitoring tests
- `test_scripts/test_business_kpi_calculation.py` - Business KPI tests

**Required Test Categories**:

#### Real-Time Metrics Collection Tests
```python
def test_real_time_metrics_collection_system():
    # Arrange
    monitoring_system = RealTimeMonitoringSystem()
    test_processing_result = {
        'invoice_number': 'CS003837319',
        'processing_time': 45.2,
        'accuracy_score': 0.92,
        'line_items_count': 135,
        'vendor_type': 'Creative-Coop',
        'processing_tier': 'document_ai',
        'error_count': 0
    }

    # Act
    metrics_recorded = monitoring_system.record_processing_metrics(test_processing_result)

    # Assert
    assert metrics_recorded['metrics_count'] == 7  # All metrics recorded
    assert metrics_recorded['accuracy_score'] == 0.92
    assert metrics_recorded['processing_time'] == 45.2
    assert metrics_recorded['timestamp'] is not None

def test_accuracy_score_calculation():
    # Test accuracy score calculation from processing results
    accuracy_tracker = AccuracyMetricsTracker()
    test_results = {
        'expected_line_items': 135,
        'extracted_line_items': 128,
        'correct_invoice_number': True,
        'valid_prices_count': 125,
        'valid_quantities_count': 130,
        'placeholder_data_detected': False
    }
    
    accuracy_score = accuracy_tracker.calculate_accuracy_score(test_results)
    
    assert 0.0 <= accuracy_score <= 1.0, "Accuracy score must be between 0 and 1"
    assert accuracy_score >= 0.90, "Should achieve high accuracy for test case"

def test_performance_metrics_tracking():
    # Test performance metrics tracking and calculation
    performance_tracker = PerformanceMetricsTracker()
    
    # Record multiple processing times
    processing_times = [42.1, 38.5, 51.2, 44.8, 39.9]
    for time_value in processing_times:
        performance_tracker.record_processing_time(time_value)
    
    performance_stats = performance_tracker.get_performance_statistics()
    
    assert performance_stats['average_processing_time'] < 60, "Average should be under target"
    assert performance_stats['sample_count'] == 5
    assert 'percentile_95' in performance_stats
    assert performance_stats['percentile_95'] <= max(processing_times)
```

#### Accuracy Monitoring Tests
```python
def test_accuracy_threshold_monitoring():
    # Test accuracy threshold monitoring and alerts
    accuracy_monitor = AccuracyThresholdMonitor()
    accuracy_monitor.set_threshold('warning', 0.85)
    accuracy_monitor.set_threshold('critical', 0.80)
    
    # Test warning threshold
    warning_result = accuracy_monitor.check_accuracy_threshold(0.82)
    assert warning_result['threshold_status'] == 'warning'
    assert warning_result['should_alert'] == True
    
    # Test critical threshold
    critical_result = accuracy_monitor.check_accuracy_threshold(0.75)
    assert critical_result['threshold_status'] == 'critical'
    assert critical_result['should_alert'] == True
    
    # Test normal operation
    normal_result = accuracy_monitor.check_accuracy_threshold(0.92)
    assert normal_result['threshold_status'] == 'normal'
    assert normal_result['should_alert'] == False

def test_creative_coop_specific_accuracy_tracking():
    # Test Creative-Coop specific accuracy metrics
    creative_coop_tracker = CreativeCoopAccuracyTracker()
    
    test_invoice_result = {
        'invoice_number': 'CS003837319',
        'expected_products': 135,
        'extracted_products': 132,
        'correct_prices': 128,
        'correct_quantities': 131,
        'correct_descriptions': 125,
        'placeholder_data_count': 0
    }
    
    accuracy_metrics = creative_coop_tracker.calculate_detailed_accuracy(test_invoice_result)
    
    assert 'product_extraction_rate' in accuracy_metrics
    assert 'price_accuracy_rate' in accuracy_metrics
    assert 'quantity_accuracy_rate' in accuracy_metrics
    assert 'description_quality_score' in accuracy_metrics
    assert accuracy_metrics['overall_accuracy'] >= 0.90

def test_accuracy_trend_analysis():
    # Test accuracy trend analysis over time
    trend_analyzer = AccuracyTrendAnalyzer()
    
    # Simulate accuracy data over time
    accuracy_data = [
        {'timestamp': '2024-01-01T10:00:00', 'accuracy': 0.92},
        {'timestamp': '2024-01-01T11:00:00', 'accuracy': 0.89},
        {'timestamp': '2024-01-01T12:00:00', 'accuracy': 0.94},
        {'timestamp': '2024-01-01T13:00:00', 'accuracy': 0.87},
        {'timestamp': '2024-01-01T14:00:00', 'accuracy': 0.91}
    ]
    
    for data_point in accuracy_data:
        trend_analyzer.add_accuracy_data_point(data_point)
    
    trend_analysis = trend_analyzer.analyze_accuracy_trends()
    
    assert 'average_accuracy' in trend_analysis
    assert 'trend_direction' in trend_analysis  # 'improving', 'declining', 'stable'
    assert 'volatility_score' in trend_analysis
```

#### Performance Monitoring Tests
```python
def test_performance_threshold_monitoring():
    # Test performance threshold monitoring
    performance_monitor = PerformanceThresholdMonitor()
    performance_monitor.set_threshold('target', 60.0)  # 60 seconds target
    performance_monitor.set_threshold('warning', 90.0)  # 90 seconds warning
    performance_monitor.set_threshold('critical', 120.0)  # 120 seconds critical
    
    # Test normal performance
    normal_result = performance_monitor.check_performance_threshold(45.2)
    assert normal_result['threshold_status'] == 'normal'
    assert normal_result['should_alert'] == False
    
    # Test warning threshold
    warning_result = performance_monitor.check_performance_threshold(95.5)
    assert warning_result['threshold_status'] == 'warning'
    assert warning_result['should_alert'] == True

def test_memory_usage_monitoring():
    # Test memory usage monitoring
    memory_monitor = MemoryUsageMonitor()
    
    test_memory_data = {
        'peak_memory_mb': 750,
        'average_memory_mb': 520,
        'memory_efficiency_score': 0.85,
        'garbage_collection_count': 3
    }
    
    memory_monitor.record_memory_usage(test_memory_data)
    memory_stats = memory_monitor.get_memory_statistics()
    
    assert memory_stats['peak_memory_mb'] == 750
    assert memory_stats['memory_within_limits'] == True  # Under 1GB
    assert memory_stats['efficiency_score'] == 0.85

def test_concurrent_processing_metrics():
    # Test concurrent processing performance metrics
    concurrent_monitor = ConcurrentProcessingMonitor()
    
    test_concurrent_data = {
        'sequential_time': 120.5,
        'concurrent_time': 85.2,
        'worker_count': 3,
        'speedup_factor': 120.5 / 85.2
    }
    
    concurrent_monitor.record_concurrent_processing_metrics(test_concurrent_data)
    concurrent_stats = concurrent_monitor.get_concurrent_statistics()
    
    assert concurrent_stats['speedup_factor'] > 1.0
    assert concurrent_stats['efficiency_improvement'] > 0.20  # At least 20% improvement
```

#### Business KPI Tracking Tests
```python
def test_business_kpi_calculation():
    # Test business KPI calculation and tracking
    business_kpi_tracker = BusinessKPITracker()
    
    daily_processing_data = {
        'total_invoices_processed': 45,
        'successful_processing_count': 43,
        'creative_coop_invoices': 12,
        'creative_coop_successful': 11,
        'manual_review_required': 3,
        'processing_errors': 2
    }
    
    kpis = business_kpi_tracker.calculate_daily_kpis(daily_processing_data)
    
    assert 'overall_success_rate' in kpis
    assert 'creative_coop_success_rate' in kpis
    assert 'manual_review_rate' in kpis
    assert 'error_rate' in kpis
    assert kpis['overall_success_rate'] >= 0.90

def test_order_tracking_success_metrics():
    # Test order tracking success metrics
    order_tracking_monitor = OrderTrackingSuccessMonitor()
    
    tracking_data = {
        'invoices_with_correct_numbers': 42,
        'total_invoices_processed': 45,
        'tracking_lookup_successes': 40,
        'tracking_lookup_attempts': 42
    }
    
    tracking_metrics = order_tracking_monitor.calculate_tracking_metrics(tracking_data)
    
    assert tracking_metrics['invoice_number_accuracy'] >= 0.90
    assert tracking_metrics['tracking_success_rate'] >= 0.85
    assert 'tracking_effectiveness_score' in tracking_metrics

def test_manual_review_reduction_tracking():
    # Test manual review reduction metrics
    review_tracker = ManualReviewReductionTracker()
    
    # Historical baseline
    baseline_data = {'manual_review_rate': 0.70}  # 70% manual review before
    
    # Current performance
    current_data = {'manual_review_rate': 0.15}   # 15% manual review now
    
    reduction_metrics = review_tracker.calculate_review_reduction(baseline_data, current_data)
    
    assert reduction_metrics['review_reduction_percentage'] >= 0.50  # At least 50% reduction
    assert reduction_metrics['automation_effectiveness'] >= 0.80
```

### Phase 2: GREEN - Minimal Implementation

**Implementation Structure**:
```python
class RealTimeMonitoringSystem:
    """Main real-time monitoring system for Creative-Coop processing."""
    
    def __init__(self):
        self.accuracy_tracker = AccuracyMetricsTracker()
        self.performance_tracker = PerformanceMetricsTracker()
        self.business_kpi_tracker = BusinessKPITracker()
        self.metrics_storage = MetricsStorage()
    
    def record_processing_metrics(self, processing_result):
        """
        Record comprehensive processing metrics in real-time.
        
        Args:
            processing_result (dict): Complete processing result with metrics
            
        Returns:
            dict: Recorded metrics summary
            
        Raises:
            MonitoringError: If metrics recording fails
        """
        try:
            timestamp = time.time()
            metrics_recorded = {}
            
            # Record accuracy metrics
            if 'accuracy_score' in processing_result:
                accuracy_metrics = self.accuracy_tracker.record_accuracy(
                    processing_result['accuracy_score'],
                    processing_result.get('vendor_type', 'unknown'),
                    timestamp
                )
                metrics_recorded.update(accuracy_metrics)
            
            # Record performance metrics
            if 'processing_time' in processing_result:
                performance_metrics = self.performance_tracker.record_processing_time(
                    processing_result['processing_time'],
                    processing_result.get('document_size', 'unknown'),
                    timestamp
                )
                metrics_recorded.update(performance_metrics)
            
            # Record business KPI data
            business_metrics = self.business_kpi_tracker.record_processing_event(
                processing_result, timestamp
            )
            metrics_recorded.update(business_metrics)
            
            # Store all metrics
            self.metrics_storage.store_metrics({
                'timestamp': timestamp,
                'processing_result': processing_result,
                'calculated_metrics': metrics_recorded
            })
            
            return {
                'metrics_count': len(metrics_recorded),
                'timestamp': timestamp,
                'recording_successful': True,
                **metrics_recorded
            }
            
        except Exception as e:
            raise MonitoringError(f"Failed to record processing metrics: {str(e)}")
    
    def get_real_time_dashboard_data(self):
        """Get current dashboard data for real-time monitoring."""
        try:
            dashboard_data = {
                'accuracy_metrics': self.accuracy_tracker.get_current_metrics(),
                'performance_metrics': self.performance_tracker.get_current_metrics(),
                'business_kpis': self.business_kpi_tracker.get_current_kpis(),
                'system_health': self._calculate_system_health(),
                'last_updated': time.time()
            }
            
            return dashboard_data
            
        except Exception as e:
            raise MonitoringError(f"Failed to get dashboard data: {str(e)}")

class AccuracyMetricsTracker:
    """Tracks and analyzes processing accuracy metrics."""
    
    def __init__(self):
        self.accuracy_data = []
        self.threshold_monitor = AccuracyThresholdMonitor()
    
    def record_accuracy(self, accuracy_score, vendor_type, timestamp):
        """Record accuracy score with context."""
        accuracy_entry = {
            'accuracy_score': accuracy_score,
            'vendor_type': vendor_type,
            'timestamp': timestamp
        }
        
        self.accuracy_data.append(accuracy_entry)
        
        # Check thresholds
        threshold_result = self.threshold_monitor.check_accuracy_threshold(accuracy_score)
        
        return {
            'accuracy_score': accuracy_score,
            'threshold_status': threshold_result['threshold_status'],
            'should_alert': threshold_result['should_alert'],
            'vendor_type': vendor_type
        }
    
    def calculate_accuracy_score(self, processing_results):
        """Calculate comprehensive accuracy score."""
        try:
            accuracy_components = {
                'line_item_extraction': self._calculate_line_item_accuracy(processing_results),
                'invoice_number_accuracy': self._calculate_invoice_number_accuracy(processing_results),
                'price_accuracy': self._calculate_price_accuracy(processing_results),
                'quantity_accuracy': self._calculate_quantity_accuracy(processing_results),
                'description_quality': self._calculate_description_quality(processing_results)
            }
            
            # Weighted average of accuracy components
            weights = {
                'line_item_extraction': 0.30,
                'invoice_number_accuracy': 0.20,
                'price_accuracy': 0.20,
                'quantity_accuracy': 0.20,
                'description_quality': 0.10
            }
            
            overall_accuracy = sum(
                accuracy_components[component] * weights[component]
                for component in accuracy_components
            )
            
            return max(0.0, min(1.0, overall_accuracy))
            
        except Exception as e:
            print(f"Accuracy calculation failed: {e}")
            return 0.0
    
    def get_current_metrics(self):
        """Get current accuracy metrics summary."""
        if not self.accuracy_data:
            return {'status': 'no_data', 'metrics': {}}
        
        recent_data = self.accuracy_data[-10:]  # Last 10 entries
        
        current_metrics = {
            'current_accuracy': recent_data[-1]['accuracy_score'],
            'average_accuracy': sum(entry['accuracy_score'] for entry in recent_data) / len(recent_data),
            'accuracy_trend': self._calculate_accuracy_trend(recent_data),
            'sample_count': len(recent_data),
            'last_updated': recent_data[-1]['timestamp']
        }
        
        return current_metrics

class PerformanceMetricsTracker:
    """Tracks and analyzes processing performance metrics."""
    
    def __init__(self):
        self.performance_data = []
        self.threshold_monitor = PerformanceThresholdMonitor()
    
    def record_processing_time(self, processing_time, document_size, timestamp):
        """Record processing time with context."""
        performance_entry = {
            'processing_time': processing_time,
            'document_size': document_size,
            'timestamp': timestamp
        }
        
        self.performance_data.append(performance_entry)
        
        # Check performance thresholds
        threshold_result = self.threshold_monitor.check_performance_threshold(processing_time)
        
        return {
            'processing_time': processing_time,
            'threshold_status': threshold_result['threshold_status'],
            'should_alert': threshold_result['should_alert'],
            'performance_rating': self._rate_performance(processing_time)
        }
    
    def get_performance_statistics(self):
        """Calculate comprehensive performance statistics."""
        if not self.performance_data:
            return {'status': 'no_data'}
        
        processing_times = [entry['processing_time'] for entry in self.performance_data]
        
        return {
            'average_processing_time': sum(processing_times) / len(processing_times),
            'median_processing_time': self._calculate_median(processing_times),
            'percentile_95': self._calculate_percentile(processing_times, 95),
            'min_processing_time': min(processing_times),
            'max_processing_time': max(processing_times),
            'sample_count': len(processing_times),
            'performance_trend': self._calculate_performance_trend()
        }
    
    def _rate_performance(self, processing_time):
        """Rate performance based on processing time."""
        if processing_time <= 30:
            return 'excellent'
        elif processing_time <= 60:
            return 'good'
        elif processing_time <= 90:
            return 'acceptable'
        else:
            return 'poor'

class BusinessKPITracker:
    """Tracks business KPIs and operational metrics."""
    
    def __init__(self):
        self.processing_events = []
        self.daily_summaries = {}
    
    def record_processing_event(self, processing_result, timestamp):
        """Record a processing event for KPI calculation."""
        event = {
            'timestamp': timestamp,
            'vendor_type': processing_result.get('vendor_type', 'unknown'),
            'processing_successful': processing_result.get('processing_successful', False),
            'accuracy_score': processing_result.get('accuracy_score', 0.0),
            'manual_review_required': processing_result.get('accuracy_score', 1.0) < 0.85,
            'invoice_number_correct': processing_result.get('invoice_number') is not None
        }
        
        self.processing_events.append(event)
        
        # Update daily summary
        date_key = time.strftime('%Y-%m-%d', time.localtime(timestamp))
        if date_key not in self.daily_summaries:
            self.daily_summaries[date_key] = {
                'total_invoices': 0,
                'successful_processing': 0,
                'creative_coop_invoices': 0,
                'creative_coop_successful': 0,
                'manual_review_required': 0,
                'correct_invoice_numbers': 0
            }
        
        summary = self.daily_summaries[date_key]
        summary['total_invoices'] += 1
        
        if event['processing_successful']:
            summary['successful_processing'] += 1
        
        if event['vendor_type'] == 'Creative-Coop':
            summary['creative_coop_invoices'] += 1
            if event['processing_successful']:
                summary['creative_coop_successful'] += 1
        
        if event['manual_review_required']:
            summary['manual_review_required'] += 1
        
        if event['invoice_number_correct']:
            summary['correct_invoice_numbers'] += 1
        
        return {
            'event_recorded': True,
            'daily_summary_updated': True,
            'current_success_rate': self._calculate_current_success_rate()
        }
    
    def calculate_daily_kpis(self, daily_data):
        """Calculate comprehensive daily KPIs."""
        if daily_data['total_invoices_processed'] == 0:
            return {'status': 'no_data'}
        
        kpis = {
            'overall_success_rate': daily_data['successful_processing_count'] / daily_data['total_invoices_processed'],
            'creative_coop_success_rate': (
                daily_data['creative_coop_successful'] / daily_data['creative_coop_invoices'] 
                if daily_data['creative_coop_invoices'] > 0 else 0.0
            ),
            'manual_review_rate': daily_data['manual_review_required'] / daily_data['total_invoices_processed'],
            'error_rate': daily_data['processing_errors'] / daily_data['total_invoices_processed'],
            'automation_effectiveness': 1.0 - (daily_data['manual_review_required'] / daily_data['total_invoices_processed'])
        }
        
        return kpis
    
    def get_current_kpis(self):
        """Get current business KPI summary."""
        if not self.processing_events:
            return {'status': 'no_data'}
        
        recent_events = self.processing_events[-50:]  # Last 50 events
        
        current_kpis = {
            'recent_success_rate': sum(1 for e in recent_events if e['processing_successful']) / len(recent_events),
            'recent_accuracy_average': sum(e['accuracy_score'] for e in recent_events) / len(recent_events),
            'creative_coop_performance': self._calculate_creative_coop_performance(recent_events),
            'manual_review_rate': sum(1 for e in recent_events if e['manual_review_required']) / len(recent_events),
            'sample_size': len(recent_events)
        }
        
        return current_kpis
```

### Phase 3: REFACTOR - Improve Design

**Refactoring Focus**:
- [ ] Extract reusable monitoring utilities
- [ ] Optimize metrics collection performance
- [ ] Improve dashboard data aggregation
- [ ] Add comprehensive alerting integration
- [ ] Enhance trend analysis capabilities

## Acceptance Criteria (Test-Driven)

- [ ] All tests pass (RED → GREEN → REFACTOR complete)
- [ ] Test coverage ≥ 90% for monitoring system
- [ ] Real-time metrics collection captures all processing events
- [ ] Accuracy tracking provides detailed Creative-Coop metrics
- [ ] Performance monitoring tracks sub-60 second target compliance
- [ ] Business KPI tracking calculates operational effectiveness
- [ ] Threshold monitoring detects quality degradation
- [ ] Trend analysis identifies performance patterns
- [ ] Dashboard data provides comprehensive real-time visibility
- [ ] Error handling tested for all monitoring failure modes
- [ ] Performance within acceptable bounds for metrics collection
- [ ] Logging includes structured monitoring data
- [ ] Integration tests verify monitoring system accuracy
- [ ] Documentation includes monitoring setup and interpretation

## Engineering Principles Compliance

**Principle 5. Observability**: Comprehensive monitoring provides complete visibility into system health and business performance

**Principle 1. Reliability**: Monitoring system ensures reliability through continuous health tracking and alerting

**Principle 4. Maintainability**: Well-structured monitoring enables easy system maintenance and issue resolution

## Monitoring & Observability

**Required Metrics**:
- `creative_coop_accuracy_score`: Real-time Creative-Coop processing accuracy
- `processing_time_percentile_95`: 95th percentile processing time
- `business_automation_rate`: Percentage of invoices processed without manual review
- `system_health_score`: Overall system health composite metric

**Log Events**:
```python
# Monitoring system health
logger.info("Real-time monitoring metrics recorded", extra={
    'correlation_id': correlation_id,
    'accuracy_score': accuracy_score,
    'processing_time': processing_time,
    'business_kpis': business_kpis,
    'monitoring_system_health': system_health
})

# Threshold breach alert
logger.warning("Performance threshold breached", extra={
    'correlation_id': correlation_id,
    'threshold_type': threshold_type,
    'current_value': current_value,
    'threshold_limit': threshold_limit,
    'alert_severity': severity
})
```

## Security Considerations

- [ ] Secure handling of monitoring data and metrics
- [ ] Protect business KPI data from unauthorized access
- [ ] Ensure monitoring system doesn't expose sensitive processing data

## Performance Requirements

- [ ] Metrics collection adds <1% processing overhead
- [ ] Dashboard data retrieval completes in <2 seconds
- [ ] Real-time monitoring supports high-frequency data collection
- [ ] Trend analysis calculations complete in <5 seconds

## Implementation Notes

**Key Design Decisions**:
- Use lightweight metrics collection to minimize processing overhead
- Implement comprehensive accuracy tracking specific to Creative-Coop requirements
- Provide real-time dashboard data for immediate visibility into system health
- Include business KPI tracking to demonstrate operational value

**Integration Points**:
- Integration with Google Cloud Monitoring for infrastructure metrics
- Connection to existing logging infrastructure for correlation
- Compatibility with alerting systems for proactive issue detection
- Integration with business reporting systems for KPI visibility

## Testing Strategy

**Test Coverage**:
- [ ] Unit tests for metrics collection and calculation components
- [ ] Integration tests for real-time monitoring system
- [ ] Performance testing for monitoring overhead measurement
- [ ] Accuracy testing for metrics calculation algorithms
- [ ] Business KPI calculation validation with real data
- [ ] Edge case testing for monitoring system resilience