"""Core data types for JSON Rewriter with duplicate key preservation."""
# pylint: disable=duplicate-code  # Type definitions shared with other modules

import json
from typing import Union, Any, List, Tuple


class Obj(list):
    """Object represented as list [(key, value), ...], preserving order and duplicate keys."""


JSONNode = Union[Obj, list, dict, str, int, float, bool, None]


def parse_json_preserving_duplicates_text(text: str) -> JSONNode:
    """Parse JSON preserving duplicate keys as Obj (list of tuples)."""
    def _hook(pairs: List[Tuple[str, Any]]) -> Obj:
        return Obj(pairs)
    return json.loads(text, object_pairs_hook=_hook)


def freeze(node: JSONNode) -> Any:
    """Convert node to immutable form for hashing/comparison."""
    if isinstance(node, Obj):
        return tuple((k, freeze(v)) for k, v in node)
    if isinstance(node, dict):
        return tuple(sorted((k, freeze(v)) for k, v in node.items()))
    if isinstance(node, list):
        return tuple(freeze(x) for x in node)
    return node
