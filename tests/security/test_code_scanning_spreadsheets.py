"""Regressions for spreadsheet formula-injection code-scanning findings."""

import csv
import json
import os
import sys
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import src.export_manager as export_module
from src.export_manager import ExportManager
from src.gui.statistics_dialog import StatisticsDialog
from src.utils.file_finder import AdvancedFileSearchDialog
from src.utils.spreadsheet_security import neutralize_spreadsheet_cell


FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


class _Cell:
    def __init__(self):
        self.value = None
        self.font = None
        self.fill = None


class _Column:
    width = None


class _Sheet:
    def __init__(self):
        self.title = "Sheet"
        self._cells = defaultdict(_Cell)
        self.column_dimensions = defaultdict(_Column)

    @staticmethod
    def _coordinate(reference):
        column = ord(reference[0]) - ord("A") + 1
        return int(reference[1:]), column

    def __getitem__(self, reference):
        return self._cells[self._coordinate(reference)]

    def __setitem__(self, reference, value):
        self[reference].value = value

    def cell(self, row, column):
        return self._cells[(row, column)]

    def append(self, values):
        next_row = max((row for row, _column in self._cells), default=0) + 1
        for column, value in enumerate(values, start=1):
            self.cell(next_row, column).value = value


class _Workbook:
    def __init__(self):
        self.active = _Sheet()
        self.saved_path = None

    def __getitem__(self, title):
        assert self.active.title == title
        return self.active

    def save(self, path):
        self.saved_path = str(path)


@pytest.mark.parametrize("prefix", FORMULA_PREFIXES)
def test_spreadsheet_cell_neutralizes_formula_prefixes(prefix):
    value = f"{prefix}dangerous()"
    assert neutralize_spreadsheet_cell(value) == f"'{value}"


def test_spreadsheet_cell_preserves_safe_and_non_text_values():
    assert neutralize_spreadsheet_cell(" safe") == " safe"
    assert neutralize_spreadsheet_cell("'already text") == "'already text"
    assert neutralize_spreadsheet_cell(42) == 42
    assert neutralize_spreadsheet_cell(None) is None


def test_export_manager_neutralizes_csv_and_excel_but_not_json(
    monkeypatch, tmp_path
):
    data = {"=unsafe-key": "+unsafe-value", "number": -7}
    csv_path = tmp_path / "export.csv"
    xlsx_path = tmp_path / "export.xlsx"
    json_path = tmp_path / "export.json"

    workbook = _Workbook()
    monkeypatch.setattr(export_module, "_EXCEL_AVAILABLE", True)
    monkeypatch.setattr(
        export_module,
        "openpyxl",
        SimpleNamespace(Workbook=lambda: workbook),
        raising=False,
    )
    monkeypatch.setattr(export_module, "Font", lambda **_kwargs: object(), raising=False)
    monkeypatch.setattr(
        export_module, "PatternFill", lambda **_kwargs: object(), raising=False
    )

    ExportManager.export_to_csv(data, csv_path, include_metadata=False)
    ExportManager.export_to_excel(data, xlsx_path, include_metadata=False)
    ExportManager.export_to_json(data, json_path, include_metadata=False)

    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[1] == ["'=unsafe-key", "'+unsafe-value"]
    assert rows[2] == ["number", "-7"]

    sheet = workbook["Export"]
    assert sheet["A2"].value == "'=unsafe-key"
    assert sheet["B2"].value == "'+unsafe-value"
    assert sheet["B3"].value == -7
    assert workbook.saved_path == str(xlsx_path)

    assert json.loads(json_path.read_text(encoding="utf-8")) == data


def test_file_finder_neutralizes_attacker_controlled_filename(qapp, tmp_path):
    source = tmp_path / "=HYPERLINK(evil).txt"
    source.write_text("content", encoding="utf-8")
    output = tmp_path / "finder.csv"
    dialog = AdvancedFileSearchDialog(initial_dir=str(tmp_path))
    dialog.results = [(str(source), os.stat(source))]

    with (
        patch(
            "src.utils.file_finder.QFileDialog.getSaveFileName",
            return_value=(str(output), "CSV Files (*.csv)"),
        ),
        patch("src.utils.file_finder.QMessageBox.information"),
    ):
        dialog._export_results()

    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["Name", "Path", "Size (bytes)", "Size (MB)", "Modified"]
    assert rows[1][0] == "'=HYPERLINK(evil).txt"
    assert rows[1][1] == str(source)


def test_statistics_dialog_neutralizes_csv_and_excel_only(
    qapp, monkeypatch, tmp_path
):
    stats = [{
        "operation": "remove",
        "original_key": "@unsafe",
        "kept_key": "\tunsafe",
        "similarity": "100",
        "line_numbers": "1",
        "count": 1,
    }]
    dialog = StatisticsDialog(stats, {})
    csv_path = tmp_path / "statistics.csv"
    xlsx_path = tmp_path / "statistics.xlsx"
    workbook = _Workbook()
    monkeypatch.setitem(
        sys.modules,
        "openpyxl",
        SimpleNamespace(Workbook=lambda: workbook),
    )

    with (
        patch(
            "src.gui.statistics_dialog.QFileDialog.getSaveFileName",
            return_value=(str(csv_path), "CSV Files (*.csv)"),
        ),
        patch("src.gui.statistics_dialog.QMessageBox.information"),
    ):
        dialog._export_csv()
    with (
        patch(
            "src.gui.statistics_dialog.QFileDialog.getSaveFileName",
            return_value=(str(xlsx_path), "Excel Files (*.xlsx)"),
        ),
        patch("src.gui.statistics_dialog.QMessageBox.information"),
    ):
        dialog._export_excel()

    with csv_path.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.reader(handle))
    assert csv_rows[1][1:3] == ["'@unsafe", "'\tunsafe"]

    sheet = workbook["Removal Statistics"]
    assert sheet.cell(2, 2).value == "'@unsafe"
    assert sheet.cell(2, 3).value == "'\tunsafe"
    assert workbook.saved_path == str(xlsx_path)

    assert stats[0]["original_key"] == "@unsafe"
    assert stats[0]["kept_key"] == "\tunsafe"
