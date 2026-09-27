"""Regression tests for File Explorer filename/content regex separation."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.core.file_explorer_executor import UnifiedFileExplorerExecutor
from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.widgets.search_widgets import FileNameQueryPanel


def _result_names(result):
    return sorted(search_result.file_info.name for search_result in result["files"])


def _search_by_name(directory: Path, pattern: str, options: dict | None = None):
    executor = UnifiedFileExplorerExecutor()
    return executor.execute_search(
        directory=str(directory),
        filename_pattern=pattern,
        content_query=None,
        search_options=options or {},
        show_hidden=False,
        recursive=False,
        filters={},
    )


def test_filename_pattern_uses_glob_by_default(tmp_path):
    """Filename search should keep wildcard glob behavior as the default."""
    (tmp_path / "keep_1.txt").write_text("one", encoding="utf-8")
    (tmp_path / "keep_2.txt").write_text("two", encoding="utf-8")
    (tmp_path / "keep_x.txt").write_text("x", encoding="utf-8")
    (tmp_path / "other.md").write_text("other", encoding="utf-8")

    result = _search_by_name(tmp_path, "keep_*.txt")

    assert _result_names(result) == ["keep_1.txt", "keep_2.txt", "keep_x.txt"]


def test_content_regex_option_does_not_turn_filename_glob_into_regex(tmp_path):
    """The content Regex checkbox must not change filename pattern semantics."""
    (tmp_path / "keep_1.txt").write_text("one", encoding="utf-8")
    (tmp_path / "keep_2.txt").write_text("two", encoding="utf-8")

    result = _search_by_name(
        tmp_path,
        r"^keep_\d+\.txt$",
        {"regex": True, "filename_regex": False},
    )

    assert _result_names(result) == []


def test_filename_regex_mode_matches_filename_regular_expressions(tmp_path):
    """Filename regex mode should make regex patterns effective in the executor."""
    (tmp_path / "keep_1.txt").write_text("one", encoding="utf-8")
    (tmp_path / "keep_2.txt").write_text("two", encoding="utf-8")
    (tmp_path / "keep_x.txt").write_text("x", encoding="utf-8")

    result = _search_by_name(
        tmp_path,
        r"^keep_\d+\.txt$",
        {"filename_regex": True, "case_sensitive": True},
    )

    assert _result_names(result) == ["keep_1.txt", "keep_2.txt"]


def test_filename_query_panel_exposes_filename_regex_mode(qapp):
    """The filename panel should own filename regex mode explicitly."""
    panel = FileNameQueryPanel()
    try:
        assert panel.get_use_regex() is False

        panel.set_pattern(r"^keep_\d+\.txt$")
        panel.set_use_regex(True)

        assert panel.get_pattern() == r"^keep_\d+\.txt$"
        assert panel.get_use_regex() is True
    finally:
        panel.deleteLater()


def test_file_explorer_dock_includes_filename_regex_in_search_options(qapp):
    """The dock should pass filename regex mode separately from content regex."""
    dock = FileExplorerDock()
    try:
        dock.filename_panel.set_use_regex(True)
        dock.search_options_panel.set_options({"regex": False})

        options = dock._get_search_options()

        assert options["filename_regex"] is True
        assert options["regex"] is False
    finally:
        dock.deleteLater()
