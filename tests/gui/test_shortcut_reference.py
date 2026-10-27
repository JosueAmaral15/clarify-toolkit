"""Regressions for the effective, modeless F1 shortcut reference."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from unittest.mock import Mock

import pytest
from PySide6 import QtCore
from PySide6.QtCore import QCoreApplication, QEvent, QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QMainWindow, QTabWidget

from src.app import MainWindow
from src.gui import editor_dock as editor_module
from src.gui.menu_builder import MenuBuilder
from src.i18n import get_translator, tr
from src.plugin_loader import PluginLoader
from src.settings_manager import SettingsManager
from src.shortcut_manager import ShortcutManager


def settle(qapp):
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()


@pytest.fixture(autouse=True)
def reset_shortcuts():
    ShortcutManager.reset_all_custom_shortcuts()
    yield
    ShortcutManager.reset_all_custom_shortcuts()


@pytest.fixture
def window(qapp, tmp_path):
    result = MainWindow.__new__(MainWindow)
    QMainWindow.__init__(result)
    result.settings = SettingsManager(str(tmp_path / "settings.json"))
    result.settings.qsettings = QSettings(str(tmp_path / "qt.ini"), QSettings.IniFormat)
    result.translator = get_translator()
    result.translator.switch_language("en")
    result.tabs = QTabWidget(result)
    result.setCentralWidget(result.tabs)
    result.tool_tabs = {}
    result.layout_manager = Mock()
    result.plugin_loader = PluginLoader(result)
    result.plugin_loader.settings = QSettings(str(tmp_path / "plugins.ini"), QSettings.IniFormat)
    result.dock_history = None
    MenuBuilder.build_all_menus(result)
    result.show()
    qapp.processEvents()
    yield result
    result.deleteLater()
    settle(qapp)
    get_translator().switch_language("en")


def _portable(sequence):
    return sequence.toString(QKeySequence.PortableText)


def _reference_item(dialog, action_name):
    for category_index in range(dialog.tree.topLevelItemCount()):
        category = dialog.tree.topLevelItem(category_index)
        for child_index in range(category.childCount()):
            child = category.child(child_index)
            if child.data(0, Qt.ItemDataRole.UserRole) == action_name:
                return child
    raise AssertionError(f"Missing shortcut reference item: {action_name}")


def test_f1_has_one_main_window_route(window):
    assert [_portable(item) for item in window.act_keyboard_shortcuts_help.shortcuts()] == ["F1"]
    assert [shortcut for shortcut in window.findChildren(QShortcut) if _portable(shortcut.key()) == "F1"] == []


def test_help_opens_one_modeless_searchable_reference(window, qapp, monkeypatch):
    monkeypatch.setattr(
        QDialog,
        "exec",
        lambda _dialog: pytest.fail("F1 reference must not enter a modal loop"),
    )

    window._show_keyboard_shortcuts_help()
    qapp.processEvents()

    dialog = window._shortcut_reference_dialog
    assert dialog.isVisible()
    assert not dialog.isModal()
    assert dialog.search_box.hasFocus()
    assert dialog.accessibleName()
    assert dialog.search_box.accessibleName()
    assert dialog.tree.accessibleName()
    assert dialog.customize_button.accessibleName()
    assert dialog.close_button.accessibleName()
    first = dialog
    window._show_keyboard_shortcuts_help()
    assert window._shortcut_reference_dialog is first


def test_reference_uses_only_effective_registered_bindings(window):
    bindings = ShortcutManager.get_registered_shortcuts(window)
    action_names = {binding.action_name for binding in bindings}

    assert "help" in action_names
    assert "open_editor" in action_names
    assert "new_file" not in action_names


def test_actual_f1_opens_once_and_escape_hides_reference(window, qapp):
    QTest.keyClick(window, Qt.Key.Key_F1)
    qapp.processEvents()

    dialog = window._shortcut_reference_dialog
    assert dialog.isVisible()
    assert len(window.findChildren(type(dialog))) == 1

    QTest.keyClick(dialog, Qt.Key.Key_Escape)
    qapp.processEvents()
    assert not dialog.isVisible()


def test_context_dialog_with_own_f1_does_not_open_global_reference(window, qapp):
    contextual = QDialog(window)
    own_help = QAction(contextual)
    own_help.setShortcut(QKeySequence("F1"))
    own_help.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
    contextual.addAction(own_help)
    calls = []
    own_help.triggered.connect(lambda: calls.append("context"))
    contextual.show()
    contextual.activateWindow()
    qapp.processEvents()

    QTest.keyClick(contextual, Qt.Key.Key_F1)
    qapp.processEvents()

    assert calls == ["context"]
    assert not hasattr(window, "_shortcut_reference_dialog")
    contextual.deleteLater()
    settle(qapp)


def test_customization_updates_live_action_reference_and_conflict(window, qapp):
    window._show_keyboard_shortcuts_help()
    dialog = window._shortcut_reference_dialog

    ShortcutManager.load_custom_shortcuts({"help": "Ctrl+Shift+I"})
    qapp.processEvents()

    assert [_portable(item) for item in window.act_keyboard_shortcuts_help.shortcuts()] == ["Ctrl+Shift+I"]
    help_item = _reference_item(dialog, "help")
    about_item = _reference_item(dialog, "about")
    assert help_item.text(1) == "Ctrl+Shift+I"
    assert tr("shortcuts.dialog.conflict_title") in help_item.text(2)
    assert tr("shortcuts.dialog.conflict_title") in about_item.text(2)


def test_search_and_runtime_translation_refresh_without_reopening(window, qapp):
    window._show_keyboard_shortcuts_help()
    dialog = window._shortcut_reference_dialog
    dialog.search_box.setText("F1")
    assert not _reference_item(dialog, "help").isHidden()
    assert _reference_item(dialog, "about").isHidden()

    get_translator().switch_language("pt_BR")
    window._retranslate_ui()
    settle(qapp)
    qapp.processEvents()

    assert dialog.windowTitle() == tr("shortcuts.dialog.help_title")
    assert dialog.search_label.text() == tr("app.lbl_shortcuts_search")
    assert dialog.tree.headerItem().text(0) == tr("shortcuts.dialog.action")
    assert _reference_item(dialog, "help").text(0) == window.act_keyboard_shortcuts_help.text()
    assert tr("shortcuts.category.help") in {
        dialog.tree.topLevelItem(index).text(0) for index in range(dialog.tree.topLevelItemCount())
    }


def test_menu_rebuild_prunes_stale_bindings_and_preserves_custom_help(window, qapp):
    ShortcutManager.load_custom_shortcuts({"help": "Ctrl+Alt+H"})
    MenuBuilder.build_all_menus(window)
    settle(qapp)

    bindings = ShortcutManager.get_registered_shortcuts(window)
    help_bindings = [item for item in bindings if item.action_name == "help"]
    assert len(help_bindings) == 1
    assert help_bindings[0].sequences == ("Ctrl+Alt+H",)
    assert not any(_portable(shortcut.key()) == "F1" for shortcut in window.findChildren(QShortcut))


def test_every_main_menu_shortcut_is_registered(window):
    for action in window.findChildren(QAction):
        if action.shortcuts():
            assert action.property("clarify_shortcut_action"), action.text()


def test_editor_existing_actions_join_effective_registry(window, qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.Format.IniFormat)
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    dock = editor_module.EditorDock(window)
    qtbot.addWidget(dock)

    bindings = ShortcutManager.get_registered_shortcuts(window)
    action_names = {binding.action_name for binding in bindings}
    expected = {
        spec.get("shortcut_action") or f"editor.{action_id}"
        for action_id, spec in dock._ACTION_SPECS.items()
        if dock._action_by_id[action_id].shortcuts()
    }

    assert expected <= action_names
    assert "editor.find" in action_names
    assert any(binding.category == "Editor Edit" for binding in bindings)
