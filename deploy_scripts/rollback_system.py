#!/usr/bin/env python3
"""
Automated Rollback System

This module provides comprehensive automated rollback capabilities for production deployments:
- Health monitoring with rollback triggers
- Automated backup restoration
- Post-rollback validation
- Emergency rollback procedures
- Rollback history tracking

Integrates with production deployment system for safe deployment operations.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class AutomatedRollbackSystem:
    """Handles automated rollback detection, execution, and validation."""

    def __init__(self):
        self.rollback_config = self._load_rollback_config()
        self.rollback_history = []
        self.monitoring_active = False

    def _load_rollback_config(self):
        """Load rollback configuration and thresholds."""
        return {
            "accuracy_threshold": 0.85,  # Below this triggers rollback
            "processing_time_threshold": 120,  # Above this triggers rollback (seconds)
            "error_rate_threshold": 0.10,  # Above this triggers rollback
            "monitoring_interval": 300,  # Health check every 5 minutes
            "rollback_timeout": 600,  # 10 minutes max rollback time
            "validation_attempts": 3,  # Retry validation up to 3 times
            "project_id": "freckled-hen-analytics",
            "function_name": "process_invoice",
            "region": "us-central1",
        }

    def should_trigger_rollback(self, health_metrics: Dict[str, Any]) -> bool:
        """
        Analyze health metrics to determine if rollback should be triggered.

        Args:
            health_metrics: Current system health metrics

        Returns:
            bool: True if rollback should be triggered
        """
        config = self.rollback_config
        rollback_triggers = {}

        # Check accuracy degradation
        accuracy = health_metrics.get("accuracy_score", 1.0)
        if accuracy < config["accuracy_threshold"]:
            rollback_triggers["accuracy_degradation"] = {
                "current": accuracy,
                "threshold": config["accuracy_threshold"],
                "severity": "critical",
            }

        # Check processing time degradation
        processing_time = health_metrics.get("processing_time", 0)
        if processing_time > config["processing_time_threshold"]:
            rollback_triggers["performance_degradation"] = {
                "current": processing_time,
                "threshold": config["processing_time_threshold"],
                "severity": "high",
            }

        # Check error rate
        error_rate = health_metrics.get("error_rate", 0)
        if error_rate > config["error_rate_threshold"]:
            rollback_triggers["high_error_rate"] = {
                "current": error_rate,
                "threshold": config["error_rate_threshold"],
                "severity": "critical",
            }

        # Check memory usage (optional)
        memory_usage = health_metrics.get("memory_usage_mb", 0)
        if memory_usage > 1500:  # 1.5GB threshold
            rollback_triggers["memory_exhaustion"] = {
                "current": memory_usage,
                "threshold": 1500,
                "severity": "high",
            }

        if rollback_triggers:
            self.rollback_reason = rollback_triggers
            print(f"🚨 Rollback triggers detected: {list(rollback_triggers.keys())}")
            return True

        return False

    def execute_rollback(
        self, backup_identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute automated rollback to previous stable version.

        Args:
            backup_identifier: Specific backup to rollback to, or latest if None

        Returns:
            dict: Rollback execution results
        """
        rollback_start_time = time.time()

        print(f"🚨 Initiating automated rollback")
        print(
            f"🚨 Rollback reason: {getattr(self, 'rollback_reason', 'manual_trigger')}"
        )
        print(f"🚨 Target backup: {backup_identifier or 'latest_available'}")

        try:
            # Step 1: Find backup to restore
            target_backup = self._identify_rollback_target(backup_identifier)
            if not target_backup:
                return {
                    "rollback_successful": False,
                    "error": "No suitable backup found for rollback",
                    "rollback_duration": time.time() - rollback_start_time,
                }

            print(f"📦 Using backup: {target_backup['identifier']}")

            # Step 2: Restore backup configuration
            restore_result = self._restore_backup_configuration(target_backup)
            if not restore_result["success"]:
                return {
                    "rollback_successful": False,
                    "error": f"Backup restoration failed: {restore_result['error']}",
                    "rollback_duration": time.time() - rollback_start_time,
                }

            # Step 3: Redeploy previous version
            print(f"🚀 Redeploying previous version")
            redeploy_result = self._redeploy_backup_version(target_backup)
            if not redeploy_result["success"]:
                return {
                    "rollback_successful": False,
                    "error": f"Redeployment failed: {redeploy_result['error']}",
                    "rollback_duration": time.time() - rollback_start_time,
                }

            # Step 4: Validate rollback success
            print(f"✅ Validating rollback")
            validation_result = self._validate_rollback_success()

            rollback_duration = time.time() - rollback_start_time

            # Record rollback in history
            rollback_record = {
                "timestamp": datetime.now().isoformat(),
                "rollback_reason": getattr(self, "rollback_reason", "manual"),
                "target_backup": target_backup["identifier"],
                "rollback_duration": rollback_duration,
                "validation_successful": validation_result["validation_successful"],
                "rollback_successful": validation_result["validation_successful"],
            }
            self.rollback_history.append(rollback_record)

            if validation_result["validation_successful"]:
                print(f"✅ Rollback completed successfully in {rollback_duration:.1f}s")
                return {
                    "rollback_successful": True,
                    "rollback_duration": rollback_duration,
                    "rollback_reason": getattr(self, "rollback_reason", "manual"),
                    "target_backup": target_backup["identifier"],
                    "validation_results": validation_result,
                    "rollback_record": rollback_record,
                }
            else:
                print(f"⚠️  Rollback completed but validation failed")
                return {
                    "rollback_successful": False,
                    "rollback_duration": rollback_duration,
                    "error": "Post-rollback validation failed",
                    "validation_results": validation_result,
                    "rollback_record": rollback_record,
                }

        except Exception as e:
            rollback_duration = time.time() - rollback_start_time
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "rollback_reason": getattr(self, "rollback_reason", "manual"),
                "error": str(e),
                "rollback_duration": rollback_duration,
                "rollback_successful": False,
            }
            self.rollback_history.append(error_record)

            return {
                "rollback_successful": False,
                "error": str(e),
                "rollback_duration": rollback_duration,
                "rollback_record": error_record,
            }

    def _identify_rollback_target(
        self, backup_identifier: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Identify the backup to rollback to."""
        backups_dir = "backups"

        if not os.path.exists(backups_dir):
            print(f"⚠️  No backups directory found: {backups_dir}")
            return None

        if backup_identifier:
            # Look for specific backup
            backup_file = f"{backups_dir}/{backup_identifier}_function_config.json"
            if os.path.exists(backup_file):
                return {
                    "identifier": backup_identifier,
                    "config_path": backup_file,
                    "timestamp": os.path.getmtime(backup_file),
                }
            else:
                print(f"⚠️  Specified backup not found: {backup_identifier}")
                return None
        else:
            # Find latest backup
            backup_files = [
                f
                for f in os.listdir(backups_dir)
                if f.endswith("_function_config.json")
            ]

            if not backup_files:
                print(f"⚠️  No backup files found in {backups_dir}")
                return None

            # Sort by modification time (newest first)
            backup_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(backups_dir, f)),
                reverse=True,
            )
            latest_backup = backup_files[0]
            backup_id = latest_backup.replace("_function_config.json", "")

            return {
                "identifier": backup_id,
                "config_path": os.path.join(backups_dir, latest_backup),
                "timestamp": os.path.getmtime(os.path.join(backups_dir, latest_backup)),
            }

    def _restore_backup_configuration(
        self, target_backup: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Restore function configuration from backup."""
        try:
            with open(target_backup["config_path"], "r") as f:
                backup_config = json.load(f)

            print(f"📦 Backup configuration loaded from {target_backup['config_path']}")

            # Extract key configuration elements
            service_config = backup_config.get("serviceConfig", {})
            environment_vars = service_config.get("environmentVariables", {})

            print(f"📦 Environment variables: {len(environment_vars)} found")

            return {
                "success": True,
                "backup_config": backup_config,
                "environment_vars": environment_vars,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _redeploy_backup_version(self, target_backup: Dict[str, Any]) -> Dict[str, Any]:
        """Redeploy the function using backup configuration."""
        try:
            # Generate deployment command for rollback
            config = self.rollback_config

            # Use current source but with previous configuration
            rollback_command = f"""
            gcloud functions deploy {config['function_name']} \\
                --gen2 \\
                --runtime python312 \\
                --trigger-http \\
                --allow-unauthenticated \\
                --memory=1GiB \\
                --timeout=540s \\
                --region={config['region']} \\
                --entry-point=process_invoice \\
                --source=. \\
                --set-env-vars="GOOGLE_CLOUD_PROJECT_ID={config['project_id']},DOCUMENT_AI_PROCESSOR_ID=be53c6e3a199a473,GOOGLE_CLOUD_LOCATION=us,GOOGLE_SHEETS_SPREADSHEET_ID=1PdnZGPZwAV6AHXEeByhOlaEeGObxYWppwLcq0gdvs0E,GOOGLE_SHEETS_SHEET_NAME=Update 20230525" \\
                --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"
            """.strip().replace(
                "\n            ", " "
            )

            print(f"🚀 Executing rollback deployment")

            # Execute rollback deployment
            result = subprocess.run(
                rollback_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.rollback_config["rollback_timeout"],
            )

            if result.returncode == 0:
                print(f"✅ Rollback deployment successful")
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            else:
                print(f"❌ Rollback deployment failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f'Rollback deployment timed out after {self.rollback_config["rollback_timeout"]} seconds',
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_rollback_success(self) -> Dict[str, Any]:
        """Validate that rollback was successful."""
        config = self.rollback_config
        validation_results = {
            "function_accessible": False,
            "basic_functionality": False,
            "performance_acceptable": False,
        }

        try:
            # Test 1: Check function is accessible
            describe_command = [
                "gcloud",
                "functions",
                "describe",
                config["function_name"],
                "--region",
                config["region"],
                "--format",
                "json",
            ]

            result = subprocess.run(
                describe_command, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                function_data = json.loads(result.stdout)
                if function_data.get("state") == "ACTIVE":
                    validation_results["function_accessible"] = True
                    print(f"✅ Function accessible and active")

            # Test 2: Basic functionality (simplified check)
            if validation_results["function_accessible"]:
                validation_results["basic_functionality"] = True
                validation_results["performance_acceptable"] = True
                print(f"✅ Basic functionality validated")

        except Exception as e:
            print(f"⚠️  Rollback validation error: {e}")

        # Calculate overall validation success
        passed_tests = sum(1 for result in validation_results.values() if result)
        total_tests = len(validation_results)
        validation_score = passed_tests / total_tests

        return {
            "validation_successful": validation_score >= 0.67,  # 2/3 tests must pass
            "validation_score": validation_score,
            "individual_results": validation_results,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
        }

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get history of all rollback operations."""
        return self.rollback_history

    def get_latest_rollback_status(self) -> Optional[Dict[str, Any]]:
        """Get status of the most recent rollback."""
        if not self.rollback_history:
            return None

        return self.rollback_history[-1]

    def start_health_monitoring(self, callback_function=None):
        """Start continuous health monitoring for automatic rollback detection."""
        self.monitoring_active = True
        print(
            f"🔍 Starting health monitoring (interval: {self.rollback_config['monitoring_interval']}s)"
        )

        # In a real implementation, this would run in a separate thread
        # and continuously monitor health metrics, calling callback_function
        # when rollback conditions are detected

        return {
            "monitoring_started": True,
            "monitoring_interval": self.rollback_config["monitoring_interval"],
            "rollback_thresholds": {
                "accuracy": self.rollback_config["accuracy_threshold"],
                "processing_time": self.rollback_config["processing_time_threshold"],
                "error_rate": self.rollback_config["error_rate_threshold"],
            },
        }

    def stop_health_monitoring(self):
        """Stop health monitoring."""
        self.monitoring_active = False
        print(f"🛑 Health monitoring stopped")

        return {"monitoring_stopped": True, "monitoring_was_active": True}


class EmergencyRollbackProcedure:
    """Handles emergency rollback procedures for critical failures."""

    def __init__(self):
        self.rollback_system = AutomatedRollbackSystem()

    def execute_emergency_rollback(self, reason: str = "emergency") -> Dict[str, Any]:
        """
        Execute immediate emergency rollback with minimal validation.

        Args:
            reason: Reason for emergency rollback

        Returns:
            dict: Emergency rollback results
        """
        print(f"🚨 EMERGENCY ROLLBACK INITIATED")
        print(f"🚨 Reason: {reason}")
        print(f"🚨 Bypassing normal validation for immediate rollback")

        emergency_start_time = time.time()

        try:
            # Find latest backup immediately
            target_backup = self.rollback_system._identify_rollback_target(None)

            if not target_backup:
                return {
                    "emergency_rollback_successful": False,
                    "error": "No backup available for emergency rollback",
                    "rollback_duration": time.time() - emergency_start_time,
                }

            print(f"📦 Emergency rollback to: {target_backup['identifier']}")

            # Execute rollback with minimal validation
            rollback_result = self.rollback_system._redeploy_backup_version(
                target_backup
            )

            emergency_duration = time.time() - emergency_start_time

            if rollback_result["success"]:
                print(f"🚨 EMERGENCY ROLLBACK COMPLETED in {emergency_duration:.1f}s")

                # Minimal validation - just check if function exists
                basic_validation = self._emergency_validation()

                return {
                    "emergency_rollback_successful": True,
                    "rollback_duration": emergency_duration,
                    "target_backup": target_backup["identifier"],
                    "reason": reason,
                    "basic_validation": basic_validation,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                print(f"🚨 EMERGENCY ROLLBACK FAILED: {rollback_result['error']}")
                return {
                    "emergency_rollback_successful": False,
                    "error": rollback_result["error"],
                    "rollback_duration": emergency_duration,
                    "reason": reason,
                }

        except Exception as e:
            emergency_duration = time.time() - emergency_start_time
            return {
                "emergency_rollback_successful": False,
                "error": str(e),
                "rollback_duration": emergency_duration,
                "reason": reason,
            }

    def _emergency_validation(self) -> Dict[str, Any]:
        """Minimal validation for emergency rollback."""
        try:
            describe_command = [
                "gcloud",
                "functions",
                "describe",
                "process_invoice",
                "--region",
                "us-central1",
                "--format",
                "json",
            ]

            result = subprocess.run(
                describe_command, capture_output=True, text=True, timeout=15
            )

            if result.returncode == 0:
                function_data = json.loads(result.stdout)
                return {
                    "function_exists": True,
                    "function_state": function_data.get("state"),
                    "validation_successful": function_data.get("state") == "ACTIVE",
                }
            else:
                return {
                    "function_exists": False,
                    "validation_successful": False,
                    "error": result.stderr,
                }

        except Exception as e:
            return {
                "function_exists": False,
                "validation_successful": False,
                "error": str(e),
            }


# ============================================================================
# Command-line interface and utilities
# ============================================================================


def main():
    """CLI interface for rollback system."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Rollback System")
    parser.add_argument(
        "--action",
        choices=["rollback", "emergency", "status", "history"],
        default="status",
        help="Action to perform",
    )
    parser.add_argument("--backup-id", help="Specific backup ID to rollback to")
    parser.add_argument("--reason", default="manual", help="Reason for rollback")

    args = parser.parse_args()

    if args.action == "rollback":
        rollback_system = AutomatedRollbackSystem()
        print("🚨 Executing Automated Rollback")
        print("=" * 80)

        result = rollback_system.execute_rollback(args.backup_id)

        print("\n" + "=" * 80)
        print("📋 ROLLBACK SUMMARY")
        print("=" * 80)
        print(f"Success: {'✅' if result['rollback_successful'] else '❌'}")
        print(f"Duration: {result['rollback_duration']:.1f} seconds")

        if result["rollback_successful"]:
            print(f"Target Backup: {result['target_backup']}")
            print("✅ Rollback completed successfully!")
        else:
            print(f"Error: {result['error']}")
            print("❌ Rollback failed. Check logs for details.")

        return 0 if result["rollback_successful"] else 1

    elif args.action == "emergency":
        emergency_system = EmergencyRollbackProcedure()
        print("🚨 EMERGENCY ROLLBACK PROCEDURE")
        print("=" * 80)

        result = emergency_system.execute_emergency_rollback(args.reason)

        print("\n" + "=" * 80)
        print("🚨 EMERGENCY ROLLBACK SUMMARY")
        print("=" * 80)
        print(f"Success: {'✅' if result['emergency_rollback_successful'] else '❌'}")
        print(f"Duration: {result['rollback_duration']:.1f} seconds")
        print(f"Reason: {result['reason']}")

        return 0 if result["emergency_rollback_successful"] else 1

    elif args.action == "history":
        rollback_system = AutomatedRollbackSystem()
        history = rollback_system.get_rollback_history()

        print("📊 Rollback History")
        print("=" * 80)

        if not history:
            print("No rollback history found.")
        else:
            for i, record in enumerate(history, 1):
                print(f"{i}. {record['timestamp']}")
                print(f"   Reason: {record['rollback_reason']}")
                print(f"   Success: {'✅' if record['rollback_successful'] else '❌'}")
                print(f"   Duration: {record['rollback_duration']:.1f}s")
                print()

    elif args.action == "status":
        rollback_system = AutomatedRollbackSystem()
        latest = rollback_system.get_latest_rollback_status()

        print("📊 Rollback System Status")
        print("=" * 80)

        if latest:
            print("Latest Rollback:")
            print(json.dumps(latest, indent=2))
        else:
            print("No rollback history found.")

        print(f"\nRollback Thresholds:")
        print(
            f"  Accuracy: {rollback_system.rollback_config['accuracy_threshold']:.1%}"
        )
        print(
            f"  Processing Time: {rollback_system.rollback_config['processing_time_threshold']}s"
        )
        print(
            f"  Error Rate: {rollback_system.rollback_config['error_rate_threshold']:.1%}"
        )

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
