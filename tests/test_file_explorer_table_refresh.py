"""Regression tests for File Explorer table refresh and stale-result cleanup."""

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.widgets.file_list_table_manager import FileListTableManager


def _file_data(path: Path) -> dict:
    stat_info = path.stat()
    return {
        "name": path.name,
        "size": stat_info.st_size,
        "mtime": stat_info.st_mtime,
        "permissions": "-rw-r--r--",
        "path": str(path),
        "is_dir": False,
    }


class _NoopHistory:
    def add_operation(self, *_args, **_kwargs):
        return None


def test_search_batch_refreshes_table_mode_without_stale_rows(qapp, tmp_path):
    """A new search ending in table mode should replace prior table rows."""
    stale_file = tmp_path / "stale.txt"
    fresh_file = tmp_path / "fresh.txt"
    stale_file.write_text("old", encoding="utf-8")
    fresh_file.write_text("needle", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.table_manager.populate([_file_data(stale_file)])
        dock.last_search_results = {str(stale_file): [(1, 0, "old")]}
        dock.results_stack.setCurrentIndex(1)
        dock.combo_view_mode.setCurrentIndex(1)
        dock._current_search_params = {"directory": str(tmp_path)}

        dock._on_batch_ready([(str(fresh_file), [(1, 0, "needle")])], 1, 1)

        table = dock.table_manager.table
        assert dock.results_stack.currentIndex() == 1
        assert table.rowCount() == 1
        assert table.item(0, FileListTableManager.COL_PATH).text() == str(fresh_file)
        assert dock.last_search_results == {str(fresh_file): [(1, 0, "needle")]}
    finally:
        dock.deleteLater()


def test_empty_search_clears_table_tree_and_sync_caches(qapp, tmp_path, monkeypatch):
    """A search with no files should not leave old table/tree data recoverable."""
    import src.gui.progress as progress

    monkeypatch.setattr(progress, "OperationHistory", lambda: _NoopHistory())

    stale_file = tmp_path / "stale.txt"
    stale_file.write_text("old", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.table_manager.populate([_file_data(stale_file)])
        dock.results_tree.populate({str(stale_file): [(1, 0, "old")]}, base_path=str(tmp_path))
        dock.last_search_results = {str(stale_file): [(1, 0, "old")]}
        dock.last_browse_results = [_file_data(stale_file)]
        dock._current_search_params = {
            "directory": str(tmp_path),
            "filename_pattern": None,
            "content_query": "missing",
            "search_options": {},
            "start_time": time.time(),
        }

        dock._on_search_finished({"files": []})

        assert dock.table_manager.table.rowCount() == 0
        assert dock.results_tree.get_matches_data() == {}
        assert dock.last_search_results == {}
        assert dock.last_browse_results == []
        assert dock.last_was_search is True
        assert "Found 0 file(s)" in dock.results_status.text()
    finally:
        dock.deleteLater()
