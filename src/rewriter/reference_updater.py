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


def build_substitution_map(
    old_keys: Set[str],
    new_keys: Set[str]
) -> Dict[str, str]:
    """
    Build substitution map for eliminated keys.
    
    Strategy:
    - For each key in old_keys that's NOT in new_keys
    - Find the closest match in new_keys using string similarity
    - Map: removed_key → kept_key
    
    Args:
        old_keys: Set of all keys before elimination
        new_keys: Set of all keys after elimination
    
    Returns:
        Dictionary mapping removed keys to their replacements
        Example: {'t.pages.contactPage': 't.pages.contact'}
    """
    def string_similarity(s1: str, s2: str) -> float:
        """Calculate similarity between two strings (0-1)."""
        # Simple similarity: common prefix length / max length
        common = 0
        for c1, c2 in zip(s1, s2):
            if c1 == c2:
                common += 1
            else:
                break
        return common / max(len(s1), len(s2))
    
    substitutions: Dict[str, str] = {}
    removed_keys = old_keys - new_keys
    
    for removed_key in removed_keys:
        # Split key into parts
        parts = removed_key.split('.')
        
        # Find best match in new_keys
        # Strategy: Look for keys with same parent path and depth
        if len(parts) <= 2:
            # Root level key, can't find parent
            continue
        
        # Get parent path (e.g., "t.pages" from "t.pages.contactPage")
        parent = '.'.join(parts[:-1])
        removed_name = parts[-1].lower()
        
        # Find candidates with same parent and depth
        candidates = []
        for new_key in new_keys:
            new_parts = new_key.split('.')
            if len(new_parts) == len(parts):
                new_parent = '.'.join(new_parts[:-1])
                if new_parent == parent:
                    candidates.append(new_key)
        
        if not candidates:
            # No direct siblings, look for similar keys (same depth)
            candidates = [
                k for k in new_keys
                if k.startswith(parent) and len(k.split('.')) == len(parts)
            ]
        
        if candidates:
            # Find best match based on name similarity
            best_match = None
            best_score = 0.0
            
            for candidate in candidates:
                candidate_name = candidate.split('.')[-1].lower()
                score = string_similarity(removed_name, candidate_name)
                
                # Also check if removed name contains candidate name or vice versa
                if candidate_name in removed_name or removed_name in candidate_name:
                    score += 0.5
                
                if score > best_score:
                    best_score = score
                    best_match = candidate
            
            if best_match:
                substitutions[removed_key] = best_match
    
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


def extract_all_keys_from_dict(data: dict, prefix: str = 't') -> Set[str]:
    """
    Extract all possible reference paths from a dictionary.
    
    Args:
        data: Dictionary to extract keys from
        prefix: Prefix for keys (default 't')
    
    Returns:
        Set of all possible reference paths
        Example: {'t', 't.pages', 't.pages.contact', 't.pages.contact.title'}
    """
    keys: Set[str] = set()
    
    def recurse(obj, path: str):
        keys.add(path)
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}"
                recurse(value, new_path)
        elif isinstance(obj, list):
            # Don't recurse into arrays (not reference paths)
            pass
    
    recurse(data, prefix)
    return keys
