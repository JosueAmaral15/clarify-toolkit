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
    Normalize a string to snake/camel/pascal/kebab/preserve; drop non-alnum (after spaces);
    optionally uppercase whole token.
    Steps:
    - Lowercase for snake/kebab; for camel/pascal, lowercase then apply.
    - Replace non-letter/digit with space; split words; rebuild.
    - For 'preserve' mode, keeps original case intact (only removes special chars).
    - Splits camelCase/PascalCase into words before applying conversion.
    """
    # remove quotes around e.g. "Today's Practice" if present (we get raw value text usually)
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
    # Examples: "expandedItems" → "expanded Items", "FAQs" → "FAQs", "faqData" → "faq Data"
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


def path_join(parts: List[str]) -> str:
    """Join path parts with dots, filtering out empty strings."""
    return ".".join([p for p in parts if p])
