#!/usr/bin/env python3
"""
Continuous Integration validation for Creative-Coop processing
Automated testing pipeline with comprehensive monitoring
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("creative_coop_ci.log"),
        logging.StreamHandler(),
    ],
)


@dataclass
class ValidationMetrics:
    """Comprehensive metrics for Creative-Coop processing validation"""

    test_name: str
    timestamp: float
    processing_time: float
    total_products: int
    unique_products: int
    unique_prices: int
    unique_quantities: int
    placeholder_count: int
    invoice_extraction_success: bool
    accuracy_score: float
    performance_score: float
    quality_score: float
    overall_score: float
    errors: List[str]
    warnings: List[str]

    def to_dict(self):
        return asdict(self)


class CreativeCooProcessingValidator:
    """Comprehensive validation framework for Creative-Coop processing"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.baseline_metrics = self.load_baseline_metrics()

    def load_baseline_metrics(self) -> Dict:
        """Load baseline metrics for comparison"""
        baseline_file = Path("test_scripts/creative_coop_baseline_metrics.json")
        if baseline_file.exists():
            with open(baseline_file, "r") as f:
                return json.load(f)
        else:
            return {
                "min_products": 100,
                "min_accuracy": 0.85,
                "max_processing_time": 120,
                "max_placeholders": 0,
                "min_price_variance": 0.8,
                "min_quantity_variance": 0.5,
            }

    def validate_complete_processing(self) -> ValidationMetrics:
        """Run complete Creative-Coop processing validation"""
        self.logger.info("🚀 Starting complete Creative-Coop processing validation")

        start_time = time.time()
        errors = []
        warnings = []

        try:
            # Load test data
            results = self.process_test_invoice()
            processing_time = time.time() - start_time

            # Calculate comprehensive metrics
            metrics = self.calculate_comprehensive_metrics(
                results, processing_time, errors, warnings
            )

            # Validate against baselines
            self.validate_against_baselines(metrics)

            # Log results
            self.log_validation_results(metrics)

            return metrics

        except Exception as e:
            self.logger.error(f"❌ Validation failed with error: {str(e)}")
            errors.append(f"Processing error: {str(e)}")

            return ValidationMetrics(
                test_name="creative_coop_complete_validation",
                timestamp=time.time(),
                processing_time=time.time() - start_time,
                total_products=0,
                unique_products=0,
                unique_prices=0,
                unique_quantities=0,
                placeholder_count=999,
                invoice_extraction_success=False,
                accuracy_score=0.0,
                performance_score=0.0,
                quality_score=0.0,
                overall_score=0.0,
                errors=errors,
                warnings=warnings,
            )

    def process_test_invoice(self) -> List:
        """Process CS003837319_Error test invoice"""
        import sys
        from unittest.mock import Mock

        sys.path.insert(0, ".")
        from main import process_creative_coop_document

        with open("test_invoices/CS003837319_Error_docai_output.json", "r") as f:
            doc_data = json.load(f)

        mock_document = Mock()
        mock_document.text = doc_data.get("text", "")
        mock_document.entities = []

        for entity_data in doc_data.get("entities", []):
            entity = Mock()
            entity.type_ = entity_data.get("type")
            entity.mention_text = entity_data.get("mentionText", "")
            mock_document.entities.append(entity)

        return process_creative_coop_document(mock_document)

    def calculate_comprehensive_metrics(
        self, results: List, processing_time: float, errors: List, warnings: List
    ) -> ValidationMetrics:
        """Calculate comprehensive validation metrics"""

        # Basic counts
        total_products = len(results)

        # Extract product codes from descriptions
        product_codes = set()
        for row in results:
            if len(row) > 3:
                import re

                match = re.search(r"\b([A-Z]{2,3}\d{4}[A-Z]?)\b", str(row[3]))
                if match:
                    product_codes.add(match.group(1))

        unique_products = len(product_codes)
        unique_prices = len(set(row[4] for row in results if len(row) > 4 and row[4]))
        unique_quantities = len(
            set(row[5] for row in results if len(row) > 5 and row[5])
        )

        # Placeholder detection
        placeholder_count = self.count_placeholders(results)

        # Invoice extraction validation
        invoice_extraction_success = any(
            "CS003837319" in str(row[2]) for row in results if len(row) > 2
        )

        # Calculate scores
        accuracy_score = self.calculate_accuracy_score(results)
        performance_score = self.calculate_performance_score(processing_time)
        quality_score = self.calculate_quality_score(results, placeholder_count)

        # Overall score (weighted average)
        overall_score = (
            accuracy_score * 0.4 + performance_score * 0.3 + quality_score * 0.3
        )

        return ValidationMetrics(
            test_name="creative_coop_complete_validation",
            timestamp=time.time(),
            processing_time=processing_time,
            total_products=total_products,
            unique_products=unique_products,
            unique_prices=unique_prices,
            unique_quantities=unique_quantities,
            placeholder_count=placeholder_count,
            invoice_extraction_success=invoice_extraction_success,
            accuracy_score=accuracy_score,
            performance_score=performance_score,
            quality_score=quality_score,
            overall_score=overall_score,
            errors=errors,
            warnings=warnings,
        )

    def count_placeholders(self, results: List) -> int:
        """Count placeholder entries in results"""
        placeholder_count = 0
        for row in results:
            if len(row) >= 6:
                description = str(row[3])
                price = row[4]
                quantity = row[5]

                if (
                    "Traditional D-code format" in description
                    or (price == "$1.60" and quantity == "24")
                    or "placeholder" in description.lower()
                ):
                    placeholder_count += 1

        return placeholder_count

    def calculate_accuracy_score(self, results: List) -> float:
        """Calculate accuracy score based on expected results"""

        if not results:
            return 0.0

        # Comprehensive accuracy indicators based on our Phase 01 implementation
        has_sufficient_products = len(results) >= 100
        has_price_variety = len(set(row[4] for row in results if len(row) > 4)) >= 20
        has_quantity_variety = len(set(row[5] for row in results if len(row) > 5)) >= 8
        has_complete_descriptions = all(
            len(str(row[3])) > 10 for row in results if len(row) > 3
        )
        has_valid_invoice_numbers = all(
            "CS003837319" in str(row[2]) for row in results if len(row) > 2
        )

        accuracy_factors = [
            has_sufficient_products,
            has_price_variety,
            has_quantity_variety,
            has_complete_descriptions,
            has_valid_invoice_numbers,
        ]

        score = sum(accuracy_factors) / len(accuracy_factors)
        return min(1.0, score)

    def calculate_performance_score(self, processing_time: float) -> float:
        """Calculate performance score based on processing time"""
        max_time = self.baseline_metrics["max_processing_time"]

        if processing_time <= max_time * 0.5:
            return 1.0  # Excellent performance
        elif processing_time <= max_time:
            return 0.8  # Good performance
        elif processing_time <= max_time * 1.5:
            return 0.5  # Acceptable performance
        else:
            return 0.0  # Poor performance

    def calculate_quality_score(self, results: List, placeholder_count: int) -> float:
        """Calculate data quality score"""
        if not results:
            return 0.0

        # Quality factors
        no_placeholders = placeholder_count == 0
        price_variance = len(set(row[4] for row in results if len(row) > 4)) / len(
            results
        )
        quantity_variance = len(set(row[5] for row in results if len(row) > 5)) / len(
            results
        )

        quality_factors = [
            no_placeholders,
            price_variance > 0.15,
            quantity_variance > 0.08,
        ]

        return sum(quality_factors) / len(quality_factors)

    def validate_against_baselines(self, metrics: ValidationMetrics):
        """Validate metrics against baseline requirements"""
        baseline = self.baseline_metrics

        validations = [
            (
                metrics.unique_products >= baseline["min_products"],
                f"Product count: {metrics.unique_products} >= {baseline['min_products']}",
            ),
            (
                metrics.processing_time <= baseline["max_processing_time"],
                f"Processing time: {metrics.processing_time:.2f}s <= {baseline['max_processing_time']}s",
            ),
            (
                metrics.placeholder_count <= baseline["max_placeholders"],
                f"Placeholders: {metrics.placeholder_count} <= {baseline['max_placeholders']}",
            ),
            (
                metrics.overall_score >= baseline["min_accuracy"],
                f"Overall score: {metrics.overall_score:.2f} >= {baseline['min_accuracy']}",
            ),
        ]

        for validation, description in validations:
            if validation:
                self.logger.info(f"✅ {description}")
            else:
                self.logger.warning(f"⚠️ {description}")
                metrics.warnings.append(description)

    def log_validation_results(self, metrics: ValidationMetrics):
        """Log comprehensive validation results"""
        self.logger.info("📊 VALIDATION RESULTS SUMMARY")
        self.logger.info(f"   Overall Score: {metrics.overall_score:.2f}")
        self.logger.info(f"   Accuracy: {metrics.accuracy_score:.2f}")
        self.logger.info(f"   Performance: {metrics.performance_score:.2f}")
        self.logger.info(f"   Quality: {metrics.quality_score:.2f}")
        self.logger.info(f"   Products: {metrics.unique_products}")
        self.logger.info(f"   Processing Time: {metrics.processing_time:.2f}s")
        self.logger.info(f"   Placeholders: {metrics.placeholder_count}")

        if metrics.errors:
            self.logger.error(f"❌ Errors: {len(metrics.errors)}")
            for error in metrics.errors:
                self.logger.error(f"   {error}")

        if metrics.warnings:
            self.logger.warning(f"⚠️ Warnings: {len(metrics.warnings)}")
            for warning in metrics.warnings:
                self.logger.warning(f"   {warning}")

    def run_regression_testing(self) -> Dict[str, bool]:
        """Run regression tests for Phase 01 functionality"""
        regression_results = {}

        try:
            # Test 1: Invoice number extraction consistency
            results = self.process_test_invoice()
            invoice_extraction = any(
                "CS003837319" in str(row[2]) for row in results if len(row) > 2
            )
            regression_results["invoice_extraction"] = invoice_extraction

            # Test 2: Product processing scope
            product_codes = set()
            for row in results:
                if len(row) > 3:
                    import re

                    match = re.search(r"\b([A-Z]{2,3}\d{4}[A-Z]?)\b", str(row[3]))
                    if match:
                        product_codes.add(match.group(1))

            regression_results["product_scope"] = len(product_codes) >= 100

            # Test 3: Placeholder elimination
            placeholder_count = self.count_placeholders(results)
            regression_results["placeholder_elimination"] = placeholder_count == 0

            # Test 4: Data quality maintenance
            unique_prices = len(set(row[4] for row in results if len(row) > 4))
            unique_quantities = len(set(row[5] for row in results if len(row) > 5))
            regression_results["data_quality"] = (
                unique_prices >= 20 and unique_quantities >= 8
            )

        except Exception as e:
            self.logger.error(f"Regression testing failed: {str(e)}")
            for key in [
                "invoice_extraction",
                "product_scope",
                "placeholder_elimination",
                "data_quality",
            ]:
                regression_results[key] = False

        return regression_results

    def generate_trend_analysis(self) -> Dict:
        """Generate trend analysis from historical validation data"""
        results_file = Path("test_scripts/creative_coop_validation_history.json")

        if not results_file.exists():
            return {"status": "No historical data available"}

        with open(results_file, "r") as f:
            history = json.load(f)

        if len(history) < 2:
            return {"status": "Insufficient data for trend analysis"}

        # Analyze trends in key metrics
        recent_runs = history[-10:]  # Last 10 runs
        trends = {
            "overall_score": [run["overall_score"] for run in recent_runs],
            "processing_time": [run["processing_time"] for run in recent_runs],
            "unique_products": [run["unique_products"] for run in recent_runs],
            "placeholder_count": [run["placeholder_count"] for run in recent_runs],
        }

        # Calculate trend direction
        trend_analysis = {}
        for metric, values in trends.items():
            if len(values) >= 2:
                trend_direction = "improving" if values[-1] > values[0] else "declining"
                avg_value = sum(values) / len(values)
                trend_analysis[metric] = {
                    "direction": trend_direction,
                    "average": avg_value,
                    "latest": values[-1],
                    "change": values[-1] - values[0],
                }

        return trend_analysis


def main():
    """Run comprehensive Creative-Coop validation"""
    validator = CreativeCooProcessingValidator()

    print("🚀 Creative-Coop CI/CD Validation Pipeline")
    print("=" * 50)

    # Step 1: Core validation
    print("\n📋 Step 1: Core Processing Validation")
    metrics = validator.validate_complete_processing()

    # Step 2: Regression testing
    print("\n📋 Step 2: Regression Testing")
    regression_results = validator.run_regression_testing()

    regression_passed = all(regression_results.values())
    print(f"Regression Status: {'✅ PASSED' if regression_passed else '❌ FAILED'}")

    for test, passed in regression_results.items():
        status = "✅" if passed else "❌"
        print(f"   {test}: {status}")

    # Step 3: Trend analysis
    print("\n📋 Step 3: Trend Analysis")
    trends = validator.generate_trend_analysis()

    if "status" in trends:
        print(f"   {trends['status']}")
    else:
        print("   Recent Performance Trends:")
        for metric, data in trends.items():
            direction_icon = "📈" if data["direction"] == "improving" else "📉"
            print(
                f"   {metric}: {direction_icon} {data['direction']} (avg: {data['average']:.2f})"
            )

    # Step 4: Save results for historical tracking
    results_file = Path("test_scripts/creative_coop_validation_history.json")

    if results_file.exists():
        with open(results_file, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(metrics.to_dict())

    # Keep only last 50 results
    history = history[-50:]

    with open(results_file, "w") as f:
        json.dump(history, f, indent=2)

    # Step 5: Final assessment
    print("\n🏆 FINAL CI/CD ASSESSMENT")
    success_criteria = [
        metrics.overall_score >= 0.85,
        regression_passed,
        len(metrics.errors) == 0,
        metrics.processing_time < 120,
    ]

    overall_success = all(success_criteria)

    if overall_success:
        print("   ✅ ALL SYSTEMS GO - Ready for deployment")
        print("   Phase 01 Creative-Coop processing exceeds all targets")
        return 0
    else:
        print("   ❌ DEPLOYMENT BLOCKED - Issues require attention")
        if metrics.overall_score < 0.85:
            print(f"   • Overall score: {metrics.overall_score:.2f} (target: 0.85)")
        if not regression_passed:
            print("   • Regression tests failing")
        if len(metrics.errors) > 0:
            print(f"   • {len(metrics.errors)} critical errors")
        if metrics.processing_time >= 120:
            print(f"   • Processing too slow: {metrics.processing_time:.2f}s")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
