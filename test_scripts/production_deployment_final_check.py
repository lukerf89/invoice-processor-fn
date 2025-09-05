"""
Final Production Deployment Readiness Check
Quick comprehensive validation to confirm all systems are production ready.
"""

import json
import time
import os
import sys
import threading
import io
from contextlib import redirect_stdout, redirect_stderr

# Add the main directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import process_creative_coop_document, detect_vendor_type


def load_test_document():
    """Load test document for validation"""
    json_file = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    try:
        with open(json_file, "r") as f:
            doc_data = json.load(f)

        # Create mock document object
        class MockDocument:
            def __init__(self, doc_data):
                self.text = doc_data.get("text", "")
                self.entities = []

                for entity_data in doc_data.get("entities", []):
                    entity = type("Entity", (), {})()
                    entity.type_ = entity_data.get("type", "")
                    entity.mention_text = entity_data.get("mentionText", "")
                    entity.confidence = entity_data.get("confidence", 0.0)
                    entity.properties = []

                    if "properties" in entity_data:
                        for prop_data in entity_data["properties"]:
                            prop = type("Property", (), {})()
                            prop.type_ = prop_data.get("type", "")
                            prop.mention_text = prop_data.get("mentionText", "")
                            prop.confidence = prop_data.get("confidence", 0.0)
                            entity.properties.append(prop)

                    self.entities.append(entity)

        return MockDocument(doc_data)

    except FileNotFoundError:
        # Create fallback mock document
        print("📄 Using fallback test document")
        fallback_text = """Creative-Coop Invoice CS003837319

Product Code | UPC         | Description                          | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
XS9826A      | 191009727774| 6"H Metal Ballerina Ornament       | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
XS9649A      | 191009725688| 8"H x 6.5"W x 4"D Paper Mache      | 24      | 0         | 0           | 24        | each | 3.50       | 2.80       | 67.20"""

        class MockDocument:
            def __init__(self, text):
                self.text = text
                self.entities = []

                entity = type("Entity", (), {})()
                entity.type_ = "line_item"
                entity.mention_text = text
                entity.confidence = 0.9
                entity.properties = []
                self.entities.append(entity)

        return MockDocument(fallback_text)


def run_core_functionality_check():
    """Test core Creative-Coop processing functionality"""
    print("🔧 Core Functionality Check")
    print("-" * 40)

    document = load_test_document()

    # Test vendor detection
    print("   Testing vendor detection...")
    try:
        vendor_type = detect_vendor_type(document.text)
        vendor_ok = vendor_type == "Creative-Coop"
        print(f"   ✅ Vendor detection: {vendor_type} {'✓' if vendor_ok else '✗'}")
    except Exception as e:
        print(f"   ❌ Vendor detection failed: {e}")
        vendor_ok = False

    # Test document processing
    print("   Testing document processing...")
    try:
        start_time = time.time()
        rows = process_creative_coop_document(document)
        processing_time = time.time() - start_time

        processing_ok = len(rows) >= 10 and processing_time < 30
        print(
            f"   ✅ Processing: {len(rows)} rows in {processing_time:.1f}s {'✓' if processing_ok else '✗'}"
        )
    except Exception as e:
        print(f"   ❌ Processing failed: {e}")
        processing_ok = False
        rows = []

    # Test output format
    print("   Testing output format...")
    try:
        if rows:
            first_row = rows[0]
            format_ok = len(first_row) == 6  # B:G columns
            print(
                f"   ✅ Output format: {len(first_row)} columns {'✓' if format_ok else '✗'}"
            )
        else:
            format_ok = False
            print("   ❌ No rows to validate format")
    except Exception as e:
        print(f"   ❌ Format validation failed: {e}")
        format_ok = False

    overall_ok = vendor_ok and processing_ok and format_ok
    status = "✅ PASS" if overall_ok else "❌ FAIL"
    print(f"   Core Functionality: {status}")

    return overall_ok


def run_performance_check():
    """Test performance requirements"""
    print("\n⚡ Performance Check")
    print("-" * 40)

    document = load_test_document()

    # Run 3 processing iterations
    processing_times = []
    row_counts = []

    for i in range(3):
        try:
            start_time = time.time()
            rows = process_creative_coop_document(document)
            end_time = time.time()

            processing_times.append(end_time - start_time)
            row_counts.append(len(rows))

        except Exception as e:
            print(f"   ❌ Iteration {i+1} failed: {e}")
            processing_times.append(999)  # Large time for failure
            row_counts.append(0)

    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        avg_rows = sum(row_counts) / len(row_counts) if row_counts else 0

        # Performance criteria
        zapier_compliant = max_time < 160  # Zapier timeout
        processing_efficient = avg_time < 30  # Reasonable processing time
        output_sufficient = avg_rows >= 10  # Meaningful output

        print(
            f"   Average time: {avg_time:.1f}s {'✓' if processing_efficient else '✗'}"
        )
        print(f"   Maximum time: {max_time:.1f}s {'✓' if zapier_compliant else '✗'}")
        print(f"   Average rows: {avg_rows:.0f} {'✓' if output_sufficient else '✗'}")

        performance_ok = zapier_compliant and processing_efficient and output_sufficient
    else:
        performance_ok = False

    status = "✅ PASS" if performance_ok else "❌ FAIL"
    print(f"   Performance: {status}")

    return performance_ok


def run_load_resilience_check():
    """Test system resilience under load"""
    print("\n🚀 Load Resilience Check")
    print("-" * 40)

    # Test concurrent processing (reduced for stability)
    concurrent_requests = 3
    results = []

    def process_worker(worker_id):
        """Worker function for concurrent processing"""
        try:
            document = load_test_document()
            start_time = time.time()
            rows = process_creative_coop_document(document)
            end_time = time.time()

            results.append(
                {
                    "worker_id": worker_id,
                    "success": True,
                    "processing_time": end_time - start_time,
                    "rows": len(rows),
                }
            )
        except Exception as e:
            results.append({"worker_id": worker_id, "success": False, "error": str(e)})

    # Execute concurrent workers
    threads = []
    start_time = time.time()

    for i in range(concurrent_requests):
        thread = threading.Thread(target=process_worker, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join(timeout=60)

    total_time = time.time() - start_time

    # Analyze results
    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]

    success_rate = (
        len(successful) / concurrent_requests if concurrent_requests > 0 else 0
    )

    print(f"   Concurrent requests: {concurrent_requests}")
    print(
        f"   Success rate: {success_rate:.1%} ({len(successful)}/{concurrent_requests})"
    )
    print(f"   Total time: {total_time:.1f}s")

    if successful:
        avg_processing_time = sum(r["processing_time"] for r in successful) / len(
            successful
        )
        total_rows = sum(r["rows"] for r in successful)
        print(f"   Avg processing time: {avg_processing_time:.1f}s")
        print(f"   Total rows extracted: {total_rows}")

    # Load resilience criteria
    resilience_ok = success_rate >= 1.0 and len(failed) == 0

    status = "✅ PASS" if resilience_ok else "❌ FAIL"
    print(f"   Load Resilience: {status}")

    if failed:
        print("   Failures:")
        for failure in failed[:3]:
            print(
                f"     - Worker {failure['worker_id']}: {failure.get('error', 'Unknown')}"
            )

    return resilience_ok


def run_error_handling_check():
    """Test error handling capabilities"""
    print("\n🛡️ Error Handling Check")
    print("-" * 40)

    error_scenarios = [
        {
            "name": "Corrupted document",
            "document_text": "CORRUPTED_DATA_\x00\x01\x02INVALID",
        },
        {
            "name": "Large document",
            "document_text": "XS9826A Product " + "Large content " * 500,
        },
        {
            "name": "Malicious content",
            "document_text": "XS9826A <script>alert('xss')</script> Product",
        },
    ]

    error_handling_results = []

    for scenario in error_scenarios:
        print(f"   Testing: {scenario['name']}")

        # Create test document
        class TestDocument:
            def __init__(self, text):
                self.text = text
                self.entities = []

                entity = type("Entity", (), {})()
                entity.type_ = "line_item"
                entity.mention_text = text
                entity.confidence = 0.9
                entity.properties = []
                self.entities.append(entity)

        document = TestDocument(scenario["document_text"])

        try:
            start_time = time.time()
            rows = process_creative_coop_document(document)
            processing_time = time.time() - start_time

            # Should handle gracefully - complete in reasonable time and not crash
            handled_gracefully = processing_time < 30 and len(rows) >= 0

            error_handling_results.append(
                {
                    "scenario": scenario["name"],
                    "success": handled_gracefully,
                    "processing_time": processing_time,
                    "rows": len(rows),
                }
            )

            status = "✅" if handled_gracefully else "❌"
            print(f"     Result: {status} ({processing_time:.1f}s, {len(rows)} rows)")

        except Exception as e:
            # Some exceptions are acceptable if handled gracefully
            handled_gracefully = (
                "timeout" in str(e).lower() or "memory" in str(e).lower()
            )

            error_handling_results.append(
                {
                    "scenario": scenario["name"],
                    "success": handled_gracefully,
                    "error": str(e)[:50],
                }
            )

            status = "✅" if handled_gracefully else "❌"
            print(f"     Result: {status} (Exception: {str(e)[:50]})")

    # Overall error handling assessment
    successful_handling = sum(1 for r in error_handling_results if r["success"])
    total_scenarios = len(error_scenarios)

    error_handling_ok = successful_handling == total_scenarios

    status = "✅ PASS" if error_handling_ok else "❌ FAIL"
    print(f"   Error Handling: {status} ({successful_handling}/{total_scenarios})")

    return error_handling_ok


def run_production_deployment_final_check():
    """Run final comprehensive production deployment check"""

    print("🎯 Production Deployment Final Check")
    print("=" * 50)

    start_time = time.time()

    # Run all validation checks
    validation_checks = {
        "core_functionality": run_core_functionality_check,
        "performance": run_performance_check,
        "load_resilience": run_load_resilience_check,
        "error_handling": run_error_handling_check,
    }

    check_results = {}

    for check_name, check_function in validation_checks.items():
        try:
            result = check_function()
            check_results[check_name] = result
        except Exception as e:
            print(f"\n❌ {check_name.replace('_', ' ').title()} failed: {e}")
            check_results[check_name] = False

    # Calculate overall success
    successful_checks = sum(1 for result in check_results.values() if result)
    total_checks = len(check_results)
    success_rate = successful_checks / total_checks

    total_time = time.time() - start_time

    print(f"\n{'='*50}")
    print("Final Production Readiness Summary")
    print(f"{'='*50}")
    print(f"Successful checks: {successful_checks}/{total_checks} ({success_rate:.1%})")
    print(f"Total validation time: {total_time:.1f} seconds")

    # Individual check status
    for check_name, passed in check_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name.replace('_', ' ').title()}: {status}")

    if success_rate == 1.0:
        print(f"\n🎉 PRODUCTION READY!")
        print("✅ All validation checks passed")
        print("✅ Creative-Coop Phase 02 system is ready for deployment")
        print("\n🚀 DEPLOY TO PRODUCTION")
        return True
    else:
        print(f"\n⚠️  NOT READY FOR PRODUCTION")
        failed_checks = [name for name, result in check_results.items() if not result]
        print(f"❌ Failed checks: {', '.join(failed_checks)}")
        print("\n🔧 Fix failing checks before deployment")
        return False


if __name__ == "__main__":
    ready = run_production_deployment_final_check()
    exit(0 if ready else 1)
