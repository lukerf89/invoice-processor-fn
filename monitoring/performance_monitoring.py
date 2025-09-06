"""
Performance Metrics Monitoring - Task 304
GREEN Phase: Minimal implementation to pass tests
"""

import statistics
import time
from typing import Any, Dict, List, Optional


class PerformanceThresholdMonitor:
    """Monitors performance thresholds and compliance."""

    def __init__(self):
        self.thresholds = {"target": 60.0, "warning": 90.0, "critical": 120.0}
        self.performance_history = []
        self.breach_history = []

    def set_threshold(self, threshold_type: str, value: float) -> None:
        """Set performance threshold."""
        # Validate threshold ordering
        if threshold_type == "warning" and value <= self.thresholds.get("target", 0.0):
            raise ValueError("Warning threshold must be greater than target")
        if threshold_type == "critical" and value <= self.thresholds.get(
            "warning", 0.0
        ):
            raise ValueError("Critical threshold must be greater than warning")

        self.thresholds[threshold_type] = value

    def get_threshold_configuration(self) -> Dict[str, float]:
        """Get current threshold configuration."""
        return self.thresholds.copy()

    def check_performance_threshold(self, processing_time: float) -> Dict[str, Any]:
        """Check processing time against thresholds."""
        self.performance_history.append(processing_time)

        if processing_time <= self.thresholds["target"]:
            status = "normal"
            should_alert = False
        elif processing_time <= self.thresholds["warning"]:
            status = "normal"  # Still within acceptable range
            should_alert = False
        elif processing_time <= self.thresholds["critical"]:
            status = "warning"
            should_alert = True
        else:
            status = "critical"
            should_alert = True

        # Record breach if needed
        if should_alert:
            self.breach_history.append(
                {
                    "timestamp": time.time(),
                    "processing_time": processing_time,
                    "threshold_status": status,
                }
            )

        return {
            "threshold_status": status,
            "should_alert": should_alert,
            "processing_time": processing_time,
        }

    def get_target_compliance_stats(self) -> Dict[str, Any]:
        """Get target compliance statistics."""
        if not self.performance_history:
            return {"status": "no_data"}

        target_threshold = self.thresholds["target"]
        compliant_count = sum(
            1 for t in self.performance_history if t <= target_threshold
        )
        total_count = len(self.performance_history)
        compliance_rate = compliant_count / total_count if total_count > 0 else 0.0

        return {
            "target_compliance_rate": compliance_rate,
            "compliant_count": compliant_count,
            "total_count": total_count,
        }

    def get_breach_history(self) -> List[Dict[str, Any]]:
        """Get threshold breach history."""
        return self.breach_history.copy()


class PerformanceMetricsTracker:
    """Tracks and analyzes processing performance metrics."""

    def __init__(self):
        self.performance_data = []
        self.threshold_monitor = PerformanceThresholdMonitor()

    def record_processing_time(
        self, processing_time: float, document_size: str, timestamp: float
    ) -> Dict[str, Any]:
        """Record processing time with context."""
        performance_entry = {
            "processing_time": processing_time,
            "document_size": document_size,
            "timestamp": timestamp,
        }

        self.performance_data.append(performance_entry)

        # Check performance thresholds
        threshold_result = self.threshold_monitor.check_performance_threshold(
            processing_time
        )

        return {
            "processing_time": processing_time,
            "threshold_status": threshold_result["threshold_status"],
            "should_alert": threshold_result["should_alert"],
            "performance_rating": self._rate_performance(processing_time),
        }

    def get_performance_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance statistics."""
        if not self.performance_data:
            return {"status": "no_data"}

        processing_times = [entry["processing_time"] for entry in self.performance_data]

        return {
            "average_processing_time": sum(processing_times) / len(processing_times),
            "median_processing_time": self._calculate_median(processing_times),
            "percentile_95": self._calculate_percentile(processing_times, 95),
            "min_processing_time": min(processing_times),
            "max_processing_time": max(processing_times),
            "sample_count": len(processing_times),
            "performance_trend": self._calculate_performance_trend(),
        }

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics summary."""
        if not self.performance_data:
            return {"status": "no_data"}

        recent_data = self.performance_data[-10:]  # Last 10 entries
        processing_times = [entry["processing_time"] for entry in recent_data]

        current_metrics = {
            "current_processing_time": recent_data[-1]["processing_time"],
            "average_processing_time": sum(processing_times) / len(processing_times),
            "performance_trend": self._calculate_performance_trend(),
            "sample_count": len(processing_times),
            "last_updated": recent_data[-1]["timestamp"],
        }

        return current_metrics

    def _rate_performance(self, processing_time: float) -> str:
        """Rate performance based on processing time."""
        if processing_time <= 40:
            return "excellent"
        elif processing_time <= 60:
            return "good"
        elif processing_time <= 90:
            return "acceptable"
        else:
            return "poor"

    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median value."""
        return statistics.median(values)

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        if index >= len(sorted_values):
            index = len(sorted_values) - 1
        return sorted_values[index]

    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend direction."""
        if len(self.performance_data) < 5:
            return "stable"

        recent_times = [
            entry["processing_time"] for entry in self.performance_data[-10:]
        ]

        # Simple trend calculation - compare first half vs second half
        mid_point = len(recent_times) // 2
        first_half_avg = (
            statistics.mean(recent_times[:mid_point])
            if mid_point > 0
            else recent_times[0]
        )
        second_half_avg = statistics.mean(recent_times[mid_point:])

        # For performance, lower is better
        if second_half_avg < first_half_avg - 5:  # 5 second improvement
            return "improving"
        elif second_half_avg > first_half_avg + 5:  # 5 second degradation
            return "declining"
        else:
            return "stable"


class MemoryUsageMonitor:
    """Monitors memory usage and optimization."""

    def __init__(self):
        self.memory_data = []
        self.memory_limit = 1024  # Default 1GB limit

    def set_memory_limit(self, limit_mb: int) -> None:
        """Set memory usage limit in MB."""
        self.memory_limit = limit_mb

    def record_memory_usage(self, memory_data: Dict[str, Any]) -> None:
        """Record memory usage data."""
        memory_entry = {
            **memory_data,
            "timestamp": time.time(),
            "memory_within_limits": memory_data.get("peak_memory_mb", 0)
            <= self.memory_limit,
        }

        self.memory_data.append(memory_entry)

        # Keep only last 100 entries
        if len(self.memory_data) > 100:
            self.memory_data = self.memory_data[-100:]

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        if not self.memory_data:
            return {"status": "no_data"}

        latest_entry = self.memory_data[-1]

        return {
            "peak_memory_mb": latest_entry.get("peak_memory_mb", 0),
            "average_memory_mb": latest_entry.get("average_memory_mb", 0),
            "efficiency_score": latest_entry.get("memory_efficiency_score", 0.0),
            "garbage_collection_count": latest_entry.get("garbage_collection_count", 0),
            "memory_within_limits": latest_entry["memory_within_limits"],
            "memory_limit_compliance": latest_entry["memory_within_limits"],
            "memory_limit_breach_detected": not latest_entry["memory_within_limits"],
        }

    def get_optimization_progress(self) -> Dict[str, Any]:
        """Get memory optimization progress metrics."""
        if len(self.memory_data) < 2:
            return {"status": "insufficient_data"}

        first_entry = self.memory_data[0]
        latest_entry = self.memory_data[-1]

        first_memory = first_entry.get("peak_memory_mb", 0)
        latest_memory = latest_entry.get("peak_memory_mb", 0)

        first_efficiency = first_entry.get(
            "memory_efficiency_score", 0.0
        ) or first_entry.get("efficiency_score", 0.0)
        latest_efficiency = latest_entry.get(
            "memory_efficiency_score", 0.0
        ) or latest_entry.get("efficiency_score", 0.0)

        # Calculate reduction and improvement
        memory_reduction = (
            (first_memory - latest_memory) / first_memory if first_memory > 0 else 0.0
        )
        efficiency_improvement = latest_efficiency - first_efficiency

        return {
            "memory_reduction_percentage": max(0.0, memory_reduction),
            "efficiency_improvement": max(0.0, efficiency_improvement),
            "optimization_trend": "improving" if memory_reduction > 0.05 else "stable",
        }


class ConcurrentProcessingMonitor:
    """Monitors concurrent processing performance."""

    def __init__(self):
        self.concurrent_data = []

    def record_concurrent_processing_metrics(
        self, concurrent_data: Dict[str, Any]
    ) -> None:
        """Record concurrent processing metrics."""
        processing_entry = {
            **concurrent_data,
            "timestamp": time.time(),
            "efficiency_improvement": self._calculate_efficiency_improvement(
                concurrent_data
            ),
        }

        self.concurrent_data.append(processing_entry)

        # Keep only last 50 entries
        if len(self.concurrent_data) > 50:
            self.concurrent_data = self.concurrent_data[-50:]

    def get_concurrent_statistics(self) -> Dict[str, Any]:
        """Get concurrent processing statistics."""
        if not self.concurrent_data:
            return {"status": "no_data"}

        latest_entry = self.concurrent_data[-1]

        return {
            "speedup_factor": latest_entry.get("speedup_factor", 1.0),
            "efficiency_improvement": latest_entry["efficiency_improvement"],
            "sequential_time": latest_entry.get("sequential_time", 0),
            "concurrent_time": latest_entry.get("concurrent_time", 0),
            "worker_count": latest_entry.get("worker_count", 1),
        }

    def get_scalability_analysis(self) -> Dict[str, Any]:
        """Get scalability analysis for different worker counts."""
        if len(self.concurrent_data) < 3:
            return {
                "status": "insufficient_data",
                "optimal_worker_count": 3,
                "scalability_efficiency": 0.8,
                "diminishing_returns_threshold": 4,
            }

        # Analyze speedup factors by worker count
        worker_speedups = {}
        for entry in self.concurrent_data:
            workers = entry.get("worker_count", 1)
            speedup = entry.get("speedup_factor", 1.0)
            if workers not in worker_speedups:
                worker_speedups[workers] = []
            worker_speedups[workers].append(speedup)

        # Find optimal worker count (highest average speedup)
        optimal_workers = 3
        best_speedup = 0.0

        for workers, speedups in worker_speedups.items():
            avg_speedup = sum(speedups) / len(speedups)
            if avg_speedup > best_speedup:
                best_speedup = avg_speedup
                optimal_workers = workers

        return {
            "optimal_worker_count": optimal_workers,
            "scalability_efficiency": min(best_speedup / optimal_workers, 1.0),
            "diminishing_returns_threshold": optimal_workers + 1,
        }

    def _calculate_efficiency_improvement(
        self, concurrent_data: Dict[str, Any]
    ) -> float:
        """Calculate efficiency improvement from concurrent processing."""
        sequential_time = concurrent_data.get("sequential_time", 0)
        concurrent_time = concurrent_data.get("concurrent_time", 0)

        if sequential_time <= 0 or concurrent_time <= 0:
            return 0.0

        return (sequential_time - concurrent_time) / sequential_time
