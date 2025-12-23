"""
Calculator Operations for Clarify
Performs set operations between memory slots (Add, Intersection, Union, Difference).

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.101
"""

from typing import Dict, Any, Optional, Tuple
from .set_operations import intersection, union, difference
from .merge_manager import MergeManager
import copy


class CalculatorOperations:
    """
    Performs operations between Calculator Memory slots.
    
    Supports:
    - Add (Deep Merge): Merge two slots using v2.9.100 merge logic
    - Intersection: A ∩ B (common keys with same values)
    - Union: A ∪ B (all keys from both slots)
    - Difference: A − B (keys only in A)
    
    Integrates with set_operations.py for consistency.
    """
    
    @staticmethod
    def add(data_a: Dict[str, Any], data_b: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Add (Deep Merge) two slots using MergeManager recursive merge.
        
        Args:
            data_a: First slot data (original)
            data_b: Second slot data (result to merge)
        
        Returns:
            Tuple (success: bool, merged_data: Optional[Dict], message: str)
        """
        try:
            # Use MergeManager._merge_recursive for consistency with v2.9.100
            merged = MergeManager._merge_recursive(copy.deepcopy(data_a), copy.deepcopy(data_b))
            
            # Calculate summary
            keys_a = len(data_a) if isinstance(data_a, dict) else 0
            keys_b = len(data_b) if isinstance(data_b, dict) else 0
            keys_merged = len(merged) if isinstance(merged, dict) else 0
            
            message = f"Add complete: {keys_a} keys (A) + {keys_b} keys (B) → {keys_merged} keys (merged)"
            return True, merged, message
            
        except Exception as e:
            return False, None, f"Add failed: {str(e)}"
    
    @staticmethod
    def intersection(data_a: Dict[str, Any], data_b: Dict[str, Any], 
                     comparison_mode: str = "key_value") -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Intersection (A ∩ B) - Common keys with same values.
        
        Uses set_operations.py for consistency with Set Operations Dock.
        
        Args:
            data_a: First slot data
            data_b: Second slot data
            comparison_mode: "key_value" (default), "full_path_value", or "key_only"
        
        Returns:
            Tuple (success: bool, result: Optional[Dict], message: str)
        """
        try:
            # Set operations expects files, but we have data directly
            # We'll use the internal logic by creating temp dicts
            from .set_operations import flatten_json, normalize_for_comparison, unflatten_json
            
            # Flatten both datasets
            flat_a = flatten_json(data_a)
            flat_b = flatten_json(data_b)
            
            # Normalize based on comparison mode
            norm_a = normalize_for_comparison(flat_a, comparison_mode)
            norm_b = normalize_for_comparison(flat_b, comparison_mode)
            
            # Intersection: keys present in both with same values
            if comparison_mode == "key_only":
                # Key-only: just check key presence
                common_keys = set(norm_a.keys()) & set(norm_b.keys())
                result_flat = {k: flat_a[k] for k in common_keys}
            else:
                # Value comparison: check key-value pairs
                common_items = set(norm_a.items()) & set(norm_b.items())
                # Get original keys from normalized items
                result_flat = {}
                for item in common_items:
                    key = item[0]
                    if key in flat_a:
                        result_flat[key] = flat_a[key]
            
            # Unflatten result
            result = unflatten_json(result_flat)
            
            count_a = len(flat_a)
            count_b = len(flat_b)
            count_result = len(result_flat)
            
            message = f"Intersection: {count_a} keys (A) ∩ {count_b} keys (B) → {count_result} common keys"
            return True, result, message
            
        except Exception as e:
            return False, None, f"Intersection failed: {str(e)}"
    
    @staticmethod
    def union(data_a: Dict[str, Any], data_b: Dict[str, Any],
              comparison_mode: str = "key_value") -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Union (A ∪ B) - All keys from both slots.
        
        Args:
            data_a: First slot data
            data_b: Second slot data
            comparison_mode: "key_value" (default), "full_path_value", or "key_only"
        
        Returns:
            Tuple (success: bool, result: Optional[Dict], message: str)
        """
        try:
            from .set_operations import flatten_json, normalize_for_comparison, unflatten_json
            
            # Flatten both datasets
            flat_a = flatten_json(data_a)
            flat_b = flatten_json(data_b)
            
            # Normalize based on comparison mode
            norm_a = normalize_for_comparison(flat_a, comparison_mode)
            norm_b = normalize_for_comparison(flat_b, comparison_mode)
            
            # Union: all keys from both (B overwrites A on conflicts)
            result_flat = {}
            result_flat.update(flat_a)  # Start with A
            result_flat.update(flat_b)  # B overwrites conflicts
            
            # Unflatten result
            result = unflatten_json(result_flat)
            
            count_a = len(flat_a)
            count_b = len(flat_b)
            count_result = len(result_flat)
            
            message = f"Union: {count_a} keys (A) ∪ {count_b} keys (B) → {count_result} total keys"
            return True, result, message
            
        except Exception as e:
            return False, None, f"Union failed: {str(e)}"
    
    @staticmethod
    def difference(data_a: Dict[str, Any], data_b: Dict[str, Any],
                   comparison_mode: str = "key_value") -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Difference (A − B) - Keys only in A.
        
        Args:
            data_a: First slot data (base)
            data_b: Second slot data (to subtract)
            comparison_mode: "key_value" (default), "full_path_value", or "key_only"
        
        Returns:
            Tuple (success: bool, result: Optional[Dict], message: str)
        """
        try:
            from .set_operations import flatten_json, normalize_for_comparison, unflatten_json
            
            # Flatten both datasets
            flat_a = flatten_json(data_a)
            flat_b = flatten_json(data_b)
            
            # Normalize based on comparison mode
            norm_a = normalize_for_comparison(flat_a, comparison_mode)
            norm_b = normalize_for_comparison(flat_b, comparison_mode)
            
            # Difference: keys in A but not in B
            if comparison_mode == "key_only":
                # Key-only: remove keys present in B
                diff_keys = set(norm_a.keys()) - set(norm_b.keys())
                result_flat = {k: flat_a[k] for k in diff_keys}
            else:
                # Value comparison: remove key-value pairs present in B
                diff_items = set(norm_a.items()) - set(norm_b.items())
                result_flat = {}
                for item in diff_items:
                    key = item[0]
                    if key in flat_a:
                        result_flat[key] = flat_a[key]
            
            # Unflatten result
            result = unflatten_json(result_flat)
            
            count_a = len(flat_a)
            count_b = len(flat_b)
            count_result = len(result_flat)
            
            message = f"Difference: {count_a} keys (A) − {count_b} keys (B) → {count_result} unique keys"
            return True, result, message
            
        except Exception as e:
            return False, None, f"Difference failed: {str(e)}"
    
    @staticmethod
    def validate_operation_data(data_a: Any, data_b: Any) -> Tuple[bool, str]:
        """
        Validate that both datasets are suitable for operations.
        
        Args:
            data_a: First dataset
            data_b: Second dataset
        
        Returns:
            Tuple (valid: bool, error_message: str)
        """
        if data_a is None:
            return False, "Slot A is empty"
        
        if data_b is None:
            return False, "Slot B is empty"
        
        if not isinstance(data_a, (dict, list)):
            return False, "Slot A data must be dict or list"
        
        if not isinstance(data_b, (dict, list)):
            return False, "Slot B data must be dict or list"
        
        return True, ""
    
    @staticmethod
    def get_operation_description(operation: str, slot_a: str, slot_b: str) -> str:
        """
        Generate human-readable description of operation.
        
        Args:
            operation: Operation name ("add", "intersection", "union", "difference")
            slot_a: First slot name
            slot_b: Second slot name
        
        Returns:
            Description string (e.g., "Add: Slot A + Slot B")
        """
        operation_symbols = {
            'add': '+',
            'intersection': '∩',
            'union': '∪',
            'difference': '−'
        }
        
        operation_names = {
            'add': 'Add (Merge)',
            'intersection': 'Intersection',
            'union': 'Union',
            'difference': 'Difference'
        }
        
        symbol = operation_symbols.get(operation.lower(), '?')
        name = operation_names.get(operation.lower(), operation.capitalize())
        
        return f"{name}: Slot {slot_a} {symbol} Slot {slot_b}"
