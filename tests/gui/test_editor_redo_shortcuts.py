"""Focused Clarify Editor Redo action and shortcut regressions."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QLineEdit, QMainWindow

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module
from src.shortcut_manager import ShortcutManager


@pytest.fixture(autouse=True)
def reset_shortcuts():
    ShortcutManager.reset_all_custom_shortcuts()
    yield
    ShortcutManager.reset_all_custom_shortcuts()


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    widget = module.EditorDock()
    qtbot.addWidget(widget)
    widget.show()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def portable_shortcuts(action):
    return [item.toString(QKeySequence.PortableText) for item in action.shortcuts()]


def test_redo_action_uses_both_managed_default_shortcuts(dock):
    assert portable_shortcuts(dock.action_redo) == ["Ctrl+Y", "Ctrl+Shift+Z"]
    assert dock.action_redo.shortcutContext() == Qt.ShortcutContext.WidgetWithChildrenShortcut
    assert ShortcutManager.get_conflicts("Ctrl+Shift+Z") == ["redo"]


def test_both_keys_trigger_the_same_action_once(dock, qtbot):
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setFocus()
    triggered = []
    dock.action_redo.triggered.connect(lambda checked=False: triggered.append(checked))

    editor.insertPlainText("one")
    editor.undo()
    qtbot.keyClick(
        editor,
        Qt.Key.Key_Z,
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
    )
    assert editor.toPlainText() == "one"
    assert len(triggered) == 1

    editor.undo()
    qtbot.keyClick(editor, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
    assert editor.toPlainText() == "one"
    assert len(triggered) == 2


def test_redo_routes_only_to_the_active_split_view(dock, monkeypatch):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.insertPlainText("one")
    tab.editor.undo()
    assert dock._show_split_view(tab, Qt.Orientation.Horizontal)
    calls = []
    monkeypatch.setattr(tab.editor, "redo", lambda: calls.append("primary"))
    monkeypatch.setattr(dock.split_editor, "redo", lambda: calls.append("split"))

    dock._last_active_editor = dock.split_editor
    dock.action_redo.trigger()

    assert calls == ["split"]


def test_redo_ignores_read_only_view_and_empty_stack(dock, qtbot):
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    initial_status = dock.lbl_status.text()
    editor.setFocus()

    qtbot.keyClick(editor, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
    assert editor.toPlainText() == ""
    assert dock.lbl_status.text() == initial_status

    editor.insertPlainText("one")
    editor.undo()
    editor.setReadOnly(True)
    qtbot.keyClick(
        editor,
        Qt.Key.Key_Z,
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
    )
    assert editor.toPlainText() == ""
    assert dock.lbl_status.text() == initial_status


def test_custom_redo_shortcut_replaces_both_defaults(qapp, qtbot, monkeypatch, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "custom.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "custom-recovery"),
    )
    ShortcutManager.set_custom_shortcut("redo", "Ctrl+Alt+R")
    custom_dock = module.EditorDock()
    qtbot.addWidget(custom_dock)

    assert portable_shortcuts(custom_dock.action_redo) == ["Ctrl+Alt+R"]
    assert ShortcutManager.get_conflicts("Ctrl+Alt+R") == ["redo"]

    custom_dock.close()
    custom_dock.deleteLater()
    qapp.processEvents()


def test_redo_shortcuts_do_not_escape_the_editor_tool(dock, qtbot):
    main = QMainWindow()
    outside = QLineEdit(main)
    main.setCentralWidget(outside)
    main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
    qtbot.addWidget(main)
    main.show()
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.insertPlainText("one")
    editor.undo()

    outside.setFocus()
    qtbot.keyClick(outside, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
    assert editor.toPlainText() == ""

    editor.setFocus()
    qtbot.keyClick(editor, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
    assert editor.toPlainText() == "one"

    main.removeDockWidget(dock)
    dock.setParent(None)
    main.close()
