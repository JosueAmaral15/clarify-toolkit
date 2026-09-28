"""
Unified File Explorer Executor - Merges List + Search + Replace logic.

Part of v2.9.116 integration: Search/Replace → File Explorer.
Combines FileListExecutor and SearchWorker into single unified pipeline.

Author: Josué Amaral
Date: 2025/12/25
"""

from __future__ import annotations

import os
import stat
import re
import fnmatch
import threading
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal  # pylint: disable=no-name-in-module  # Qt dynamic

from .file_list_executor import FileInfo, FileListExecutor, ListResult
from .search_replace import preserve_case_like
from ..utils.atomic_files import file_revision, write_existing_text_atomically
from ..utils import read_text
from ..utils.logger import get_logger

# Initialize logger for structured logging (Protocolo Simplicidade 3 - Etapa 6)
logger = get_logger(__name__)

# Memory optimization constants (v2.9.120 - 2026-01-09)
MAX_SNIPPET_LENGTH = 200  # Maximum characters to store per match snippet
MAX_TOTAL_MATCHES = 50000  # Maximum total matches across all files
TEXT_SAMPLE_BYTES = 8192  # Lightweight sample for text/binary classification
MAX_REPLACE_FILE_BYTES = 4 * 1024 * 1024
MAX_REPLACE_FILES = 1000
MAX_REPLACE_MATCHES = 10000
MAX_OPERATION_ERRORS = 50
BINARY_SEARCH_CHUNK_SIZE = 64 * 1024
BINARY_REGEX_OVERLAP_BYTES = 4096
BINARY_SNIPPET_CONTEXT_BYTES = 24
CONTENT_SCOPE_TEXT = "text"
CONTENT_SCOPE_BINARY = "binary"
CONTENT_SCOPE_BOTH = "both"
MAX_TARGET_PATHS = 1000
MAX_TARGET_PATH_BYTES = 4096
MAX_TARGET_TOTAL_BYTES = 1024 * 1024


def normalize_target_paths(paths):
    """Validate a bounded path snapshot without discovering any other targets."""
    if not isinstance(paths, (list, tuple)) or len(paths) > MAX_TARGET_PATHS:
        raise ValueError("At most 1000 explicit target paths are allowed")
    normalized = []
    seen = set()
    total_bytes = 0
    for raw_path in paths:
        value = os.fspath(raw_path)
        if not isinstance(value, str) or not value.strip() or "\x00" in value:
            raise ValueError("Target paths must be nonempty filesystem paths")
        if len(value) > MAX_TARGET_PATH_BYTES:
            raise ValueError("Target path exceeds the 4096-byte limit")
        path = os.path.abspath(value)
        size = len(os.fsencode(path))
        if size > MAX_TARGET_PATH_BYTES:
            raise ValueError("Target path exceeds the 4096-byte limit")
        total_bytes += size
        if total_bytes > MAX_TARGET_TOTAL_BYTES:
            raise ValueError("Explicit target paths exceed the 1 MiB total limit")
        if path not in seen:
            seen.add(path)
            normalized.append(path)
    return normalized


def resolve_target_scope(directory, target_scope="folder", target_paths=None):
    """Return a display/filter root and exact paths, or None for folder discovery."""
    if target_scope == "selected":
        paths = normalize_target_paths(target_paths)
        if not paths:
            raise ValueError("Select at least one result in the active view")
        try:
            root = os.path.commonpath([os.path.dirname(path) for path in paths])
        except ValueError:
            root = ""  # Different volumes: glob matching uses each path's parent.
        return root, paths
    if target_scope not in {"folder", "file"} or target_paths is not None:
        raise ValueError("Invalid or ambiguous target scope")
    path = normalize_target_paths([directory])[0]
    if target_scope == "file":
        if not os.path.isfile(path):
            raise ValueError("File target must be an existing regular file")
        return os.path.dirname(path), [path]
    return path, None


@dataclass
class SearchMatch:
    """Container for search match information.

    Memory optimizations (v2.9.120):
    - snippet truncated to MAX_SNIPPET_LENGTH (was unlimited)
    - context_before/after removed (were rarely used, 3x memory overhead)
    """

    line: int
    col: int
    snippet: str
    context_before: str = ""  # Deprecated: kept for compatibility but not populated
    context_after: str = ""   # Deprecated: kept for compatibility but not populated


@dataclass
class SearchResult:
    """Container for file search results."""

    file_info: FileInfo
    matches: List[SearchMatch]
    match_count: int = 0


class UnifiedFileExplorerExecutor(QObject):
    """
    Unified executor for Browse + Search + Replace operations.

    Features:
    - File listing with advanced filters
    - Content search with regex/case/word options
    - Filename pattern matching
    - Replace operations (first/all)
    - Preserve case in replacements
    - Advanced conditions (AND/OR logic)
    - Progress tracking

    Signals:
        progress: (str) Current file being processed
        progress_detailed: (int, int, str) Current, total, message
        done: (dict) Final results {files: List[SearchResult], stats: dict}
        error: (str) Error messages
    """

    progress = Signal(str)
    progress_detailed = Signal(int, int, str)
    done = Signal(dict)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._cancel = False
        self._paused = False
        self._control = threading.Condition()

    def prepare_operation(self):
        """Reset controls before dispatch, never after the user can cancel a worker."""
        with self._control:
            self._cancel = False
            self._paused = False
            self._control.notify_all()

    def checkpoint(self):
        """Wait without spinning when paused; cancellation always wakes waiters."""
        with self._control:
            while self._paused and not self._cancel:
                self._control.wait()
            return not self._cancel

    def cancel(self):
        """Cancel the operation."""
        with self._control:
            self._cancel = True
            self._paused = False
            self._control.notify_all()

    def pause(self):
        """Pause processing."""
        with self._control:
            if not self._cancel:
                self._paused = True

    def resume(self):
        """Resume processing."""
        with self._control:
            self._paused = False
            self._control.notify_all()

    # pylint: disable=too-many-positional-arguments  # Complex browse parameters required
    def execute_browse(
        self, directory: str, show_hidden: bool = False, recursive: bool = False, filters: Dict[str, Any] = None,
        conditions: List[Dict[str, Any]] = None, logic_operator: str = "AND", *, prepared: bool = False,
        target_scope: str = "folder", target_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute browse operation (list files).

        Args:
            directory: Directory path
            show_hidden: Show hidden files
            recursive: Recurse into subdirectories
            filters: Filter configuration (includes include_globs, exclude_globs)
            conditions: Advanced conditions list (v2.9.116 - Phase 4)
            logic_operator: "AND" or "OR" for conditions (v2.9.116 - Phase 4)
            target_scope: folder (default), file, or selected; explicit targets never recurse
            target_paths: Bounded exact path snapshot, only for selected scope

        Returns:
            Dict with files and statistics
        """
        if not prepared:
            self.prepare_operation()

        logger.debug(
            f"EXECUTOR execute_browse() | ENTER - "
            f"dir={directory}, recursive={recursive}, show_hidden={show_hidden}"
        )
        filters = filters or {}

        try:
            directory, paths = resolve_target_scope(directory, target_scope, target_paths)
            candidates = filters.get("candidate_paths")
            if paths is not None and candidates is not None:
                allowed = set(normalize_target_paths(candidates))
                paths = [path for path in paths if path in allowed]
            elif paths is None and candidates is not None:
                paths = candidates
        except (ValueError, TypeError, OSError, UnicodeError) as exc:
            return self._condition_failure(f"Invalid target: {exc}")

        # Step 1: Get base file list
        if paths is None:
            result = FileListExecutor.list_files(directory, show_hidden, recursive, filters, checkpoint=self.checkpoint)
        else:
            scoped = self._execute_browse_from_candidates(
                directory, paths, show_hidden, filters, explicit=target_scope != "folder"
            )
            result = ListResult([item.file_info for item in scoped["files"]], scoped["stats"]["errors"])

        file_list = result.files

        # Step 2: Apply type filter (files only, directories only, or any)
        type_filter = filters.get("type", "any")
        if type_filter == "files":
            file_list = [f for f in file_list if not f.is_dir]
        elif type_filter == "dirs":
            file_list = [f for f in file_list if f.is_dir]
        # "any" or other values: keep all files

        # Evaluate the complete expression, including content, with shared semantics.
        condition_errors = []
        if conditions:
            try:
                objects, logic = self._prepare_conditions(conditions, logic_operator)
            except (ValueError, TypeError, re.error) as exc:
                return self._condition_failure(str(exc))
            filtered = []
            for file_info in file_list:
                if not self.checkpoint():
                    break
                try:
                    if self._matches_condition_objects(file_info.path, objects, logic):
                        filtered.append(file_info)
                except (OSError, UnicodeError, ValueError) as exc:
                    if len(condition_errors) < MAX_OPERATION_ERRORS:
                        condition_errors.append(f"Condition failed for {file_info.path}: {exc}")
            file_list = filtered

        # Step 3: Apply include/exclude glob filters (from Search/Replace)
        include_globs = filters.get("include_globs", [])
        exclude_globs = filters.get("exclude_globs", [])

        if include_globs or exclude_globs:
            def matches_glob(file_path: str, file_name: str, pattern: str) -> bool:
                return self._matches_glob(file_path, file_name, pattern, directory or os.path.dirname(file_path))

            filtered_files = []
            for file_info in file_list:
                if not self.checkpoint():
                    break
                file_path = file_info.path
                file_name = file_info.name

                # Check exclude globs first (higher priority)
                excluded = False
                for pattern in exclude_globs:
                    if matches_glob(file_path, file_name, pattern):
                        excluded = True
                        break

                if excluded:
                    continue

                # Check include globs (if any)
                if include_globs:
                    included = False
                    for pattern in include_globs:
                        if matches_glob(file_path, file_name, pattern):
                            included = True
                            break

                    if not included:
                        continue

                filtered_files.append(file_info)

            file_list = filtered_files

        # Step 3: Create search results
        search_results = [SearchResult(file_info=file_info, matches=[], match_count=0) for file_info in file_list]

        stats = FileListExecutor.calculate_statistics(file_list)
        stats["errors"] = (result.errors + condition_errors)[:MAX_OPERATION_ERRORS]
        stats["cancelled"] = self._cancel
        if candidates is not None:
            stats["candidate_paths_errors"] = result.errors

        return {"files": search_results, "stats": stats}

    # pylint: disable=too-many-positional-arguments  # Complex search parameters required
    def execute_search(
        self,
        directory: str,
        filename_pattern: Optional[str] = None,
        content_query: Optional[str] = None,
        search_options: Dict[str, Any] = None,
        show_hidden: bool = False,
        recursive: bool = False,
        filters: Dict[str, Any] = None,
        conditions: List[Dict[str, Any]] = None,
        logic_operator: str = "AND",
        *, prepared: bool = False, target_scope: str = "folder", target_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute search operation (filename and/or content).

        Args:
            directory: Directory path
            filename_pattern: Wildcard pattern (*.py, test_*) or regex when filename_regex is enabled
            content_query: Text to search in file content
            search_options: {case_sensitive, whole_word, regex, filename_regex, content_scope}
            show_hidden: Show hidden files
            recursive: Recurse into subdirectories
            filters: Filter configuration
            conditions: Advanced conditions list
            logic_operator: "AND" or "OR" for conditions

        Returns:
            Dict with files and statistics
        """

        # BUGFIX: Reset cancel flag at start of each search
        # The executor instance is reused, so _cancel persists between searches
        if not prepared:
            self.prepare_operation()

        search_options = search_options or {}
        filters = dict(filters or {})
        candidate_paths = filters.get("candidate_paths")

        # Step 1: List files
        logger.debug(
            f"EXECUTOR execute_search() | Calling execute_browse("
            f"dir={directory}, show_hidden={show_hidden}, recursive={recursive})"
        )
        browse_result = self.execute_browse(
            directory, show_hidden, recursive, filters, prepared=True,
            target_scope=target_scope, target_paths=target_paths,
        )

        files_to_search = [sr.file_info for sr in browse_result["files"]]
        logger.debug(
            "[SEARCH DEBUG] Browse found %d files (recursive=%s, show_hidden=%s)",
            len(files_to_search), recursive, show_hidden
        )

        try:
            condition_objects, condition_logic = self._prepare_conditions(conditions, logic_operator)
        except (ValueError, TypeError, re.error) as exc:
            return self._condition_failure(str(exc))
        condition_errors = list(browse_result["stats"].get("errors", []))[:MAX_OPERATION_ERRORS]

        # Step 2: Apply filename pattern filter
        if filename_pattern:
            before_filter = len(files_to_search)
            if search_options.get("filename_regex", False):
                try:
                    flags = 0 if search_options.get("case_sensitive", False) else re.IGNORECASE
                    filename_regex = re.compile(filename_pattern, flags)
                except re.error as e:
                    error_message = f"Invalid filename regex pattern: {e}"
                    logger.error("%s | pattern=%s", error_message, filename_pattern[:50], exc_info=True)
                    self.error.emit(error_message)
                    stats = FileListExecutor.calculate_statistics([])
                    stats["errors"] = [error_message]
                    stats["total_matches"] = 0
                    stats["files_with_matches"] = 0
                    return {"files": [], "stats": stats}

                files_to_search = [
                    f for f in files_to_search if not f.is_dir and filename_regex.search(f.name.rstrip("/"))
                ]
                filename_filter_mode = "regex"
            else:
                files_to_search = [
                    f for f in files_to_search if not f.is_dir and fnmatch.fnmatch(f.name.rstrip("/"), filename_pattern)
                ]
                filename_filter_mode = "glob"

            logger.debug(
                "EXECUTOR execute_search() | After filename %s filter: %d → %d files",
                filename_filter_mode,
                before_filter,
                len(files_to_search),
            )
            logger.debug(
                "[SEARCH DEBUG] Filename pattern '%s' (%s) filter: %d → %d files",
                filename_pattern, filename_filter_mode, before_filter, len(files_to_search)
            )

        # Step 3: Apply content search
        search_results = []
        total_files = len(files_to_search)
        total_match_count = 0  # Track total matches across all files (v2.9.120)
        content_scope = self._normalize_content_scope(search_options.get("content_scope", CONTENT_SCOPE_TEXT))
        text_files_searched = 0
        binary_files_searched = 0
        content_scope_skipped = 0

        for idx, file_info in enumerate(files_to_search, 1):
            if not self.checkpoint():
                break

            # Check global match limit (v2.9.120 - Memory optimization)
            if total_match_count >= MAX_TOTAL_MATCHES:
                warning_msg = (
                    f"Maximum total matches reached ({MAX_TOTAL_MATCHES:,}). "
                    "Search stopped. Refine your search for better results."
                )
                logger.warning(warning_msg, extra={"total_matches": total_match_count, "files_processed": idx})
                self.error.emit(warning_msg)
                break

            self.progress.emit(file_info.path)
            self.progress_detailed.emit(idx, total_files, file_info.path)

            # Skip directories for content search
            if file_info.is_dir:
                continue

            try:
                # If no content query, just list matching files
                condition_cache = {}
                if not self._matches_condition_objects(
                    file_info.path, condition_objects, condition_logic, condition_cache
                ):
                    continue
                if not content_query:
                    search_results.append(SearchResult(file_info=file_info, matches=[], match_count=0))
                    continue

                file_kind = self._classify_content_file(file_info.path)
                if not self._content_scope_allows(file_kind, content_scope):
                    content_scope_skipped += 1
                    continue

                if file_kind == CONTENT_SCOPE_BINARY:
                    binary_files_searched += 1
                    matches = self._search_in_binary_file(file_info.path, content_query, search_options)
                else:
                    text_files_searched += 1
                    text = condition_cache["text"] if "text" in condition_cache else read_text(file_info.path)
                    matches = self._search_in_text(text, content_query, search_options)

                if matches:
                    search_results.append(SearchResult(file_info=file_info, matches=matches, match_count=len(matches)))
                    total_match_count += len(matches)  # Update total counter

            except Exception as e:  # pylint: disable=broad-exception-caught  # File search robustness
                if len(condition_errors) < MAX_OPERATION_ERRORS:
                    condition_errors.append(f"Error processing {file_info.path}: {e}")



        # Calculate statistics
        file_infos = [sr.file_info for sr in search_results]
        stats = FileListExecutor.calculate_statistics(file_infos)
        stats["total_matches"] = sum(sr.match_count for sr in search_results)
        stats["files_with_matches"] = sum(1 for sr in search_results if sr.match_count > 0)
        stats["errors"] = condition_errors
        stats["cancelled"] = self._cancel
        if candidate_paths is not None:
            stats["incremental_universe"] = True
            stats["candidate_paths_count"] = len(candidate_paths)
            stats["candidate_paths_errors"] = browse_result["stats"].get("candidate_paths_errors", [])
        if content_query:
            stats["content_scope"] = content_scope
            stats["text_files_searched"] = text_files_searched
            stats["binary_files_searched"] = binary_files_searched
            stats["content_scope_skipped"] = content_scope_skipped

        logger.debug("[SEARCH DEBUG] Final results: %d files, %d matches", len(search_results), stats["total_matches"])

        # Log memory optimization stats (v2.9.120)
        if stats["total_matches"] > 0:
            logger.info(
                "Search completed with memory optimizations",
                extra={
                    "total_matches": stats["total_matches"],
                    "files_with_matches": stats["files_with_matches"],
                    "truncated_snippets": True,
                    "max_snippet_length": MAX_SNIPPET_LENGTH,
                    "hit_global_limit": total_match_count >= MAX_TOTAL_MATCHES,
                },
            )

        return {"files": search_results, "stats": stats}

    def _execute_browse_from_candidates(
        self, directory: str, candidate_paths: List[str], show_hidden: bool, filters: Dict[str, Any],
        *, explicit: bool = False,
    ) -> Dict[str, Any]:
        """Build search candidates from an explicit prior-result universe."""
        directory_abs = os.path.abspath(directory) if directory else ""
        filters_without_candidates = dict(filters)
        filters_without_candidates.pop("candidate_paths", None)

        type_filter = filters_without_candidates.get("type", "any")
        include_globs = filters_without_candidates.get("include_globs", [])
        exclude_globs = filters_without_candidates.get("exclude_globs", [])
        file_list: List[FileInfo] = []
        errors: List[str] = []
        seen_paths = set()

        for raw_path in candidate_paths:
            if explicit and len(errors) >= MAX_OPERATION_ERRORS:
                errors[-1] += "; target error limit reached; remaining targets were not processed"
                break
            if not self.checkpoint():
                break
            try:
                path = os.path.abspath(str(raw_path))
                if path in seen_paths:
                    continue
                seen_paths.add(path)

                if not explicit and os.path.commonpath([directory_abs, path]) != directory_abs:
                    errors.append(f"Candidate outside directory ignored: {raw_path}")
                    continue

                if not os.path.exists(path):
                    errors.append(f"Candidate no longer exists: {raw_path}")
                    continue

                root = directory_abs or os.path.dirname(path)
                rel_path = os.path.relpath(path, root)
                if not explicit and not show_hidden and self._path_has_hidden_part(rel_path):
                    continue

                file_info = FileListExecutor._get_file_info(path)
                if type_filter == "files" and file_info.is_dir:
                    continue
                if type_filter == "dirs" and not file_info.is_dir:
                    continue

                if not file_info.is_dir:
                    depth = self._relative_file_depth(rel_path)
                    if not FileListExecutor._matches_filters(
                        path, os.path.basename(path), depth, filters_without_candidates
                    ):
                        continue

                excluded = any(
                    self._matches_glob(path, file_info.name.rstrip("/"), pattern, root)
                    for pattern in exclude_globs
                )
                if excluded:
                    continue

                if include_globs and not any(
                    self._matches_glob(path, file_info.name.rstrip("/"), pattern, root)
                    for pattern in include_globs
                ):
                    continue

                file_list.append(file_info)
            except Exception as exc:  # pylint: disable=broad-exception-caught  # Candidate robustness
                errors.append(f"Error accessing candidate {raw_path}: {exc}")

        search_results = [SearchResult(file_info=file_info, matches=[], match_count=0) for file_info in file_list]
        stats = FileListExecutor.calculate_statistics(file_list)
        stats["errors"] = errors
        stats["candidate_paths_errors"] = errors
        return {"files": search_results, "stats": stats}

    @staticmethod
    def _path_has_hidden_part(relative_path: str) -> bool:
        """Return True if any relative path component is hidden."""
        return any(part.startswith(".") for part in relative_path.split(os.sep) if part not in ("", "."))

    @staticmethod
    def _relative_file_depth(relative_path: str) -> int:
        """Return FileListExecutor-compatible recursive depth for a file path."""
        parent = os.path.dirname(relative_path)
        if parent in ("", "."):
            return 0
        return len([part for part in parent.split(os.sep) if part])

    @staticmethod
    def _matches_glob(file_path: str, file_name: str, pattern: str, directory: str) -> bool:
        """Match path/name using the same glob semantics used by browse mode."""
        rel_path = os.path.relpath(file_path, directory)
        rel_path_posix = rel_path.replace(os.sep, "/")
        path_posix = file_path.replace(os.sep, "/")

        return (
            pattern in file_path.split(os.sep)
            or fnmatch.fnmatch(file_name, pattern)
            or fnmatch.fnmatch(rel_path, pattern)
            or fnmatch.fnmatch(rel_path_posix, pattern)
            or fnmatch.fnmatch(file_path, pattern)
            or fnmatch.fnmatch(path_posix, pattern)
        )

    # pylint: disable=too-many-positional-arguments  # Complex replace parameters required
    def execute_replace(
        self,
        files: List[SearchResult],
        search_query: str,
        replacement: str,
        preserve_case: bool = False,
        replace_all: bool = False,
        search_options: Dict[str, bool] = None,
        *, prepared: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute replace operation.

        Args:
            files: List of SearchResult objects
            search_query: Text to search for
            replacement: Replacement text
            preserve_case: Preserve original case
            replace_all: Replace all occurrences (vs first only)
            search_options: {case_sensitive, whole_word, regex}

        Returns:
            Dict with replacement results
        """
        if not prepared:
            self.prepare_operation()
        search_options = search_options or {}
        replaced_count = 0
        files_modified = 0
        errors = []

        def outcome():
            return {
                "success": not errors and not self._cancel,
                "cancelled": self._cancel,
                "replaced_count": replaced_count,
                "replacements_made": replaced_count,
                "files_modified": files_modified,
                "errors": errors,
                "error": "\n".join(errors) or ("Operation cancelled" if self._cancel else ""),
            }

        if not search_query or len(files) > MAX_REPLACE_FILES:
            errors.append("A nonempty query and at most 1000 selected files are required")
            return outcome()
        if search_options.get("multi_query"):
            errors.append("Replacement of independent multi-queries is not supported")
            return outcome()
        if any(len(value) > MAX_REPLACE_FILE_BYTES or len(value.encode("utf-8")) > MAX_REPLACE_FILE_BYTES
               for value in (search_query, replacement)):
            errors.append("Replacement query or value exceeds the 4 MiB limit")
            return outcome()
        try:
            self._compile_replace_pattern(search_query, search_options)
        except re.error as exc:
            errors.append(f"Invalid replacement regex: {exc}")
            return outcome()

        seen = set()
        for search_result in files:
            if not self.checkpoint():
                break
            file_path = os.path.abspath(search_result.file_info.path)
            if file_path in seen:
                continue
            seen.add(file_path)
            self.progress.emit(f"Replacing in {file_path}")
            try:
                info = os.lstat(file_path)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("Replacement requires a regular file without links")
                if info.st_size > MAX_REPLACE_FILE_BYTES:
                    raise ValueError("Text replacement file exceeds the 4 MiB limit")
                if self._classify_content_file(file_path) == CONTENT_SCOPE_BINARY:
                    raise ValueError("replace supports text files only; skipped binary file")
                with open(file_path, "rb") as source:
                    raw = source.read(MAX_REPLACE_FILE_BYTES + 1)
                if len(raw) > MAX_REPLACE_FILE_BYTES:
                    raise ValueError("Text replacement file exceeds the 4 MiB limit")
                content = raw.decode("utf-8")
                new_content, count = self._replace_in_text(
                    content, search_query, replacement, preserve_case, replace_all, search_options
                )
                if count > 0:
                    if not self.checkpoint():
                        break
                    write_existing_text_atomically(file_path, new_content, file_revision(info))
                    replaced_count += count
                    files_modified += 1
            except (OSError, UnicodeError, ValueError, re.error) as exc:
                errors.append(f"Error replacing in {file_path}: {exc}")
                if len(errors) >= MAX_OPERATION_ERRORS:
                    errors[-1] += "; error limit reached; remaining files were not processed"
                    break
        return outcome()

    @staticmethod
    def _normalize_content_scope(scope: str) -> str:
        """Normalize content search scope to a supported value."""
        if scope in {CONTENT_SCOPE_TEXT, CONTENT_SCOPE_BINARY, CONTENT_SCOPE_BOTH}:
            return scope
        return CONTENT_SCOPE_TEXT

    @staticmethod
    def _classify_content_file(path: str) -> str:
        """Classify a file as text or binary using a bounded byte sample."""
        with open(path, "rb") as fh:
            sample = fh.read(TEXT_SAMPLE_BYTES)

        if not sample:
            return CONTENT_SCOPE_TEXT

        if b"\x00" in sample:
            return CONTENT_SCOPE_BINARY

        try:
            sample.decode("utf-8")
        except UnicodeDecodeError:
            return CONTENT_SCOPE_BINARY

        allowed_controls = {7, 8, 9, 10, 12, 13, 27}
        control_count = sum(1 for byte in sample if byte < 32 and byte not in allowed_controls)
        if control_count / len(sample) > 0.30:
            return CONTENT_SCOPE_BINARY

        return CONTENT_SCOPE_TEXT

    @staticmethod
    def _content_scope_allows(file_kind: str, content_scope: str) -> bool:
        """Return whether a classified file should be searched for the selected content scope."""
        if content_scope == CONTENT_SCOPE_BOTH:
            return True
        return file_kind == content_scope

    def _search_in_text(self, text: str, query: str, options: Dict[str, bool]) -> List[SearchMatch]:
        """Search for query in text and return matches."""
        matches = []

        case_sensitive = options.get("case_sensitive", False)
        whole_word = options.get("whole_word", False)
        use_regex = options.get("regex", False)

        try:
            # Build regex pattern
            if use_regex:
                pattern = query
            else:
                pattern = re.escape(query)

            # Add word boundaries if needed
            if whole_word:
                pattern = r"\b" + pattern + r"\b"

            # Compile with case sensitivity
            # SECURITY OWASP A03: Regex DoS Prevention
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:  # pylint: disable=broad-exception-caught  # Regex validation
                logger.error("Invalid regex pattern: %s", pattern[:50], exc_info=True)
                self.error.emit(f"Invalid regex pattern: {e}")
                return []

            # Find all matches with timeout protection
            # SECURITY: Prevent ReDoS (Regular Expression Denial of Service)
            # Note: Python's re module doesn't have built-in timeout
            # For production, consider using regex module with timeout parameter
            lines = text.splitlines()
            match_count = 0
            MAX_MATCHES_PER_FILE = 10000  # pylint: disable=invalid-name  # Constant

            for line_num, line_text in enumerate(lines, 1):
                if not self.checkpoint():
                    break

                try:
                    for match in regex.finditer(line_text):
                        if not self.checkpoint():
                            break
                        if match_count >= MAX_MATCHES_PER_FILE:
                            logger.warning("Max matches reached: %d", MAX_MATCHES_PER_FILE)
                            self.error.emit(f"Too many matches (>{MAX_MATCHES_PER_FILE}). Results truncated.")
                            return matches

                        col = match.start()

                        # Memory optimization (v2.9.120): Truncate snippet and remove context lines
                        # - Limits snippet to MAX_SNIPPET_LENGTH (200 chars)
                        # - Removes context_before/after (3x memory reduction)
                        truncated_snippet = (
                            line_text[:MAX_SNIPPET_LENGTH]
                            if len(line_text) > MAX_SNIPPET_LENGTH
                            else line_text
                        )

                        matches.append(
                            SearchMatch(
                                line=line_num,
                                col=col,
                                snippet=truncated_snippet,
                                context_before="",  # Removed for memory optimization
                                context_after="",   # Removed for memory optimization
                            )
                        )
                        match_count += 1

                except Exception:  # pylint: disable=broad-exception-caught  # Regex safety
                    # Catch potential regex matching errors (e.g., catastrophic backtracking)
                    logger.error("Error matching regex on line %d", line_num, exc_info=True)
                    # Continue with next line instead of failing entire operation
                    continue

        except re.error as e:
            logger.error("Regex compilation error: %s", e, exc_info=True)
            self.error.emit(f"Invalid regex pattern: {e}")
        except Exception as e:  # pylint: disable=broad-exception-caught  # Search robustness
            logger.error("Unexpected error in search: %s", e, exc_info=True)
            self.error.emit(f"Search error: {e}")

        return matches

    def _search_in_binary_file(self, path: str, query: str, options: Dict[str, bool]) -> List[SearchMatch]:
        """Search for UTF-8 query bytes in a binary file without loading it all in memory."""
        query_bytes = query.encode("utf-8")
        if not query_bytes:
            return []

        use_regex = options.get("regex", False)
        whole_word = options.get("whole_word", False)
        case_sensitive = options.get("case_sensitive", False)

        pattern = query_bytes if use_regex else re.escape(query_bytes)
        if whole_word:
            pattern = rb"\b" + pattern + rb"\b"

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            logger.error("Invalid binary regex pattern: %s", pattern[:50], exc_info=True)
            self.error.emit(f"Invalid regex pattern: {e}")
            return []

        if use_regex:
            overlap = BINARY_REGEX_OVERLAP_BYTES
        else:
            overlap = min(max(len(query_bytes) - 1, 0), BINARY_SEARCH_CHUNK_SIZE)

        matches: List[SearchMatch] = []
        carry = b""
        file_offset = 0
        match_count = 0
        max_matches_per_file = 10000

        with open(path, "rb") as fh:
            while True:
                if not self.checkpoint():
                    break

                chunk = fh.read(BINARY_SEARCH_CHUNK_SIZE)
                if not chunk:
                    break

                window = carry + chunk
                window_base_offset = file_offset - len(carry)
                new_data_start = len(carry)

                for match in regex.finditer(window):
                    if not self.checkpoint():
                        break
                    if match.end() <= new_data_start:
                        continue
                    if match_count >= max_matches_per_file:
                        logger.warning("Max binary matches reached: %d", max_matches_per_file)
                        self.error.emit(f"Too many matches (>{max_matches_per_file}). Results truncated.")
                        return matches

                    absolute_offset = window_base_offset + match.start()
                    snippet = self._format_binary_snippet(window, match.start(), match.end(), absolute_offset)
                    matches.append(SearchMatch(line=1, col=absolute_offset, snippet=snippet))
                    match_count += 1

                file_offset += len(chunk)
                carry = window[-overlap:] if overlap else b""

        return matches

    @staticmethod
    def _format_binary_snippet(window: bytes, match_start: int, match_end: int, absolute_offset: int) -> str:
        """Format a safe bounded binary snippet around a match."""
        context_start = max(0, match_start - BINARY_SNIPPET_CONTEXT_BYTES)
        context_end = min(len(window), match_end + BINARY_SNIPPET_CONTEXT_BYTES)
        snippet_bytes = window[context_start:context_end]
        preview_bytes = snippet_bytes[:64]
        hex_preview = preview_bytes.hex(" ")
        ascii_preview = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in preview_bytes)
        if len(snippet_bytes) > len(preview_bytes):
            hex_preview += " ..."
            ascii_preview += "..."
        snippet = f"bytes {absolute_offset}-{absolute_offset + (match_end - match_start)}: {hex_preview} | {ascii_preview}"
        return snippet[:MAX_SNIPPET_LENGTH]

    # pylint: disable=too-many-positional-arguments  # Complex replace parameters required
    def _replace_in_text(
        self, text: str, query: str, replacement: str, preserve_case: bool, replace_all: bool, options: Dict[str, bool]
    ) -> Tuple[str, int]:
        """
        Replace query with replacement in text.

        Returns:
            Tuple of (new_text, replacement_count)
        """
        if not query:
            raise ValueError("Replacement query must not be empty")
        regex = self._compile_replace_pattern(query, options)
        fragments = []
        last_end = 0
        count = 0
        output_bytes = 0
        for match in regex.finditer(text):
            if not self.checkpoint():
                return text, 0
            if count >= MAX_REPLACE_MATCHES:
                raise ValueError("Replacement exceeds the 10000 matches per file limit")
            value = match.expand(replacement) if options.get("regex") else replacement
            if preserve_case:
                value = preserve_case_like(match.group(0), value)
            prefix = text[last_end:match.start()]
            output_bytes += len(prefix.encode("utf-8")) + len(value.encode("utf-8"))
            if output_bytes > MAX_REPLACE_FILE_BYTES:
                raise ValueError("Replacement output exceeds the 4 MiB limit")
            fragments.extend((prefix, value))
            last_end = match.end()
            count += 1
            if not replace_all:
                break
        suffix = text[last_end:]
        if output_bytes + len(suffix.encode("utf-8")) > MAX_REPLACE_FILE_BYTES:
            raise ValueError("Replacement output exceeds the 4 MiB limit")
        fragments.append(suffix)
        return "".join(fragments), count

    @staticmethod
    def _compile_replace_pattern(query, options):
        pattern = query if options.get("regex") else re.escape(query)
        if options.get("whole_word"):
            pattern = r"\b(?:" + pattern + r")\b"
        return re.compile(pattern, 0 if options.get("case_sensitive") else re.IGNORECASE)

    def _replace_preserve_case(
        self, text: str, pattern: re.Pattern, replacement: str, count: int = 0
    ) -> Tuple[str, int]:
        """Replace with case preservation."""
        replaced = 0
        result = []
        last_end = 0

        for match in pattern.finditer(text):
            # Add text before match
            result.append(text[last_end : match.start()])

            # Determine case pattern of original
            original = match.group(0)
            new_text = self._apply_case_pattern(original, replacement)
            result.append(new_text)

            last_end = match.end()
            replaced += 1

            # Stop if we've replaced enough
            if 0 < count <= replaced:
                result.append(text[last_end:])
                break
        else:
            # Add remaining text
            result.append(text[last_end:])

        return "".join(result), replaced

    @staticmethod
    def _apply_case_pattern(original: str, replacement: str) -> str:
        """Apply case pattern from original to replacement."""
        return preserve_case_like(original, replacement)

    @staticmethod
    def _prepare_conditions(conditions, logic_operator):
        from .filters import Condition

        if not isinstance(logic_operator, str):
            raise ValueError("Condition logic must be AND or OR")
        logic = logic_operator.upper()
        if logic not in {"AND", "OR"}:
            raise ValueError("Condition logic must be AND or OR")
        return [Condition.from_mapping(data) for data in (conditions or [])], logic

    @staticmethod
    def _condition_failure(message):
        stats = FileListExecutor.calculate_statistics([])
        stats.update(errors=[f"Invalid conditions: {message}"], total_matches=0, files_with_matches=0)
        return {"files": [], "stats": stats}

    def _matches_condition_objects(self, path, objects, logic, content_cache=None):
        cache = content_cache if content_cache is not None else {}

        def evaluate(condition):
            if not self.checkpoint():
                return False
            if condition.field != "content":
                return condition.matches(path)
            if not os.path.isfile(path):
                return False
            if "text" not in cache:
                if os.path.getsize(path) > MAX_REPLACE_FILE_BYTES:
                    raise ValueError("Content condition file exceeds the 4 MiB limit")
                if self._classify_content_file(path) != CONTENT_SCOPE_TEXT:
                    raise ValueError("Content conditions require UTF-8 text, not binary files")
                with open(path, "rb") as source:
                    raw = source.read(MAX_REPLACE_FILE_BYTES + 1)
                if len(raw) > MAX_REPLACE_FILE_BYTES:
                    raise ValueError("Content condition file exceeds the 4 MiB limit")
                cache["text"] = raw.decode("utf-8")
            return condition.matches(path, content=cache["text"])

        if not objects:
            return True
        if logic == "AND":
            return all(evaluate(condition) for condition in objects)
        first_error = None
        for condition in objects:
            try:
                if evaluate(condition):
                    return True
            except (OSError, UnicodeError, ValueError) as exc:
                first_error = first_error or exc
        if first_error is not None:
            raise first_error
        return False

    def _apply_conditions(self, results, conditions, logic_operator):
        """Compatibility entry point using the complete shared expression."""
        objects, logic = self._prepare_conditions(conditions, logic_operator)
        return [result for result in results if self._matches_condition_objects(
            result.file_info.path, objects, logic
        )]

    def _check_condition(self, result, condition):
        return bool(self._apply_conditions([result], [condition], "AND"))


__all__ = ["UnifiedFileExplorerExecutor", "SearchResult", "SearchMatch"]
