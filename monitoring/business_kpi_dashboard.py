"""
Business KPI Dashboard - Task 304
GREEN Phase: Minimal implementation to pass tests
"""

import re
import statistics
import time
from typing import Any, Dict, List, Optional


class BusinessKPITracker:
    """Tracks business KPIs and operational metrics."""

    def __init__(self):
        self.processing_events = []
        self.daily_summaries = {}

    def record_processing_event(
        self, processing_result: Dict[str, Any], timestamp: float
    ) -> Dict[str, Any]:
        """Record a processing event for KPI calculation."""
        event = {
            "timestamp": timestamp,
            "vendor_type": processing_result.get("vendor_type", "unknown"),
            "processing_successful": processing_result.get(
                "processing_successful", False
            ),
            "accuracy_score": processing_result.get("accuracy_score", 0.0),
            "manual_review_required": processing_result.get("accuracy_score", 1.0)
            < 0.85,
            "invoice_number_correct": processing_result.get("invoice_number")
            is not None,
        }

        self.processing_events.append(event)

        # Keep only last 500 events to prevent memory issues
        if len(self.processing_events) > 500:
            self.processing_events = self.processing_events[-500:]

        # Update daily summary
        date_key = time.strftime("%Y-%m-%d", time.localtime(timestamp))
        if date_key not in self.daily_summaries:
            self.daily_summaries[date_key] = {
                "total_invoices": 0,
                "successful_processing": 0,
                "creative_coop_invoices": 0,
                "creative_coop_successful": 0,
                "manual_review_required": 0,
                "correct_invoice_numbers": 0,
            }

        summary = self.daily_summaries[date_key]
        summary["total_invoices"] += 1

        if event["processing_successful"]:
            summary["successful_processing"] += 1

        if event["vendor_type"] == "Creative-Coop":
            summary["creative_coop_invoices"] += 1
            if event["processing_successful"]:
                summary["creative_coop_successful"] += 1

        if event["manual_review_required"]:
            summary["manual_review_required"] += 1

        if event["invoice_number_correct"]:
            summary["correct_invoice_numbers"] += 1

        return {
            "event_recorded": True,
            "daily_summary_updated": True,
            "current_success_rate": self._calculate_current_success_rate(),
        }

    def calculate_daily_kpis(self, daily_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive daily KPIs."""
        if daily_data.get("total_invoices_processed", 0) == 0:
            return {"status": "no_data"}

        total_invoices = daily_data["total_invoices_processed"]
        successful_count = daily_data["successful_processing_count"]
        cc_invoices = daily_data.get("creative_coop_invoices", 0)
        cc_successful = daily_data.get("creative_coop_successful", 0)
        manual_review = daily_data.get("manual_review_required", 0)
        errors = daily_data.get("processing_errors", 0)

        kpis = {
            "overall_success_rate": successful_count / total_invoices,
            "creative_coop_success_rate": (
                cc_successful / cc_invoices if cc_invoices > 0 else 0.0
            ),
            "manual_review_rate": manual_review / total_invoices,
            "error_rate": errors / total_invoices,
            "automation_effectiveness": 1.0 - (manual_review / total_invoices),
        }

        return kpis

    def get_current_kpis(self) -> Dict[str, Any]:
        """Get current business KPI summary."""
        if not self.processing_events:
            return {"status": "no_data"}

        recent_events = self.processing_events[-50:]  # Last 50 events

        # Calculate Creative-Coop specific performance
        cc_events = [e for e in recent_events if e["vendor_type"] == "Creative-Coop"]
        cc_performance = self._calculate_creative_coop_performance(cc_events)

        current_kpis = {
            "recent_success_rate": sum(
                1 for e in recent_events if e["processing_successful"]
            )
            / len(recent_events),
            "recent_accuracy_average": sum(e["accuracy_score"] for e in recent_events)
            / len(recent_events),
            "creative_coop_performance": cc_performance,
            "manual_review_rate": sum(
                1 for e in recent_events if e["manual_review_required"]
            )
            / len(recent_events),
            "sample_size": len(recent_events),
        }

        return current_kpis

    def get_daily_summaries(self) -> Dict[str, Any]:
        """Get daily summary data."""
        return self.daily_summaries.copy()

    def _calculate_current_success_rate(self) -> float:
        """Calculate current success rate from recent events."""
        if not self.processing_events:
            return 0.0

        recent_events = self.processing_events[-10:]  # Last 10 events
        successful_count = sum(
            1 for event in recent_events if event["processing_successful"]
        )
        return successful_count / len(recent_events)

    def _calculate_creative_coop_performance(
        self, cc_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate Creative-Coop specific performance metrics."""
        if not cc_events:
            return {
                "success_rate": 0.0,
                "average_accuracy": 0.0,
                "average_extraction_rate": 0.0,
                "sample_count": 0,
            }

        successful_count = sum(1 for e in cc_events if e["processing_successful"])
        success_rate = successful_count / len(cc_events)
        average_accuracy = sum(e["accuracy_score"] for e in cc_events) / len(cc_events)

        # Estimate extraction rate based on accuracy score (simplified)
        average_extraction_rate = average_accuracy * 0.95  # Rough approximation

        return {
            "success_rate": success_rate,
            "average_accuracy": average_accuracy,
            "average_extraction_rate": average_extraction_rate,
            "sample_count": len(cc_events),
        }


class OrderTrackingSuccessMonitor:
    """Monitors order tracking success and invoice number extraction quality."""

    def __init__(self):
        self.tracking_results = []

    def calculate_tracking_metrics(
        self, tracking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate tracking success metrics."""
        correct_numbers = tracking_data.get("invoices_with_correct_numbers", 0)
        total_processed = tracking_data.get("total_invoices_processed", 1)
        lookup_successes = tracking_data.get("tracking_lookup_successes", 0)
        lookup_attempts = tracking_data.get("tracking_lookup_attempts", 1)

        invoice_accuracy = (
            correct_numbers / total_processed if total_processed > 0 else 0.0
        )
        tracking_success = (
            lookup_successes / lookup_attempts if lookup_attempts > 0 else 0.0
        )

        # Calculate tracking effectiveness score (weighted combination)
        effectiveness_score = (invoice_accuracy * 0.6) + (tracking_success * 0.4)

        return {
            "invoice_number_accuracy": invoice_accuracy,
            "tracking_success_rate": tracking_success,
            "tracking_effectiveness_score": effectiveness_score,
        }

    def evaluate_invoice_number_quality(
        self, test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate invoice number extraction quality."""
        extracted_number = test_case.get("extracted_invoice_number")
        expected_format = test_case.get("expected_format", "")
        extraction_confidence = test_case.get("extraction_confidence", 0.0)

        if extracted_number is None:
            return {"format_compliance": 0.0, "extraction_confidence": 0.0}

        # Check format compliance using regex
        format_compliance = 1.0 if re.match(expected_format, extracted_number) else 0.8

        return {
            "format_compliance": format_compliance,
            "extraction_confidence": extraction_confidence,
        }

    def record_tracking_integration_result(self, result: Dict[str, Any]) -> None:
        """Record tracking system integration result."""
        tracking_entry = {
            "timestamp": time.time(),
            "invoice_number": result.get("invoice_number"),
            "lookup_successful": result.get("tracking_lookup_successful", False),
            "data_complete": result.get("tracking_data_complete", False),
            "response_time": result.get("integration_response_time", 0.0),
        }

        self.tracking_results.append(tracking_entry)

        # Keep only last 100 results
        if len(self.tracking_results) > 100:
            self.tracking_results = self.tracking_results[-100:]

    def get_integration_success_metrics(self) -> Dict[str, Any]:
        """Get tracking system integration success metrics."""
        if not self.tracking_results:
            return {"status": "no_data"}

        successful_lookups = [
            r for r in self.tracking_results if r["lookup_successful"]
        ]
        complete_data = [r for r in successful_lookups if r["data_complete"]]

        integration_success_rate = len(successful_lookups) / len(self.tracking_results)
        data_completeness_rate = (
            len(complete_data) / len(successful_lookups) if successful_lookups else 0.0
        )

        response_times = [r["response_time"] for r in self.tracking_results]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0

        return {
            "integration_success_rate": integration_success_rate,
            "data_completeness_rate": data_completeness_rate,
            "average_response_time": avg_response_time,
        }


class ManualReviewReductionTracker:
    """Tracks manual review reduction and automation progress."""

    def __init__(self):
        self.automation_progress = []

    def calculate_review_reduction(
        self, baseline_data: Dict[str, Any], current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate manual review reduction metrics."""
        baseline_rate = baseline_data.get("manual_review_rate", 1.0)
        current_rate = current_data.get("manual_review_rate", 1.0)

        # Calculate reduction percentage
        reduction_percentage = (
            (baseline_rate - current_rate) / baseline_rate if baseline_rate > 0 else 0.0
        )

        # Calculate automation effectiveness
        automation_effectiveness = 1.0 - current_rate

        return {
            "review_reduction_percentage": max(0.0, reduction_percentage),
            "automation_effectiveness": max(0.0, automation_effectiveness),
            "baseline_manual_rate": baseline_rate,
            "current_manual_rate": current_rate,
        }

    def record_automation_progress(self, progress_data: Dict[str, Any]) -> None:
        """Record automation progress data."""
        progress_entry = {
            "timestamp": time.time(),
            "period": progress_data.get("period"),
            "manual_review_rate": progress_data.get("manual_review_rate", 0.0),
            "automation_rate": progress_data.get("automation_rate", 0.0),
        }

        self.automation_progress.append(progress_entry)

        # Keep only last 20 periods
        if len(self.automation_progress) > 20:
            self.automation_progress = self.automation_progress[-20:]

    def get_automation_progress_analysis(self) -> Dict[str, Any]:
        """Get automation progress analysis."""
        if len(self.automation_progress) < 2:
            return {
                "status": "insufficient_data",
                "automation_trend": "unknown",
                "total_improvement": 0.0,
            }

        first_entry = self.automation_progress[0]
        latest_entry = self.automation_progress[-1]

        first_automation = first_entry["automation_rate"]
        latest_automation = latest_entry["automation_rate"]

        # Calculate trend
        if latest_automation > first_automation + 0.1:
            trend = "improving"
        elif latest_automation < first_automation - 0.1:
            trend = "declining"
        else:
            trend = "stable"

        # Calculate total improvement
        total_improvement = (
            (latest_automation - first_automation) / first_automation
            if first_automation > 0
            else 0.0
        )

        # Calculate quarterly improvement rate
        periods = len(self.automation_progress)
        quarterly_rate = total_improvement / max(periods - 1, 1)

        return {
            "automation_trend": trend,
            "total_improvement": max(0.0, total_improvement),
            "quarterly_improvement_rate": quarterly_rate,
        }

    def calculate_vendor_specific_automation_success(
        self, vendor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate vendor-specific automation success metrics."""
        baseline_manual = vendor_data.get("baseline_manual_rate", 1.0)
        current_manual = vendor_data.get("current_manual_rate", 1.0)
        accuracy_met = vendor_data.get("accuracy_threshold_met", False)
        time_improved = vendor_data.get("processing_time_improved", False)
        extraction_rate = vendor_data.get("line_item_extraction_rate", 0.0)

        # Calculate automation success rate
        automation_success_rate = 1.0 - current_manual

        # Calculate manual review reduction
        manual_review_reduction = (
            (baseline_manual - current_manual) / baseline_manual
            if baseline_manual > 0
            else 0.0
        )

        # Calculate overall effectiveness score (weighted)
        effectiveness_components = {
            "automation_rate": automation_success_rate * 0.3,
            "accuracy_bonus": 0.2 if accuracy_met else 0.0,
            "performance_bonus": 0.1 if time_improved else 0.0,
            "extraction_quality": extraction_rate * 0.4,
        }

        overall_effectiveness = sum(effectiveness_components.values())

        return {
            "automation_success_rate": automation_success_rate,
            "manual_review_reduction": max(0.0, manual_review_reduction),
            "overall_effectiveness_score": min(1.0, overall_effectiveness),
        }

    def calculate_automation_roi(self, roi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ROI for automation improvements."""
        manual_cost = roi_data.get("manual_processing_cost_per_invoice", 25.0)
        automated_cost = roi_data.get("automated_processing_cost_per_invoice", 2.0)
        volume = roi_data.get("monthly_invoice_volume", 100)
        baseline_manual_rate = roi_data.get("baseline_manual_rate", 0.7)
        current_manual_rate = roi_data.get("current_manual_rate", 0.15)
        investment = roi_data.get("development_investment", 50000)

        # Calculate baseline and current monthly costs
        baseline_cost = volume * (
            baseline_manual_rate * manual_cost
            + (1 - baseline_manual_rate) * automated_cost
        )
        current_cost = volume * (
            current_manual_rate * manual_cost
            + (1 - current_manual_rate) * automated_cost
        )

        # Calculate savings
        monthly_savings = baseline_cost - current_cost
        annual_savings = monthly_savings * 12

        # Calculate ROI metrics
        payback_months = (
            investment / monthly_savings if monthly_savings > 0 else float("inf")
        )
        roi_percentage = (
            (annual_savings - investment) / investment if investment > 0 else 0.0
        )

        return {
            "monthly_cost_savings": monthly_savings,
            "annual_cost_savings": annual_savings,
            "payback_period_months": min(payback_months, 60),  # Cap at 5 years
            "roi_percentage": roi_percentage,
        }
