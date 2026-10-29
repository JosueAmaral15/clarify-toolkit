"""Regressions for theme-safe Editor read-only and edit-only indicators."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial

import pytest
from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QTextEdit

from src.gui import editor_dock as dock_module
from src.gui.json_editor_tab import JsonEditorTab
from src.gui.widgets.editor_tab import EditorTab
from src.theme_manager import ThemeManager


@pytest.fixture(autouse=True)
def restore_application_theme(qapp):
    palette = QtGui.QPalette(qapp.palette())
    stylesheet = qapp.styleSheet()
    style_name = qapp.style().objectName()
    yield
    qapp.setStyle(style_name)
    qapp.setPalette(palette)
    qapp.setStyleSheet(stylesheet)


def make_dock(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        dock_module,
        "UnsavedRecoveryStore",
        partial(dock_module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    dock = dock_module.EditorDock()
    qtbot.addWidget(dock)
    return dock


def editor_colors(editor):
    palette = editor.viewport().palette()
    return (
        palette.color(QtGui.QPalette.ColorRole.Base),
        palette.color(QtGui.QPalette.ColorRole.Text),
    )


def assert_dark_editor(editor):
    background, foreground = editor_colors(editor)
    assert background.lightness() < 80
    assert foreground.lightness() > background.lightness()


def assert_light_editor(editor):
    background, foreground = editor_colors(editor)
    assert background.lightness() > 180
    assert foreground.lightness() < background.lightness()


def test_text_edit_only_indicator_does_not_override_dark_theme(qapp, qtbot):
    ThemeManager.apply_theme(qapp, "dark")
    tab = EditorTab(edit_only_mode=True)
    qtbot.addWidget(tab)
    tab.show()
    qapp.processEvents()

    stylesheet = tab.editor.styleSheet().lower()
    assert "border" in stylesheet
    assert "background" not in stylesheet
    assert "color:" not in stylesheet
    assert_dark_editor(tab.editor)
    assert "edit-only" in tab.editor.accessibleDescription().lower()


def test_edit_only_toggle_preserves_content_selection_undo_and_editability(qapp, qtbot):
    ThemeManager.apply_theme(qapp, "dark")
    tab = EditorTab()
    qtbot.addWidget(tab)
    tab.editor.setPlainText("alpha beta")
    cursor = tab.editor.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(5, QtGui.QTextCursor.MoveMode.KeepAnchor)
    tab.editor.setTextCursor(cursor)
    undo_available = tab.editor.document().isUndoAvailable()

    tab.toggle_edit_only_mode()

    current = tab.editor.textCursor()
    assert tab.editor.toPlainText() == "alpha beta"
    assert (current.selectionStart(), current.selectionEnd()) == (1, 5)
    assert tab.editor.document().isUndoAvailable() == undo_available
    assert not tab.editor.isReadOnly()
    assert tab.editor.property("clarifyEditOnly") is True
    assert "edit-only" in tab.editor.accessibleDescription().lower()
    assert_dark_editor(tab.editor)


def test_actual_read_only_text_view_tracks_runtime_theme(qapp, qtbot):
    tab = EditorTab()
    qtbot.addWidget(tab)
    tab.editor.setPlainText("read only")
    tab.editor.setReadOnly(True)

    ThemeManager.apply_theme(qapp, "light")
    qapp.processEvents()
    assert_light_editor(tab.editor)
    ThemeManager.apply_theme(qapp, "dark")
    qapp.processEvents()
    assert_dark_editor(tab.editor)

    assert tab.editor.isReadOnly()
    assert tab.editor.toPlainText() == "read only"


def test_json_edit_only_keeps_theme_validation_and_accessibility(qapp, qtbot):
    ThemeManager.apply_theme(qapp, "dark")
    tab = JsonEditorTab(edit_only_mode=True)
    qtbot.addWidget(tab)
    tab.editor.setPlainText("{")
    tab._validate()
    diagnostic_style = tab.editor.styleSheet()
    highlighter = tab.highlighter

    assert "#F44747" in diagnostic_style
    assert "background" not in diagnostic_style.lower()
    assert_dark_editor(tab.editor)
    assert "edit-only" in tab.editor.accessibleDescription().lower()

    tab.toggle_edit_only_mode()
    assert tab.editor.toPlainText() == "{"
    assert tab.highlighter is highlighter
    assert tab.editor.styleSheet() == diagnostic_style
    assert tab.editor.property("clarifyEditOnly") is False
    assert_dark_editor(tab.editor)


def test_json_actual_read_only_view_tracks_runtime_theme(qapp, qtbot):
    tab = JsonEditorTab()
    qtbot.addWidget(tab)
    tab.editor.setPlainText("{}")
    tab._validate()
    tab.editor.setReadOnly(True)

    ThemeManager.apply_theme(qapp, "light")
    qapp.processEvents()
    assert_light_editor(tab.editor)
    ThemeManager.apply_theme(qapp, "dark")
    qapp.processEvents()
    assert_dark_editor(tab.editor)

    assert tab.editor.isReadOnly()
    assert tab.editor.toPlainText() == "{}"


def test_split_read_only_state_and_theme_follow_primary_without_document_copy(qapp, qtbot, tmp_path, monkeypatch):
    ThemeManager.apply_theme(qapp, "dark")
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    dock._new_file()
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("shared")
    tab.editor.setReadOnly(True)
    document = tab.editor.document()

    assert dock._show_split_view(tab, QtCore.Qt.Orientation.Horizontal)
    assert dock.split_editor.document() is document
    assert dock.split_editor.isReadOnly()
    assert_dark_editor(tab.editor)
    assert_dark_editor(dock.split_editor)
    assert [dock.tab_widget.widget(index).get_tab_title() for index in range(dock.tab_widget.count())] == [
        "Untitled",
        "Untitled-2",
    ]

    ThemeManager.apply_theme(qapp, "light")
    qapp.processEvents()
    assert_light_editor(tab.editor)
    assert_light_editor(dock.split_editor)


def test_find_extra_selections_survive_edit_only_theme_transition(qapp, qtbot):
    ThemeManager.apply_theme(qapp, "dark")
    tab = EditorTab()
    qtbot.addWidget(tab)
    tab.editor.setPlainText("match match")
    selection = QTextEdit.ExtraSelection()
    cursor = tab.editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(5, QtGui.QTextCursor.MoveMode.KeepAnchor)
    selection.cursor = cursor
    selection.format.setBackground(QtGui.QColor("#336699"))
    tab.editor.setExtraSelections([selection])

    tab.toggle_edit_only_mode()

    selections = tab.editor.extraSelections()
    assert len(selections) == 1
    assert (selections[0].cursor.selectionStart(), selections[0].cursor.selectionEnd()) == (
        0,
        5,
    )
    assert_dark_editor(tab.editor)
