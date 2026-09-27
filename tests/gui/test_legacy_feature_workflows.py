"""Offline workflow checks supporting the legacy-task audit."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QTreeWidgetItem

from src.calculator_memory import CalculatorMemory
from src.calculator_operations import CalculatorOperations
from src.gui.diff_viewer_dialog import DiffViewerDialog
from src.gui.panels.results_tree import (
    ITEM_TYPE_DIRECTORY, ITEM_TYPE_FILE, ITEM_TYPE_MATCH, ITEM_TYPE_ROLE,
    RESULT_PATH_ROLE, ResultsTree,
)
from src.gui.venn_diagram_dialog import VennDiagramDialog


@pytest.mark.parametrize("item_type", [ITEM_TYPE_FILE, ITEM_TYPE_MATCH])
def test_result_activation_opens_only_target_file(qtbot, tmp_path, item_type):
    path = tmp_path / "result.txt"
    path.write_text("result", encoding="utf-8")
    other_path = tmp_path / "other.txt"
    other_path.write_text("other", encoding="utf-8")
    editor = SimpleNamespace(open_file_path=Mock())
    window = SimpleNamespace(dock_editor=editor, _show_editor=Mock())
    tree = ResultsTree(main_window=window)
    qtbot.addWidget(tree)
    other = QTreeWidgetItem(tree, ["other"])
    other.setData(0, ITEM_TYPE_ROLE, ITEM_TYPE_FILE)
    other.setData(0, RESULT_PATH_ROLE, str(other_path))
    item = QTreeWidgetItem(tree, ["result"])
    item.setData(0, ITEM_TYPE_ROLE, item_type)
    item.setData(0, RESULT_PATH_ROLE, str(path))
    tree.setCurrentItem(item)
    other.setSelected(True)
    tree.show()
    tree.setFocus()
    qtbot.keyClick(tree, Qt.Key_Return)
    editor.open_file_path.assert_called_once_with(str(path))
    window._show_editor.assert_called_once()


def test_directory_activation_does_not_open_descendants(qtbot, tmp_path):
    editor = SimpleNamespace(open_file_path=Mock())
    window = SimpleNamespace(dock_editor=editor, _show_editor=Mock())
    tree = ResultsTree(main_window=window)
    qtbot.addWidget(tree)
    item = QTreeWidgetItem(tree, ["directory"])
    item.setData(0, ITEM_TYPE_ROLE, ITEM_TYPE_DIRECTORY)
    item.setData(0, RESULT_PATH_ROLE, str(tmp_path))
    tree.itemActivated.emit(item, 0)
    editor.open_file_path.assert_not_called()
    window._show_editor.assert_not_called()


def test_calculator_slots_persist_merge_recall_and_clear(tmp_path, monkeypatch):
    settings = QSettings(str(tmp_path / "memory.ini"), QSettings.IniFormat)
    monkeypatch.setattr("src.calculator_memory.QSettings", lambda *args: settings)
    memory = CalculatorMemory()
    assert memory.store_result("A", {"a": 1})
    assert memory.store_result("B", {"b": 2})
    success, result, _message = CalculatorOperations.add(
        memory.recall_result("A"), memory.recall_result("B")
    )
    assert success
    assert result == {"a": 1, "b": 2}
    assert memory.store_result("C", result)
    assert CalculatorMemory().recall_result("C") == result
    assert memory.clear_slot("C")
    assert CalculatorMemory().recall_result("C") is None
    assert not memory.store_result("F", result)


def test_diff_viewer_syncs_scroll_and_retains_values(qtbot):
    data = {f"key_{i}": i for i in range(200)}
    dialog = DiffViewerDialog(data, data, "a.json", "b.json")
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: dialog.text_a.verticalScrollBar().maximum() > 0)
    assert json.loads(dialog.text_a.toPlainText()) == data
    left = dialog.text_a.verticalScrollBar()
    right = dialog.text_b.verticalScrollBar()
    left.setValue(left.maximum() // 2)
    assert right.value() == left.value()
    right.setValue(0)
    assert left.value() == 0


def test_diff_viewer_can_scroll_to_end_with_unequal_document_lengths(qtbot):
    dialog = DiffViewerDialog(
        {f"key_{i}": i for i in range(300)},
        {f"key_{i}": i for i in range(60)}, "long.json", "short.json",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    left = dialog.text_a.verticalScrollBar()
    right = dialog.text_b.verticalScrollBar()
    qtbot.waitUntil(lambda: left.maximum() > right.maximum() > 0)
    left.setValue(left.maximum())
    assert left.value() == left.maximum()
    assert right.value() == right.maximum()
    right.setValue(right.maximum() // 2)
    assert abs(left.value() / left.maximum() - right.value() / right.maximum()) < 0.01


def test_venn_regions_show_their_key_values(qtbot):
    dialog = VennDiagramDialog(
        {"a": 1, "common": 3}, {"b": 2, "common": 3}, "a.json", "b.json"
    )
    qtbot.addWidget(dialog)
    for region, key, value in [("only_a", "a", "1"),
                               ("only_b", "b", "2"),
                               ("intersection", "common", "3")]:
        dialog.show_region_details(region)
        assert dialog.list_keys.count() == 1
        assert dialog.list_keys.item(0).text() == key
        dialog.list_keys.setCurrentRow(0)
        assert dialog.text_value.toPlainText() == value


def test_tutorial_index_targets_exist():
    root = Path(__file__).resolve().parents[2] / "docs" / "tutorials"
    index = json.loads((root / "index.json").read_text(encoding="utf-8"))
    assert index["tutorials"]
    for tutorial in index["tutorials"]:
        assert (root / tutorial["file"]).is_file(), tutorial["file"]
