"""Data safety checks for the legacy regex-insert requirement (LEG-01)."""

import json

import pytest

from src.core.memory_register import MemoryRegister
from src.gui.json_editor_tab import JsonEditorTab


@pytest.fixture
def tab(qtbot, mock_message_box):
    widget = JsonEditorTab()
    qtbot.addWidget(widget)
    return widget


@pytest.mark.parametrize("position, expected", [
    ("Before (sibling)", ["first", "added", "target", "last"]),
    ("After (sibling)", ["first", "target", "added", "last"]),
])
@pytest.mark.parametrize("container", ["root", "nested", "array"])
def test_insert_preserves_sibling_order_and_undo(tab, position, expected, container):
    content = {"first": 1, "target": 2, "last": 3}
    if container == "nested":
        content = {"parent": content}
    elif container == "array":
        content = [content]
    original = json.dumps(content)
    tab.editor.setPlainText(original)
    tab.editor.moveCursor(tab.editor.textCursor().MoveOperation.End)
    tab.editor.insertPlainText(" ")
    before_insert = tab.editor.toPlainText()

    tab._handle_regex_insert("target", "added", "42", position)

    modified = tab.editor.toPlainText()
    result = json.loads(modified)
    if container == "nested":
        result = result["parent"]
    elif container == "array":
        result = result[0]
    assert list(result) == expected
    assert result["added"] == 42
    tab.editor.undo()
    assert tab.editor.toPlainText() == before_insert
    tab.editor.undo()
    assert tab.editor.toPlainText() == original
    tab.editor.redo()
    tab.editor.redo()
    assert tab.editor.toPlainText() == modified


@pytest.mark.parametrize("position", [
    "Inside (as child)", "Before (sibling)", "After (sibling)",
])
def test_existing_key_is_not_silently_overwritten(tab, mock_message_box, position):
    original = '{"target": {"existing": 1}, "existing": 2}'
    tab.editor.setPlainText(original)
    tab._handle_regex_insert("target", "existing", "99", position)
    assert tab.editor.toPlainText() == original
    assert mock_message_box[-1][0] == "critical"


def test_scalar_target_reports_error_without_losing_text(tab, mock_message_box):
    original = '{"target": 1}'
    tab.editor.setPlainText(original)
    tab._handle_regex_insert("target", "added", "42", "Inside (as child)")
    assert tab.editor.toPlainText() == original
    assert mock_message_box[-1][0] == "critical"
    assert "not an object" in mock_message_box[-1][1][2]


def test_inside_insertion_can_be_undone(tab):
    original = '{"target": {}}'
    tab.editor.setPlainText(original)
    tab._handle_regex_insert("target", "added", "true", "Inside (as child)")
    assert json.loads(tab.editor.toPlainText()) == {"target": {"added": True}}
    tab.editor.undo()
    assert tab.editor.toPlainText() == original


def test_register_values_are_substituted_literally_once():
    register = MemoryRegister()
    register.capture("one|$1", r"(.*)\|(.*)")
    assert register.replace_in_text("$2 $1") == "$1 one"


def test_unknown_register_is_not_partially_substituted():
    register = MemoryRegister()
    register.capture("one", r"(.+)")
    assert register.replace_in_text("$10 $100 $1") == "$10 $100 one"
