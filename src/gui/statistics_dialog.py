#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Statistics Dialog - Detailed statistics viewer (Sprint B Feature #3 v2.9.31)
Shows detailed removal statistics with interactive table, search, filter, and export.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QComboBox, QLabel,
    QHeaderView, QMenu, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from typing import List, Dict, Any
import csv
import json


class StatisticsDialog(QDialog):
    """Dialog to display detailed statistics about JSON operations.
    
    Features:
    - Two tabs: Removal Operations + Reference Stats
    - Interactive table with 6 columns
    - Sort by clicking headers
    - Search box to filter results
    - Column filters
    - Export to CSV/JSON/Excel
    """
    
    def __init__(self, removal_stats: List[Dict[str, Any]], reference_stats: Dict[str, int], parent=None):
        super().__init__(parent)
        self.removal_stats = removal_stats
        self.reference_stats = reference_stats
        self.setWindowTitle("Detailed Statistics")
        self.setMinimumSize(900, 600)
        
        self._init_ui()
        self._populate_data()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Tab 1: Removal Operations
        self.removal_tab = self._create_removal_tab()
        self.tabs.addTab(self.removal_tab, "Removal Operations")
        
        # Tab 2: Reference Stats
        self.reference_tab = self._create_reference_tab()
        self.tabs.addTab(self.reference_tab, "Reference Statistics")
        
        layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Export button with dropdown menu
        self.btn_export = QPushButton("Export ▼")
        self.export_menu = QMenu()
        self.export_menu.addAction("Export CSV", self._export_csv)
        self.export_menu.addAction("Export JSON", self._export_json)
        self.export_menu.addAction("Export Excel", self._export_excel)
        self.btn_export.setMenu(self.export_menu)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        
        button_layout.addWidget(self.btn_export)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
    
    def _create_removal_tab(self):
        """Create the removal operations tab."""
        widget = QTableWidget()
        
        # Search and filter section
        container = QTableWidget()
        container_layout = QVBoxLayout(container)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter results...")
        self.search_box.textChanged.connect(self._filter_removal_table)
        search_layout.addWidget(self.search_box)
        container_layout.addLayout(search_layout)
        
        # Column filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Operation:"))
        self.operation_filter = QComboBox()
        self.operation_filter.addItem("All Operations")
        self.operation_filter.currentTextChanged.connect(self._filter_removal_table)
        filter_layout.addWidget(self.operation_filter)
        filter_layout.addStretch()
        container_layout.addLayout(filter_layout)
        
        # Table
        self.removal_table = QTableWidget()
        self.removal_table.setColumnCount(6)
        self.removal_table.setHorizontalHeaderLabels([
            "Operation Type", "Original Key", "Kept Key", 
            "Similarity %", "Line Numbers", "Count"
        ])
        self.removal_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.removal_table.horizontalHeader().setStretchLastSection(False)
        self.removal_table.setSortingEnabled(True)
        self.removal_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.removal_table.setColumnWidth(0, 150)  # Operation Type
        self.removal_table.setColumnWidth(1, 250)  # Original Key
        self.removal_table.setColumnWidth(2, 250)  # Kept Key
        self.removal_table.setColumnWidth(3, 100)  # Similarity
        self.removal_table.setColumnWidth(4, 100)  # Line Numbers
        self.removal_table.setColumnWidth(5, 80)   # Count
        
        container_layout.addWidget(self.removal_table)
        
        return container
    
    def _create_reference_tab(self):
        """Create the reference statistics tab."""
        widget = QTableWidget()
        container_layout = QVBoxLayout(widget)
        
        # Table for reference stats
        self.reference_table = QTableWidget()
        self.reference_table.setColumnCount(2)
        self.reference_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.reference_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.reference_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.reference_table.setAlternatingRowColors(True)
        
        container_layout.addWidget(self.reference_table)
        
        return widget
    
    def _populate_data(self):
        """Populate tables with data."""
        # Populate removal operations table
        self.removal_table.setRowCount(len(self.removal_stats))
        
        operations_set = set()
        for i, entry in enumerate(self.removal_stats):
            self.removal_table.setItem(i, 0, QTableWidgetItem(entry.get('operation', 'N/A')))
            self.removal_table.setItem(i, 1, QTableWidgetItem(entry.get('original_key', 'N/A')))
            self.removal_table.setItem(i, 2, QTableWidgetItem(entry.get('kept_key', 'N/A')))
            self.removal_table.setItem(i, 3, QTableWidgetItem(entry.get('similarity', 'N/A')))
            self.removal_table.setItem(i, 4, QTableWidgetItem(entry.get('line_numbers', 'N/A')))
            
            # Count column as number for sorting
            count_item = QTableWidgetItem()
            count_item.setData(Qt.ItemDataRole.DisplayRole, entry.get('count', 0))
            self.removal_table.setItem(i, 5, count_item)
            
            operations_set.add(entry.get('operation', 'N/A'))
        
        # Populate operation filter dropdown
        for op in sorted(operations_set):
            self.operation_filter.addItem(op)
        
        # Populate reference stats table
        ref_rows = [
            ("References Created", self.reference_stats.get('created', 0)),
            ("References Resolved", self.reference_stats.get('resolved', 0)),
            ("Invalid References", self.reference_stats.get('invalid', 0)),
            ("Duplicates Deleted", self.reference_stats.get('deleted', 0)),
            ("Objects Kept", self.reference_stats.get('kept', 0)),
        ]
        
        self.reference_table.setRowCount(len(ref_rows))
        for i, (metric, value) in enumerate(ref_rows):
            self.reference_table.setItem(i, 0, QTableWidgetItem(metric))
            value_item = QTableWidgetItem()
            value_item.setData(Qt.ItemDataRole.DisplayRole, value)
            self.reference_table.setItem(i, 1, value_item)
    
    def _filter_removal_table(self):
        """Filter the removal table based on search box and operation filter."""
        search_text = self.search_box.text().lower()
        operation_filter = self.operation_filter.currentText()
        
        for row in range(self.removal_table.rowCount()):
            should_show = True
            
            # Check operation filter
            if operation_filter != "All Operations":
                operation = self.removal_table.item(row, 0).text()
                if operation != operation_filter:
                    should_show = False
            
            # Check search text (search in all columns)
            if should_show and search_text:
                row_text = ""
                for col in range(self.removal_table.columnCount()):
                    item = self.removal_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    should_show = False
            
            self.removal_table.setRowHidden(row, not should_show)
    
    def _export_csv(self):
        """Export removal stats to CSV."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                headers = []
                for col in range(self.removal_table.columnCount()):
                    headers.append(self.removal_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Write data (only visible rows)
                for row in range(self.removal_table.rowCount()):
                    if not self.removal_table.isRowHidden(row):
                        row_data = []
                        for col in range(self.removal_table.columnCount()):
                            item = self.removal_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV: {e}")
    
    def _export_json(self):
        """Export removal stats to JSON."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "", "JSON Files (*.json)"
        )
        if not filename:
            return
        
        try:
            # Export only visible rows
            data = []
            for row in range(self.removal_table.rowCount()):
                if not self.removal_table.isRowHidden(row):
                    data.append(self.removal_stats[row])
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            QMessageBox.information(self, "Success", f"Exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export JSON: {e}")
    
    def _export_excel(self):
        """Export removal stats to Excel (requires openpyxl)."""
        try:
            import openpyxl
        except ImportError:
            QMessageBox.warning(
                self, "Missing Dependency", 
                "Excel export requires 'openpyxl' package.\nInstall with: pip install openpyxl"
            )
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "", "Excel Files (*.xlsx)"
        )
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
            QMessageBox.information(self, "Success", f"Exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export Excel: {e}")
