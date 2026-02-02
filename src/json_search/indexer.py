"""
Project Indexer
===============

Builds searchable index from JSON/TS/TSX files.

Supports:
- Single file indexing
- Directory recursive indexing
- Automatic file type detection
- Ignore common build directories (node_modules, dist, build, .next)

Author: Josué Amaral
Date: 2025-11-24
"""

import os
import json
import glob
from typing import Dict, List, Any

from .flattener import flatten_object
from .ts_extractor import extract_top_level_objects_from_ts, guess_line_number

# Type alias for the flat index structure
FlatIndex = Dict[str, List[Dict[str, Any]]]


class ProjectIndexer:
    """
    Indexes JSON/TS/TSX files from a target path.

    If target_is_file is True, indexes only that single file.
    Otherwise, recursively indexes all matching files in the directory.

    Attributes:
        target_path: Path to file or directory
        target_is_file: Whether target_path is a file (vs directory)
        flat: Flattened index mapping dot-paths to metadata
        files: List of indexed file paths
    """

    def __init__(self, target_path: str, target_is_file: bool):
        """
        Initialize indexer with target.

        Args:
            target_path: File path or directory path to index
            target_is_file: True if target_path is a single file
        """
        self.target_path = target_path
        self.target_is_file = target_is_file
        self.flat: FlatIndex = {}
        self.files: List[str] = []

    def rebuild(self) -> None:
        """
        Build or rebuild the index from target files.

        Scans target_path (file or directory), parses JSON/TS/TSX files,
        flattens nested structures, and builds searchable index.
        """
        if self.target_is_file:
            files = [self.target_path]
        else:
            # Glob patterns for supported file types
            patterns = ["**/*.json", "**/*.ts", "**/*.tsx"]

            # Directories to ignore
            ignore_dirs = {
                os.path.sep + "node_modules" + os.path.sep,
                os.path.sep + ".next" + os.path.sep,
                os.path.sep + "dist" + os.path.sep,
                os.path.sep + "build" + os.path.sep,
                os.path.sep + ".git" + os.path.sep,
            }

            files: List[str] = []
            for pat in patterns:
                files.extend(glob.glob(os.path.join(self.target_path, pat), recursive=True))

            # Filter out ignored directories
            files = [f for f in files if not any(token in f for token in ignore_dirs)]

        self.files = sorted(files)
        new_flat: FlatIndex = {}

        for fpath in self.files:
            ext = os.path.splitext(fpath)[1].lower()

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()

                if ext == ".json":
                    # Parse JSON file
                    try:
                        obj = json.loads(text)
                        flat = flatten_object(obj)
                        for json_path, v in flat.items():
                            lineno = guess_line_number(text, json_path)
                            new_flat.setdefault(json_path, []).append({
                                "file": fpath,
                                "value": v,
                                "line": lineno
                            })
                    except json.JSONDecodeError:
                        pass  # Skip invalid JSON

                elif ext in (".ts", ".tsx", ".js", ".jsx"):
                    # Extract TS/JS object literals
                    objects = extract_top_level_objects_from_ts(text)
                    for obj in objects:
                        flat = flatten_object(obj)
                        for json_path, v in flat.items():
                            new_flat.setdefault(json_path, []).append({
                                "file": fpath,
                                "value": v,
                                "line": guess_line_number(text, json_path)
                            })
                else:
                    # Unknown extension - try TS-like parse if single-file mode
                    if self.target_is_file:
                        objects = extract_top_level_objects_from_ts(text)
                        for obj in objects:
                            flat = flatten_object(obj)
                            for json_path, v in flat.items():
                                new_flat.setdefault(json_path, []).append({
                                    "file": fpath,
                                    "value": v,
                                    "line": guess_line_number(text, json_path)
                                })

            except Exception:
                pass  # Skip files that can't be read/parsed

        self.flat = new_flat

    def get_flat(self) -> FlatIndex:
        """
        Get the flattened index.

        Returns:
            Dictionary mapping dot-paths to lists of metadata dicts
        """
        return self.flat

    def root_display(self) -> str:
        """
        Get display string for the indexed target.

        Returns:
            The target_path string
        """
        return self.target_path
