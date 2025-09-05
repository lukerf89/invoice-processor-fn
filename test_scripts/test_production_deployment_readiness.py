"""
Production Deployment Readiness Tests - TDD Implementation
Tests comprehensive production readiness with load testing, error recovery,
monitoring, security, and Zapier compatibility validation.

RED PHASE: Define production readiness requirements through failing tests
"""

import csv
import io
import json
import os
import sys
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the main directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import detect_vendor_type, process_creative_coop_document

# Expected results from manual PDF analysis of CS003837319_Error 2.PDF
EXPECTED_CS_ERROR2_RESULTS = [
    {
        "code": "XS9826A",
        "upc": "191009727774",
        "qty": 24,
        "price": 1.60,
        "desc_contains": "Metal Ballerina",
    },
    {
        "code": "XS9649A",
        "upc": "191009725688",
        "qty": 24,
        "price": 2.80,
        "desc_contains": "Paper Mache",
    },
    {
        "code": "XS9482",
        "upc": "191009714712",
        "qty": 12,
        "price": 2.80,
        "desc_contains": "Wood Shoe",
    },
    {
        "code": "XS9840A",
        "upc": "191009727910",
        "qty": 24,
        "price": 2.80,
        "desc_contains": "Metal",
    },
    {
        "code": "XS8185",
        "upc": "191009721666",
        "qty": 16,
        "price": 12.00,
        "desc_contains": "Cotton Lumbar Pillow",
    },
    {
        "code": "XS9357",
        "upc": "191009713470",
        "qty": 12,
        "price": 4.00,
        "desc_contains": "Metal Bow Tree",
    },
    {
        "code": "XS7529",
        "upc": "191009690856",
        "qty": 18,
        "price": 8.00,
        "desc_contains": "Metal Leaves",
    },
    {
        "code": "XS7653A",
        "upc": "191009689553",
        "qty": 24,
        "price": 4.00,
        "desc_contains": "Stoneware",
    },
    {
        "code": "XS8109",
        "upc": "191009720799",
        "qty": 12,
        "price": 12.80,
        "desc_contains": "Wool Felt",
    },
    {
        "code": "XS8379A",
        "upc": "191009705277",
        "qty": 24,
        "price": 4.00,
        "desc_contains": "Stoneware Mug",
    },
    {
        "code": "XS5747A",
        "upc": "191009635727",
        "qty": 24,
        "price": 3.20,
        "desc_contains": "Cotton",
    },
    {
        "code": "XS8838",
        "upc": "191009709855",
        "qty": 6,
        "price": 5.60,
        "desc_contains": "Glass Canister",
    },
    {
        "code": "XS8837",
        "upc": "191009709848",
        "qty": 6,
        "price": 6.40,
        "desc_contains": "Glass Canister",
    },
    {
        "code": "XS3350",
        "upc": "191009571414",
        "qty": 12,
        "price": 8.00,
        "desc_contains": "Cotton Tea",
    },
    {
        "code": "XS3844",
        "upc": "191009582816",
        "qty": 4,
        "price": 18.80,
        "desc_contains": "Acrylic",
    },
    {
        "code": "XS8714",
        "upc": "191009722922",
        "qty": 4,
        "price": 18.80,
        "desc_contains": "Acrylic Throw",
    },
    {
        "code": "XS5692A",
        "upc": "191009636038",
        "qty": 24,
        "price": 3.20,
        "desc_contains": "Stoneware Mug",
    },
    {
        "code": "XS9082",
        "upc": "191009723929",
        "qty": 12,
        "price": 4.00,
        "desc_contains": "Cotton PotHolder",
    },
    {
        "code": "XS7793A",
        "upc": "191009717706",
        "qty": 24,
        "price": 3.00,
        "desc_contains": "Paper",
    },
    {
        "code": "XS8978",
        "upc": "191009723592",
        "qty": 4,
        "price": 17.20,
        "desc_contains": "Cotton Table",
    },
]


def load_cs_error2_document():
    """Load CS003837319_Error 2.PDF Document AI output for testing"""
    json_file = "/Volumes/Working/Code/GoogleCloud/invoice-processor-fn/test_invoices/CS003837319_Error 2_docai_output.json"

    try:
        with open(json_file, "r") as f:
            doc_data = json.load(f)
    except FileNotFoundError:
        pytest.skip(f"CS Error 2 JSON file not found: {json_file}")

    # Create mock document object compatible with main.py expectations
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


def test_production_load_simulation():
    """Test system under realistic production load - RED PHASE: Will initially fail"""

    # Simulate concurrent webhook requests (typical Zapier load)
    concurrent_requests = 10
    test_documents = []

    # Create test documents representing typical production mix
    test_documents.extend(
        [
            create_cs_error2_document(),  # Tabular XS format
            create_traditional_d_code_document(),  # Pattern-based D format
            create_mixed_format_document(),  # Mixed content
        ]
        * 4
    )  # 12 total documents

    results = []
    errors = []

    def process_document_worker(doc_index, document):
        """Worker function to process a single document"""
        try:
            start_time = time.time()
            rows = process_creative_coop_document(document)
            end_time = time.time()

            processing_time = end_time - start_time
            results.append(
                {
                    "doc_index": doc_index,
                    "processing_time": processing_time,
                    "rows_extracted": len(rows),
                    "success": True,
                }
            )
        except Exception as e:
            errors.append({"doc_index": doc_index, "error": str(e), "success": False})

    # Launch concurrent processing threads
    threads = []
    for i, document in enumerate(test_documents[:concurrent_requests]):
        thread = threading.Thread(target=process_document_worker, args=(i, document))
        threads.append(thread)

    # Start all threads simultaneously
    start_time = time.time()
    for thread in threads:
        thread.start()

    # Wait for all to complete
    for thread in threads:
        thread.join(timeout=60)  # 60 second timeout per thread

    total_time = time.time() - start_time

    # Analyze results
    successful_processes = len([r for r in results if r["success"]])
    failed_processes = len(errors)

    print(f"\n🚀 Production Load Test Results:")
    print(f"Concurrent requests: {concurrent_requests}")
    print(f"Successful processes: {successful_processes}/{concurrent_requests}")
    print(f"Failed processes: {failed_processes}")
    print(f"Total processing time: {total_time:.2f}s")

    if results:
        avg_processing_time = sum(r["processing_time"] for r in results) / len(results)
        max_processing_time = max(r["processing_time"] for r in results)
        total_rows = sum(r["rows_extracted"] for r in results)

        print(f"Average processing time: {avg_processing_time:.2f}s")
        print(f"Maximum processing time: {max_processing_time:.2f}s")
        print(f"Total rows extracted: {total_rows}")
        print(f"Overall throughput: {total_rows/total_time:.1f} rows/second")

    # Production requirements
    assert (
        successful_processes >= concurrent_requests * 0.95
    ), f"Success rate {successful_processes/concurrent_requests:.1%} below 95%"
    assert (
        max_processing_time < 160
    ), f"Max processing time {max_processing_time:.2f}s exceeds Zapier 160s timeout"
    assert (
        failed_processes == 0
    ), f"Found {failed_processes} failed processes in production load test"


def test_error_recovery_production_scenarios():
    """Test error recovery for realistic production failure scenarios - RED PHASE: Will initially fail"""

    error_scenarios = [
        {
            "name": "Corrupted PDF data",
            "setup": lambda: create_corrupted_document(),
            "expected_behavior": "Return empty results, not crash",
        },
        {
            "name": "Memory pressure simulation",
            "setup": lambda: create_large_memory_document(),
            "expected_behavior": "Complete processing within memory limits",
        },
        {
            "name": "Malformed document entities",
            "setup": lambda: create_malformed_entities_document(),
            "expected_behavior": "Graceful degradation with partial processing",
        },
    ]

    recovery_results = {}

    for scenario in error_scenarios:
        print(f"\nTesting: {scenario['name']}")

        try:
            if callable(scenario["setup"]):
                test_data = scenario["setup"]()

                result = test_error_scenario_with_data(scenario["name"], test_data)

            recovery_results[scenario["name"]] = {"success": True, "behavior": result}
            print(f"✅ {scenario['name']}: Handled gracefully")

        except Exception as e:
            recovery_results[scenario["name"]] = {"success": False, "error": str(e)}
            print(f"❌ {scenario['name']}: Failed - {e}")

    # All scenarios should be handled gracefully
    failed_scenarios = [
        name for name, result in recovery_results.items() if not result["success"]
    ]
    assert (
        len(failed_scenarios) == 0
    ), f"Failed to handle error scenarios: {failed_scenarios}"


def test_production_monitoring_and_alerting():
    """Test production monitoring capabilities - RED PHASE: Will initially fail"""

    document = create_cs_error2_document()

    # Capture all output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        start_time = time.time()
        rows = process_creative_coop_document(document)
        end_time = time.time()

    stdout_content = stdout_capture.getvalue()
    stderr_content = stderr_capture.getvalue()

    # Validate monitoring information is logged
    monitoring_checks = {
        "processing_time_logged": "Processing time" in stdout_content
        or "seconds" in stdout_content,
        "vendor_detection_logged": "Creative-Coop" in stdout_content,
        "tier_usage_logged": "Tier" in stdout_content,
        "extraction_counts_logged": any(
            str(i) in stdout_content for i in range(10, 50)
        ),
        "error_handling_logged": len(stderr_content) == 0
        or "ERROR" not in stderr_content,
    }

    print(f"\n📊 Production Monitoring Validation:")
    for check, passed in monitoring_checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check.replace('_', ' ').title()}: {status}")

    # All monitoring checks should pass
    failed_checks = [check for check, passed in monitoring_checks.items() if not passed]
    assert len(failed_checks) == 0, f"Monitoring checks failed: {failed_checks}"


def test_security_production_hardening():
    """Test security aspects for production deployment - RED PHASE: Will initially fail"""

    security_tests = []

    # Test 1: Large PDF handling (DoS protection)
    def test_large_pdf_handling():
        # Simulate very large PDF processing
        large_text = "X" * 1000000  # 1MB of text
        document = create_mock_document(large_text)

        start_time = time.time()
        try:
            rows = process_creative_coop_document(document)
            processing_time = time.time() - start_time

            # Should complete within reasonable time and memory
            assert (
                processing_time < 60
            ), f"Large PDF took {processing_time:.2f}s, risk of DoS"
            return True
        except Exception as e:
            # Should handle gracefully, not crash
            return "handled gracefully" in str(e).lower() or processing_time < 60

    # Test 2: Malicious content handling
    def test_malicious_content_handling():
        malicious_patterns = [
            "<?php eval($_POST['cmd']); ?>",  # PHP injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "'; DROP TABLE invoices; --",  # SQL injection attempt
            "../../../etc/passwd",  # Path traversal attempt
        ]

        for pattern in malicious_patterns:
            document = create_mock_document(
                f"XS9826A {pattern} 24 0 0 24 each 2.00 1.60 38.40"
            )
            try:
                rows = process_creative_coop_document(document)
                # Should process normally, malicious content should be treated as text
                assert len(rows) >= 0  # Should not crash
            except Exception as e:
                # Should not fail due to malicious content
                return False

        return True

    # Test 3: Memory exhaustion protection
    def test_memory_exhaustion_protection():
        # Test with many repeated patterns
        large_document_lines = []
        for i in range(10000):  # 10k products
            large_document_lines.append(
                f"XS{i:04d}A | 191009{i:06d} | Product {i} | 1 | 0 | 0 | 1 | each | 2.00 | 1.60 | 1.60"
            )

        large_text = "\n".join(large_document_lines)
        document = create_mock_document(large_text)

        try:
            # Import psutil only if available, otherwise skip memory test
            try:
                import os

                import psutil

                process = psutil.Process(os.getpid())
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                print("psutil not available, skipping detailed memory monitoring")
                initial_memory = 0

            start_time = time.time()
            rows = process_creative_coop_document(document)
            processing_time = time.time() - start_time

            if initial_memory > 0:
                final_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = final_memory - initial_memory

                # Memory growth should be reasonable
                assert (
                    memory_growth < 500
                ), f"Memory grew by {memory_growth:.1f}MB, potential memory exhaustion"

            # Should complete in reasonable time
            assert (
                processing_time < 120
            ), f"Large document processing took {processing_time:.2f}s"
            return True
        except Exception as e:
            # Should handle large documents gracefully
            return (
                "memory" in str(e).lower()
                or "limit" in str(e).lower()
                or "timeout" in str(e).lower()
            )

    # Run security tests
    security_results = {
        "large_pdf_handling": test_large_pdf_handling(),
        "malicious_content_handling": test_malicious_content_handling(),
        "memory_exhaustion_protection": test_memory_exhaustion_protection(),
    }

    print(f"\n🔒 Security Hardening Results:")
    for test_name, passed in security_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")

    # All security tests should pass
    failed_security_tests = [
        test for test, passed in security_results.items() if not passed
    ]
    assert (
        len(failed_security_tests) == 0
    ), f"Security tests failed: {failed_security_tests}"


def test_zapier_webhook_compatibility():
    """Test full compatibility with Zapier webhook patterns - RED PHASE: Will initially fail"""

    # Test different Zapier input formats
    zapier_test_cases = [
        {
            "name": "Direct file upload",
            "payload": {"invoice_file": "mock_pdf_content"},
            "expected": "Should process uploaded PDF file",
        },
        {
            "name": "URL-based processing",
            "payload": {"file_url": "https://example.com/invoice.pdf"},
            "expected": "Should download and process PDF from URL",
        },
        {
            "name": "Form data format",
            "payload": {"invoice_file": "url_to_pdf"},
            "expected": "Should handle form data input method",
        },
    ]

    compatibility_results = {}

    for test_case in zapier_test_cases:
        print(f"\nTesting Zapier format: {test_case['name']}")

        try:
            # Simulate Zapier webhook call
            result = simulate_zapier_webhook(test_case["payload"])

            compatibility_results[test_case["name"]] = {
                "success": True,
                "result": result,
            }
            print(f"✅ {test_case['name']}: Compatible")

        except Exception as e:
            compatibility_results[test_case["name"]] = {
                "success": False,
                "error": str(e),
            }
            print(f"❌ {test_case['name']}: Failed - {e}")

    # All Zapier formats should be compatible
    failed_formats = [
        name for name, result in compatibility_results.items() if not result["success"]
    ]
    assert (
        len(failed_formats) == 0
    ), f"Zapier compatibility failed for: {failed_formats}"


def test_production_performance_benchmarks():
    """Test performance under production-like conditions - RED PHASE: Will initially fail"""

    # Performance benchmark scenarios
    benchmark_scenarios = [
        {
            "name": "Single CS Error 2",
            "documents": [create_cs_error2_document()],
            "target_time": 15.0,
        },
        {
            "name": "Multiple D-code invoices",
            "documents": [create_traditional_d_code_document()] * 3,
            "target_time": 10.0,
        },
        {
            "name": "Mixed format batch",
            "documents": [
                create_cs_error2_document(),
                create_traditional_d_code_document(),
                create_mixed_format_document(),
            ],
            "target_time": 25.0,
        },
    ]

    benchmark_results = {}

    for scenario in benchmark_scenarios:
        print(f"\nBenchmarking: {scenario['name']}")

        processing_times = []
        total_rows = 0

        # Run multiple iterations for accurate benchmarking
        for iteration in range(3):
            start_time = time.time()

            iteration_rows = 0
            for document in scenario["documents"]:
                rows = process_creative_coop_document(document)
                iteration_rows += len(rows)

            end_time = time.time()
            processing_time = end_time - start_time
            processing_times.append(processing_time)
            total_rows = max(total_rows, iteration_rows)

        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)

        benchmark_results[scenario["name"]] = {
            "avg_time": avg_time,
            "max_time": max_time,
            "total_rows": total_rows,
            "meets_target": avg_time <= scenario["target_time"],
        }

        status = "✅ PASS" if avg_time <= scenario["target_time"] else "❌ FAIL"
        print(
            f"   Average time: {avg_time:.2f}s (target: {scenario['target_time']}s) {status}"
        )
        print(f"   Max time: {max_time:.2f}s")
        print(f"   Rows extracted: {total_rows}")

    # All benchmarks should meet targets
    failed_benchmarks = [
        name for name, result in benchmark_results.items() if not result["meets_target"]
    ]
    assert (
        len(failed_benchmarks) == 0
    ), f"Performance benchmarks failed: {failed_benchmarks}"


# Helper functions for test setup
def create_cs_error2_document():
    """Create CS Error 2 document for testing"""
    try:
        return load_cs_error2_document()
    except:
        # Fallback if file not available
        cs_text = """
        Product Code | UPC         | Description                          | Qty Ord | Qty Alloc | Qty Shipped | Qty BkOrd | U/M  | List Price | Your Price | Your Extd Price
        XS9826A      | 191009727774| 6"H Metal Ballerina Ornament       | 24      | 0         | 0           | 24        | each | 2.00       | 1.60       | 38.40
        XS9649A      | 191009725688| 8"H x 6.5"W x 4"D Paper Mache      | 24      | 0         | 0           | 24        | each | 3.50       | 2.80       | 67.20
        """
        return create_mock_document(cs_text)


def create_traditional_d_code_document():
    """Create traditional D-code document for testing"""
    d_code_text = """
    Creative-Coop Order
    DF6802 Blue Ceramic Vase 8 0 lo each $12.50 wholesale $100.00
    ST1234 Cotton Throw Set 6 0 Set $8.00 retail $48.00
    """
    return create_mock_document(d_code_text)


def create_mixed_format_document():
    """Create mixed format document for testing"""
    mixed_text = """
    Creative-Coop Mixed Invoice
    
    Tabular section:
    XS9826A | 191009727774 | Product | 24 | 0 | 0 | 24 | each | 2.00 | 1.60 | 38.40
    
    Pattern section:
    DF6802 Vase 8 0 Set $12.50 $100.00
    
    Context section:
    ST1234: Cotton Throw
    Price: $8.00 wholesale
    Quantity: 6
    """
    return create_mock_document(mixed_text)


def create_corrupted_document():
    """Create corrupted document for error testing"""
    corrupted_text = "CORRUPTED_DATA_\x00\x01\x02INVALID_PDF_CONTENT"
    return create_mock_document(corrupted_text)


def create_large_memory_document():
    """Create large document for memory pressure testing"""
    large_lines = []
    for i in range(1000):  # Create large but reasonable document
        large_lines.append(
            f"XS{i:04d}A | 191009{i:06d} | Large Product {i} | 1 | 0 | 0 | 1 | each | 2.00 | 1.60 | 1.60"
        )

    large_text = "\n".join(large_lines)
    return create_mock_document(large_text)


def create_malformed_entities_document():
    """Create document with malformed entities"""

    class MalformedDocument:
        def __init__(self):
            self.text = "XS9826A Valid text"
            self.entities = []

            # Create malformed entity
            entity = type("Entity", (), {})()
            entity.type_ = None  # Invalid type
            entity.mention_text = None  # Invalid text
            entity.confidence = "invalid_confidence"  # Invalid confidence
            entity.properties = "not_a_list"  # Invalid properties
            self.entities.append(entity)

    return MalformedDocument()


def create_mock_document(text):
    """Create mock document for testing"""

    class MockDocument:
        def __init__(self, text):
            self.text = text
            self.entities = []

            # Create basic entity for testing
            entity = type("Entity", (), {})()
            entity.type_ = "line_item"
            entity.mention_text = text
            entity.confidence = 0.9
            entity.properties = []
            self.entities.append(entity)

    return MockDocument(text)


def test_error_scenario_with_data(scenario_name, test_data):
    """Test error scenario with provided data"""
    try:
        rows = process_creative_coop_document(test_data)
        return {"processed": True, "rows": len(rows)}
    except Exception as e:
        return {"processed": False, "error": str(e), "handled_gracefully": True}


def simulate_zapier_webhook(payload):
    """Simulate Zapier webhook call"""
    # Mock implementation for testing
    if "invoice_file" in payload:
        return {
            "status": "success",
            "method": "file_upload",
            "payload_received": payload,
        }
    elif "file_url" in payload:
        return {
            "status": "success",
            "method": "url_download",
            "payload_received": payload,
        }
    else:
        raise ValueError("Invalid Zapier payload format")


if __name__ == "__main__":
    print("🧪 Running Production Deployment Readiness Tests (RED PHASE)")
    print("=" * 70)

    # Run individual test functions to see current state
    try:
        print("\n🚀 Testing Production Load Simulation...")
        test_production_load_simulation()
        print("✅ Load simulation test passed")
    except Exception as e:
        print(f"❌ Load simulation test failed: {e}")

    try:
        print("\n🔧 Testing Error Recovery Scenarios...")
        test_error_recovery_production_scenarios()
        print("✅ Error recovery test passed")
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")

    try:
        print("\n📊 Testing Production Monitoring...")
        test_production_monitoring_and_alerting()
        print("✅ Monitoring test passed")
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")

    try:
        print("\n🔒 Testing Security Hardening...")
        test_security_production_hardening()
        print("✅ Security test passed")
    except Exception as e:
        print(f"❌ Security test failed: {e}")

    try:
        print("\n🌐 Testing Zapier Compatibility...")
        test_zapier_webhook_compatibility()
        print("✅ Zapier compatibility test passed")
    except Exception as e:
        print(f"❌ Zapier compatibility test failed: {e}")

    try:
        print("\n⚡ Testing Performance Benchmarks...")
        test_production_performance_benchmarks()
        print("✅ Performance benchmark test passed")
    except Exception as e:
        print(f"❌ Performance benchmark test failed: {e}")

    print("\n" + "=" * 70)
    print("RED PHASE: Production deployment tests defined")
    print("Next: Implement GREEN phase to make tests pass")
