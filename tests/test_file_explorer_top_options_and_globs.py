"""Regression tests for File Explorer top options and glob fields."""

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.core.file_explorer_executor import SearchResult
from src.core.file_list_executor import FileListExecutor
from src.gui.file_explorer_dock import FileExplorerDock


def _file_names(result):
    return sorted(item.file_info.name for item in result["files"] if not item.file_info.is_dir)


def _browse_with_top_controls(dock, directory):
    return dock.executor.execute_browse(
        directory=str(directory),
        show_hidden=dock.chk_all.isChecked(),
        recursive=dock.chk_recursive.isChecked(),
        filters=dock._build_filters(),
    )


def _search_result_for(path: Path) -> SearchResult:
    return SearchResult(file_info=FileListExecutor._get_file_info(str(path)), matches=[], match_count=0)


def _finish_browse_with_result(dock, directory: Path, result, *, long_format: bool, human_readable: bool):
    dock._current_browse_params = {
        "directory": str(directory),
        "show_hidden": dock.chk_all.isChecked(),
        "recursive": dock.chk_recursive.isChecked(),
        "filters": dock._build_filters(),
        "long_format": long_format,
        "human_readable": human_readable,
        "start_time": time.time(),
    }
    dock._on_browse_finished(result)


def test_hidden_and_recursive_checkboxes_change_browse_scope(qapp, tmp_path):
    """All/Hidden and Recursive checkboxes should affect the files browsed."""
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "nested.txt").write_text("nested", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.chk_all.setChecked(False)
        dock.chk_recursive.setChecked(False)
        result = _browse_with_top_controls(dock, tmp_path)
        assert _file_names(result) == ["visible.txt"]

        dock.chk_all.setChecked(True)
        dock.chk_recursive.setChecked(True)
        result = _browse_with_top_controls(dock, tmp_path)
        assert _file_names(result) == [".hidden.txt", "nested.txt", "visible.txt"]
    finally:
        dock.deleteLater()


def test_include_globs_field_accepts_multiple_patterns(qapp, tmp_path):
    """Include globs should support comma/semicolon-separated patterns and path globs."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("main", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.py").write_text("guide", encoding="utf-8")
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.ed_inc.setText("**/src/**;*.md")

        filters = dock._build_filters()
        result = dock.executor.execute_browse(str(tmp_path), show_hidden=False, recursive=True, filters=filters)

        assert filters["include_globs"] == ["**/src/**", "*.md"]
        assert _file_names(result) == ["README.md", "main.py"]
    finally:
        dock.deleteLater()


def test_exclude_globs_field_accepts_file_and_path_patterns(qapp, tmp_path):
    """Exclude globs should support filename globs and path globs such as **/src/**."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("main", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.py").write_text("guide", encoding="utf-8")
    (tmp_path / "temp.tmp").write_text("tmp", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.ed_exc.setText("**/src/**,*.tmp")

        filters = dock._build_filters()
        result = dock.executor.execute_browse(str(tmp_path), show_hidden=False, recursive=True, filters=filters)

        assert filters["exclude_globs"] == ["**/src/**", "*.tmp"]
        assert _file_names(result) == ["guide.py"]
    finally:
        dock.deleteLater()


def test_long_human_and_sort_checkboxes_change_table_output(qapp, tmp_path):
    """Long/Human/Sort checkboxes should alter table formatting and ordering."""
    first = tmp_path / "b.txt"
    second = tmp_path / "a.txt"
    first.write_bytes(b"x" * 2048)
    second.write_bytes(b"x" * 100)

    result = {"files": [_search_result_for(first), _search_result_for(second)]}
    dock = FileExplorerDock()
    try:
        dock.chk_sort_results.setChecked(True)
        _finish_browse_with_result(dock, tmp_path, result, long_format=True, human_readable=False)

        assert dock.last_browse_results[0]["name"] == "a.txt"
        assert dock.table_manager.table.item(0, dock.table_manager.COL_NAME).text() == "a.txt"
        assert dock.table_manager.table.item(0, dock.table_manager.COL_SIZE).text() == "100"
        assert ":" in dock.table_manager.table.item(0, dock.table_manager.COL_PERMISSIONS).text()
    finally:
        dock.deleteLater()

    dock = FileExplorerDock()
    try:
        _finish_browse_with_result(dock, tmp_path, result, long_format=False, human_readable=True)

        assert dock.table_manager.table.item(0, dock.table_manager.COL_SIZE).text() == "2.0 KB"
        assert ":" not in dock.table_manager.table.item(0, dock.table_manager.COL_PERMISSIONS).text()
    finally:
        dock.deleteLater()
