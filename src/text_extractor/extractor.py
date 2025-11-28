"""
Text Extractor
==============

Main extraction logic for converting HTML/JSX to structured paths/JSON.

Combines parsing, normalization, and path building.

Author: Josué Amaral
Date: 2025-11-24
"""

import os
import glob
from typing import List, Dict, Any, Optional, Tuple

from .jsx_parser import parse_jsx_file
from .normalizer import normalize_text
from .path_builder import PathBuilder, build_nested_json


def extract_from_file(file_path: str,
                      param_name: Optional[str] = None,
                      drop_standard_tags: bool = True,
                      case_style: str = 'snake',
                      uppercase: bool = False,
                      limit: Optional[str] = None,
                      avoid_cut: bool = True,
                      add_key: bool = True,
                      add_value: bool = True) -> List[Tuple[str, str]]:
    """
    Extract structured paths from a single JSX/HTML file.
    
    Args:
        file_path: Path to file
        param_name: Attribute to extract (e.g., 'label'). None = all attributes
        drop_standard_tags: Filter standard HTML tags from hierarchy
        case_style: 'snake', 'camel', 'pascal', or 'kebab'
        uppercase: Convert to uppercase
        limit: Character limit for values
        avoid_cut: Preserve word boundaries when truncating
        add_key: Include tag name in path
        add_value: Include normalized value in path
        
    Returns:
        List of (path, original_value) tuples
    """
    # Get filename without extension for prefix
    filename = os.path.splitext(os.path.basename(file_path))[0]
    
    # Parse JSX
    parsed_data = parse_jsx_file(file_path, param_name, drop_standard_tags)
    
    # Build paths
    builder = PathBuilder(add_key=add_key, add_value=add_value, file_prefix=filename)
    results = []
    
    for tag_name, value, tag_stack in parsed_data:
        # Normalize value
        normalized_value = normalize_text(
            value,
            case_style=case_style,
            uppercase=uppercase,
            limit=limit,
            avoid_cut=avoid_cut
        )
        
        # Build path
        path = builder.build_path(tag_stack, tag_name, normalized_value)
        results.append((path, value))
    
    return results


def extract_from_directory(directory: str,
                           extensions: Optional[List[str]] = None,
                           param_name: Optional[str] = None,
                           drop_standard_tags: bool = True,
                           case_style: str = 'snake',
                           uppercase: bool = False,
                           limit: Optional[str] = None,
                           avoid_cut: bool = True,
                           add_key: bool = True,
                           add_value: bool = True) -> List[Tuple[str, str]]:
    """
    Extract structured paths from all matching files in a directory.
    
    Args:
        directory: Directory to scan
        extensions: File extensions to process (e.g., ['.jsx', '.tsx']). None = ['.jsx', '.tsx', '.js']
        param_name: Attribute to extract
        drop_standard_tags: Filter standard HTML tags
        case_style: Text normalization style
        uppercase: Convert to uppercase
        limit: Character limit
        avoid_cut: Preserve word boundaries
        add_key: Include tag names
        add_value: Include values
        
    Returns:
        List of (path, original_value) tuples from all files
    """
    if extensions is None:
        extensions = ['.jsx', '.tsx', '.js', '.html']
    
    all_results = []
    
    # Find matching files
    for ext in extensions:
        pattern = os.path.join(directory, f"**/*{ext}")
        files = glob.glob(pattern, recursive=True)
        
        for file_path in files:
            try:
                results = extract_from_file(
                    file_path,
                    param_name=param_name,
                    drop_standard_tags=drop_standard_tags,
                    case_style=case_style,
                    uppercase=uppercase,
                    limit=limit,
                    avoid_cut=avoid_cut,
                    add_key=add_key,
                    add_value=add_value
                )
                all_results.extend(results)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    return all_results


def extract_to_json(paths_and_values: List[Tuple[str, str]],
                    nested: bool = True) -> Dict[str, Any]:
    """
    Convert extracted paths to JSON format.
    
    Args:
        paths_and_values: List of (path, value) tuples
        nested: If True, create nested structure. If False, return flat dict.
        
    Returns:
        JSON-serializable dictionary
    """
    if not nested:
        # Flat structure
        return {path: value for path, value in paths_and_values}
    
    # Nested structure
    paths = [p for p, v in paths_and_values]
    values = [v for p, v in paths_and_values]
    return build_nested_json(paths, values)
