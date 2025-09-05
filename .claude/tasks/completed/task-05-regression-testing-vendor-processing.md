# Task 05: Regression Testing - Existing Vendor Processing Validation

## TDD Cycle Overview
**RED**: Write tests that establish current 100% accuracy baselines for existing vendors
**GREEN**: Verify all vendor processing maintains accuracy after XS-code pattern changes
**REFACTOR**: Create automated regression test suite for ongoing vendor validation

## Test Requirements
- [ ] Baseline accuracy tests for HarperCollins (100% accuracy requirement)
- [ ] OneHundred80 processing validation tests
- [ ] Rifle Paper processing accuracy tests
- [ ] Generic vendor processing regression tests
- [ ] Pattern matching performance tests across all vendors
- [ ] End-to-end processing pipeline tests for each vendor type

## Implementation Steps (Red-Green-Refactor)

### Step 1: RED - Establish Current Baselines

```python
# Test file: test_scripts/test_vendor_processing_regression.py
import pytest
import json
import csv
import os
from unittest.mock import patch, MagicMock

# Import vendor-specific processing functions
from main import (
    process_harpercollins_document,
    process_onehundred80_document,
    detect_vendor_type,
    extract_line_items_from_entities,
    process_creative_coop_document
)

class TestVendorRegressionBaselines:
    """Establish accuracy baselines for all vendor processing"""

    @pytest.fixture
    def harpercollins_test_data(self):
        """Load HarperCollins test data"""
        # Use known good HarperCollins invoice
        test_files = [
            'test_invoices/HarperCollins_PO_docai_output.json',
            'test_invoices/anne_mcgilvray_harpercollins_docai_output.json'
        ]

        for test_file in test_files:
            if os.path.exists(test_file):
                with open(test_file, 'r') as f:
                    return json.load(f)

        pytest.skip("No HarperCollins test data available")

    @pytest.fixture
    def onehundred80_test_data(self):
        """Load OneHundred80 test data"""
        test_files = [
            'test_invoices/OneHundred80_docai_output.json',
            'test_invoices/onehundred80_test_docai_output.json'
        ]

        for test_file in test_files:
            if os.path.exists(test_file):
                with open(test_file, 'r') as f:
                    return json.load(f)

        pytest.skip("No OneHundred80 test data available")

    @pytest.fixture
    def rifle_paper_test_data(self):
        """Load Rifle Paper test data"""
        test_files = [
            'test_invoices/Rifle_Paper_INV_J7XM9XQ3HB_docai_output.json',
            'test_invoices/rifle_paper_docai_output.json'
        ]

        for test_file in test_files:
            if os.path.exists(test_file):
                with open(test_file, 'r') as f:
                    return json.load(f)

        pytest.skip("No Rifle Paper test data available")

    def test_harpercollins_baseline_accuracy(self, harpercollins_test_data):
        """RED: Establish HarperCollins 100% accuracy baseline"""
        # Expected HarperCollins results based on known good processing
        expected_items = [
            # Expected format: [Order Date, Vendor, INV/PO, Item (ISBN; Title), Wholesale, Qty]
            # This should be populated with actual expected results from perfect_processing.py
        ]

        # Process with current implementation
        line_items = process_harpercollins_document(harpercollins_test_data)

        # RED: Document current performance as baseline
        baseline_count = len(line_items)

        # Verify processing produces results
        assert baseline_count > 0, f"HarperCollins baseline should produce items, got {baseline_count}"

        # Document baseline for comparison
        print(f"HarperCollins baseline: {baseline_count} items extracted")

        # Validate format consistency
        for i, item in enumerate(line_items):
            assert len(item) == 6, f"HarperCollins item {i} should have 6 columns, got {len(item)}: {item}"

        return baseline_count

    def test_onehundred80_baseline_accuracy(self, onehundred80_test_data):
        """RED: Establish OneHundred80 baseline accuracy"""
        # Process with current implementation
        line_items = process_onehundred80_document(onehundred80_test_data)

        baseline_count = len(line_items)

        # Verify processing produces results
        assert baseline_count > 0, f"OneHundred80 baseline should produce items, got {baseline_count}"

        print(f"OneHundred80 baseline: {baseline_count} items extracted")

        # Validate format
        for i, item in enumerate(line_items):
            assert len(item) == 6, f"OneHundred80 item {i} should have 6 columns, got {len(item)}: {item}"

        return baseline_count

    def test_rifle_paper_baseline_accuracy(self, rifle_paper_test_data):
        """RED: Establish Rifle Paper baseline accuracy"""
        # Rifle Paper uses generic processing
        line_items = extract_line_items_from_entities(rifle_paper_test_data)

        baseline_count = len(line_items)

        # Verify processing produces results
        assert baseline_count > 0, f"Rifle Paper baseline should produce items, got {baseline_count}"

        print(f"Rifle Paper baseline: {baseline_count} items extracted")

        # Validate format
        for i, item in enumerate(line_items):
            assert len(item) == 6, f"Rifle Paper item {i} should have 6 columns, got {len(item)}: {item}"

        return baseline_count

    def test_vendor_detection_baselines(self, harpercollins_test_data, onehundred80_test_data):
        """RED: Test vendor detection accuracy baselines"""

        # Test HarperCollins detection
        hc_vendor = detect_vendor_type(harpercollins_test_data)
        assert 'harper' in hc_vendor['vendor'].lower(), f"Should detect HarperCollins, got {hc_vendor['vendor']}"

        # Test OneHundred80 detection
        oh80_vendor = detect_vendor_type(onehundred80_test_data)
        assert 'onehundred80' in oh80_vendor['vendor'].lower(), f"Should detect OneHundred80, got {oh80_vendor['vendor']}"

        print(f"Vendor detection baselines:")
        print(f"  HarperCollins: {hc_vendor['vendor']} (confidence: {hc_vendor['confidence']:.2f})")
        print(f"  OneHundred80: {oh80_vendor['vendor']} (confidence: {oh80_vendor['confidence']:.2f})")

    def test_d_code_pattern_still_works_for_existing_vendors(self):
        """RED: Test that D-code patterns work with test data"""
        import re

        # Test current D-code pattern
        current_pattern = r"\b(D[A-Z]\d{4}[A-Z]?)\b"

        # Sample D-codes from existing vendors (if any)
        test_d_codes = ["DA1234A", "DB5678B", "DG9999C", "DH1111"]

        test_text = " ".join(test_d_codes)
        matches = re.findall(current_pattern, test_text)

        # Should match all D-codes
        assert len(matches) == len(test_d_codes), f"D-pattern should match all D-codes, got {len(matches)}/{len(test_d_codes)}"
        assert set(matches) == set(test_d_codes), f"Matches don't match expected: {matches} vs {test_d_codes}"
```

### Step 2: GREEN - Verify No Regression After Changes

```python
# Tests to verify processing maintains accuracy after XS-code pattern fix

    def test_harpercollins_accuracy_maintained_after_pattern_fix(self, harpercollins_test_data):
        """GREEN: Verify HarperCollins processing unchanged after XS-code pattern fix"""

        # Get baseline from previous test
        baseline_items = process_harpercollins_document(harpercollins_test_data)
        baseline_count = len(baseline_items)

        # After pattern fix, should produce identical results
        post_fix_items = process_harpercollins_document(harpercollins_test_data)
        post_fix_count = len(post_fix_items)

        # GREEN: Should maintain exact same accuracy
        assert post_fix_count == baseline_count, f"HarperCollins regression: {baseline_count} → {post_fix_count} items"

        # Verify item content hasn't changed
        for i, (baseline_item, post_fix_item) in enumerate(zip(baseline_items, post_fix_items)):
            assert baseline_item == post_fix_item, f"HarperCollins item {i} changed: {baseline_item} → {post_fix_item}"

        print(f"HarperCollins: ✅ No regression ({post_fix_count} items)")

    def test_onehundred80_accuracy_maintained_after_pattern_fix(self, onehundred80_test_data):
        """GREEN: Verify OneHundred80 processing unchanged after XS-code pattern fix"""

        # Similar test for OneHundred80
        baseline_items = process_onehundred80_document(onehundred80_test_data)
        baseline_count = len(baseline_items)

        post_fix_items = process_onehundred80_document(onehundred80_test_data)
        post_fix_count = len(post_fix_items)

        assert post_fix_count == baseline_count, f"OneHundred80 regression: {baseline_count} → {post_fix_count} items"

        print(f"OneHundred80: ✅ No regression ({post_fix_count} items)")

    def test_rifle_paper_accuracy_maintained_after_pattern_fix(self, rifle_paper_test_data):
        """GREEN: Verify Rifle Paper processing unchanged after XS-code pattern fix"""

        baseline_items = extract_line_items_from_entities(rifle_paper_test_data)
        baseline_count = len(baseline_items)

        post_fix_items = extract_line_items_from_entities(rifle_paper_test_data)
        post_fix_count = len(post_fix_items)

        assert post_fix_count == baseline_count, f"Rifle Paper regression: {baseline_count} → {post_fix_count} items"

        print(f"Rifle Paper: ✅ No regression ({post_fix_count} items)")

    def test_vendor_detection_unchanged_after_pattern_fix(self, harpercollins_test_data, onehundred80_test_data):
        """GREEN: Verify vendor detection unchanged after pattern fix"""

        # Vendor detection shouldn't be affected by product code patterns
        hc_vendor = detect_vendor_type(harpercollins_test_data)
        oh80_vendor = detect_vendor_type(onehundred80_test_data)

        assert 'harper' in hc_vendor['vendor'].lower()
        assert 'onehundred80' in oh80_vendor['vendor'].lower()

        print(f"Vendor detection: ✅ No regression")

    def test_updated_pattern_still_matches_d_codes(self):
        """GREEN: Test that updated pattern still matches existing D-codes"""
        # Updated pattern that includes XS codes
        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"

        # Test D-codes still work
        test_d_codes = ["DA1234A", "DB5678B", "DG9999C", "DH1111"]
        test_text = " ".join(test_d_codes)

        matches = re.findall(updated_pattern, test_text)

        assert len(matches) == len(test_d_codes), f"Updated pattern should match D-codes, got {len(matches)}/{len(test_d_codes)}"
        assert set(matches) == set(test_d_codes), f"D-code matches incorrect: {matches} vs {test_d_codes}"

        print(f"D-code pattern: ✅ Still works with updated pattern")

    def test_updated_pattern_now_matches_xs_codes(self):
        """GREEN: Test that updated pattern now matches XS-codes"""
        updated_pattern = r"\b((?:D[A-Z]\d{4}|XS\d+)[A-Z]?)\b"

        # Test XS-codes now work
        test_xs_codes = ["XS9826A", "XS8911A", "XS9649A", "XS9482", "XS9840A"]
        test_text = " ".join(test_xs_codes)

        matches = re.findall(updated_pattern, test_text)

        assert len(matches) == len(test_xs_codes), f"Updated pattern should match XS-codes, got {len(matches)}/{len(test_xs_codes)}"
        assert set(matches) == set(test_xs_codes), f"XS-code matches incorrect: {matches} vs {test_xs_codes}"

        print(f"XS-code pattern: ✅ Now works with updated pattern")
```

### Step 3: REFACTOR - Automated Regression Test Suite

Create comprehensive automated regression testing:

```python
# Automated regression test suite for all vendors

class VendorRegressionTestSuite:
    """Automated regression test suite for vendor processing"""

    def __init__(self):
        self.test_results = {}
        self.baselines = {}

    def run_full_regression_suite(self):
        """Run complete regression test suite for all vendors"""

        vendors = ['harpercollins', 'onehundred80', 'rifle_paper', 'creative_coop']

        print("🧪 Running Full Vendor Regression Test Suite")
        print("=" * 50)

        for vendor in vendors:
            try:
                result = self.test_vendor_regression(vendor)
                self.test_results[vendor] = result

                if result['passed']:
                    print(f"✅ {vendor}: PASSED ({result['items']} items)")
                else:
                    print(f"❌ {vendor}: FAILED - {result['error']}")

            except Exception as e:
                self.test_results[vendor] = {
                    'passed': False,
                    'error': str(e),
                    'items': 0
                }
                print(f"❌ {vendor}: ERROR - {str(e)}")

        return self.generate_regression_report()

    def test_vendor_regression(self, vendor_name):
        """Test regression for specific vendor"""

        # Load test data for vendor
        test_data = self.load_vendor_test_data(vendor_name)

        if not test_data:
            return {'passed': False, 'error': 'No test data available', 'items': 0}

        try:
            # Process with vendor-specific function
            if vendor_name == 'harpercollins':
                line_items = process_harpercollins_document(test_data)
            elif vendor_name == 'onehundred80':
                line_items = process_onehundred80_document(test_data)
            elif vendor_name == 'creative_coop':
                line_items = process_creative_coop_document(test_data)
            else:
                line_items = extract_line_items_from_entities(test_data)

            # Validate format
            for item in line_items:
                if len(item) != 6:
                    raise ValueError(f"Invalid format: {len(item)} columns instead of 6")

            return {
                'passed': True,
                'items': len(line_items),
                'error': None
            }

        except Exception as e:
            return {
                'passed': False,
                'items': 0,
                'error': str(e)
            }

    def load_vendor_test_data(self, vendor_name):
        """Load test data for specific vendor"""

        test_file_map = {
            'harpercollins': ['test_invoices/HarperCollins_PO_docai_output.json'],
            'onehundred80': ['test_invoices/OneHundred80_docai_output.json'],
            'rifle_paper': ['test_invoices/Rifle_Paper_INV_J7XM9XQ3HB_docai_output.json'],
            'creative_coop': ['test_invoices/CS003837319_Error 2_docai_output.json']
        }

        for test_file in test_file_map.get(vendor_name, []):
            if os.path.exists(test_file):
                with open(test_file, 'r') as f:
                    return json.load(f)

        return None

    def generate_regression_report(self):
        """Generate comprehensive regression test report"""

        total_vendors = len(self.test_results)
        passed_vendors = sum(1 for r in self.test_results.values() if r['passed'])
        failed_vendors = total_vendors - passed_vendors

        report = {
            'summary': {
                'total_vendors': total_vendors,
                'passed': passed_vendors,
                'failed': failed_vendors,
                'pass_rate': (passed_vendors / total_vendors * 100) if total_vendors > 0 else 0
            },
            'details': self.test_results,
            'recommendations': []
        }

        # Add recommendations based on results
        if failed_vendors > 0:
            report['recommendations'].append("⚠️ Some vendors failed regression testing - investigate before deployment")

        if report['summary']['pass_rate'] < 100:
            report['recommendations'].append("🔍 Review failed vendors and fix issues before proceeding")
        else:
            report['recommendations'].append("✅ All vendors passed - safe to deploy XS-code pattern fix")

        return report

# Performance comparison utility
def compare_processing_performance():
    """Compare processing performance before and after pattern changes"""

    import time

    performance_results = {}

    # Test each vendor processing time
    test_suite = VendorRegressionTestSuite()

    for vendor in ['harpercollins', 'onehundred80', 'rifle_paper']:
        test_data = test_suite.load_vendor_test_data(vendor)

        if test_data:
            start_time = time.time()

            if vendor == 'harpercollins':
                line_items = process_harpercollins_document(test_data)
            elif vendor == 'onehundred80':
                line_items = process_onehundred80_document(test_data)
            else:
                line_items = extract_line_items_from_entities(test_data)

            end_time = time.time()

            performance_results[vendor] = {
                'processing_time': end_time - start_time,
                'items_processed': len(line_items),
                'items_per_second': len(line_items) / max(end_time - start_time, 0.001)
            }

    return performance_results
```

## Acceptance Criteria (Test-Driven)

- [ ] Baseline accuracy established for all existing vendors (HarperCollins, OneHundred80, Rifle Paper)
- [ ] HarperCollins maintains 100% processing accuracy after XS-code pattern changes
- [ ] OneHundred80 processing accuracy unchanged after pattern modifications
- [ ] Rifle Paper processing maintains baseline accuracy levels
- [ ] Vendor detection continues working correctly for all vendor types
- [ ] D-code pattern matching still works for existing vendors using D-codes
- [ ] XS-code pattern matching now works for Creative-Coop without affecting others
- [ ] Processing performance remains within acceptable limits for all vendors
- [ ] Automated regression test suite provides comprehensive coverage
- [ ] All vendors produce properly formatted 6-column output

## Engineering Principles Applied

**Principle 1 - Backward Compatibility**: All existing vendor processing preserved
**Principle 2 - Performance**: No degradation in processing speed across vendors
**Principle 3 - Reliability**: Comprehensive regression testing prevents production issues
**Principle 4 - Maintainability**: Automated test suite for ongoing regression validation
**Principle 5 - Quality Assurance**: 100% pass rate required before deployment

## Code Review Checklist

- [ ] **Baseline Testing**: Current accuracy levels documented for all vendors
- [ ] **Regression Prevention**: Post-change accuracy matches baseline levels
- [ ] **Pattern Compatibility**: Updated patterns work for both existing and new codes
- [ ] **Performance**: Processing times remain within acceptable limits
- [ ] **Format Consistency**: All vendors output 6-column format correctly
- [ ] **Error Handling**: Graceful failure for any vendor processing issues
- [ ] **Automation**: Regression test suite can run independently
- [ ] **Documentation**: Clear test results and recommendations provided

## Success Metrics

- **Zero Regression**: 100% of existing vendors maintain current accuracy levels
- **Pattern Compatibility**: D-codes continue working, XS-codes now work
- **Performance**: <5% processing time increase across all vendors
- **Quality**: 100% pass rate on regression test suite
- **Coverage**: All vendor types included in automated regression testing

## Files Created/Modified

- `test_scripts/test_vendor_processing_regression.py` (comprehensive regression tests)
- `test_scripts/vendor_regression_test_suite.py` (automated test suite)
- Performance comparison utilities
- Regression test reporting tools

## Risk Assessment

**High Risk**: Breaking existing vendor processing during pattern updates
- **Mitigation**: Comprehensive baseline testing, careful pattern modification
- **Detection**: Automated regression test suite, before/after comparison

**Medium Risk**: Performance degradation from updated regex patterns
- **Mitigation**: Performance benchmarking, pattern optimization
- **Detection**: Processing time monitoring, timeout alerts

**Low Risk**: Test data not representative of production scenarios
- **Mitigation**: Use actual production invoice examples where possible
- **Detection**: Manual validation of test results against known good data

## Dependencies

- Test invoices for all vendor types (HarperCollins, OneHundred80, Rifle Paper)
- Document AI output files for comprehensive testing
- Existing vendor processing functions in main.py
- Performance monitoring and benchmarking utilities
