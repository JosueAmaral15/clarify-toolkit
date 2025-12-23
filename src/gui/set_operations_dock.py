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
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Signal

from src.set_operations import difference, intersection, symmetric_difference, union
from src.i18n import tooltip_tr
from .base_dock import BaseDock
from ..history_manager import HistoryManager
from .history_dialog import HistoryDialog
from ..presets_manager import PresetsManager
from .presets_dialog import PresetsDialog


class SetOperationsDock(BaseDock):
    """Dock widget for JSON set operations."""
    
    # Signal emitted when user wants to store result in Calculator (v2.9.98)
    store_in_calculator_requested = Signal(object, str)  # (data, source)

    def __init__(self, parent=None):
        """Initialize Set Operations dock.
        
        Args:
            parent: Parent widget (optional)
        """
        self.file_paths: List[str] = []
        self.history_manager = HistoryManager()
        self.presets_manager = PresetsManager()
        super().__init__("JSON Set Operations", parent)

    def _setup_ui(self):
        """Setup user interface components."""
        # Create scroll area for all controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)  # No frame
        
        scroll_widget = QWidget()
        main_layout = QVBoxLayout(scroll_widget)

        # === File Selection Section ===
        file_group = QGroupBox("File Selection")
        file_layout = QGridLayout()

        # File A
        file_layout.addWidget(QLabel("File A:"), 0, 0)
        self.ed_file_a = QLineEdit()
        self.ed_file_a.setPlaceholderText("Select first JSON file...")
        self.ed_file_a.setToolTip(tooltip_tr("set_ops.file_a"))
        file_layout.addWidget(self.ed_file_a, 0, 1)
        self.btn_browse_a = QPushButton("Browse...")
        self.btn_browse_a.setMaximumWidth(100)
        self.btn_browse_a.setToolTip(tooltip_tr("set_ops.btn_browse_a"))
        file_layout.addWidget(self.btn_browse_a, 0, 2)

        # File B
        file_layout.addWidget(QLabel("File B:"), 1, 0)
        self.ed_file_b = QLineEdit()
        self.ed_file_b.setPlaceholderText("Select second JSON file...")
        self.ed_file_b.setToolTip(tooltip_tr("set_ops.file_b"))
        file_layout.addWidget(self.ed_file_b, 1, 1)
        self.btn_browse_b = QPushButton("Browse...")
        self.btn_browse_b.setMaximumWidth(100)
        self.btn_browse_b.setToolTip(tooltip_tr("set_ops.btn_browse_b"))
        file_layout.addWidget(self.btn_browse_b, 1, 2)

        # Multiple files checkbox
        self.chk_multiple = QCheckBox("Multiple files (pipeline processing)")
        self.chk_multiple.setToolTip(tooltip_tr("set_ops.chk_multiple"))
        file_layout.addWidget(self.chk_multiple, 2, 0, 1, 3)

        # File list (hidden by default)
        self.list_files = QListWidget()
        self.list_files.setMaximumHeight(100)
        self.list_files.setVisible(False)
        file_layout.addWidget(self.list_files, 3, 0, 1, 3)

        # Buttons for file list
        file_btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("+ Add File")
        self.btn_add_file.setToolTip(tooltip_tr("set_ops.btn_add_file"))
        self.btn_add_file.setVisible(False)
        self.btn_remove_file = QPushButton("- Remove Selected")
        self.btn_remove_file.setToolTip(tooltip_tr("set_ops.btn_remove_file"))
        self.btn_remove_file.setVisible(False)
        self.btn_clear_files = QPushButton("Clear All")
        self.btn_clear_files.setToolTip(tooltip_tr("set_ops.btn_clear_files"))
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
        self.chk_intersection.setToolTip(tooltip_tr("set_ops.intersection"))
        self.chk_union = QCheckBox("∪ Union")
        self.chk_union.setToolTip(tooltip_tr("set_ops.union"))
        self.chk_difference = QCheckBox("− Difference")
        self.chk_difference.setToolTip(tooltip_tr("set_ops.difference"))
        self.chk_symmetric = QCheckBox("⊕ Symmetric Difference (2 files only)")
        self.chk_symmetric.setToolTip(tooltip_tr("set_ops.symmetric"))

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
        self.radio_key_value.setToolTip(tooltip_tr("set_ops.radio_key_value"))
        self.radio_full_path = QRadioButton("Full path and values (dot notation)")
        self.radio_full_path.setToolTip(tooltip_tr("set_ops.radio_full_path"))
        self.radio_key_only = QRadioButton("Keys only (path)")
        self.radio_key_only.setToolTip(tooltip_tr("set_ops.radio_key_only"))

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
        self.chk_ignore_case_keys.setToolTip(tooltip_tr("set_ops.ignore_case_keys"))
        self.chk_ignore_case_values = QCheckBox("Ignore case in values")
        self.chk_ignore_case_values.setToolTip(tooltip_tr("set_ops.ignore_case_values"))
        self.chk_skip_empty = QCheckBox("Skip empty values")
        self.chk_skip_empty.setToolTip(tooltip_tr("set_ops.skip_empty"))
        self.chk_arrays_ignore_order = QCheckBox("Arrays: ignore order")
        self.chk_arrays_ignore_order.setToolTip(tooltip_tr("set_ops.arrays_ignore_order"))

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
        self.combo_output.setToolTip(tooltip_tr("set_ops.combo_output"))
        output_layout.addWidget(self.combo_output)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # === Action Buttons ===
        btn_layout = QHBoxLayout()
        self.btn_execute = QPushButton("Execute")
        self.btn_execute.setMinimumHeight(35)
        self.btn_execute.setToolTip(tooltip_tr("set_ops.btn_execute"))
        
        self.btn_save_preset = QPushButton("💾 Save Preset")
        self.btn_save_preset.setToolTip("Save current configuration as preset (v2.9.95)")
        
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setToolTip("Clear all inputs, file selections, and results")
        self.btn_save = QPushButton("Save Result")
        self.btn_save.setToolTip("Save operation results to JSON file (enabled after successful execution)")
        self.btn_save.setEnabled(False)
        self.btn_export = QPushButton("Export...")
        self.btn_export.setToolTip("Export results to CSV, Excel, YAML, or TOML (v2.9.93)")
        self.btn_export.setEnabled(False)
        
        self.btn_view_diff = QPushButton("🔍 View Diff")
        self.btn_view_diff.setToolTip("View side-by-side diff between files (v2.9.99)")
        self.btn_view_diff.setEnabled(False)
        
        self.btn_store_calc = QPushButton("🧮 Store in Calculator")
        self.btn_store_calc.setToolTip("Store result in Calculator memory slot (v2.9.98)")
        self.btn_store_calc.setEnabled(False)
        
        self.btn_history = QPushButton("📜 History")
        self.btn_history.setToolTip("View operation history (v2.9.94)")
        
        self.btn_presets = QPushButton("📋 Presets")
        self.btn_presets.setToolTip("Manage operation presets (v2.9.95)")

        btn_layout.addWidget(self.btn_execute)
        btn_layout.addWidget(self.btn_save_preset)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_view_diff)
        btn_layout.addWidget(self.btn_store_calc)
        btn_layout.addWidget(self.btn_history)
        btn_layout.addWidget(self.btn_presets)
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
        
        # === Comparative Statistics Dashboard (v2.9.96) ===
        self.txt_statistics = QTextEdit()
        self.txt_statistics.setReadOnly(True)
        self.txt_statistics.setMaximumHeight(300)
        self.txt_statistics.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10pt;")
        self.txt_statistics.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.txt_statistics)

        main_layout.addStretch()
        
        # Set scroll widget and add to main layout
        scroll.setWidget(scroll_widget)
        self.layout.addWidget(scroll)

    def _connect_signals(self):
        """Connect UI signals to slots."""
        self.btn_browse_a.clicked.connect(lambda: self._browse_file("a"))
        self.btn_browse_b.clicked.connect(lambda: self._browse_file("b"))
        self.chk_multiple.toggled.connect(self._toggle_multiple_files)
        self.btn_add_file.clicked.connect(self._add_file)
        self.btn_remove_file.clicked.connect(self._remove_file)
        self.btn_clear_files.clicked.connect(self._clear_files)
        self.btn_execute.clicked.connect(self._execute)
        self.btn_save_preset.clicked.connect(self._save_current_as_preset)
        self.btn_clear.clicked.connect(self._clear_all)
        self.btn_save.clicked.connect(self._save_result)
        self.btn_export.clicked.connect(self._export_result)
        self.btn_view_diff.clicked.connect(self._view_diff)
        self.btn_store_calc.clicked.connect(self._store_in_calculator)
        self.btn_history.clicked.connect(self._show_history)
        self.btn_presets.clicked.connect(self._show_presets)

    def _browse_file(self, target: str):
        """Browse for JSON file.
        
        Args:
            target: Target field ('a' or 'b')
        """
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
        """Add file to multi-file list via file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Add JSON File", "", "JSON Files (*.json);;All Files (*)")

        if file_path:
            self.list_files.addItem(file_path)

    def _remove_file(self):
        """Remove selected file from multi-file list."""
        current_row = self.list_files.currentRow()
        if current_row >= 0:
            self.list_files.takeItem(current_row)

    def _clear_files(self):
        """Clear file list."""
        self.list_files.clear()

    def _get_files(self) -> List[str]:
        """Get list of files to process.
        
        Returns:
            List of file paths from either 2-file mode (File A/B) or multi-file list.
        """
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
            from src.set_operations import validate_file_path

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
            
            # Store original data for diff viewer (v2.9.99)
            self.file_a_data = file_dicts[0] if len(file_dicts) > 0 else {}
            self.file_b_data = file_dicts[1] if len(file_dicts) > 1 else {}
            
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

        # Store result data for export
        self.result_data = results

        # Save to history (v2.9.94)
        try:
            # Determine primary operation (first checked)
            operation_type = "⊕"  # Default symmetric diff
            if self.chk_intersection.isChecked():
                operation_type = "∩"
            elif self.chk_union.isChecked():
                operation_type = "∪"
            elif self.chk_difference.isChecked():
                operation_type = "−"
            
            self.history_manager.add_operation(
                operation_type=operation_type,
                file1=files[0],
                file2=files[1] if len(files) > 1 else files[0],
                comparison_mode=comparison_mode,
                result_count=sum(len(r.get(list(r.keys())[0], [])) for r in results.values()),
                result_data=results
            )
        except Exception as e:
            print(f"Warning: Failed to save operation to history: {e}")

        # Calculate comparative statistics (v2.9.96)
        try:
            from ..statistics_manager import StatisticsManager
            
            # Calculate stats for each file
            file1_stats = StatisticsManager.calculate_statistics(file_dicts[0])
            file2_stats = StatisticsManager.calculate_statistics(file_dicts[1] if len(file_dicts) > 1 else file_dicts[0])
            
            # Calculate stats for result
            result_count = sum(len(r.get(list(r.keys())[0], [])) for r in results.values())
            result_stats = StatisticsManager.calculate_statistics(results)
            
            # Calculate overlap percentage
            overlap_pct = StatisticsManager.calculate_overlap_percentage(file1_stats, file2_stats, result_count)
            
            # Format comparative statistics
            stats_text = StatisticsManager.format_comparative_statistics(
                file1_stats, file2_stats, result_stats, overlap_pct
            )
            
            # Display in statistics area
            self.txt_statistics.setText(stats_text)
            self.txt_statistics.setVisible(True)
            
        except Exception as e:
            print(f"Warning: Failed to calculate statistics: {e}")
            self.txt_statistics.setVisible(False)

        # Enable save, export, diff viewer, and calculator buttons
        self.btn_save.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.btn_view_diff.setEnabled(True)
        self.btn_store_calc.setEnabled(True)

        self.show_info("Success", f"Operations completed!\n\n{chr(10).join(stats_lines)}")

    def _save_result(self):
        """Save operation results to JSON file.
        
        Opens save dialog and writes current result from output area to file.
        Shows success message with file path.
        """
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
    
    def _export_result(self):
        """Export results to multiple formats (v2.9.93)."""
        if not hasattr(self, 'result_data') or not self.result_data:
            self.show_warning("No Data", "No results to export. Please execute an operation first.")
            return
        
        from pathlib import Path
        from PySide6.QtWidgets import QFileDialog
        from ..export_manager import ExportManager
        
        # Format filter
        filter_str = "CSV Files (*.csv);;Excel Files (*.xlsx);;YAML Files (*.yaml);;TOML Files (*.toml);;JSON Files (*.json)"
        
        # Open save dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            filter_str
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Determine format from filter
            format_map = {
                "CSV Files (*.csv)": "csv",
                "Excel Files (*.xlsx)": "xlsx",
                "YAML Files (*.yaml)": "yaml",
                "TOML Files (*.toml)": "toml",
                "JSON Files (*.json)": "json"
            }
            
            export_format = format_map.get(selected_filter, "json")
            
            # Ensure correct extension
            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(f".{export_format}")
            
            # Export
            ExportManager.export(
                data=self.result_data,
                output_path=path,
                format=export_format,
                flatten=True,  # Flatten for CSV/Excel/TOML
                include_metadata=True  # Add timestamp + operation type
            )
            
            self.show_info("Export Successful", f"Results exported to:\n{path}")
        
        except ImportError as e:
            self.show_error("Export Failed", f"Missing dependency:\n{e}\n\nInstall with: pip install openpyxl tomli-w")
        except Exception as e:
            self.show_error("Export Failed", str(e))
    
    def _store_in_calculator(self):
        """Store result in Calculator memory slot (v2.9.98)."""
        if not hasattr(self, 'result_data') or not self.result_data:
            self.show_warning("No Data", "No results to store. Please execute an operation first.")
            return
        
        # Determine operation source description
        operation = "Unknown"
        if self.rad_intersection.isChecked():
            operation = "Intersection (∩)"
        elif self.rad_union.isChecked():
            operation = "Union (∪)"
        elif self.rad_difference.isChecked():
            operation = "Difference (−)"
        elif self.rad_symmetric_diff.isChecked():
            operation = "Symmetric Difference (⊕)"
        
        # Get file names for source description
        file_a = os.path.basename(self.ed_file_a.text()) if self.ed_file_a.text() else "File A"
        file_b = os.path.basename(self.ed_file_b.text()) if self.ed_file_b.text() else "File B"
        
        source = f"Set Operations: {operation} ({file_a}, {file_b})"
        
        # Emit signal for Calculator to handle
        self.store_in_calculator_requested.emit(self.result_data, source)
        
        self.show_info("Stored", f"Result sent to Calculator\nSource: {source}")
    
    def _view_diff(self):
        """Open diff viewer dialog for side-by-side comparison (v2.9.99)."""
        if not hasattr(self, 'file_a_data') or not hasattr(self, 'file_b_data'):
            self.show_warning("No Data", "No input files to compare. Execute operation first.")
            return
        
        from .diff_viewer_dialog import DiffViewerDialog
        
        # Get file names
        file_a_name = os.path.basename(self.ed_file_a.text()) if self.ed_file_a.text() else "File A"
        file_b_name = os.path.basename(self.ed_file_b.text()) if self.ed_file_b.text() else "File B"
        
        # Get current comparison mode
        comparison_mode = "key_value"
        if self.radio_full_path.isChecked():
            comparison_mode = "full_path_value"
        elif self.radio_key_only.isChecked():
            comparison_mode = "key_only"
        
        dialog = DiffViewerDialog(
            self.file_a_data,
            self.file_b_data,
            file_a_name,
            file_b_name,
            comparison_mode,
            self
        )
        dialog.exec()


    def _clear_all(self):
        """Clear all inputs and results."""
        self.ed_file_a.clear()
        self.ed_file_b.clear()
        self.list_files.clear()
        self.txt_result.clear()
        self.lbl_stats.clear()
        self.txt_statistics.clear()
        self.txt_statistics.setVisible(False)
        self.btn_save.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_view_diff.setEnabled(False)
        self.btn_store_calc.setEnabled(False)

        # Reset checkboxes
        self.chk_intersection.setChecked(False)
        self.chk_union.setChecked(False)
        self.chk_difference.setChecked(False)
        self.chk_symmetric.setChecked(False)

    def _show_history(self):
        """Show operation history dialog (v2.9.94)."""
        dialog = HistoryDialog(self.history_manager, self)
        
        # Connect re-execute signal
        dialog.re_execute_requested.connect(self._re_execute_from_history)
        
        dialog.exec()
    
    def _re_execute_from_history(self, entry: dict):
        """
        Re-execute operation from history.
        
        Args:
            entry: History entry with operation data
        """
        try:
            # Set files
            self.ed_file_a.setText(entry["file1"])
            self.ed_file_b.setText(entry["file2"])
            
            # Set comparison mode
            if entry["comparison_mode"] == "full_path_value":
                self.radio_full_path.setChecked(True)
            elif entry["comparison_mode"] == "key_only":
                self.radio_key_only.setChecked(True)
            else:
                self.radio_key_value.setChecked(True)
            
            # Set operation type
            op_map = {
                "∩": self.chk_intersection,
                "∪": self.chk_union,
                "−": self.chk_difference,
                "⊕": self.chk_symmetric
            }
            
            # Uncheck all first
            for chk in op_map.values():
                chk.setChecked(False)
            
            # Check the one from history
            if entry["operation_type"] in op_map:
                op_map[entry["operation_type"]].setChecked(True)
            
            # Execute
            self._execute()
            
        except Exception as e:
            self.show_error("Re-execute Error", f"Failed to re-execute operation:\n{e}")
    
    def _show_presets(self):
        """Show operation presets dialog (v2.9.95)."""
        dialog = PresetsDialog(self.presets_manager, self)
        
        # Connect preset load signal
        dialog.preset_load_requested.connect(self._load_preset)
        
        dialog.exec()
    
    def _load_preset(self, preset: dict):
        """
        Load preset into current configuration.
        
        Args:
            preset: Preset data dictionary
        """
        try:
            # Set comparison mode
            if preset.get("comparison_mode") == "full_path_value":
                self.radio_full_path.setChecked(True)
            elif preset.get("comparison_mode") == "key_only":
                self.radio_key_only.setChecked(True)
            else:
                self.radio_key_value.setChecked(True)
            
            # Set operation type
            op_map = {
                "∩": self.chk_intersection,
                "∪": self.chk_union,
                "−": self.chk_difference,
                "⊕": self.chk_symmetric
            }
            
            # Uncheck all first
            for chk in op_map.values():
                chk.setChecked(False)
            
            # Check the one from preset
            if preset.get("operation_type") in op_map:
                op_map[preset["operation_type"]].setChecked(True)
            
            # Set options
            self.chk_ignore_case_keys.setChecked(preset.get("ignore_case_keys", False))
            self.chk_ignore_case_values.setChecked(preset.get("ignore_case_values", False))
            self.chk_skip_empty.setChecked(preset.get("skip_empty", True))
            self.chk_arrays_ignore_order.setChecked(preset.get("arrays_ignore_order", False))
            
            # Load favorite files if any
            favorite_files = preset.get("favorite_files", [])
            if favorite_files and len(favorite_files) >= 2:
                self.ed_file_a.setText(favorite_files[0])
                self.ed_file_b.setText(favorite_files[1])
            
            self.show_info("Preset Loaded", f"Loaded preset: {preset.get('name', 'Unnamed')}")
            
        except Exception as e:
            self.show_error("Load Preset Error", f"Failed to load preset:\n{e}")
    
    def _save_current_as_preset(self):
        """Save current configuration as a new preset."""
        from PySide6.QtWidgets import QInputDialog
        
        # Solicita nome do preset
        name, ok = QInputDialog.getText(
            self,
            "Save Preset",
            "Enter preset name:"
        )
        
        if not ok or not name.strip():
            return
        
        name = name.strip()
        
        # Verifica se nome já existe
        if self.presets_manager.get_preset(name):
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Preset Exists",
                f"A preset named '{name}' already exists.\nOverwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        try:
            # Determina operação selecionada
            operation_type = "⊕"  # Default
            if self.chk_intersection.isChecked():
                operation_type = "∩"
            elif self.chk_union.isChecked():
                operation_type = "∪"
            elif self.chk_difference.isChecked():
                operation_type = "−"
            
            # Determina comparison mode
            comparison_mode = "key_value"
            if self.radio_full_path.isChecked():
                comparison_mode = "full_path_value"
            elif self.radio_key_only.isChecked():
                comparison_mode = "key_only"
            
            # Coleta arquivos atuais (favorite files)
            favorite_files = []
            if self.ed_file_a.text():
                favorite_files.append(self.ed_file_a.text())
            if self.ed_file_b.text():
                favorite_files.append(self.ed_file_b.text())
            
            # Cria preset
            preset = self.presets_manager.create_preset_from_current(
                name=name,
                operation_type=operation_type,
                comparison_mode=comparison_mode,
                ignore_case_keys=self.chk_ignore_case_keys.isChecked(),
                ignore_case_values=self.chk_ignore_case_values.isChecked(),
                skip_empty=self.chk_skip_empty.isChecked(),
                arrays_ignore_order=self.chk_arrays_ignore_order.isChecked(),
                favorite_files=favorite_files
            )
            
            # Salva
            success = self.presets_manager.save_preset(preset)
            
            if success:
                self.show_info("Preset Saved", f"Preset '{name}' saved successfully!")
            else:
                self.show_error("Save Error", "Failed to save preset.")
        
        except Exception as e:
            self.show_error("Save Preset Error", f"Failed to save preset:\n{e}")


