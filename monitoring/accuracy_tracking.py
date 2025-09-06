"""
Accuracy Metrics Tracking - Task 304
GREEN Phase: Minimal implementation to pass tests
"""

import statistics
import time
from typing import Any, Dict, List, Optional


class AccuracyThresholdMonitor:
    """Monitors accuracy thresholds and triggers alerts."""

    def __init__(self):
        self.thresholds = {"target": 0.95, "warning": 0.85, "critical": 0.80}
        self.breach_history = []

    def set_threshold(self, threshold_type: str, value: float) -> None:
        """Set accuracy threshold."""
        # Validate threshold ordering
        if threshold_type == "warning" and value >= self.thresholds.get("target", 1.0):
            raise ValueError("Warning threshold must be less than target")
        if threshold_type == "critical" and value >= self.thresholds.get(
            "warning", 1.0
        ):
            raise ValueError("Critical threshold must be less than warning")

        self.thresholds[threshold_type] = value

    def get_threshold_configuration(self) -> Dict[str, float]:
        """Get current threshold configuration."""
        return self.thresholds.copy()

    def check_accuracy_threshold(self, accuracy_score: float) -> Dict[str, Any]:
        """Check accuracy against thresholds."""
        if accuracy_score >= self.thresholds["warning"]:
            status = "normal"
            should_alert = False
        elif accuracy_score >= self.thresholds["critical"]:
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
                    "accuracy_score": accuracy_score,
                    "threshold_status": status,
                }
            )

        return {
            "threshold_status": status,
            "should_alert": should_alert,
            "accuracy_score": accuracy_score,
        }

    def get_breach_history(self) -> List[Dict[str, Any]]:
        """Get threshold breach history."""
        return self.breach_history.copy()


class AccuracyMetricsTracker:
    """Tracks and analyzes processing accuracy metrics."""

    def __init__(self):
        self.accuracy_data = []
        self.threshold_monitor = AccuracyThresholdMonitor()

    def record_accuracy(
        self, accuracy_score: float, vendor_type: str, timestamp: float
    ) -> Dict[str, Any]:
        """Record accuracy score with context."""
        accuracy_entry = {
            "accuracy_score": accuracy_score,
            "vendor_type": vendor_type,
            "timestamp": timestamp,
        }

        self.accuracy_data.append(accuracy_entry)

        # Check thresholds
        threshold_result = self.threshold_monitor.check_accuracy_threshold(
            accuracy_score
        )

        return {
            "accuracy_score": accuracy_score,
            "threshold_status": threshold_result["threshold_status"],
            "should_alert": threshold_result["should_alert"],
            "vendor_type": vendor_type,
        }

    def calculate_accuracy_score(self, processing_results: Dict[str, Any]) -> float:
        """Calculate comprehensive accuracy score."""
        try:
            accuracy_components = {
                "line_item_extraction": self._calculate_line_item_accuracy(
                    processing_results
                ),
                "invoice_number_accuracy": self._calculate_invoice_number_accuracy(
                    processing_results
                ),
                "price_accuracy": self._calculate_price_accuracy(processing_results),
                "quantity_accuracy": self._calculate_quantity_accuracy(
                    processing_results
                ),
                "description_quality": self._calculate_description_quality(
                    processing_results
                ),
            }

            # Weighted average of accuracy components
            weights = {
                "line_item_extraction": 0.30,
                "invoice_number_accuracy": 0.20,
                "price_accuracy": 0.20,
                "quantity_accuracy": 0.20,
                "description_quality": 0.10,
            }

            overall_accuracy = sum(
                accuracy_components[component] * weights[component]
                for component in accuracy_components
            )

            return max(0.0, min(1.0, overall_accuracy))

        except Exception as e:
            print(f"Accuracy calculation failed: {e}")
            return 0.0

    def _calculate_line_item_accuracy(
        self, processing_results: Dict[str, Any]
    ) -> float:
        """Calculate line item extraction accuracy."""
        expected = processing_results.get("expected_line_items", 1)
        extracted = processing_results.get("extracted_line_items", 0)
        return extracted / expected if expected > 0 else 0.0

    def _calculate_invoice_number_accuracy(
        self, processing_results: Dict[str, Any]
    ) -> float:
        """Calculate invoice number extraction accuracy."""
        return 1.0 if processing_results.get("correct_invoice_number", False) else 0.0

    def _calculate_price_accuracy(self, processing_results: Dict[str, Any]) -> float:
        """Calculate price accuracy rate."""
        expected = processing_results.get("expected_line_items", 1)
        valid_prices = processing_results.get("valid_prices_count", 0)
        return valid_prices / expected if expected > 0 else 0.0

    def _calculate_quantity_accuracy(self, processing_results: Dict[str, Any]) -> float:
        """Calculate quantity accuracy rate."""
        expected = processing_results.get("expected_line_items", 1)
        valid_quantities = processing_results.get("valid_quantities_count", 0)
        return valid_quantities / expected if expected > 0 else 0.0

    def _calculate_description_quality(
        self, processing_results: Dict[str, Any]
    ) -> float:
        """Calculate description quality score."""
        expected = processing_results.get("expected_line_items", 1)
        clean_descriptions = processing_results.get(
            "clean_descriptions_count", expected // 2
        )
        return clean_descriptions / expected if expected > 0 else 0.0

    def _calculate_accuracy_trend(self, recent_data: List[Dict[str, Any]]) -> str:
        """Calculate accuracy trend direction."""
        if len(recent_data) < 2:
            return "stable"

        recent_scores = [entry["accuracy_score"] for entry in recent_data]

        # Simple trend calculation - compare first half vs second half
        mid_point = len(recent_scores) // 2
        first_half_avg = (
            statistics.mean(recent_scores[:mid_point]) if mid_point > 0 else 0
        )
        second_half_avg = statistics.mean(recent_scores[mid_point:])

        if second_half_avg > first_half_avg + 0.02:
            return "improving"
        elif second_half_avg < first_half_avg - 0.02:
            return "declining"
        else:
            return "stable"

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current accuracy metrics summary."""
        if not self.accuracy_data:
            return {"status": "no_data", "metrics": {}}

        recent_data = self.accuracy_data[-10:]  # Last 10 entries

        current_metrics = {
            "current_accuracy": recent_data[-1]["accuracy_score"],
            "average_accuracy": sum(entry["accuracy_score"] for entry in recent_data)
            / len(recent_data),
            "accuracy_trend": self._calculate_accuracy_trend(recent_data),
            "sample_count": len(recent_data),
            "last_updated": recent_data[-1]["timestamp"],
        }

        return current_metrics


class CreativeCoopAccuracyTracker:
    """Specialized accuracy tracking for Creative-Coop invoices."""

    def __init__(self):
        pass

    def calculate_detailed_accuracy(
        self, invoice_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate detailed Creative-Coop accuracy metrics."""
        expected_products = invoice_result.get("expected_products", 1)
        extracted_products = invoice_result.get("extracted_products", 0)
        correct_prices = invoice_result.get("correct_prices", 0)
        correct_quantities = invoice_result.get("correct_quantities", 0)
        correct_descriptions = invoice_result.get("correct_descriptions", 0)
        placeholder_data_count = invoice_result.get("placeholder_data_count", 0)

        # Calculate individual component accuracies
        product_extraction_rate = (
            extracted_products / expected_products if expected_products > 0 else 0.0
        )
        price_accuracy_rate = (
            correct_prices / expected_products if expected_products > 0 else 0.0
        )
        quantity_accuracy_rate = (
            correct_quantities / expected_products if expected_products > 0 else 0.0
        )
        description_quality_score = (
            correct_descriptions / expected_products if expected_products > 0 else 0.0
        )

        # Placeholder data penalty
        placeholder_data_penalty = min(
            placeholder_data_count * 0.02, 0.20
        )  # Max 20% penalty

        # Calculate overall accuracy (weighted average)
        weights = {
            "extraction": 0.30,
            "prices": 0.25,
            "quantities": 0.25,
            "descriptions": 0.20,
        }

        overall_accuracy = (
            product_extraction_rate * weights["extraction"]
            + price_accuracy_rate * weights["prices"]
            + quantity_accuracy_rate * weights["quantities"]
            + description_quality_score * weights["descriptions"]
        ) - placeholder_data_penalty

        overall_accuracy = max(0.0, min(1.0, overall_accuracy))

        return {
            "product_extraction_rate": product_extraction_rate,
            "price_accuracy_rate": price_accuracy_rate,
            "quantity_accuracy_rate": quantity_accuracy_rate,
            "description_quality_score": description_quality_score,
            "placeholder_data_penalty": placeholder_data_penalty,
            "overall_accuracy": overall_accuracy,
        }


class AccuracyTrendAnalyzer:
    """Analyzes accuracy trends over time."""

    def __init__(self):
        self.accuracy_data_points = []

    def add_accuracy_data_point(self, data_point: Dict[str, Any]) -> None:
        """Add accuracy data point for trend analysis."""
        self.accuracy_data_points.append(data_point)

        # Keep only last 100 data points
        if len(self.accuracy_data_points) > 100:
            self.accuracy_data_points = self.accuracy_data_points[-100:]

    def analyze_accuracy_trends(self) -> Dict[str, Any]:
        """Analyze accuracy trends over time."""
        if len(self.accuracy_data_points) < 2:
            return {
                "status": "insufficient_data",
                "average_accuracy": 0.0,
                "trend_direction": "unknown",
                "volatility_score": 0.0,
            }

        accuracy_values = [point["accuracy"] for point in self.accuracy_data_points]

        # Calculate average accuracy
        average_accuracy = statistics.mean(accuracy_values)

        # Calculate trend direction
        trend_direction = self._calculate_trend_direction(accuracy_values)

        # Calculate volatility score (coefficient of variation)
        volatility_score = self._calculate_volatility(accuracy_values)

        return {
            "average_accuracy": average_accuracy,
            "trend_direction": trend_direction,
            "volatility_score": volatility_score,
            "sample_count": len(accuracy_values),
        }

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction using linear regression slope."""
        if len(values) < 2:
            return "stable"

        # Simple slope calculation
        n = len(values)
        x_values = list(range(n))

        # Calculate slope using least squares
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility score (normalized standard deviation)."""
        if len(values) < 2:
            return 0.0

        mean_value = statistics.mean(values)
        if mean_value == 0:
            return 1.0

        std_deviation = statistics.stdev(values)
        # Normalize by mean and cap at 1.0
        return min(std_deviation / mean_value, 1.0)
