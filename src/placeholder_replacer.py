"""
Placeholder Replacer
====================

Replaces placeholders like {t.pages.home.title} with translated values from mapping files.

Features:
- Parse JSON/CSV mapping files
- Flatten nested dictionaries for dot-notation lookup
- Replace placeholders with longest-match-first strategy
- Optional scope limiting with regex patterns
- Backup file creation (.bak)
- Recursive directory processing

Author: Josué Amaral
Date: 2025-11-24
"""

import os
import re
import json
import csv
import shutil
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path


def flatten_dict(nested: Dict[str, Any], prefix: str = "", sep: str = ".") -> Dict[str, str]:
    """
    Flatten nested dictionary to dot-notation keys.
    
    Args:
        nested: Nested dictionary
        prefix: Current prefix (used in recursion)
        sep: Separator for path segments
        
    Returns:
        Flat dictionary with dot-notation keys
        
    Example:
        >>> flatten_dict({"a": {"b": "value"}})
        {"a.b": "value"}
    """
    result = {}
    
    for key, value in nested.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        
        if isinstance(value, dict):
            result.update(flatten_dict(value, full_key, sep))
        else:
            # Convert to string
            result[full_key] = str(value)
    
    return result


def parse_mapping_file(file_path: str) -> Dict[str, str]:
    """
    Parse mapping file (JSON or CSV) into flat dictionary.
    
    Supported formats:
    - JSON: Nested or flat structure
    - CSV: Two columns (key, value)
    
    Args:
        file_path: Path to mapping file
        
    Returns:
        Flat dictionary mapping keys to values
        
    Raises:
        ValueError: If file format is unsupported or invalid
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            return flatten_dict(data)
        else:
            raise ValueError("JSON file must contain an object at root")
    
    elif ext == '.csv':
        result = {}
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    key = row[0].strip()
                    value = row[1].strip()
                    if key:  # Skip empty keys
                        result[key] = value
        return result
    
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .json or .csv")


def replace_placeholders(content: str,
                         mapping: Dict[str, str],
                         root_var: str = "t",
                         scope_start: Optional[str] = None,
                         scope_end: Optional[str] = None) -> Tuple[str, int]:
    """
    Replace placeholders in content using mapping dictionary.
    
    Placeholders format: {root_var.key.path}
    Uses longest-match-first strategy to avoid partial replacements.
    
    Args:
        content: Text content to process
        mapping: Dictionary mapping dot-paths to values
        root_var: Root variable name (default: "t")
        scope_start: Optional regex pattern for scope start
        scope_end: Optional regex pattern for scope end
        
    Returns:
        Tuple of (modified_content, replacement_count)
        
    Example:
        >>> mapping = {"pages.home": "Home"}
        >>> replace_placeholders("Title: {t.pages.home}", mapping)
        ("Title: Home", 1)
    """
    if not mapping:
        return content, 0
    
    # Apply scope limiting if patterns provided
    if scope_start and scope_end:
        try:
            # Find all scope regions
            pattern = f"({scope_start})(.*?)({scope_end})"
            matches = list(re.finditer(pattern, content, re.DOTALL))
            
            if not matches:
                return content, 0
            
            # Process only within scopes
            result_parts = []
            last_end = 0
            total_count = 0
            
            for match in matches:
                # Add content before scope (unchanged)
                result_parts.append(content[last_end:match.start()])
                
                # Add scope start
                result_parts.append(match.group(1))
                
                # Process scope content
                scope_content = match.group(2)
                processed, count = _replace_in_text(scope_content, mapping, root_var)
                result_parts.append(processed)
                total_count += count
                
                # Add scope end
                result_parts.append(match.group(3))
                
                last_end = match.end()
            
            # Add remaining content
            result_parts.append(content[last_end:])
            
            return ''.join(result_parts), total_count
            
        except re.error as e:
            raise ValueError(f"Invalid scope regex: {e}")
    
    # No scope limiting - process entire content
    return _replace_in_text(content, mapping, root_var)


def _replace_in_text(content: str, mapping: Dict[str, str], root_var: str) -> Tuple[str, int]:
    """Internal: Replace placeholders in text without scope limiting."""
    # Sort keys by length (descending) for longest-match-first
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    
    count = 0
    result = content
    
    for key in sorted_keys:
        # Build placeholder pattern: {root_var.key}
        placeholder = f"{{{root_var}.{key}}}"
        
        if placeholder in result:
            result = result.replace(placeholder, mapping[key])
            count += result.count(mapping[key]) - content.count(mapping[key])
    
    return result, count


def backup_file(file_path: str) -> str:
    """
    Create backup of file with .bak extension.
    
    Args:
        file_path: Path to file to backup
        
    Returns:
        Path to backup file
    """
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    return backup_path


def process_file(file_path: str,
                 mapping: Dict[str, str],
                 root_var: str = "t",
                 scope_start: Optional[str] = None,
                 scope_end: Optional[str] = None,
                 create_backup: bool = True,
                 dry_run: bool = False) -> Tuple[int, str]:
    """
    Process a single file, replacing placeholders.
    
    Args:
        file_path: Path to file to process
        mapping: Mapping dictionary
        root_var: Root variable name
        scope_start: Scope start pattern
        scope_end: Scope end pattern
        create_backup: Whether to create .bak file
        dry_run: If True, don't modify file (just return preview)
        
    Returns:
        Tuple of (replacement_count, modified_content)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Failed to read {file_path}: {e}")
    
    # Replace placeholders
    modified, count = replace_placeholders(content, mapping, root_var, scope_start, scope_end)
    
    if not dry_run and count > 0:
        # Create backup if requested
        if create_backup:
            backup_file(file_path)
        
        # Write modified content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified)
        except Exception as e:
            raise IOError(f"Failed to write {file_path}: {e}")
    
    return count, modified


def process_directory(directory: str,
                      mapping: Dict[str, str],
                      root_var: str = "t",
                      scope_start: Optional[str] = None,
                      scope_end: Optional[str] = None,
                      create_backup: bool = True,
                      extensions: Optional[List[str]] = None) -> Dict[str, int]:
    """
    Process all matching files in directory recursively.
    
    Args:
        directory: Directory to process
        mapping: Mapping dictionary
        root_var: Root variable name
        scope_start: Scope start pattern
        scope_end: Scope end pattern
        create_backup: Whether to create backups
        extensions: List of extensions to process (e.g., ['.js', '.jsx'])
        
    Returns:
        Dictionary mapping file paths to replacement counts
    """
    if extensions is None:
        extensions = ['.js', '.jsx', '.ts', '.tsx', '.html']
    
    results = {}
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1]
            
            if ext in extensions:
                try:
                    count, _ = process_file(
                        file_path,
                        mapping,
                        root_var,
                        scope_start,
                        scope_end,
                        create_backup,
                        dry_run=False
                    )
                    if count > 0:
                        results[file_path] = count
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return results
