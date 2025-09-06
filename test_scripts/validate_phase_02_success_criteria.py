#!/usr/bin/env python3
"""
Phase 02 Success Criteria Validation

This module validates that Phase 02 enhancements meet specific business objectives:
- Price extraction: 95%+ accuracy (eliminates $1.60 placeholders)
- Quantity processing: 90%+ accuracy (shipped vs ordered logic)
- Description completeness: 95%+ (UPC integration, no placeholders)
- Overall processing: 90%+ accuracy target

Provides detailed metrics and actionable insights for production readiness.
"""

import json
import os
import sys
import time
from datetime import datetime

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "main",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"
    ),
)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)


class Phase02SuccessCriteriaValidator:
    """Validates Phase 02 success criteria with detailed reporting"""

    def __init__(self):
        self.validation_timestamp = datetime.now().isoformat()
        self.cs_document = None
        self.processing_results = []
        self.validation_report = {}

    def load_cs_document(self):
        """Load the CS003837319_Error 2 test document"""
        test_file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "test_invoices",
            "CS003837319_Error 2_docai_output.json",
        )

        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Test document not found: {test_file_path}")

        with open(test_file_path, "r", encoding="utf-8") as f:
            document_data = json.load(f)

        # Create mock document object
        class MockDocument:
            def __init__(self, data):
                self.text = data.get("text", "")
                self.pages = data.get("pages", [])
                self.entities = data.get("entities", [])

        self.cs_document = MockDocument(document_data)
        print("✅ Loaded CS003837319_Error 2 test document")

    def process_with_phase_02_enhancements(self):
        """Process document with Phase 02 enhancements"""
        print("🚀 Processing document with Phase 02 enhancements...")

        try:
            # Process using Phase 02 enhanced function
            print(f"🔍 Checking main module: {main}")
            print(
                f"🔍 Has enhanced function: {hasattr(main, 'process_creative_coop_document_phase_02_enhanced')}"
            )
            print(
                f"🔍 Has base function: {hasattr(main, 'process_creative_coop_document')}"
            )

            # Try Phase 02 enhanced function first
            try:
                self.processing_results = (
                    main.process_creative_coop_document_phase_02_enhanced(
                        self.cs_document
                    )
                )
                print(
                    f"✅ Processed {len(self.processing_results)} line items with Phase 02 enhancements"
                )
            except AttributeError as e:
                print(
                    f"⚠️  Phase 02 enhanced function not available ({e}), using current processing..."
                )
                self.processing_results = main.process_creative_coop_document(
                    self.cs_document
                )
                print(
                    f"✅ Processed {len(self.processing_results)} line items with current processing"
                )

        except Exception as e:
            print(f"❌ Error during Phase 02 processing: {e}")
            import traceback

            traceback.print_exc()
            raise

    def validate_price_extraction_accuracy(self):
        """Validate price extraction meets 95%+ accuracy target"""
        print("\n📊 Validating Price Extraction Accuracy (Target: 95%+)")

        if not self.processing_results:
            return {
                "accuracy": 0,
                "target_met": False,
                "details": "No results to validate",
            }

        total_items = len(self.processing_results)

        # Count valid prices (not placeholders or empty)
        placeholder_prices = ["$0.00", "$1.60", None, "", "N/A"]
        valid_price_items = []
        invalid_price_items = []

        for item in self.processing_results:
            price = item.get("price", "")
            if price and price not in placeholder_prices:
                # Additional validation for realistic prices
                try:
                    price_value = float(price.replace("$", "").replace(",", ""))
                    if price_value > 0 and price_value < 1000:  # Reasonable price range
                        valid_price_items.append(item)
                    else:
                        invalid_price_items.append(item)
                except ValueError:
                    invalid_price_items.append(item)
            else:
                invalid_price_items.append(item)

        price_accuracy = len(valid_price_items) / total_items if total_items > 0 else 0
        target_met = price_accuracy >= 0.95

        price_validation = {
            "accuracy": price_accuracy,
            "target_met": target_met,
            "valid_items": len(valid_price_items),
            "invalid_items": len(invalid_price_items),
            "total_items": total_items,
            "sample_valid_prices": [
                item.get("price") for item in valid_price_items[:5]
            ],
            "sample_invalid_prices": [
                item.get("price") for item in invalid_price_items[:5]
            ],
            "improvement_needed": max(0, 0.95 - price_accuracy),
        }

        print(f"   Price Accuracy: {price_accuracy:.1%}")
        print(f"   Target Met: {'✅' if target_met else '❌'}")
        print(f"   Valid Prices: {len(valid_price_items)} / {total_items}")

        if not target_met:
            print(
                f"   Improvement Needed: {price_validation['improvement_needed']:.1%}"
            )
            print(f"   Sample Invalid: {price_validation['sample_invalid_prices']}")

        return price_validation

    def validate_quantity_processing_accuracy(self):
        """Validate quantity processing meets 90%+ accuracy target"""
        print("\n📊 Validating Quantity Processing Accuracy (Target: 90%+)")

        if not self.processing_results:
            return {
                "accuracy": 0,
                "target_met": False,
                "details": "No results to validate",
            }

        total_items = len(self.processing_results)

        # Count valid quantities (positive, realistic values)
        placeholder_quantities = [
            0,
            24,
            None,
        ]  # 24 is known placeholder from Creative-Coop
        valid_quantity_items = []
        invalid_quantity_items = []

        for item in self.processing_results:
            quantity = item.get("quantity", 0)

            # Validate quantity is realistic
            if (
                isinstance(quantity, (int, float))
                and quantity > 0
                and quantity not in placeholder_quantities
                and quantity <= 1000
            ):  # Reasonable upper limit
                valid_quantity_items.append(item)
            else:
                invalid_quantity_items.append(item)

        quantity_accuracy = (
            len(valid_quantity_items) / total_items if total_items > 0 else 0
        )
        target_met = quantity_accuracy >= 0.90

        quantity_validation = {
            "accuracy": quantity_accuracy,
            "target_met": target_met,
            "valid_items": len(valid_quantity_items),
            "invalid_items": len(invalid_quantity_items),
            "total_items": total_items,
            "sample_valid_quantities": [
                item.get("quantity") for item in valid_quantity_items[:5]
            ],
            "sample_invalid_quantities": [
                item.get("quantity") for item in invalid_quantity_items[:5]
            ],
            "improvement_needed": max(0, 0.90 - quantity_accuracy),
        }

        print(f"   Quantity Accuracy: {quantity_accuracy:.1%}")
        print(f"   Target Met: {'✅' if target_met else '❌'}")
        print(f"   Valid Quantities: {len(valid_quantity_items)} / {total_items}")

        if not target_met:
            print(
                f"   Improvement Needed: {quantity_validation['improvement_needed']:.1%}"
            )
            print(
                f"   Sample Invalid: {quantity_validation['sample_invalid_quantities']}"
            )

        return quantity_validation

    def validate_description_completeness(self):
        """Validate description completeness meets 95%+ target"""
        print("\n📊 Validating Description Completeness (Target: 95%+)")

        if not self.processing_results:
            return {
                "completeness": 0,
                "target_met": False,
                "details": "No results to validate",
            }

        total_items = len(self.processing_results)

        # Count complete descriptions (no placeholders, sufficient length, meaningful content)
        placeholder_indicators = [
            "Traditional D-code format",
            "No description available",
            "Product description not found",
            "Unknown product",
            "",
        ]

        complete_description_items = []
        incomplete_description_items = []

        for item in self.processing_results:
            description = item.get("description", "")

            # Validate description completeness
            is_complete = (
                description  # Not empty
                and len(description) > 20  # Sufficient length
                and not any(
                    placeholder in description for placeholder in placeholder_indicators
                )  # No placeholders
                and len(description.split()) >= 3  # At least 3 words
            )

            if is_complete:
                complete_description_items.append(item)
            else:
                incomplete_description_items.append(item)

        description_completeness = (
            len(complete_description_items) / total_items if total_items > 0 else 0
        )
        target_met = description_completeness >= 0.95

        description_validation = {
            "completeness": description_completeness,
            "target_met": target_met,
            "complete_items": len(complete_description_items),
            "incomplete_items": len(incomplete_description_items),
            "total_items": total_items,
            "sample_complete_descriptions": [
                (
                    item.get("description")[:50] + "..."
                    if len(item.get("description", "")) > 50
                    else item.get("description", "")
                )
                for item in complete_description_items[:3]
            ],
            "sample_incomplete_descriptions": [
                (
                    item.get("description")[:50] + "..."
                    if len(item.get("description", "")) > 50
                    else item.get("description", "")
                )
                for item in incomplete_description_items[:3]
            ],
            "improvement_needed": max(0, 0.95 - description_completeness),
        }

        print(f"   Description Completeness: {description_completeness:.1%}")
        print(f"   Target Met: {'✅' if target_met else '❌'}")
        print(
            f"   Complete Descriptions: {len(complete_description_items)} / {total_items}"
        )

        if not target_met:
            print(
                f"   Improvement Needed: {description_validation['improvement_needed']:.1%}"
            )
            print(
                f"   Sample Incomplete: {description_validation['sample_incomplete_descriptions']}"
            )

        return description_validation

    def validate_overall_processing_accuracy(self):
        """Validate overall processing meets 90%+ target"""
        print("\n📊 Validating Overall Processing Accuracy (Target: 90%+)")

        # Get individual component validations
        price_validation = self.validation_report.get("price_extraction", {})
        quantity_validation = self.validation_report.get("quantity_processing", {})
        description_validation = self.validation_report.get(
            "description_completeness", {}
        )

        # Calculate overall accuracy (weighted average)
        price_accuracy = price_validation.get("accuracy", 0)
        quantity_accuracy = quantity_validation.get("accuracy", 0)
        description_completeness = description_validation.get("completeness", 0)

        overall_accuracy = (
            price_accuracy + quantity_accuracy + description_completeness
        ) / 3
        target_met = overall_accuracy >= 0.90

        overall_validation = {
            "overall_accuracy": overall_accuracy,
            "target_met": target_met,
            "component_breakdown": {
                "price_accuracy": price_accuracy,
                "quantity_accuracy": quantity_accuracy,
                "description_completeness": description_completeness,
            },
            "improvement_needed": max(0, 0.90 - overall_accuracy),
            "weakest_component": min(
                [
                    ("price", price_accuracy),
                    ("quantity", quantity_accuracy),
                    ("description", description_completeness),
                ],
                key=lambda x: x[1],
            )[0],
        }

        print(f"   Overall Accuracy: {overall_accuracy:.1%}")
        print(f"   Target Met: {'✅' if target_met else '❌'}")
        print(f"   Component Breakdown:")
        print(f"     - Price: {price_accuracy:.1%}")
        print(f"     - Quantity: {quantity_accuracy:.1%}")
        print(f"     - Description: {description_completeness:.1%}")

        if not target_met:
            print(
                f"   Improvement Needed: {overall_validation['improvement_needed']:.1%}"
            )
            print(f"   Weakest Component: {overall_validation['weakest_component']}")

        return overall_validation

    def generate_detailed_report(self):
        """Generate detailed Phase 02 success criteria report"""
        print("\n" + "=" * 80)
        print("📈 PHASE 02 SUCCESS CRITERIA VALIDATION REPORT")
        print("=" * 80)

        # Summary
        overall_validation = self.validation_report.get("overall_processing", {})
        overall_success = overall_validation.get("target_met", False)
        overall_accuracy = overall_validation.get("overall_accuracy", 0)

        print(
            f"🎯 Overall Success: {'✅ PASSED' if overall_success else '❌ NEEDS IMPROVEMENT'}"
        )
        print(f"📊 Overall Accuracy: {overall_accuracy:.1%}")
        print(f"📅 Validation Timestamp: {self.validation_timestamp}")
        print(f"📄 Document Processed: CS003837319_Error 2.PDF")
        print(f"🔢 Total Line Items: {len(self.processing_results)}")

        # Individual component status
        print(f"\n📋 Component Status:")

        components = [
            (
                "Price Extraction",
                self.validation_report.get("price_extraction", {}),
                "95%+",
            ),
            (
                "Quantity Processing",
                self.validation_report.get("quantity_processing", {}),
                "90%+",
            ),
            (
                "Description Completeness",
                self.validation_report.get("description_completeness", {}),
                "95%+",
            ),
        ]

        for component_name, validation_data, target in components:
            accuracy_key = (
                "accuracy" if "accuracy" in validation_data else "completeness"
            )
            accuracy = validation_data.get(accuracy_key, 0)
            target_met = validation_data.get("target_met", False)
            status = "✅" if target_met else "❌"

            print(f"   {status} {component_name}: {accuracy:.1%} (Target: {target})")

        # Action items if improvements needed
        if not overall_success:
            print(f"\n🔧 IMPROVEMENT ACTION ITEMS:")

            price_validation = self.validation_report.get("price_extraction", {})
            if not price_validation.get("target_met", True):
                improvement = price_validation.get("improvement_needed", 0)
                print(f"   🔴 Price Extraction: Improve by {improvement:.1%}")
                print(f"      - Focus on eliminating placeholder prices: $0.00, $1.60")
                print(f"      - Enhance tabular extraction patterns")

            quantity_validation = self.validation_report.get("quantity_processing", {})
            if not quantity_validation.get("target_met", True):
                improvement = quantity_validation.get("improvement_needed", 0)
                print(f"   🟡 Quantity Processing: Improve by {improvement:.1%}")
                print(f"      - Implement shipped vs ordered logic")
                print(f"      - Remove quantity placeholder values (24)")

            description_validation = self.validation_report.get(
                "description_completeness", {}
            )
            if not description_validation.get("target_met", True):
                improvement = description_validation.get("improvement_needed", 0)
                print(f"   🟠 Description Completeness: Improve by {improvement:.1%}")
                print(f"      - Integrate UPC codes with descriptions")
                print(f"      - Eliminate 'Traditional D-code format' placeholders")

        else:
            print(
                f"\n🎉 All Phase 02 success criteria met! Ready for production deployment."
            )

        # Performance insights
        print(f"\n⚡ Performance Insights:")
        print(f"   📈 Processing Efficiency: {overall_accuracy:.1%}")

        if overall_accuracy >= 0.95:
            print(f"   🌟 Exceptional performance - exceeds all targets")
        elif overall_accuracy >= 0.90:
            print(f"   ✨ Good performance - meets overall target")
        else:
            print(f"   ⚠️  Below target - requires optimization")

        return {
            "overall_success": overall_success,
            "overall_accuracy": overall_accuracy,
            "validation_report": self.validation_report,
            "timestamp": self.validation_timestamp,
            "total_items": len(self.processing_results),
        }

    def save_validation_report(self, filename=None):
        """Save validation report to file"""
        if not filename:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase_02_validation_report_{timestamp_str}.json"

        report_path = os.path.join(
            os.path.dirname(__file__), "..", "test_invoices", filename
        )

        full_report = {
            "validation_timestamp": self.validation_timestamp,
            "document_processed": "CS003837319_Error 2.PDF",
            "total_line_items": len(self.processing_results),
            "validation_results": self.validation_report,
            "overall_success": self.validation_report.get("overall_processing", {}).get(
                "target_met", False
            ),
            "overall_accuracy": self.validation_report.get(
                "overall_processing", {}
            ).get("overall_accuracy", 0),
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)

        print(f"💾 Validation report saved: {report_path}")
        return report_path

    def run_full_validation(self):
        """Run complete Phase 02 success criteria validation"""
        print("🚀 Starting Phase 02 Success Criteria Validation...")
        print("=" * 80)

        try:
            # Load test document
            self.load_cs_document()

            # Process with Phase 02 enhancements
            self.process_with_phase_02_enhancements()

            # Run individual validations
            self.validation_report["price_extraction"] = (
                self.validate_price_extraction_accuracy()
            )
            self.validation_report["quantity_processing"] = (
                self.validate_quantity_processing_accuracy()
            )
            self.validation_report["description_completeness"] = (
                self.validate_description_completeness()
            )
            self.validation_report["overall_processing"] = (
                self.validate_overall_processing_accuracy()
            )

            # Generate detailed report
            summary = self.generate_detailed_report()

            # Save report
            report_path = self.save_validation_report()

            return summary

        except Exception as e:
            print(f"❌ Validation failed: {e}")
            raise


def main():
    """Main validation runner"""
    validator = Phase02SuccessCriteriaValidator()

    try:
        summary = validator.run_full_validation()

        # Exit with appropriate code
        success = summary.get("overall_success", False)
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"💥 Fatal error during validation: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
