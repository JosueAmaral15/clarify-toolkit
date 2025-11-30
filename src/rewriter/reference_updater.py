#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reference Updater - Update orphaned references in project files (Task #23 - v2.9.10)

When eliminate_duplicates removes redundant keys from JSON dictionaries,
it can leave orphaned references in .tsx/.jsx files that cause runtime errors.

Example Problem:
    Dictionary before: {pages: {contact: {...}, contactPage: {...}}}
    After eliminate: {pages: {contact: {...}}}  // contactPage removed (duplicate)
    TSX file: {t.pages.contactPage.title}  // Now undefined!

Solution:
    1. Scan project files BEFORE eliminating duplicates
    2. Build substitution map (contactPage → contact)
    3. Update all references in files
    4. Preview changes before applying
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ReferenceMatch:
    """Represents a found reference in a file."""
    file_path: str
    line_number: int
    line_content: str
    reference: str  # e.g., "t.pages.contactPage.title"
    start_pos: int
    end_pos: int


@dataclass
class Substitution:
    """Represents a substitution to be applied."""
    old_ref: str
    new_ref: str
    affected_files: List[str]
    count: int


def scan_project_references(
    directory: str,
    extensions: Optional[List[str]] = None
) -> Dict[str, List[ReferenceMatch]]:
    """
    Scan project files for translation references.
    
    Detects patterns:
    - {t.pages.contact.title}
    - t.pages.contact.title
    
    Args:
        directory: Root directory to scan
        extensions: File extensions to scan (default: ['.tsx', '.jsx', '.ts', '.js'])
    
    Returns:
        Dictionary mapping reference paths to list of matches
        Example: {'t.pages.contact': [ReferenceMatch(...), ...]}
    """
    if extensions is None:
        extensions = ['.tsx', '.jsx', '.ts', '.js']
    
    # Regex patterns
    # Pattern 1: {t.something.path}
    pattern_curly = re.compile(r'\{(t\.[A-Za-z0-9_.]+)\}')
    # Pattern 2: t.something.path (standalone, not in curly braces)
    pattern_standalone = re.compile(r'(?<!\{)(t\.[A-Za-z0-9_.]+)(?!\})')
    
    references: Dict[str, List[ReferenceMatch]] = {}
    
    # Walk directory
    for root, _, files in os.walk(directory):
        for filename in files:
            # Check extension
            if not any(filename.endswith(ext) for ext in extensions):
                continue
            
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, start=1):
                    # Find all matches in line
                    for match in pattern_curly.finditer(line):
                        ref = match.group(1)
                        ref_match = ReferenceMatch(
                            file_path=filepath,
                            line_number=line_num,
                            line_content=line.strip(),
                            reference=ref,
                            start_pos=match.start(),
                            end_pos=match.end()
                        )
                        
                        if ref not in references:
                            references[ref] = []
                        references[ref].append(ref_match)
                    
                    for match in pattern_standalone.finditer(line):
                        ref = match.group(1)
                        ref_match = ReferenceMatch(
                            file_path=filepath,
                            line_number=line_num,
                            line_content=line.strip(),
                            reference=ref,
                            start_pos=match.start(),
                            end_pos=match.end()
                        )
                        
                        if ref not in references:
                            references[ref] = []
                        references[ref].append(ref_match)
            
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")
                continue
    
    return references


def build_substitution_map_by_value(
    old_keys_values: Dict[str, str],
    new_keys_values: Dict[str, str]
) -> Dict[str, str]:
    """
    Build substitution map based on VALUE EQUALITY (not string similarity).
    
    Strategy (conforme especificações do usuário):
    1. Identify removed keys: keys in old but not in new
    2. For each removed key, find new key with SAME VALUE (identical)
    3. Priority rules:
       a) Prefer key with same parent path (t.pages.contact > t.pages.contactPage)
       b) If multiple candidates, use first one (linha menor vence)
       c) Do NOT touch if values are different
       d) Same key in different paths is OK (different full paths)
    
    Args:
        old_keys_values: Dict of path → value BEFORE elimination
        new_keys_values: Dict of path → value AFTER elimination
    
    Returns:
        Dict mapping removed_path → kept_path (only for IDENTICAL values)
        Example: {'t.pages.contactPage.title': 't.pages.contact.title'}
    
    User Requirements:
    - "Se ocorrer duas chaves com valores redundantes, e se marcado que se deve
      eliminar redundâncias, então a chave/objeto/caminho mais abaixo do arquivo
      deve ser eliminado, ou seja, apagado do arquivo."
    - "Se essas chaves estão em paths diferentes, ou seja, de pais chaves ou
      ancestrais chaves diferentes, ainda sim devem ser eliminados caso houver
      redundâncias de valores."
    - "E se houver chaves iguais com valores diferentes, deixa quieto, não mexa!"
    - "Não mexa se tiverem a mesma chave em caminhos diferentes, somente se
      estiverem com a mesma chave pai."
    """
    substitutions: Dict[str, str] = {}
    
    old_paths = set(old_keys_values.keys())
    new_paths = set(new_keys_values.keys())
    removed_paths = old_paths - new_paths
    
    for removed_path in removed_paths:
        removed_value = old_keys_values[removed_path]
        
        # Find candidates with IDENTICAL VALUE (not similarity!)
        candidates = [
            new_path for new_path, new_value in new_keys_values.items()
            if new_value == removed_value  # ✅ VALUE EQUALITY
        ]
        
        if not candidates:
            # No key with same value found
            continue
        
        # Priority rules:
        # 1. Single candidate: use it
        if len(candidates) == 1:
            substitutions[removed_path] = candidates[0]
            continue
        
        # 2. Multiple candidates: prefer same parent path
        removed_parts = removed_path.split('.')
        if len(removed_parts) <= 1:
            # Root level, no parent to compare
            substitutions[removed_path] = candidates[0]
            continue
        
        removed_parent = '.'.join(removed_parts[:-1])
        
        # Find candidate with same parent
        same_parent_candidates = []
        for candidate in candidates:
            candidate_parts = candidate.split('.')
            if len(candidate_parts) > 1:
                candidate_parent = '.'.join(candidate_parts[:-1])
                if candidate_parent == removed_parent:
                    same_parent_candidates.append(candidate)
        
        if same_parent_candidates:
            # Use first same-parent candidate (linha menor vence)
            substitutions[removed_path] = same_parent_candidates[0]
        else:
            # No same-parent match: use first candidate
            substitutions[removed_path] = candidates[0]
    
    return substitutions


def apply_substitutions_to_file(
    filepath: str,
    substitution_map: Dict[str, str],
    create_backup: bool = True
) -> int:
    """
    Apply substitutions to a single file.
    
    Args:
        filepath: Path to file to update
        substitution_map: Dictionary of old_ref → new_ref
        create_backup: Whether to create .bak file
    
    Returns:
        Number of substitutions made
    """
    if not os.path.exists(filepath):
        return 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        substitutions_made = 0
        
        # Apply each substitution
        for old_ref, new_ref in substitution_map.items():
            # Replace in both formats: {t.path} and t.path
            pattern1 = re.compile(re.escape('{' + old_ref + '}'))
            pattern2 = re.compile(r'\b' + re.escape(old_ref) + r'\b')
            
            count1 = len(pattern1.findall(content))
            count2 = len(pattern2.findall(content))
            
            if count1 > 0:
                content = pattern1.sub('{' + new_ref + '}', content)
                substitutions_made += count1
            
            if count2 > 0:
                content = pattern2.sub(new_ref, content)
                substitutions_made += count2
        
        # Only write if changes were made
        if content != original_content:
            # Create backup
            if create_backup:
                backup_path = filepath + '.bak'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
            
            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return substitutions_made
    
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return 0


def update_references_in_project(
    directory: str,
    substitution_map: Dict[str, str],
    extensions: Optional[List[str]] = None,
    create_backup: bool = True
) -> Dict[str, int]:
    """
    Update all references in project files.
    
    Args:
        directory: Root directory to process
        substitution_map: Dictionary of old_ref → new_ref
        extensions: File extensions to process
        create_backup: Whether to create .bak files
    
    Returns:
        Dictionary mapping filepath to number of substitutions made
    """
    if extensions is None:
        extensions = ['.tsx', '.jsx', '.ts', '.js']
    
    results: Dict[str, int] = {}
    
    for root, _, files in os.walk(directory):
        for filename in files:
            if not any(filename.endswith(ext) for ext in extensions):
                continue
            
            filepath = os.path.join(root, filename)
            count = apply_substitutions_to_file(filepath, substitution_map, create_backup)
            
            if count > 0:
                results[filepath] = count
    
    return results


def extract_all_keys_from_obj(data, prefix: str = 't') -> Dict[str, str]:
    """
    Extract all reference paths AND their values from Obj/dict structure.
    
    Supports both dict and Obj (list of tuples from rewriter).
    Returns dictionary mapping full path to its leaf value (primitives only).
    
    Args:
        data: Obj or dict structure from JSON rewriter
        prefix: Prefix for keys (default 't')
    
    Returns:
        Dictionary mapping full path → value (only leaf nodes)
        Example: {'t.pages.contact.title': 'Contact Us', 't.pages.contact.description': 'Get in touch'}
    
    Example:
        >>> from ..utils.json_types import Obj
        >>> obj = Obj([('pages', Obj([('contact', Obj([('title', 'Contact')]))]))])
        >>> extract_all_keys_from_obj(obj)
        {'t.pages.contact.title': 'Contact'}
    """
    # Import Obj type locally to avoid circular import
    try:
        from ..utils.json_types import Obj
    except ImportError:
        # Fallback: define Obj as list if import fails
        Obj = list
    
    keys_values: Dict[str, str] = {}
    
    def recurse(obj, path: str):
        # Handle Obj type (list of tuples)
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, dict)):
            # Check if it's Obj-like (list of tuples with 2 elements)
            if isinstance(obj, list) and obj and isinstance(obj[0], tuple) and len(obj[0]) == 2:
                for key, value in obj:
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, (str, int, float, bool, type(None))):
                        # Leaf node: store path → value
                        keys_values[new_path] = str(value) if value is not None else ''
                    else:
                        # Non-leaf: recurse
                        recurse(value, new_path)
                return
        
        # Handle dict type
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, (str, int, float, bool, type(None))):
                    # Leaf node: store path → value
                    keys_values[new_path] = str(value) if value is not None else ''
                else:
                    # Non-leaf: recurse
                    recurse(value, new_path)
        
        # Don't recurse into arrays (not reference paths)
    
    recurse(data, prefix)
    return keys_values
