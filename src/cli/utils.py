"""
CLI Utilities
Helper functions for CLI argument parsing and file list building.

Refactored from src/app.py (Phase 3.1 - v2.9.114)
Original lines: 1117-1145 (29 lines)
"""

from __future__ import annotations
import fnmatch
import os
import re
from typing import List, Optional

from ..core import Condition


def split_globs(s: Optional[str]) -> List[str]:
    """
    Split glob patterns separated by semicolon or comma.

    Args:
        s: String with glob patterns (e.g., "*.ts;*.tsx")

    Returns:
        List of individual glob patterns

    Example:
        >>> split_globs("*.ts;*.tsx,*.js")
        ['*.ts', '*.tsx', '*.js']
    """
    if not s:
        return []
    return [p.strip() for p in re.split(r"[;,]", s) if p.strip()]


def parse_conditions(items: Optional[List[str]]) -> List[Condition]:
    """
    Parse condition strings into Condition objects.

    Args:
        items: List of condition strings in format "FIELD:OP:VALUE"
               e.g., ["content:contains:React", "ext:equals:ts"]

    Returns:
        List of Condition objects

    Example:
        >>> parse_conditions(["content:contains:React"])
        [Condition(field='content', op='contains', value='React')]
    """
    out: List[Condition] = []
    for raw in (items or []):
        # format: FIELD:OP:VALUE  e.g., content:contains:React
        parts = raw.split(":", 2)
        if len(parts) == 3:
            out.append(Condition(parts[0].strip(), parts[1].strip(), parts[2]))
    return out


def build_file_list(root: str, include_globs: List[str], exclude_globs: List[str]) -> List[str]:
    """
    Build a list of files matching include/exclude patterns.

    Args:
        root: Root directory to search
        include_globs: List of patterns to include (empty = all files)
        exclude_globs: List of patterns to exclude

    Returns:
        List of file paths matching the criteria

    Example:
        >>> build_file_list("./src", ["*.py"], ["*test*.py"])
        ['./src/app.py', './src/utils.py']
    """
    files: List[str] = []
    for r, _, fs in os.walk(root):
        for f in fs:
            full = os.path.join(r, f)
            if include_globs:
                if not any(fnmatch.fnmatch(full, pat) for pat in include_globs):
                    continue
            if exclude_globs and any(fnmatch.fnmatch(full, pat) for pat in exclude_globs):
                continue
            files.append(full)
    return files
