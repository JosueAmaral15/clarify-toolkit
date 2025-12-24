"""
Search worker thread for file scanning.
Extracted from app.py (v2.9.114 - Phase 1.2).
"""

import time
import fnmatch
import os
from typing import Dict, List, Tuple, Callable, Optional

from PySide6.QtCore import QObject, Signal

from ...utils import read_text


class SearchWorker(QObject):
    """
    Background worker for searching files.
    Features:
    - Multi-threaded file processing
    - Enhanced progress tracking (v2.5.0+)
    - Pause/resume support (v2.5.0+)
    - Multi-query search (v2.8.0)
    - Filename/content/both search modes (v2.9.112)
    """
    # Signals with enhanced progress tracking (v2.5.0+)
    progress = Signal(str)  # Current file being processed
    progress_detailed = Signal(int, int, str)  # (current, total, message) for progress bar
    done = Signal(dict)  # Final results
    error = Signal(str)  # Error messages

    def __init__(self, pattern_text: str, iter_files_fn: Callable, search_options_factory, 
                 is_multi_query: bool = False, multi_query_processor=None,
                 search_mode: str = "content_only", filename_pattern: Optional[str] = None):
        """
        Initialize search worker.
        
        Args:
            pattern_text: Compiled regex pattern for content search
            iter_files_fn: Function that yields file paths to search
            search_options_factory: Factory for creating SearchOptions
            is_multi_query: Whether to use multi-query search (v2.8.0)
            multi_query_processor: MultiQueryProcessor instance (v2.8.0)
            search_mode: "filename_only", "content_only", or "both" (v2.9.112)
            filename_pattern: Wildcard pattern for filename matching (v2.9.112)
        """
        super().__init__()
        self.pattern_text = pattern_text
        self.iter_files_fn = iter_files_fn
        self.search_options_factory = search_options_factory
        self.is_multi_query = is_multi_query  # v2.8.0
        self.multi_query_processor = multi_query_processor  # v2.8.0
        self.search_mode = search_mode  # v2.9.112
        self.filename_pattern = filename_pattern  # v2.9.112
        self._cancel = False
        self._paused = False  # NEW - v2.5.0+

    def cancel(self):
        """Cancel the search operation."""
        self._cancel = True
    
    def pause(self):
        """Pause processing (v2.5.0+)."""
        self._paused = True
    
    def resume(self):
        """Resume processing (v2.5.0+)."""
        self._paused = False

    def run(self):
        """
        Execute file search with detailed progress tracking.
        
        Features:
        - v2.5.0+: Pause/resume support
        - v2.8.0: Multi-query search
        - v2.9.112: Filename/content/both search modes
        """
        matches: Dict[str, List[Tuple[int, int, str]]] = {}
        
        # Collect all files first to know total count
        files_to_process = list(self.iter_files_fn())
        
        # v2.9.112: Filter by filename pattern if needed
        if self.search_mode in ("filename_only", "both") and self.filename_pattern:
            filtered_files = []
            for p in files_to_process:
                filename = os.path.basename(p)
                # Support simple wildcards like *.py, test_*, etc.
                if fnmatch.fnmatch(filename, self.filename_pattern):
                    filtered_files.append(p)
            files_to_process = filtered_files
        
        total_files = len(files_to_process)
        
        for idx, p in enumerate(files_to_process, 1):
            # Check for cancellation
            if self._cancel:
                break
            
            # Check for pause (NEW - v2.5.0+)
            while self._paused and not self._cancel:
                time.sleep(0.1)  # Wait while paused
            
            try:
                # Emit detailed progress (current, total, message)
                self.progress.emit(p)  # Legacy signal for backward compatibility
                self.progress_detailed.emit(idx, total_files, p)
                
                # v2.9.112: Handle filename-only search mode
                if self.search_mode == "filename_only":
                    # Just list the file with a placeholder match
                    matches[p] = [(0, 0, f"Matched file: {os.path.basename(p)}")]
                    continue
                
                # For content search or both modes, read and search file content
                text = read_text(p)
                lst: List[Tuple[int, int, str]] = []
                
                # v2.8.0: Multi-query search support
                if self.is_multi_query and self.multi_query_processor:
                    # Use MultiQueryProcessor for multiple patterns
                    query_matches = self.multi_query_processor.search_in_text(text)
                    # Convert from (line, col, snippet, query_line_num) to (line, col, snippet)
                    lst = [(line, col, snippet) for line, col, snippet, _ in query_matches]
                else:
                    # Single pattern search (original behavior)
                    for m in self.pattern_text.finditer(text):
                        line = text.count("\n", 0, m.start()) + 1
                        col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                        snippet = text.splitlines()[line - 1] if line - 1 < len(text.splitlines()) else ""
                        lst.append((line, col, snippet))
                
                if lst:
                    matches[p] = lst
            except Exception as e:
                self.error.emit(f"[WARN] {p}: {e}")
                # continue to next files
        
        self.done.emit(matches)
