#!/usr/bin/env python3
"""Test camelCase conversion fix with camelCase splitting."""

import re

def normalize_token(s: str, case_style: str, to_upper: bool) -> str:
    """
    Normalize a string to snake/camel/pascal/kebab/preserve; drop non-alnum (after spaces);
    optionally uppercase whole token.
    Splits camelCase/PascalCase into words before applying conversion.
    """
    s = s.strip()
    
    # Special handling for 'preserve' mode - keep original case
    if case_style == "preserve" or case_style == "none":
        # Only remove non-alphanumeric characters, keep original case
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", s)
        # Remove leading/trailing underscores
        token = cleaned.strip("_")
        if to_upper:
            token = token.upper()
        return token
    
    # Step 1: Split camelCase/PascalCase into separate words
    # Insert space before uppercase letters that follow lowercase or are followed by lowercase
    with_spaces = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)  # lowerUpper → lower Upper
    with_spaces = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', with_spaces)  # XMLParser → XML Parser
    
    # Step 2: Convert any remaining non-alphanumeric into space
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", with_spaces)
    
    # Step 3: Split into words
    words = [w for w in cleaned.strip().split() if w]
    
    if not words:
        token = ""
    else:
        if case_style == "snake":
            token = "_".join(w.lower() for w in words)
        elif case_style == "kebab":
            token = "-".join(w.lower() for w in words)
        elif case_style == "camel":
            head = words[0].lower()
            tail = [w[:1].upper() + w[1:].lower() for w in words[1:]]
            token = head + "".join(tail)
        elif case_style == "pascal":
            token = "".join(w[:1].upper() + w[1:].lower() for w in words)
        else:
            # default snake
            token = "_".join(w.lower() for w in words)
    if to_upper:
        token = token.upper()
    return token


# Test cases from the user's output
test_strings = [
    "expandedItems",
    "filteredFAQs",
    "faqCategories",
    "t.pages.contact.quickLinks.faq",
    "FAQPage",
    "XMLHttpRequest",
    "getHTMLElement",
]

print("Testing FIXED camelCase normalization:\n")
for s in test_strings:
    result_camel = normalize_token(s, "camel", False)
    result_pascal = normalize_token(s, "pascal", False)
    result_preserve = normalize_token(s, "preserve", False)
    result_snake = normalize_token(s, "snake", False)
    print(f"Input: '{s}'")
    print(f"  camel:    '{result_camel}' {'✓' if s[0].islower() and result_camel != s.lower() else ''}")
    print(f"  pascal:   '{result_pascal}'")
    print(f"  preserve: '{result_preserve}'")
    print(f"  snake:    '{result_snake}'")
    print()
