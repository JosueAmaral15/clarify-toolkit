"""Effective File/Edit/View shortcut regressions for Clarify Editor."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QLineEdit, QMainWindow

from src.editor_notes import TemporaryNoteStore
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
    settings = QtCore.QSettings(
        str(tmp_path / "editor.ini"),
        QtCore.QSettings.IniFormat,
    )
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    monkeypatch.setattr(
        module,
        "TemporaryNoteStore",
        partial(TemporaryNoteStore, root=tmp_path / "notes"),
    )
    widget = module.EditorDock()
    widget.show()
    qtbot.addWidget(widget)
    qapp.processEvents()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def _portable_shortcuts(action):
    return tuple(sequence.toString(QKeySequence.PortableText) for sequence in action.shortcuts())


def _menu_action_ids(dock):
    for menu_id in ("file", "edit", "view"):
        for action_id in dock._MENU_SPECS[menu_id]["items"]:
            if action_id is not None:
                yield menu_id, action_id


def test_every_file_edit_view_command_has_one_managed_binding(dock):
    """Visible commands must be configurable through the central registry."""
    registered = ShortcutManager.get_registered_shortcuts(dock)
    registered_names = {binding.action_name for binding in registered}

    for menu_id, action_id in _menu_action_ids(dock):
        action = dock._action_by_id[action_id]
        shortcut_action = dock._ACTION_SPECS[action_id].get("shortcut_action")
        assert shortcut_action, f"{menu_id}.{action_id} lacks a managed action"
        assert action.shortcuts(), f"{menu_id}.{action_id} lacks a shortcut"
        assert action.property("clarify_shortcut_action") == shortcut_action
        assert action.property("clarify_shortcut_category") == f"Editor {menu_id.title()}"
        assert shortcut_action in registered_names


def test_editor_shortcuts_are_scoped_to_the_editor_widget_tree(dock):
    for _menu_id, action_id in _menu_action_ids(dock):
        assert dock._action_by_id[action_id].shortcutContext() == Qt.ShortcutContext.WidgetWithChildrenShortcut


def test_replace_uses_ctrl_h_once_and_drops_legacy_ctrl_r(dock, qtbot, monkeypatch):
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setFocus()
    calls = []
    monkeypatch.setattr(
        dock,
        "_show_find_dialog",
        lambda replace_enabled: calls.append(replace_enabled),
    )

    assert _portable_shortcuts(dock.action_find_replace) == ("Ctrl+H",)
    qtbot.keyClick(editor, Qt.Key.Key_H, Qt.KeyboardModifier.ControlModifier)
    assert calls == [True]

    qtbot.keyClick(editor, Qt.Key.Key_R, Qt.KeyboardModifier.ControlModifier)
    assert calls == [True]


def test_customization_updates_live_editor_action_and_registry(dock, qapp, qtbot, monkeypatch):
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setFocus()
    calls = []
    monkeypatch.setattr(
        dock,
        "_show_find_dialog",
        lambda replace_enabled: calls.append(replace_enabled),
    )
    ShortcutManager.set_custom_shortcut("replace", "Ctrl+Alt+H")
    qapp.processEvents()

    assert _portable_shortcuts(dock.action_find_replace) == ("Ctrl+Alt+H",)
    binding = next(item for item in ShortcutManager.get_registered_shortcuts(dock) if item.action_name == "replace")
    assert binding.sequences == ("Ctrl+Alt+H",)
    assert binding.customized
    qtbot.keyClick(
        editor,
        Qt.Key.Key_H,
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
    )
    assert calls == [True]


def test_editor_defaults_do_not_conflict_with_tool_or_os_defaults(dock):
    seen = set()
    for _menu_id, action_id in _menu_action_ids(dock):
        shortcut_action = dock._ACTION_SPECS[action_id]["shortcut_action"]
        if shortcut_action in seen:
            continue
        seen.add(shortcut_action)
        for sequence in ShortcutManager.get_key_sequences(shortcut_action):
            portable = sequence.toString(QKeySequence.PortableText)
            assert ShortcutManager.get_conflicts(portable) == [shortcut_action]
            assert not ShortcutManager.is_os_shortcut(portable)


def test_find_replace_action_reuses_single_modeless_session(dock, qtbot, qapp):
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setPlainText("needle needle")
    editor.setFocus()

    qtbot.keyClick(editor, Qt.Key.Key_H, Qt.KeyboardModifier.ControlModifier)
    qapp.processEvents()
    dialog = dock._find_dialog

    assert dialog is not None
    assert dialog.replace_enabled
    assert dialog.find_input.hasFocus()

    dock.action_find.trigger()
    assert dock._find_dialog is dialog
    assert not dialog.replace_enabled


def test_editor_shortcuts_do_not_activate_from_another_tool(dock, qtbot, qapp):
    main = QMainWindow()
    outside = QLineEdit(main)
    main.setCentralWidget(outside)
    main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
    qtbot.addWidget(main)
    main.show()
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    initial_count = dock.tab_widget.count()

    outside.setFocus()
    qtbot.keyClick(outside, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
    qapp.processEvents()
    assert dock.tab_widget.count() == initial_count

    editor.setFocus()
    qtbot.keyClick(editor, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
    qapp.processEvents()
    assert dock.tab_widget.count() == initial_count + 1

    main.removeDockWidget(dock)
    dock.setParent(None)
    main.close()


def test_two_step_file_chord_invokes_one_existing_handler(dock, qtbot, monkeypatch):
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setFocus()
    calls = []
    monkeypatch.setattr(
        dock,
        "_open_explorer_folder",
        lambda: calls.append("open-folder"),
    )

    qtbot.keyClick(editor, Qt.Key.Key_K, Qt.KeyboardModifier.ControlModifier)
    qtbot.keyClick(editor, Qt.Key.Key_O, Qt.KeyboardModifier.ControlModifier)

    assert calls == ["open-folder"]
