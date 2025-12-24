"""
JSON Translate Helpers
Helper functions for JSON/TS dictionary-driven text translation.

Refactored from src/app.py (Phase 3.2 - v2.9.114)
Original lines: 204-773 (excluding non-translation helpers)

Functions:
- _escape_variants_for_quotes: Handle quote/apostrophe variants
- _compile_value_union_regex: Build regex for dictionary values
- _apply_scoped_translation_tag_balanced: Tag-balanced translation
- mask_existing_placeholders: Protect existing placeholders
- unmask_existing_placeholders: Restore placeholders
- apply_scoped_translation: Apply translation in scope
- process_translate_file: Process file with translation
- load_translation_dict: Load dictionary from JSON/TS
- flatten_dict_paths: Flatten nested dict to paths
- translate_replace_texts: Forward/inverse text translation
- read_translation_dict: Read and parse dictionary file
"""

from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, Optional

from ..utils import read_text, write_text, safe_backup_file, parse_exclusion_patterns
from ..rewriter import find_object_block, ts_block_to_json_text


# ---------- Exclusion masking (skip-regex) ----------

# --- NEW: robust value → regex compiler for dictionary texts (handles quotes/apostrophes) ---

def _escape_variants_for_quotes(s: str) -> list[str]:
    """
    Return regex-safe variants of the same text so we can match values written with
    real quotes/apostrophes or with escaped forms (\" \').
    """
    # Base escaped
    base = re.escape(s)

    # If text contains double quotes, also allow escaped-double-quote variant
    variants = { base }
    if '"' in s:
        variants.add(re.escape(s.replace('"', '\\"')))
    if "'" in s:
        variants.add(re.escape(s.replace("'", "\\'")))

    # Also handle cases where the source file has "already-escaped" strings in TS/JS blocks
    # (e.g., We\\'re). We accept both one and two backslashes before quotes.
    if "\\\"" in s or "\\\'" in s:
        variants.add(re.escape(s.replace("\\\"", "\"").replace("\\\'", "'")))
    return list(variants)


def _compile_value_union_regex(value_to_key: dict[str, str]) -> re.Pattern:
    """
    Build a single alternation regex with named groups for each value.
    We sort by length (desc) to prefer the longest phrase first.
    """
    # Sort items by length of value, desc
    items = sorted(value_to_key.items(), key=lambda kv: len(kv[0]), reverse=True)

    parts = []
    group_names = []  # keep for debug if needed
    idx = 0
    for val, _key in items:
        if not val:
            continue
        # produce variants for quotes/apostrophes
        variants = _escape_variants_for_quotes(val)
        # fold multiple variants into a small alternation
        if len(variants) == 1:
            body = variants[0]
        else:
            body = "(?:" + "|".join(variants) + ")"
        gname = f"V{idx}"
        parts.append(f"(?P<{gname}>{body})")
        group_names.append(gname)
        idx += 1

    if not parts:
        # something degenerate but keep a harmless regex
        return re.compile(r"(?!x)x")

    # We're replacing *visible text* in scoped chunks, so we don't anchor with word boundaries.
    # The masking of {t.…} ensures we won't replace inside placeholders.
    big = "|".join(parts)
    return re.compile(big)


# ---------- JSON Translate — GUI helpers (scope, masking, backup) ----------

RE_PLACEHOLDER = re.compile(r"\{([A-Za-z_]\w*)(?:\.[A-Za-z0-9_]+)+\}")
_TAG_OPEN_RE  = re.compile(r"<\s*([A-Za-z][\w:-]*)[^>]*?>", re.DOTALL)
_TAG_CLOSE_RE = re.compile(r"</\s*([A-Za-z][\w:-]*)\s*>", re.DOTALL)


def _apply_scoped_translation_tag_balanced(content: str, fn_transform) -> str:
    """
    Tag-balanced scope:
      - Scan for tags <name ...> and </name>
      - When an opening tag is found, find its *matching* closing tag of the same name,
        counting nested occurrences of the same tag.
      - Apply fn_transform to the *inner* content (after open tag, before close tag).
      - Leave tags themselves untouched.
    We process outermost-to-innermost to ensure all text within elements is covered.
    """
    out = []
    i = 0
    n = len(content)

    while i < n:
        m_open = _TAG_OPEN_RE.search(content, i)
        if not m_open:
            out.append(content[i:])
            break

        # Write everything before the opening tag
        out.append(content[i:m_open.start()])

        tag_name = m_open.group(1)
        tag_open_end = m_open.end()

        # Find matching closing tag for tag_name (with nesting of the *same* tag)
        depth = 1
        j = tag_open_end
        while j < n and depth > 0:
            m_next_open  = _TAG_OPEN_RE.search(content, j)
            m_next_close = _TAG_CLOSE_RE.search(content, j)

            if not m_next_close and not m_next_open:
                # unmatched => give up and dump the rest
                out.append(content[m_open.start():])
                return "".join(out)

            # choose the nearest next tag of any kind
            candidates = [m for m in (m_next_open, m_next_close) if m]
            m_next = min(candidates, key=lambda m: m.start())

            if m_next.re is _TAG_OPEN_RE and m_next.group(1) == tag_name:
                depth += 1
                j = m_next.end()
                continue

            if m_next.re is _TAG_CLOSE_RE and m_next.group(1) == tag_name:
                depth -= 1
                j = m_next.end()
                if depth == 0:
                    # We have a full <tag> ... </tag> region
                    open_tag  = content[m_open.start():tag_open_end]
                    inner     = content[tag_open_end:m_next.start()]
                    close_tag = content[m_next.start():j]

                    out.append(open_tag)
                    out.append(fn_transform(inner))
                    out.append(close_tag)

                    i = j
                    break

                continue

            # A different tag; skip past it and continue searching
            j = m_next.end()

        # If loop exited without finding matching close (depth > 0), append rest and break
        if depth > 0:
            out.append(content[m_open.start():])
            break

    return "".join(out)


def mask_existing_placeholders(text: str) -> tuple[str, list[str]]:
    """Protect existing {root.path} so we don't touch/duplicate them."""
    guards: list[str] = []
    def _mask(m: re.Match) -> str:
        idx = len(guards); guards.append(m.group(0))
        return f"@@TREF{idx}@@"
    return RE_PLACEHOLDER.sub(_mask, text), guards


def unmask_existing_placeholders(text: str, guards: list[str]) -> str:
    """Restore protected placeholders."""
    for i, tok in enumerate(guards):
        text = text.replace(f"@@TREF{i}@@", tok)
    return text


def apply_scoped_translation(content: str,
                             start_rx: str,
                             end_rx: str,
                             fn_transform) -> str:
    """
    Apply 'fn_transform' ONLY to chunks between start/end delimiters.

    If delimiters look like generic HTML/JSX tags (start '<...>' / end '</...>'),
    we switch to a tag-balanced mode: pair opening tag <name ...> with </name>, honoring nesting
    of the *same* tag, and transform the entire element's *inner* content.

    Otherwise we fall back to simple flat pairing using the provided regexes.
    """
    start_rx = (start_rx or "").strip()
    end_rx = (end_rx or "").strip()

    if not start_rx or not end_rx:
        # no scope => transform whole file
        return fn_transform(content)

    # Detect "generic tag" mode
    generic_tag_mode = (
        start_rx == "<[^>]*?>" and end_rx == "</[^>]*?>"
    ) or (
        start_rx.startswith("<") and end_rx.startswith("</")
    )

    if generic_tag_mode:
        return _apply_scoped_translation_tag_balanced(content, fn_transform)

    # Fallback: flat regex pairing (previous behavior)
    start = re.compile(start_rx, re.DOTALL)
    end = re.compile(end_rx, re.DOTALL)

    out = []
    i = 0
    n = len(content)

    while i < n:
        mstart = start.search(content, i)
        if not mstart:
            out.append(content[i:])
            break
        out.append(content[i:mstart.start()])
        mend = end.search(content, mstart.end())
        if not mend:
            out.append(content[mstart.start():])
            break

        before = content[mstart.start():mstart.end()]
        inner  = content[mstart.end():mend.start()]
        after  = content[mend.start():mend.end()]

        out.append(before)
        out.append(fn_transform(inner))
        out.append(after)

        i = mend.end()

    return "".join(out)


def process_translate_file(path: str,
                           dictionary: dict,
                           root_alias: str,
                           start_rx: str,
                           end_rx: str,
                           make_backup: bool,
                           dont_override: bool,
                           inverse: bool,
                           exclude_patterns: list[str],
                           emit_export: bool = True,
                           preserve_uppercase: bool = False) -> tuple[bool, Optional[str]]:
    """
    Load file, translate (forward or inverse) honoring scope, options, and exclusions.
    Returns (changed, error_message).
    
    Args:
        path: File path to process
        dictionary: Translation dictionary
        root_alias: Root name for placeholders (e.g., 't')
        start_rx: Start delimiter regex
        end_rx: End delimiter regex
        make_backup: Create backup before modifying
        dont_override: Skip files with existing placeholders
        inverse: Inverse translation mode
        exclude_patterns: Patterns to exclude from translation
        emit_export: Emit export statement (for TS/JS)
        preserve_uppercase: Preserve uppercase in translations
        
    Returns:
        (changed, error_message) tuple
    """
    try:
        content = read_text(path)
    except Exception as e:
        return False, f"Could not read file: {e}"

    # If dont_override, skip files that already have placeholders
    if dont_override and RE_PLACEHOLDER.search(content):
        return False, None

    # Mask existing placeholders
    masked, guards = mask_existing_placeholders(content)

    # Mask exclusions if any
    if exclude_patterns:
        from ..utils import mask_exclusions, unmask_exclusions
        skip_rx_list = parse_exclusion_patterns(exclude_patterns)
        masked, exc_guards = mask_exclusions(masked, skip_rx_list)
    else:
        exc_guards = []

    # Define transformation function
    def transform_chunk(chunk: str) -> str:
        # Import here to avoid circular dependency
        from ..processors.code_aware_translator import CodeAwareJSONTranslator
        tr = CodeAwareJSONTranslator(dictionary, root_name=root_alias)
        if inverse:
            return tr.translate_refs_to_text(chunk)
        return tr.translate_text_to_refs(chunk)

    # Apply scoped translation
    translated = apply_scoped_translation(masked, start_rx, end_rx, transform_chunk)

    # Unmask exclusions
    if exc_guards:
        from ..utils import unmask_exclusions
        translated = unmask_exclusions(translated, exc_guards)

    # Unmask placeholders
    translated = unmask_existing_placeholders(translated, guards)

    # Check if changed
    if translated == content:
        return False, None

    # Make backup if requested
    if make_backup:
        try:
            safe_backup_file(path)
        except Exception as e:
            return False, f"Could not create backup: {e}"

    # Write result
    try:
        write_text(path, translated)
        return True, None
    except Exception as e:
        return False, f"Could not write file: {e}"


def load_translation_dict(path: str) -> Dict[str, Any]:
    """
    Load a dictionary file (JSON / TS/JS object literal).
    If it's TS/JS, we try to find the main { ... } and parse it to JSON.
    """
    text = read_text(path)
    if path.lower().endswith((".json",)):
        return json.loads(text)

    # Fallback: naive TS/JS extraction (re-usable from dedupe machinery below)
    start, end, block = find_object_block(text)
    block_json = ts_block_to_json_text(block)
    return json.loads(block_json)


def flatten_dict_paths(d: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    """
    Flatten a nested dict into {"a.b.c": "value"} for leaf strings.
    
    Args:
        d: Dictionary to flatten
        prefix: Prefix for keys
        
    Returns:
        Flattened dictionary with dot-notation paths
        
    Example:
        >>> flatten_dict_paths({"a": {"b": {"c": "value"}}})
        {"a.b.c": "value"}
    """
    out: Dict[str, str] = {}
    for k, v in (d or {}).items():
        kk = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten_dict_paths(v, kk))
        else:
            out[kk] = v if v is not None else ""
    return out


def translate_replace_texts(content: str,
                            dictionary: Dict[str, Any],
                            root_name: str = "t",
                            inverse: bool = False) -> str:
    """
    Wrapper around CodeAwareJSONTranslator.
    - forward  (inverse=False): text → {root.path}
    - inverse  (inverse=True):  {root.path} → text
    
    Args:
        content: Text content to translate
        dictionary: Translation dictionary
        root_name: Root name for placeholders (default: 't')
        inverse: If True, translate placeholders to text; if False, text to placeholders
        
    Returns:
        Translated content
    """
    from ..processors.code_aware_translator import CodeAwareJSONTranslator
    tr = CodeAwareJSONTranslator(dictionary, root_name=root_name)
    if inverse:
        return tr.translate_refs_to_text(content)
    return tr.translate_text_to_refs(content)


def read_translation_dict(path: str) -> Dict[str, Any]:
    """
    Read and parse translation dictionary from JSON or TS/JS file.
    
    Args:
        path: Path to dictionary file
        
    Returns:
        Parsed dictionary
    """
    text = read_text(path)
    if path.lower().endswith(".json"):
        return json.loads(text)
    # TS/JS object literal — find largest {…:…} block and coerce to JSON-ish
    _start, _end, block = find_object_block(text)
    block_json = ts_block_to_json_text(block)
    return json.loads(block_json)
