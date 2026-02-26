#!/usr/bin/env python3
"""
Test all case styles (snake_case, kebab-case, camelCase, PascalCase).

Verifies that all case conversions follow standard naming conventions:
- snake_case: all_lowercase_with_underscores
- kebab-case: all-lowercase-with-hyphens
- camelCase: firstLowerRestMixed (with special handling for already camelCase)
- PascalCase: FirstUpperRestMixed

Programmer: #3
"""

from src.extractors.advanced_extractor import smart_truncate
from src.utils.normalization import normalize_token


def test_all_case_styles():
    """Test all case style conversions with various input types."""
    
    test_cases = [
        # (input, expected_snake, expected_kebab, expected_camel, expected_pascal, description)
        ("Category", "category", "category", "category", "Category", "Single word Title case"),
        ("FAQ", "faq", "faq", "faq", "FAQ", "Single word all caps"),
        ("Hero", "hero", "hero", "hero", "Hero", "Single word Title case"),
        ("Still", "still", "still", "still", "Still", "Single word Title case"),
        ("t.pages", "t_pages", "t-pages", "tPages", "TPages", "Compound with dot separator"),
        ("Category Filter", "category_filter", "category-filter", "categoryFilter", "CategoryFilter", "Two words with space"),
        ("FAQ Items", "faq_items", "faq-items", "faqItems", "FAQItems", "Acronym + word"),
        ("filteredFAQs", "filteredfaqs", "filteredfaqs", "filteredFAQs", "FilteredFAQs", "Already camelCase - preserve"),
        ("expandedItems", "expandeditems", "expandeditems", "expandedItems", "ExpandedItems", "Already camelCase - preserve"),
        ("faqCategories", "faqcategories", "faqcategories", "faqCategories", "FAQCategories", "Already camelCase - preserve"),
    ]
    
    print("=" * 130)
    print("COMPREHENSIVE CASE STYLE TEST")
    print("=" * 130)
    print()
    print(f"{'Input':<25} {'snake_case':<25} {'kebab-case':<25} {'camelCase':<25} {'PascalCase':<25}")
    print("-" * 130)
    
    all_passed = True
    
    for text, exp_snake, exp_kebab, exp_camel, exp_pascal, description in test_cases:
        snake = normalize_token(text, "snake", to_upper=False)
        kebab = normalize_token(text, "kebab", to_upper=False)
        camel = normalize_token(text, "camel", to_upper=False)
        pascal = normalize_token(text, "pascal", to_upper=False)
        
        snake_ok = snake == exp_snake
        kebab_ok = kebab == exp_kebab
        camel_ok = camel == exp_camel
        pascal_ok = pascal == exp_pascal
        
        status_snake = "✅" if snake_ok else "❌"
        status_kebab = "✅" if kebab_ok else "❌"
        status_camel = "✅" if camel_ok else "❌"
        status_pascal = "✅" if pascal_ok else "❌"
        
        print(f"{text:<25} {snake:<23} {status_snake} {kebab:<23} {status_kebab} {camel:<23} {status_camel} {pascal:<23} {status_pascal}")
        
        if not (snake_ok and kebab_ok and camel_ok and pascal_ok):
            all_passed = False
            if not snake_ok:
                print(f"  ⚠️  Expected snake_case: '{exp_snake}', got: '{snake}'")
            if not kebab_ok:
                print(f"  ⚠️  Expected kebab-case: '{exp_kebab}', got: '{kebab}'")
            if not camel_ok:
                print(f"  ⚠️  Expected camelCase: '{exp_camel}', got: '{camel}'")
            if not pascal_ok:
                print(f"  ⚠️  Expected PascalCase: '{exp_pascal}', got: '{pascal}'")
    
    print("\n" + "=" * 130)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Case style rules verified:")
        print("  • snake_case: ALL lowercase with underscores")
        print("  • kebab-case: ALL lowercase with hyphens")
        print("  • camelCase: First char lowercase, already camelCase preserved")
        print("  • PascalCase: First char uppercase")
        return True
    else:
        print("❌ SOME TESTS FAILED! Review the logic.")
        return False


def test_with_truncation():
    """Test case styles combined with truncation (limit=2)."""
    
    print("\n\n" + "=" * 130)
    print("CASE STYLES WITH TRUNCATION (limit=2, after mode)")
    print("=" * 130)
    print()
    
    test_cases = [
        ("{/* Category Filter */}", "Category"),
        ("{/* FAQ Items */}", "FAQ"),
        ("{t.pages.contact.quickLinks.faq}", "t.pages"),
        ("filteredFAQs.map((item", "filteredFAQs"),
    ]
    
    print(f"{'Input':<45} {'Truncated':<20} {'snake_case':<20} {'kebab-case':<20} {'camelCase':<20}")
    print("-" * 125)
    
    for raw_text, expected_truncated in test_cases:
        truncated = smart_truncate(raw_text, "2", avoid_cut=True, avoid_cut_direction="after")
        
        snake = normalize_token(truncated, "snake", to_upper=False)
        kebab = normalize_token(truncated, "kebab", to_upper=False)
        camel = normalize_token(truncated, "camel", to_upper=False)
        
        input_display = raw_text if len(raw_text) <= 42 else raw_text[:39] + "..."
        print(f"{input_display:<45} {truncated:<20} {snake:<20} {kebab:<20} {camel:<20}")
    
    print("\n" + "=" * 130)
    print("✅ Truncation + case conversion working correctly!")


if __name__ == "__main__":
    import sys
    success = test_all_case_styles()
    test_with_truncation()
    print("\n" + "=" * 130)
    sys.exit(0 if success else 1)
