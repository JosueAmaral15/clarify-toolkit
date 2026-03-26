#!/usr/bin/env python3
"""
Test camelCase preservation for single words vs compound keys.

Expected behavior:
- Single words after truncation: preserve original case (Category, FAQ, Hero)
- Compound keys: apply camelCase (t.pages → tPages)
- Pure camelCase: preserve as-is (expandedItems, filteredFAQs)

Programmer: #3
"""

from src.extractors.advanced_extractor import smart_truncate
from src.utils.normalization import normalize_token

def test_camelcase_preservation():
    """Test that camelCase preserves original capitalization for single words."""
    
    test_cases = [
        # (input, expected_after_truncate, expected_after_normalize)
        ("{t.pages.contact.quickLinks.faq}", "t.pages", "tPages"),
        ("{/* Category Filter */}", "Category", "Category"),
        ("{/* FAQ Items */}", "FAQ", "FAQ"),
        ("{/* Still Have Questions */}", "Still", "Still"),
        ("{/* Hero Section */}", "Hero", "Hero"),
        ("filteredFAQs.map((item", "filteredFAQs", "filteredFAQs"),
        ("expandedItems.has(item.id)", "expandedItems", "expandedItems"),
        ("faqCategories.map((category", "faqCategories", "faqCategories"),
        ("{t.pages.faq.categories[index]}", "t.pages", "tPages"),
        ("{t.pages.faq.faqData[index].question}", "t.pages", "tPages"),
    ]
    
    print("Testing camelCase preservation with limit=2, after mode:\n")
    print(f"{'Input':<45} {'Truncated':<20} {'Normalized':<20} {'Status'}")
    print("=" * 105)
    
    all_passed = True
    
    for raw_text, expected_truncated, expected_normalized in test_cases:
        truncated = smart_truncate(raw_text, "2", avoid_cut=True, avoid_cut_direction="after")
        normalized = normalize_token(truncated, "camel", to_upper=False)
        
        truncate_ok = truncated == expected_truncated
        normalize_ok = normalized == expected_normalized
        status = "✅ PASS" if (truncate_ok and normalize_ok) else "❌ FAIL"
        
        if not (truncate_ok and normalize_ok):
            all_passed = False
        
        # Truncate input display for readability
        input_display = raw_text if len(raw_text) <= 40 else raw_text[:37] + "..."
        
        print(f"{input_display:<45} {truncated:<20} {normalized:<20} {status}")
        
        if not truncate_ok:
            print(f"  ⚠️  Expected truncated: '{expected_truncated}'")
        if not normalize_ok:
            print(f"  ⚠️  Expected normalized: '{expected_normalized}'")
    
    print("\n" + "=" * 105)
    
    if all_passed:
        print("✅ All tests PASSED! camelCase preservation is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED. Review the logic.")
        return False


if __name__ == "__main__":
    import sys
    success = test_camelcase_preservation()
    sys.exit(0 if success else 1)
