"""JSON deduplication operations: dedupe, join_keys, eliminate_duplicates."""

from typing import List, Dict, Optional, Set, Any, Tuple
from .types import Obj, JSONNode, freeze


def dedupe(node: JSONNode) -> Tuple[JSONNode, int]:
    """Remove duplicate (key, value) pairs in Obj nodes, recursively.
    
    Returns:
        Tuple of (processed_node, removed_count)
    """
    removed_count = 0
    
    if isinstance(node, Obj):
        seen: Set = set()
        out = Obj()
        for k, v in node:
            v2, child_removed = dedupe(v)
            removed_count += child_removed
            sig = (k, freeze(v2))
            if sig in seen:
                removed_count += 1
                continue
            seen.add(sig)
            out.append((k, v2))
        return out, removed_count
    if isinstance(node, list):
        result = []
        for x in node:
            processed, child_removed = dedupe(x)
            removed_count += child_removed
            result.append(processed)
        return result, removed_count
    return node, 0


def merge_obj_values(values: List[Obj]) -> Tuple[Obj, int]:
    """Merge multiple Obj values by concatenating their pairs and joining keys.
    
    Returns:
        Tuple of (merged_result, removed_count)
    """
    merged_pairs: Obj = Obj()
    for o in values:
        merged_pairs.extend(o)
    return join_keys(merged_pairs)


def join_keys(node: JSONNode) -> Tuple[JSONNode, int]:
    """
    Combine duplicate keys in Obj nodes:
    - If all values are identical → keep one
    - If all values are Obj → merge them recursively
    - Otherwise → deduplicate and keep first unique value(s)
    
    Returns:
        Tuple of (processed_node, merged_count) - always 0 for removed_count
    """
    removed_count = 0
    
    if isinstance(node, Obj):
        processed = []
        for k, v in node:
            processed_v, child_removed = join_keys(v)
            removed_count += child_removed
            processed.append((k, processed_v))
        
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
                merged_val, merge_removed = merge_obj_values(vals)
                removed_count += merge_removed
                out.append((k, merged_val)); continue
            uniq: List[JSONNode] = []
            seen = set()
            for v in vals:
                sig = freeze(v)
                if sig in seen: continue
                seen.add(sig); uniq.append(v)
            out.append((k, uniq[0] if len(uniq) == 1 else uniq))
        return out, removed_count
    if isinstance(node, list):
        result = []
        for x in node:
            processed, child_removed = join_keys(x)
            removed_count += child_removed
            result.append(processed)
        return result, removed_count
    return node, 0


def eliminate_duplicates(node: JSONNode) -> Tuple[JSONNode, int]:
    """
    Remove globally duplicate values across the entire tree.
    Only the first occurrence of each unique value is kept.
    
    Returns:
        Tuple of (processed_node, removed_duplicate_values_count)
    """
    seen: Set = set()
    removed_count = 0
    
    def _visit(n: JSONNode) -> Optional[JSONNode]:
        nonlocal removed_count
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen:
                    removed_count += 1
                    continue
                seen.add(sig)
                out.append((k, v2))
            return out if out else None
        if isinstance(n, list):
            out: List[JSONNode] = []
            for v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen:
                    removed_count += 1
                    continue
                seen.add(sig)
                out.append(v2)
            return out if out else None
        return n
    
    res = _visit(node)
    return (res if res is not None else Obj()), removed_count


def exclude_numeric_keys(node: JSONNode) -> Tuple[JSONNode, int]:
    """
    Remove keys that are purely numeric (e.g., '0', '123', '456').
    Recursively processes Obj and list nodes.
    
    Returns:
        Tuple of (processed_node, removed_numeric_keys_count)
    """
    removed_count = 0
    
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # Skip if key is numeric
            if k.isdigit():
                removed_count += 1
                continue
            # Recursively process value
            processed_v, child_removed = exclude_numeric_keys(v)
            removed_count += child_removed
            out.append((k, processed_v))
        return out, removed_count
    if isinstance(node, list):
        result = []
        for x in node:
            processed, child_removed = exclude_numeric_keys(x)
            removed_count += child_removed
            result.append(processed)
        return result, removed_count
    return node, 0


def skip_empty_values(node: JSONNode) -> Tuple[JSONNode, int]:
    """
    Remove empty values from JSON structure.
    
    Empty values include:
    - Empty strings: ""
    - None/null
    - Empty lists: []
    - Empty dicts/Obj: {}
    - Whitespace-only strings: "   "
    
    Recursively processes Obj and list nodes.
    
    Returns:
        Tuple of (processed_node, removed_empty_pairs_count)
    """
    removed_count = 0
    
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
            processed, child_removed = skip_empty_values(v)
            removed_count += child_removed
            # Skip if empty
            if is_empty(processed):
                removed_count += 1
                continue
            out.append((k, processed))
        return out, removed_count
    if isinstance(node, list):
        out = []
        for item in node:
            processed, child_removed = skip_empty_values(item)
            removed_count += child_removed
            if not is_empty(processed):
                out.append(processed)
        return out, removed_count
    return node, 0


def avoid_duplicate_child_keys(node: JSONNode) -> Tuple[JSONNode, int]:
    """
    Avoid child keys with the same name as parent keys.
    
    Example:
        { pages: { home: { home: { home: 'Welcome' } } } }
    Becomes:
        { pages: { home: 'Welcome' } }
    
    If both parent and child are objects, they are merged.
    If values conflict, parent value is kept (child ignored).
    
    Recursively processes Obj and list nodes.
    
    Returns:
        Tuple of (processed_node, collapsed_hierarchies_count)
    """
    removed_count = 0
    
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # First, recursively process the value
            processed_v, child_removed = avoid_duplicate_child_keys(v)
            removed_count += child_removed
            
            # Check if the value is an Obj with a single key that matches current key
            if isinstance(processed_v, Obj) and len(processed_v) == 1:
                child_key, child_val = processed_v[0]
                if child_key == k:
                    # Found duplicate: t.pages.home.home
                    removed_count += 1
                    # If both are objects, merge them
                    if isinstance(child_val, Obj):
                        # Recursively check child_val for more duplicates
                        final_val, more_removed = avoid_duplicate_child_keys(child_val)
                        removed_count += more_removed
                        out.append((k, final_val))
                    else:
                        # Child is not an object, just use it directly
                        out.append((k, child_val))
                    continue
            
            # No duplicate found, keep as is
            out.append((k, processed_v))
        return out, removed_count
    if isinstance(node, list):
        result = []
        for x in node:
            processed, child_removed = avoid_duplicate_child_keys(x)
            removed_count += child_removed
            result.append(processed)
        return result, removed_count
    return node, 0


def remove_duplicate_array_values(node: JSONNode, consecutive_only: bool = False) -> Tuple[JSONNode, int]:
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
    
    Returns:
        Tuple of (processed_node, removed_array_elements_count)
    """
    removed_count = 0
    
    if isinstance(node, Obj):
        out = Obj()
        for k, v in node:
            # Recursively process value
            processed_v, child_removed = remove_duplicate_array_values(v, consecutive_only)
            removed_count += child_removed
            out.append((k, processed_v))
        return out, removed_count
    
    if isinstance(node, list):
        if consecutive_only:
            # Remove only consecutive duplicates
            if not node:
                return [], 0
            result = []
            prev_item, prev_removed = remove_duplicate_array_values(node[0], consecutive_only)
            removed_count += prev_removed
            result.append(prev_item)
            
            for i in range(1, len(node)):
                curr_item, curr_removed = remove_duplicate_array_values(node[i], consecutive_only)
                removed_count += curr_removed
                # Compare with previous item using freeze for consistent comparison
                if freeze(curr_item) != freeze(prev_item):
                    result.append(curr_item)
                    prev_item = curr_item
                else:
                    # Consecutive duplicate found
                    removed_count += 1
            return result, removed_count
        else:
            # Remove all duplicates (set-like behavior)
            seen = set()
            result = []
            for item in node:
                processed, child_removed = remove_duplicate_array_values(item, consecutive_only)
                removed_count += child_removed
                sig = freeze(processed)
                if sig not in seen:
                    seen.add(sig)
                    result.append(processed)
                else:
                    # Duplicate found
                    removed_count += 1
            return result, removed_count
    
    return node, 0


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


def array_to_object_conversion(
    node: JSONNode,
    max_key_length: int = 30,
    case_style: str = 'camel',
    scope_path: str = ''
) -> JSONNode:
    """
    Convert arrays to objects with intelligently generated keys (Task #21 - v2.9.10).
    
    Strategy:
    1. Take first N characters of string value (default 30)
    2. Remove accents, special characters, keep only alphanumeric
    3. Convert to target case style (camelCase by default)
    4. Handle conflicts by adding more words until unique
    
    Args:
        node: JSONNode tree to process
        max_key_length: Maximum initial key length (default 30 chars)
        case_style: Target case style ('camel', 'pascal', 'snake', 'kebab')
        scope_path: Current path for conflict resolution (internal)
    
    Returns:
        Processed JSONNode with arrays converted to objects
    
    Example:
        ["O usuario pode seguir..."] →
        {oUsuarioPodeSeguir: "O usuario pode seguir..."}
    """
    import re
    import unicodedata
    
    def remove_accents(text: str) -> str:
        """Remove accents from text."""
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    def clean_text(text: str) -> str:
        """Remove special characters, keep alphanumeric and spaces."""
        # Remove accents
        text = remove_accents(text)
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.strip()
    
    def to_case(text: str, style: str) -> str:
        """Convert text to target case style."""
        words = text.split()
        if not words:
            return text
        
        if style == 'camel':
            # camelCase: first word lowercase, rest capitalized
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        elif style == 'pascal':
            # PascalCase: all words capitalized
            return ''.join(w.capitalize() for w in words)
        elif style == 'snake':
            # snake_case: all lowercase with underscores
            return '_'.join(w.lower() for w in words)
        elif style == 'kebab':
            # kebab-case: all lowercase with hyphens
            return '-'.join(w.lower() for w in words)
        else:
            # Default to camelCase
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    
    def generate_key(value: str, max_len: int, used_keys: set) -> str:
        """
        Generate unique key from value string.
        
        Strategy:
        1. Take first max_len chars
        2. Clean and convert to case
        3. If conflict, add more words until unique or exhaust value
        """
        if not isinstance(value, str) or not value.strip():
            # Fallback for non-string or empty
            base = "item"
            counter = 1
            while f"{base}{counter}" in used_keys:
                counter += 1
            return f"{base}{counter}"
        
        # Clean value
        cleaned = clean_text(value)
        if not cleaned:
            # If cleaning removed everything, use fallback
            base = "item"
            counter = 1
            while f"{base}{counter}" in used_keys:
                counter += 1
            return f"{base}{counter}"
        
        # Try with initial length
        words = cleaned.split()
        key = to_case(' '.join(words)[:max_len], case_style)
        
        if key not in used_keys:
            return key
        
        # Conflict: try adding more words
        for i in range(1, len(words) + 1):
            key = to_case(' '.join(words[:i]), case_style)
            if key not in used_keys:
                return key
        
        # Still conflict: add entire string
        key = to_case(cleaned, case_style)
        if key not in used_keys:
            return key
        
        # Ultimate fallback: add counter
        counter = 1
        base_key = key
        while f"{base_key}{counter}" in used_keys:
            counter += 1
        return f"{base_key}{counter}"
    
    def process_array(arr: list, path: str) -> JSONNode:
        """Convert array to object if it contains strings."""
        # Check if array contains only strings
        if not arr:
            return arr
        
        # Check if all items are strings
        all_strings = all(isinstance(item, str) for item in arr)
        
        if all_strings:
            # Convert to object
            obj = Obj()
            used_keys = set()
            
            for value in arr:
                key = generate_key(value, max_key_length, used_keys)
                used_keys.add(key)
                obj.append((key, value))
            
            return obj
        else:
            # Recursively process array items
            return [process_node(item, f"{path}[]") for item in arr]
    
    def process_node(n: JSONNode, path: str = "") -> JSONNode:
        """Recursively process node."""
        if isinstance(n, str):
            return n
        
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                new_path = f"{path}.{k}" if path else k
                
                # Apply conversion only within scope (if specified)
                if not scope_path or new_path.startswith(scope_path):
                    processed_v = process_node(v, new_path)
                else:
                    processed_v = v
                
                out.append((k, processed_v))
            return out
        
        if isinstance(n, list):
            # Check if we should convert this array
            if not scope_path or path.startswith(scope_path):
                return process_array(n, path)
            else:
                return [process_node(item, f"{path}[]") for item in n]
        
        # Other types (int, float, bool, None)
        return n
    
    return process_node(node)


def skip_keys_without_siblings(node: JSONNode) -> Tuple[JSONNode, int]:
    """
    Remove keys that don't have siblings (Task #35 - v2.9.11).
    
    A serial chain is a hierarchy where each level has only one child,
    continuing until reaching a leaf value (not an object with multiple children).
    
    Example:
        Input:  {a: {b: {c: "value"}}}  // Serial chain: a->b->c->leaf
        Output: {}  // All removed (no siblings at any level)
        
        Input:  {a: {b: "val1", c: "val2"}}  // a->{b,c} (siblings exist)
        Output: {a: {b: "val1", c: "val2"}}  // Kept (b and c are siblings)
    
    Args:
        node: JSON node to process
    
    Returns:
        Tuple of (processed_node, removed_orphan_chains_count)
    """
    removed_count = 0
    
    def has_siblings_in_subtree(obj: Obj) -> bool:
        """Check if obj or any descendant has multiple children."""
        if len(obj) > 1:
            return True  # This level has siblings
        
        if len(obj) == 0:
            return False  # Empty object
        
        # Single child - check if it's an object with descendants
        k, v = obj[0]
        if isinstance(v, Obj):
            return has_siblings_in_subtree(v)
        else:
            # Leaf value (not an object)
            return False
    
    def process_obj(obj: Obj) -> Optional[Obj]:
        """Process Obj node, returning None if should be removed."""
        nonlocal removed_count
        
        if not obj:
            return obj
        
        # Process all children first (recursively)
        processed_children = []
        for k, v in obj:
            if isinstance(v, Obj):
                processed_v = process_obj(v)
                if processed_v is not None:  # Keep if not removed
                    processed_children.append((k, processed_v))
            elif isinstance(v, list):
                processed_v = process_list(v)
                processed_children.append((k, processed_v))
            else:
                # Leaf value - always keep at this stage
                processed_children.append((k, v))
        
        # Now check if this object should be kept
        # Keep if: has multiple children OR has siblings in subtree
        if len(processed_children) > 1:
            # Has siblings at this level
            return Obj(processed_children)
        elif len(processed_children) == 1:
            # Single child - check if it (or descendants) has siblings
            k, v = processed_children[0]
            if isinstance(v, Obj) and has_siblings_in_subtree(v):
                # Child subtree has siblings - keep this level
                return Obj(processed_children)
            else:
                # Serial chain (no siblings anywhere) - remove
                removed_count += 1
                return None
        else:
            # Empty after processing
            return None
    
    def process_list(arr: list) -> list:
        """Process list items."""
        result = []
        for item in arr:
            if isinstance(item, Obj):
                processed = process_obj(item)
                if processed is not None:
                    result.append(processed)
            elif isinstance(item, list):
                result.append(process_list(item))
            else:
                result.append(item)
        return result
    
    # Start processing
    if isinstance(node, Obj):
        result = process_obj(node)
        return (result if result is not None else Obj()), removed_count
    elif isinstance(node, list):
        return process_list(node), removed_count
    else:
        return node, 0
