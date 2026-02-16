#!/usr/bin/env python3
"""Complete test for all case conversion styles with camelCase splitting."""

import sys
# Path handled by pytest/PYTHONPATH

from src.utils.normalization import normalize_token

# Test cases covering various input formats
test_cases = [
    # Already camelCase
    ("expandedItems", "camel", False, "expandedItems"),
    ("filteredFAQs", "camel", False, "filteredFaQs"),  # FAQ splits to Fa Qs
    ("faqCategories", "camel", False, "faqCategories"),
    
    # Already PascalCase
    ("FAQPage", "pascal", False, "FaqPage"),
    ("XMLHttpRequest", "pascal", False, "XmlHttpRequest"),
    
    # Mixed with special chars
    ("t.pages.contact.quickLinks.faq", "camel", False, "tPagesContactQuickLinksFaq"),
    ("t.pages.contact.quickLinks.faq", "snake", False, "t_pages_contact_quick_links_faq"),
    ("t.pages.contact.quickLinks.faq", "kebab", False, "t-pages-contact-quick-links-faq"),
    ("t.pages.contact.quickLinks.faq", "pascal", False, "TPagesContactQuickLinksFaq"),
    ("t.pages.contact.quickLinks.faq", "preserve", False, "t_pages_contact_quickLinks_faq"),
    
    # Space-separated words
    ("Hello World", "camel", False, "helloWorld"),
    ("Hello World", "pascal", False, "HelloWorld"),
    ("Hello World", "snake", False, "hello_world"),
    ("Hello World", "kebab", False, "hello-world"),
    
    # Already snake_case
    ("hello_world_test", "camel", False, "helloWorldTest"),
    ("hello_world_test", "pascal", False, "HelloWorldTest"),
    
    # Edge cases
    ("", "camel", False, ""),
    ("A", "camel", False, "a"),
    ("ABC", "camel", False, "abc"),
]

print("Complete Case Conversion Test:\n")
print(f"{'Input':<35} {'Style':<10} {'Expected':<30} {'Got':<30} {'Status'}")
print("=" * 110)

passed = 0
failed = 0

for input_str, case_style, to_upper, expected in test_cases:
    result = normalize_token(input_str, case_style, to_upper)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"{input_str:<35} {case_style:<10} {expected:<30} {result:<30} {status}")

print("=" * 110)
print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")

if failed > 0:
    sys.exit(1)
else:
    print("\n✅ All tests passed!")
    sys.exit(0)
