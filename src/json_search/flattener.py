"""
JSON Flattener
==============

Converts nested JSON structures to flat dot-path notation for efficient searching.

Example:
    Input:  {"a": {"b": {"c": 1}}}
    Output: {"a.b.c": 1}

Author: Josué Amaral
Date: 2025-11-24
"""

from typing import Any, Dict, Optional


def flatten_object(obj: Any, prefix: str = "", out: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Flatten a nested dict into dot-paths.
    
    Args:
        obj: The object to flatten (dict, list, or primitive)
        prefix: Current path prefix (used in recursion)
        out: Accumulator dict (used in recursion)
    
    Returns:
        Dictionary mapping dot-paths to values
        
    Example:
        >>> flatten_object({"a": {"b": 1, "c": 2}})
        {"a.b": 1, "a.c": 2}
    """
    if out is None:
        out = {}
        
    if isinstance(obj, dict):
        for k, v in obj.items():
            next_key = f"{prefix}.{k}" if prefix else k
            flatten_object(v, next_key, out)
    elif isinstance(obj, list):
        # Flatten list items with array indices
        for i, item in enumerate(obj):
            next_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
            flatten_object(item, next_key, out)
    else:
        # Primitive value - store at current path
        out[prefix] = obj
        
    return out
