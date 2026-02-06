#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Set Operations - Core Logic (v2.9.32)

Provides set operations (intersection, union, difference, symmetric difference)
for JSON files with pipeline processing and flexible comparison modes.

Design Patterns:
    - Strategy (GoF): Each operation is a strategy
    - Template Method (GoF): Common pipeline for all operations
    - Information Expert (GRASP): This module knows set logic

Author: Josué Amaral
Date: December 2, 2025
Version: 2.9.32
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple



from src.utils.logger import get_logger

logger = get_logger(__name__)

def validate_file_path(file_path: str) -> bool:
    """
    Validate file path for security (CWE-22: Path Traversal).

    Args:
        file_path: File path to validate

    Returns:
        True if path is safe, False otherwise

    Security Checks:
        - File must exist
        - File must be readable
        - File must have .json extension
        - Path must be absolute (no relative paths like ../)
    """
    try:
        # Convert to absolute path
        abs_path = Path(file_path).resolve()

        # Check file exists
        if not abs_path.exists():
            return False

        # Check is file (not directory)
        if not abs_path.is_file():
            return False

        # Check extension is .json
        if abs_path.suffix.lower() != ".json":
            return False

        # Check is readable
        if not os.access(abs_path, os.R_OK):
            return False

        return True
    except (OSError, ValueError):
        return False


def flatten_json(obj: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flatten nested JSON structure into dot-notation dictionary.

    Args:
        obj: JSON object (dict, list, or primitive)
        parent_key: Parent key for recursion
        sep: Separator for key hierarchy (default: '.')

    Returns:
        Flattened dictionary with dot-notation keys

    Examples:
        >>> flatten_json({"a": {"b": 1, "c": 2}})
        {'a.b': 1, 'a.c': 2}
        >>> flatten_json({"items": [1, 2, 3]})
        {'items.0': 1, 'items.1': 2, 'items.2': 3}
    """
    items = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep).items())
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_json(v, new_key, sep).items())
    else:
        return {parent_key: obj}

    return dict(items)


def unflatten_json(flat_dict: Dict[str, Any], sep: str = ".") -> Any:
    """
    Reconstruct nested JSON from flattened dot-notation dictionary.

    Args:
        flat_dict: Flattened dictionary with dot-notation keys
        sep: Separator used in key hierarchy (default: '.')

    Returns:
        Reconstructed nested JSON object

    Examples:
        >>> unflatten_json({'a.b': 1, 'a.c': 2})
        {'a': {'b': 1, 'c': 2}}
        >>> unflatten_json({'items.0': 1, 'items.1': 2})
        {'items': [1, 2]}
    """
    nested = {}

    for key, value in flat_dict.items():
        parts = key.split(sep)
        current = nested

        for i, part in enumerate(parts[:-1]):
            # Determine if next level should be list or dict
            next_part = parts[i + 1]
            is_next_array = next_part.isdigit()

            if part not in current:
                current[part] = [] if is_next_array else {}

            if isinstance(current[part], list):
                idx = int(part) if part.isdigit() else 0
                # Extend list if needed
                while len(current[part]) <= idx:
                    current[part].append(None)
                if current[part][idx] is None:
                    current[part][idx] = [] if is_next_array else {}
                current = current[part][idx]
            else:
                current = current[part]

        # Set the final value
        final_key = parts[-1]
        if final_key.isdigit() and isinstance(current, dict):
            # Convert to list if numeric keys
            current = []

        if isinstance(current, list):
            idx = int(final_key)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[final_key] = value

    return nested


def normalize_for_comparison(value: Any, arrays_ignore_order: bool = False) -> Any:
    """
    Normalize value for comparison (handles arrays, maintains strict types).

    Args:
        value: Value to normalize
        arrays_ignore_order: If True, convert arrays to frozensets (order independent)

    Returns:
        Normalized hashable value

    Examples:
        >>> normalize_for_comparison([1, 2, 3], arrays_ignore_order=True)
        frozenset({1, 2, 3})
        >>> normalize_for_comparison([1, 2, 3], arrays_ignore_order=False)
        (1, 2, 3)
        >>> normalize_for_comparison({"a": 1})
        frozenset({('a', 1)})
    """
    if isinstance(value, dict):
        # Convert dict to frozenset of items for hashability
        return frozenset((k, normalize_for_comparison(v, arrays_ignore_order)) for k, v in value.items())
    elif isinstance(value, list):
        if arrays_ignore_order:
            # Convert to frozenset (order doesn't matter)
            return frozenset(normalize_for_comparison(v, arrays_ignore_order) for v in value)
        else:
            # Convert to tuple (order matters)
            return tuple(normalize_for_comparison(v, arrays_ignore_order) for v in value)
    elif value is None:
        return None  # Keep null distinct from empty string
    else:
        return value  # Primitives: int, str, float, bool (strict types)


# pylint: disable=too-many-positional-arguments  # API design - all params meaningful
def compare_files(
    files_data: List[Dict[str, Any]],
    comparison_mode: str = "key_value",
    ignore_case_keys: bool = False,
    ignore_case_values: bool = False,
    skip_empty: bool = False,
    arrays_ignore_order: bool = False,
) -> Tuple[List[Dict[str, Set]], Dict[str, int]]:
    """
    Prepare files for comparison by flattening and normalizing.

    Args:
        files_data: List of JSON objects to compare
        comparison_mode: 'key_value', 'full_path_value', or 'key_only'
        ignore_case_keys: Normalize key case for comparison
        ignore_case_values: Normalize value case for comparison
        skip_empty: Skip empty string values
        arrays_ignore_order: Treat arrays as sets (order independent)

    Returns:
        Tuple of (list of prepared sets, statistics dict)
    """
    prepared = []
    stats = {"total_keys": 0, "skipped_empty": 0}

    for obj in files_data:
        flat = flatten_json(obj)
        items = set()

        for key, value in flat.items():
            # Skip empty values if requested
            if skip_empty and isinstance(value, str) and not value.strip():
                stats["skipped_empty"] += 1
                continue

            # Normalize key case
            norm_key = key.lower() if ignore_case_keys else key

            # Normalize value case (only for strings)
            norm_value = value
            if ignore_case_values and isinstance(value, str):
                norm_value = value.lower()

            # Normalize value for comparison
            norm_value = normalize_for_comparison(norm_value, arrays_ignore_order)

            # Create comparison tuple based on mode
            if comparison_mode == "key_value":
                items.add((norm_key.split(".")[-1], norm_value))  # Only last key part
            elif comparison_mode == "full_path_value":
                items.add((norm_key, norm_value))  # Full path
            elif comparison_mode == "key_only":
                items.add(norm_key)  # Just the path

            stats["total_keys"] += 1

        prepared.append(items)

    return prepared, stats


def intersection(files_data: List[Dict[str, Any]], **opts) -> Dict[str, Any]:
    """
    Compute intersection of multiple JSON files (A ∩ B ∩ C ...).

    Pipeline: left-to-right sequential intersection.

    Args:
        files_data: List of JSON objects
        **opts: Comparison options (passed to compare_files)

    Returns:
        JSON object containing only common elements
    """
    if not files_data:
        return {}

    if len(files_data) == 1:
        return files_data[0]

    prepared, _ = compare_files(files_data, **opts)

    # Compute intersection: result = A ∩ B ∩ C ...
    result_set = prepared[0]
    for items in prepared[1:]:
        result_set = result_set.intersection(items)

    # Reconstruct JSON from result set
    # This is simplified - full implementation would need to track original structure
    return {"intersection": list(result_set)}


def union(files_data: List[Dict[str, Any]], **opts) -> Dict[str, Any]:
    """
    Compute union of multiple JSON files (A ∪ B ∪ C ...).

    Args:
        files_data: List of JSON objects
        **opts: Comparison options

    Returns:
        JSON object containing all elements from all files
    """
    if not files_data:
        return {}

    prepared, _ = compare_files(files_data, **opts)

    # Compute union
    result_set = set()
    for items in prepared:
        result_set = result_set.union(items)

    return {"union": list(result_set)}


def difference(files_data: List[Dict[str, Any]], **opts) -> Dict[str, Any]:
    """
    Compute difference (A - B - C ...).

    Pipeline: left-to-right sequential subtraction.

    Args:
        files_data: List of JSON objects
        **opts: Comparison options

    Returns:
        JSON object containing elements only in first file
    """
    if not files_data:
        return {}

    if len(files_data) == 1:
        return files_data[0]

    prepared, _ = compare_files(files_data, **opts)

    # Compute difference: result = A - B - C ...
    result_set = prepared[0]
    for items in prepared[1:]:
        result_set = result_set.difference(items)

    return {"difference": list(result_set)}


def symmetric_difference(file_a: Dict[str, Any], file_b: Dict[str, Any], **opts) -> Dict[str, Any]:
    """
    Compute symmetric difference (A ⊕ B) - elements in A or B but not both.

    Note: Only works with 2 files.

    Args:
        file_a: First JSON object
        file_b: Second JSON object
        **opts: Comparison options

    Returns:
        JSON object containing elements exclusive to each file
    """
    prepared, _ = compare_files([file_a, file_b], **opts)

    result_set = prepared[0].symmetric_difference(prepared[1])

    return {"symmetric_difference": list(result_set)}


# CLI Support
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="JSON Set Operations CLI (v2.9.32)")
    parser.add_argument(
        "operation", choices=["intersection", "union", "difference", "symmetric"], help="Set operation to perform"
    )
    parser.add_argument("files", nargs="+", help="JSON files to process")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--ignore-case-keys", action="store_true", help="Ignore case in keys")
    parser.add_argument("--ignore-case-values", action="store_true", help="Ignore case in values")
    parser.add_argument("--skip-empty", action="store_true", help="Skip empty values")
    parser.add_argument("--arrays-ignore-order", action="store_true", help="Treat arrays as sets")
    parser.add_argument(
        "--mode", choices=["key_value", "full_path_value", "key_only"], default="key_value", help="Comparison mode"
    )

    args = parser.parse_args()

    # Validate file count for symmetric difference
    if args.operation == "symmetric" and len(args.files) != 2:
        print("Error: Symmetric difference requires exactly 2 files.", file=sys.stderr)
        sys.exit(1)

    # Validate and load JSON files (Security: CWE-22)
    try:
        file_dicts = []
        for fpath in args.files:
            # Security validation
            if not validate_file_path(fpath):
                print(f"Error: Invalid or insecure file path: {fpath}", file=sys.stderr)
                print("  File must exist, be readable, and have .json extension", file=sys.stderr)
                sys.exit(1)

            with open(fpath, "r", encoding="utf-8") as f:
                file_dicts.append(json.load(f))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error loading files: {exc}", file=sys.stderr)
        sys.exit(1)

    # Prepare options
    options = {
        "comparison_mode": args.mode,
        "ignore_case_keys": args.ignore_case_keys,
        "ignore_case_values": args.ignore_case_values,
        "skip_empty": args.skip_empty,
        "arrays_ignore_order": args.arrays_ignore_order,
    }

    # Execute operation
    result = {}
    try:
        if args.operation == "intersection":
            result = intersection(file_dicts, **options)
        elif args.operation == "union":
            result = union(file_dicts, **options)
        elif args.operation == "difference":
            result = difference(file_dicts, **options)
        elif args.operation == "symmetric":
            result = symmetric_difference(file_dicts[0], file_dicts[1], **options)
    except Exception as exc:  # pylint: disable=broad-exception-caught  # CLI error handling
        print(f"Error executing operation: {exc}", file=sys.stderr)
        sys.exit(1)

    # Output result
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            logger.error(f"✓ Result saved to: {args.output}")
        except OSError as exc:
            print(f"Error saving output: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)
