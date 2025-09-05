#!/usr/bin/env python3
"""
Compare current output quantities with expected quantities
"""

# From the user's table
expected_quantities = {
    "DA4315": 12,
    "DF0716": 0,
    "DF4987": 0,
    "DF5599": 8,
    "DF6360": 6,
    "DF6419A": 8,
    "DF6642": 8,
    "DF6802": 6,
    "DF7212A": 0,
    "DF7222A": 0,
    "DF7225A": 0,
    "DF7336": 0,
    "DF7753A": 24,
    "DF7838A": 24,
    "DF8071A": 12,
    "DF8323A": 4,
    "DF8592A": 12,
    "DF8611": 2,
    "DF8637A": 12,
    "DF8649": 6,
    "DF8667A": 12,
    "DF8688": 0,
    "DF8805A": 24,
    "DF9397": 0,
    "DF9407": 4,
    "DF9505": 4,
    "DF9677A": 0,
    "DF9686A": 0,
    "DF9751A": 16,
    "DF9879": 6,
    "DF9880": 6,
    "DF9887A": 24,
    "DG0104A": 0,
    "DG0217A": 6,
    "DG0289": 0,
    "DG0338A": 0,
    "DG0446A": 0,
    "DG0509": 4,
    "DG0512A": 0,
    "DG0635A": 12,
    "DG0642A": 0,
    "DG0718A": 0,
    "DG0744": 0,
    "DG0792": 0,
    "DG0859": 0,
    "DG0881A": 0,
    "DG0990A": 0,
    "DG1062": 0,
    "DG1278": 6,
    "DG1281": 6,
    "DG1378": 4,
    "DG1407A": 0,
}

# Current output quantities from the improved CSV
current_quantities = {
    "DA4315": 12,
    "DF0716": 12,
    "DF4987": 12,
    "DF5599": 12,
    "DF6360": 12,
    "DF6419A": 8,
    "DF6642": 8,
    "DF6802": 8,
    "DF7212A": 8,
    "DF7222A": 8,
    "DF7225A": 8,
    "DF7336": 8,
    "DF7753A": 24,
    "DF7838A": 24,
    "DF8071A": 24,
    "DF8323A": 4,
    "DF8592A": 12,
    "DF8611": 2,
    "DF8637A": 6,
    "DF8649": 6,
    "DF8667A": 12,
    "DF8688": 0,
    "DF8805A": 24,
    "DF9397": 0,
    "DF9407": 0,
    "DF9505": 4,
    "DF9677A": 0,
    "DF9686A": 0,
    "DF9751A": 16,
    "DF9879": 6,
    "DF9880": 6,
    "DF9887A": 24,
    "DG0104A": 0,
    "DG0217A": 6,
    "DG0289": 0,
    "DG0338A": 0,
    "DG0446A": 0,
    "DG0509": 4,
    "DG0512A": 0,
    "DG0635A": 0,
    "DG0642A": 0,
    "DG0718A": 0,
    "DG0744": 0,
    "DG0792": 0,
    "DG0859": 0,
    "DG0881A": 0,
    "DG0990A": 0,
    "DG1062": 0,
    "DG1278": 60,
    "DG1281": 60,
    "DG1378": 60,
    "DG1407A": 60,
}

print("=== QUANTITY COMPARISON ANALYSIS ===\n")

# Count different types of issues
perfect_matches = 0
quantity_issues = []

for product_code in expected_quantities:
    expected = expected_quantities[product_code]
    current = current_quantities.get(product_code, "MISSING")

    if current == expected:
        perfect_matches += 1
    else:
        issue_type = ""
        if current == "MISSING":
            issue_type = "MISSING"
        elif expected == 0 and current > 0:
            issue_type = "FALSE_POSITIVE"
        elif expected > 0 and current == 0:
            issue_type = "FALSE_ZERO"
        else:
            issue_type = "WRONG_VALUE"

        quantity_issues.append(
            {
                "product": product_code,
                "expected": expected,
                "current": current,
                "issue_type": issue_type,
            }
        )

print(
    f"✅ Perfect matches: {perfect_matches}/{len(expected_quantities)} ({perfect_matches/len(expected_quantities)*100:.1f}%)"
)
print(f"❌ Issues found: {len(quantity_issues)}")

print(f"\n📊 Issue breakdown:")
issue_counts = {}
for issue in quantity_issues:
    issue_type = issue["issue_type"]
    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

for issue_type, count in issue_counts.items():
    print(f"  {issue_type}: {count} items")

print(f"\n🔍 Detailed issues:")
for issue in quantity_issues:
    print(
        f"  {issue['product']}: Expected={issue['expected']}, Got={issue['current']} ({issue['issue_type']})"
    )

print(f"\n🎯 Priority fixes needed:")
print(
    f"1. FALSE_ZERO (should be positive but showing 0): {issue_counts.get('FALSE_ZERO', 0)} items"
)
print(
    f"2. FALSE_POSITIVE (should be 0 but showing positive): {issue_counts.get('FALSE_POSITIVE', 0)} items"
)
print(
    f"3. WRONG_VALUE (wrong quantity value): {issue_counts.get('WRONG_VALUE', 0)} items"
)
