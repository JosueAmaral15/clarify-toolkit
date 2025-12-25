#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Rewriter Dock - Modular implementation
Rewrites JSON/TS files with options to join keys, eliminate duplicates, and format output.
"""

from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.accessibility_manager import AccessibilityManager
from src.core.filters import Condition
from src.core import cli_dedupe
from src.i18n.translator import tooltip_tr, tr
from src.utils.advanced_conditions import apply_conditions_to_files, get_conditions_from_ui
from src.utils import format_removal_statistics
from .base_dock import BaseDock

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


class JsonRewriterDock(BaseDock):
    """
    Dock widget for JSON rewriter functionality.
    Rewrites JSON/TS files with deduplication and formatting options.

    Features:
    - Input/output file selection
    - From TS/JS option (preserve TypeScript format)
    - Emit export default option
    - Join keys option
    - Eliminate duplicates option
    - No blank lines option
    - Configurable indentation
    """

    def __init__(self, parent: QWidgetType | None = None):
        super().__init__(tr("json_rewriter.title"), parent)
        self._load_preferences()
        self._apply_accessibility()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()

    def _create_widgets(self) -> None:
        """Create all widgets for the rewriter dock."""
        # Input file section
        self.lbl_in = QLabel(tr("json_rewriter.lbl_in"))
        self.ed_in = QLineEdit()
        self.btn_in = QPushButton(tr("json_rewriter.btn_open"))

        # Output file section
        self.lbl_out = QLabel(tr("json_rewriter.lbl_out"))
        self.ed_out = QLineEdit()
        self.btn_out = QPushButton(tr("json_rewriter.btn_save_as"))

        # Options checkboxes
        self.chk_from_ts = QCheckBox(tr("json_rewriter.chk_from_ts"))
        self.chk_ts_out = QCheckBox(tr("json_rewriter.chk_ts_out"))
        self.chk_join = QCheckBox(tr("json_rewriter.chk_join"))
        self.chk_elim = QCheckBox(tr("json_rewriter.chk_elim"))
        self.chk_nlb = QCheckBox(tr("json_rewriter.chk_nlb"))
        self.chk_exclude_numeric = QCheckBox(tr("json_rewriter.chk_exclude_numeric"))
        self.chk_skip_empty = QCheckBox(tr("json_rewriter.chk_skip_empty"))
        self.chk_avoid_dup_child = QCheckBox(tr("json_rewriter.chk_avoid_dup_child"))
        self.chk_normalize_escaping = QCheckBox(tr("json_rewriter.chk_normalize_escaping"))
        self.chk_convert_arrays = QCheckBox(tr("json_rewriter.chk_convert_arrays"))
        self.chk_skip_no_siblings = QCheckBox(tr("json_rewriter.chk_skip_no_siblings"))

        # Task #52 - Remove duplicate objects
        self.chk_remove_dup_objects = QCheckBox(tr("json_rewriter.chk_remove_dup_objects"))
        self.chk_include_dup_arrays = QCheckBox(tr("json_rewriter.chk_include_dup_arrays"))
        self.lbl_dup_threshold = QLabel(tr("json_rewriter.lbl_dup_threshold"))
        self.spin_dup_threshold = QSpinBox()
        self.spin_dup_threshold.setRange(50, 100)
        self.spin_dup_threshold.setValue(100)
        self.spin_dup_threshold.setSuffix("%")
        self.combo_dup_mode = QComboBox()
        self.combo_dup_mode.addItems([tr("json_rewriter.combo_dup_remove"), tr("json_rewriter.combo_dup_ref")])

        # Task #23 - Update orphaned references
        self.chk_update_refs = QCheckBox(tr("json_rewriter.chk_update_refs"))
        self.ed_project_dir = QLineEdit()
        self.btn_project_browse = QPushButton(tr("json_rewriter.btn_browse"))
        self.chk_ref_backup = QCheckBox(tr("json_rewriter.chk_ref_backup"))
        self.chk_ref_backup.setChecked(True)

        self.chk_remove_dup_consecutive = QCheckBox(tr("json_rewriter.chk_remove_dup_consecutive"))
        self.chk_remove_dup_all = QCheckBox(tr("json_rewriter.chk_remove_dup_all"))
        self.chk_enforce_case = QCheckBox(tr("json_rewriter.chk_enforce_case"))
        self.chk_enforce_case.setChecked(True)  # Applied automatically
        self.combo_case_style = QComboBox()
        self.combo_case_style.addItems(["camelCase", "PascalCase", "snake_case", "kebab-case"])
        self.combo_case_style.setCurrentIndex(0)  # Default: camelCase
        self.chk_validate_case = QCheckBox(tr("json_rewriter.chk_validate_case"))
        self.chk_validate_case.setChecked(False)  # Optional validation
        self.chk_is_file = QCheckBox(tr("json_rewriter.chk_is_file"))
        self.chk_is_file.setChecked(True)

        # Sprint B Feature #1: Advanced Filters
        self.btn_advanced_filters = QPushButton(tr("json_rewriter.btn_advanced_filters"))
        self.chk_apply_all_types = QCheckBox(tr("json_rewriter.chk_apply_all_types"))
        self.chk_apply_all_types.setChecked(False)
        self.advanced_conditions: list[Condition] = []  # Storage for configured conditions
        self.advanced_filters_enabled = False  # Whether filters are active

        # Sprint A Feature: Reference Resolver (v2.9.29)
        self.lbl_ref_mode = QLabel(tr("json_rewriter.lbl_ref_mode"))
        self.radio_delete_dups = QRadioButton(tr("json_rewriter.radio_delete_dups"))
        self.radio_delete_dups.setChecked(True)  # Default mode
        self.radio_use_refs = QRadioButton(tr("json_rewriter.radio_use_refs"))
        self.chk_resolve_refs = QCheckBox(tr("json_rewriter.chk_resolve_refs"))
        self.chk_resolve_refs.setChecked(False)

        # Sprint B Feature #4: Reference Format Configuration (v2.9.30)
        self.btn_configure_format = QPushButton(tr("json_rewriter.btn_configure_format"))

        # Indent spinner
        self.lbl_indent = QLabel(tr("json_rewriter.lbl_indent"))
        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(-1, 16)
        self.spin_indent.setValue(2)

        # Action button
        self.btn_run = QPushButton(tr("json_rewriter.btn_run"))

    def _create_layout(self) -> None:
        """Arrange widgets in the dock."""
        # Clear the existing VBoxLayout and replace with QGridLayout
        g = QGridLayout()

        # Remove the old layout and set the new one
        old_layout = self.main_widget.layout()
        if old_layout:
            QWidget().setLayout(old_layout)  # Take ownership to delete
        self.main_widget.setLayout(g)

        # Row 0: Input file
        g.addWidget(self.lbl_in, 0, 0)
        g.addWidget(self.ed_in, 0, 1, 1, 3)
        g.addWidget(self.btn_in, 0, 4)

        # Row 1: Output file
        g.addWidget(self.lbl_out, 1, 0)
        g.addWidget(self.ed_out, 1, 1, 1, 3)
        g.addWidget(self.btn_out, 1, 4)

        # Row 2: Options checkboxes (line 1)
        g.addWidget(self.chk_from_ts, 2, 0)
        g.addWidget(self.chk_ts_out, 2, 1)
        g.addWidget(self.chk_join, 2, 2)
        g.addWidget(self.chk_elim, 2, 3)
        g.addWidget(self.chk_nlb, 2, 4)

        # Row 3: Options checkboxes (line 2)
        g.addWidget(self.chk_exclude_numeric, 3, 0)
        g.addWidget(self.chk_skip_empty, 3, 1)
        g.addWidget(self.chk_avoid_dup_child, 3, 2)
        g.addWidget(self.chk_normalize_escaping, 3, 3)
        g.addWidget(self.chk_is_file, 3, 4)

        # Row 4: Options checkboxes (line 3) - Array operations
        g.addWidget(self.chk_convert_arrays, 4, 0, 1, 2)
        g.addWidget(self.chk_remove_dup_consecutive, 4, 2, 1, 1)
        g.addWidget(self.chk_remove_dup_all, 4, 3, 1, 1)
        g.addWidget(self.chk_skip_no_siblings, 4, 4, 1, 1)

        # Row 5: Update references (Task #23)
        g.addWidget(self.chk_update_refs, 5, 0, 1, 1)
        g.addWidget(self.ed_project_dir, 5, 1, 1, 2)
        g.addWidget(self.btn_project_browse, 5, 3)
        g.addWidget(self.chk_ref_backup, 5, 4)

        # Row 6: Enforce consistent case
        g.addWidget(self.chk_enforce_case, 6, 0, 1, 2)
        g.addWidget(QLabel(tr("json_rewriter.lbl_case_style")), 6, 2)
        g.addWidget(self.combo_case_style, 6, 3)
        g.addWidget(self.chk_validate_case, 6, 4)

        # Row 7: Remove duplicate objects (Task #52)
        g.addWidget(self.chk_remove_dup_objects, 7, 0, 1, 1)
        g.addWidget(self.chk_include_dup_arrays, 7, 1)
        g.addWidget(self.lbl_dup_threshold, 7, 2)
        g.addWidget(self.spin_dup_threshold, 7, 3)
        g.addWidget(self.combo_dup_mode, 7, 4)

        # Row 8: Advanced Filters (Sprint B Feature #1)
        g.addWidget(self.btn_advanced_filters, 8, 0, 1, 2)
        g.addWidget(self.chk_apply_all_types, 8, 2, 1, 2)

        # Row 9: Reference Resolver (Sprint A v2.9.29)
        g.addWidget(self.lbl_ref_mode, 9, 0)
        g.addWidget(self.radio_delete_dups, 9, 1, 1, 2)
        g.addWidget(self.radio_use_refs, 9, 3, 1, 2)

        # Row 10: Resolve references checkbox + Configure Format button (Sprint B Feature #4)
        g.addWidget(self.chk_resolve_refs, 10, 0, 1, 2)
        g.addWidget(self.btn_configure_format, 10, 2, 1, 2)

        # Row 11: Indent and run button
        g.addWidget(self.lbl_indent, 11, 0)
        g.addWidget(self.spin_indent, 11, 1)
        g.addWidget(self.btn_run, 11, 4)

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_in.clicked.connect(self._open_in)
        self.btn_out.clicked.connect(self._open_out)
        self.btn_project_browse.clicked.connect(self._browse_project_dir)
        self.btn_run.clicked.connect(self._rewrite)
        self.btn_advanced_filters.clicked.connect(self._open_advanced_filters_dialog)
        self.btn_configure_format.clicked.connect(self._open_format_config_dialog)

        # Sprint A v2.9.29: Save preferences when reference resolver options change
        self.radio_delete_dups.toggled.connect(self._save_preferences)
        self.radio_use_refs.toggled.connect(self._save_preferences)
        self.chk_resolve_refs.toggled.connect(self._save_preferences)

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips to all widgets (v2.9.74)."""
        self.ed_in.setToolTip(tooltip_tr("json_rewriter.ed_in"))
        self.btn_in.setToolTip(tooltip_tr("json_rewriter.btn_in"))
        self.ed_out.setToolTip(tooltip_tr("json_rewriter.ed_out"))
        self.btn_out.setToolTip(tooltip_tr("json_rewriter.btn_out"))
        self.chk_from_ts.setToolTip(tooltip_tr("json_rewriter.chk_from_ts"))
        self.chk_ts_out.setToolTip(tooltip_tr("json_rewriter.chk_ts_out"))
        self.chk_join.setToolTip(tooltip_tr("json_rewriter.chk_join"))
        self.chk_elim.setToolTip(tooltip_tr("json_rewriter.chk_elim"))
        self.chk_nlb.setToolTip(tooltip_tr("json_rewriter.chk_nlb"))
        self.chk_exclude_numeric.setToolTip(tooltip_tr("json_rewriter.chk_exclude_numeric"))
        self.chk_skip_empty.setToolTip(tooltip_tr("json_rewriter.chk_skip_empty"))
        self.chk_avoid_dup_child.setToolTip(tooltip_tr("json_rewriter.chk_avoid_dup_child"))
        self.chk_normalize_escaping.setToolTip(tooltip_tr("json_rewriter.chk_normalize_escaping"))
        self.chk_convert_arrays.setToolTip(tooltip_tr("json_rewriter.chk_convert_arrays"))
        self.chk_skip_no_siblings.setToolTip(tooltip_tr("json_rewriter.chk_skip_no_siblings"))
        self.chk_remove_dup_objects.setToolTip(tooltip_tr("json_rewriter.chk_remove_dup_objects"))
        self.chk_include_dup_arrays.setToolTip(tooltip_tr("json_rewriter.chk_include_dup_arrays"))
        self.spin_dup_threshold.setToolTip(tooltip_tr("json_rewriter.spin_dup_threshold"))
        self.combo_dup_mode.setToolTip(tooltip_tr("json_rewriter.combo_dup_mode"))
        self.chk_update_refs.setToolTip(tooltip_tr("json_rewriter.chk_update_refs"))
        self.ed_project_dir.setToolTip(tooltip_tr("json_rewriter.ed_project_dir"))
        self.btn_project_browse.setToolTip(tooltip_tr("json_rewriter.btn_project_browse"))
        self.chk_ref_backup.setToolTip(tooltip_tr("json_rewriter.chk_ref_backup"))
        self.chk_remove_dup_consecutive.setToolTip(tooltip_tr("json_rewriter.chk_remove_dup_consecutive"))
        self.chk_remove_dup_all.setToolTip(tooltip_tr("json_rewriter.chk_remove_dup_all"))
        self.chk_enforce_case.setToolTip(tooltip_tr("json_rewriter.chk_enforce_case"))
        self.combo_case_style.setToolTip(tooltip_tr("json_rewriter.combo_case_style"))
        self.chk_validate_case.setToolTip(tooltip_tr("json_rewriter.chk_validate_case"))
        self.chk_is_file.setToolTip(tooltip_tr("json_rewriter.chk_is_file"))
        self.btn_advanced_filters.setToolTip(tooltip_tr("json_rewriter.btn_advanced_filters"))
        self.chk_apply_all_types.setToolTip(tooltip_tr("json_rewriter.chk_apply_all_types"))
        self.radio_delete_dups.setToolTip(tooltip_tr("json_rewriter.radio_delete_dups"))
        self.radio_use_refs.setToolTip(tooltip_tr("json_rewriter.radio_use_refs"))
        self.chk_resolve_refs.setToolTip(tooltip_tr("json_rewriter.chk_resolve_refs"))
        self.btn_configure_format.setToolTip(tooltip_tr("json_rewriter.btn_configure_format"))
        self.spin_indent.setToolTip(tooltip_tr("json_rewriter.spin_indent"))
        self.btn_run.setToolTip(tooltip_tr("json_rewriter.btn_run"))

    # UI Helper Methods

    def _open_in(self) -> None:
        """Browse for input file."""
        f, _ = QFileDialog.getOpenFileName(
            self, "Select input", "", "JSON/TS/JS (*.json *.ts *.tsx *.js *.jsx);;All (*)"
        )
        if f:
            self.ed_in.setText(f)

    def _open_out(self) -> None:
        """Browse for output file."""
        f, _ = QFileDialog.getSaveFileName(self, "Save output", "", "All (*)")
        if f:
            self.ed_out.setText(f)

    def _browse_project_dir(self) -> None:
        """Browse for project directory (Task #23)."""
        d = QFileDialog.getExistingDirectory(self, "Select project directory", "", QFileDialog.Option.ShowDirsOnly)
        if d:
            self.ed_project_dir.setText(d)

    def _open_format_config_dialog(self) -> None:
        """Open dialog to configure reference format (Sprint B Feature #4 - v2.9.30)."""
        settings = QSettings("Clarify", "JsonRewriter")

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Reference Format Configuration")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Active options group
        active_group = QGroupBox("Format Options")
        active_layout = QVBoxLayout()

        # Format dropdown
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Reference format:"))
        combo_format = QComboBox()
        combo_format.addItems(["$ref: (Default)", "#/ (JSON Pointer)", "@ (Compact)"])
        current_format = settings.value("reference_format", "$ref")
        if current_format == "$ref":
            combo_format.setCurrentIndex(0)
        elif current_format == "#/":
            combo_format.setCurrentIndex(1)
        elif current_format == "@":
            combo_format.setCurrentIndex(2)
        format_layout.addWidget(combo_format)
        active_layout.addLayout(format_layout)

        # Checkboxes
        chk_line_numbers = QCheckBox("Include line numbers")
        chk_line_numbers.setChecked(settings.value("include_line_numbers_ref", True, type=bool))
        chk_line_numbers.setToolTip("Append :line_number to references (e.g., $ref:path:123)")
        active_layout.addWidget(chk_line_numbers)

        chk_relative = QCheckBox("Use relative paths")
        chk_relative.setChecked(settings.value("use_relative_paths", False, type=bool))
        chk_relative.setToolTip("Remove 'root.' prefix from paths (e.g., users.admin instead of root.users.admin)")
        active_layout.addWidget(chk_relative)

        # Preview label
        preview_label = QLabel()
        preview_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; font-family: monospace;"
        )
        preview_label.setWordWrap(True)

        def update_preview():
            fmt = ["$ref", "#/", "@"][combo_format.currentIndex()]
            path = "users.admin" if chk_relative.isChecked() else "root.users.admin"
            line = ":123" if chk_line_numbers.isChecked() else ""
            example = f"{fmt}:{path}{line}" if fmt == "$ref" else f"{fmt}{path}{line}"
            preview_label.setText(f"Example: <b>{example}</b>")

        combo_format.currentIndexChanged.connect(update_preview)
        chk_line_numbers.toggled.connect(update_preview)
        chk_relative.toggled.connect(update_preview)
        update_preview()

        active_layout.addWidget(QLabel("Preview:"))
        active_layout.addWidget(preview_label)
        active_group.setLayout(active_layout)
        layout.addWidget(active_group)

        # Future features group (grayed out)
        future_group = QGroupBox("Cross-File References (Coming Soon)")
        future_group.setEnabled(False)
        future_layout = QVBoxLayout()
        future_layout.addWidget(QCheckBox("Enable cross-file references"))
        future_layout.addWidget(QCheckBox("Use absolute file paths"))
        future_group.setLayout(future_layout)
        layout.addWidget(future_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )

        def reset_defaults():
            combo_format.setCurrentIndex(0)
            chk_line_numbers.setChecked(True)
            chk_relative.setChecked(False)
            update_preview()

        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(reset_defaults)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog and save if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            format_map = {0: "$ref", 1: "#/", 2: "@"}
            settings.setValue("reference_format", format_map[combo_format.currentIndex()])
            settings.setValue("include_line_numbers_ref", chk_line_numbers.isChecked())
            settings.setValue("use_relative_paths", chk_relative.isChecked())

    def _open_advanced_filters_dialog(self) -> None:
        """Open dialog to configure advanced file filters (Sprint B Feature #1)."""
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced File Filters")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Info label
        info = QLabel(
            "Configure filters to apply BEFORE processing files.\nFilters use AND logic (all conditions must match)."
        )
        layout.addWidget(info)

        # Create 3 condition rows (same UI as AI Processor)
        cond_group = QGroupBox("Filter Conditions")
        cond_layout = QGridLayout()

        # Headers
        cond_layout.addWidget(QLabel("Field"), 0, 0)
        cond_layout.addWidget(QLabel("Operator"), 0, 1)
        cond_layout.addWidget(QLabel("Value"), 0, 2)
        cond_layout.addWidget(QLabel("Scope"), 0, 3)
        cond_layout.addWidget(QLabel("Case"), 0, 4)
        cond_layout.addWidget(QLabel("Regex"), 0, 5)

        # Create condition rows
        cond_rows = []
        for row in range(3):
            combo_field = QComboBox()
            combo_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])

            combo_op = QComboBox()
            combo_op.addItems(
                [
                    "",
                    "contains",
                    "not contains",
                    "equals",
                    "not equals",
                    "starts with",
                    "ends with",
                    ">",
                    "<",
                    ">=",
                    "<=",
                ]
            )

            ed_value = QLineEdit()
            ed_value.setPlaceholderText("Filter value")

            combo_scope = QComboBox()
            combo_scope.addItems(
                ["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag", "hierarchical"]
            )

            chk_case = QCheckBox()
            chk_case.setChecked(True)

            chk_regex = QCheckBox()

            grid_row = row + 1
            cond_layout.addWidget(combo_field, grid_row, 0)
            cond_layout.addWidget(combo_op, grid_row, 1)
            cond_layout.addWidget(ed_value, grid_row, 2)
            cond_layout.addWidget(combo_scope, grid_row, 3)
            cond_layout.addWidget(chk_case, grid_row, 4)
            cond_layout.addWidget(chk_regex, grid_row, 5)

            cond_rows.append((combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex))

        cond_group.setLayout(cond_layout)
        layout.addWidget(cond_group)

        # Load existing conditions into UI
        for i, cond in enumerate(self.advanced_conditions[:3]):  # Max 3 rows
            if i < len(cond_rows):
                combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex = cond_rows[i]
                combo_field.setCurrentText(cond.field)
                combo_op.setCurrentText(cond.operator)
                ed_value.setText(cond.value)
                combo_scope.setCurrentText(cond.scope_type)
                chk_case.setChecked(cond.case_sensitive)
                chk_regex.setChecked(cond.use_regex)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog and save conditions if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.advanced_conditions = get_conditions_from_ui(cond_rows)
            self.advanced_filters_enabled = len(self.advanced_conditions) > 0

            # Feedback
            if self.advanced_filters_enabled:
                QMessageBox.information(
                    self,
                    "Filters Configured",
                    f"✅ {len(self.advanced_conditions)} filter(s) configured.\n\n"
                    "Filters will be applied BEFORE processing files.",
                )
            else:
                QMessageBox.information(
                    self, "Filters Cleared", "❌ No filters configured. All files will be processed."
                )

    # Core Processing

    def _rewrite(self) -> None:
        """Execute rewrite operation on selected file."""
        if not self.ed_in.text().strip():
            QMessageBox.warning(self, "Missing", "Choose an input file.")
            return

        # Case validation dialog (if enabled)
        if self.chk_enforce_case.isChecked() and self.chk_validate_case.isChecked():
            try:
                # Read and parse input file
                from src import rewriter as rw

                with open(self.ed_in.text().strip(), "r", encoding="utf-8") as f:
                    text = f.read()

                # Parse based on format
                if self.chk_from_ts.isChecked():
                    obj = rw.ts_process_full_preserving(text)
                else:
                    obj = rw.parse_json_preserving_duplicates_text(text)

                # Show validation dialog
                from .case_validator_dialog import show_case_validator

                accepted, obj_converted, warnings = show_case_validator(obj, self)

                # User cancelled
                if not accepted:
                    QMessageBox.information(self, "Cancelled", "Case conversion cancelled by user.")
                    return

                # User accepted - we'll use the converted object
                # But first, temporarily disable enforce_case to avoid double conversion
                # (We'll write the already-converted object)
                self.chk_enforce_case.setChecked(False)

                # Write the converted object to a temporary state
                # and let cli_dedupe handle the rest
                # Actually, we need to serialize it back to text first
                if self.chk_ts_out.isChecked():
                    temp_text = rw.dump_ts_node(obj_converted, indent=self.spin_indent.value())
                    if not self.chk_nlb.isChecked():
                        temp_text = rw.collapse_blank_lines(temp_text)
                else:
                    temp_text = rw.dump_ts_obj(obj_converted, indent=self.spin_indent.value())

                # Write to output
                out_path = self.ed_out.text().strip() or self.ed_in.text().strip()
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(temp_text)

                QMessageBox.information(self, "Done", f"Rewriter finished with {len(warnings)} case conversions.")

                # Re-enable enforce_case for next run
                self.chk_enforce_case.setChecked(True)
                return

            except Exception as e:
                QMessageBox.critical(self, "Validation Error", f"Failed to validate case: {e}")
                return

        # Build argparse namespace with all options
        ns = argparse.Namespace(
            input=self.ed_in.text().strip(),
            output=self.ed_out.text().strip() or None,
            indent=self.spin_indent.value(),
            from_ts=self.chk_from_ts.isChecked(),
            ts_out=self.chk_ts_out.isChecked(),
            join_keys=self.chk_join.isChecked(),
            eliminate_duplicates=self.chk_elim.isChecked(),
            no_line_break=self.chk_nlb.isChecked(),
            exclude_numeric=self.chk_exclude_numeric.isChecked(),
            skip_empty=self.chk_skip_empty.isChecked(),
            avoid_duplicate_child_keys=self.chk_avoid_dup_child.isChecked(),
            normalize_escaping=self.chk_normalize_escaping.isChecked(),
            convert_arrays_to_objects=self.chk_convert_arrays.isChecked(),
            remove_dup_consecutive=self.chk_remove_dup_consecutive.isChecked(),
            remove_dup_all=self.chk_remove_dup_all.isChecked(),
            skip_no_siblings=self.chk_skip_no_siblings.isChecked(),
            enforce_case=self.chk_enforce_case.isChecked(),
            case_style=self.combo_case_style.currentText()
            .lower()
            .replace("-", "")
            .replace("case", ""),  # 'camelCase' -> 'camel'
            is_file=self.chk_is_file.isChecked(),
            remove_duplicate_objects=self.chk_remove_dup_objects.isChecked(),
            duplicate_threshold=self.spin_dup_threshold.value(),
            include_duplicate_arrays=self.chk_include_dup_arrays.isChecked(),
            duplicate_mode="reference" if self.combo_dup_mode.currentIndex() == 1 else "remove",
            # Sprint A v2.9.29: Reference Resolver
            resolve_references=self.chk_resolve_refs.isChecked(),
            use_references=self.radio_use_refs.isChecked(),
            # Sprint B Feature #4 v2.9.30: Reference Format Configuration
            reference_format=QSettings("Clarify", "JsonRewriter").value("reference_format", "$ref", type=str),
            include_line_numbers_ref=QSettings("Clarify", "JsonRewriter").value(
                "include_line_numbers_ref", True, type=bool
            ),
            use_relative_paths=QSettings("Clarify", "JsonRewriter").value("use_relative_paths", False, type=bool),
        )

        # Execute rewrite (Sprint B Feature #1: pass advanced conditions, Sprint B Feature #3: get detailed stats)
        try:
            output_text, substitution_map, removal_stats, detailed_stats = cli_dedupe(
                ns,
                advanced_conditions=self.advanced_conditions if self.advanced_filters_enabled else None,
                apply_all_types=self.chk_apply_all_types.isChecked(),
            )

            # Task #23: Update orphaned references in project (if enabled)
            if self.chk_update_refs.isChecked() and substitution_map:
                project_dir = self.ed_project_dir.text().strip()

                if not project_dir:
                    QMessageBox.warning(self, "Missing", "Choose a project directory to update references.")
                    return

                if not os.path.isdir(project_dir):
                    QMessageBox.warning(self, "Invalid", f"Project directory does not exist: {project_dir}")
                    return

                # Show preview dialog with substitutions
                from src import rewriter as rw

                results = rw.update_references_in_project(
                    project_dir, substitution_map, create_backup=self.chk_ref_backup.isChecked()
                )

                if results:
                    # Show summary
                    total_subs = sum(results.values())
                    file_count = len(results)
                    msg = f"Updated {total_subs} references in {file_count} files:\n\n"
                    for filepath, count in list(results.items())[:10]:
                        msg += f"  - {os.path.basename(filepath)}: {count} changes\n"
                    if file_count > 10:
                        msg += f"  ... and {file_count - 10} more files\n"
                    QMessageBox.information(self, "References Updated", msg)
                else:
                    QMessageBox.information(self, "No Changes", "No orphaned references found in project.")

            # Task v2.9.22: Format and display removal statistics (Q3: MessageBox only)
            stats_msg = format_removal_statistics(removal_stats)
            if stats_msg:
                QMessageBox.information(self, "Done", f"Rewriter finished.\n\n{stats_msg}")

                # Sprint B Feature #3 (v2.9.31): Show detailed statistics dialog if there are stats
                if detailed_stats:
                    from .statistics_dialog import StatisticsDialog

                    # Collect reference stats
                    ref_stats = {
                        "created": removal_stats.get("references_created", 0),
                        "resolved": removal_stats.get("references_resolved", 0),
                        "invalid": removal_stats.get("references_invalid", 0),
                        "deleted": removal_stats.get("deleted", 0),
                        "kept": removal_stats.get("kept", 0),
                    }
                    dialog = StatisticsDialog(detailed_stats, ref_stats, self)
                    dialog.exec()
            else:
                # Q5-C: Special message if nothing was removed
                QMessageBox.information(self, "Done", "Rewriter finished.\n\nℹ️ No items were removed by any operation.")

            # Save preferences after successful execution
            self._save_preferences()
        except Exception as e:
            import traceback

            QMessageBox.critical(self, "Error", f"{str(e)}\n\n{traceback.format_exc()}")

    def _load_preferences(self) -> None:
        """Load preferences from QSettings (Task #52 + Sprint B Feature #1)."""
        settings = QSettings("Clarify", "JsonRewriter")

        # Load duplicate objects settings
        if hasattr(self, "chk_remove_dup_objects"):
            self.chk_remove_dup_objects.setChecked(settings.value("remove_duplicate_objects", False, type=bool))
            self.chk_include_dup_arrays.setChecked(settings.value("include_duplicate_arrays", False, type=bool))
            self.spin_dup_threshold.setValue(settings.value("duplicate_threshold", 100, type=int))
            self.combo_dup_mode.setCurrentIndex(settings.value("duplicate_mode_index", 0, type=int))

        # Load reference resolver settings (Sprint A v2.9.29)
        if hasattr(self, "radio_use_refs"):
            use_refs = settings.value("use_references", False, type=bool)
            if use_refs:
                self.radio_use_refs.setChecked(True)
            else:
                self.radio_delete_dups.setChecked(True)

            self.chk_resolve_refs.setChecked(settings.value("resolve_references", False, type=bool))

        # Load reference format settings (Sprint B Feature #4 v2.9.30)
        # Note: These are loaded but applied in _rewrite() when calling create_references()
        # Default values: reference_format="$ref", include_line_numbers_ref=True, use_relative_paths=False

        # Load advanced filters settings (Sprint B Feature #1)
        if hasattr(self, "chk_apply_all_types"):
            self.chk_apply_all_types.setChecked(settings.value("advanced_filters_apply_all_types", False, type=bool))
            self.advanced_filters_enabled = settings.value("advanced_filters_enabled", False, type=bool)

            # Load serialized conditions (JSON format)
            import json

            conditions_json = settings.value("advanced_filters_conditions", "[]", type=str)
            try:
                conditions_data = json.loads(conditions_json)
                self.advanced_conditions = [
                    Condition(
                        field=c["field"],
                        operator=c["operator"],
                        value=c["value"],
                        scope_type=c.get("scope_type", "none"),
                        scope_value=c.get("scope_value", ""),
                        case_sensitive=c.get("case_sensitive", True),
                        whole_word=c.get("whole_word", False),
                        use_regex=c.get("use_regex", False),
                    )
                    for c in conditions_data
                ]
            except (json.JSONDecodeError, KeyError):
                self.advanced_conditions = []

    def _save_preferences(self) -> None:
        """Save preferences to QSettings (Task #52 + Sprint B Feature #1)."""
        settings = QSettings("Clarify", "JsonRewriter")

        # Save duplicate objects settings
        settings.setValue("remove_duplicate_objects", self.chk_remove_dup_objects.isChecked())
        settings.setValue("include_duplicate_arrays", self.chk_include_dup_arrays.isChecked())
        settings.setValue("duplicate_threshold", self.spin_dup_threshold.value())
        settings.setValue("duplicate_mode_index", self.combo_dup_mode.currentIndex())

        # Save reference resolver settings (Sprint A v2.9.29)
        settings.setValue("use_references", self.radio_use_refs.isChecked())
        settings.setValue("resolve_references", self.chk_resolve_refs.isChecked())

        # Save advanced filters settings (Sprint B Feature #1)
        settings.setValue("advanced_filters_apply_all_types", self.chk_apply_all_types.isChecked())
        settings.setValue("advanced_filters_enabled", self.advanced_filters_enabled)

        # Serialize conditions to JSON
        import json

        conditions_data = [
            {
                "field": c.field,
                "operator": c.operator,
                "value": c.value,
                "scope_type": c.scope_type,
                "scope_value": c.scope_value,
                "case_sensitive": c.case_sensitive,
                "whole_word": c.whole_word,
                "use_regex": c.use_regex,
            }
            for c in self.advanced_conditions
        ]
        settings.setValue("advanced_filters_conditions", json.dumps(conditions_data))

    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._rewrite()

    def _apply_accessibility(self) -> None:
        """Apply accessibility labels to all widgets (v2.9.37)."""
        # Input/Output file section
        AccessibilityManager.set_accessible_widget(
            self.lbl_in, "JSON Rewriter - Label - Input File", "Label indicating input file path field"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_in, "JSON Rewriter - Input - Input File Path", "JSON or TypeScript file to rewrite"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_in, "JSON Rewriter - Button - Browse Input File", "Open file browser to select input file"
        )
        AccessibilityManager.set_accessible_widget(
            self.lbl_out, "JSON Rewriter - Label - Output File", "Label indicating output file path field"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_out,
            "JSON Rewriter - Input - Output File Path",
            "Optional output file path (defaults to overwriting input file)",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_out,
            "JSON Rewriter - Button - Browse Output File",
            "Open file browser to select output file location",
        )

        # Format options
        AccessibilityManager.set_accessible_widget(
            self.chk_from_ts,
            "JSON Rewriter - Checkbox - From TypeScript/JavaScript",
            "Parse input as TypeScript/JavaScript object literal (preserves file format)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_ts_out,
            "JSON Rewriter - Checkbox - Emit Export Default",
            "Add 'export default ...' wrapper to output (TypeScript/JavaScript format)",
        )

        # Core transformation options
        AccessibilityManager.set_accessible_widget(
            self.chk_join,
            "JSON Rewriter - Checkbox - Join Keys",
            "Merge nested object keys into flat structure (e.g., user.name)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_elim,
            "JSON Rewriter - Checkbox - Eliminate Duplicates",
            "Remove duplicate values and consolidate keys",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_nlb,
            "JSON Rewriter - Checkbox - No Blank Lines",
            "Remove blank lines from output for compact formatting",
        )

        # Advanced filtering options
        AccessibilityManager.set_accessible_widget(
            self.chk_exclude_numeric,
            "JSON Rewriter - Checkbox - Exclude Numeric Keys",
            "Skip keys with numeric names (e.g., '0', '123')",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_skip_empty,
            "JSON Rewriter - Checkbox - Skip Empty Values",
            "Remove key-value pairs with empty values (empty strings, null, undefined)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_avoid_dup_child,
            "JSON Rewriter - Checkbox - Avoid Duplicate Child Keys",
            "Prevent duplicate keys in nested child objects",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_normalize_escaping,
            "JSON Rewriter - Checkbox - Normalize Escaping",
            "Standardize escape sequences (e.g., \\n, \\t) across file",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_convert_arrays,
            "JSON Rewriter - Checkbox - Convert Arrays to Objects",
            "Transform arrays into objects with indexed keys",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_skip_no_siblings,
            "JSON Rewriter - Checkbox - Skip Keys Without Siblings",
            "Remove object keys that have no sibling keys",
        )

        # Duplicate objects section
        AccessibilityManager.set_accessible_widget(
            self.chk_remove_dup_objects,
            "JSON Rewriter - Checkbox - Remove Duplicate Objects",
            "Detect and remove duplicate object structures",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_include_dup_arrays,
            "JSON Rewriter - Checkbox - Include Arrays in Duplicate Detection",
            "Also check arrays for duplicates (not just objects)",
        )
        AccessibilityManager.set_accessible_widget(
            self.lbl_dup_threshold,
            "JSON Rewriter - Label - Similarity Threshold",
            "Label indicating similarity percentage threshold",
        )
        AccessibilityManager.set_accessible_widget(
            self.spin_dup_threshold,
            "JSON Rewriter - SpinBox - Similarity Threshold Percentage",
            "Percentage threshold for detecting similar objects (0-100)",
        )
        AccessibilityManager.set_accessible_widget(
            self.combo_dup_mode,
            "JSON Rewriter - ComboBox - Duplicate Detection Mode",
            "Algorithm for detecting duplicates (exact, fuzzy, semantic)",
        )

        # Reference update section
        AccessibilityManager.set_accessible_widget(
            self.chk_update_refs,
            "JSON Rewriter - Checkbox - Update References in Project",
            "Update all references in project files when keys are renamed",
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_project_dir,
            "JSON Rewriter - Input - Project Directory",
            "Root directory of project to scan for references",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_project_browse,
            "JSON Rewriter - Button - Browse Project Directory",
            "Open folder browser to select project directory",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_ref_backup,
            "JSON Rewriter - Checkbox - Create Backups",
            "Create backup files (.bak) before updating references",
        )

        # Array duplicate options
        AccessibilityManager.set_accessible_widget(
            self.chk_remove_dup_consecutive,
            "JSON Rewriter - Checkbox - Remove Consecutive Array Duplicates",
            "Remove only consecutive duplicate elements in arrays",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_remove_dup_all,
            "JSON Rewriter - Checkbox - Remove All Array Duplicates",
            "Remove all duplicate elements in arrays (keeps first occurrence)",
        )

        # Case enforcement section
        AccessibilityManager.set_accessible_widget(
            self.chk_enforce_case,
            "JSON Rewriter - Checkbox - Enforce Consistent Case",
            "Convert all keys to consistent naming convention",
        )
        AccessibilityManager.set_accessible_widget(
            self.combo_case_style,
            "JSON Rewriter - ComboBox - Case Style",
            "Naming convention style (camelCase, snake_case, PascalCase, etc.)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_validate_case,
            "JSON Rewriter - Checkbox - Validate Case Before Applying",
            "Show preview and warnings before converting case style",
        )

        # File type filter
        AccessibilityManager.set_accessible_widget(
            self.chk_is_file,
            "JSON Rewriter - Checkbox - Is File",
            "Treat input path as single file (unchecked for directory)",
        )

        # Advanced filters
        AccessibilityManager.set_accessible_widget(
            self.btn_advanced_filters,
            "JSON Rewriter - Button - Advanced Filters",
            "Open advanced filtering dialog with custom conditions",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_apply_all_types,
            "JSON Rewriter - Checkbox - Apply to All File Types",
            "Apply filters to all file types (not just JSON files)",
        )

        # Reference mode section
        AccessibilityManager.set_accessible_widget(
            self.lbl_ref_mode,
            "JSON Rewriter - Label - Duplicate Handling Mode",
            "Label indicating duplicate handling mode selection",
        )
        AccessibilityManager.set_accessible_widget(
            self.radio_delete_dups,
            "JSON Rewriter - RadioButton - Delete Duplicates",
            "Delete duplicate objects permanently",
        )
        AccessibilityManager.set_accessible_widget(
            self.radio_use_refs,
            "JSON Rewriter - RadioButton - Use References",
            "Replace duplicates with $ref pointers (JSON Schema standard)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_resolve_refs,
            "JSON Rewriter - Checkbox - Resolve Existing References",
            "Expand existing $ref pointers back to full objects",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_configure_format,
            "JSON Rewriter - Button - Configure Reference Format",
            "Configure reference format settings ($ref, JSONPath, custom)",
        )

        # Indentation section
        AccessibilityManager.set_accessible_widget(
            self.lbl_indent, "JSON Rewriter - Label - Indentation", "Label indicating indentation setting"
        )
        AccessibilityManager.set_accessible_widget(
            self.spin_indent,
            "JSON Rewriter - SpinBox - Indentation Spaces",
            "Number of spaces for indentation (0 or negative for compact mode)",
        )

        # Action button
        AccessibilityManager.set_accessible_widget(
            self.btn_run, "JSON Rewriter - Button - Run Rewrite", "Execute JSON rewrite operation with selected options"
        )
