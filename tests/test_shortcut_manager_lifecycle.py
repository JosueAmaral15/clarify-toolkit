"""Shortcut registry teardown regressions."""

# pylint: disable=no-name-in-module  # PySide6/shiboken6 expose dynamic bindings.

from PySide6.QtGui import QAction
from PySide6.QtCore import QObject
from shiboken6 import delete, isValid

from src.shortcut_manager import ShortcutManager


def test_destroyed_action_does_not_emit_through_deleted_event_source(qapp):
    owner = QObject()
    action = QAction(owner)
    ShortcutManager.register_action(action, "copy")

    deleted_events = ShortcutManager.events()
    delete(deleted_events)
    assert not isValid(deleted_events)

    # QAction destruction invokes the registered destroyed callback while the
    # old shared event source is already gone. This used to raise RuntimeError.
    delete(owner)
    qapp.processEvents()

    replacement = ShortcutManager.events()
    assert isValid(replacement)
    assert replacement is not deleted_events
