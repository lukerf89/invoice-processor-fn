#!/usr/bin/env python3
"""
Debug clean_item_description function
"""
import re


def clean_item_description_debug(description, product_code, upc_code):
    """Debug version of clean_item_description with print statements"""
    print(f"\n=== DEBUG clean_item_description ===")
    print(f"Input description: '{description}'")
    print(f"Product code: '{product_code}'")
    print(f"UPC code: '{upc_code}'")

    if not description:
        return ""

    # Start with the original description
    original_desc = description.strip()
    print(f"Original desc: '{original_desc}'")

    # Try to extract the actual product description using multiple strategies
    clean_desc = ""

    # Strategy 1: Look for description that starts with dimensions or quoted text
    desc_patterns = [
        r"(S/\d+\s+.{10,})",  # Sets like 'S/3 11-3/4" Rnd...' or 'S/4 18" Sq Cotton...' - CHECK FIRST
        r'(\d+(?:["\'-]\d+)*["\']?[LWH][^0-9\n]{10,})',  # Starts with dimensions like '3-1/4"L x 4"H...' - Must have L/W/H
        r"([A-Z][^0-9\n]{15,})",  # Text starting with capital, at least 15 chars
        r'"([^"]+)"',  # Quoted text
    ]

    print(f"Testing patterns:")
    for i, pattern in enumerate(desc_patterns):
        print(f"  Pattern {i+1}: {pattern}")
        matches = re.findall(pattern, original_desc, re.IGNORECASE)
        print(f"    Matches: {matches}")
        if matches:
            for match in matches:
                candidate = match.strip()
                print(f"    Candidate: '{candidate}'")
                # Make sure it doesn't contain product codes or UPC codes
                if (
                    not re.search(
                        r"\b" + re.escape(product_code) + r"\b",
                        candidate,
                        re.IGNORECASE,
                    )
                    and not re.search(r"\b\d{12,13}\b", candidate)
                    and len(candidate) > 10
                ):
                    clean_desc = candidate
                    print(f"    ✅ SELECTED: '{clean_desc}'")
                    break
                else:
                    print(f"    ❌ REJECTED (contains product code/UPC or too short)")
            if clean_desc:
                break

    print(f"Result after Strategy 1: '{clean_desc}'")

    # Strategy 2: If no good description found, clean the original
    if not clean_desc or len(clean_desc) < 5:
        print(f"Using Strategy 2 (fallback cleaning)")
        clean_desc = original_desc

        # Remove product code if it appears in the description
        if product_code:
            clean_desc = re.sub(
                r"\b" + re.escape(product_code) + r"\b",
                "",
                clean_desc,
                flags=re.IGNORECASE,
            )
            print(f"After removing product code: '{clean_desc}'")

        # Remove UPC codes (12-13 digit numbers)
        clean_desc = re.sub(r"\b\d{12,13}\b", "", clean_desc)
        print(f"After removing UPC codes: '{clean_desc}'")

        # Remove pricing patterns (like "4.00 3.20 38.40")
        clean_desc = re.sub(r"\b\d+\.\d{2}\b", "", clean_desc)
        print(f"After removing pricing: '{clean_desc}'")

        # Remove quantity patterns (like "12 0 each", "8 0 lo each")
        clean_desc = re.sub(
            r"\b\d+\s+\d+\s+(?:lo\s+)?each\b", "", clean_desc, flags=re.IGNORECASE
        )
        clean_desc = re.sub(r"\b\d+\s+\d+\s+Set\b", "", clean_desc, flags=re.IGNORECASE)
        print(f"After removing quantity patterns: '{clean_desc}'")

    # Final cleanup
    clean_desc = " ".join(clean_desc.split())  # Normalize whitespace
    clean_desc = clean_desc.strip(" -\n\r")  # Remove leading/trailing junk
    print(f"Final result: '{clean_desc}'")

    return clean_desc


# Test with DF6802 data
test_description = 'S/4 18" Sq Cotton Embroidered Napkins, Tied w Twill Tape'
product_code = "DF6802"
upc_code = "0191009519157"

result = clean_item_description_debug(test_description, product_code, upc_code)
print(f"\n🎯 FINAL RESULT: '{result}'")
