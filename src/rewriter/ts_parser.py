"""TypeScript/JavaScript parser: find and extract object blocks from TS/JS files."""
# pylint: disable=multiple-statements  # Intentional compact parser state machine

import re
from typing import Optional, Tuple, List


def strip_bom(s: str) -> str:
    """Remove BOM (Byte Order Mark) from beginning of string."""
    return s.lstrip("\ufeff")


def scan_find_next_lbrace(s: str, pos: int) -> int:
    """Find next '{' in string, skipping over comments and strings."""
    i, n = pos, len(s)
    in_str = False; q = ""; esc = False; in_line = False; in_block = False
    while i < n:
        ch = s[i]; nxt = s[i+1] if i+1 < n else ""
        if in_line:
            if ch == "\n": in_line = False
            i += 1; continue
        if in_block:
            if ch == "*" and nxt == "/": in_block = False; i += 2; continue
            i += 1; continue
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: in_str = False
            i += 1; continue
        if ch == "/" and nxt == "/": in_line = True; i += 2; continue
        if ch == "/" and nxt == "*": in_block = True; i += 2; continue
        if ch in ("'", '"', "`"): in_str = True; q = ch; i += 1; continue
        if ch == "{": return i
        i += 1
    return -1


def extract_balanced_from(s: str, lbrace_idx: int) -> Optional[Tuple[int, int, str]]:
    """Extract balanced {...} block starting at lbrace_idx."""
    i, n = lbrace_idx, len(s)
    in_str = False; q = ""; esc = False; in_line = False; in_block = False
    depth = 0; start = None
    while i < n:
        ch = s[i]; nxt = s[i+1] if i+1 < n else ""
        if in_line:
            if ch == "\n": in_line = False
            i += 1; continue
        if in_block:
            if ch == "*" and nxt == "/": in_block = False; i += 2; continue
            i += 1; continue
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: in_str = False
            i += 1; continue
        if ch == "/" and nxt == "/": in_line = True; i += 2; continue
        if ch == "/" and nxt == "*": in_block = True; i += 2; continue
        if ch in ("'", '"', "`"): in_str = True; q = ch; i += 1; continue

        if ch == "{":
            if depth == 0: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                end = i + 1
                return start, end, s[start:end]
        i += 1
    return None


def find_object_block(raw: str) -> Tuple[int, int, str]:
    """
    Find the main object block in TS/JS source.
    Tries 'export default {...}' first, then '= {...}', then largest block with colons.
    """
    s = strip_bom(raw)
    m = re.search(r'\bexport\s+default\b', s)
    if m:
        lb = scan_find_next_lbrace(s, m.end())
        if lb != -1:
            ext = extract_balanced_from(s, lb)
            if ext and ":" in ext[2]:
                return ext
    for m in re.finditer(r'=', s):
        lb = scan_find_next_lbrace(s, m.end())
        if lb != -1:
            ext = extract_balanced_from(s, lb)
            if ext and ":" in ext[2]:
                return ext
    # fallback: largest with many colons
    blocks = []
    i = s.find("{")
    while i != -1:
        ext = extract_balanced_from(s, i)
        if not ext: break
        blocks.append(ext)
        i = s.find("{", ext[1])
    if not blocks:
        raise ValueError("Could not find a {…} block.")
    blocks.sort(key=lambda t: (t[2].count(":"), len(t[2])), reverse=True)
    return blocks[0]


def strip_comments_code(s: str) -> str:
    """Remove comments (// and /* */) from code while preserving strings."""
    out = []
    i = 0; n = len(s)
    in_str = False; q = ""; esc = False; in_line = False; in_block = False
    while i < n:
        ch = s[i]; nxt = s[i+1] if i+1 < n else ""
        if in_line:
            if ch == "\n": in_line = False; out.append(ch)
            i += 1; continue
        if in_block:
            if ch == "*" and nxt == "/": in_block = False; i += 2; continue
            i += 1; continue
        if in_str:
            out.append(ch)
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: in_str = False
            i += 1; continue
        if ch == "/" and nxt == "/": in_line = True; i += 2; continue
        if ch == "/" and nxt == "*": in_block = True; i += 2; continue
        if ch in ("'", '"', "`"):
            in_str = True; q = ch; out.append(ch); i += 1; continue
        out.append(ch); i += 1
    return "".join(out)


def lift_strings_to_placeholders(s: str) -> tuple[str, List[str]]:
    """Replace string literals with placeholders to protect them during transformation."""
    import json  # pylint: disable=import-outside-toplevel  # Optional JSON dependency
    out, tokens = [], []
    i = 0; n = len(s); start = 0
    while i < n:
        ch = s[i]
        if ch in ("'", '"', "`"):
            out.append(s[start:i])
            q = ch; i += 1; buf = []; esc = False
            while i < n:
                c = s[i]
                if esc: buf.append(c); esc = False; i += 1; continue
                if c == "\\": buf.append(c); esc = True; i += 1; continue
                if c == q: i += 1; break
                buf.append(c); i += 1
            content = "".join(buf)
            tokens.append(json.dumps(content, ensure_ascii=False))
            out.append(f"@@S{len(tokens)-1}@@")
            start = i
        else:
            i += 1
    out.append(s[start:])
    return "".join(out), tokens


def restore_placeholders(s: str, tokens: List[str]) -> str:
    """Restore string literals from placeholders."""
    for i, t in enumerate(tokens):
        s = s.replace(f"@@S{i}@@", t)
    return s


def quote_bare_and_numeric_keys(s: str) -> str:
    """Convert bare identifiers and numeric keys to quoted keys for JSON compatibility."""
    ident = r'[A-Za-z_$][A-Za-z0-9_$]*'
    s = re.sub(r'([{\[,]\s*)(' + ident + r')(\s*:)', r'\1"\2"\3', s)
    s = re.sub(r'([{\[,]\s*)(\d+)(\s*:)', r'\1"\2"\3', s)
    return s


def remove_trailing_commas(s: str) -> str:
    """Remove trailing commas before closing braces/brackets."""
    return re.sub(r',(\s*[}\]])', r'\1', s)


def ts_block_to_json_text(block: str) -> str:
    """
    Convert a TS/JS object literal block into valid JSON text.
    Pipeline: strip comments → lift strings → quote keys → remove trailing commas → restore strings.
    """
    b = strip_comments_code(block)
    no_str, tokens = lift_strings_to_placeholders(b)
    with_keys = quote_bare_and_numeric_keys(no_str)
    no_trailing = remove_trailing_commas(with_keys)
    return restore_placeholders(no_trailing, tokens)
