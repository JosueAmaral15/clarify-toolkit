"""
Reference Resolver functions for Sprint A (v2.9.29).

These functions implement reference resolution for JSON deduplication:
- create_references(): Replace duplicates with $ref:path:line or delete them
- resolve_references(): Expand $ref to actual values
"""

import re
from typing import Tuple, Dict, Any, Optional
from .types import Obj, JSONNode, freeze


def create_references(
    node: JSONNode,
    mode: str = 'delete',
    include_line_numbers: bool = True
) -> Tuple[JSONNode, Dict[str, int]]:
    """
    Replace duplicate objects with references or delete them.
    
    This is Sprint A implementation (single-file only).
    
    Args:
        node: JSONNode to process
        mode: 'delete' removes duplicates, 'references' creates $ref
        include_line_numbers: If True, format is $ref:path:line, else $ref:path
    
    Returns:
        Tuple of (processed_node, stats) where stats contains:
            - 'created': Number of references created
            - 'deleted': Number of duplicates deleted
            - 'kept': Number of unique objects kept
    
    Examples:
        >>> obj = Obj([('user', {'name': 'John'}), ('author', {'name': 'John'})])
        >>> result, stats = create_references(obj, mode='references')
        >>> stats['created']
        1
    """
    stats = {'created': 0, 'deleted': 0, 'kept': 0}
    
    # Track seen objects: {frozen_value: (path, line_number, original_value)}
    seen_objects: Dict[Any, Tuple[str, int, JSONNode]] = {}
    line_counter = [1]  # Mutable counter for simulating line numbers
    
    def get_line_number(node: JSONNode) -> int:
        """Extract line number from node if available, else simulate."""
        if isinstance(node, Obj) and hasattr(node, '__line__'):
            return getattr(node, '__line__')
        # Simulate line numbers for testing (increment on each call)
        current_line = line_counter[0]
        line_counter[0] += 1
        return current_line
    
    def process_node(n: JSONNode, path: str = 'root', parent_line: int = 0) -> Optional[JSONNode]:
        """
        Recursively process node, tracking and replacing/removing duplicates.
        
        Args:
            n: Current node to process
            path: Current path in tree (e.g., 'root.users.profile')
            parent_line: Line number from parent (for inherited line tracking)
        
        Returns:
            Processed node, reference string, or None if deleted
        """
        nonlocal stats
        
        if isinstance(n, Obj):
            frozen_val = freeze(n)
            line_num = get_line_number(n) or parent_line
            
            # Check if we've seen this exact value before
            if frozen_val in seen_objects:
                # Found duplicate!
                orig_path, orig_line, _ = seen_objects[frozen_val]
                
                if mode == 'references':
                    # Create reference
                    if include_line_numbers and orig_line > 0:
                        ref_str = f"$ref:{orig_path}:{orig_line}"
                    else:
                        ref_str = f"$ref:{orig_path}"
                    
                    stats['created'] += 1
                    return ref_str
                else:
                    # Delete mode
                    stats['deleted'] += 1
                    return None
            
            # Not a duplicate - track it (but don't count root itself)
            seen_objects[frozen_val] = (path, line_num, n)
            if path != 'root':  # Don't count root node in 'kept' stat
                stats['kept'] += 1
            
            # Process children recursively
            out = Obj()
            for k, v in n:
                child_path = f"{path}.{k}"
                processed_v = process_node(v, child_path, line_num)
                
                if processed_v is not None:
                    out.append((k, processed_v))
            
            return out
        
        elif isinstance(n, list):
            # Process array items
            result = []
            for idx, item in enumerate(n):
                child_path = f"{path}[{idx}]"
                processed_item = process_node(item, child_path, parent_line)
                
                if processed_item is not None:
                    result.append(processed_item)
            
            return result
        
        else:
            # Primitive value - no deduplication
            return n
    
    # Process the tree
    result = process_node(node)
    return (result if result is not None else Obj()), stats


def resolve_references(node: JSONNode) -> Tuple[JSONNode, Dict[str, int]]:
    """
    Expand $ref references to their actual values.
    
    Supports formats:
    - $ref:path.to.key:123 (with line number)
    - $ref:path.to.key (without line number)
    
    This is Sprint A implementation (single-file only).
    
    Args:
        node: JSONNode to process
    
    Returns:
        Tuple of (processed_node, stats) where stats contains:
            - 'resolved': Number of valid references expanded
            - 'invalid': Number of invalid references (warnings logged)
    
    Examples:
        >>> obj = Obj([('user', {'name': 'John'}), ('ref', '$ref:root.user')])
        >>> result, stats = resolve_references(obj)
        >>> stats['resolved']
        1
    """
    stats = {'resolved': 0, 'invalid': 0}
    
    # Build index: {path: value, path_with_line: value}
    index: Dict[str, JSONNode] = {}
    
    def build_index(n: JSONNode, path: str = 'root'):
        """Build path index for value lookups."""
        if isinstance(n, Obj):
            for k, v in n:
                child_path = f"{path}.{k}"
                index[child_path] = v
                build_index(v, child_path)
        
        elif isinstance(n, list):
            for idx, item in enumerate(n):
                child_path = f"{path}[{idx}]"
                index[child_path] = item
                build_index(item, child_path)
    
    def resolve_node(n: JSONNode, path: str = 'root') -> JSONNode:
        """
        Recursively resolve references in node.
        
        Args:
            n: Current node to process
            path: Current path (for error reporting)
        
        Returns:
            Processed node with references expanded
        """
        nonlocal stats
        
        # Check if this is a reference string
        if isinstance(n, str) and n.startswith('$ref:'):
            # Parse reference
            ref_pattern = r'^\$ref:([^:]+)(?::(\d+))?$'
            match = re.match(ref_pattern, n)
            
            if not match:
                # Invalid format
                print(f"⚠️  Warning: Invalid reference format '{n}' at {path}")
                stats['invalid'] += 1
                return n  # Keep as-is
            
            ref_path = match.group(1)
            ref_line = match.group(2)  # May be None
            
            # Lookup value
            if ref_path in index:
                referenced_value = index[ref_path]
                stats['resolved'] += 1
                return referenced_value
            else:
                # Path not found
                print(f"⚠️  Warning: Reference target not found: '{ref_path}' (line {ref_line}) at {path}")
                stats['invalid'] += 1
                return n  # Keep as-is
        
        # Recursively process children
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                child_path = f"{path}.{k}"
                resolved_v = resolve_node(v, child_path)
                out.append((k, resolved_v))
            return out
        
        elif isinstance(n, list):
            result = []
            for idx, item in enumerate(n):
                child_path = f"{path}[{idx}]"
                resolved_item = resolve_node(item, child_path)
                result.append(resolved_item)
            return result
        
        else:
            # Primitive value
            return n
    
    # First, build index
    build_index(node)
    
    # Then, resolve all references
    result = resolve_node(node)
    
    return result, stats
