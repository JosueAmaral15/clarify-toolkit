"""ShortcutManager regressions for actions with portable aliases."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

import pytest
from PySide6.QtGui import QAction, QKeySequence

from src.shortcut_manager import ShortcutManager


@pytest.fixture(autouse=True)
def reset_shortcuts():
    ShortcutManager.reset_all_custom_shortcuts()
    yield
    ShortcutManager.reset_all_custom_shortcuts()


def portable_shortcuts(action):
    return [item.toString(QKeySequence.PortableText) for item in action.shortcuts()]


def test_redo_has_two_default_key_sequences():
    sequences = [item.toString(QKeySequence.PortableText) for item in ShortcutManager.get_key_sequences("redo")]

    assert sequences == ["Ctrl+Y", "Ctrl+Shift+Z"]
    assert ShortcutManager.get_conflicts("Ctrl+Shift+Z") == ["redo"]


def test_custom_redo_shortcut_replaces_the_default_set():
    ShortcutManager.set_custom_shortcut("redo", "Ctrl+Alt+R")

    sequences = [item.toString(QKeySequence.PortableText) for item in ShortcutManager.get_key_sequences("redo")]

    assert sequences == ["Ctrl+Alt+R"]
    assert ShortcutManager.get_conflicts("Ctrl+Shift+Z") == []
    assert ShortcutManager.get_conflicts("Ctrl+Alt+R") == ["redo"]


def test_action_registration_applies_every_active_sequence(qapp):
    action = QAction("Redo")

    ShortcutManager.add_shortcut_to_action(action, "redo")

    assert portable_shortcuts(action) == ["Ctrl+Y", "Ctrl+Shift+Z"]
