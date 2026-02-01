#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Statistics Dialog - Detailed statistics viewer (Sprint B Feature #3 v2.9.31)
Shows detailed removal statistics with interactive table, search, filter, and export.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


from typing import List, Dict, Any
import json
            import openpyxl  # type: ignore[import-not-found]  # Optional dependency

from PySide6.QtWidgets import (
from PySide6.QtCore import Qt
import csv

from src.i18n.translator import tr
            )

    def _export_excel(self):
        """Export removal stats to Excel (requires openpyxl)."""
        try:
            import openpyxl  # type: ignore[import-not-found]  # Optional dependency
        except ImportError:
            QMessageBox.warning(
                self, tr("statistics.msg_missing_dependency_title"), tr("statistics.msg_missing_openpyxl")
            )
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Excel", "", "Excel Files (*.xlsx)")
        if not filename:
            return

        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Removal Statistics"

            # Write headers
            headers = []
            for col in range(self.removal_table.columnCount()):
                headers.append(self.removal_table.horizontalHeaderItem(col).text())
            sheet.append(headers)

            # Write data (only visible rows)
            for row in range(self.removal_table.rowCount()):
                if not self.removal_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.removal_table.columnCount()):
                        item = self.removal_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    sheet.append(row_data)

            workbook.save(filename)
            QMessageBox.information(
                self, tr("statistics.msg_success_title"), tr("statistics.msg_exported_csv").format(filename=filename)
            )
        except Exception as e:
            QMessageBox.critical(
                self, tr("statistics.msg_error_title"), tr("statistics.msg_export_excel_failed").format(error=e)
            )
