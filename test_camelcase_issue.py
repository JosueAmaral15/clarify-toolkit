#!/usr/bin/env python3
"""Test camelCase conversion issue."""

import re

def normalize_token(s: str, case_style: str, to_upper: bool) -> str:
    """
    Normalize a string to snake/camel/pascal/kebab; drop non-alnum (after spaces);
    optionally uppercase whole token.
    """
    s = s.strip()
    
    if case_style == "preserve" or case_style == "none":
        # Only remove non-alphanumeric characters, keep original case
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", s)
        # Remove leading/trailing underscores
        token = cleaned.strip("_")
        if to_upper:
            token = token.upper()
        return token
    
    # Convert any non-alphanumeric into space
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", s)
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
    "t.pages.faq.faqData[index].question"
]

print("Testing camelCase normalization:\n")
for s in test_strings:
    result_camel = normalize_token(s, "camel", False)
    result_preserve = normalize_token(s, "preserve", False)
    result_snake = normalize_token(s, "snake", False)
    print(f"Input: '{s}'")
    print(f"  camel:    '{result_camel}'")
    print(f"  preserve: '{result_preserve}'")
    print(f"  snake:    '{result_snake}'")
    print()
