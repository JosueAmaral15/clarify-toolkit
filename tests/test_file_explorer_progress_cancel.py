"""Regression tests for File Explorer progress cancellation."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.core.file_explorer_executor import UnifiedFileExplorerExecutor
from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.panels.file_explorer_worker import FileExplorerWorker


def test_progress_cancel_marks_dock_executor_and_worker(qapp):
    """Progress dialog Cancel should propagate beyond the visible dialog."""
    dock = FileExplorerDock()
    worker = FileExplorerWorker(dock.executor)
    try:
        dock._worker = worker
        dock._ensure_progress_dialog()

        dock._on_progress_canceled()

        assert dock._cancel_requested is True
        assert dock.executor._cancel is True
        assert worker._cancel_requested is True
        assert dock.progress_dialog.labelText() == "Canceling..."
    finally:
        if dock.progress_dialog:
            dock.progress_dialog.close()
        dock.deleteLater()
        worker.deleteLater()


def test_worker_cancel_stops_pending_batch_emission(qapp):
    """Worker cancellation should prevent queued result batches from reaching the UI."""
    worker = FileExplorerWorker(UnifiedFileExplorerExecutor())
    emitted_batches = []
    worker.batch_ready.connect(lambda batch, batch_num, total: emitted_batches.append((batch, batch_num, total)))
    try:
        worker.cancel()
        worker._emit_in_batches({f"/tmp/file_{idx}.txt": [] for idx in range(250)}, batch_size=100)

        assert emitted_batches == []
    finally:
        worker.deleteLater()


def test_executor_resets_cancel_state_for_new_browse_and_replace(tmp_path):
    """A canceled operation should not poison the next browse or replace request."""
    executor = UnifiedFileExplorerExecutor()
    target = tmp_path / "sample.txt"
    target.write_text("needle", encoding="utf-8")

    executor.cancel()
    browse_result = executor.execute_browse(str(tmp_path), show_hidden=False, recursive=False, filters={})

    assert executor._cancel is False
    assert [item.file_info.name for item in browse_result["files"]] == ["sample.txt"]

    executor.cancel()
    replace_result = executor.execute_replace(
        browse_result["files"],
        search_query="needle",
        replacement="changed",
        replace_all=True,
        search_options={},
    )

    assert executor._cancel is False
    assert replace_result["replaced_count"] == 1
    assert target.read_text(encoding="utf-8") == "changed"
