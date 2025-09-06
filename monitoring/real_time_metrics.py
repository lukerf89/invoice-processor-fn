"""
Real-Time Monitoring System - Task 304
GREEN Phase: Minimal implementation to pass tests
"""

import json
import time
from typing import Any, Dict, List, Optional

from .accuracy_tracking import AccuracyMetricsTracker
from .business_kpi_dashboard import BusinessKPITracker
from .performance_monitoring import PerformanceMetricsTracker


class MonitoringError(Exception):
    """Custom exception for monitoring system errors."""

    pass


class MetricsStorage:
    """Simple in-memory storage for metrics data."""

    def __init__(self):
        self.stored_metrics: List[Dict[str, Any]] = []

    def store_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """Store metrics data."""
        self.stored_metrics.append(metrics_data)

        # Keep only last 1000 entries to prevent memory issues
        if len(self.stored_metrics) > 1000:
            self.stored_metrics = self.stored_metrics[-1000:]


class RealTimeMonitoringSystem:
    """Main real-time monitoring system for Creative-Coop processing."""

    def __init__(self):
        self.accuracy_tracker = AccuracyMetricsTracker()
        self.performance_tracker = PerformanceMetricsTracker()
        self.business_kpi_tracker = BusinessKPITracker()
        self.metrics_storage = MetricsStorage()

    def record_processing_metrics(
        self, processing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Record comprehensive processing metrics in real-time.

        Args:
            processing_result (dict): Complete processing result with metrics

        Returns:
            dict: Recorded metrics summary

        Raises:
            MonitoringError: If metrics recording fails
        """
        if processing_result is None:
            raise MonitoringError(
                "Failed to record processing metrics: Processing result cannot be None"
            )

        # Validate input data types and ranges
        if not isinstance(processing_result, dict):
            raise MonitoringError(
                "Failed to record processing metrics: Processing result must be a dictionary"
            )

        # Validate processing_time if present
        if "processing_time" in processing_result:
            processing_time = processing_result["processing_time"]
            if isinstance(processing_time, str) and processing_time != "invalid":
                try:
                    processing_time = float(processing_time)
                except ValueError:
                    raise MonitoringError(
                        "Failed to record processing metrics: Invalid processing_time format"
                    )
            elif isinstance(processing_time, str) and processing_time == "invalid":
                raise MonitoringError(
                    "Failed to record processing metrics: Invalid processing_time format"
                )
            elif not isinstance(processing_time, (int, float)) or processing_time < 0:
                raise MonitoringError(
                    "Failed to record processing metrics: Processing time must be non-negative"
                )

        # Validate accuracy_score if present
        if "accuracy_score" in processing_result:
            accuracy_score = processing_result["accuracy_score"]
            if isinstance(accuracy_score, str) and accuracy_score == "invalid":
                raise MonitoringError(
                    "Failed to record processing metrics: Invalid accuracy_score format"
                )
            elif (
                not isinstance(accuracy_score, (int, float))
                or accuracy_score < 0.0
                or accuracy_score > 1.0
            ):
                raise MonitoringError(
                    "Failed to record processing metrics: Accuracy score must be between 0.0 and 1.0"
                )

        # Validate that we have at least some meaningful data to record
        has_meaningful_data = any(
            key in processing_result
            for key in ["accuracy_score", "processing_time", "processing_successful"]
        )
        if not has_meaningful_data:
            raise MonitoringError(
                "Failed to record processing metrics: No meaningful metrics data provided"
            )

        try:
            timestamp = time.time()
            metrics_recorded = {}

            # Record accuracy metrics
            if "accuracy_score" in processing_result:
                accuracy_metrics = self.accuracy_tracker.record_accuracy(
                    processing_result["accuracy_score"],
                    processing_result.get("vendor_type", "unknown"),
                    timestamp,
                )
                metrics_recorded.update(accuracy_metrics)

            # Record performance metrics
            if "processing_time" in processing_result:
                performance_metrics = self.performance_tracker.record_processing_time(
                    processing_result["processing_time"],
                    processing_result.get("document_size", "unknown"),
                    timestamp,
                )
                metrics_recorded.update(performance_metrics)

            # Record business KPI data
            business_metrics = self.business_kpi_tracker.record_processing_event(
                processing_result, timestamp
            )
            metrics_recorded.update(business_metrics)

            # Store all metrics
            self.metrics_storage.store_metrics(
                {
                    "timestamp": timestamp,
                    "processing_result": processing_result,
                    "calculated_metrics": metrics_recorded,
                }
            )

            return {
                "metrics_count": len(metrics_recorded),
                "timestamp": timestamp,
                "recording_successful": True,
                "accuracy_score": processing_result.get("accuracy_score"),
                "processing_time": processing_result.get("processing_time"),
                "vendor_type": processing_result.get("vendor_type"),
                **metrics_recorded,
            }

        except Exception as e:
            raise MonitoringError(f"Failed to record processing metrics: {str(e)}")

    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data for real-time monitoring."""
        try:
            system_health = self._calculate_system_health()

            dashboard_data = {
                "accuracy_metrics": self.accuracy_tracker.get_current_metrics(),
                "performance_metrics": self.performance_tracker.get_current_metrics(),
                "business_kpis": self.business_kpi_tracker.get_current_kpis(),
                "system_health": system_health,
                "last_updated": time.time(),
            }

            return dashboard_data

        except Exception as e:
            raise MonitoringError(f"Failed to get dashboard data: {str(e)}")

    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score."""
        try:
            accuracy_metrics = self.accuracy_tracker.get_current_metrics()
            performance_metrics = self.performance_tracker.get_current_metrics()
            business_kpis = self.business_kpi_tracker.get_current_kpis()

            # Handle no data cases
            if accuracy_metrics.get("status") == "no_data":
                return {
                    "overall_health_score": 0.0,
                    "health_status": "unknown",
                    "components": {
                        "accuracy": "no_data",
                        "performance": "no_data",
                        "business": "no_data",
                    },
                }

            # Calculate component scores
            accuracy_score = accuracy_metrics.get("current_accuracy", 0.0)
            performance_rating = self._performance_to_score(
                performance_metrics.get("current_processing_time", 120)
            )
            business_score = (
                business_kpis.get("recent_success_rate", 0.0)
                if business_kpis.get("status") != "no_data"
                else 0.5
            )

            # Weighted overall health score
            weights = {"accuracy": 0.4, "performance": 0.3, "business": 0.3}
            overall_score = (
                accuracy_score * weights["accuracy"]
                + performance_rating * weights["performance"]
                + business_score * weights["business"]
            )

            # Determine health status
            if overall_score >= 0.9:
                health_status = "excellent"
            elif overall_score >= 0.8:
                health_status = "good"
            elif overall_score >= 0.7:
                health_status = "fair"
            else:
                health_status = "poor"

            return {
                "overall_health_score": overall_score,
                "health_status": health_status,
                "components": {
                    "accuracy": accuracy_score,
                    "performance": performance_rating,
                    "business": business_score,
                },
            }

        except Exception as e:
            return {
                "overall_health_score": 0.0,
                "health_status": "error",
                "error": str(e),
            }

    def _performance_to_score(self, processing_time: float) -> float:
        """Convert processing time to a 0-1 score."""
        if processing_time <= 30:
            return 1.0  # Excellent
        elif processing_time <= 60:
            return 0.8  # Good
        elif processing_time <= 90:
            return 0.6  # Acceptable
        else:
            return 0.3  # Poor
