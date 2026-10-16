"""Bounded immutable CSV export plans for GUI-owned result snapshots."""

# pylint: disable=no-name-in-module  # Qt exposes dynamic bindings.

from __future__ import annotations

import csv
import io
import os
import tempfile
from dataclasses import dataclass
from threading import Event
from typing import Iterable, Sequence

from PySide6.QtCore import QObject, Signal, Slot

MAX_CSV_EXPORT_ROWS = 100_000
MAX_CSV_EXPORT_COLUMNS = 16
MAX_CSV_EXPORT_CELL_BYTES = 1024 * 1024
MAX_CSV_EXPORT_TOTAL_BYTES = 20 * 1024 * 1024
MAX_CSV_EXPORT_PATH_BYTES = 4_096

CsvRow = tuple[str, ...]


def _bounded_text(value, label: str) -> tuple[str, int]:
    if not isinstance(value, str):
        raise ValueError(f"CSV {label} values must be text")
    if len(value) > MAX_CSV_EXPORT_CELL_BYTES:
        raise ValueError(f"A CSV {label} value exceeds the 1 MiB safety limit")
    size = len(value.encode("utf-8"))
    if size > MAX_CSV_EXPORT_CELL_BYTES:
        raise ValueError(f"A CSV {label} value exceeds the 1 MiB safety limit")
    return value, size


@dataclass(frozen=True)
class CsvExportResult:
    """Completed export metadata returned to the GUI thread."""

    output_path: str
    row_count: int
    source_count: int


@dataclass(frozen=True)
class CsvExportPlan:
    """Bounded CSV snapshot and destination selected on the GUI thread."""

    headers: CsvRow
    rows: tuple[CsvRow, ...]
    output_path: str
    source_count: int

    @classmethod
    def from_rows(
        cls,
        headers: Sequence[str],
        rows: Iterable[Sequence[str]],
        output_path: str,
        *,
        source_count: int,
    ) -> "CsvExportPlan":
        if not isinstance(output_path, str) or not output_path:
            raise ValueError("A CSV output path is required")
        if (
            len(output_path) > MAX_CSV_EXPORT_PATH_BYTES
            or len(output_path.encode("utf-8")) > MAX_CSV_EXPORT_PATH_BYTES
        ):
            raise ValueError("CSV output path exceeds the 4 KiB safety limit")
        if isinstance(source_count, bool) or not isinstance(source_count, int):
            raise ValueError("CSV source count must be an integer")
        if source_count < 0 or source_count > MAX_CSV_EXPORT_ROWS:
            raise ValueError("CSV source count exceeds the 100000-item safety limit")

        immutable_headers = tuple(headers)
        if not immutable_headers:
            raise ValueError("CSV export requires at least one column")
        if len(immutable_headers) > MAX_CSV_EXPORT_COLUMNS:
            raise ValueError("CSV export exceeds the 16-column safety limit")

        total_bytes = 0
        checked_headers = []
        for header in immutable_headers:
            text, size = _bounded_text(header, "header")
            total_bytes += size + 4
            checked_headers.append(text)

        snapshot = []
        for row_number, row in enumerate(rows, start=1):
            if row_number > MAX_CSV_EXPORT_ROWS:
                raise ValueError("CSV export exceeds the 100000-row safety limit")
            immutable_row = tuple(row)
            if len(immutable_row) != len(checked_headers):
                raise ValueError("CSV rows must match the header column count")
            checked_row = []
            for value in immutable_row:
                text, size = _bounded_text(value, "cell")
                total_bytes += size + 4
                if total_bytes > MAX_CSV_EXPORT_TOTAL_BYTES:
                    raise ValueError("CSV export exceeds the 20 MiB safety limit")
                checked_row.append(text)
            snapshot.append(tuple(checked_row))

        return cls(
            headers=tuple(checked_headers),
            rows=tuple(snapshot),
            output_path=output_path,
            source_count=source_count,
        )

    def execute(self, checkpoint) -> CsvExportResult | None:
        """Serialize and atomically publish the snapshot with checkpoints."""
        output_path = os.path.abspath(self.output_path)
        output_directory = os.path.dirname(output_path)
        os.makedirs(output_directory, exist_ok=True)
        descriptor, temporary_path = tempfile.mkstemp(
            prefix=".clarify-csv-",
            suffix=".tmp",
            dir=output_directory,
        )
        os.close(descriptor)
        try:
            total_bytes = 0
            with open(temporary_path, "w", encoding="utf-8", newline="") as handle:
                for row in (self.headers, *self.rows):
                    if not checkpoint():
                        return None
                    buffer = io.StringIO(newline="")
                    csv.writer(buffer).writerow(row)
                    chunk = buffer.getvalue()
                    total_bytes += len(chunk.encode("utf-8"))
                    if total_bytes > MAX_CSV_EXPORT_TOTAL_BYTES:
                        raise ValueError("CSV export exceeds the 20 MiB safety limit")
                    handle.write(chunk)
            if not checkpoint():
                return None
            os.replace(temporary_path, output_path)
            temporary_path = ""
            return CsvExportResult(
                output_path=output_path,
                row_count=len(self.rows),
                source_count=self.source_count,
            )
        finally:
            if temporary_path:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass


class CsvExportWorker(QObject):
    """QObject worker for a bounded CSV export plan."""

    completed = Signal(object)
    failed = Signal(str)
    settled = Signal()

    def __init__(self, plan: CsvExportPlan):
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
