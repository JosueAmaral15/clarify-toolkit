"""
Query Parser
============

Parses and executes search queries against flattened JSON index.

Supports:
- Composite queries: "base.path,sub.path"
- Case sensitivity toggle
- Whole word matching
- Regular expressions
- Multiple file/occurrence support

Author: Josué Amaral
Date: 2025-11-24
"""

import re
from typing import Tuple, Optional, List, Dict, Any

FlatIndex = Dict[str, List[Dict[str, Any]]]  # path -> [{"file": str, "value": Any, "line": int}]


def parse_composite_query(raw: str) -> Tuple[str, Optional[str]]:
    """
    Parse a composite query of the form "base.path,sub.path".

    The left side is the base path; optional right side is appended subpath.
    Leading 't.' or 't' is stripped from the base side for convenience.

    Args:
        raw: Query string (e.g., "t.pages.testFormatDetail,hero.title")

    Returns:
        Tuple of (base_path, sub_path)

    Examples:
        >>> parse_composite_query("t.pages.home,title")
        ("pages.home", "title")

        >>> parse_composite_query("auth.login")
        ("auth.login", None)
    """
    q = raw.strip()
    idx = q.find(",")

    if idx >= 0:
        left = q[:idx].strip()
        right = q[idx + 1:].strip()
    else:
        left, right = q, None

    # Remove optional 't' or 't.' prefix (common convention)
    if left.startswith("t."):
        left = left[2:]
    elif left == "t":
        left = ""

    base_path = left
    sub_path = right if (right and len(right) > 0) else None

    return base_path, sub_path


def match_with_options(candidate: str, needle: str,
                       case_sensitive: bool, whole_word: bool, regex: bool) -> bool:
    """
    Apply case/whole-word/regex rules to match a candidate path.

    Args:
        candidate: The path to test (e.g., "pages.home.title")
        needle: The search pattern
        case_sensitive: Whether to match case exactly
        whole_word: Whether to match whole segments only (dot-separated)
        regex: Whether needle is a regular expression

    Returns:
        True if candidate matches needle with given options
    """
    if regex:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.search(needle, candidate, flags) is not None
        except re.error:
            return False

    hay = candidate if case_sensitive else candidate.lower()
    ndl = needle if case_sensitive else needle.lower()

    if whole_word:
        # Whole word: compare token-by-token (dot-separated)
        tokens = hay.split(".")
        return ndl in tokens

    return ndl in hay


def resolve_query(flat: FlatIndex, raw_query: str,
                  case_sensitive: bool, whole_word: bool, regex: bool):
    """
    Resolve a query against the flattened index.

    Returns exact matches and suggestions based on search options.

    Args:
        flat: Flattened index mapping paths to metadata
        raw_query: User query string
        case_sensitive: Match case exactly
        whole_word: Match whole path segments only
        regex: Treat query as regular expression

    Returns:
        Tuple of (exact_matches, suggestions)
        - exact_matches: List of dicts with "path", "file", "value", "line"
        - suggestions: List of dicts with "path", "file", "line"
    """
    base_path, sub_path = parse_composite_query(raw_query)
    needle = f"{base_path}.{sub_path}" if sub_path else base_path

    exact: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []

    # Scan entire index
    for key, metas in flat.items():
        matched = match_with_options(key, needle, case_sensitive, whole_word, regex) if needle else False

        if matched:
            # Exact match - include all occurrences
            for meta in metas:
                exact.append({
                    "path": key,
                    "file": meta["file"],
                    "value": meta["value"],
                    "line": meta.get("line")
                })
        else:
            # Suggestions: keys that start with base_path
            if base_path and key.startswith(base_path):
                for meta in metas:
                    suggestions.append({
                        "path": key,
                        "file": meta["file"],
                        "line": meta.get("line")
                    })

    # Deduplication
    def _dedup(items):
        seen = set()
        out = []
        for it in items:
            sig = (it["path"], it["file"], it.get("line"))
            if sig not in seen:
                seen.add(sig)
                out.append(it)
        return out

    exact = _dedup(exact)[:200]  # Limit to 200 results
    suggestions = _dedup(suggestions)[:200]

    return exact, suggestions


def resolve_query_by_value(flat: FlatIndex, search_value: str,
                            case_sensitive: bool, regex: bool) -> List[Dict[str, Any]]:
    """
    Search for entries whose values match the search pattern.

    Args:
        flat: Flattened index mapping paths to metadata
        search_value: Value pattern to search for
        case_sensitive: Match case exactly
        regex: Treat search_value as regular expression

    Returns:
        List of dicts with "key", "file", "value", "line", "match_type"

    Examples:
        >>> flat = {"pages.home.title": [{"file": "en.json", "value": "Welcome", "line": 5}]}
        >>> resolve_query_by_value(flat, "Welcome", True, False)
        [{"key": "pages.home.title", "value": "Welcome", "file": "en.json", "line": 5, "match_type": "value"}]
    """
    results: List[Dict[str, Any]] = []

    for key_path, metadata_list in flat.items():
        for metadata in metadata_list:
            value = metadata.get("value")

            # Convert value to string for matching (handle None specially)
            if value is None:
                value_str = "None"
            else:
                value_str = str(value)

            # Apply matching rules
            matched = False
            if regex:
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    matched = re.search(search_value, value_str, flags) is not None
                except re.error:
                    matched = False
            else:
                # Simple substring match
                if case_sensitive:
                    matched = search_value in value_str
                else:
                    matched = search_value.lower() in value_str.lower()

            if matched:
                results.append({
                    "key": key_path,
                    "value": value,
                    "file": metadata["file"],
                    "line": metadata.get("line"),
                    "match_type": "value"
                })

    # Limit results to 200
    return results[:200]


def resolve_query_with_mode(flat: FlatIndex, search_key: str, search_value: str,
                             search_mode: str, case_sensitive: bool, regex: bool) -> List[Dict[str, Any]]:
    """
    Resolve query based on search mode (key, value, or both).

    Args:
        flat: Flattened index
        search_key: Key pattern to search for
        search_value: Value pattern to search for
        search_mode: "key", "value", or "both"
        case_sensitive: Match case exactly
        regex: Treat patterns as regular expressions

    Returns:
        Unified list of results with match_type indicator

    Examples:
        >>> resolve_query_with_mode(flat, "title", "", "key", False, False)
        # Returns all keys containing "title"

        >>> resolve_query_with_mode(flat, "", "Welcome", "value", True, False)
        # Returns all entries with value = "Welcome"

        >>> resolve_query_with_mode(flat, "title", "Home", "both", False, False)
        # Returns keys with "title" OR values with "Home"
    """
    results: List[Dict[str, Any]] = []

    # Mode 1: Key only
    if search_mode == "key":
        if search_key:
            exact, _ = resolve_query(flat, search_key, case_sensitive, False, regex)
            for match in exact:
                # Normalize: resolve_query returns "path", we need "key"
                result = {
                    "key": match.get("path", match.get("key", "")),
                    "value": match.get("value"),
                    "file": match.get("file"),
                    "line": match.get("line"),
                    "match_type": "key"
                }
                results.append(result)

    # Mode 2: Value only
    elif search_mode == "value":
        if search_value:
            value_results = resolve_query_by_value(flat, search_value, case_sensitive, regex)
            results.extend(value_results)

    # Mode 3: Both (key OR value)
    else:  # "both"
        # Search keys
        if search_key:
            exact, _ = resolve_query(flat, search_key, case_sensitive, False, regex)
            for match in exact:
                result = {
                    "key": match.get("path", match.get("key", "")),
                    "value": match.get("value"),
                    "file": match.get("file"),
                    "line": match.get("line"),
                    "match_type": "key"
                }
                results.append(result)

        # Search values
        if search_value:
            value_results = resolve_query_by_value(flat, search_value, case_sensitive, regex)
            results.extend(value_results)

    # Deduplicate results (same key + file + line)
    seen = set()
    deduped = []
    for result in results:
        signature = (result.get("key"), result.get("file"), result.get("line"))
        if signature not in seen:
            seen.add(signature)
            deduped.append(result)

    return deduped[:200]  # Limit to 200 results
