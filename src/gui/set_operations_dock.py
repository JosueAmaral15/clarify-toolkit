#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Set Operations Dock - GUI Interface (v2.9.32)

Provides GUI for JSON set operations with pipeline processing.

Design Patterns:
    - Controller (GRASP): Coordinates UI workflow
    - Observer (GoF): Qt signals for communication
    - Low Coupling (GRASP): Depends only on set_operations core logic

Author: Josué Amaral
Date: December 2, 2025
Version: 2.9.32
"""

import json
import os
from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
)

from ..set_operations import difference, intersection, symmetric_difference, union
from .base_dock import BaseDock


class SetOperationsDock(BaseDock):
    """Dock widget for JSON set operations."""

    def __init__(self, parent=None):
        self.file_paths: List[str] = []
        super().__init__("JSON Set Operations", parent)

    def _setup_ui(self):
        """Setup user interface components."""
        main_layout = QVBoxLayout()

        # === File Selection Section ===
        file_group = QGroupBox("File Selection")
        file_layout = QGridLayout()

        # File A
        file_layout.addWidget(QLabel("File A:"), 0, 0)
        self.ed_file_a = QLineEdit()
        self.ed_file_a.setPlaceholderText("Select first JSON file...")
        file_layout.addWidget(self.ed_file_a, 0, 1)
        self.btn_browse_a = QPushButton("Browse...")
        self.btn_browse_a.setMaximumWidth(100)
        file_layout.addWidget(self.btn_browse_a, 0, 2)

        # File B
        file_layout.addWidget(QLabel("File B:"), 1, 0)
        self.ed_file_b = QLineEdit()
        self.ed_file_b.setPlaceholderText("Select second JSON file...")
        file_layout.addWidget(self.ed_file_b, 1, 1)
        self.btn_browse_b = QPushButton("Browse...")
        self.btn_browse_b.setMaximumWidth(100)
        file_layout.addWidget(self.btn_browse_b, 1, 2)

        # Multiple files checkbox
        self.chk_multiple = QCheckBox("Multiple files (pipeline processing)")
        self.chk_multiple.setToolTip("Enable to add more files for sequential operations")
        file_layout.addWidget(self.chk_multiple, 2, 0, 1, 3)

        # File list (hidden by default)
        self.list_files = QListWidget()
        self.list_files.setMaximumHeight(100)
        self.list_files.setVisible(False)
        file_layout.addWidget(self.list_files, 3, 0, 1, 3)

        # Buttons for file list
        file_btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("+ Add File")
        self.btn_add_file.setVisible(False)
        self.btn_remove_file = QPushButton("- Remove Selected")
        self.btn_remove_file.setVisible(False)
        self.btn_clear_files = QPushButton("Clear All")
        self.btn_clear_files.setVisible(False)
        file_btn_layout.addWidget(self.btn_add_file)
        file_btn_layout.addWidget(self.btn_remove_file)
        file_btn_layout.addWidget(self.btn_clear_files)
        file_btn_layout.addStretch()
        file_layout.addLayout(file_btn_layout, 4, 0, 1, 3)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # === Operations Section ===
        ops_group = QGroupBox("Operations (Pipeline: Left → Right)")
        ops_layout = QVBoxLayout()

        ops_layout.addWidget(QLabel("Select operations to perform:"))
        self.chk_intersection = QCheckBox("∩ Intersection")
        self.chk_union = QCheckBox("∪ Union")
        self.chk_difference = QCheckBox("− Difference")
        self.chk_symmetric = QCheckBox("⊕ Symmetric Difference (2 files only)")

        ops_layout.addWidget(self.chk_intersection)
        ops_layout.addWidget(self.chk_union)
        ops_layout.addWidget(self.chk_difference)
        ops_layout.addWidget(self.chk_symmetric)

        ops_group.setLayout(ops_layout)
        main_layout.addWidget(ops_group)

        # === Comparison Mode Section ===
        comp_group = QGroupBox("Comparison Mode")
        comp_layout = QVBoxLayout()

        self.radio_key_value = QRadioButton("Keys and values (strict types)")
        self.radio_key_value.setChecked(True)
        self.radio_full_path = QRadioButton("Full path and values (dot notation)")
        self.radio_key_only = QRadioButton("Keys only (path)")

        self.comp_mode_group = QButtonGroup()
        self.comp_mode_group.addButton(self.radio_key_value)
        self.comp_mode_group.addButton(self.radio_full_path)
        self.comp_mode_group.addButton(self.radio_key_only)

        comp_layout.addWidget(self.radio_key_value)
        comp_layout.addWidget(self.radio_full_path)
        comp_layout.addWidget(self.radio_key_only)

        comp_group.setLayout(comp_layout)
        main_layout.addWidget(comp_group)

        # === Options Section ===
        opts_group = QGroupBox("Options")
        opts_layout = QVBoxLayout()

        self.chk_ignore_case_keys = QCheckBox("Ignore case in keys")
        self.chk_ignore_case_values = QCheckBox("Ignore case in values")
        self.chk_skip_empty = QCheckBox("Skip empty values")
        self.chk_arrays_ignore_order = QCheckBox("Arrays: ignore order")
        self.chk_arrays_ignore_order.setToolTip("Treat [1,2,3] same as [3,2,1]")

        opts_layout.addWidget(self.chk_ignore_case_keys)
        opts_layout.addWidget(self.chk_ignore_case_values)
        opts_layout.addWidget(self.chk_skip_empty)
        opts_layout.addWidget(self.chk_arrays_ignore_order)

        opts_group.setLayout(opts_layout)
        main_layout.addWidget(opts_group)

        # === Output Format Section ===
        output_group = QGroupBox("Output Format")
        output_layout = QVBoxLayout()

        output_layout.addWidget(QLabel("Select output organization:"))
        self.combo_output = QComboBox()
        self.combo_output.addItems(["JSON nested (all operations)", "Separate files", "Display only (no save)"])
        output_layout.addWidget(self.combo_output)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # === Action Buttons ===
        btn_layout = QHBoxLayout()
        self.btn_execute = QPushButton("Execute")
        self.btn_execute.setMinimumHeight(35)
        self.btn_clear = QPushButton("Clear")
        self.btn_save = QPushButton("Save Result")
        self.btn_save.setEnabled(False)

        btn_layout.addWidget(self.btn_execute)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        # === Results Section ===
        main_layout.addWidget(QLabel("Results:"))
        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setMinimumHeight(200)
        main_layout.addWidget(self.txt_result)

        # === Statistics Section ===
        self.lbl_stats = QLabel("")
        self.lbl_stats.setWordWrap(True)
        self.lbl_stats.setStyleSheet("color: #6A9955; font-weight: bold;")
        main_layout.addWidget(self.lbl_stats)

        main_layout.addStretch()
        self.layout.addLayout(main_layout)

    def _connect_signals(self):
        """Connect UI signals to slots."""
        self.btn_browse_a.clicked.connect(lambda: self._browse_file("a"))
        self.btn_browse_b.clicked.connect(lambda: self._browse_file("b"))
        self.chk_multiple.toggled.connect(self._toggle_multiple_files)
        self.btn_add_file.clicked.connect(self._add_file)
        self.btn_remove_file.clicked.connect(self._remove_file)
        self.btn_clear_files.clicked.connect(self._clear_files)
        self.btn_execute.clicked.connect(self._execute)
        self.btn_clear.clicked.connect(self._clear_all)
        self.btn_save.clicked.connect(self._save_result)

    def _browse_file(self, target: str):
        """Browse for JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select File {target.upper()}", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            if target == "a":
                self.ed_file_a.setText(file_path)
            else:
                self.ed_file_b.setText(file_path)

    def _toggle_multiple_files(self, checked: bool):
        """Toggle multiple files mode."""
        self.list_files.setVisible(checked)
        self.btn_add_file.setVisible(checked)
        self.btn_remove_file.setVisible(checked)
        self.btn_clear_files.setVisible(checked)

        if checked:
            # Populate list with File A and B if they exist
            self.list_files.clear()
            if self.ed_file_a.text():
                self.list_files.addItem(self.ed_file_a.text())
            if self.ed_file_b.text():
                self.list_files.addItem(self.ed_file_b.text())

    def _add_file(self):
        """Add file to list."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Add JSON File", "", "JSON Files (*.json);;All Files (*)")

        if file_path:
            self.list_files.addItem(file_path)

    def _remove_file(self):
        """Remove selected file from list."""
        current_row = self.list_files.currentRow()
        if current_row >= 0:
            self.list_files.takeItem(current_row)

    def _clear_files(self):
        """Clear file list."""
        self.list_files.clear()

    def _get_files(self) -> List[str]:
        """Get list of files to process."""
        if self.chk_multiple.isChecked():
            files = []
            for i in range(self.list_files.count()):
                files.append(self.list_files.item(i).text())
            return files
        else:
            files = []
            if self.ed_file_a.text():
                files.append(self.ed_file_a.text())
            if self.ed_file_b.text():
                files.append(self.ed_file_b.text())
            return files

    def _execute(self):
        """Execute set operations."""
        files = self._get_files()

        # Validate inputs
        if len(files) < 2:
            self.show_error("Error", "Please select at least 2 JSON files.")
            return

        # Check at least one operation selected
        if not any(
            [
                self.chk_intersection.isChecked(),
                self.chk_union.isChecked(),
                self.chk_difference.isChecked(),
                self.chk_symmetric.isChecked(),
            ]
        ):
            self.show_error("Error", "Please select at least one operation.")
            return

        # Validate and load JSON files (Security: CWE-22)
        try:
            from ..set_operations import validate_file_path

            file_dicts = []
            for file_path in files:
                # Security validation
                if not validate_file_path(file_path):
                    self.show_error(
                        "Security Error",
                        f"Invalid or insecure file path:\n{file_path}\n\n"
                        "File must exist, be readable, and have .json extension.",
                    )
                    return

                with open(file_path, "r", encoding="utf-8") as f:
                    file_dicts.append(json.load(f))
        except Exception as e:
            self.show_error("Error Loading Files", str(e))
            return

        # Get options
        comparison_mode = "key_value"
        if self.radio_full_path.isChecked():
            comparison_mode = "full_path_value"
        elif self.radio_key_only.isChecked():
            comparison_mode = "key_only"

        options = {
            "comparison_mode": comparison_mode,
            "ignore_case_keys": self.chk_ignore_case_keys.isChecked(),
            "ignore_case_values": self.chk_ignore_case_values.isChecked(),
            "skip_empty": self.chk_skip_empty.isChecked(),
            "arrays_ignore_order": self.chk_arrays_ignore_order.isChecked(),
        }

        # Execute operations
        results = {}
        stats_lines = []

        try:
            if self.chk_intersection.isChecked():
                result = intersection(file_dicts, **options)
                results["intersection"] = result
                count = len(result.get("intersection", []))
                stats_lines.append(f"✓ Intersection: {count} items")

            if self.chk_union.isChecked():
                result = union(file_dicts, **options)
                results["union"] = result
                count = len(result.get("union", []))
                stats_lines.append(f"✓ Union: {count} items")

            if self.chk_difference.isChecked():
                result = difference(file_dicts, **options)
                results["difference"] = result
                count = len(result.get("difference", []))
                stats_lines.append(f"✓ Difference: {count} items")

            if self.chk_symmetric.isChecked():
                if len(file_dicts) != 2:
                    self.show_warning("Warning", "Symmetric difference only works with 2 files. Using first 2.")
                result = symmetric_difference(file_dicts[0], file_dicts[1], **options)
                results["symmetric_difference"] = result
                count = len(result.get("symmetric_difference", []))
                stats_lines.append(f"✓ Symmetric Difference: {count} items")

        except Exception as e:
            self.show_error("Error Executing Operations", str(e))
            return

        # Display results
        output_text = json.dumps(results, indent=2, ensure_ascii=False)
        self.txt_result.setText(output_text)

        # Display statistics
        self.lbl_stats.setText("\n".join(stats_lines))

        # Enable save button
        self.btn_save.setEnabled(True)

        self.show_info("Success", f"Operations completed!\n\n{chr(10).join(stats_lines)}")

    def _save_result(self):
        """Save results to file."""
        if not self.txt_result.toPlainText():
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "JSON Files (*.json)")

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.txt_result.toPlainText())
                self.show_info("Success", f"Results saved to:\n{file_path}")
            except Exception as e:
                self.show_error("Error Saving", str(e))

    def _clear_all(self):
        """Clear all inputs and results."""
        self.ed_file_a.clear()
        self.ed_file_b.clear()
        self.list_files.clear()
        self.txt_result.clear()
        self.lbl_stats.clear()
        self.btn_save.setEnabled(False)

        # Reset checkboxes
        self.chk_intersection.setChecked(False)
        self.chk_union.setChecked(False)
        self.chk_difference.setChecked(False)
        self.chk_symmetric.setChecked(False)
