"""Real tab layouts and app registration without full MainWindow startup."""

import json
import logging
import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QDockWidget, QLineEdit
from src.app import MainWindow
from src.gui.dock_factory import DockFactory
from src.layout_manager import LayoutManager


class ModePage(QWidget):
    def __init__(self):
        super().__init__()
        self.mode = "advanced"
        self.buffer = QLineEdit(self)
        self.buffer.setText("unsaved test buffer")

    def get_workspace_mode(self):
        return self.mode

    def set_workspace_mode(self, mode):
        self.mode = mode


@pytest.fixture
def tab_window(qapp, qtbot, tmp_path):
    window = QMainWindow()
    window.tabs = QTabWidget()
    window.setCentralWidget(window.tabs)
    window.layout_manager = LayoutManager(window)
    window.layout_manager.settings = QSettings(str(tmp_path / "layouts.ini"), QSettings.IniFormat)
    window.tool_tabs = {}
    window.logger = logging.getLogger(__name__)
    for name in ("editor", "file_explorer", "rewriter", "insert"):
        page = ModePage()
        window.layout_manager.register_dock(name, page)
        window.tabs.addTab(page, name)
        setattr(window, "dock_" + name, page)
    window.insert_panel = window.dock_insert
    window.tab_search = window.dock_file_explorer
    window.resize(900, 650)
    window.show()
    qtbot.addWidget(window)
    return window


def visible(window):
    return {
        window.tabs.widget(index).property("clarify_tool_id")
        for index in range(window.tabs.count())
        if window.tabs.isTabVisible(index)
    }


@pytest.mark.parametrize(
    "preset,expected",
    [
        ("Compact", {"editor"}),
        ("Standard", {"editor", "file_explorer", "rewriter"}),
        ("Advanced", {"editor", "file_explorer", "rewriter", "insert"}),
    ],
)
def test_presets_control_tabs_not_widgets_or_buffers(tab_window, preset, expected):
    window = tab_window
    before = [window.tabs.widget(i) for i in range(window.tabs.count())]
    assert window.layout_manager.apply_preset(preset)
    assert visible(window) == expected
    assert window.tabs.isTabVisible(window.tabs.currentIndex())
    assert [window.tabs.widget(i) for i in range(window.tabs.count())] == before
    assert all(page.buffer.text() == "unsaved test buffer" for page in before)
    assert window.layout_manager.settings.value("LastLayout") == preset


def test_compact_opens_only_editor_when_explicitly_missing(tab_window):
    window = tab_window
    window.tabs.removeTab(0)
    calls = []

    def show_editor():
        calls.append("editor")
        window.tabs.addTab(window.dock_editor, "editor")

    window._show_editor = show_editor
    window.layout_manager.apply_preset_compact()
    assert calls == ["editor"] and visible(window) == {"editor"}


def test_saved_compact_does_not_reopen_closed_tools_or_leave_blank(tab_window):
    window = tab_window
    window.layout_manager.apply_preset_compact()
    window.tabs.removeTab(window.tabs.indexOf(window.dock_editor))
    window._show_editor = lambda: pytest.fail("automatic startup tool creation")
    assert window.layout_manager.restore_last_layout()
    assert window.tabs.isTabVisible(window.tabs.currentIndex())
    assert window.tabs.count() == 3


def test_custom_layout_restores_order_visibility_active_and_mode(tab_window):
    window = tab_window
    manager = window.layout_manager
    window.dock_file_explorer.set_workspace_mode("compact")
    window.tabs.tabBar().moveTab(2, 0)
    window.tabs.setTabVisible(window.tabs.indexOf(window.insert_panel), False)
    window.tabs.setCurrentWidget(window.dock_file_explorer)
    manager.save_layout("custom")
    saved_order = [window.tabs.widget(i) for i in range(window.tabs.count())]
    window.dock_file_explorer.set_workspace_mode("advanced")
    window.tabs.tabBar().moveTab(0, 3)
    manager.apply_preset_advanced()
    window.tabs.setCurrentWidget(window.insert_panel)
    assert manager.load_layout("custom")
    assert [window.tabs.widget(i) for i in range(window.tabs.count())] == saved_order
    assert visible(window) == {"editor", "file_explorer", "rewriter"}
    assert window.tabs.currentWidget() is window.dock_file_explorer
    assert window.dock_file_explorer.get_workspace_mode() == "compact"


def test_logical_visibility_saved_even_when_window_hidden(tab_window):
    window = tab_window
    window.layout_manager.apply_preset_standard()
    window.hide()
    window.layout_manager.save_layout("hidden-window")
    window.show()
    window.layout_manager.apply_preset_advanced()
    assert window.layout_manager.load_layout("hidden-window")
    assert visible(window) == {"editor", "file_explorer", "rewriter"}


def test_load_does_not_show_removed_pages_as_floating_widgets(tab_window):
    window = tab_window
    window.layout_manager.save_layout("before-close")
    page = window.dock_rewriter
    window.tabs.removeTab(window.tabs.indexOf(page))
    assert page.isHidden()
    assert window.layout_manager.load_layout("before-close")
    assert page.isHidden() and window.tabs.indexOf(page) == -1
    assert window.tabs.count() == 3


def test_newly_opened_tab_not_hidden_by_old_snapshot(tab_window):
    window = tab_window
    window.layout_manager.save_layout("before-new")
    page = QWidget()
    window.layout_manager.register_dock("clock", page)
    window.tabs.addTab(page, "clock")
    assert window.layout_manager.load_layout("before-new")
    assert window.tabs.isTabVisible(window.tabs.indexOf(page))


def test_legacy_search_visibility_maps_to_shared_workspace(tab_window):
    window = tab_window
    manager = window.layout_manager
    manager.save_layout("legacy")
    manager.settings.remove("Layouts/legacy/tabs")
    manager.settings.remove("Layouts/legacy/dock_file_explorer_visible")
    manager.settings.setValue("Layouts/legacy/dock_search_visible", False)
    assert manager.load_layout("legacy")
    assert "file_explorer" not in visible(window)
    assert "editor" in visible(window)


@pytest.mark.parametrize(
    "raw",
    [
        "{",
        "{}",
        json.dumps([{"id": "x", "visible": "false"}]),
        json.dumps([{"id": "x", "visible": True, "mode": "wrong"}]),
        json.dumps([{"id": "x", "visible": True}] * 2),
        json.dumps([{"id": str(i), "visible": True} for i in range(129)]),
        "x" * 65537,
        json.dumps([{"id": str(i) + "\u00e9" * 300, "visible": True} for i in range(110)], ensure_ascii=False),
    ],
)
def test_corrupt_tab_records_rejected_before_ui_changes(tab_window, raw):
    window = tab_window
    manager = window.layout_manager
    manager.save_layout("corrupt")
    manager.settings.setValue("Layouts/corrupt/tabs", raw)
    window.tabs.setCurrentWidget(window.insert_panel)
    before = visible(window)
    assert not manager.load_layout("corrupt")
    assert visible(window) == before and window.tabs.currentWidget() is window.insert_panel
    assert manager.settings.group() == ""


def test_actual_attribute_registration_includes_editor_and_explorer(tab_window):
    window = tab_window
    window.layout_manager.docks.clear()
    MainWindow._register_docks_with_layout_manager(window)
    assert window.layout_manager.docks["editor"] is window.dock_editor
    assert window.layout_manager.docks["file_explorer"] is window.dock_file_explorer
    assert window.layout_manager.docks["rewriter"] is window.dock_rewriter
    assert "search" not in window.layout_manager.docks


@pytest.mark.parametrize("active", [["editor"], "x" * 513])
def test_corrupt_active_tab_rejected_without_changing_selection(tab_window, active):
    manager = tab_window.layout_manager
    manager.save_layout("active-corrupt")
    manager.settings.setValue("Layouts/active-corrupt/active_tab", active)
    tab_window.tabs.setCurrentWidget(tab_window.insert_panel)
    assert not manager.load_layout("active-corrupt")
    assert tab_window.tabs.currentWidget() is tab_window.insert_panel
    assert manager.settings.group() == ""


def test_initialization_does_not_reveal_layout_hidden_tabs(tab_window):
    window = tab_window
    window.layout_manager.apply_preset_standard()
    before = visible(window)
    window.tabs.setCurrentWidget(window.dock_file_explorer)
    MainWindow._initialize_all_tabs(window)
    assert visible(window) == before
    assert window.tabs.currentWidget() is window.dock_file_explorer


def test_factory_registers_lazy_actual_docks(tab_window):
    dock = DockFactory.create_dock(tab_window, QDockWidget, "dock_clock")
    assert tab_window.layout_manager.docks["clock"] is dock
    assert dock.objectName() == "dock_clock"


def test_convenience_factory_static_call_retains_registration(tab_window, monkeypatch):
    from src import gui

    monkeypatch.setattr(gui, "PlaceholderReplacerDock", QDockWidget)
    dock = DockFactory().create_placeholder_replacer_dock(tab_window)
    assert tab_window.layout_manager.docks["placeholder_replacer"] is dock
    assert tab_window.dock_placeholder_replacer is dock


def test_sync_discovers_new_tab_by_stable_id(tab_window):
    page = QWidget()
    page.setProperty("clarify_tool_id", "plugin-demo")
    tab_window.tabs.addTab(page, "Translated name")
    tab_window.layout_manager.apply_preset_advanced()
    assert tab_window.layout_manager.docks["plugin-demo"] is page
    assert "plugin-demo" in visible(tab_window)
