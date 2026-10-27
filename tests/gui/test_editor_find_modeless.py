"""Modeless single-session regressions for Clarify Editor Find/Replace."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtGui import QTextCursor

from src.editor_notes import TemporaryNoteStore
from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    """Create an EditorDock with private settings and managed stores."""
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
    qtbot.addWidget(widget)
    widget.show()
    qapp.processEvents()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def test_find_action_is_modeless_and_uses_the_lower_panel(dock, monkeypatch, qapp):
    """Find must return immediately instead of entering a nested event loop."""
    dock._new_file()
    monkeypatch.setattr(
        module._EditorFindDialog,
        "exec",
        lambda _dialog: pytest.fail("Find invoked blocking QDialog.exec()"),
    )

    dock._show_find_dialog(False)
    qapp.processEvents()

    assert dock._find_dialog is not None
    assert dock._find_panel_host.isVisibleTo(dock)
    assert not dock._find_dialog.isWindow()
    assert dock._find_dialog.find_input.hasFocus()


def test_docked_and_floating_modes_reuse_one_session_and_persist(dock, qapp):
    """Changing presentation must reparent, not clone, the Find session."""
    dock._new_file()
    dock._show_find_dialog(True)
    dialog = dock._find_dialog
    dialog.find_input.setText("needle")
    dialog.replace_input.setText("replacement")
    dialog.chk_case_sensitive.setChecked(True)

    dock._toggle_find_presentation()
    qapp.processEvents()

    assert dock._find_dialog is dialog
    assert dock._find_presentation_mode == "floating"
    assert dialog.isWindow()
    assert dialog.isVisible()
    assert not dock._find_panel_host.isVisible()
    assert dialog.find_input.text() == "needle"
    assert dialog.replace_input.text() == "replacement"
    assert dialog.chk_case_sensitive.isChecked()
    assert dock.settings.value("find/presentation_mode", type=str) == "floating"

    dock._toggle_find_presentation()
    qapp.processEvents()

    assert dock._find_dialog is dialog
    assert dock._find_presentation_mode == "docked"
    assert not dialog.isWindow()
    assert dock._find_panel_host.isVisibleTo(dock)


def test_find_and_replace_routes_share_session_and_active_buffer_history(dock, qapp):
    """Actions and tab changes must retarget one session without leaking values."""
    dock._new_file()
    first = dock.tab_widget.currentWidget()
    first.editor.setPlainText("first needle")
    dock._show_find_dialog(False)
    dialog = dock._find_dialog
    dialog.find_input.setText("first")

    dock._new_file()
    second = dock.tab_widget.currentWidget()
    second.editor.setPlainText("second needle")
    qapp.processEvents()

    assert dock._find_dialog is dialog
    assert dialog.editor is second.editor
    assert dialog.find_input.text() == ""

    cursor = second.editor.textCursor()
    cursor.setPosition(7)
    cursor.setPosition(13, QTextCursor.MoveMode.KeepAnchor)
    second.editor.setTextCursor(cursor)
    dock._show_find_dialog(True)

    assert dock._find_dialog is dialog
    assert dialog.replace_enabled
    assert dialog.replace_input.isVisibleTo(dialog)
    assert dialog.find_input.text() == "needle"

    dock.tab_widget.setCurrentWidget(first)
    qapp.processEvents()

    assert dialog.editor is first.editor
    assert dialog.find_input.text() == "first"


def test_close_hides_session_and_editor_close_disconnects_it(dock, qapp):
    """Panel close is reusable while Editor close releases all callbacks."""
    dock._new_file()
    dock._show_find_dialog(False)
    dialog = dock._find_dialog

    dialog.btn_close.click()
    qapp.processEvents()

    assert dock._find_dialog is dialog
    assert not dialog.isVisible()
    assert not dock._find_panel_host.isVisible()

    dock._show_find_dialog(False)
    assert dock._find_dialog is dialog
    assert dialog.isVisibleTo(dock)
    dock._toggle_find_presentation()
    qapp.processEvents()
    assert dialog.isWindow()

    assert dock.close()
    qapp.processEvents()
    assert dock._find_dialog is None


def test_active_split_retargets_same_session_on_focus_change(dock, qapp):
    """The panel follows the active view of one shared document."""
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("shared needle")
    assert dock._show_split_view(tab, QtCore.Qt.Orientation.Horizontal)
    dock._show_find_dialog(False)
    dialog = dock._find_dialog

    assert dialog.editor is dock.split_editor

    tab.editor.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
    qapp.processEvents()

    assert dock._find_dialog is dialog
    assert dialog.editor is tab.editor


def test_open_session_retranslates_without_recreation(dock, qapp):
    """Runtime language changes update both hosts through the one widget."""
    dock._new_file()
    dock._show_find_dialog(False)
    dialog = dock._find_dialog
    translator = module.get_translator()
    original = translator.current_language
    target = "pt_BR" if original != "pt_BR" else "en"

    try:
        translator.switch_language(target)
        qapp.processEvents()

        assert dock._find_dialog is dialog
        assert dialog.lbl_find.text() == translator.get("editor.lbl_find")
        assert dialog.btn_toggle_presentation.text() == translator.get(
            "editor.btn_find_float"
        )
    finally:
        translator.switch_language(original)
