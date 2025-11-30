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


def exclude_numeric_keys(node: JSONNode) -> JSONNode:
    """
    Remove keys that are purely numeric (e.g., '0', '123', '456').
    Recursively processes Obj and list nodes.
    """
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # Skip if key is numeric
            if k.isdigit():
                continue
            # Recursively process value
            out.append((k, exclude_numeric_keys(v)))
        return out
    if isinstance(node, list):
        return [exclude_numeric_keys(x) for x in node]
    return node


def skip_empty_values(node: JSONNode) -> JSONNode:
    """
    Remove empty values from JSON structure.
    
    Empty values include:
    - Empty strings: ""
    - None/null
    - Empty lists: []
    - Empty dicts/Obj: {}
    - Whitespace-only strings: "   "
    
    Recursively processes Obj and list nodes.
    """
    def is_empty(value: Any) -> bool:
        """Check if value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, Obj)):
            return len(value) == 0
        if isinstance(value, dict):
            return len(value) == 0
        return False
    
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # Recursively process value first
            processed = skip_empty_values(v)
            # Skip if empty
            if is_empty(processed):
                continue
            out.append((k, processed))
        return out
    if isinstance(node, list):
        out = []
        for item in node:
            processed = skip_empty_values(item)
            if not is_empty(processed):
                out.append(processed)
        return out
    return node


def avoid_duplicate_child_keys(node: JSONNode) -> JSONNode:
    """
    Avoid child keys with the same name as parent keys.
    
    Example:
        { pages: { home: { home: { home: 'Welcome' } } } }
    Becomes:
        { pages: { home: 'Welcome' } }
    
    If both parent and child are objects, they are merged.
    If values conflict, parent value is kept (child ignored).
    
    Recursively processes Obj and list nodes.
    """
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # First, recursively process the value
            processed_v = avoid_duplicate_child_keys(v)
            
            # Check if the value is an Obj with a single key that matches current key
            if isinstance(processed_v, Obj) and len(processed_v) == 1:
                child_key, child_val = processed_v[0]
                if child_key == k:
                    # Found duplicate: t.pages.home.home
                    # If both are objects, merge them
                    if isinstance(child_val, Obj):
                        # Recursively check child_val for more duplicates
                        final_val = avoid_duplicate_child_keys(child_val)
                        out.append((k, final_val))
                    else:
                        # Child is not an object, just use it directly
                        out.append((k, child_val))
                    continue
            
            # No duplicate found, keep as is
            out.append((k, processed_v))
        return out
    if isinstance(node, list):
        return [avoid_duplicate_child_keys(x) for x in node]
    return node


def remove_duplicate_array_values(node: JSONNode, consecutive_only: bool = False) -> JSONNode:
    """
    Remove duplicate values from arrays in JSON structure.
    
    Args:
        node: JSON node to process
        consecutive_only: If True, only removes consecutive duplicates (e.g., ['a','a','b'] → ['a','b'])
                         If False, removes all duplicates (e.g., ['a','b','a'] → ['a','b'])
    
    Examples:
        consecutive_only=True:  ['a', 'a', 'b', 'c', 'c'] → ['a', 'b', 'c']
        consecutive_only=False: ['a', 'b', 'a', 'c', 'b'] → ['a', 'b', 'c']
    
    Recursively processes Obj and list nodes.
    Uses set-like behavior to preserve first occurrence.
    """
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # Recursively process value
            out.append((k, remove_duplicate_array_values(v, consecutive_only)))
        return out
    
    if isinstance(node, list):
        if consecutive_only:
            # Remove only consecutive duplicates
            if not node:
                return []
            result = [node[0]]
            for i in range(1, len(node)):
                # Compare with previous item using freeze for consistent comparison
                if freeze(node[i]) != freeze(node[i-1]):
                    result.append(remove_duplicate_array_values(node[i], consecutive_only))
                # If equal to previous, skip it (don't add to result)
            return result
        else:
            # Remove all duplicates (set-like behavior)
            seen = set()
            result = []
            for item in node:
                processed = remove_duplicate_array_values(item, consecutive_only)
                sig = freeze(processed)
                if sig not in seen:
                    seen.add(sig)
                    result.append(processed)
            return result
    
    return node


def enforce_consistent_case(node: JSONNode, target_case: str = 'camel', warn_inconsistencies: bool = True) -> tuple[JSONNode, List[str]]:
    """
    Enforce consistent case style on all JSON keys.
    
    Args:
        node: JSON node to process
        target_case: Target case style - 'camel', 'pascal', 'snake', or 'kebab' (default: 'camel')
        warn_inconsistencies: If True, collect warnings for keys that deviate from target case
    
    Returns:
        Tuple of (processed_node, warnings_list)
        
    Examples:
        Input:  { "homeTitle": "A", "AboutPage": "B", "user_name": "C" }
        Output: { "homeTitle": "A", "aboutPage": "B", "userName": "C" }
        Warnings: ["Key 'AboutPage' converted to 'aboutPage'", "Key 'user_name' converted to 'userName'"]
    """
    import re
    
    warnings = []
    
    def split_words(s: str) -> List[str]:
        """Split identifier into words."""
        # Handle kebab-case and snake_case
        s = s.replace('-', ' ').replace('_', ' ')
        # Handle camelCase and PascalCase
        s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s)
        return [w for w in s.split() if w]
    
    def to_camel(s: str) -> str:
        words = split_words(s)
        if not words:
            return s
        return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    
    def to_pascal(s: str) -> str:
        words = split_words(s)
        if not words:
            return s
        return ''.join(w.capitalize() for w in words)
    
    def to_snake(s: str) -> str:
        words = split_words(s)
        return '_'.join(w.lower() for w in words)
    
    def to_kebab(s: str) -> str:
        words = split_words(s)
        return '-'.join(w.lower() for w in words)
    
    converters = {
        'camel': to_camel,
        'pascal': to_pascal,
        'snake': to_snake,
        'kebab': to_kebab
    }
    
    converter = converters.get(target_case)
    if not converter:
        warnings.append(f"Unknown case style '{target_case}', defaulting to camelCase")
        converter = to_camel
    
    def process_node(n: JSONNode, path: str = "") -> JSONNode:
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                # Convert key
                new_key = converter(k)
                
                # Warn if changed
                if warn_inconsistencies and new_key != k:
                    key_path = f"{path}.{k}" if path else k
                    warnings.append(f"Key '{key_path}' converted from '{k}' to '{new_key}'")
                
                # Recursively process value
                new_path = f"{path}.{new_key}" if path else new_key
                processed_v = process_node(v, new_path)
                out.append((new_key, processed_v))
            return out
        
        if isinstance(n, list):
            return [process_node(item, f"{path}[]") for item in n]
        
        return n
    
    processed = process_node(node)
    return processed, warnings


def normalize_escaping(node: JSONNode) -> JSONNode:
    """
    Normalize excessive escaping in string values (Task #22 - v2.9.10).
    
    Detects patterns like:
    - \\\\\\' (3+ backslashes before quote) → \\'
    - \\\\\\\\" (3+ backslashes before double quote) → \\\\"
    
    Examples:
        "value": "don\\\\\\'t" → "value": "don\\'t"
        "value": "say \\\\\\"hi\\\\\\"" → "value": "say \\"hi\\""
    
    Note: \\' (single backslash + quote) is kept unchanged as it's valid.
    
    Args:
        node: JSONNode tree to process
    
    Returns:
        Processed JSONNode with normalized escaping
    """
    import re
    
    def normalize_string(s: str) -> str:
        """Normalize excessive backslash escaping in a single string."""
        if not isinstance(s, str):
            return s
        
        # Pattern 1: Detect 2+ backslashes before single quote → normalize to \'
        # Match: \\\\' or \\\\\' or \\\\\\' etc. → replace with \'
        pattern1 = r"\\{2,}'"
        normalized = re.sub(pattern1, r"\'", s)
        
        # Pattern 2: Detect 2+ backslashes before double quote → normalize to \"
        # Match: \\\\" or \\\\\\" or \\\\\\\\" etc. → replace with \"
        pattern2 = r'\\{2,}"'
        normalized = re.sub(pattern2, r'\"', normalized)
        
        return normalized
    
    def process_node(n: JSONNode) -> JSONNode:
        """Recursively process node and normalize string escaping."""
        if isinstance(n, str):
            return normalize_string(n)
        
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                # Normalize both key and value
                new_k = normalize_string(k) if isinstance(k, str) else k
                new_v = process_node(v)
                out.append((new_k, new_v))
            return out
        
        if isinstance(n, list):
            return [process_node(item) for item in n]
        
        # For other types (int, float, bool, None), return as-is
        return n
    
    return process_node(node)
