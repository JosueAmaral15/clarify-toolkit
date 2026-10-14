"""Regression tests for File Explorer incremental content search."""

import os
import sys
import time
from pathlib import Path

from PySide6.QtCore import QSettings  # pylint: disable=no-name-in-module

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.core.file_explorer_executor import SearchResult, UnifiedFileExplorerExecutor
from src.core.file_list_executor import FileListExecutor
from src.gui.file_explorer_dock import FileExplorerDock
from src.i18n.translator import get_translator, tr


class _NoopHistory:
    def add_operation(self, *_args, **_kwargs):
        return None


def _search_result(path: Path) -> SearchResult:
    return SearchResult(file_info=FileListExecutor._get_file_info(str(path)), matches=[], match_count=0)


def _names(result):
    return sorted(search_result.file_info.name for search_result in result["files"])


def test_executor_candidate_paths_limit_content_search_universe(tmp_path):
    """candidate_paths should restrict content search to the previous universe."""
    keep = tmp_path / "keep.txt"
    skipped = tmp_path / "skipped.txt"
    keep.write_text("needle here", encoding="utf-8")
    skipped.write_text("needle here too", encoding="utf-8")

    executor = UnifiedFileExplorerExecutor()
    result = executor.execute_search(
        directory=str(tmp_path),
        filename_pattern=None,
        content_query="needle",
        search_options={},
        show_hidden=False,
        recursive=False,
        filters={"candidate_paths": [str(keep)]},
    )

    assert _names(result) == ["keep.txt"]
    assert result["stats"]["incremental_universe"] is True
    assert result["stats"]["candidate_paths_count"] == 1


def test_executor_candidate_paths_still_apply_new_filename_filter(tmp_path):
    """A later filename filter should refine the previous universe, not expand it."""
    first = tmp_path / "first.txt"
    second = tmp_path / "second.md"
    outside = tmp_path / "outside.txt"
    first.write_text("needle", encoding="utf-8")
    second.write_text("needle", encoding="utf-8")
    outside.write_text("needle", encoding="utf-8")

    executor = UnifiedFileExplorerExecutor()
    result = executor.execute_search(
        directory=str(tmp_path),
        filename_pattern="*.txt",
        content_query="needle",
        search_options={},
        show_hidden=False,
        recursive=False,
        filters={"candidate_paths": [str(first), str(second)]},
    )

    assert _names(result) == ["first.txt"]


def test_dock_attaches_incremental_universe_only_for_same_directory_and_content(qapp, tmp_path):
    """The dock should only use prior results when directory and content query match."""
    current_dir = str(tmp_path)
    other_dir = str(tmp_path / "other")
    paths = [str(tmp_path / "one.txt"), str(tmp_path / "two.txt")]

    dock = FileExplorerDock()
    try:
        dock.chk_reuse_previous.setChecked(False)
        dock._last_content_search_universe = {
            "directory": current_dir,
            "content_query": "needle",
            "paths": paths,
        }

        assert dock._attach_incremental_universe_filter({}, current_dir, "needle") is None
        dock.chk_reuse_previous.setChecked(True)
        filters = {}
        assert dock._attach_incremental_universe_filter(filters, current_dir, "needle") == paths
        assert filters["candidate_paths"] == paths

        assert dock._attach_incremental_universe_filter({}, other_dir, "needle") is None
        assert dock._attach_incremental_universe_filter({}, current_dir, "different") is None
        assert dock._attach_incremental_universe_filter({}, current_dir, "") is None
    finally:
        dock.deleteLater()


def test_reuse_checkbox_is_opt_in_and_persists_explicit_choice(qapp):
    settings = QSettings("Clarify", "FileExplorer")
    had_previous = settings.contains("reuse_previous_results")
    previous = settings.value("reuse_previous_results")
    settings.remove("reuse_previous_results")
    settings.sync()
    dock = FileExplorerDock()
    restored = None
    try:
        assert not dock.chk_reuse_previous.isChecked()
        dock.chk_reuse_previous.setChecked(True)
        assert dock.settings.value("reuse_previous_results", False, type=bool)

        restored = FileExplorerDock()
        assert restored.chk_reuse_previous.isChecked()
    finally:
        if restored is not None:
            restored.deleteLater()
        dock.deleteLater()
        if had_previous:
            settings.setValue("reuse_previous_results", previous)
        else:
            settings.remove("reuse_previous_results")
        settings.sync()


def test_reuse_checkbox_retranslates_in_every_supported_language(qapp):
    translator = get_translator()
    original_language = translator.current_language
    dock = FileExplorerDock()
    try:
        for language in ("en", "pt_BR", "es", "fr", "de", "ja", "zh"):
            translator.switch_language(language)
            assert dock.chk_reuse_previous.text() == tr(
                "file_explorer.reuse_previous"
            )
            assert dock.chk_reuse_previous.toolTip() == tr(
                "file_explorer.reuse_previous_tooltip"
            )
            assert dock.chk_reuse_previous.text() != "file_explorer.reuse_previous"
    finally:
        translator.switch_language(original_language)
        dock.deleteLater()
        qapp.processEvents()


def test_search_criteria_changes_invalidate_previous_result_cache(qapp):
    dock = FileExplorerDock()
    try:
        changes = (
            lambda: dock.combo_type.setCurrentIndex(1),
            lambda: dock.ed_inc.setText("*.txt"),
            lambda: dock.ed_exc.setText("build;.git"),
            lambda: dock.filename_panel.set_pattern("*.py"),
            lambda: dock.content_panel.set_query("different"),
            lambda: dock.filter_panel.ed_size_min.setText("1"),
        )
        for change in changes:
            dock._last_content_search_universe = {"paths": ["stale"]}
            change()
            assert dock._last_content_search_universe is None
    finally:
        dock.deleteLater()


def test_dock_remembers_empty_content_search_as_empty_universe(qapp, tmp_path, monkeypatch):
    """A zero-result content search should become an empty universe until query/directory changes."""
    import src.gui.progress as progress

    monkeypatch.setattr(progress, "OperationHistory", lambda: _NoopHistory())

    dock = FileExplorerDock()
    try:
        dock.chk_reuse_previous.setChecked(True)
        dock._current_search_params = {
            "directory": str(tmp_path),
            "filename_pattern": None,
            "content_query": "needle",
            "search_options": {},
            "start_time": time.time(),
        }

        dock._on_search_finished({"files": []})

        filters = {}
        assert dock._last_content_search_universe == {
            "directory": str(tmp_path),
            "content_query": "needle",
            "paths": [],
        }
        assert dock._attach_incremental_universe_filter(filters, str(tmp_path), "needle") == []
        assert filters["candidate_paths"] == []
    finally:
        dock.deleteLater()


def test_dock_remembers_latest_content_search_paths(qapp, tmp_path, monkeypatch):
    """Finished content searches should provide candidate paths for the next compatible search."""
    import src.gui.progress as progress

    monkeypatch.setattr(progress, "OperationHistory", lambda: _NoopHistory())

    found = tmp_path / "found.txt"
    found.write_text("needle", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.chk_reuse_previous.setChecked(True)
        dock._current_search_params = {
            "directory": str(tmp_path),
            "filename_pattern": None,
            "content_query": "needle",
            "search_options": {},
            "start_time": time.time(),
        }

        dock._on_search_finished({"files": [_search_result(found)]})

        filters = {}
        assert dock._attach_incremental_universe_filter(filters, str(tmp_path), "needle") == [str(found)]
        assert filters["candidate_paths"] == [str(found)]
    finally:
        dock.deleteLater()
