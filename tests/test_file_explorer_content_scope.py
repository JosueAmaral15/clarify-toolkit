"""Regression tests for File Explorer text/binary content search scope."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.core.file_explorer_executor import UnifiedFileExplorerExecutor
from src.gui.widgets.search_widgets import SearchOptionsPanel
from src.i18n import tr


def _result_names(result):
    return sorted(search_result.file_info.name for search_result in result["files"])


def _search(directory: Path, query: str, content_scope: str | None = None):
    options = {"case_sensitive": False, "whole_word": False, "regex": False}
    if content_scope is not None:
        options["content_scope"] = content_scope

    executor = UnifiedFileExplorerExecutor()
    return executor.execute_search(
        directory=str(directory),
        filename_pattern=None,
        content_query=query,
        search_options=options,
        show_hidden=False,
        recursive=False,
        filters={},
    )


def test_default_content_scope_searches_text_files_only(tmp_path):
    """Default content search should not decode binary files as text."""
    (tmp_path / "plain.txt").write_text("needle in text", encoding="utf-8")
    (tmp_path / "blob.bin").write_bytes(b"\x00needle in binary\xff")

    result = _search(tmp_path, "needle")

    assert _result_names(result) == ["plain.txt"]
    assert result["stats"]["content_scope"] == "text"
    assert result["stats"]["binary_files_searched"] == 0
    assert result["stats"]["content_scope_skipped"] == 1


def test_text_scope_accepts_utf8_with_accents(tmp_path):
    """UTF-8 text with Portuguese accents should remain searchable as text."""
    (tmp_path / "pt.txt").write_text("O coração tem uma agulha aqui.", encoding="utf-8")
    (tmp_path / "blob.bin").write_bytes(b"\x00cora\xc3\xa7\xc3\xa3o\xff")

    result = _search(tmp_path, "coração", "text")

    assert _result_names(result) == ["pt.txt"]
    assert result["files"][0].matches[0].snippet == "O coração tem uma agulha aqui."


def test_binary_scope_searches_binary_files_only(tmp_path):
    """Binary scope should search bytes and skip text files."""
    (tmp_path / "plain.txt").write_text("needle in text", encoding="utf-8")
    (tmp_path / "blob.bin").write_bytes(b"\x00prefix needle suffix\xff")

    result = _search(tmp_path, "needle", "binary")

    assert _result_names(result) == ["blob.bin"]
    assert result["stats"]["text_files_searched"] == 0
    assert result["stats"]["binary_files_searched"] == 1
    assert result["files"][0].matches[0].snippet.startswith("bytes ")


def test_both_scope_returns_text_and_binary_matches(tmp_path):
    """Both scope should return matches from text and binary files."""
    (tmp_path / "plain.txt").write_text("needle in text", encoding="utf-8")
    (tmp_path / "blob.bin").write_bytes(b"\x00prefix needle suffix\xff")

    result = _search(tmp_path, "needle", "both")

    assert _result_names(result) == ["blob.bin", "plain.txt"]
    assert result["stats"]["text_files_searched"] == 1
    assert result["stats"]["binary_files_searched"] == 1


def test_replace_skips_binary_results(tmp_path):
    """Replace remains text-only even when search found a binary result."""
    binary_path = tmp_path / "blob.bin"
    binary_path.write_bytes(b"\x00prefix needle suffix\xff")

    executor = UnifiedFileExplorerExecutor()
    search_result = executor.execute_search(
        directory=str(tmp_path),
        filename_pattern=None,
        content_query="needle",
        search_options={"content_scope": "binary"},
        show_hidden=False,
        recursive=False,
        filters={},
    )

    replace_result = executor.execute_replace(
        search_result["files"],
        search_query="needle",
        replacement="changed",
        search_options={},
        replace_all=True,
    )

    assert replace_result["replaced_count"] == 0
    assert replace_result["files_modified"] == 0
    assert "replace supports text files only" in replace_result["errors"][0]
    assert binary_path.read_bytes() == b"\x00prefix needle suffix\xff"


def test_search_options_panel_exposes_content_scope(qapp):
    """The UI should expose Text/ASCII, Binary, and Both content scopes."""
    panel = SearchOptionsPanel()
    try:
        assert panel.get_options()["content_scope"] == "text"
        assert [
            panel.combo_content_scope.itemText(index)
            for index in range(panel.combo_content_scope.count())
        ] == [
            tr("search.content_scope_text"),
            tr("search.content_scope_binary"),
            tr("search.content_scope_both"),
        ]
        assert panel.lbl_content_scope.text() == tr("search.lbl_content_scope")
        assert panel.combo_content_scope.toolTip() == tr("search.tooltip_content_scope")
        assert panel.lbl_content_scope.toolTip() == tr("search.tooltip_content_scope")
        assert "64 KiB" in panel.combo_content_scope.toolTip()

        panel.set_options({"content_scope": "binary"})
        assert panel.get_options()["content_scope"] == "binary"

        panel.set_options({"content_scope": "both"})
        panel.retranslateUi()
        assert panel.get_options()["content_scope"] == "both"
    finally:
        panel.deleteLater()
