"""Regression tests for File Explorer Advanced Filters size range."""

import os
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from PySide6.QtCore import QDate

from src.gui.file_explorer_dock import FileExplorerDock


def _result_file_names(result):
    return sorted(item.file_info.name for item in result["files"] if not item.file_info.is_dir)


def test_advanced_size_filters_are_forwarded_to_executor(qapp):
    """Size Min/Max from Advanced Filters must be present in built filters."""
    dock = FileExplorerDock()
    try:
        dock.filter_panel.ed_size_min.setText("1")
        dock.filter_panel.cmb_size_min_unit.setCurrentText("KB")
        dock.filter_panel.ed_size_max.setText("3")
        dock.filter_panel.cmb_size_max_unit.setCurrentText("KB")

        filters = dock._build_filters()

        assert filters["size"] == {"min": 1024, "max": 3072}
    finally:
        dock.deleteLater()


def test_advanced_size_filters_limit_browse_results(qapp, tmp_path):
    """Browse results should honor the Size Min/Max range from Advanced Filters."""
    (tmp_path / "small.txt").write_bytes(b"x" * 100)
    (tmp_path / "medium.txt").write_bytes(b"x" * 2_000)
    (tmp_path / "large.txt").write_bytes(b"x" * 5_000)

    dock = FileExplorerDock()
    try:
        dock.filter_panel.ed_size_min.setText("1")
        dock.filter_panel.cmb_size_min_unit.setCurrentText("KB")
        dock.filter_panel.ed_size_max.setText("3")
        dock.filter_panel.cmb_size_max_unit.setCurrentText("KB")

        filters = dock._build_filters()
        result = dock.executor.execute_browse(
            directory=str(tmp_path),
            show_hidden=False,
            recursive=False,
            filters=filters,
        )

        assert _result_file_names(result) == ["medium.txt"]
    finally:
        dock.deleteLater()


def test_regex_filter_limits_browse_results(qapp, tmp_path):
    """Regex Advanced Filter should apply to filenames."""
    (tmp_path / "keep_alpha.txt").write_text("a", encoding="utf-8")
    (tmp_path / "drop_beta.txt").write_text("b", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.filter_panel.ed_regex.setText(r"^keep_")
        dock.filter_panel.chk_regex_enabled.setChecked(True)

        result = dock.executor.execute_browse(
            directory=str(tmp_path),
            show_hidden=False,
            recursive=False,
            filters=dock._build_filters(),
        )

        assert _result_file_names(result) == ["keep_alpha.txt"]
    finally:
        dock.deleteLater()


def test_mtime_filter_limits_browse_results(qapp, tmp_path):
    """Modified-time Advanced Filter should compare file dates."""
    old_file = tmp_path / "old.txt"
    new_file = tmp_path / "new.txt"
    old_file.write_text("old", encoding="utf-8")
    new_file.write_text("new", encoding="utf-8")

    old_ts = datetime(2025, 12, 31, 12, 0).timestamp()
    new_ts = datetime(2026, 1, 15, 12, 0).timestamp()
    os.utime(old_file, (old_ts, old_ts))
    os.utime(new_file, (new_ts, new_ts))

    dock = FileExplorerDock()
    try:
        dock.filter_panel.chk_mtime_after_enabled.setChecked(True)
        dock.filter_panel.dte_mtime_after.setDate(QDate(2026, 1, 1))

        result = dock.executor.execute_browse(
            directory=str(tmp_path),
            show_hidden=False,
            recursive=False,
            filters=dock._build_filters(),
        )

        assert _result_file_names(result) == ["new.txt"]
    finally:
        dock.deleteLater()


def test_extension_filter_limits_browse_results(qapp, tmp_path):
    """Extension Advanced Filter should honor comma-separated extensions."""
    (tmp_path / "a.py").write_text("py", encoding="utf-8")
    (tmp_path / "b.md").write_text("md", encoding="utf-8")
    (tmp_path / "c.txt").write_text("txt", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.filter_panel.chk_use_ext_filter.setChecked(True)
        dock.filter_panel.ed_extensions.setText("py, txt")

        result = dock.executor.execute_browse(
            directory=str(tmp_path),
            show_hidden=False,
            recursive=False,
            filters=dock._build_filters(),
        )

        assert _result_file_names(result) == ["a.py", "c.txt"]
    finally:
        dock.deleteLater()


def test_depth_and_exclude_dir_filters_limit_recursive_browse(qapp, tmp_path):
    """Depth and excluded-dir filters should affect recursive browsing."""
    (tmp_path / "root.txt").write_text("root", encoding="utf-8")
    (tmp_path / "level1").mkdir()
    (tmp_path / "level1" / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "level1" / "level2").mkdir()
    (tmp_path / "level1" / "level2" / "two.txt").write_text("two", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "hidden.txt").write_text("hidden", encoding="utf-8")
    (tmp_path / "custom_skip").mkdir()
    (tmp_path / "custom_skip" / "custom_hidden.txt").write_text("hidden", encoding="utf-8")

    dock = FileExplorerDock()
    try:
        dock.filter_panel.spn_depth.setValue(1)
        dock.filter_panel.ed_exclude_custom.setText("custom_skip")

        result = dock.executor.execute_browse(
            directory=str(tmp_path),
            show_hidden=False,
            recursive=True,
            filters=dock._build_filters(),
        )

        assert _result_file_names(result) == ["one.txt", "root.txt"]
    finally:
        dock.deleteLater()


def test_advanced_filter_panel_nested_fields_are_forwarded(qapp):
    """Regex and modified-time filters use the same nested panel format as size."""
    dock = FileExplorerDock()
    try:
        dock.filter_panel.ed_regex.setText(r".*\\.txt")
        dock.filter_panel.chk_regex_enabled.setChecked(True)
        dock.filter_panel.chk_mtime_after_enabled.setChecked(True)
        dock.filter_panel.dte_mtime_after.setDate(QDate(2026, 1, 1))
        dock.filter_panel.chk_mtime_before_enabled.setChecked(True)
        dock.filter_panel.dte_mtime_before.setDate(QDate(2026, 1, 31))

        filters = dock._build_filters()

        assert filters["regex"] == {"enabled": True, "pattern": r".*\\.txt"}
        assert filters["mtime"]["after"].isoformat() == "2026-01-01"
        assert filters["mtime"]["before"].isoformat() == "2026-01-31"
    finally:
        dock.deleteLater()
