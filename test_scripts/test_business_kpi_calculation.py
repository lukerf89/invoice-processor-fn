"""
Test suite for Business KPI Calculation - Task 304
RED Phase: Write failing tests for business KPI tracking and operational metrics
"""

import json
import os
import sys
import time
from unittest.mock import Mock, patch

import pytest

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import business KPI tracking components (will fail initially - RED phase)
try:
    from monitoring.business_kpi_dashboard import (
        BusinessKPITracker,
        ManualReviewReductionTracker,
        OrderTrackingSuccessMonitor,
    )
except ImportError as e:
    # Expected in RED phase - modules don't exist yet
    print(f"Expected import error in RED phase: {e}")
    BusinessKPITracker = None
    OrderTrackingSuccessMonitor = None
    ManualReviewReductionTracker = None


class TestBusinessKPITracker:
    """Test suite for business KPI tracking and calculation."""

    def test_business_kpi_calculation(self):
        """Test business KPI calculation and tracking."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()
        daily_processing_data = {
            "total_invoices_processed": 45,
            "successful_processing_count": 43,
            "creative_coop_invoices": 12,
            "creative_coop_successful": 11,
            "manual_review_required": 3,
            "processing_errors": 2,
        }

        # Act
        kpis = business_kpi_tracker.calculate_daily_kpis(daily_processing_data)

        # Assert
        assert "overall_success_rate" in kpis
        assert "creative_coop_success_rate" in kpis
        assert "manual_review_rate" in kpis
        assert "error_rate" in kpis
        assert "automation_effectiveness" in kpis

        # Verify calculations
        expected_success_rate = 43 / 45  # ~95.6%
        expected_cc_success_rate = 11 / 12  # ~91.7%
        expected_manual_rate = 3 / 45  # ~6.7%
        expected_error_rate = 2 / 45  # ~4.4%
        expected_automation = 1.0 - (3 / 45)  # ~93.3%

        assert abs(kpis["overall_success_rate"] - expected_success_rate) < 0.01
        assert abs(kpis["creative_coop_success_rate"] - expected_cc_success_rate) < 0.01
        assert abs(kpis["manual_review_rate"] - expected_manual_rate) < 0.01
        assert abs(kpis["error_rate"] - expected_error_rate) < 0.01
        assert abs(kpis["automation_effectiveness"] - expected_automation) < 0.01

        assert kpis["overall_success_rate"] >= 0.90

    def test_processing_event_recording(self):
        """Test processing event recording for KPI calculation."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()
        processing_result = {
            "vendor_type": "Creative-Coop",
            "processing_successful": True,
            "accuracy_score": 0.916,
            "invoice_number": "CS003837319",
            "processing_time": 47.8,
        }
        timestamp = time.time()

        # Act
        recording_result = business_kpi_tracker.record_processing_event(
            processing_result, timestamp
        )

        # Assert
        assert recording_result["event_recorded"] == True
        assert recording_result["daily_summary_updated"] == True
        assert "current_success_rate" in recording_result
        assert isinstance(recording_result["current_success_rate"], float)

    def test_current_kpis_calculation(self):
        """Test current business KPI calculation."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()

        # Record multiple processing events
        processing_events = [
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.92,
                "invoice_number": "CS001",
            },
            {
                "vendor_type": "HarperCollins",
                "processing_successful": True,
                "accuracy_score": 0.98,
                "invoice_number": "HC001",
            },
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.88,
                "invoice_number": "CS002",
            },
            {
                "vendor_type": "OneHundred80",
                "processing_successful": False,
                "accuracy_score": 0.65,
                "invoice_number": None,
            },
        ]

        timestamp = time.time()
        for event in processing_events:
            business_kpi_tracker.record_processing_event(event, timestamp)
            timestamp += 1

        # Act
        current_kpis = business_kpi_tracker.get_current_kpis()

        # Assert
        assert "recent_success_rate" in current_kpis
        assert "recent_accuracy_average" in current_kpis
        assert "creative_coop_performance" in current_kpis
        assert "manual_review_rate" in current_kpis
        assert "sample_size" in current_kpis

        assert current_kpis["sample_size"] == len(processing_events)

        # Verify success rate calculation (3 successful out of 4)
        expected_success_rate = 3 / 4  # 75%
        assert abs(current_kpis["recent_success_rate"] - expected_success_rate) < 0.01

    def test_creative_coop_specific_kpi_tracking(self):
        """Test Creative-Coop specific KPI tracking."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()

        # Record Creative-Coop specific events
        creative_coop_events = [
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.916,  # Our 85.7% baseline equivalent
                "invoice_number": "CS003837319",
                "line_items_extracted": 128,
                "expected_line_items": 135,
            },
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.923,
                "invoice_number": "CS004848705",
                "line_items_extracted": 95,
                "expected_line_items": 98,
            },
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": False,
                "accuracy_score": 0.745,
                "invoice_number": "CS005555555",
                "line_items_extracted": 65,
                "expected_line_items": 120,
            },
        ]

        timestamp = time.time()
        for event in creative_coop_events:
            business_kpi_tracker.record_processing_event(event, timestamp)
            timestamp += 1

        # Act
        current_kpis = business_kpi_tracker.get_current_kpis()
        creative_coop_performance = current_kpis["creative_coop_performance"]

        # Assert
        assert "success_rate" in creative_coop_performance
        assert "average_accuracy" in creative_coop_performance
        assert "average_extraction_rate" in creative_coop_performance

        # Verify Creative-Coop success rate (2 out of 3)
        expected_cc_success_rate = 2 / 3  # ~66.7%
        assert (
            abs(creative_coop_performance["success_rate"] - expected_cc_success_rate)
            < 0.01
        )

        # Verify average accuracy calculation
        expected_avg_accuracy = (0.916 + 0.923 + 0.745) / 3
        assert (
            abs(creative_coop_performance["average_accuracy"] - expected_avg_accuracy)
            < 0.01
        )

    def test_daily_summary_aggregation(self):
        """Test daily summary aggregation and KPI calculation."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()

        # Simulate a full day of processing events
        daily_events = []
        base_timestamp = time.time()

        # Generate diverse processing events
        for i in range(50):  # 50 events in a day
            vendor_types = [
                "Creative-Coop",
                "HarperCollins",
                "OneHundred80",
                "Rifle Paper",
            ]
            vendor_type = vendor_types[i % len(vendor_types)]

            processing_successful = i % 10 != 9  # 90% success rate
            accuracy_score = 0.95 if processing_successful else 0.70

            event = {
                "vendor_type": vendor_type,
                "processing_successful": processing_successful,
                "accuracy_score": accuracy_score,
                "invoice_number": (
                    f"{vendor_type[:2]}{i:03d}" if processing_successful else None
                ),
            }

            business_kpi_tracker.record_processing_event(
                event, base_timestamp + i * 3600
            )
            daily_events.append(event)

        # Act
        daily_summaries = business_kpi_tracker.get_daily_summaries()
        current_kpis = business_kpi_tracker.get_current_kpis()

        # Assert
        assert len(daily_summaries) >= 1  # At least one day's data

        # Verify KPI calculations match expected values
        creative_coop_events = [
            e for e in daily_events if e["vendor_type"] == "Creative-Coop"
        ]
        expected_cc_count = len(creative_coop_events)
        expected_cc_successful = len(
            [e for e in creative_coop_events if e["processing_successful"]]
        )

        assert current_kpis["sample_size"] >= len(daily_events[-10:])  # Recent sample

    def test_no_data_handling(self):
        """Test handling of scenarios with no processing data."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()

        # Test with no recorded events
        current_kpis = business_kpi_tracker.get_current_kpis()
        assert current_kpis["status"] == "no_data"

        # Test daily KPI calculation with zero processing
        zero_processing_data = {
            "total_invoices_processed": 0,
            "successful_processing_count": 0,
            "creative_coop_invoices": 0,
            "creative_coop_successful": 0,
            "manual_review_required": 0,
            "processing_errors": 0,
        }

        kpis = business_kpi_tracker.calculate_daily_kpis(zero_processing_data)
        assert kpis["status"] == "no_data"


class TestOrderTrackingSuccessMonitor:
    """Test suite for order tracking success monitoring."""

    def test_order_tracking_success_metrics(self):
        """Test order tracking success metrics."""
        if OrderTrackingSuccessMonitor is None:
            pytest.skip("OrderTrackingSuccessMonitor not implemented yet (RED phase)")

        # Arrange
        order_tracking_monitor = OrderTrackingSuccessMonitor()
        tracking_data = {
            "invoices_with_correct_numbers": 42,
            "total_invoices_processed": 45,
            "tracking_lookup_successes": 40,
            "tracking_lookup_attempts": 42,
        }

        # Act
        tracking_metrics = order_tracking_monitor.calculate_tracking_metrics(
            tracking_data
        )

        # Assert
        assert tracking_metrics["invoice_number_accuracy"] >= 0.90
        assert tracking_metrics["tracking_success_rate"] >= 0.85
        assert "tracking_effectiveness_score" in tracking_metrics

        # Verify calculations
        expected_invoice_accuracy = 42 / 45  # ~93.3%
        expected_tracking_success = 40 / 42  # ~95.2%

        assert (
            abs(tracking_metrics["invoice_number_accuracy"] - expected_invoice_accuracy)
            < 0.01
        )
        assert (
            abs(tracking_metrics["tracking_success_rate"] - expected_tracking_success)
            < 0.01
        )

    def test_invoice_number_extraction_quality_tracking(self):
        """Test invoice number extraction quality tracking."""
        if OrderTrackingSuccessMonitor is None:
            pytest.skip("OrderTrackingSuccessMonitor not implemented yet (RED phase)")

        # Arrange
        order_tracking_monitor = OrderTrackingSuccessMonitor()

        # Test invoice number extraction scenarios
        extraction_test_cases = [
            {
                "extracted_invoice_number": "CS003837319",
                "expected_format": "CS[0-9]{9}",
                "vendor_type": "Creative-Coop",
                "extraction_confidence": 0.95,
            },
            {
                "extracted_invoice_number": "HC123456",
                "expected_format": "HC[0-9]{6}",
                "vendor_type": "HarperCollins",
                "extraction_confidence": 0.98,
            },
            {
                "extracted_invoice_number": "O180987",
                "expected_format": "O18[0-9]{4}",
                "vendor_type": "OneHundred80",
                "extraction_confidence": 0.87,
            },
            {
                "extracted_invoice_number": None,
                "expected_format": "RF[0-9]{8}",
                "vendor_type": "Rifle Paper",
                "extraction_confidence": 0.0,
            },
        ]

        # Act & Assert
        for test_case in extraction_test_cases:
            quality_score = order_tracking_monitor.evaluate_invoice_number_quality(
                test_case
            )

            if test_case["extracted_invoice_number"] is not None:
                assert quality_score["format_compliance"] >= 0.80
                assert (
                    quality_score["extraction_confidence"]
                    == test_case["extraction_confidence"]
                )
            else:
                assert quality_score["format_compliance"] == 0.0
                assert quality_score["extraction_confidence"] == 0.0

    def test_tracking_system_integration_success(self):
        """Test tracking system integration success metrics."""
        if OrderTrackingSuccessMonitor is None:
            pytest.skip("OrderTrackingSuccessMonitor not implemented yet (RED phase)")

        # Arrange
        order_tracking_monitor = OrderTrackingSuccessMonitor()

        # Simulate tracking system integration results
        integration_results = [
            {
                "invoice_number": "CS003837319",
                "tracking_lookup_successful": True,
                "order_status_retrieved": True,
                "tracking_data_complete": True,
                "integration_response_time": 1.2,
            },
            {
                "invoice_number": "HC123456",
                "tracking_lookup_successful": True,
                "order_status_retrieved": True,
                "tracking_data_complete": False,  # Partial data
                "integration_response_time": 0.8,
            },
            {
                "invoice_number": "O180987",
                "tracking_lookup_successful": False,  # Lookup failed
                "order_status_retrieved": False,
                "tracking_data_complete": False,
                "integration_response_time": 5.2,  # Timeout
            },
        ]

        # Act
        for result in integration_results:
            order_tracking_monitor.record_tracking_integration_result(result)

        integration_metrics = order_tracking_monitor.get_integration_success_metrics()

        # Assert
        assert "integration_success_rate" in integration_metrics
        assert "average_response_time" in integration_metrics
        assert "data_completeness_rate" in integration_metrics

        # Verify calculations (2 out of 3 successful lookups)
        expected_success_rate = 2 / 3  # ~66.7%
        assert (
            abs(integration_metrics["integration_success_rate"] - expected_success_rate)
            < 0.01
        )

        # Verify data completeness (1 complete out of 2 successful)
        expected_completeness = 1 / 2  # 50%
        assert (
            abs(integration_metrics["data_completeness_rate"] - expected_completeness)
            < 0.01
        )


class TestManualReviewReductionTracker:
    """Test suite for manual review reduction tracking."""

    def test_manual_review_reduction_tracking(self):
        """Test manual review reduction metrics."""
        if ManualReviewReductionTracker is None:
            pytest.skip("ManualReviewReductionTracker not implemented yet (RED phase)")

        # Arrange
        review_tracker = ManualReviewReductionTracker()

        # Historical baseline
        baseline_data = {"manual_review_rate": 0.70}  # 70% manual review before

        # Current performance
        current_data = {"manual_review_rate": 0.15}  # 15% manual review now

        # Act
        reduction_metrics = review_tracker.calculate_review_reduction(
            baseline_data, current_data
        )

        # Assert
        assert (
            reduction_metrics["review_reduction_percentage"] >= 0.50
        )  # At least 50% reduction
        assert reduction_metrics["automation_effectiveness"] >= 0.80

        # Verify calculations
        expected_reduction = (0.70 - 0.15) / 0.70  # ~78.6% reduction
        expected_automation = 1.0 - 0.15  # 85% automation

        assert (
            abs(reduction_metrics["review_reduction_percentage"] - expected_reduction)
            < 0.01
        )
        assert (
            abs(reduction_metrics["automation_effectiveness"] - expected_automation)
            < 0.01
        )

    def test_automation_progress_tracking(self):
        """Test automation progress tracking over time."""
        if ManualReviewReductionTracker is None:
            pytest.skip("ManualReviewReductionTracker not implemented yet (RED phase)")

        # Arrange
        review_tracker = ManualReviewReductionTracker()

        # Simulate automation progress over time
        progress_data = [
            {"period": "2024-Q1", "manual_review_rate": 0.70, "automation_rate": 0.30},
            {"period": "2024-Q2", "manual_review_rate": 0.45, "automation_rate": 0.55},
            {"period": "2024-Q3", "manual_review_rate": 0.25, "automation_rate": 0.75},
            {"period": "2024-Q4", "manual_review_rate": 0.15, "automation_rate": 0.85},
        ]

        # Act
        for data in progress_data:
            review_tracker.record_automation_progress(data)

        progress_analysis = review_tracker.get_automation_progress_analysis()

        # Assert
        assert "automation_trend" in progress_analysis
        assert "total_improvement" in progress_analysis
        assert "quarterly_improvement_rate" in progress_analysis

        # Verify trend detection (should be 'improving')
        assert progress_analysis["automation_trend"] == "improving"

        # Verify total improvement calculation
        expected_total_improvement = (0.85 - 0.30) / 0.30  # ~183% improvement
        assert (
            progress_analysis["total_improvement"] >= 1.5
        )  # At least 150% improvement

    def test_creative_coop_automation_success(self):
        """Test Creative-Coop specific automation success tracking."""
        if ManualReviewReductionTracker is None:
            pytest.skip("ManualReviewReductionTracker not implemented yet (RED phase)")

        # Arrange
        review_tracker = ManualReviewReductionTracker()

        # Creative-Coop automation data based on our achievements
        creative_coop_data = {
            "vendor_type": "Creative-Coop",
            "baseline_manual_rate": 0.95,  # 95% manual before automation
            "current_manual_rate": 0.14,  # 14% manual after (86% automated)
            "accuracy_threshold_met": True,  # 85.7% accuracy achieved
            "processing_time_improved": True,  # Sub-60 second processing
            "line_item_extraction_rate": 0.857,  # 85.7% line item success
        }

        # Act
        cc_automation_metrics = (
            review_tracker.calculate_vendor_specific_automation_success(
                creative_coop_data
            )
        )

        # Assert
        assert "automation_success_rate" in cc_automation_metrics
        assert "manual_review_reduction" in cc_automation_metrics
        assert "overall_effectiveness_score" in cc_automation_metrics

        # Verify Creative-Coop specific calculations
        expected_automation_rate = 1.0 - 0.14  # 86% automation
        expected_reduction = (0.95 - 0.14) / 0.95  # ~85.3% reduction

        assert cc_automation_metrics["automation_success_rate"] >= 0.85
        assert cc_automation_metrics["manual_review_reduction"] >= 0.80
        assert cc_automation_metrics["overall_effectiveness_score"] >= 0.85

    def test_roi_calculation_for_automation(self):
        """Test ROI calculation for automation improvements."""
        if ManualReviewReductionTracker is None:
            pytest.skip("ManualReviewReductionTracker not implemented yet (RED phase)")

        # Arrange
        review_tracker = ManualReviewReductionTracker()

        # ROI calculation data
        roi_data = {
            "manual_processing_cost_per_invoice": 25.0,  # $25 per manual review
            "automated_processing_cost_per_invoice": 2.0,  # $2 per automated processing
            "monthly_invoice_volume": 500,  # 500 invoices per month
            "baseline_manual_rate": 0.70,  # 70% manual before
            "current_manual_rate": 0.15,  # 15% manual now
            "development_investment": 50000,  # $50K development investment
        }

        # Act
        roi_metrics = review_tracker.calculate_automation_roi(roi_data)

        # Assert
        assert "monthly_cost_savings" in roi_metrics
        assert "annual_cost_savings" in roi_metrics
        assert "payback_period_months" in roi_metrics
        assert "roi_percentage" in roi_metrics

        # Verify cost savings calculation
        baseline_monthly_cost = 500 * 0.70 * 25.0 + 500 * 0.30 * 2.0  # $8,800
        current_monthly_cost = 500 * 0.15 * 25.0 + 500 * 0.85 * 2.0  # $2,725
        expected_monthly_savings = (
            baseline_monthly_cost - current_monthly_cost
        )  # $6,075

        assert abs(roi_metrics["monthly_cost_savings"] - expected_monthly_savings) < 1.0
        assert roi_metrics["annual_cost_savings"] >= 70000  # At least $70K annually
        assert roi_metrics["payback_period_months"] <= 12  # Payback within 12 months


class TestBusinessKPIIntegration:
    """Integration tests for business KPI components."""

    def test_comprehensive_business_kpi_dashboard_integration(self):
        """Test comprehensive business KPI integration for dashboard."""
        if (
            BusinessKPITracker is None
            or OrderTrackingSuccessMonitor is None
            or ManualReviewReductionTracker is None
        ):
            pytest.skip("Business KPI components not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()
        order_tracking_monitor = OrderTrackingSuccessMonitor()
        review_tracker = ManualReviewReductionTracker()

        # Simulate comprehensive daily processing
        comprehensive_data = {
            "business_metrics": {
                "total_invoices_processed": 100,
                "successful_processing_count": 92,
                "creative_coop_invoices": 35,
                "creative_coop_successful": 30,
                "manual_review_required": 8,
                "processing_errors": 8,
            },
            "tracking_metrics": {
                "invoices_with_correct_numbers": 88,
                "total_invoices_processed": 92,
                "tracking_lookup_successes": 85,
                "tracking_lookup_attempts": 88,
            },
            "automation_metrics": {
                "baseline_manual_rate": 0.75,
                "current_manual_rate": 0.08,
                "automation_effectiveness": 0.92,
            },
        }

        # Act
        # Calculate business KPIs
        business_kpis = business_kpi_tracker.calculate_daily_kpis(
            comprehensive_data["business_metrics"]
        )

        # Calculate tracking metrics
        tracking_metrics = order_tracking_monitor.calculate_tracking_metrics(
            comprehensive_data["tracking_metrics"]
        )

        # Calculate automation metrics
        automation_metrics = review_tracker.calculate_review_reduction(
            {
                "manual_review_rate": comprehensive_data["automation_metrics"][
                    "baseline_manual_rate"
                ]
            },
            {
                "manual_review_rate": comprehensive_data["automation_metrics"][
                    "current_manual_rate"
                ]
            },
        )

        # Combine for dashboard
        dashboard_kpis = {
            "business_performance": business_kpis,
            "tracking_performance": tracking_metrics,
            "automation_performance": automation_metrics,
        }

        # Assert
        # Business performance validation
        assert dashboard_kpis["business_performance"]["overall_success_rate"] >= 0.90
        assert (
            dashboard_kpis["business_performance"]["creative_coop_success_rate"] >= 0.85
        )
        assert dashboard_kpis["business_performance"]["manual_review_rate"] <= 0.10

        # Tracking performance validation
        assert dashboard_kpis["tracking_performance"]["invoice_number_accuracy"] >= 0.90
        assert dashboard_kpis["tracking_performance"]["tracking_success_rate"] >= 0.90

        # Automation performance validation
        assert (
            dashboard_kpis["automation_performance"]["review_reduction_percentage"]
            >= 0.80
        )
        assert (
            dashboard_kpis["automation_performance"]["automation_effectiveness"] >= 0.90
        )

    def test_real_time_kpi_updates(self):
        """Test real-time KPI updates as processing events occur."""
        if BusinessKPITracker is None:
            pytest.skip("BusinessKPITracker not implemented yet (RED phase)")

        # Arrange
        business_kpi_tracker = BusinessKPITracker()

        # Simulate real-time processing events
        real_time_events = [
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.92,
            },
            {
                "vendor_type": "HarperCollins",
                "processing_successful": True,
                "accuracy_score": 0.98,
            },
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.89,
            },
            {
                "vendor_type": "OneHundred80",
                "processing_successful": False,
                "accuracy_score": 0.65,
            },
            {
                "vendor_type": "Creative-Coop",
                "processing_successful": True,
                "accuracy_score": 0.94,
            },
        ]

        # Act & Assert - KPIs should update in real-time
        timestamp = time.time()

        for i, event in enumerate(real_time_events):
            # Record event
            business_kpi_tracker.record_processing_event(event, timestamp + i)

            # Get updated KPIs
            current_kpis = business_kpi_tracker.get_current_kpis()

            # Verify KPIs reflect current state
            assert current_kpis["sample_size"] == i + 1

            # Verify success rate calculation
            successful_events = sum(
                1 for e in real_time_events[: i + 1] if e["processing_successful"]
            )
            expected_success_rate = successful_events / (i + 1)
            assert (
                abs(current_kpis["recent_success_rate"] - expected_success_rate) < 0.01
            )

        # Final verification
        final_kpis = business_kpi_tracker.get_current_kpis()
        assert final_kpis["sample_size"] == len(real_time_events)
        assert final_kpis["recent_success_rate"] == 4 / 5  # 4 successful out of 5


if __name__ == "__main__":
    # Run tests with verbose output to see RED phase failures
    pytest.main([__file__, "-v", "-s"])
