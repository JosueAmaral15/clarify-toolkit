"""Actual menu paths, with no MainWindow startup or installed plugin execution."""

import gc
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QSettings
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import QMainWindow, QMenu, QTabWidget, QWidget
from shiboken6 import isValid

from src.app import MainWindow
from src.gui.history_dock import HistoryDock
from src.gui.menu_builder import MenuBuilder
from src.gui.plugin_manager_dialog import PluginManagerDialog
from src.gui.tab_manager import TabManager
from src.i18n import get_translator, tr
from src.plugin_loader import PluginLoader, PluginMetadata
from src.plugins.plugin_base import PluginBase
from src.settings_manager import SettingsManager


def settle(qapp):
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()


@pytest.fixture
def window(qapp, tmp_path):
    # Exercise real MainWindow methods without constructor services/tool startup.
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
    yield result
    result.deleteLater()
    settle(qapp)
    get_translator().switch_language("en")


def add_plugin(window, tmp_path, enabled=False):
    metadata = PluginMetadata({"id": "fake", "name": "Fake", "enabled": enabled}, tmp_path)
    window.plugin_loader.metadata[metadata.id] = metadata
    plugin = Mock()
    window.plugin_loader.plugins[metadata.id] = plugin
    return metadata, plugin


@pytest.mark.parametrize("initial_none", [True, False])
def test_history_lazy_none_or_missing_has_visible_content(window, initial_none):
    if not initial_none:
        del window.dock_history
    window._toggle_history(False)
    assert getattr(window, "dock_history", None) is None
    window._toggle_history(True)
    dock = window.dock_history
    assert isinstance(dock, HistoryDock)
    assert dock.main_widget.layout().indexOf(dock.tree_history) >= 0
    assert not dock.isHidden()
    window._toggle_history(False)
    assert dock.isHidden()
    window._toggle_history(True)
    assert window.dock_history is dock


def test_history_retranslation_preserves_entries_and_selection(window):
    window._toggle_history(True)
    dock = window.dock_history
    dock.add_operation("Search", {"query": "unchanged", "files_processed": 2})
    item = dock.tree_history.topLevelItem(0)
    dock.tree_history.setCurrentItem(item)
    history = dock.get_history()
    get_translator().switch_language("pt_BR")
    assert dock.get_history() == history
    assert dock.tree_history.currentItem() is item
    assert dock.tree_history.headerItem().text(0) == tr("history_dock.header_time")
    assert dock.windowTitle() == tr("history_dialog.title")
    assert dock.tree_history.currentItem().text(2).startswith(f"{tr('history_dock.detail_query')}:")


def test_history_layout_remains_qt_owned_through_gc_and_repeated_deletion(window, qapp):
    for _ in range(20):
        dock = HistoryDock(window)
        assert dock.layout.parent() == dock.main_widget
        assert dock.main_widget.layout() == dock.layout
        assert dock.layout.itemAt(2).layout().parent() == dock.layout
        dock.add_operation("Search", {"query": "synthetic", "files_processed": 1})
        gc.collect()
        qapp.processEvents()
        assert dock.tree_history.topLevelItemCount() == 1
        dock.deleteLater()
        settle(qapp)
        assert not isValid(dock)
        del dock
        gc.collect()
    assert not window.findChildren(HistoryDock)


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("fails", [False, True])
def test_plugin_menu_toggle_and_failure_rollback(window, tmp_path, mock_message_box, enabled, fails):
    metadata, plugin = add_plugin(window, tmp_path, enabled)
    if fails:
        (plugin.deactivate if enabled else plugin.activate).side_effect = RuntimeError("fake failure")
    MenuBuilder._build_plugins_menu(window, window.menuBar())
    window.plugin_actions["fake"].trigger()
    expected = enabled if fails else not enabled
    assert metadata.enabled is expected
    assert window.plugin_actions["fake"].isChecked() is expected
    assert window.plugin_loader.settings.value("plugins/fake/enabled", type=bool) is expected
    assert bool(mock_message_box) is fails


@pytest.mark.parametrize("fails", [False, True])
def test_plugin_dialog_checkbox_bool_syncs_menu(window, tmp_path, mock_message_box, fails):
    metadata, plugin = add_plugin(window, tmp_path)
    if fails:
        plugin.activate.side_effect = RuntimeError("fake failure")
    MenuBuilder._build_plugins_menu(window, window.menuBar())
    dialog = PluginManagerDialog(window.plugin_loader, window)
    checkbox = dialog.table.cellWidget(0, 0)
    checkbox.setChecked(True)
    assert metadata.enabled is (not fails)
    assert checkbox.isChecked() is (not fails)
    assert window.plugin_actions["fake"].isChecked() is (not fails)
    get_translator().switch_language("pt_BR")
    assert dialog.table.horizontalHeaderItem(0).text() == tr("plugin_manager.header_enabled")
    assert dialog.lbl_info.text() == tr("plugin_manager.counts").format(1, int(not fails))
    assert bool(mock_message_box) is fails


def test_missing_plugin_and_idempotent_transition(window, tmp_path):
    assert window.plugin_loader.set_plugin_enabled("missing", True) is False
    metadata, plugin = add_plugin(window, tmp_path)
    assert window.plugin_loader.set_plugin_enabled("fake", False)
    plugin.deactivate.assert_not_called()
    assert not metadata.enabled


def test_repeated_menu_translation_is_bounded_preserves_state_and_foreign_objects(window, qapp):
    foreign = QAction("foreign", window)
    MenuBuilder.build_all_menus(window)
    settle(qapp)
    baseline = (len(window.findChildren(QAction)), len(window.findChildren(QShortcut)))
    window.act_undo.setEnabled(True)
    window.act_theme_system.setChecked(False)
    window.act_theme_dark.setChecked(True)
    for language in ["pt_BR", "es", "fr", "de", "zh", "ja", "en"] * 2:
        get_translator().switch_language(language)
        window._retranslate_ui()
        settle(qapp)
        assert (len(window.findChildren(QAction)), len(window.findChildren(QShortcut))) == baseline
        assert window.act_undo.isEnabled()
        assert window.act_theme_dark.isChecked()
        assert not window.act_theme_system.isChecked()
        assert window.act_new_from_template.text() == tr("menu.file.new_template")
        assert window.act_ai_assistant.text() == tr("tutorial_assistant.window_title")
        assert isValid(foreign) and foreign.isEnabled()


def test_language_changes_translate_tabs_without_changing_visibility_identity(window):
    for tool_id in ("translate", "file_explorer", "insert", "editor"):
        widget = QWidget()
        widget.setProperty("clarify_tool_id", tool_id)
        window.tabs.addTab(widget, "old")
    window.tabs.setCurrentIndex(1)
    window.tabs.setTabVisible(2, False)
    get_translator().switch_language("pt_BR")
    window._retranslate_ui()
    assert window.tabs.currentIndex() == 1
    assert not window.tabs.isTabVisible(2)
    assert window.tabs.tabText(0) == tr("menu.tools.json_translate")
    assert window.tabs.tabText(1) == tr("menu.tools.file_explorer")
    assert window.tabs.tabText(2) == tr("ui_builder.tab_insert")
    assert window.tabs.tabText(3) == "old"
    assert TabManager.translated_title("unknown") is None


def test_plugin_entries_and_submenus_survive_language_menu_cleanup(window, qapp):
    MenuBuilder.build_all_menus(window)
    file_menu = window.menuBar().findChild(QMenu, "m_file")
    separator = file_menu.addSeparator()
    callback = Mock()
    action = QAction("Plugin export", window)
    action.triggered.connect(callback)
    file_menu.addAction(action)
    submenu = file_menu.addMenu("Plugin tools")
    child_action = submenu.addAction("Child")
    plugin_root = window.menuBar().addMenu("Plugin root")
    root_action = plugin_root.addAction("Root")
    for language in ("pt_BR", "en", "fr"):
        assert [item.text() for item in window.menuBar().actions()
                if item not in window._menu_bar_baseline] == ["Plugin root"]
        get_translator().switch_language(language)
        window._retranslate_ui()
        settle(qapp)
        file_menu = window.menuBar().findChild(QMenu, "m_file")
        assert separator in file_menu.actions()
        assert action in file_menu.actions()
        assert submenu.parent() == file_menu
        assert child_action in submenu.actions()
        assert plugin_root.menuAction() in window.menuBar().actions()
        assert isValid(root_action)
    action.trigger()
    callback.assert_called_once()


def test_language_action_can_replace_its_own_menu_safely(window, qapp):
    MenuBuilder.build_all_menus(window)
    window.translator.languageChanged.connect(window._on_language_changed)
    action = window.act_lang_pt
    try:
        action.trigger()
        settle(qapp)
        assert not isValid(action)
        assert window.act_lang_pt.isChecked()
        assert window.act_ai_assistant.text() == tr("tutorial_assistant.window_title")
        assert len(window.findChildren(QShortcut)) == 2
    finally:
        window.translator.languageChanged.disconnect(window._on_language_changed)


def test_plugin_api_reuses_localized_tools_root(window, qapp):
    MenuBuilder.build_all_menus(window)
    get_translator().switch_language("pt_BR")
    window._retranslate_ui()
    plugin = PluginBase()
    callback = Mock()
    action = plugin.add_menu_item(window, "Tools/My Plugin", "Run", callback)
    roots = [
        menu
        for menu in window.menuBar().findChildren(QMenu)
        if menu.parent() == window.menuBar() and menu.menuAction() in window.menuBar().actions()
    ]
    assert len([menu for menu in roots if menu.property("clarify_menu_key") == "menu.tools"]) == 1
    assert not any(menu.title() == "Tools" for menu in roots)
    get_translator().switch_language("en")
    window._retranslate_ui()
    settle(qapp)
    assert isValid(action)
    action.trigger()
    callback.assert_called_once()


def test_shortcut_tooltips_follow_portuguese_and_do_not_repeat_suffix(window, qapp):
    MenuBuilder.build_all_menus(window)
    get_translator().switch_language("pt_BR")
    window._retranslate_ui()
    window._apply_shortcuts_to_menu()
    window._apply_shortcuts_to_menu()
    settle(qapp)
    assert window.act_undo.toolTip().startswith(tr("shortcuts.desc.undo"))
    assert window.act_undo.toolTip().count("(") <= 1
    assert window.act_open_editor.toolTip().startswith(tr("menu.tooltip_open_editor"))
