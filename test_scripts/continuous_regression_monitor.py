#!/usr/bin/env python3
"""
Continuous regression monitoring for vendor processing
Automated pipeline that runs after any changes to Creative-Coop processing
"""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Import our regression framework
try:
    from vendor_regression_framework import RegressionSummary, VendorRegressionTester

    FRAMEWORK_AVAILABLE = True
except ImportError:
    FRAMEWORK_AVAILABLE = False

# Try to import optional scheduling dependencies
try:
    import schedule

    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False


class ContinuousRegressionMonitor:
    """Continuous monitoring for vendor processing regressions"""

    def __init__(self, monitoring_interval_hours: int = 6):
        self.monitoring_interval = monitoring_interval_hours
        if FRAMEWORK_AVAILABLE:
            self.tester = VendorRegressionTester()
        else:
            self.tester = None

        self.history_file = Path("test_scripts/regression_history.json")
        self.alert_threshold = 0.8  # Alert if success rate drops below 80%
        self.performance_threshold = 2.0  # Alert if processing time increases by 2x

    def start_monitoring(self):
        """Start continuous regression monitoring"""
        if not FRAMEWORK_AVAILABLE:
            print("❌ Regression framework not available - cannot start monitoring")
            return

        print(
            f"🔄 Starting continuous regression monitoring (every {self.monitoring_interval}h)"
        )

        if SCHEDULE_AVAILABLE:
            # Schedule regular regression tests
            schedule.every(self.monitoring_interval).hours.do(
                self.run_scheduled_regression_test
            )

            # Run initial test
            self.run_scheduled_regression_test()

            # Keep monitoring running
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        else:
            print("⚠️ Schedule library not available - running single test")
            self.run_scheduled_regression_test()

    def run_scheduled_regression_test(self):
        """Run scheduled regression test and analyze trends"""
        print(f"\n⏰ Running scheduled regression test at {datetime.now()}")

        try:
            # Run regression tests
            summary = self.tester.run_all_regression_tests()

            # Store results
            self.store_regression_history(summary)

            # Analyze trends
            self.analyze_regression_trends()

            # Check for alerts
            self.check_regression_alerts(summary)

            print(f"✅ Scheduled regression test completed")

        except Exception as e:
            print(f"❌ Scheduled regression test failed: {e}")
            self.send_alert("Regression Test Error", f"Scheduled test failed: {e}")

    def run_single_regression_test(self) -> Dict[str, Any]:
        """Run a single regression test and return results"""
        if not FRAMEWORK_AVAILABLE:
            return {"error": "Regression framework not available"}

        try:
            summary = self.tester.run_all_regression_tests()

            # Store results
            self.store_regression_history(summary)

            # Check for alerts
            alerts = self.check_regression_alerts(summary, send_alerts=False)

            return {
                "success": True,
                "summary": {
                    "total_tests": summary.total_tests,
                    "passed_tests": summary.passed_tests,
                    "failed_tests": summary.failed_tests,
                    "success_rate": (
                        summary.passed_tests / summary.total_tests
                        if summary.total_tests > 0
                        else 0
                    ),
                    "total_time": summary.total_time,
                    "overall_success": summary.overall_success,
                },
                "alerts": alerts,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def store_regression_history(self, summary: RegressionSummary):
        """Store regression test results for trend analysis"""
        # Load existing history
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                history = []
        else:
            history = []

        # Add current results
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": summary.total_tests,
            "passed_tests": summary.passed_tests,
            "failed_tests": summary.failed_tests,
            "success_rate": (
                summary.passed_tests / summary.total_tests
                if summary.total_tests > 0
                else 0
            ),
            "total_time": summary.total_time,
            "vendor_results": {
                result.vendor: {
                    "passed": result.passed,
                    "processing_time": result.processing_time,
                    "memory_usage_mb": result.memory_usage_mb,
                    "error_message": result.error_message,
                }
                for result in summary.test_results
            },
        }

        history.append(history_entry)

        # Keep only last 100 entries
        history = history[-100:]

        # Save updated history
        try:
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save regression history: {e}")

    def analyze_regression_trends(self):
        """Analyze regression trends over time"""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return

        if len(history) < 2:
            return

        # Analyze recent trends (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_results = []

        for entry in history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time > recent_cutoff:
                    recent_results.append(entry)
            except (ValueError, KeyError):
                continue

        if len(recent_results) >= 2:
            # Calculate trend metrics
            success_rates = [entry["success_rate"] for entry in recent_results]
            processing_times = [entry["total_time"] for entry in recent_results]

            success_trend = (
                success_rates[-1] - success_rates[0] if len(success_rates) > 1 else 0
            )
            time_trend = (
                processing_times[-1] - processing_times[0]
                if len(processing_times) > 1
                else 0
            )

            print(f"📈 24h Regression Trends:")
            print(f"   Success Rate: {success_trend:+.1%}")
            print(f"   Processing Time: {time_trend:+.1f}s")

            # Alert on negative trends
            if success_trend < -0.1:  # 10% drop in success rate
                self.send_alert(
                    "Regression Trend Alert",
                    f"Success rate declined by {success_trend:.1%} in last 24h",
                )

            if time_trend > 30:  # 30s increase in processing time
                self.send_alert(
                    "Performance Trend Alert",
                    f"Processing time increased by {time_trend:.1f}s in last 24h",
                )

    def check_regression_alerts(
        self, summary: RegressionSummary, send_alerts: bool = True
    ) -> List[str]:
        """Check if current results warrant alerts"""
        alerts = []

        # Success rate alert
        success_rate = (
            summary.passed_tests / summary.total_tests if summary.total_tests > 0 else 0
        )
        if success_rate < self.alert_threshold:
            alerts.append(
                f"Success rate ({success_rate:.1%}) below threshold ({self.alert_threshold:.1%})"
            )

        # Performance alerts
        for result in summary.test_results:
            if result.processing_time > 60:  # Alert if any test takes > 60s
                alerts.append(
                    f"{result.vendor} processing time ({result.processing_time:.1f}s) exceeds 60s"
                )

        # Memory alerts
        for result in summary.test_results:
            if result.memory_usage_mb > 100:  # Alert if memory usage > 100MB
                alerts.append(
                    f"{result.vendor} memory usage ({result.memory_usage_mb:.1f}MB) exceeds 100MB"
                )

        # Critical failure alerts
        critical_vendors = ["HarperCollins", "OneHundred80", "Creative-Coop"]
        for result in summary.test_results:
            if result.vendor in critical_vendors and not result.passed:
                alerts.append(f"CRITICAL: {result.vendor} regression test failed")

        # Send alerts if any and sending is enabled
        if alerts and send_alerts:
            self.send_alert("Regression Alert", "\n".join(alerts))

        return alerts

    def send_alert(self, title: str, message: str):
        """Send regression alert (can be extended with email/Slack integration)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"[{timestamp}] {title}\n{message}"

        # Log alert
        print(f"🚨 ALERT: {alert_message}")

        # Store alert
        alerts_file = Path("test_scripts/regression_alerts.log")
        try:
            with open(alerts_file, "a") as f:
                f.write(f"{alert_message}\n\n")
        except Exception as e:
            print(f"⚠️ Failed to write alert to log: {e}")

        # TODO: Add email/Slack integration for production alerts

    def generate_trend_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate trend report for specified number of days"""
        if not self.history_file.exists():
            return {"error": "No historical data available"}

        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"error": "Failed to load historical data"}

        # Filter to specified timeframe
        cutoff = datetime.now() - timedelta(days=days)
        recent_history = []

        for entry in history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time > cutoff:
                    recent_history.append(entry)
            except (ValueError, KeyError):
                continue

        if not recent_history:
            return {"error": f"No data available for last {days} days"}

        # Calculate trend metrics
        success_rates = [entry["success_rate"] for entry in recent_history]
        processing_times = [entry["total_time"] for entry in recent_history]

        trend_report = {
            "period_days": days,
            "total_tests_run": len(recent_history),
            "average_success_rate": sum(success_rates) / len(success_rates),
            "average_processing_time": sum(processing_times) / len(processing_times),
            "success_rate_trend": (
                success_rates[-1] - success_rates[0] if len(success_rates) > 1 else 0
            ),
            "processing_time_trend": (
                processing_times[-1] - processing_times[0]
                if len(processing_times) > 1
                else 0
            ),
            "vendor_reliability": {},
        }

        # Calculate per-vendor reliability
        for vendor in [
            "HarperCollins",
            "OneHundred80",
            "Rifle Paper",
            "Core Functions",
            "Memory Usage",
            "Performance",
        ]:
            vendor_results = []
            for entry in recent_history:
                if vendor in entry.get("vendor_results", {}):
                    vendor_results.append(entry["vendor_results"][vendor]["passed"])

            if vendor_results:
                trend_report["vendor_reliability"][vendor] = {
                    "success_rate": sum(vendor_results) / len(vendor_results),
                    "total_tests": len(vendor_results),
                }

        return trend_report

    def get_latest_status(self) -> Dict[str, Any]:
        """Get the latest regression test status"""
        if not self.history_file.exists():
            return {"status": "No test history available"}

        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"status": "Failed to load test history"}

        if not history:
            return {"status": "No test results available"}

        latest = history[-1]

        # Calculate time since last test
        try:
            last_test_time = datetime.fromisoformat(latest["timestamp"])
            time_since_last = datetime.now() - last_test_time
            hours_since = time_since_last.total_seconds() / 3600
        except (ValueError, KeyError):
            hours_since = float("inf")

        status = {
            "last_test": latest["timestamp"],
            "hours_since_last_test": hours_since,
            "success_rate": latest["success_rate"],
            "total_tests": latest["total_tests"],
            "failed_tests": latest["failed_tests"],
            "processing_time": latest["total_time"],
            "status": (
                "HEALTHY"
                if latest["success_rate"] >= self.alert_threshold
                else "DEGRADED"
            ),
            "vendor_status": {},
        }

        # Add per-vendor status
        for vendor, result in latest.get("vendor_results", {}).items():
            status["vendor_status"][vendor] = {
                "passed": result["passed"],
                "processing_time": result["processing_time"],
                "has_error": bool(result["error_message"]),
            }

        return status


def main():
    """Run continuous regression monitoring or single test"""
    import sys

    monitor = ContinuousRegressionMonitor(monitoring_interval_hours=6)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "single":
            print("🔍 Running single regression test...")
            result = monitor.run_single_regression_test()

            if result.get("success"):
                summary = result["summary"]
                print(f"\n📊 Test Results:")
                print(f"   Success Rate: {summary['success_rate']:.1%}")
                print(f"   Tests: {summary['passed_tests']}/{summary['total_tests']}")
                print(f"   Time: {summary['total_time']:.1f}s")
                print(
                    f"   Status: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}"
                )

                if result["alerts"]:
                    print(f"\n🚨 Alerts:")
                    for alert in result["alerts"]:
                        print(f"   - {alert}")
            else:
                print(f"❌ Test failed: {result.get('error', 'Unknown error')}")

            return (
                0
                if result.get("success") and result["summary"]["overall_success"]
                else 1
            )

        elif command == "status":
            print("📊 Getting latest regression test status...")
            status = monitor.get_latest_status()

            if "status" in status and status["status"] == "No test history available":
                print("⚠️ No test history available - run a test first")
                return 1

            print(f"\n📈 Latest Status:")
            print(f"   Last Test: {status.get('last_test', 'Unknown')}")
            print(f"   Hours Since: {status.get('hours_since_last_test', 0):.1f}")
            print(f"   Success Rate: {status.get('success_rate', 0):.1%}")
            print(f"   Status: {status.get('status', 'Unknown')}")

            return 0

        elif command == "trends":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            print(f"📈 Generating {days}-day trend report...")

            trends = monitor.generate_trend_report(days)

            if "error" in trends:
                print(f"❌ {trends['error']}")
                return 1

            print(f"\n📊 {days}-Day Trend Report:")
            print(f"   Tests Run: {trends['total_tests_run']}")
            print(f"   Avg Success Rate: {trends['average_success_rate']:.1%}")
            print(f"   Avg Processing Time: {trends['average_processing_time']:.1f}s")

            trend_dir = (
                "↗️"
                if trends["success_rate_trend"] > 0
                else "↘️" if trends["success_rate_trend"] < 0 else "➡️"
            )
            print(f"   Success Trend: {trend_dir} {trends['success_rate_trend']:+.1%}")

            if trends["vendor_reliability"]:
                print(f"\n🏬 Vendor Reliability:")
                for vendor, reliability in trends["vendor_reliability"].items():
                    print(
                        f"   {vendor}: {reliability['success_rate']:.1%} ({reliability['total_tests']} tests)"
                    )

            return 0

        else:
            print(f"❌ Unknown command: {command}")
            print(
                "Usage: python continuous_regression_monitor.py [single|status|trends [days]|monitor]"
            )
            return 1
    else:
        # Default: start continuous monitoring
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            print("\n🔄 Continuous regression monitoring stopped")


if __name__ == "__main__":
    import sys

    sys.exit(main() or 0)
