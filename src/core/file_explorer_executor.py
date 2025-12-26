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
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from .file_list_executor import FileInfo, FileListExecutor
from ..utils import read_text


@dataclass
class SearchMatch:
    """Container for search match information."""
    line: int
    col: int
    snippet: str
    context_before: str = ""
    context_after: str = ""


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
    
    def execute_browse(
        self,
        directory: str,
        show_hidden: bool = False,
        recursive: bool = False,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute browse operation (list files).
        
        Args:
            directory: Directory path
            show_hidden: Show hidden files
            recursive: Recurse into subdirectories
            filters: Filter configuration (includes include_globs, exclude_globs)
            
        Returns:
            Dict with files and statistics
        """
        filters = filters or {}
        
        # Step 1: Get base file list
        result = FileListExecutor.list_files(
            directory, show_hidden, recursive, filters
        )
        
        file_list = result.files
        
        # Step 2: Apply include/exclude glob filters (from Search/Replace)
        include_globs = filters.get('include_globs', [])
        exclude_globs = filters.get('exclude_globs', [])
        
        if include_globs or exclude_globs:
            filtered_files = []
            for file_info in file_list:
                file_path = file_info.path
                file_name = file_info.name
                
                # Check exclude globs first (higher priority)
                excluded = False
                for pattern in exclude_globs:
                    if fnmatch.fnmatch(file_path, f"*{pattern}*") or \
                       fnmatch.fnmatch(file_name, pattern):
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                # Check include globs (if any)
                if include_globs:
                    included = False
                    for pattern in include_globs:
                        if fnmatch.fnmatch(file_path, pattern) or \
                           fnmatch.fnmatch(file_name, pattern):
                            included = True
                            break
                    
                    if not included:
                        continue
                
                filtered_files.append(file_info)
            
            file_list = filtered_files
        
        # Step 3: Create search results
        search_results = [
            SearchResult(
                file_info=file_info,
                matches=[],
                match_count=0
            )
            for file_info in file_list
        ]
        
        stats = FileListExecutor.calculate_statistics(file_list)
        stats['errors'] = result.errors
        
        return {
            'files': search_results,
            'stats': stats
        }
    
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
        logic_operator: str = "AND"
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
        search_options = search_options or {}
        
        # Step 1: List files
        browse_result = self.execute_browse(
            directory, show_hidden, recursive, filters
        )
        
        files_to_search = [sr.file_info for sr in browse_result['files']]
        
        # Step 2: Apply filename pattern filter
        if filename_pattern:
            files_to_search = [
                f for f in files_to_search
                if not f.is_dir and fnmatch.fnmatch(f.name.rstrip('/'), filename_pattern)
            ]
        
        # Step 3: Apply content search
        search_results = []
        total_files = len(files_to_search)
        
        for idx, file_info in enumerate(files_to_search, 1):
            if self._cancel:
                break
            
            self.progress.emit(file_info.path)
            self.progress_detailed.emit(idx, total_files, file_info.path)
            
            # Skip directories for content search
            if file_info.is_dir:
                continue
            
            try:
                # If no content query, just list matching files
                if not content_query:
                    search_results.append(SearchResult(
                        file_info=file_info,
                        matches=[],
                        match_count=0
                    ))
                    continue
                
                # Read file and search
                text = read_text(file_info.path)
                matches = self._search_in_text(
                    text, content_query, search_options
                )
                
                if matches:
                    search_results.append(SearchResult(
                        file_info=file_info,
                        matches=matches,
                        match_count=len(matches)
                    ))
                
            except Exception as e:
                self.error.emit(f"Error processing {file_info.path}: {e}")
        
        # Step 4: Apply advanced conditions if provided
        if conditions:
            search_results = self._apply_conditions(
                search_results, conditions, logic_operator
            )
        
        # Calculate statistics
        file_infos = [sr.file_info for sr in search_results]
        stats = FileListExecutor.calculate_statistics(file_infos)
        stats['total_matches'] = sum(sr.match_count for sr in search_results)
        stats['files_with_matches'] = sum(1 for sr in search_results if sr.match_count > 0)
        
        return {
            'files': search_results,
            'stats': stats
        }
    
    def execute_replace(
        self,
        files: List[SearchResult],
        search_query: str,
        replacement: str,
        preserve_case: bool = False,
        replace_all: bool = False,
        search_options: Dict[str, bool] = None
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
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content, count = self._replace_in_text(
                    content,
                    search_query,
                    replacement,
                    preserve_case,
                    replace_all,
                    search_options
                )
                
                if count > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    replaced_count += count
                    files_modified += 1
                    
            except Exception as e:
                errors.append(f"Error replacing in {file_path}: {e}")
                self.error.emit(errors[-1])
        
        return {
            'replaced_count': replaced_count,
            'files_modified': files_modified,
            'errors': errors
        }
    
    def _search_in_text(
        self,
        text: str,
        query: str,
        options: Dict[str, bool]
    ) -> List[SearchMatch]:
        """Search for query in text and return matches."""
        matches = []
        
        case_sensitive = options.get('case_sensitive', False)
        whole_word = options.get('whole_word', False)
        use_regex = options.get('regex', False)
        
        try:
            # Build regex pattern
            if use_regex:
                pattern = query
            else:
                pattern = re.escape(query)
            
            # Add word boundaries if needed
            if whole_word:
                pattern = r'\b' + pattern + r'\b'
            
            # Compile with case sensitivity
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            # Find all matches
            lines = text.splitlines()
            for line_num, line_text in enumerate(lines, 1):
                for match in regex.finditer(line_text):
                    col = match.start()
                    
                    matches.append(SearchMatch(
                        line=line_num,
                        col=col,
                        snippet=line_text,
                        context_before=lines[line_num - 2] if line_num > 1 else "",
                        context_after=lines[line_num] if line_num < len(lines) else ""
                    ))
        
        except re.error as e:
            self.error.emit(f"Invalid regex pattern: {e}")
        
        return matches
    
    def _replace_in_text(
        self,
        text: str,
        query: str,
        replacement: str,
        preserve_case: bool,
        replace_all: bool,
        options: Dict[str, bool]
    ) -> Tuple[str, int]:
        """
        Replace query with replacement in text.
        
        Returns:
            Tuple of (new_text, replacement_count)
        """
        case_sensitive = options.get('case_sensitive', False)
        whole_word = options.get('whole_word', False)
        use_regex = options.get('regex', False)
        
        try:
            # Build regex pattern
            if use_regex:
                pattern = query
            else:
                pattern = re.escape(query)
            
            if whole_word:
                pattern = r'\b' + pattern + r'\b'
            
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            # Perform replacement
            if replace_all:
                if preserve_case:
                    new_text, count = self._replace_preserve_case(text, regex, replacement)
                else:
                    new_text = regex.sub(replacement, text)
                    count = len(regex.findall(text))
            else:
                # Replace first occurrence only
                if preserve_case:
                    new_text, count = self._replace_preserve_case(text, regex, replacement, count=1)
                else:
                    new_text = regex.sub(replacement, text, count=1)
                    count = 1 if regex.search(text) else 0
            
            return new_text, count
        
        except re.error as e:
            self.error.emit(f"Replacement error: {e}")
            return text, 0
    
    def _replace_preserve_case(
        self,
        text: str,
        pattern: re.Pattern,
        replacement: str,
        count: int = 0
    ) -> Tuple[str, int]:
        """Replace with case preservation."""
        replaced = 0
        result = []
        last_end = 0
        
        for match in pattern.finditer(text):
            # Add text before match
            result.append(text[last_end:match.start()])
            
            # Determine case pattern of original
            original = match.group(0)
            new_text = self._apply_case_pattern(original, replacement)
            result.append(new_text)
            
            last_end = match.end()
            replaced += 1
            
            # Stop if we've replaced enough
            if count > 0 and replaced >= count:
                result.append(text[last_end:])
                break
        else:
            # Add remaining text
            result.append(text[last_end:])
        
        return ''.join(result), replaced
    
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
        self,
        results: List[SearchResult],
        conditions: List[Dict[str, Any]],
        logic_operator: str
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
    
    def _check_condition(
        self,
        result: SearchResult,
        condition: Dict[str, Any]
    ) -> bool:
        """Check if result matches a single condition."""
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        file_info = result.file_info
        
        # Get field value
        if field == 'filename':
            field_value = file_info.name
        elif field == 'path':
            field_value = file_info.path
        elif field == 'ext':
            field_value = os.path.splitext(file_info.name)[1]
        elif field == 'size':
            field_value = file_info.size
        elif field == 'mtime':
            field_value = file_info.mtime
        elif field == 'content':
            # Content already searched, check match count
            return result.match_count > 0
        else:
            return False
        
        # Apply operator
        if operator == '=':
            return str(field_value) == str(value)
        elif operator == '!=':
            return str(field_value) != str(value)
        elif operator == 'contains':
            return str(value).lower() in str(field_value).lower()
        elif operator == '>':
            return field_value > value
        elif operator == '<':
            return field_value < value
        elif operator == '>=':
            return field_value >= value
        elif operator == '<=':
            return field_value <= value
        
        return False


__all__ = ['UnifiedFileExplorerExecutor', 'SearchResult', 'SearchMatch']
