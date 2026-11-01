"""Explicit detach/reattach lifecycle for tools in the main tab workspace."""

# pylint: disable=no-name-in-module  # PySide6 and Shiboken expose dynamic symbols.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from shiboken6 import isValid as is_valid
from PySide6.QtCore import QByteArray, QObject, Qt, QThread
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStyle,
    QToolButton,
    QWidget,
)

from ..i18n import tr


@dataclass
class _DetachedTool:
    widget: QWidget
    tool_id: str
    title: str
    focus_widget: Optional[QWidget]
    window: "DetachedToolWindow"


class DetachedToolWindow(QMainWindow):
    """A top-level host with one explicit action for returning its tool."""

    def __init__(self, manager: "ToolWindowManager", widget: QWidget, title: str):
        super().__init__(manager.main_window, Qt.WindowType.Window)
        self._manager = manager
        self._tool_widget = widget
        self._allow_close = False
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setObjectName("clarify_detached_tool_window")
        self.setWindowOpacity(manager.main_window.windowOpacity())

        header = QFrame(self)
        header.setObjectName("clarify_detached_tool_header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(6, 2, 4, 2)
        self.title_label = QLabel(title, header)
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.toggle_button = QToolButton(header)
        self.toggle_button.setObjectName("clarify_tool_dock_toggle")
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.clicked.connect(lambda: manager.attach_tool(widget))
        layout.addWidget(self.toggle_button)
        self.setMenuWidget(header)
        self.setCentralWidget(widget)
        self.retranslate_ui(title)

    def retranslate_ui(self, title: str) -> None:
        """Refresh the host and its single command after a language change."""
        self.title_label.setText(title)
        self.setWindowTitle(f"{title} - {tr('tool_window.detached', 'Detached')}")
        label = tr("tool_window.attach", "Reattach tool")
        self.toggle_button.setAccessibleName(label)
        self.toggle_button.setToolTip(tr("tool_window.attach_tooltip", "Return this tool to the main workspace"))
        self.toggle_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton))

    def closeEvent(self, event):  # pylint: disable=invalid-name
        if self._allow_close:
            super().closeEvent(event)
            return
        event.ignore()
        self._manager.close_detached_tool(self._tool_widget)

    def release_tool(self) -> QWidget:
        """Release the tool without invoking its close lifecycle."""
        widget = self.takeCentralWidget()
        self._allow_close = True
        self.hide()
        self.close()
        self.deleteLater()
        return widget


class ToolWindowManager(QObject):
    """Own detached hosts while keeping each tool widget instance unchanged."""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.tabs = main_window.tabs
        self._detached: dict[QWidget, _DetachedTool] = {}
        self._tool_order: list[QWidget] = []
        self._session_geometry: dict[str, QByteArray] = {}

        self.toggle_button = QToolButton(self.tabs)
        self.toggle_button.setObjectName("clarify_tool_dock_toggle")
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.clicked.connect(self.detach_current_tool)
        self.tabs.setCornerWidget(self.toggle_button, Qt.Corner.TopRightCorner)
        self.tabs.currentChanged.connect(self.sync_main_control)
        self.retranslate_ui()
        self.sync_main_control()

    def _require_gui_thread(self) -> None:
        app = QApplication.instance()
        if app is None or QThread.currentThread() is not app.thread():
            raise RuntimeError("Tool windows may only be changed on the GUI thread")

    def register_attached(self, widget: QWidget) -> None:
        """Record a tab page without changing its existing order."""
        if widget not in self._tool_order:
            self._tool_order.append(widget)
        self.sync_main_control()

    def is_detached(self, widget: QWidget) -> bool:
        return widget in self._detached

    def is_open(self, widget: Optional[QWidget]) -> bool:
        return bool(widget is not None and (self.tabs.indexOf(widget) >= 0 or widget in self._detached))

    def ordered_open_widgets(self) -> list[QWidget]:
        """Return live attached and detached tools in stable workspace order."""
        return [widget for widget in self._tool_order if is_valid(widget) and self.is_open(widget)]

    def detached_windows(self) -> tuple["DetachedToolWindow", ...]:
        """Return live detached hosts for shared appearance updates."""
        return tuple(record.window for record in self._detached.values())

    def activate_detached(self, widget: QWidget) -> bool:
        """Raise an existing detached host instead of silently reattaching it."""
        record = self._detached.get(widget)
        if record is None:
            return False
        record.window.show()
        record.window.raise_()
        record.window.activateWindow()
        self._restore_focus(record)
        return True

    def detach_current_tool(self) -> bool:
        """Detach the page selected in the main workspace."""
        widget = self.tabs.currentWidget()
        return self.detach_tool(widget) if widget is not None else False

    def detach_tool(self, widget: QWidget) -> bool:
        """Move one tool into a managed top-level host without recreating it."""
        self._require_gui_thread()
        if widget in self._detached:
            return self.activate_detached(widget)
        index = self.tabs.indexOf(widget)
        if index < 0:
            return False

        tool_id = str(widget.property("clarify_tool_id") or "")
        title = self.tabs.tabText(index) or widget.windowTitle() or tool_id
        focus_widget = QApplication.focusWidget()
        if focus_widget is None or (focus_widget is not widget and not widget.isAncestorOf(focus_widget)):
            focus_widget = None

        self.register_attached(widget)
        self.tabs.removeTab(index)
        window = DetachedToolWindow(self, widget, title)
        record = _DetachedTool(widget, tool_id, title, focus_widget, window)
        self._detached[widget] = record
        if tool_id:
            self.main_window.tool_tabs[tool_id] = (widget, -1)

        geometry = self._load_geometry(tool_id)
        if geometry is not None and not geometry.isEmpty():
            window.restoreGeometry(geometry)
        else:
            window.resize(max(640, widget.width()), max(480, widget.height()))
        window.show()
        window.raise_()
        window.activateWindow()
        self._restore_focus(record)
        self.sync_main_control()
        self.main_window._save_tab_state()
        return True

    def attach_tool(self, widget: QWidget, *, activate: bool = True) -> bool:
        """Return a detached tool to its stable position in the main workspace."""
        self._require_gui_thread()
        record = self._detached.pop(widget, None)
        if record is None:
            return False

        self._save_geometry(record)
        released = record.window.release_tool()
        if released is not widget:
            raise RuntimeError("Detached host released an unexpected tool")

        from .tab_manager import TabManager

        TabManager.prepare_embedded_tool(widget)
        title = TabManager.translated_title(record.tool_id) or record.title
        index = self._attached_insert_index(widget)
        index = self.tabs.insertTab(index, widget, title)
        self.tabs.setTabVisible(index, True)
        self._sync_tool_tab_indexes()
        if activate:
            self.tabs.setCurrentIndex(index)
            self.main_window.activateWindow()
            self._restore_focus(record)
        self.sync_main_control()
        self.main_window._restore_window_flags()
        self.main_window._save_tab_state()
        return True

    def close_detached_tool(self, widget: QWidget) -> None:
        """Route detached-window close through the existing main-tab contract."""
        if not self.attach_tool(widget):
            return
        index = self.tabs.indexOf(widget)
        if index >= 0:
            self.main_window._close_tab(index)

    def forget(self, widget: QWidget) -> None:
        """Forget a tool only after the normal close path removed it."""
        record = self._detached.pop(widget, None)
        if record is not None:
            self._save_geometry(record)
            record.window.release_tool()
        self._tool_order = [item for item in self._tool_order if item is not widget]
        self.sync_main_control()

    def reattach_all(self, *, activate: bool = False) -> None:
        """Settle every detached host before application shutdown."""
        self._require_gui_thread()
        current = self.tabs.currentWidget()
        for widget in list(self._tool_order):
            if widget in self._detached:
                self.attach_tool(widget, activate=activate)
        if not activate and current is not None:
            index = self.tabs.indexOf(current)
            if index >= 0:
                self.tabs.setCurrentIndex(index)

    def retranslate_ui(self) -> None:
        """Refresh attached and detached controls after runtime language changes."""
        label = tr("tool_window.detach", "Detach current tool")
        self.toggle_button.setAccessibleName(label)
        self.toggle_button.setToolTip(tr("tool_window.detach_tooltip", "Open the current tool in a separate window"))
        self.toggle_button.setIcon(self.tabs.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        from .tab_manager import TabManager

        for record in self._detached.values():
            title = TabManager.translated_title(record.tool_id) or record.title
            record.window.retranslate_ui(title)
        self.sync_main_control()

    def sync_main_control(self, _index: int = -1) -> None:
        """Expose one stable command for the currently selected workspace tool."""
        available = self.tabs.currentWidget() is not None
        self.toggle_button.setEnabled(available)
        if available:
            self.toggle_button.setToolTip(
                tr("tool_window.detach_tooltip", "Open the current tool in a separate window")
            )
        else:
            self.toggle_button.setToolTip(tr("tool_window.unavailable", "No tool is available to detach"))

    def _attached_insert_index(self, widget: QWidget) -> int:
        try:
            position = self._tool_order.index(widget)
        except ValueError:
            self._tool_order.append(widget)
            return self.tabs.count()
        preceding = self._tool_order[:position]
        return sum(1 for item in preceding if self.tabs.indexOf(item) >= 0)

    def _sync_tool_tab_indexes(self) -> None:
        for tool_id, (widget, _old_index) in list(self.main_window.tool_tabs.items()):
            index = self.tabs.indexOf(widget)
            if index >= 0 or widget in self._detached:
                self.main_window.tool_tabs[tool_id] = (widget, index)

    @staticmethod
    def _restore_focus(record: _DetachedTool) -> None:
        target = record.focus_widget
        if target is not None and is_valid(target) and (target is record.widget or record.widget.isAncestorOf(target)):
            target.setFocus(Qt.FocusReason.OtherFocusReason)

    def _settings(self):
        settings = getattr(self.main_window, "settings", None)
        return getattr(settings, "qsettings", None)

    def _load_geometry(self, tool_id: str) -> Optional[QByteArray]:
        if tool_id in self._session_geometry:
            return self._session_geometry[tool_id]
        settings = self._settings()
        if settings is None or not tool_id:
            return None
        value = settings.value(f"tool_windows/{tool_id}/geometry", None)
        return value if isinstance(value, QByteArray) else None

    def _save_geometry(self, record: _DetachedTool) -> None:
        geometry = record.window.saveGeometry()
        self._session_geometry[record.tool_id] = geometry
        settings = self._settings()
        if settings is not None and record.tool_id:
            settings.setValue(f"tool_windows/{record.tool_id}/geometry", geometry)
