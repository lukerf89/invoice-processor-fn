#!/usr/bin/env python3
"""
Validation Test for Enhanced Tabular Price Extraction - Task 201

This script tests the enhanced tabular price extraction against the real
CS003837319_Error 2.PDF document to validate the 95% accuracy goal.
"""

import json
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import (
    extract_creative_coop_product_mappings_corrected,
    extract_tabular_price_creative_coop_enhanced,
)


def load_test_document(filename):
    """Load test document from test_invoices directory"""
    test_file_path = os.path.join(
        os.path.dirname(__file__), "..", "test_invoices", filename
    )

    with open(test_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("text", "")


def main():
    """Test enhanced price extraction accuracy against CS003837319_Error 2.PDF"""

    print("🧪 Enhanced Tabular Price Extraction Validation - Task 201")
    print("=" * 70)

    # Load the CS document
    document_text = load_test_document("CS003837319_Error 2_docai_output.json")

    # Extract all product codes from the document
    product_mappings = extract_creative_coop_product_mappings_corrected(document_text)

    if not product_mappings:
        print("❌ No product mappings found in document")
        return

    print(f"📊 Found {len(product_mappings)} products in document")
    print()

    # Test price extraction for each product
    successful_extractions = 0
    failed_extractions = 0
    results = []

    for product_code, product_info in product_mappings.items():
        print(f"Testing product: {product_code}")

        # Test enhanced tabular price extraction
        extracted_price = extract_tabular_price_creative_coop_enhanced(
            document_text, product_code
        )

        if extracted_price:
            successful_extractions += 1
            print(f"  ✅ Enhanced extraction: {extracted_price}")
            results.append(
                {
                    "product_code": product_code,
                    "extracted_price": extracted_price,
                    "status": "success",
                    "upc": product_info.get("upc", "Unknown"),
                    "description": product_info.get("description", "Unknown")[:50]
                    + "...",
                }
            )
        else:
            failed_extractions += 1
            print(f"  ❌ Enhanced extraction failed")
            results.append(
                {
                    "product_code": product_code,
                    "extracted_price": None,
                    "status": "failed",
                    "upc": product_info.get("upc", "Unknown"),
                    "description": product_info.get("description", "Unknown")[:50]
                    + "...",
                }
            )

        print()

    # Calculate accuracy
    total_products = len(product_mappings)
    accuracy_percentage = (
        (successful_extractions / total_products) * 100 if total_products > 0 else 0
    )

    print()
    print("📈 ENHANCED TABULAR PRICE EXTRACTION RESULTS")
    print("=" * 50)
    print(f"Total Products: {total_products}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Failed Extractions: {failed_extractions}")
    print(f"Accuracy: {accuracy_percentage:.1f}%")
    print()

    # Show detailed results
    print("📋 DETAILED RESULTS")
    print("-" * 80)
    print(f"{'Product':<10} {'Price':<8} {'Status':<8} {'UPC':<13} {'Description':<30}")
    print("-" * 80)

    for result in results:
        price_str = result["extracted_price"] if result["extracted_price"] else "N/A"
        print(
            f"{result['product_code']:<10} {price_str:<8} {result['status']:<8} {result['upc']:<13} {result['description']:<30}"
        )

    # Check if we achieved 95% accuracy goal
    print()
    if accuracy_percentage >= 95.0:
        print("🎉 SUCCESS: Achieved 95%+ accuracy goal!")
        print(f"   Target: 95% | Actual: {accuracy_percentage:.1f}%")
    elif accuracy_percentage >= 90.0:
        print("🟡 GOOD: Close to 95% accuracy goal")
        print(
            f"   Target: 95% | Actual: {accuracy_percentage:.1f}% (gap: {95.0 - accuracy_percentage:.1f}%)"
        )
    else:
        print("🔴 NEEDS IMPROVEMENT: Below 90% accuracy")
        print(
            f"   Target: 95% | Actual: {accuracy_percentage:.1f}% (gap: {95.0 - accuracy_percentage:.1f}%)"
        )

    print()
    print("Task 201 validation complete.")
    return accuracy_percentage


if __name__ == "__main__":
    main()
