"""Main JSON Rewriter coordinator with CRITICAL BUG FIX for data loss.

This module contains sanitize_keys_and_values with the fix that handles Obj type correctly.
"""

import re
import json
from typing import Optional, Dict, Any
from .types import Obj, JSONNode
from .ts_parser import find_object_block, ts_block_to_json_text
from .operations import dedupe, join_keys, eliminate_duplicates
from .serializer import dump_ts_node
from ..utils.file_utils import read_text


def sanitize_keys_and_values(obj: dict,
                             allow_numeric_keys: bool = False,
                             strip_leading_numeric_segment: bool = True,
                             drop_empty_values: bool = True) -> dict:
    """
    CRITICAL BUG FIX APPLIED: This function now handles both dict and Obj types correctly.
    
    - If drop_empty_values: remove entries whose value is '' (or whitespace-only).
    - If not allow_numeric_keys:
        • For keys like '1.abcd' → keep only 'abcd' (strip leading digits + dots).
        • For keys like '1234'   → drop the entire key.
    Applies recursively.
    """
    def clean_key(k: str) -> Optional[str]:
        if allow_numeric_keys:
            return k
        if re.fullmatch(r'\d+', k):
            return None  # drop pure-numeric key
        if strip_leading_numeric_segment and re.match(r'^\d+(\.|_)+', k):
            # remove leading digits and separators like "123." or "123_"
            k2 = re.sub(r'^\d+(?:[._])+', '', k)
            return k2 or None
        return k

    def walk(v):
        # Handle Obj type (list of key-value tuples used by JSON Rewriter)
        # *** THIS IS THE CRITICAL BUG FIX ***
        if isinstance(v, Obj):
            out = Obj()
            for k, x in v:
                nk = clean_key(k)
                if nk is None:
                    continue
                vx = walk(x)
                # empty-value culling for strings
                if drop_empty_values and isinstance(vx, str) and not vx.strip():
                    continue
                out.append((nk, vx))
            return out
        if isinstance(v, dict):
            out = {}
            for k, x in v.items():
                nk = clean_key(k)
                if nk is None:
                    continue
                vx = walk(x)
                # empty-value culling for strings
                if drop_empty_values and isinstance(vx, str) and not vx.strip():
                    continue
                out[nk] = vx
            return out
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v

    return walk(obj)


def ts_process_full_preserving(raw_full: str, indent: Optional[int], join: bool, elim: bool, normalize_esc: bool = False, convert_arrays: bool = False) -> str:
    """
    Complete pipeline: find TS/JS object block → parse → dedupe → join → eliminate → normalize escaping → array to object → serialize.
    
    Args:
        raw_full: Full TS/JS file content
        indent: Indentation level (None or <=0 for compact)
        join: Apply join_keys operation
        elim: Apply eliminate_duplicates operation
        normalize_esc: Apply normalize_escaping operation (Task #22 - v2.9.10)
        convert_arrays: Apply array_to_object_conversion operation (Task #21 - v2.9.10)
    
    Returns:
        Processed file content (statistics are discarded here - use cli_dedupe for full stats)
    """
    start, end, block = find_object_block(raw_full)
    block_json = ts_block_to_json_text(block)
    
    from .types import parse_json_preserving_duplicates_text
    node = parse_json_preserving_duplicates_text(block_json)
    
    # Apply operations (discard counters in this simplified function)
    node, _ = dedupe(node)
    if join:
        node, _ = join_keys(node)
    if elim:
        node, _ = eliminate_duplicates(node)
    if normalize_esc:
        node = normalize_escaping(node)
    if convert_arrays:
        node = array_to_object_conversion(node)

    new_block = dump_ts_node(node, indent, 0)
    
    # Reconstruct full file
    before = raw_full[:start]
    after = raw_full[end:]
    return before + new_block + after


def load_translation_dict(path: str) -> Dict[str, Any]:
    """
    Load a dictionary file (JSON / TS/JS object literal).
    If it's TS/JS, we try to find the main { ... } and parse it to JSON.
    """
    text = read_text(path)
    if path.lower().endswith((".json",)):
        return json.loads(text)

    # Fallback: naive TS/JS extraction
    start, end, block = find_object_block(text)
    block_json = ts_block_to_json_text(block)
    return json.loads(block_json)
