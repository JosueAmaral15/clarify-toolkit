"""Bounded file-replacement worker for SearchReplacePanel."""

# pylint: disable=no-name-in-module

from __future__ import annotations

import os
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot

from ...core import file_explorer_executor as explorer_core
from ...core.file_list_executor import FileInfo
from .search_worker import SearchFileRequest


@dataclass(frozen=True)
class ReplaceFileRequest:
    """Immutable replacement plan captured before leaving the GUI thread."""

    files: SearchFileRequest
    query: str
    replacement: str
    case_sensitive: bool
    whole_word: bool
    regex: bool
    preserve_case: bool
    replace_all: bool

    def validate(self) -> None:
        if not self.query:
            raise ValueError("Replacement query must not be empty")
        for value in (self.query, self.replacement):
            if (
                len(value) > explorer_core.MAX_REPLACE_FILE_BYTES
                or len(value.encode("utf-8")) > explorer_core.MAX_REPLACE_FILE_BYTES
            ):
                raise ValueError("Replacement query or value exceeds the 4 MiB limit")
        explorer_core.UnifiedFileExplorerExecutor._compile_replace_pattern(self.query, self.options)

    @property
    def options(self) -> dict[str, bool]:
        return {
            "case_sensitive": self.case_sensitive,
            "whole_word": self.whole_word,
            "regex": self.regex,
        }


class SearchReplaceFileWorker(QObject):
    """Discover targets and delegate bounded atomic replacement to shared core."""

    progress = Signal(int, int, str)
    error = Signal(str)
    done = Signal(object)
    settled = Signal()

    def __init__(self, request: ReplaceFileRequest):
        super().__init__()
        self.request = request
        self.executor = explorer_core.UnifiedFileExplorerExecutor()
        self.executor.prepare_operation()
        self._cancel_requested = False
        self._progress_current = 0
        self._progress_total = 0

    @property
    def is_cancelled(self) -> bool:
        return self._cancel_requested or self.executor._cancel

    def cancel(self) -> None:
        self._cancel_requested = True
        self.executor.cancel()

    def pause(self) -> None:
        self.executor.pause()

    def resume(self) -> None:
        self.executor.resume()

    @staticmethod
    def _empty_result(*, cancelled=False, error="") -> dict:
        errors = [error] if error else []
        return {
            "success": not cancelled and not errors,
            "cancelled": cancelled,
            "replaced_count": 0,
            "replacements_made": 0,
            "files_modified": 0,
            "files_discovered": 0,
            "errors": errors,
            "error": error or ("Operation cancelled" if cancelled else ""),
        }

    def _on_executor_progress(self, message: str) -> None:
        self._progress_current += 1
        self.progress.emit(self._progress_current, self._progress_total, message)

    @Slot()
    def run(self) -> None:
        result = None
        connected = False
        try:
            if self._cancel_requested:
                result = self._empty_result(cancelled=True)
            else:
                files = []
                for path in self.request.files.iter_files(self.executor.checkpoint):
                    if len(files) >= explorer_core.MAX_REPLACE_FILES:
                        result = self._empty_result(
                            error=("Replacement discovery exceeds the " f"{explorer_core.MAX_REPLACE_FILES}-file limit")
                        )
                        break
                    files.append(
                        explorer_core.SearchResult(
                            FileInfo(
                                name=os.path.basename(path),
                                path=path,
                                size=0,
                                mtime=None,
                                permissions="",
                                owner="",
                                group="",
                                is_dir=False,
                            ),
                            [],
                            0,
                        )
                    )
                    self.progress.emit(len(files), 0, f"Discovered {os.path.basename(path)}")

                if result is None and self.is_cancelled:
                    result = self._empty_result(cancelled=True)
                if result is None:
                    self._progress_current = 0
                    self._progress_total = len(files)
                    self.executor.progress.connect(self._on_executor_progress)
                    connected = True
                    result = self.executor.execute_replace(
                        files=files,
                        search_query=self.request.query,
                        replacement=self.request.replacement,
                        search_options=self.request.options,
                        preserve_case=self.request.preserve_case,
                        replace_all=self.request.replace_all,
                        prepared=True,
                    )
                    result["files_discovered"] = len(files)
            for message in result.get("errors", ()):
                self.error.emit(message)
            self.done.emit(result)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            message = f"Replacement failed: {exc}"
            self.error.emit(message)
            self.done.emit(self._empty_result(error=message))
        finally:
            if connected:
                try:
                    self.executor.progress.disconnect(self._on_executor_progress)
                except (RuntimeError, TypeError):
                    pass
            self.settled.emit()
