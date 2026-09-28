"""The Explorer must evaluate the same full condition expression in every mode."""

from unittest.mock import Mock

import pytest

import src.core.filters as filters
import src.core.file_explorer_executor as core
from src.gui.widgets.search_widgets import ConditionsGrid
from src.gui.file_explorer_dock import FileExplorerDock


def execute(path, conditions, *, query="needle", logic="AND", browse=False):
    executor = core.UnifiedFileExplorerExecutor()
    if browse:
        return executor.execute_browse(str(path), conditions=conditions, logic_operator=logic)
    return executor.execute_search(str(path), content_query=query, conditions=conditions,
                                   logic_operator=logic)


@pytest.mark.parametrize("browse", [False, True])
@pytest.mark.parametrize("operator,value,expected", [
    ("contains", "absent", False), ("not contains", "absent", True),
    ("equals", "needle cat", True), ("not equals", "needle cat", False),
    ("contains", "CAT", True), ("regex", r"c.t", True),
    ("starts with", "needle", True), ("ends with", "cat", True),
])
def test_content_value_and_operator_are_not_search_match_count(tmp_path, browse, operator, value, expected):
    (tmp_path / "sample.txt").write_text("needle cat")
    result = execute(tmp_path, [{"field": "content", "operator": operator, "value": value,
                                "case_sensitive": False}], browse=browse)
    assert bool(result["files"]) is expected
    assert not result["stats"]["errors"]


@pytest.mark.parametrize("query", [None, "needle"])
@pytest.mark.parametrize("logic,expected", [("AND", []), ("OR", ["sample.txt"])])
def test_mixed_metadata_content_expression(tmp_path, query, logic, expected):
    (tmp_path / "sample.txt").write_text("needle")
    conditions = [{"field": "filename", "operator": "contains", "value": "other"},
                  {"field": "content", "operator": "contains", "value": "needle"}]
    result = execute(tmp_path, conditions, query=query, logic=logic)
    assert [item.file_info.name for item in result["files"]] == expected


@pytest.mark.parametrize("operator,value,expected", [
    ("greater than", "3", True), (">", "3", True), ("less than", "3", False),
    ("greater than or equal", "6", True), ("less than or equal", "6", True),
    ("=", "6", True), ("!=", "6", False), ("equals", "6", True),
])
@pytest.mark.parametrize("browse", [False, True])
def test_old_and_canonical_numeric_operators(tmp_path, operator, value, expected, browse):
    (tmp_path / "sample.txt").write_text("needle")
    result = execute(tmp_path, [{"field": "size", "operator": operator, "value": value}], browse=browse)
    assert bool(result["files"]) is expected
    assert not result["stats"]["errors"]


@pytest.mark.parametrize("condition", [
    {"field": "content", "operator": "contains", "value": "cats", "whole_word": True},
    {"field": "content", "operator": "contains", "value": "CAT", "case_sensitive": True},
    {"field": "content", "operator": "ends with", "value": "needle", "regex": True},
    {"field": "content", "operator": "contains", "value": "outside", "scope_type": "brackets"},
])
def test_content_options_are_honored(tmp_path, condition):
    (tmp_path / "sample.txt").write_text("needle outside [cat catsup]")
    assert not execute(tmp_path, [condition])["files"]


@pytest.mark.parametrize("condition", [
    {"field": "missing", "operator": "contains", "value": "needle"},
    {"field": "size", "operator": "contains", "value": "1"},
    {"field": "size", "operator": ">", "value": "NaN"},
    {"field": "mtime", "operator": ">", "value": "yesterday"},
    {"field": "content", "operator": "regex", "value": "["},
    "invalid preset entry",
])
@pytest.mark.parametrize("browse", [False, True])
def test_invalid_condition_fails_closed_with_diagnostics(tmp_path, condition, browse):
    (tmp_path / "sample.txt").write_text("needle")
    result = execute(tmp_path, [condition], browse=browse)
    assert result["files"] == []
    assert "Invalid conditions" in result["stats"]["errors"][0]


def test_bounded_condition_read_and_binary_diagnostic(tmp_path, monkeypatch):
    (tmp_path / "sample.txt").write_text("needle")
    (tmp_path / "data.bin").write_bytes(b"\x00needle")
    monkeypatch.setattr(core, "MAX_REPLACE_FILE_BYTES", 3)
    condition = {"field": "content", "operator": "contains", "value": "needle"}
    result = execute(tmp_path, [condition])
    assert result["files"] == []
    assert len(result["stats"]["errors"]) == 2
    monkeypatch.setattr(core, "MAX_REPLACE_FILE_BYTES", 100)
    result = execute(tmp_path, [condition])
    assert [item.file_info.name for item in result["files"]] == ["sample.txt"]
    assert "binary" in result["stats"]["errors"][0]


def test_shared_conditions_read_content_only_once(tmp_path, monkeypatch):
    path = tmp_path / "sample.txt"
    path.write_text("needle cat")
    read = Mock(wraps=filters.read_text)
    monkeypatch.setattr(filters, "read_text", read)
    conditions = [filters.Condition("content", "contains", "needle"),
                  filters.Condition("content", "contains", "cat")]
    assert filters.filter_files_by_conditions([str(path)], conditions) == [str(path)]
    assert read.call_count == 1


def test_shared_or_can_match_metadata_when_content_read_fails(tmp_path, monkeypatch):
    path = tmp_path / "sample.txt"
    path.write_text("needle")
    monkeypatch.setattr(filters, "read_text", Mock(side_effect=PermissionError("unreadable")))
    conditions = [filters.Condition("content", "contains", "needle"),
                  filters.Condition("filename", "equals", "sample.txt")]
    assert filters.filter_files_by_conditions([str(path)], conditions, "OR") == [str(path)]


@pytest.mark.parametrize("content_first", [False, True])
def test_or_does_not_depend_on_order_for_binary_files(tmp_path, content_first):
    (tmp_path / "data.bin").write_bytes(b"\x00needle")
    content = {"field": "content", "operator": "contains", "value": "needle"}
    metadata = {"field": "filename", "operator": "equals", "value": "data.bin"}
    conditions = [content, metadata] if content_first else [metadata, content]
    result = execute(tmp_path, conditions, query=None, logic="OR")
    assert [item.file_info.name for item in result["files"]] == ["data.bin"]
    assert not result["stats"]["errors"]


def test_regex_end_anchor_and_grouped_whole_word():
    end = filters.Condition("content", "ends with", "cat", use_regex=True)
    assert end._apply_string_matching("needle cat", "cat", "ends with")
    assert not end._apply_string_matching("cat needle", "cat", "ends with")
    word = filters.Condition("content", "contains", "cat|dog", use_regex=True, whole_word=True)
    assert not word._apply_string_matching("cats hotdog", "cat|dog", "contains")


def test_grid_emits_numeric_data_and_clears_rows(qapp):
    grid = ConditionsGrid()
    try:
        row = grid.condition_rows[0]
        row["field"].setCurrentIndex(row["field"].findData("size"))
        row["operator"].setCurrentText("greater than")
        row["value"].setText("4")
        assert grid.get_conditions()[0]["operator"] == ">"
        grid.clear_conditions()
        assert not grid.condition_rows and grid.get_conditions() == []
    finally:
        grid.deleteLater()


def test_completion_errors_are_visible_and_bounded(qapp):
    dock = FileExplorerDock()
    try:
        dock.results_status.setText("Found 0 file(s)")
        dock._report_result_errors({"stats": {"errors": ["Invalid conditions"] * 50}})
        assert "50 error(s)" in dock.results_status.text()
        assert dock.results_status.toolTip().splitlines() == ["Invalid conditions"] * 5
    finally:
        dock.deleteLater()
