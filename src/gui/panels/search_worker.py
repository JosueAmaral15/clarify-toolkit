"""
Search worker thread for file scanning.
Extracted from app.py (v2.9.114 - Phase 1.2).
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness

import fnmatch
import os
from dataclasses import dataclass
from threading import Event

from typing import Callable, Dict, Iterator, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal

from ...core import Condition, filter_files_by_conditions
from ...utils import read_text, walk_files


@dataclass(frozen=True)
class SearchConditionRequest:
    """Immutable condition copied from GUI-owned condition rows."""

    field: str
    operator: str
    value: str
    scope_type: str
    scope_value: str
    case_sensitive: bool
    whole_word: bool
    use_regex: bool

    @classmethod
    def from_condition(cls, condition: Condition) -> "SearchConditionRequest":
        return cls(
            field=condition.field,
            operator=condition.operator,
            value=condition.value,
            scope_type=condition.scope_type,
            scope_value=condition.scope_value,
            case_sensitive=condition.case_sensitive,
            whole_word=condition.whole_word,
            use_regex=condition.use_regex,
        )

    def to_condition(self) -> Condition:
        """Build a worker-owned condition from the immutable transfer object."""
        return Condition(
            field=self.field,
            operator=self.operator,
            value=self.value,
            scope_type=self.scope_type,
            scope_value=self.scope_value,
            case_sensitive=self.case_sensitive,
            whole_word=self.whole_word,
            use_regex=self.use_regex,
        )


@dataclass(frozen=True)
class SearchFileRequest:
    """Immutable file-discovery state captured on the GUI thread."""

    root: str
    include_globs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    conditions: tuple[SearchConditionRequest, ...]
    logic_operator: str

    def iter_files(self, checkpoint=None) -> Iterator[str]:
        conditions = tuple(condition.to_condition() for condition in self.conditions)
        for file_path in walk_files(self.root, self.include_globs, self.exclude_globs):
            if checkpoint is not None and not checkpoint():
                return
            if not conditions or filter_files_by_conditions(
                (file_path,), conditions, self.logic_operator
            ):
                if checkpoint is not None and not checkpoint():
                    return
                yield file_path


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
    MAX_DISCOVERED_FILES = 100_000

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
        self._cancel_event = Event()
        self._resume_event = Event()
        self._resume_event.set()

    @property
    def is_cancelled(self) -> bool:
        """Return the thread-safe cancellation state."""
        return self._cancel_event.is_set()

    def cancel(self):
        """Cancel the search operation."""
        self._cancel_event.set()
        self._resume_event.set()

    def pause(self):
        """Pause processing (v2.5.0+)."""
        self._resume_event.clear()

    def resume(self):
        """Resume processing (v2.5.0+)."""
        self._resume_event.set()

    def _wait_until_resumed(self) -> bool:
        """Wait cooperatively and return False when cancellation wins."""
        while not self._resume_event.wait(0.1):
            if self.is_cancelled:
                return False
        return not self.is_cancelled

    def run(self):
        """
        Execute file search with detailed progress tracking.

        Features:
        - v2.5.0+: Pause/resume support
        - v2.8.0: Multi-query search
        - v2.9.112: Filename/content/both search modes
        """
        matches: Dict[str, List[Tuple[int, int, str]]] = {}

        # Collect a bounded snapshot so progress has a stable denominator.
        files_to_process = []
        try:
            for file_path in self.iter_files_fn():
                if self.is_cancelled:
                    self.done.emit({})
                    return
                files_to_process.append(file_path)
                if len(files_to_process) > self.MAX_DISCOVERED_FILES:
                    raise ValueError(
                        f"Search exceeds the {self.MAX_DISCOVERED_FILES}-file safety limit"
                    )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.error.emit(str(exc))
            self.done.emit({})
            return

        # v2.9.112: Filter by filename pattern if needed
        if self.search_mode in ("filename_only", "both") and self.filename_pattern:
            filtered_files = []
            for file_path in files_to_process:
                filename = os.path.basename(file_path)
                # Support simple wildcards like *.py, test_*, etc.
                if fnmatch.fnmatch(filename, self.filename_pattern):
                    filtered_files.append(file_path)
            files_to_process = filtered_files

        total_files = len(files_to_process)

        for idx, file_path in enumerate(files_to_process, 1):
            # Check for cancellation
            if self.is_cancelled:
                break

            # Check for pause (NEW - v2.5.0+)
            if not self._wait_until_resumed():
                break

            try:
                # Emit detailed progress (current, total, message)
                self.progress.emit(file_path)  # Legacy signal
                self.progress_detailed.emit(idx, total_files, file_path)

                # v2.9.112: Handle filename-only search mode
                if self.search_mode == "filename_only":
                    # Just list the file with a placeholder match
                    matches[file_path] = [
                        (0, 0, f"Matched file: {os.path.basename(file_path)}")
                    ]
                    continue

                # For content search or both modes, read and search file content
                text = read_text(file_path)
                if self.is_cancelled:
                    break
                lst: List[Tuple[int, int, str]] = []

                # v2.8.0: Multi-query search support
                if self.is_multi_query and self.multi_query_processor:
                    # Use MultiQueryProcessor for multiple patterns
                    query_matches = self.multi_query_processor.search_in_text(text)
                    # Convert from (line, col, snippet, query_line_num)
                    lst = [(line, col, snippet)
                           for line, col, snippet, _ in query_matches]
                else:
                    # Single pattern search (original behavior)
                    for m in self.pattern_text.finditer(text):
                        line = text.count("\n", 0, m.start()) + 1
                        col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                        lines = text.splitlines()
                        snippet = lines[line - 1] if line - 1 < len(lines) else ""
                        lst.append((line, col, snippet))

                if lst:
                    matches[file_path] = lst
            except Exception as exc:
                self.error.emit(f"[WARN] {file_path}: {exc}")
                # continue to next files

        self.done.emit(matches)
