"""Isolated regressions for Clarify Editor priority stage 1."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QFileDialog

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as editor_dock_module


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    """Create an EditorDock with recovery confined to the test directory."""
    monkeypatch.setattr(
        editor_dock_module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    widget = editor_dock_module.EditorDock()
    qtbot.addWidget(widget)
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def test_first_save_settles_edit_only_tab_state(dock, monkeypatch, tmp_path):
    """A successful first save becomes a clean, file-backed document."""
    target = tmp_path / "first save.txt"
    dock._new_file(edit_only=True)
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("remember this")
    setattr(tab, "_clarify_external_state", "missing")
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(target), "All Files (*)"),
    )

    assert dock._save_file_as() is True

    assert target.read_text(encoding="utf-8") == "remember this"
    assert tab.file_path == str(target)
    assert tab.edit_only_mode is False
    assert tab.is_modified is False
    assert tab.editor.document().isModified() is False
    assert getattr(tab, "_clarify_external_state") == "clean"
    assert str(target) in dock.recent_files
    title = dock.tab_widget.tabText(dock.tab_widget.currentIndex())
    assert "*" not in title
    assert "[missing]" not in title
    assert "\N{LOCK}" not in title


def test_failed_first_save_preserves_unsaved_state(dock, monkeypatch, tmp_path):
    """A failed first save must not claim a path or clear dirty state."""
    target = tmp_path / "failed.txt"
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("draft")
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(target), "All Files (*)"),
    )
    monkeypatch.setattr(tab, "save_file", lambda _path=None: False)
    monkeypatch.setattr(editor_dock_module.QMessageBox, "critical", lambda *_args: None)

    assert dock._save_file_as() is False
    assert tab.file_path is None
    assert tab.is_modified is True
    assert "*" in dock.tab_widget.tabText(dock.tab_widget.currentIndex())


def test_first_save_settles_json_tab_state(dock, monkeypatch, tmp_path):
    """JSON tabs use the same first-save state transition."""
    target = tmp_path / "draft.json"
    tab = dock.load_generated_content('{"value": 1}', "draft.json", extension=".json")
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(target), "JSON Files (*.json)"),
    )

    assert dock._save_file_as() is True
    assert target.read_text(encoding="utf-8") == '{"value": 1}'
    assert tab.is_modified is False
    assert tab.editor.document().isModified() is False
    assert "*" not in dock.tab_widget.tabText(dock.tab_widget.currentIndex())


def test_tab_and_shift_tab_use_editor_indentation(dock, qtbot):
    """Tab indents with the configured unit and Shift+Tab removes one unit."""
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    dock.indent_use_tabs = False
    dock.indent_width = 4

    tab.editor.setPlainText("one\ntwo")
    tab.editor.selectAll()
    qtbot.keyClick(tab.editor, Qt.Key_Tab)
    assert tab.editor.toPlainText() == "    one\n    two"

    tab.editor.selectAll()
    qtbot.keyClick(tab.editor, Qt.Key_Backtab)
    assert tab.editor.toPlainText() == "one\ntwo"

    cursor = tab.editor.textCursor()
    cursor.movePosition(QTextCursor.End)
    tab.editor.setTextCursor(cursor)
    qtbot.keyClick(tab.editor, Qt.Key_Tab)
    assert tab.editor.toPlainText() == "one\ntwo    "


def test_tab_character_preference_is_persisted(dock):
    """The explicit tabs/spaces choice and width survive in QSettings."""
    dock._set_indent_use_tabs(True)
    dock._set_indent_width(8)

    assert dock.indent_use_tabs is True
    assert dock.indent_width == 8
    assert dock.settings.value("indent_use_tabs", False, type=bool) is True
    assert dock.settings.value("indent_width", 0, type=int) == 8
