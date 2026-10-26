"""Regressions for explicit tool detach and predictable reattachment."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QLineEdit,
    QMainWindow,
    QTabWidget,
    QWidget,
)

from src.app import MainWindow
from src.gui import tool_window_manager as tool_windows


class _ToolToggleHost(QMainWindow):
    """Minimal host for the real MainWindow tool-tab contract."""

    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.tool_tabs = {}
        self.layout_manager = None
        self.saved_states = 0
        self.restored_flags = 0

    def _save_tab_state(self):
        self.saved_states += 1

    def _restore_window_flags(self):
        self.restored_flags += 1

    def _close_tab(self, index):
        return MainWindow._close_tab(self, index)


class _CloseAwareDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Close aware", parent)
        self.setWidget(QWidget())
        self.allow_close = False
        self.close_requests = 0

    def request_tab_close(self):
        self.close_requests += 1
        return self.allow_close


class _MemorySettings:
    def __init__(self):
        self.values = {}

    def set(self, key, value):
        self.values[key] = value


class _StateHost(_ToolToggleHost):
    def __init__(self):
        super().__init__()
        self.settings = _MemorySettings()
        self.tab_search = None
        self.tab_insert = None
        self._restoring_tabs = False

    def _save_tab_state(self):
        return MainWindow._save_tab_state(self)


def _add_tool(host, widget, tool_id="editor", title="Clarify Editor"):
    return MainWindow._add_tool_tab(host, widget, title, tool_id)


def test_current_tool_exposes_one_accessible_detach_control(qtbot):
    """Adding a tool must expose the missing dock/undock control."""
    host = _ToolToggleHost()
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)

    _add_tool(host, dock)

    control = host.tabs.cornerWidget(Qt.Corner.TopRightCorner)
    assert control is not None
    assert control.objectName() == "clarify_tool_dock_toggle"
    assert control.accessibleName()
    assert control.toolTip()
    assert control.isEnabled()


def test_toggle_moves_same_tool_instance_and_redocks_explicitly(qtbot):
    host = _ToolToggleHost()
    dock = QDockWidget("Clarify Editor", host)
    editor = QLineEdit(dock)
    dock.setWidget(editor)
    qtbot.addWidget(host)
    host.show()
    _add_tool(host, dock)
    host.activateWindow()
    editor.setFocus()
    qtbot.waitUntil(editor.hasFocus)

    host.tool_window_manager.toggle_button.click()
    qtbot.waitUntil(lambda: host.tool_window_manager.is_detached(dock))
    record = host.tool_window_manager._detached[dock]

    assert host.tabs.indexOf(dock) == -1
    assert record.window.centralWidget() is dock
    assert dock.widget() is editor
    assert record.window.toggle_button.accessibleName()
    assert len(record.window.menuWidget().findChildren(type(record.window.toggle_button))) == 1

    record.window.toggle_button.click()
    qtbot.waitUntil(lambda: host.tabs.indexOf(dock) >= 0)

    assert host.tabs.currentWidget() is dock
    assert dock.widget() is editor
    assert not host.tool_window_manager.is_detached(dock)
    assert editor.hasFocus()


def test_redock_restores_stable_tab_order_and_saved_geometry(qtbot):
    host = _ToolToggleHost()
    first = QDockWidget("First", host)
    second = QDockWidget("Second", host)
    first.setWidget(QWidget())
    second.setWidget(QWidget())
    qtbot.addWidget(host)
    host.show()
    _add_tool(host, first, "first", "First")
    _add_tool(host, second, "second", "Second")

    host.tabs.setCurrentWidget(first)
    assert host.tool_window_manager.detach_current_tool()
    record = host.tool_window_manager._detached[first]
    record.window.setGeometry(41, 53, 720, 510)
    expected = record.window.saveGeometry()
    assert host.tool_window_manager.attach_tool(first)

    assert [host.tabs.widget(i) for i in range(host.tabs.count())] == [first, second]
    assert host.tool_window_manager.detach_tool(first)
    restored = host.tool_window_manager._detached[first].window.saveGeometry()
    assert restored == expected


def test_opening_an_already_detached_tool_raises_it_without_duplication(qtbot):
    host = _ToolToggleHost()
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)
    _add_tool(host, dock)
    assert host.tool_window_manager.detach_tool(dock)

    result = _add_tool(host, dock)

    assert result == -1
    assert host.tabs.indexOf(dock) == -1
    assert host.tool_window_manager.is_detached(dock)
    assert len(host.tool_window_manager._detached) == 1


def test_detached_close_reuses_tab_close_veto_and_success(qtbot):
    host = _ToolToggleHost()
    dock = _CloseAwareDock(host)
    qtbot.addWidget(host)
    _add_tool(host, dock)
    assert host.tool_window_manager.detach_tool(dock)
    detached = host.tool_window_manager._detached[dock].window

    detached.close()
    QApplication.processEvents()
    assert dock.close_requests == 1
    assert host.tabs.indexOf(dock) >= 0
    assert not host.tool_window_manager.is_detached(dock)

    dock.allow_close = True
    assert host.tool_window_manager.detach_tool(dock)
    host.tool_window_manager._detached[dock].window.close()
    QApplication.processEvents()
    assert dock.close_requests == 2
    assert host.tabs.indexOf(dock) == -1
    assert dock not in host.tool_window_manager.ordered_open_widgets()


def test_shutdown_reattaches_without_closing_or_recreating_tools(qtbot):
    host = _ToolToggleHost()
    first = QDockWidget("First", host)
    second = QWidget(host)
    first.setWidget(QWidget())
    qtbot.addWidget(host)
    _add_tool(host, first, "first", "First")
    _add_tool(host, second, "insert", "Insert")
    assert host.tool_window_manager.detach_tool(first)
    assert host.tool_window_manager.detach_tool(second)

    host.tool_window_manager.reattach_all(activate=False)

    assert [host.tabs.widget(i) for i in range(host.tabs.count())] == [first, second]
    assert not host.tool_window_manager._detached


def test_controls_retranslate_without_changing_tool_identity(qtbot, monkeypatch):
    host = _ToolToggleHost()
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)
    _add_tool(host, dock)
    assert host.tool_window_manager.detach_tool(dock)
    record = host.tool_window_manager._detached[dock]
    monkeypatch.setattr(tool_windows, "tr", lambda key, default=None: f"translated:{key}")

    host.tool_window_manager.retranslate_ui()

    assert host.tool_window_manager.toggle_button.accessibleName() == "translated:tool_window.detach"
    assert record.window.toggle_button.accessibleName() == "translated:tool_window.attach"
    assert "translated:tool_window.detached" in record.window.windowTitle()
    assert record.window.centralWidget() is dock


def test_detach_is_rejected_before_widget_access_off_gui_thread(qtbot):
    host = _ToolToggleHost()
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)
    _add_tool(host, dock)
    errors = []

    class Caller(QThread):
        def run(self):
            try:
                host.tool_window_manager.detach_tool(dock)
            except RuntimeError as error:
                errors.append(str(error))

    caller = Caller()
    caller.start()
    assert caller.wait(2000)

    assert errors == ["Tool windows may only be changed on the GUI thread"]
    assert host.tabs.indexOf(dock) >= 0


def test_control_disables_when_workspace_has_no_current_tool(qtbot):
    host = _ToolToggleHost()
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)
    _add_tool(host, dock)

    MainWindow._close_tab(host, 0)

    assert host.tabs.count() == 0
    assert not host.tool_window_manager.toggle_button.isEnabled()
    assert host.tool_window_manager.toggle_button.toolTip()

    _add_tool(host, dock)
    assert host.tool_window_manager.toggle_button.isEnabled()
    assert host.tool_window_manager.toggle_button.toolTip() == tool_windows.tr(
        "tool_window.detach_tooltip", "Open the current tool in a separate window"
    )


def test_detached_fixed_tools_remain_open_in_session_state(qtbot):
    host = _StateHost()
    explorer = QDockWidget("File Explorer", host)
    insert = QWidget(host)
    explorer.setWidget(QWidget())
    host.tab_search = explorer
    host.tab_insert = insert
    qtbot.addWidget(host)
    _add_tool(host, explorer, "file_explorer", "File Explorer")
    _add_tool(host, insert, "insert", "Insert")

    assert host.tool_window_manager.detach_tool(explorer)
    assert host.tool_window_manager.detach_tool(insert)
    MainWindow._save_tab_state(host)

    assert host.settings.values["tabs_open_tools"] == ["file_explorer"]
    assert host.settings.values["tabs_fixed_open"] == {
        "search_replace": True,
        "insert": True,
    }
