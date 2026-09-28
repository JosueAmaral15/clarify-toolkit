#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File List Executor - Core file listing logic

Extracted from file_list_dock.py (v2.9.114 - Phase 2.4.2)
Handles file discovery, filtering, and information gathering.

Features:
- Directory traversal with recursion
- Advanced filtering (regex, size, mtime, extensions, depth)
- Permissions and ownership information
- Statistics calculation
- Error handling for permission issues
"""

from __future__ import annotations

import os
import stat
import pwd
import grp
import re
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Container for file information."""

    name: str
    path: str
    size: int
    mtime: datetime
    permissions: str
    owner: str
    group: str
    is_dir: bool


# pylint: disable=too-few-public-methods  # Simple data container
class ListResult:
    """Container for file listing results."""

    def __init__(self, files: List[FileInfo], errors: List[str] = None):
        """
        Initialize list result.

        Args:
            files: List of FileInfo objects
            errors: List of error messages encountered
        """
        self.files = files
        self.errors = errors or []
        self.total_size = sum(f.size for f in files if not f.is_dir)
        self.file_count = sum(1 for f in files if not f.is_dir)
        self.dir_count = sum(1 for f in files if f.is_dir)


class FileListExecutor:
    """Executor for file listing operations."""

    @staticmethod
    def list_files(
        directory: str, show_hidden: bool = False, recursive: bool = False, filters: Dict[str, Any] = None,
        *, checkpoint=None,
    ) -> ListResult:
        """
        List files in directory with optional filtering.

        Args:
            directory: Directory path to list
            show_hidden: Whether to show hidden files
            recursive: Whether to recurse into subdirectories
            filters: Filter configuration dictionary

        Returns:
            ListResult with files and statistics
        """
        if not os.path.isdir(directory):
            return ListResult([], [f"Directory does not exist: {directory}"])

        filters = filters or {}
        files = []
        errors = []

        # Collect files
        collected = FileListExecutor._collect_files(
            directory, show_hidden, recursive, filters, depth=0, checkpoint=checkpoint
        )

        # Convert to FileInfo objects
        for filepath in collected:
            if checkpoint is not None and not checkpoint():
                break
            try:
                file_info = FileListExecutor._get_file_info(filepath)
                files.append(file_info)
            except (PermissionError, FileNotFoundError) as e:
                errors.append(f"Error accessing {filepath}: {e}")
                continue

        return ListResult(files, errors)

    @staticmethod
    def _collect_files(
        directory: str, show_hidden: bool, recursive: bool, filters: Dict[str, Any], depth: int = 0,
        *, checkpoint=None, ancestors=None,
    ) -> List[str]:
        """Collect file paths from directory."""
        files = []
        if checkpoint is not None and not checkpoint():
            return files
        # Preserve useful directory links, but never recurse into an ancestor.
        real_directory = os.path.realpath(directory)
        ancestors = ancestors or frozenset()
        if real_directory in ancestors:
            return files
        ancestors = ancestors | {real_directory}

        try:
            entries = os.listdir(directory)
        except PermissionError:
            return files

        for entry in sorted(entries):
            if checkpoint is not None and not checkpoint():
                break
            # Skip hidden files if not showing all
            if not show_hidden and entry.startswith("."):
                continue

            filepath = os.path.join(directory, entry)

            # Check if directory should be excluded
            if os.path.isdir(filepath):
                if FileListExecutor._should_exclude_directory(entry, filters):
                    continue
                files.append(filepath)

            # Apply filters to files
            if os.path.isfile(filepath):
                if FileListExecutor._matches_filters(filepath, entry, depth, filters):
                    files.append(filepath)

            # Recurse into subdirectories
            if recursive and os.path.isdir(filepath):
                # Check depth limit
                max_depth = filters.get("depth", 0)
                if not max_depth or depth < max_depth:
                    files.extend(FileListExecutor._collect_files(
                        filepath, show_hidden, recursive, filters, depth + 1,
                        checkpoint=checkpoint, ancestors=ancestors,
                    ))

        return files

    @staticmethod
    def _get_file_info(filepath: str) -> FileInfo:
        """Get file information."""
        st = os.stat(filepath)
        name = os.path.basename(filepath)
        is_dir = os.path.isdir(filepath)

        if is_dir:
            name += "/"

        return FileInfo(
            name=name,
            path=filepath,
            size=st.st_size if not is_dir else 0,
            mtime=datetime.fromtimestamp(st.st_mtime),
            permissions=FileListExecutor._format_permissions(st.st_mode),
            owner=FileListExecutor._get_owner(st.st_uid),
            group=FileListExecutor._get_group(st.st_gid),
            is_dir=is_dir,
        )

    @staticmethod
    # pylint: disable=too-many-return-statements  # Filter chain logic requires early returns
    def _matches_filters(filepath: str, filename: str, depth: int, filters: Dict[str, Any]) -> bool:
        """Check if file matches all filter criteria."""
        from ..utils.logger import get_logger  # pylint: disable=import-outside-toplevel  # Lazy import

        logger = get_logger(__name__)

        if not filters:
            return True

        # Regex filter
        regex_config = filters.get("regex", {})
        if regex_config.get("enabled") and regex_config.get("pattern"):
            try:
                if not re.search(regex_config["pattern"], filename):
                    logger.debug("Regex filter rejected: %s (pattern: %s)", filename, regex_config["pattern"])
                    return False
            except re.error as e:
                logger.debug("Invalid regex pattern: %s - %s", regex_config["pattern"], e)
                # Invalid regex, ignore

        # Size filter
        try:
            file_size = os.path.getsize(filepath)
            size_config = filters.get("size", {})

            min_size = size_config.get("min")
            if min_size is not None and file_size < min_size:
                return False

            max_size = size_config.get("max")
            if max_size is not None and file_size > max_size:
                return False
        except OSError:
            pass

        # MTime filter
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
            mtime_config = filters.get("mtime", {})

            after = mtime_config.get("after")
            if after and mtime < after:
                return False

            before = mtime_config.get("before")
            if before and mtime > before:
                return False
        except OSError:
            pass

        # Extension filter
        extensions = filters.get("extensions", [])
        if extensions:
            file_ext = os.path.splitext(filename)[1].lstrip(".").lower()
            # Normalize extensions to remove leading dots for comparison
            normalized_exts = [ext.lstrip(".").lower() for ext in extensions]
            if file_ext not in normalized_exts:
                return False

        # Depth filter
        max_depth = filters.get("depth", 0)
        if 0 < max_depth < depth:
            return False

        return True

    @staticmethod
    def _should_exclude_directory(dirname: str, filters: Dict[str, Any]) -> bool:
        """Check if directory should be excluded."""
        if not filters:
            return False

        exclude_dirs = filters.get("exclude_dirs", [])
        if not exclude_dirs:
            return False

        # Direct match
        if dirname in exclude_dirs:
            return True

        # Pattern matching (basic wildcards)
        for pattern in exclude_dirs:
            if pattern.startswith("*") and dirname.endswith(pattern[1:]):
                return True
            if pattern.endswith("*") and dirname.startswith(pattern[:-1]):
                return True

        return False

    @staticmethod
    def _format_permissions(mode: int) -> str:
        """Format permissions string (Unix-style)."""
        perms = ""

        # File type
        if stat.S_ISDIR(mode):
            perms += "d"
        elif stat.S_ISLNK(mode):
            perms += "l"
        else:
            perms += "-"

        # Owner permissions
        perms += "r" if mode & stat.S_IRUSR else "-"
        perms += "w" if mode & stat.S_IWUSR else "-"
        perms += "x" if mode & stat.S_IXUSR else "-"

        # Group permissions
        perms += "r" if mode & stat.S_IRGRP else "-"
        perms += "w" if mode & stat.S_IWGRP else "-"
        perms += "x" if mode & stat.S_IXGRP else "-"

        # Other permissions
        perms += "r" if mode & stat.S_IROTH else "-"
        perms += "w" if mode & stat.S_IWOTH else "-"
        perms += "x" if mode & stat.S_IXOTH else "-"

        return perms

    @staticmethod
    def _get_owner(uid: int) -> str:
        """Get owner name from UID."""
        try:
            return pwd.getpwuid(uid).pw_name
        except (KeyError, AttributeError):
            return str(uid)

    @staticmethod
    def _get_group(gid: int) -> str:
        """Get group name from GID."""
        try:
            return grp.getgrgid(gid).gr_name
        except (KeyError, AttributeError):
            return str(gid)

    @staticmethod
    def format_size_human(size: int) -> str:
        """Convert size to human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    @staticmethod
    def calculate_statistics(files: List[FileInfo]) -> Dict[str, Any]:
        """Calculate statistics for file list."""
        total_size = sum(f.size for f in files if not f.is_dir)
        file_count = sum(1 for f in files if not f.is_dir)
        dir_count = sum(1 for f in files if f.is_dir)

        # Extension breakdown
        extensions = {}
        for f in files:
            if not f.is_dir:
                ext = os.path.splitext(f.name)[1].lower() or "(no extension)"
                extensions[ext] = extensions.get(ext, 0) + 1

        return {
            "total_size": total_size,
            "total_size_human": FileListExecutor.format_size_human(total_size),
            "file_count": file_count,
            "dir_count": dir_count,
            "total_count": len(files),
            "extensions": extensions,
        }


__all__ = ["FileListExecutor", "FileInfo", "ListResult"]
