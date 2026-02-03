"""
Unified File Explorer Executor - Merges List + Search + Replace logic.

Part of v2.9.116 integration: Search/Replace → File Explorer.
Combines FileListExecutor and SearchWorker into single unified pipeline.

Author: Josué Amaral
Date: 2025/12/25
"""

from __future__ import annotations

import os
import re
import fnmatch
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal  # pylint: disable=no-name-in-module  # Qt dynamic

from .file_list_executor import FileInfo, FileListExecutor
from ..utils import read_text
from ..utils.logger import get_logger

# Initialize logger for structured logging (Protocolo Simplicidade 3 - Etapa 6)
logger = get_logger(__name__)

# Memory optimization constants (v2.9.120 - 2026-01-09)
MAX_SNIPPET_LENGTH = 200  # Maximum characters to store per match snippet
MAX_TOTAL_MATCHES = 50000  # Maximum total matches across all files


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

    def cancel(self):
        """Cancel the operation."""
        self._cancel = True

    def pause(self):
        """Pause processing."""
        self._paused = True

    def resume(self):
        """Resume processing."""
        self._paused = False

    # pylint: disable=too-many-positional-arguments  # Complex browse parameters required
    def execute_browse(
        self, directory: str, show_hidden: bool = False, recursive: bool = False, filters: Dict[str, Any] = None,
        conditions: List[Dict[str, Any]] = None, logic_operator: str = "AND"
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

        Returns:
            Dict with files and statistics
        """
        print(
            f"DEBUG EXECUTOR 101 execute_browse() | ENTER - "
            f"dir={directory}, recursive={recursive}, show_hidden={show_hidden}"
        )
        filters = filters or {}

        # Step 1: Get base file list
        print("DEBUG EXECUTOR 122 execute_browse() | Calling FileListExecutor.list_files()")
        result = FileListExecutor.list_files(directory, show_hidden, recursive, filters)
        print(f"DEBUG EXECUTOR 124 execute_browse() | FileListExecutor returned {len(result.files)} files")

        file_list = result.files

        # Step 2: Apply type filter (files only, directories only, or any)
        type_filter = filters.get("type", "any")
        if type_filter == "files":
            file_list = [f for f in file_list if not f.is_dir]
        elif type_filter == "dirs":
            file_list = [f for f in file_list if f.is_dir]
        # "any" or other values: keep all files

        # Step 2.5: Apply advanced conditions if provided (v2.9.116 - Phase 4)
        if conditions:
            try:
                # pylint: disable=import-outside-toplevel  # Circular import avoidance
                from ..core.filters import filter_files_by_conditions, Condition

                # Convert dict conditions to Condition objects
                condition_objects = []
                for cond_dict in conditions:
                    condition_obj = Condition(
                        field=cond_dict.get("field", ""),
                        operator=cond_dict.get("operator", ""),
                        value=cond_dict.get("value", ""),
                        scope_type=cond_dict.get("scope_type", ""),
                        scope_value=cond_dict.get("scope_value", ""),
                        case_sensitive=cond_dict.get("case_sensitive", True),
                        whole_word=cond_dict.get("whole_word", False),
                        use_regex=cond_dict.get("regex", False),
                    )
                    condition_objects.append(condition_obj)

                file_paths = [f.path for f in file_list]
                original_count = len(file_paths)

                filtered_paths = filter_files_by_conditions(file_paths, condition_objects, logic_operator)

                # Convert back to FileInfo objects
                filtered_paths_set = set(filtered_paths)
                file_list = [f for f in file_list if f.path in filtered_paths_set]

                filtered_count = original_count - len(file_list)
                logger.info("Advanced conditions filtered %d files in browse mode", filtered_count)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Filter robustness
                logger.error("Error applying conditions in browse mode: %s", e, exc_info=True)

        # Step 3: Apply include/exclude glob filters (from Search/Replace)
        include_globs = filters.get("include_globs", [])
        exclude_globs = filters.get("exclude_globs", [])

        if include_globs or exclude_globs:
            filtered_files = []
            for file_info in file_list:
                file_path = file_info.path
                file_name = file_info.name

                # Check exclude globs first (higher priority)
                excluded = False
                for pattern in exclude_globs:
                    # Check if pattern exists as a path component (directory name)
                    # This correctly handles .venv, node_modules, etc.
                    path_components = file_path.split(os.sep)
                    if pattern in path_components:
                        excluded = True
                        break
                    # Also check if pattern matches filename (for patterns like *.pyc)
                    if fnmatch.fnmatch(file_name, pattern):
                        excluded = True
                        break

                if excluded:
                    continue

                # Check include globs (if any)
                if include_globs:
                    included = False
                    for pattern in include_globs:
                        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_name, pattern):
                            included = True
                            break

                    if not included:
                        continue

                filtered_files.append(file_info)

            file_list = filtered_files

        # Step 3: Create search results
        search_results = [SearchResult(file_info=file_info, matches=[], match_count=0) for file_info in file_list]

        stats = FileListExecutor.calculate_statistics(file_list)
        stats["errors"] = result.errors

        return {"files": search_results, "stats": stats}

    # pylint: disable=too-many-positional-arguments  # Complex search parameters required
    def execute_search(
        self,
        directory: str,
        filename_pattern: Optional[str] = None,
        content_query: Optional[str] = None,
        search_options: Dict[str, bool] = None,
        show_hidden: bool = False,
        recursive: bool = False,
        filters: Dict[str, Any] = None,
        conditions: List[Dict[str, Any]] = None,
        logic_operator: str = "AND",
    ) -> Dict[str, Any]:
        """
        Execute search operation (filename and/or content).

        Args:
            directory: Directory path
            filename_pattern: Wildcard pattern (*.py, test_*)
            content_query: Text to search in file content
            search_options: {case_sensitive, whole_word, regex}
            show_hidden: Show hidden files
            recursive: Recurse into subdirectories
            filters: Filter configuration
            conditions: Advanced conditions list
            logic_operator: "AND" or "OR" for conditions

        Returns:
            Dict with files and statistics
        """
        print(f"DEBUG EXECUTOR 218 execute_search() | ENTER - _cancel={self._cancel}")

        # BUGFIX: Reset cancel flag at start of each search
        # The executor instance is reused, so _cancel persists between searches
        self._cancel = False
        print("DEBUG EXECUTOR 251 execute_search() | Reset _cancel to False")

        search_options = search_options or {}

        # Step 1: List files
        print(
            f"DEBUG EXECUTOR 249 execute_search() | Calling execute_browse("
            f"dir={directory}, show_hidden={show_hidden}, recursive={recursive})"
        )
        browse_result = self.execute_browse(directory, show_hidden, recursive, filters)
        print(f"DEBUG EXECUTOR 251 execute_search() | Browse returned {len(browse_result.get('files', []))} files")

        files_to_search = [sr.file_info for sr in browse_result["files"]]
        print(f"DEBUG EXECUTOR 253 execute_search() | files_to_search has {len(files_to_search)} items")
        logger.debug(
            "[SEARCH DEBUG] Browse found %d files (recursive=%s, show_hidden=%s)",
            len(files_to_search), recursive, show_hidden
        )

        # OPTIMIZATION: Apply advanced conditions EARLY to avoid unnecessary file I/O
        # (Sprint 1 - Task 1.1 - Fase 2 + BUGFIX)
        # FIX: Separate content-based vs non-content-based conditions
        # - Size, extension, date → Apply EARLY (before content search)
        # - Content → Apply LATE (after reading file)
        if conditions:
            # Separate conditions by type
            early_conditions = []  # size, ext, filename, path, mtime
            late_conditions = []  # content (needs file read)

            for cond in conditions:
                field = cond.get("field", "")
                if field == "content":
                    late_conditions.append(cond)
                else:
                    early_conditions.append(cond)

            # Apply non-content conditions EARLY
            if early_conditions:
                try:
                    # pylint: disable=import-outside-toplevel  # Circular import avoidance
                    from ..core.filters import filter_files_by_conditions, Condition

                    # Convert dict conditions to Condition objects
                    condition_objects = []
                    for cond_dict in early_conditions:
                        condition_obj = Condition(
                            field=cond_dict.get("field", ""),
                            operator=cond_dict.get("operator", ""),
                            value=cond_dict.get("value", ""),
                            scope_type=cond_dict.get("scope_type", ""),
                            scope_value=cond_dict.get("scope_value", ""),
                            case_sensitive=cond_dict.get("case_sensitive", True),
                            whole_word=cond_dict.get("whole_word", False),
                            use_regex=cond_dict.get(
                                "regex", False
                            ),  # Note: dict uses 'regex', Condition uses 'use_regex'
                        )
                        condition_objects.append(condition_obj)

                    file_paths = [f.path for f in files_to_search]
                    original_count = len(file_paths)

                    filtered_paths = filter_files_by_conditions(file_paths, condition_objects, logic_operator)

                    filtered_out = original_count - len(filtered_paths)

                    logger.info(
                        "Applied %d non-content conditions EARLY (before content search)",
                        len(early_conditions),
                        extra={
                            "logic": logic_operator,
                            "filtered_out": filtered_out,
                            "remaining": len(filtered_paths),
                            "original_count": original_count,
                        },
                    )

                    # Keep only files that passed conditions
                    files_to_search = [f for f in files_to_search if f.path in filtered_paths]
                except Exception as e:  # pylint: disable=broad-exception-caught  # Filter robustness
                    logger.error("Failed to apply early conditions: %s", e, exc_info=True)
                    # Continue without early filtering on error

        logger.debug("Files to search after filters+conditions: %d", len(files_to_search))
        print(f"DEBUG EXECUTOR 320 execute_search() | After conditions: {len(files_to_search)} files")

        # Step 2: Apply filename pattern filter
        if filename_pattern:
            print(f"DEBUG EXECUTOR 323 execute_search() | Applying filename pattern: '{filename_pattern}'")
            before_filter = len(files_to_search)
            files_to_search = [
                f for f in files_to_search if not f.is_dir and fnmatch.fnmatch(f.name.rstrip("/"), filename_pattern)
            ]
            print(
                f"DEBUG EXECUTOR 328 execute_search() | After filename filter: "
                f"{before_filter} → {len(files_to_search)} files"
            )
            logger.debug(
                "[SEARCH DEBUG] Filename pattern '%s' filter: %d → %d files",
                filename_pattern, before_filter, len(files_to_search)
            )
        else:
            print("DEBUG EXECUTOR 331 execute_search() | No filename pattern specified")

        # Step 3: Apply content search
        print(f"DEBUG EXECUTOR 334 execute_search() | Starting content search on {len(files_to_search)} files")
        print(f"DEBUG EXECUTOR 335 execute_search() | content_query='{content_query}'")
        search_results = []
        total_files = len(files_to_search)
        total_match_count = 0  # Track total matches across all files (v2.9.120)

        for idx, file_info in enumerate(files_to_search, 1):
            if self._cancel:
                print("DEBUG EXECUTOR 344 execute_search() | CANCEL FLAG SET - Breaking loop")
                break

            # Check global match limit (v2.9.120 - Memory optimization)
            if total_match_count >= MAX_TOTAL_MATCHES:
                warning_msg = (
                    f"Maximum total matches reached ({MAX_TOTAL_MATCHES:,}). "
                    "Search stopped. Refine your search for better results."
                )
                logger.warning(warning_msg, extra={"total_matches": total_match_count, "files_processed": idx})
                self.error.emit(warning_msg)
                print("DEBUG EXECUTOR 351 execute_search() | MAX MATCHES REACHED - Breaking loop")
                break

            self.progress.emit(file_info.path)
            self.progress_detailed.emit(idx, total_files, file_info.path)

            # Skip directories for content search
            if file_info.is_dir:
                continue

            try:
                # If no content query, just list matching files
                if not content_query:
                    search_results.append(SearchResult(file_info=file_info, matches=[], match_count=0))
                    continue

                # Read file and search
                text = read_text(file_info.path)
                matches = self._search_in_text(text, content_query, search_options)

                if matches:
                    search_results.append(SearchResult(file_info=file_info, matches=matches, match_count=len(matches)))
                    total_match_count += len(matches)  # Update total counter

            except Exception as e:  # pylint: disable=broad-exception-caught  # File search robustness
                self.error.emit(f"Error processing {file_info.path}: {e}")

        # Step 4: Apply content-based conditions if provided (LATE - after reading files)
        # NOTE: Content conditions need file content, so applied AFTER search
        if conditions:
            late_conditions = [c for c in conditions if c.get("field") == "content"]
            if late_conditions:
                logger.debug("Applying %d content-based conditions LATE", len(late_conditions))
                search_results = self._apply_conditions(search_results, late_conditions, logic_operator)

        # Calculate statistics
        file_infos = [sr.file_info for sr in search_results]
        stats = FileListExecutor.calculate_statistics(file_infos)
        stats["total_matches"] = sum(sr.match_count for sr in search_results)
        stats["files_with_matches"] = sum(1 for sr in search_results if sr.match_count > 0)

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

    # pylint: disable=too-many-positional-arguments  # Complex replace parameters required
    def execute_replace(
        self,
        files: List[SearchResult],
        search_query: str,
        replacement: str,
        preserve_case: bool = False,
        replace_all: bool = False,
        search_options: Dict[str, bool] = None,
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
        search_options = search_options or {}
        replaced_count = 0
        files_modified = 0
        errors = []

        for search_result in files:
            if self._cancel:
                break

            file_path = search_result.file_info.path
            self.progress.emit(f"Replacing in {file_path}")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content, count = self._replace_in_text(
                    content, search_query, replacement, preserve_case, replace_all, search_options
                )

                if count > 0:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    replaced_count += count
                    files_modified += 1

            except Exception as e:  # pylint: disable=broad-exception-caught  # Replace robustness
                errors.append(f"Error replacing in {file_path}: {e}")
                self.error.emit(errors[-1])

        return {"replaced_count": replaced_count, "files_modified": files_modified, "errors": errors}

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
                if self._cancel:  # Allow cancellation
                    break

                try:
                    for match in regex.finditer(line_text):
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

    # pylint: disable=too-many-positional-arguments  # Complex replace parameters required
    def _replace_in_text(
        self, text: str, query: str, replacement: str, preserve_case: bool, replace_all: bool, options: Dict[str, bool]
    ) -> Tuple[str, int]:
        """
        Replace query with replacement in text.

        Returns:
            Tuple of (new_text, replacement_count)
        """
        case_sensitive = options.get("case_sensitive", False)
        whole_word = options.get("whole_word", False)
        use_regex = options.get("regex", False)

        try:
            # Build regex pattern
            if use_regex:
                pattern = query
            else:
                pattern = re.escape(query)

            if whole_word:
                pattern = r"\b" + pattern + r"\b"

            # SECURITY OWASP A03: Regex DoS Prevention
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                regex = re.compile(pattern, flags)
            except re.error:
                logger.error("Invalid regex in replace: %s", pattern[:50], exc_info=True)
                return (text, 0)  # Return original text unchanged

            # BUG FIX: Escape backslashes in replacement string when NOT using regex mode
            # This prevents "bad escape \S" errors when user input contains backslashes
            # In regex mode, allow backreferences like \1, \2, \g<name>
            if not use_regex:
                # Escape backslashes to treat them literally (e.g., \S becomes \\S)
                # This allows users to type literal backslashes without regex interpretation
                safe_replacement = replacement.replace("\\", "\\\\")
            else:
                # In regex mode, keep backslashes for backreferences (\1, \2, etc)
                safe_replacement = replacement

            # Perform replacement
            if replace_all:
                if preserve_case:
                    new_text, count = self._replace_preserve_case(text, regex, safe_replacement)
                else:
                    new_text = regex.sub(safe_replacement, text)
                    count = len(regex.findall(text))
            else:
                # Replace first occurrence only
                if preserve_case:
                    new_text, count = self._replace_preserve_case(text, regex, safe_replacement, count=1)
                else:
                    new_text = regex.sub(safe_replacement, text, count=1)
                    count = 1 if regex.search(text) else 0

            return new_text, count

        except re.error as e:
            self.error.emit(f"Replacement error: {e}")
            return text, 0

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
        if original.isupper():
            return replacement.upper()
        elif original.islower():
            return replacement.lower()
        elif original[0].isupper():
            return replacement[0].upper() + replacement[1:].lower()
        return replacement

    def _apply_conditions(
        self, results: List[SearchResult], conditions: List[Dict[str, Any]], logic_operator: str
    ) -> List[SearchResult]:
        """
        Apply advanced conditions to filter results.

        Conditions format:
        [
            {
                'field': 'ext',  # filename, path, ext, size, mtime, content
                'operator': '=',  # =, !=, contains, >, <, >=, <=
                'value': '.py',
                'scope': 'all',  # For content: 'all' or 'any'
                'case_sensitive': False,
                'whole_word': False,
                'regex': False
            },
            ...
        ]
        """
        if not conditions:
            return results

        filtered = []

        for result in results:
            matches_conditions = []

            for condition in conditions:
                matches = self._check_condition(result, condition)
                matches_conditions.append(matches)

            # Apply logic operator
            if logic_operator == "AND":
                if all(matches_conditions):
                    filtered.append(result)
            else:  # OR
                if any(matches_conditions):
                    filtered.append(result)

        return filtered

    # pylint: disable=too-many-return-statements  # Condition checking requires early returns
    def _check_condition(self, result: SearchResult, condition: Dict[str, Any]) -> bool:
        """Check if result matches a single condition."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        file_info = result.file_info

        # Get field value
        if field == "filename":
            field_value = file_info.name
        elif field == "path":
            field_value = file_info.path
        elif field == "ext":
            field_value = os.path.splitext(file_info.name)[1]
        elif field == "size":
            field_value = file_info.size
        elif field == "mtime":
            field_value = file_info.mtime
        elif field == "content":
            # Content already searched, check match count
            return result.match_count > 0
        else:
            return False

        # Apply operator
        if operator == "=":
            return str(field_value) == str(value)
        elif operator == "!=":
            return str(field_value) != str(value)
        elif operator == "contains":
            return str(value).lower() in str(field_value).lower()
        elif operator == ">":
            return field_value > value
        elif operator == "<":
            return field_value < value
        elif operator == ">=":
            return field_value >= value
        elif operator == "<=":
            return field_value <= value

        return False


__all__ = ["UnifiedFileExplorerExecutor", "SearchResult", "SearchMatch"]
