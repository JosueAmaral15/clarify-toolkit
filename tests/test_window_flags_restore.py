"""Regression tests for MainWindow flag restoration behavior."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from PySide6.QtCore import Qt

from src.app import _restore_qt_window_flags


class _FakeWindow:
    def __init__(self, flags, state=Qt.WindowNoState, visible=True):
        self._flags = flags
        self._state = state
        self._visible = visible
        self.calls = []

    def windowFlags(self):
        return self._flags

    def setWindowFlags(self, flags):
        self.calls.append(("setWindowFlags", flags))
        self._flags = flags
        self._visible = False

    def isVisible(self):
        return self._visible

    def windowState(self):
        return self._state

    def setWindowState(self, state):
        self.calls.append(("setWindowState", state))
        self._state = state

    def show(self):
        self.calls.append(("show", None))
        self._visible = True

    def showMaximized(self):
        self.calls.append(("showMaximized", None))
        self._visible = True

    def showFullScreen(self):
        self.calls.append(("showFullScreen", None))
        self._visible = True

    def showMinimized(self):
        self.calls.append(("showMinimized", None))
        self._visible = True


def test_restore_window_flags_preserves_visible_maximized_state():
    """Restoring flags should bring a visible maximized window back maximized."""
    desired_flags = Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
    current_flags = Qt.Window | Qt.WindowCloseButtonHint
    window = _FakeWindow(current_flags, state=Qt.WindowMaximized, visible=True)

    changed = _restore_qt_window_flags(window, desired_flags)

    assert changed is True
    assert ("setWindowFlags", desired_flags) in window.calls
    assert ("setWindowState", Qt.WindowMaximized) in window.calls
    assert window.calls[-1] == ("showMaximized", None)
    assert window.isVisible() is True


def test_restore_window_flags_does_not_show_hidden_window():
    """Restoring flags should not make a hidden window visible."""
    desired_flags = Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
    current_flags = Qt.Window | Qt.WindowCloseButtonHint
    window = _FakeWindow(current_flags, state=Qt.WindowNoState, visible=False)

    changed = _restore_qt_window_flags(window, desired_flags)

    assert changed is True
    assert ("setWindowFlags", desired_flags) in window.calls
    assert ("setWindowState", Qt.WindowNoState) in window.calls
    assert ("show", None) not in window.calls


def test_restore_window_flags_noops_when_flags_are_current():
    """No visible change should be triggered when flags are already correct."""
    desired_flags = Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
    window = _FakeWindow(desired_flags, state=Qt.WindowMaximized, visible=True)

    changed = _restore_qt_window_flags(window, desired_flags)

    assert changed is False
    assert window.calls == []
