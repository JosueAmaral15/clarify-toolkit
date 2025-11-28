"""JSON deduplication operations: dedupe, join_keys, eliminate_duplicates."""

from typing import List, Dict, Optional, Set, Any
from .types import Obj, JSONNode, freeze


def dedupe(node: JSONNode) -> JSONNode:
    """Remove duplicate (key, value) pairs in Obj nodes, recursively."""
    if isinstance(node, Obj):
        seen: Set = set()
        out = Obj()
        for k, v in node:
            v2 = dedupe(v)
            sig = (k, freeze(v2))
            if sig in seen:
                continue
            seen.add(sig)
            out.append((k, v2))
        return out
    if isinstance(node, list):
        return [dedupe(x) for x in node]
    return node


def merge_obj_values(values: List[Obj]) -> Obj:
    """Merge multiple Obj values by concatenating their pairs and joining keys."""
    merged_pairs: Obj = Obj()
    for o in values:
        merged_pairs.extend(o)
    return join_keys(merged_pairs)


def join_keys(node: JSONNode) -> JSONNode:
    """
    Combine duplicate keys in Obj nodes:
    - If all values are identical → keep one
    - If all values are Obj → merge them recursively
    - Otherwise → deduplicate and keep first unique value(s)
    """
    if isinstance(node, Obj):
        processed = [(k, join_keys(v)) for (k, v) in node]
        order: List[str] = []
        groups: Dict[str, List[JSONNode]] = {}
        for k, v in processed:
            if k not in groups:
                groups[k] = []; order.append(k)
            groups[k].append(v)

        out = Obj()
        for k in order:
            vals = groups[k]
            if len(vals) == 1:
                out.append((k, vals[0])); continue
            first_sig = freeze(vals[0])
            if all(freeze(v) == first_sig for v in vals[1:]):
                out.append((k, vals[0])); continue
            if all(isinstance(v, Obj) for v in vals):
                out.append((k, merge_obj_values(vals))); continue
            uniq: List[JSONNode] = []
            seen = set()
            for v in vals:
                sig = freeze(v)
                if sig in seen: continue
                seen.add(sig); uniq.append(v)
            out.append((k, uniq[0] if len(uniq) == 1 else uniq))
        return out
    if isinstance(node, list):
        return [join_keys(x) for x in node]
    return node


def eliminate_duplicates(node: JSONNode) -> JSONNode:
    """
    Remove globally duplicate values across the entire tree.
    Only the first occurrence of each unique value is kept.
    """
    seen: Set = set()
    
    def _visit(n: JSONNode) -> Optional[JSONNode]:
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen: continue
                seen.add(sig)
                out.append((k, v2))
            return out if out else None
        if isinstance(n, list):
            out: List[JSONNode] = []
            for v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen: continue
                seen.add(sig)
                out.append(v2)
            return out if out else None
        return n
    
    res = _visit(node)
    return res if res is not None else Obj()
