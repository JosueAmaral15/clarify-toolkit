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
# pylint: disable=broad-exception-caught  # Translation robustness
# pylint: disable=import-outside-toplevel  # Circular import avoidance
# pylint: disable=unused-argument  # API compatibility

from __future__ import annotations
import json
import re
from typing import Any, Callable, Dict, Optional, Sequence

from ..utils import read_text, write_text, safe_backup_file
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


def _merge_scoped_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return sorted, non-overlapping spans for one-pass transformation."""
    merged: list[list[int]] = []
    for start, end in sorted(spans):
        if start >= end:
            continue
        if not merged or start >= merged[-1][1]:
            merged.append([start, end])
            continue
        merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def _find_tag_balanced_inner_spans(
    content: str,
    start_rx: str = "<[^>]*?>",
    end_rx: str = "</[^>]*?>",
) -> list[tuple[int, int]]:
    """Find inner spans of matching balanced HTML/XML-like elements."""
    spans: list[tuple[int, int]] = []
    i = 0
    n = len(content)
    opening_pattern = (
        _TAG_OPEN_RE
        if start_rx == "<[^>]*?>"
        else re.compile(start_rx, re.DOTALL)
    )
    closing_pattern = (
        _TAG_CLOSE_RE
        if end_rx == "</[^>]*?>"
        else re.compile(end_rx, re.DOTALL)
    )

    while i < n:
        opening = opening_pattern.search(content, i)
        if not opening:
            break

        opening_tag = _TAG_OPEN_RE.fullmatch(opening.group(0))
        if not opening_tag:
            i = opening.end()
            continue

        tag_name = opening_tag.group(1)
        depth = 1
        cursor = opening.end()
        while cursor < n and depth > 0:
            next_open = _TAG_OPEN_RE.search(content, cursor)
            next_close = _TAG_CLOSE_RE.search(content, cursor)
            candidates = [match for match in (next_open, next_close) if match]
            if not candidates:
                return spans

            next_tag = min(candidates, key=lambda match: match.start())
            if next_tag.re is _TAG_OPEN_RE and next_tag.group(1) == tag_name:
                depth += 1
            elif next_tag.re is _TAG_CLOSE_RE and next_tag.group(1) == tag_name:
                depth -= 1
                if depth == 0:
                    if closing_pattern.fullmatch(next_tag.group(0)):
                        spans.append((opening.end(), next_tag.start()))
                    i = next_tag.end()
                    break
            cursor = next_tag.end()
        else:
            break

    return spans


def _find_scoped_inner_spans(content: str, start_rx: str, end_rx: str) -> list[tuple[int, int]]:
    """Find transformable regions for one delimiter pair."""
    start_rx = (start_rx or "").strip()
    end_rx = (end_rx or "").strip()
    if not start_rx or not end_rx:
        return [(0, len(content))]

    generic_tag_mode = (
        start_rx == "<[^>]*?>" and end_rx == "</[^>]*?>"
    ) or (
        start_rx.startswith("<") and end_rx.startswith("</")
    )
    if generic_tag_mode:
        return _find_tag_balanced_inner_spans(content, start_rx, end_rx)

    start = re.compile(start_rx, re.DOTALL)
    end = re.compile(end_rx, re.DOTALL)
    spans: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(content):
        opening = start.search(content, cursor)
        if not opening:
            break
        closing = end.search(content, opening.end())
        if not closing:
            break
        spans.append((opening.end(), closing.start()))
        cursor = closing.end()
    return spans


def _transform_scoped_spans(
    content: str,
    spans: list[tuple[int, int]],
    fn_transform: Callable[[str], str],
) -> str:
    """Transform each merged source span exactly once."""
    out: list[str] = []
    cursor = 0
    for start, end in _merge_scoped_spans(spans):
        out.append(content[cursor:start])
        out.append(fn_transform(content[start:end]))
        cursor = end
    out.append(content[cursor:])
    return "".join(out)


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
    spans = _find_tag_balanced_inner_spans(content)
    return _transform_scoped_spans(content, spans, fn_transform)


def mask_existing_placeholders(text: str) -> tuple[str, list[str]]:
    """Protect existing {root.path} so we don't touch/duplicate them."""
    guards: list[str] = []
    def _mask(m: re.Match) -> str:
        idx = len(guards)
        guards.append(m.group(0))
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
    return apply_scoped_translations(content, [(start_rx, end_rx)], fn_transform)


def apply_scoped_translations(
    content: str,
    scope_pairs: Sequence[tuple[str, str]],
    fn_transform: Callable[[str], str],
) -> str:
    """Apply a transform to the union of one or more delimiter-pair scopes.

    Regions are resolved against the original content and overlapping regions
    are merged, so no source text is transformed more than once. An empty list,
    or a pair with an empty delimiter, preserves the legacy whole-file behavior.
    """
    if not scope_pairs:
        return fn_transform(content)

    spans: list[tuple[int, int]] = []
    for start_rx, end_rx in scope_pairs:
        pair_spans = _find_scoped_inner_spans(content, start_rx, end_rx)
        if pair_spans == [(0, len(content))]:
            return fn_transform(content)
        spans.extend(pair_spans)

    return _transform_scoped_spans(content, spans, fn_transform)


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
                           preserve_uppercase: bool = False,
                           scope_pairs: Optional[Sequence[tuple[str, str]]] = None,
                           ) -> tuple[bool, Optional[str]]:
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
        scope_pairs: Optional list of delimiter pairs; overrides start/end when provided
        
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
        masked, exc_guards = mask_exclusions(masked, exclude_patterns)
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
    pairs = scope_pairs if scope_pairs is not None else [(start_rx, end_rx)]
    translated = apply_scoped_translations(masked, pairs, transform_chunk)

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
    _, _, block = find_object_block(text)
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
