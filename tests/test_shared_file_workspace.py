"""Shared compact/advanced workspace: lightweight app routes and real workers."""

import logging
import os
import threading
from pathlib import Path
import pytest
import shiboken6
from PySide6.QtCore import QCoreApplication, QEvent, QPoint
from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from src.app import MainWindow
from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.ui_builder import UIBuilder
from src.layout_manager import LayoutManager
from src.theme_manager import ThemeManager
from src.i18n.translator import tr
from src.ui import thread_manager, FeatureType
from test_file_explorer_lifecycle import docks, pause_at_first_checkpoint
from test_file_explorer_replace import populate_dock
from test_file_explorer_target_scope import select_paths, set_scope


class MemorySettings:
    def __init__(self):
        self.data = {}

    def get(self, name, default=None):
        return self.data.get(name, default)

    def set(self, name, value):
        self.data[name] = value


class LightWindow(QMainWindow):
    _add_tool_tab = MainWindow._add_tool_tab
    _show_search_replace = MainWindow._show_search_replace
    _show_file_explorer = MainWindow._show_file_explorer
    _show_insert = MainWindow._show_insert
    _save_tab_state = MainWindow._save_tab_state
    _restore_tab_state = MainWindow._restore_tab_state
    _restore_tab_state_impl = MainWindow._restore_tab_state_impl
    _close_tab = MainWindow._close_tab

    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.settings = MemorySettings()
        self.tool_tabs = {}
        self.tab_search = self.tab_insert = self.dock_file_explorer = None
        self.progress_manager = None
        self.layout_manager = LayoutManager(self)
        self.logger = logging.getLogger(__name__)

    def _restore_window_flags(self):
        pass


@pytest.fixture
def workspace_host(qapp, qtbot, monkeypatch):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    monkeypatch.setattr(thread_manager, "_feature_locks", {feature: threading.Lock() for feature in FeatureType})
    for name in ("information", "warning", "critical"):
        monkeypatch.setattr(QMessageBox, name, lambda *a, **kw: QMessageBox.Ok)
    host = LightWindow()
    host.resize(1100, 800)
    yield host
    dock = host.dock_file_explorer
    if dock is not None and shiboken6.isValid(dock) and dock._operation_running():
        dock._request_shutdown()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)


def test_routes_and_close_reopen_use_one_instance_and_tab(workspace_host):
    host = workspace_host
    host._show_search_replace()
    dock = host.dock_file_explorer
    dock.content_panel.set_query("needle")
    for _ in range(3):
        host._show_file_explorer()
        assert dock.get_workspace_mode() == "advanced"
        host._show_search_replace()
        assert dock.get_workspace_mode() == "compact"
    assert host.tab_search is dock and host.tabs.count() == 1
    host._close_tab(0)
    assert host.tabs.count() == 0
    host._show_file_explorer()
    assert host.dock_file_explorer is dock
    assert host.tabs.count() == 1 and dock.content_panel.get_query() == "needle"


def test_ui_builder_creates_only_shared_workspace_and_insert(workspace_host):
    host = workspace_host
    host._restoring_tabs = True
    host.settings.data = {
        "tabs_open_tools": ["file_explorer"],
        "tabs_current_tool": "file_explorer",
        "tabs_fixed_open": {"search_replace": True, "insert": False},
    }
    before = dict(host.settings.data)
    UIBuilder.build_panels(host)
    assert host.tab_search is host.dock_file_explorer
    assert isinstance(host.tab_search, FileExplorerDock)
    assert host.tabs.count() == 2 and host.settings.data == before
    host._restore_tab_state()
    assert host.tabs.count() == 1 and not host._restoring_tabs
    assert host.tabs.currentWidget() is host.dock_file_explorer


def test_legacy_closed_search_and_open_explorer_restore_without_duplication(workspace_host):
    host = workspace_host
    host._restoring_tabs = True
    UIBuilder.build_panels(host)
    host.dock_file_explorer.set_workspace_mode("compact")
    host.settings.data = {
        "tabs_open_tools": ["file_explorer", "search_replace"],
        "tabs_fixed_open": {"search_replace": False, "insert": False},
        "tabs_current_tool": "file_explorer",
        "tabs_current_index": 99,
    }
    before = dict(host.settings.data)
    host._restore_tab_state()
    assert host.tabs.count() == 1 and host.settings.data == before
    assert host.dock_file_explorer.get_workspace_mode() == "compact"
    assert host.tabs.currentWidget() is host.dock_file_explorer


def test_saved_tab_identity_not_index_and_restore_keeps_mode(workspace_host):
    host = workspace_host
    UIBuilder.build_panels(host)
    host.dock_file_explorer.set_workspace_mode("compact")
    host.tabs.tabBar().moveTab(0, 1)
    host.tabs.setCurrentWidget(host.dock_file_explorer)
    host._save_tab_state()
    assert host.settings.get("tabs_fixed_open") == {"search_replace": True, "insert": True}
    assert host.settings.get("tabs_current_tool") == "file_explorer"
    host.tabs.tabBar().moveTab(1, 0)
    host.tabs.setCurrentWidget(host.tab_insert)
    host._restore_tab_state()
    assert host.tabs.currentWidget() is host.dock_file_explorer
    assert host.dock_file_explorer.get_workspace_mode() == "compact"


def test_legacy_fixed_tabs_restore_selection_without_open_tools(workspace_host):
    host = workspace_host
    host._restoring_tabs = True
    UIBuilder.build_panels(host)
    host.settings.data = {
        "tabs_open_tools": [],
        "tabs_current_index": 1,
        "tabs_fixed_open": {"search_replace": True, "insert": True},
    }
    host.tabs.setCurrentWidget(host.dock_file_explorer)
    before = dict(host.settings.data)
    host._restore_tab_state()
    assert host.tabs.currentWidget() is host.tab_insert
    assert host.settings.data == before


def test_hidden_insert_reopens_same_buffer_and_registration(workspace_host):
    host = workspace_host
    UIBuilder.build_panels(host)
    page = host.tab_insert
    page.ed_text.setPlainText("unsaved insert buffer")
    host.tabs.setTabVisible(host.tabs.indexOf(page), False)
    host._show_insert()
    assert host.tabs.isTabVisible(host.tabs.indexOf(page))
    assert host.tabs.currentWidget() is page
    assert host.layout_manager.docks["insert"] is page
    host._close_tab(host.tabs.indexOf(page))
    host._show_insert()
    assert host.tab_insert is page and host.insert_panel is page
    assert page.ed_text.toPlainText() == "unsaved insert buffer"
    assert page.property("clarify_tool_id") == "insert"


def test_tab_tracking_after_layout_reorder_and_close(workspace_host):
    host = workspace_host
    UIBuilder.build_panels(host)
    host._show_insert()
    host.tabs.tabBar().moveTab(host.tabs.indexOf(host.tab_insert), 0)
    host._close_tab(0)
    assert host.tool_tabs["file_explorer"][1] == host.tabs.indexOf(host.dock_file_explorer) == 0


@pytest.mark.parametrize("scope", ["file", "folder", "selected"])
@pytest.mark.parametrize("view", [0, 1])
def test_toggle_preserves_state_selection_results_and_cache(tmp_path, docks, scope, view):
    chosen = tmp_path / "chosen.txt"
    chosen.write_text("needle")
    dock = docks()
    populate_dock(dock, [chosen])
    select_paths(dock, view, [chosen])
    set_scope(dock, scope)
    dock.ed_directory.setText(str(tmp_path if scope == "folder" else chosen))
    dock.content_panel.set_query("needle")
    dock.replace_panel.set_replacement("updated")
    dock.filter_panel.set_filters({"extensions": ["txt"], "depth": 2})
    dock.conditions_grid.set_conditions(
        [{"field": "content", "operator": "contains", "value": "needle", "scope_type": "brackets", "whole_word": True}]
    )
    signature = dock._snapshot_target()[-1]
    cached = {"target_signature": signature}
    dock._last_content_search_universe = cached
    selected = dock._selected_result_paths()
    results = dock.last_search_results
    for mode in ("compact", "advanced", "compact"):
        dock.workspace_mode.buttons[mode].click()
        assert dock.get_workspace_mode() == mode
        assert dock._snapshot_target()[-1] == signature
        assert dock._selected_result_paths() == selected
        assert dock.last_search_results is results
        assert dock._last_content_search_universe is cached
        assert dock.content_panel.get_query() == "needle"
        assert dock.replace_panel.get_replacement() == "updated"
    assert dock.section_filters.isHidden() and dock.section_conditions.isHidden()
    assert "txt" in dock.workspace_mode.summary.text()
    assert tr("file_explorer.filter_conditions").format(1, "AND") in dock.workspace_mode.summary.text()
    assert dock.workspace_mode.mapTo(dock, QPoint()).y() < dock.section_directory.mapTo(dock, QPoint()).y()


@pytest.mark.parametrize("action", ["resume", "cancel", "close", "delete"])
@pytest.mark.parametrize("kind", ["search", "replace"])
def test_toggle_paused_worker_no_extra_operation_or_late_callbacks(tmp_path, docks, qtbot, monkeypatch, action, kind):
    chosen = tmp_path / "chosen.txt"
    sibling = tmp_path / "sibling.md"
    chosen.write_text("needle")
    sibling.write_text("needle")
    dock = docks()
    dock.ed_directory.setText(str(tmp_path))
    dock.ed_exc.clear()
    dock.content_panel.set_query("needle")
    dock.replace_panel.set_replacement("changed")
    dock.filter_panel.set_filters({"extensions": ["txt"]})
    if kind == "replace":
        populate_dock(dock, [chosen])
        select_paths(dock, 1, [chosen])
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.Yes)
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    dock._list_files() if kind == "search" else dock._start_replace(True)
    qtbot.waitUntil(entered.is_set, timeout=3000)
    worker = dock._worker
    generation = dock._operation_generation
    signature = dock._snapshot_target()[-1]
    dock.workspace_mode.buttons["compact"].click()
    assert dock._worker is worker and dock._operation_generation == generation
    assert dock._snapshot_target()[-1] == signature
    assert "txt" in dock.workspace_mode.summary.text()
    if action == "resume":
        dock.executor.resume()
    elif action == "cancel":
        dock._on_progress_canceled()
    elif action == "close":
        dock.close()
    else:
        dock.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)
    if action == "resume":
        if kind == "search":
            assert set(dock.last_search_results) == {str(chosen)}
        else:
            assert chosen.read_text() == "changed"
        assert dock.get_workspace_mode() == "compact"
    else:
        assert chosen.read_text() == "needle"
    assert sibling.read_text() == "needle"


def test_summary_plain_bounded_updated_by_preset_clear_and_language(docks):
    dock = docks()
    dock.set_workspace_mode("compact")
    dock.filter_panel.set_filters({"extensions_text": "<b>txt</b>" * 2500, "use_ext_filter": True})
    assert len(dock.workspace_mode.summary.text()) <= 1024
    assert "<b>" in dock.workspace_mode.summary.text()
    dock._apply_filters_to_widgets({"extensions": ["md"]})
    assert "md" in dock.workspace_mode.summary.text()
    dock.filter_panel.clear_filters()
    assert "md" not in dock.workspace_mode.summary.text()
    dock.retranslateUi()
    assert dock.workspace_mode.buttons["compact"].text() == tr("file_explorer.mode_compact")


def test_invalid_mode_does_not_change_state_or_preferences(docks):
    dock = docks()
    dock.set_workspace_mode("compact")
    with pytest.raises(ValueError):
        dock.set_workspace_mode("wrong")
    assert dock.get_workspace_mode() == "compact"
    assert dock.settings.value("workspace_mode") == "compact"


@pytest.mark.parametrize("mode", ["compact", "advanced"])
@pytest.mark.parametrize("width", [900, 1200])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_visible_workspace_geometry_and_optional_screenshot(workspace_host, qtbot, qapp, mode, width, theme):
    ThemeManager.apply_theme(qapp, theme)
    host = workspace_host
    host._show_file_explorer()
    dock = host.dock_file_explorer
    dock.set_workspace_mode(mode)
    dock.content_panel.set_query("needle")
    dock.filter_panel.set_filters({"extensions": ["txt"]})
    host.resize(width, 800)
    host.show()
    qtbot.wait(30)
    assert host.width() == width
    for button in dock.workspace_mode.buttons.values():
        assert button.geometry().right() < dock.workspace_mode.width()
        assert button.geometry().height() >= 32
        assert host.rect().contains(button.mapTo(host, QPoint()))
        assert host.rect().contains(button.mapTo(host, button.rect().bottomRight()))
        assert button.visibleRegion().boundingRect() == button.rect()
    selector_bottom = dock.workspace_mode.mapTo(dock, dock.workspace_mode.rect().bottomLeft()).y()
    assert selector_bottom < dock.section_directory.mapTo(dock, QPoint()).y()
    dock._controls_scroll.horizontalScrollBar().setValue(dock._controls_scroll.horizontalScrollBar().maximum())
    assert all(
        button.visibleRegion().boundingRect() == button.rect() for button in dock.workspace_mode.buttons.values()
    )
    dock._controls_scroll.horizontalScrollBar().setValue(0)
    assert dock.workspace_mode.buttons[mode].isChecked()
    assert not dock.workspace_mode.buttons["advanced" if mode == "compact" else "compact"].isChecked()
    directory = os.environ.get("CLARIFY_WORKSPACE_SCREENSHOTS")
    if directory:
        Path(directory).mkdir(parents=True, exist_ok=True)
        assert host.grab().save(str(Path(directory) / f"{mode}-{width}-{theme}.png"))
    ThemeManager.apply_theme(qapp, "system")
