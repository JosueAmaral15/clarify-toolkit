"""Bounded immutable export plans for match-result trees."""

# pylint: disable=no-name-in-module  # Qt exposes dynamic bindings.

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from threading import Event
from typing import Iterable, Iterator, Mapping, Sequence

from PySide6.QtCore import QObject, Signal, Slot

MAX_RESULT_EXPORT_FILES = 100_000
MAX_RESULT_EXPORT_MATCHES = 50_000
MAX_RESULT_EXPORT_PATH_BYTES = 4_096
MAX_RESULT_EXPORT_SNIPPET_BYTES = 1024 * 1024
MAX_RESULT_EXPORT_TOTAL_BYTES = 20 * 1024 * 1024

Match = tuple[int, int, str]
MatchFile = tuple[str, tuple[Match, ...]]


def iter_match_result_lines(matches: Iterable[MatchFile]) -> Iterator[str]:
    """Yield the established ResultsTree text format without joining it in memory."""
    matches = tuple(matches)
    total_files = len(matches)
    total_matches = sum(len(items) for _file_path, items in matches)

    yield "=" * 80
    yield "CLARIFY - SEARCH RESULTS"
    yield "=" * 80
    yield f"Total files with matches: {total_files}"
    yield f"Total matches: {total_matches}"
    yield "=" * 80
    yield ""

    for file_path, items in matches:
        yield f"📁 {file_path}"
        yield f"   Matches: {len(items)}"
        yield "-" * 80
        for line_num, col, snippet in items:
            yield f"   Line {line_num}, Col {col}:"
            yield f"      {snippet.strip()}"
        yield ""


def format_match_results(matches: Mapping[str, Sequence[Match]]) -> str:
    """Preserve the public synchronous ResultsTree export format."""
    if not matches:
        return ""
    immutable = tuple((path, tuple(items)) for path, items in matches.items())
    return "\n".join(iter_match_result_lines(immutable))


@dataclass(frozen=True)
class MatchResultExportResult:
    """Completed export metadata returned to the GUI thread."""

    output_path: str
    total_files: int
    total_matches: int


@dataclass(frozen=True)
class MatchResultExportPlan:
    """Bounded result snapshot and destination selected on the GUI thread."""

    matches: tuple[MatchFile, ...]
    output_path: str
    total_matches: int

    @classmethod
    def from_matches(
        cls,
        matches: Mapping[str, Sequence[Match]],
        output_path: str,
    ) -> "MatchResultExportPlan":
        if not matches:
            raise ValueError("There are no match results to save")
        if len(matches) > MAX_RESULT_EXPORT_FILES:
            raise ValueError(f"Result export exceeds the {MAX_RESULT_EXPORT_FILES}-file safety limit")
        if not isinstance(output_path, str) or not output_path:
            raise ValueError("A result output path is required")
        if (
            len(output_path) > MAX_RESULT_EXPORT_PATH_BYTES
            or len(output_path.encode("utf-8")) > MAX_RESULT_EXPORT_PATH_BYTES
        ):
            raise ValueError("Result output path exceeds the 4 KiB safety limit")

        snapshot = []
        total_matches = 0
        total_characters = 0
        for file_path, items in matches.items():
            if not isinstance(file_path, str):
                raise ValueError("Result paths must be text")
            if len(file_path) > MAX_RESULT_EXPORT_PATH_BYTES:
                raise ValueError("A result path exceeds the 4 KiB safety limit")
            total_characters += len(file_path)
            immutable_items = []
            for item in items:
                if not isinstance(item, (tuple, list)) or len(item) != 3:
                    raise ValueError("Each result match must contain line, column and snippet")
                line_num, column, snippet = item
                if (
                    isinstance(line_num, bool)
                    or not isinstance(line_num, int)
                    or isinstance(column, bool)
                    or not isinstance(column, int)
                ):
                    raise ValueError("Result line and column values must be integers")
                if not isinstance(snippet, str):
                    raise ValueError("Result snippets must be text")
                if len(snippet) > MAX_RESULT_EXPORT_SNIPPET_BYTES:
                    raise ValueError("A result snippet exceeds the 1 MiB safety limit")
                total_matches += 1
                if total_matches > MAX_RESULT_EXPORT_MATCHES:
                    raise ValueError(f"Result export exceeds the {MAX_RESULT_EXPORT_MATCHES}-match safety limit")
                total_characters += len(snippet) + 64
                if total_characters > MAX_RESULT_EXPORT_TOTAL_BYTES:
                    raise ValueError("Result export exceeds the 20 MiB total safety limit")
                immutable_items.append((line_num, column, snippet))
            snapshot.append((file_path, tuple(immutable_items)))

        return cls(tuple(snapshot), output_path, total_matches)

    def execute(self, checkpoint) -> MatchResultExportResult | None:
        """Serialize and atomically publish the snapshot with cooperative checkpoints."""
        for file_path, items in self.matches:
            if not checkpoint():
                return None
            if len(file_path.encode("utf-8")) > MAX_RESULT_EXPORT_PATH_BYTES:
                raise ValueError("A result path exceeds the 4 KiB safety limit")
            for _line_num, _column, snippet in items:
                if not checkpoint():
                    return None
                if len(snippet.encode("utf-8")) > MAX_RESULT_EXPORT_SNIPPET_BYTES:
                    raise ValueError("A result snippet exceeds the 1 MiB safety limit")

        output_path = os.path.abspath(self.output_path)
        output_directory = os.path.dirname(output_path)
        os.makedirs(output_directory, exist_ok=True)
        descriptor, temporary_path = tempfile.mkstemp(
            prefix=".clarify-match-results-",
            suffix=".tmp",
            dir=output_directory,
        )
        os.close(descriptor)
        try:
            total_bytes = 0
            first_line = True
            with open(temporary_path, "w", encoding="utf-8") as handle:
                for line in iter_match_result_lines(self.matches):
                    if not checkpoint():
                        return None
                    chunk = line if first_line else f"\n{line}"
                    first_line = False
                    chunk_bytes = len(chunk.encode("utf-8"))
                    total_bytes += chunk_bytes
                    if total_bytes > MAX_RESULT_EXPORT_TOTAL_BYTES:
                        raise ValueError("Result export exceeds the 20 MiB total safety limit")
                    handle.write(chunk)
            if not checkpoint():
                return None
            os.replace(temporary_path, output_path)
            temporary_path = ""
            return MatchResultExportResult(
                output_path=output_path,
                total_files=len(self.matches),
                total_matches=self.total_matches,
            )
        finally:
            if temporary_path:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass


class MatchResultExportWorker(QObject):
    """QObject worker for a bounded match-result export plan."""

    completed = Signal(object)
    failed = Signal(str)
    settled = Signal()

    def __init__(self, plan: MatchResultExportPlan):
        super().__init__()
        self.plan = plan
        self._cancel_event = Event()

    @Slot()
    def run(self):
        try:
            result = self.plan.execute(lambda: not self._cancel_event.is_set())
            if result is not None:
                self.completed.emit(result)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.failed.emit(str(exc))
        finally:
            self.settled.emit()

    @Slot()
    def cancel(self):
        self._cancel_event.set()
