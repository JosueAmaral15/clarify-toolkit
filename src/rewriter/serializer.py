"""Serialize JSON structures to TypeScript/JavaScript format."""

import re
import json
from typing import Any, Optional, List
from .types import Obj, JSONNode


_ident_re = re.compile(r'^[A-Za-z_$][A-Za-z0-9_$]*$')
_num_re = re.compile(r'^\d+$')


def esc_single(s: str) -> str:
    """Escape string for single-quoted TS/JS strings."""
    return (s.replace('\\', '\\\\')
             .replace("'", "\\'")
             .replace('\r', '\\r')
             .replace('\n', '\\n')
             .replace('\t', '\\t'))


def dump_ts_scalar(x: Any) -> str:
    """Serialize scalar value to TS/JS format."""
    if isinstance(x, str): 
        return "'" + esc_single(x) + "'"
    if x is True: 
        return "true"
    if x is False: 
        return "false"
    if x is None: 
        return "null"
    return json.dumps(x, ensure_ascii=False)


def dump_ts_key(k: str) -> str:
    """
    Serialize object key to TS/JS format.
    Simple identifiers and numbers don't need quotes.
    """
    if _ident_re.match(k) or _num_re.match(k):
        return k
    return "'" + esc_single(k) + "'"


def dump_ts_obj(obj: Obj, indent: Optional[int], level: int) -> str:
    """Serialize Obj to TS/JS object format with optional indentation."""
    if not obj: 
        return "{}"
    
    if indent is None or indent <= 0:
        # Compact format (no line breaks)
        parts = ["{"]
        parts.extend(("," if i else "") + dump_ts_key(k) + ":" + dump_ts_node(v, indent, level)
                     for i, (k, v) in enumerate(obj))
        parts.append("}")
        return "".join(parts)
    
    # Pretty format (with indentation)
    ind = " " * indent
    parts: List[str] = ["{\n"]
    for i, (k, v) in enumerate(obj):
        if i: 
            parts.append(",\n")
        parts.append(ind * (level + 1) + dump_ts_key(k) + ": " + dump_ts_node(v, indent, level + 1))
    parts.append("\n" + ind * level + "}")
    return "".join(parts)


def dump_ts_array(arr: list, indent: Optional[int], level: int) -> str:
    """Serialize array to TS/JS format with optional indentation."""
    if not arr: 
        return "[]"
    
    if indent is None or indent <= 0:
        # Compact format
        parts = ["["]
        parts.extend(("," if i else "") + dump_ts_node(v, indent, level)
                     for i, v in enumerate(arr))
        parts.append("]")
        return "".join(parts)
    
    # Pretty format
    ind = " " * indent
    parts: List[str] = ["[\n"]
    for i, v in enumerate(arr):
        if i: 
            parts.append(",\n")
        parts.append(ind * (level + 1) + dump_ts_node(v, indent, level + 1))
    parts.append("\n" + ind * level + "]")
    return "".join(parts)


def dump_ts_node(node: JSONNode, indent: Optional[int], level: int) -> str:
    """Serialize any JSONNode to TS/JS format (polymorphic dispatcher)."""
    if isinstance(node, Obj): 
        return dump_ts_obj(node, indent, level)
    if isinstance(node, list): 
        return dump_ts_array(node, indent, level)
    return dump_ts_scalar(node)


def collapse_blank_lines(s: str) -> str:
    """Collapse multiple consecutive blank lines into one."""
    return re.sub(r'\n[ \t]*\n+', '\n', s)
