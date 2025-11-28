"""
TypeScript Object Extractor
============================

Extracts and parses object literals from TypeScript/JavaScript files.

Supports:
- export const name = { ... }
- export const name: Type = { ... }
- export default { ... }

Uses json5 for tolerant parsing when available, with fallback normalization.

Author: Josué Amaral
Date: 2025-11-24
"""

import re
import json
from typing import Any, Dict, List, Optional

# Optional json5 for better TS/JS object parsing
try:
    import json5  # type: ignore
    HAS_JSON5 = True
except ImportError:
    HAS_JSON5 = False


# Regex patterns for export statements
EXPORT_CONST_RE = re.compile(
    r"export\s+const\s+[\w$]+\s*(?::\s*[\w<>{}\[\]\s|,:'\"`.\-]+)?=\s*{",
    re.UNICODE
)
EXPORT_DEFAULT_RE = re.compile(r"export\s+default\s*{", re.UNICODE)

# Normalization patterns for fallback parser
COMMENT_LINE_RE = re.compile(r"//.*?$", re.MULTILINE)
COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")
UNQUOTED_KEY_RE = re.compile(r"(?P<prefix>[\{\s,])(?P<key>[A-Za-z_]\w*)\s*:", re.UNICODE)


def _find_matching_closing_brace(s: str, open_index: int) -> int:
    """
    Find the index of the matching '}' for '{' at open_index.
    
    Respects string literals and escape sequences.
    
    Args:
        s: Source text
        open_index: Index of opening '{'
        
    Returns:
        Index of matching '}', or -1 if not found
    """
    depth = 0
    in_str: Optional[str] = None
    esc = False

    i = open_index
    while i < len(s):
        ch = s[i]

        # Handle string escapes
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            i += 1
            continue

        # Detect string start
        if ch in ("'", '"', "`"):
            in_str = ch
            i += 1
            continue

        # Track brace depth
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return -1


def _parse_js_like_object(obj_literal: str) -> Optional[Dict[str, Any]]:
    """
    Parse a JavaScript-like object literal.
    
    Tries json5 first (handles single quotes, trailing commas, comments).
    Falls back to naive normalization for standard JSON parsing.
    
    Args:
        obj_literal: JavaScript object literal string
        
    Returns:
        Parsed dict, or None if parsing fails
    """
    # Try json5 (best option)
    if HAS_JSON5:
        try:
            return json5.loads(obj_literal)
        except Exception:
            pass

    # Fallback: normalize to JSON
    def _replace_backticks_no_interp(m):
        inner = m.group(1)
        # Escape for JSON
        inner = inner.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{inner}"'

    try:
        s = obj_literal
        # Convert template literals (no interpolation)
        s = re.sub(r"`([^`$]*)`", _replace_backticks_no_interp, s)
        # Remove comments
        s = COMMENT_BLOCK_RE.sub("", s)
        s = COMMENT_LINE_RE.sub("", s)
        # Quote unquoted keys
        s = UNQUOTED_KEY_RE.sub(lambda m: f'{m.group("prefix")}"{m.group("key")}":', s)
        # Convert single quotes to double quotes
        s = s.replace("\\'", "__SINGLE_QUOTE_ESC__")
        s = s.replace("'", '"')
        s = s.replace("__SINGLE_QUOTE_ESC__", "\\'")
        # Remove trailing commas
        s = TRAILING_COMMA_RE.sub(r"\1", s)
        return json.loads(s)
    except Exception:
        return None


def extract_top_level_objects_from_ts(text: str) -> List[Dict[str, Any]]:
    """
    Extract and parse top-level object literals from TypeScript/JavaScript.
    
    Matches:
        - export const name = { ... }
        - export const name: Type = { ... }
        - export default { ... }
    
    Args:
        text: TypeScript/JavaScript source code
        
    Returns:
        List of parsed object dicts
    """
    out: List[Dict[str, Any]] = []
    s = text.replace("\r\n", "\n")

    for regex in (EXPORT_CONST_RE, EXPORT_DEFAULT_RE):
        for m in regex.finditer(s):
            start_brace = s.find("{", m.start())
            if start_brace < 0:
                continue
                
            end_brace = _find_matching_closing_brace(s, start_brace)
            if end_brace < 0:
                continue

            literal = s[start_brace:end_brace + 1]
            parsed = _parse_js_like_object(literal)
            
            if isinstance(parsed, dict):
                out.append(parsed)

    return out


def guess_line_number(text: str, dot_path: str) -> Optional[int]:
    """
    Guess the line number where a dot-path key appears in source text.
    
    Strategy:
    1. Look for exact "key:" pattern at line start
    2. Fallback to any word-bounded occurrence of the key
    
    Args:
        text: Source file content
        dot_path: Dot-path like "a.b.c" (uses last segment)
        
    Returns:
        1-based line number, or None if not found
    """
    last_segment = dot_path.split(".")[-1].replace("[", "").replace("]", "")
    
    # Try exact pattern: "key": or key: at line start
    pattern1 = re.compile(
        r'(?m)^\s*(?:"|\')?%s(?:"|\')?\s*:' % re.escape(last_segment)
    )
    match = pattern1.search(text)
    if match:
        return text.count("\n", 0, match.start()) + 1
    
    # Fallback: any word-bounded occurrence
    pattern2 = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(last_segment))
    match2 = pattern2.search(text)
    if match2:
        return text.count("\n", 0, match2.start()) + 1
    
    return None


def js_like_dump(obj: Any, indent: int = 2) -> str:
    """
    Pretty-print object in JavaScript style (unquoted keys).
    
    Args:
        obj: Object to format
        indent: Indentation spaces per level
        
    Returns:
        Formatted string with JS-style syntax
    """
    def _fmt(v, level):
        sp = " " * (indent * level)
        if isinstance(v, dict):
            items = []
            for k, vv in v.items():
                key = str(k)  # Unquoted
                items.append(f'{sp}{" " * indent}{key}: {_fmt(vv, level + 1)}')
            return "{\n" + ",\n".join(items) + ("\n" + sp if items else "") + "}"
        if isinstance(v, list):
            items = []
            for vv in v:
                items.append(f'{sp}{" " * indent}{_fmt(vv, level + 1)}')
            return "[\n" + ",\n".join(items) + ("\n" + sp if items else "") + "]"
        if isinstance(v, str):
            return '"' + v.replace('"', '\\"') + '"'
        return str(v)
    
    return _fmt(obj, 0)
