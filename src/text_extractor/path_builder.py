"""
Path Builder
============

Builds hierarchical paths from tag stacks and converts to nested JSON.

Features:
- Build dot-notation paths from tag hierarchies
- Convert flat paths to nested JSON structures
- Handle duplicate paths
- Include/exclude keys and values in paths

Author: Josué Amaral
Date: 2025-11-24
"""

from typing import List, Dict, Any, Optional


class PathBuilder:
    """
    Builds hierarchical paths from tag stacks.

    Example:
        builder = PathBuilder(add_key=True, add_value=True)
        path = builder.build_path(["App", "Form"], "Button", "Submit")
        # Result: "App.Form.Button.Submit"
    """

    def __init__(self,
                 add_key: bool = True,
                 add_value: bool = True,
                 file_prefix: Optional[str] = None):
        """
        Initialize path builder.

        Args:
            add_key: Include tag name in path
            add_value: Include normalized value in path
            file_prefix: Optional prefix (e.g., filename) for all paths
        """
        self.add_key = add_key
        self.add_value = add_value
        self.file_prefix = file_prefix

    def build_path(self,
                   tag_stack: List[str],
                   tag_name: str,
                   value: str) -> str:
        """
        Build dot-notation path from components.

        Args:
            tag_stack: List of parent tags
            tag_name: Current tag name
            value: Normalized value string

        Returns:
            Dot-notation path string
        """
        components = []

        # Add file prefix if set
        if self.file_prefix:
            components.append(self.file_prefix)

        # Add parent hierarchy
        components.extend(tag_stack)

        # Add current tag name if requested
        if self.add_key:
            components.append(tag_name)

        # Add value if requested
        if self.add_value and value:
            components.append(value)

        return '.'.join(components)


def build_nested_json(paths: List[str], values: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convert flat dot-notation paths to nested JSON structure.

    Args:
        paths: List of dot-notation paths
        values: Optional list of values (same length as paths). If None, uses empty strings.

    Returns:
        Nested dictionary structure

    Example:
        >>> build_nested_json(["app.home.title", "app.home.subtitle"])
        {"app": {"home": {"title": "", "subtitle": ""}}}

        >>> build_nested_json(["app.home.title"], ["Home Page"])
        {"app": {"home": {"title": "Home Page"}}}
    """
    if values is None:
        values = [""] * len(paths)

    if len(paths) != len(values):
        raise ValueError("paths and values must have same length")

    result: Dict[str, Any] = {}

    for path, value in zip(paths, values):
        parts = path.split('.')
        current = result

        # Navigate/create nested structure
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Conflict: existing value, create nested dict
                current[part] = {"_value": current[part]}
            current = current[part]

        # Set final value
        final_key = parts[-1]
        if final_key in current and isinstance(current[final_key], dict):
            # Already a dict, add _value key
            current[final_key]["_value"] = value
        else:
            current[final_key] = value

    return result


def flatten_nested_json(nested: Dict[str, Any], prefix: str = "") -> List[str]:
    """
    Flatten nested JSON back to dot-notation paths.

    Args:
        nested: Nested dictionary
        prefix: Current path prefix (used in recursion)

    Returns:
        List of dot-notation paths
    """
    paths = []

    for key, value in nested.items():
        current_path = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            # Recurse into nested dict
            paths.extend(flatten_nested_json(value, current_path))
        else:
            # Leaf value
            paths.append(current_path)

    return paths
