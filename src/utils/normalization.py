"""
Normalization Utilities

Functions for normalizing text tokens extracted from files:
- Smart truncation with word boundary awareness
- Case style conversion (snake_case, camelCase, PascalCase, kebab-case)
- Standard HTML tag detection
- Path building utilities

Extracted from add/main.py for use in parameter/attribute extraction.

Author: Josué Amaral
Date: 2025-12-02
"""

import re
from typing import List, Optional


STANDARD_HTML_TAGS = {
    'html','head','title','base','link','meta','style','script','noscript',
    'body','section','nav','article','aside','h1','h2','h3','h4','h5','h6','header',
    'footer','address','main','p','hr','pre','blockquote','ol','ul','li','dl','dt','dd',
    'figure','figcaption','div','a','em','strong','small','s','cite','q','dfn','abbr','ruby',
    'rb','rt','rtc','rp','data','time','code','var','samp','kbd','sub','sup','i','b','u',
    'mark','bdi','bdo','span','br','wbr','ins','del','picture','source','img','iframe',
    'embed','object','param','video','audio','track','map','area','table','caption',
    'colgroup','col','tbody','thead','tfoot','tr','td','th','form','label','input',
    'button','select','datalist','optgroup','option','textarea','output','progress',
    'meter','fieldset','legend','details','summary','dialog','slot','template','canvas'
}


def is_standard_tag(name: str) -> bool:
    """Check if a tag name is a standard HTML tag."""
    return name.lower() in STANDARD_HTML_TAGS


def kept_prefix(file_root: str, stack: list[str], drop_standard: bool) -> list[str]:
    """
    Return [file_root] plus the stack up to the deepest NON-standard tag
    (when drop_standard=True). If none exists, just [file_root].
    If drop_standard=False, return [file_root] + full stack.
    """
    if not drop_standard:
        return [file_root] + stack

    # find deepest custom tag from right to left
    for i in range(len(stack) - 1, -1, -1):
        if not is_standard_tag(stack[i]):
            return [file_root] + stack[:i + 1]
    return [file_root]


# pylint: disable=too-many-return-statements  # Text truncation requires multiple early returns
def smart_truncate(text: str, limit: Optional[str], avoid_cut: bool) -> str:
    """
    Truncate text by char limit. If limit is 'all' or None -> return original.
    If avoid_cut=True, cut at the last whitespace boundary <= limit (when possible).
    """
    if not text or limit in (None, 'all', 'ALL', 'All'):
        return text
    try:
        n = int(limit)
    except Exception:  # pylint: disable=broad-exception-caught  # Invalid limit handling
        return text

    if n <= 0 or len(text) <= n:
        return text

    sub = text[:n]

    if not avoid_cut:
        return sub

    # If we ended already on whitespace, just strip trailing whitespace.
    if sub[-1].isspace():
        return sub.rstrip()

    # Find the last whitespace run before the cut and cut right before it.
    # This matches from the last whitespace up to the end of `sub`.
    m = re.search(r'\s+\S*$', sub, flags=re.UNICODE)
    if m:
        cut = m.start()
        if cut > 0:
            return sub[:cut].rstrip()

    # Fallback: no whitespace found in the window (a very long first word).
    return sub


def normalize_token(s: str, case_style: str, to_upper: bool) -> str:
    """
    Normalize a string to snake/camel/pascal/kebab/preserve.
    
    IMPORTANT: Only splits camelCase/PascalCase when there are OTHER separators present.
    If input contains ONLY alphanumeric characters (no spaces, dots, hyphens, etc.),
    it's treated as a single joined word and NOT split.
    
    Examples:
      - 'expandedItems' (no separators) → 'expandedItems' (preserved as-is)
      - 'expanded items test' (spaces) → 'expanded_items_test' (snake_case)
      - 'expanded.items.test' (dots) → 'expanded_items_test' (snake_case)
      - 'expandedItems to make test' (mixed) → 'expandedItems_to_make_test' (keep expandedItems)
    
    Steps:
    - Check if input contains separators (spaces, dots, hyphens, etc.)
    - If NO separators → keep as-is (don't split camelCase)
    - If HAS separators → replace separators with spaces, but DON'T split individual words
    - Apply case_style conversion only to the separator replacement
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
    
    # Check if input contains ANY non-alphanumeric characters (separators)
    has_separators = bool(re.search(r"[^0-9A-Za-z]", s))
    
    if not has_separators:
        # Input is pure alphanumeric (e.g., 'expandedItems', 'filteredFAQs', 'Category')
        # Don't split camelCase - treat as single joined word
        if to_upper:
            return s.upper()
        
        # For snake_case: lowercase everything (single word)
        if case_style == "snake" and s:
            return s.lower()
        
        # For kebab-case: lowercase everything (single word)
        if case_style == "kebab" and s:
            return s.lower()
        
        # For camelCase: lowercase first character
        # Special case: if it's already mixed case (e.g., 'expandedItems'), keep as-is
        # But if it's all uppercase (e.g., 'FAQ') or Title case (e.g., 'Category'), lowercase first char
        if case_style == "camel" and s:
            # Check if it's already proper camelCase (first char lowercase, has uppercase elsewhere)
            if s[0].islower() and any(c.isupper() for c in s[1:]):
                # Already camelCase like 'expandedItems'
                return s
            # Otherwise, lowercase the first character
            return s[0].lower() + s[1:].lower() if len(s) > 1 else s.lower()
        
        # For pascal, uppercase the first character
        if case_style == "pascal" and s:
            return s[0].upper() + s[1:] if len(s) > 1 else s.upper()
        
        return s
    
    # Input has separators - replace them but DON'T split camelCase words
    # Just replace non-alphanumeric with the appropriate separator for the case style
    
    if case_style == "snake":
        # Replace any non-alphanumeric with underscore
        token = re.sub(r"[^0-9A-Za-z]+", "_", s)
        token = token.strip("_")
        # snake_case should be all lowercase
        token = token.lower()
    elif case_style == "kebab":
        # Replace any non-alphanumeric with hyphen
        token = re.sub(r"[^0-9A-Za-z]+", "-", s)
        token = token.strip("-")
        # kebab-case should be all lowercase
        token = token.lower()
    elif case_style == "camel" or case_style == "pascal":
        # For camel/pascal with separators, we need to process each segment
        # Split by non-alphanumeric, then join back
        segments = re.split(r"[^0-9A-Za-z]+", s)
        segments = [seg for seg in segments if seg]
        
        if case_style == "camel" and segments:
            # First segment as-is (keep its case), rest capitalize first letter
            token = segments[0] + "".join(seg[:1].upper() + seg[1:] if len(seg) > 1 else seg.upper() for seg in segments[1:])
        elif case_style == "pascal" and segments:
            # All segments capitalize first letter
            token = "".join(seg[:1].upper() + seg[1:] if len(seg) > 1 else seg.upper() for seg in segments)
        else:
            token = "".join(segments)
    else:
        # default snake
        token = re.sub(r"[^0-9A-Za-z]+", "_", s)
        token = token.strip("_")

    if to_upper:
        token = token.upper()
    return token


def path_join(parts: List[str]) -> str:
    """Join path parts with dots, filtering out empty strings."""
    return ".".join([p for p in parts if p])
