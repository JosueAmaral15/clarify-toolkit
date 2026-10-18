"""Regressions for QDockWidget tools embedded in the main tab workspace."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QMainWindow, QTabWidget, QWidget

from src.app import MainWindow


class _ToolTabHost(QMainWindow):
    """Minimal host for MainWindow's real tab add/close contracts."""

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


class _CloseAwareDock(QDockWidget):
    """Expose whether the main tab close path consulted the tool."""

    def __init__(self, parent=None):
        super().__init__("Close aware", parent)
        self.allow_close = False
        self.close_requests = 0

    def request_tab_close(self):
        self.close_requests += 1
        return self.allow_close


def _add_tool(host, widget, tool_id="editor"):
    return MainWindow._add_tool_tab(host, widget, "Clarify Editor", tool_id)


def test_embedded_qdock_has_no_native_float_or_close_chrome(qtbot):
    """A tab page must not display unusable QDockWidget window controls."""
    host = _ToolTabHost()
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)

    _add_tool(host, dock)

    assert dock.features() == QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
    assert dock.titleBarWidget() is not None
    assert dock.titleBarWidget().objectName() == "clarify_embedded_tool_title_bar"
    assert dock.titleBarWidget().maximumHeight() == 0
    assert host.dockWidgetArea(dock) == Qt.DockWidgetArea.NoDockWidgetArea


def test_embedding_is_idempotent_and_preserves_main_window_controls(qtbot):
    """Reopening a tool reuses one hidden title bar and leaves the host flags alone."""
    host = _ToolTabHost()
    host.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.WindowMinimizeButtonHint
        | Qt.WindowType.WindowMaximizeButtonHint
        | Qt.WindowType.WindowCloseButtonHint
    )
    dock = QDockWidget("Clarify Editor", host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)
    before_flags = host.windowFlags()

    first_index = _add_tool(host, dock)
    title_bar = dock.titleBarWidget()
    second_index = _add_tool(host, dock)

    assert first_index == second_index == 0
    assert dock.titleBarWidget() is title_bar
    assert host.windowFlags() == before_flags
    assert host.tabs.count() == 1


def test_plain_widget_tool_is_not_given_dock_chrome(qtbot):
    """Non-dock pages such as Insert remain ordinary tab widgets."""
    host = _ToolTabHost()
    page = QWidget(host)
    qtbot.addWidget(host)

    _add_tool(host, page, "insert")

    assert host.tabs.indexOf(page) == 0
    assert not hasattr(page, "titleBarWidget")


def test_tool_close_still_uses_main_tab_contract(qtbot):
    """Removing the chrome cannot bypass request_tab_close and recovery hooks."""
    host = _ToolTabHost()
    dock = _CloseAwareDock(host)
    dock.setWidget(QWidget())
    qtbot.addWidget(host)
    _add_tool(host, dock)

    MainWindow._close_tab(host, 0)
    assert dock.close_requests == 1
    assert host.tabs.indexOf(dock) == 0

    dock.allow_close = True
    MainWindow._close_tab(host, 0)
    assert dock.close_requests == 2
    assert host.tabs.indexOf(dock) == -1
