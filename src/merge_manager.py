#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge Manager - Apply Set Operations results back to original files

Provides functionality to merge operation results back to source files
with support for multiple merge modes, automatic backups, and safety validations.

v2.9.100 - Merge Results to File
Author: Josué Amaral
Date: 2025-12-23
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path


class MergeManager:
    """Manages merging of Set Operations results back to original files."""

    # Merge modes
    MODE_REPLACE = "replace"  # Overwrite entire file
    MODE_MERGE = "merge"      # Deep merge with existing content
    MODE_NEW_FILE = "new_file"  # Create new file with suffix

    def __init__(self, max_backups: int = 5, auto_backup: bool = True):
        """
        Initialize MergeManager.

        Args:
            max_backups: Maximum number of backup files to keep per file (default: 5)
            auto_backup: Whether to automatically backup files before merge (default: True)
        """
        self.max_backups = max_backups
        self.auto_backup = auto_backup

    # pylint: disable=too-many-return-statements  # Each validation needs early return
    # pylint: disable=inconsistent-return-statements  # False positive - all paths return tuple
    def merge_to_file(
        self,
        file_path: str,
        result_data: Dict[str, Any],
        mode: str,
        backup: Optional[bool] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Merge result data to file with specified mode.

        Args:
            file_path: Path to target file
            result_data: Data from Set Operations result
            mode: Merge mode (replace/merge/new_file)
            backup: Override auto_backup setting (optional)

        Returns:
            Tuple of (success: bool, message: str, output_path: Optional[str])
        """
        # Validate inputs
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}", None

        if mode not in [self.MODE_REPLACE, self.MODE_MERGE, self.MODE_NEW_FILE]:
            return False, f"Invalid mode: {mode}. Use 'replace', 'merge', or 'new_file'", None

        # Validate permissions
        valid, perm_msg = self._validate_permissions(file_path)
        if not valid:
            return False, perm_msg, None

        # Validate result data is valid JSON
        try:
            json.dumps(result_data)
        except (TypeError, ValueError) as e:
            return False, f"Invalid result data (not JSON serializable): {e}", None

        # Determine if backup is needed
        do_backup = backup if backup is not None else self.auto_backup

        try:
            # Execute merge based on mode
            if mode == self.MODE_NEW_FILE:
                output_path = self._get_new_file_path(file_path)
                success, message = self._write_json_file(output_path, result_data)
                if success:
                    return True, f"Created new file: {output_path}", output_path
                return False, message, None

            elif mode == self.MODE_REPLACE:
                # Backup original if enabled
                if do_backup:
                    backup_path = self._backup_file(file_path)
                    if not backup_path:
                        return False, f"Failed to create backup for: {file_path}", None

                # Replace file with result
                success, message = self._write_json_file(file_path, result_data)
                if success:
                    return True, f"Replaced file: {file_path}", file_path
                return False, message, None

            elif mode == self.MODE_MERGE:
                # Load original file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_data = json.load(f)
                except json.JSONDecodeError as e:
                    return False, f"Original file is not valid JSON: {e}", None

                # Backup original if enabled
                if do_backup:
                    backup_path = self._backup_file(file_path)
                    if not backup_path:
                        return False, f"Failed to create backup for: {file_path}", None

                # Perform deep merge
                merged_data = self._merge_recursive(original_data, result_data)

                # Write merged result
                success, message = self._write_json_file(file_path, merged_data)
                if success:
                    return True, f"Merged to file: {file_path}", file_path
                return False, message, None

        except Exception as e:  # pylint: disable=broad-exception-caught  # Catch-all for merge robustness
            return False, f"Unexpected error during merge: {e}", None

    # pylint: disable=inconsistent-return-statements  # False positive - all paths return tuple
    def simulate_merge(
        self,
        file_path: str,
        result_data: Dict[str, Any],
        mode: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Simulate merge operation without writing to disk (for preview).

        Args:
            file_path: Path to target file
            result_data: Data from Set Operations result
            mode: Merge mode (replace/merge/new_file)

        Returns:
            Tuple of (success: bool, merged_data: Optional[Dict], message: str)
        """
        if not os.path.exists(file_path):
            return False, None, f"File not found: {file_path}"

        try:
            if mode in (self.MODE_REPLACE, self.MODE_NEW_FILE):
                # In replace/new_file mode, result is the final output
                return True, result_data, "Preview: Replace/New file mode"

            elif mode == self.MODE_MERGE:
                # Load original file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_data = json.load(f)
                except json.JSONDecodeError as e:
                    return False, None, f"Original file is not valid JSON: {e}"

                # Simulate merge
                merged_data = self._merge_recursive(original_data, result_data)
                return True, merged_data, "Preview: Merge mode"

        except Exception as e:  # pylint: disable=broad-exception-caught  # Catch-all for simulation robustness
            return False, None, f"Simulation error: {e}"

    def _merge_recursive(self, original: Any, result: Any) -> Any:
        """
        Recursively merge result into original data.

        Strategy:
        - Key only in result → add
        - Key only in original → keep
        - Key in both + different value → result overwrites (priority)
        - Arrays: replace (no element-wise merge)
        - Nested dicts: merge recursively

        Args:
            original: Original data structure
            result: Result data structure

        Returns:
            Merged data structure
        """
        # If result is not dict, replace entirely
        if not isinstance(result, dict):
            return result

        # If original is not dict, result overwrites
        if not isinstance(original, dict):
            return result

        # Both are dicts - merge recursively
        merged = original.copy()

        for key, value in result.items():
            if key in merged:
                # Key exists in both - check if both are dicts
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    # Recursive merge for nested dicts
                    merged[key] = self._merge_recursive(merged[key], value)
                else:
                    # Arrays or primitives - result overwrites
                    merged[key] = value
            else:
                # Key only in result - add
                merged[key] = value

        return merged

    def _backup_file(self, file_path: str) -> Optional[str]:
        """
        Create backup of file with timestamp and rotation.

        Args:
            file_path: Path to file to backup

        Returns:
            Path to backup file if successful, None otherwise
        """
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            backup_path = f"{file_path}.bak.{timestamp}"

            # Copy file to backup location
            shutil.copy2(file_path, backup_path)

            # Rotate backups (keep only max_backups)
            self._rotate_backups(file_path)

            return backup_path

        except Exception as e:  # pylint: disable=broad-exception-caught  # Catch-all for backup robustness
            print(f"Warning: Failed to create backup: {e}")
            return None

    def _rotate_backups(self, file_path: str) -> None:
        """
        Rotate backup files, keeping only max_backups most recent.

        Args:
            file_path: Path to original file
        """
        try:
            # Find all backup files for this file
            directory = os.path.dirname(file_path)
            basename = os.path.basename(file_path)

            # List all .bak files for this file
            backup_files = []
            for filename in os.listdir(directory):
                if filename.startswith(basename + ".bak."):
                    backup_path = os.path.join(directory, filename)
                    backup_files.append(backup_path)

            # Sort by modification time (oldest first)
            backup_files.sort(key=os.path.getmtime)

            # Delete oldest backups if exceeding max_backups
            while len(backup_files) > self.max_backups:
                oldest = backup_files.pop(0)
                os.remove(oldest)

        except Exception as e:  # pylint: disable=broad-exception-caught  # Catch-all for rotation robustness
            print(f"Warning: Failed to rotate backups: {e}")

    def _validate_permissions(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate file permissions for write access.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (valid: bool, message: str)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"

        # Check if file is writable
        if not os.access(file_path, os.W_OK):
            return False, f"No write permission for file: {file_path}"

        # Check if directory is writable (for backups)
        directory = os.path.dirname(file_path)
        if not os.access(directory, os.W_OK):
            return False, f"No write permission for directory: {directory}"

        return True, "Permissions OK"

    def _write_json_file(self, file_path: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Write JSON data to file with pretty formatting.

        Args:
            file_path: Path to output file
            data: Data to write

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, f"Successfully wrote to: {file_path}"
        except Exception as e:  # pylint: disable=broad-exception-caught  # Catch-all for file write robustness
            return False, f"Failed to write file: {e}"

    def _get_new_file_path(self, file_path: str) -> str:
        """
        Generate new file path with _merged suffix.

        Args:
            file_path: Original file path

        Returns:
            New file path with suffix
        """
        path = Path(file_path)
        stem = path.stem
        suffix = path.suffix
        directory = path.parent

        # Generate new filename: data.json → data_merged.json
        new_filename = f"{stem}_merged{suffix}"
        new_path = directory / new_filename

        # If file exists, add number: data_merged_1.json, data_merged_2.json, etc.
        counter = 1
        while new_path.exists():
            new_filename = f"{stem}_merged_{counter}{suffix}"
            new_path = directory / new_filename
            counter += 1

        return str(new_path)

    def get_backup_files(self, file_path: str) -> List[str]:
        """
        Get list of backup files for given file.

        Args:
            file_path: Path to original file

        Returns:
            List of backup file paths sorted by timestamp (newest first)
        """
        try:
            directory = os.path.dirname(file_path)
            basename = os.path.basename(file_path)

            # List all .bak files for this file
            backup_files = []
            for filename in os.listdir(directory):
                if filename.startswith(basename + ".bak."):
                    backup_path = os.path.join(directory, filename)
                    backup_files.append(backup_path)

            # Sort by modification time (newest first)
            backup_files.sort(key=os.path.getmtime, reverse=True)

            return backup_files

        except Exception as e:  # pylint: disable=broad-exception-caught  # Catch-all for listing robustness
            print(f"Warning: Failed to list backups: {e}")
            return []
