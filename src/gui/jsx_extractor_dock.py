#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSX Parameter Extractor Dock

Extracts parameters and attributes from JSX/TSX files and generates hierarchical JSON.
Based on add/main.py functionality.

Features:
- Path selection (file or directory) with Browse button
- JSX or Generic mode parsing
- Attribute extraction (key="value") or tag content extraction
- Hierarchical path building with customizable options
- Output: text paths and JSON structure

Author: Josué Amaral
Date: 2025-12-02
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


from __future__ import annotations

import os
from typing import Optional

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QWidget,
)

from src.i18n.translator import tooltip_tr, tr
from .base_dock import BaseDock


class JSXExtractorDock(BaseDock):
    """
    Dock widget for JSX/TSX parameter and attribute extraction.

    Scans files or directories for JSX/TSX files and extracts parameters/attributes
    building hierarchical JSON structures based on component tree.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__("JSX Parameter Extractor", parent)

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()  # v2.9.70
        self._connect_signals()

    def _validate_path_security(self, path: str, operation: str = "access") -> Optional[str]:  # pylint: disable=unused-argument  # For future use
        """
        Validate path for security (path traversal prevention).

        Args:
            path: Path to validate
            operation: Type of operation ("access" or "save")

        Returns:
            Validated real path if valid, None if invalid
        """
        try:
            real_path = os.path.realpath(path)
            home_dir = os.path.expanduser("~")
            cwd = os.getcwd()

            # Check if path is within allowed directories
            if not (real_path.startswith(home_dir) or real_path.startswith(cwd)):
                QMessageBox.warning(
                    self,
                    tr("jsx.msg_security_error_title"),
                    tr("jsx.msg_security_access_denied").format(real_path),
                )
                return None

            return real_path
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, tr("jsx.msg_error_title"), tr("jsx.msg_invalid_path").format(e))
            return None

    # pylint: disable=attribute-defined-outside-init  # Pattern: widgets created in helper method
    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Path section
        self.path_label = QLabel(tr("jsx.lbl_path"))
        self.ed_path = QLineEdit()
        self.ed_path.setPlaceholderText(tr("jsx.placeholder_path"))

        self.btn_browse = QPushButton(tr("jsx.btn_browse"))

        self.is_file = QCheckBox(tr("jsx.chk_is_file"))

        # Param and mode section
        self.param_label = QLabel(tr("jsx.lbl_param"))
        self.ed_param = QLineEdit("")
        self.ed_param.setPlaceholderText(tr("jsx.placeholder_param"))

        self.chk_is_attribute_mode = QCheckBox(tr("jsx.chk_is_attribute"))
        self.chk_is_attribute_mode.setChecked(True)  # Default: attribute mode

        self.mode_label = QLabel(tr("jsx.lbl_mode"))
        self.cb_mode = QComboBox()
        self.cb_mode.addItems([tr("combo.mode_jsx"), tr("combo.mode_generic")])

        # Generic delimiters (only for generic mode)
        self.start_label = QLabel(tr("jsx.lbl_start_delim"))
        self.ed_start = QLineEdit("<.*?>")
        self.ed_start.setEnabled(False)

        self.end_label = QLabel(tr("jsx.lbl_end_delim"))
        self.ed_end = QLineEdit("</.*?>")
        self.ed_end.setEnabled(False)

        # Extensions
        self.ext_label = QLabel(tr("jsx.lbl_extensions"))
        self.ed_ext = QLineEdit(".tsx .jsx .js .ts")

        # Options group
        self.options_group = QGroupBox(tr("jsx.group_options"))

        self.chk_include_key = QCheckBox(tr("jsx.chk_include_key"))
        self.chk_include_key.setChecked(True)

        self.chk_include_value = QCheckBox(tr("jsx.chk_include_value"))
        self.chk_include_value.setChecked(False)

        self.chk_no_standard = QCheckBox(tr("jsx.chk_no_standard"))
        self.chk_no_standard.setChecked(False)

        self.chk_only_strings = QCheckBox(tr("jsx.chk_only_strings"))
        self.chk_only_strings.setChecked(False)

        self.chk_include_quotation_marks = QCheckBox(tr("jsx.chk_include_quotes"))
        self.chk_include_quotation_marks.setChecked(False)

        # Normalization options
        self.norm_group = QGroupBox(tr("jsx.group_normalization"))

        self.case_label = QLabel(tr("jsx.lbl_case_style"))
        self.cb_case = QComboBox()
        self.cb_case.addItems([
            tr("combo.case_snake"), tr("combo.case_camel"),
            tr("combo.case_pascal"), tr("combo.case_kebab")
        ])

        self.chk_upper = QCheckBox(tr("jsx.chk_uppercase"))
        self.chk_upper.setChecked(False)

        self.limit_label = QLabel(tr("jsx.lbl_limit"))
        self.ed_limit = QLineEdit("all")
        self.ed_limit.setPlaceholderText(tr("jsx.placeholder_limit"))

        self.chk_avoid_cut = QCheckBox(tr("jsx.chk_avoid_cut"))
        self.chk_avoid_cut.setChecked(False)

        # JSON options
        self.json_group = QGroupBox(tr("jsx.group_json"))

        self.indent_label = QLabel(tr("jsx.lbl_indentation"))
        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(0, 8)
        self.spin_indent.setValue(2)

        # Avoid keys (filter)
        self.avoid_label = QLabel(tr("jsx.lbl_avoid_keys"))
        self.avoid_keys = QLineEdit("")
        self.avoid_keys.setPlaceholderText(tr("jsx.placeholder_avoid_keys"))

        self.avoid_keys_mode_label = QLabel(tr("jsx.lbl_avoid_mode"))
        self.cb_avoid_mode = QComboBox()
        self.cb_avoid_mode.addItems([tr("combo.avoid_contains"), tr("combo.avoid_equals")])

        # Action buttons
        self.btn_run = QPushButton(tr("jsx.btn_extract"))

        self.btn_save = QPushButton(tr("jsx.btn_save"))

        self.btn_copy = QPushButton(tr("jsx.btn_copy"))

        self.btn_clear = QPushButton(tr("jsx.btn_clear"))

        # Output tabs
        self.tabs = QTabWidget()

        self.out_paths = QPlainTextEdit()
        self.out_paths.setReadOnly(True)
        self.out_paths.setPlaceholderText(tr("jsx.placeholder_paths"))
        font = QFont("Courier New", 10)
        self.out_paths.setFont(font)

        self.out_json = QPlainTextEdit()
        self.out_json.setReadOnly(True)
        self.out_json.setPlaceholderText(tr("jsx.placeholder_json"))
        self.out_json.setFont(font)

        self.tabs.addTab(self.out_paths, tr("jsx_extractor.tab_paths"))
        self.tabs.addTab(self.out_json, tr("jsx_extractor.tab_json"))

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")

    def _create_layout(self) -> None:
        """Create and arrange layout."""
        # Path row
        row_path = QHBoxLayout()
        row_path.addWidget(self.path_label)
        row_path.addWidget(self.ed_path, 1)
        row_path.addWidget(self.btn_browse)
        row_path.addWidget(self.is_file)

        # Param and mode row
        row_param = QHBoxLayout()
        row_param.addWidget(self.param_label)
        row_param.addWidget(self.ed_param, 1)
        row_param.addWidget(self.chk_is_attribute_mode)
        row_param.addWidget(self.mode_label)
        row_param.addWidget(self.cb_mode)

        # Generic delimiters row
        row_delim = QHBoxLayout()
        row_delim.addWidget(self.start_label)
        row_delim.addWidget(self.ed_start, 1)
        row_delim.addWidget(self.end_label)
        row_delim.addWidget(self.ed_end, 1)

        # Extensions row
        row_ext = QHBoxLayout()
        row_ext.addWidget(self.ext_label)
        row_ext.addWidget(self.ed_ext, 1)

        # Options group layout
        options_layout = QGridLayout()
        options_layout.addWidget(self.chk_include_key, 0, 0)
        options_layout.addWidget(self.chk_include_value, 0, 1)
        options_layout.addWidget(self.chk_no_standard, 1, 0)
        options_layout.addWidget(self.chk_only_strings, 1, 1)
        options_layout.addWidget(self.chk_include_quotation_marks, 2, 0)
        self.options_group.setLayout(options_layout)

        # Normalization group layout
        norm_layout = QGridLayout()
        norm_layout.addWidget(self.case_label, 0, 0)
        norm_layout.addWidget(self.cb_case, 0, 1)
        norm_layout.addWidget(self.chk_upper, 0, 2)
        norm_layout.addWidget(self.limit_label, 1, 0)
        norm_layout.addWidget(self.ed_limit, 1, 1)
        norm_layout.addWidget(self.chk_avoid_cut, 1, 2)
        self.norm_group.setLayout(norm_layout)

        # JSON group layout
        json_layout = QHBoxLayout()
        json_layout.addWidget(self.indent_label)
        json_layout.addWidget(self.spin_indent)
        json_layout.addStretch()
        self.json_group.setLayout(json_layout)

        # Avoid keys row
        row_avoid = QHBoxLayout()
        row_avoid.addWidget(self.avoid_label)
        row_avoid.addWidget(self.avoid_keys, 1)
        row_avoid.addWidget(self.avoid_keys_mode_label)
        row_avoid.addWidget(self.cb_avoid_mode)

        # Action buttons row
        row_buttons = QHBoxLayout()
        row_buttons.addWidget(self.btn_run)
        row_buttons.addWidget(self.btn_save)
        row_buttons.addWidget(self.btn_copy)
        row_buttons.addWidget(self.btn_clear)
        row_buttons.addStretch()

        # Main layout (fix v2.9.40.1 - use self.layout from BaseDock)
        self.layout.addLayout(row_path)
        self.layout.addLayout(row_param)
        self.layout.addLayout(row_delim)
        self.layout.addLayout(row_ext)
        self.layout.addWidget(self.options_group)
        self.layout.addWidget(self.norm_group)
        self.layout.addWidget(self.json_group)
        self.layout.addLayout(row_avoid)
        self.layout.addLayout(row_buttons)
        self.layout.addWidget(self.tabs, 1)
        self.layout.addWidget(self.status_label)

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.btn_browse.clicked.connect(self._on_browse)
        self.btn_run.clicked.connect(self._on_run)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_copy.clicked.connect(self._on_copy)
        self.btn_clear.clicked.connect(self._on_clear)
        self.cb_mode.currentTextChanged.connect(self._on_mode_changed)

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips (v2.9.70)."""
        # Path section
        self.ed_path.setToolTip(tooltip_tr("jsx_extractor.ed_path"))
        self.btn_browse.setToolTip(tooltip_tr("jsx_extractor.btn_browse"))
        self.is_file.setToolTip(tooltip_tr("jsx_extractor.is_file"))

        # Param and mode section
        self.ed_param.setToolTip(tooltip_tr("jsx_extractor.ed_param"))
        self.chk_is_attribute_mode.setToolTip(tooltip_tr("jsx_extractor.chk_is_attribute_mode"))
        self.cb_mode.setToolTip(tooltip_tr("jsx_extractor.cb_mode"))

        # Generic delimiters
        self.ed_start.setToolTip(tooltip_tr("jsx_extractor.ed_start"))
        self.ed_end.setToolTip(tooltip_tr("jsx_extractor.ed_end"))

        # Extensions
        self.ed_ext.setToolTip(tooltip_tr("jsx_extractor.ed_ext"))

        # Extraction options
        self.chk_include_key.setToolTip(tooltip_tr("jsx_extractor.chk_include_key"))
        self.chk_include_value.setToolTip(tooltip_tr("jsx_extractor.chk_include_value"))
        self.chk_no_standard.setToolTip(tooltip_tr("jsx_extractor.chk_no_standard"))
        self.chk_only_strings.setToolTip(tooltip_tr("jsx_extractor.chk_only_strings"))
        self.chk_include_quotation_marks.setToolTip(tooltip_tr("jsx_extractor.chk_include_quotation_marks"))

        # Normalization options
        self.cb_case.setToolTip(tooltip_tr("jsx_extractor.cb_case"))
        self.chk_upper.setToolTip(tooltip_tr("jsx_extractor.chk_upper"))
        self.ed_limit.setToolTip(tooltip_tr("jsx_extractor.ed_limit"))
        self.chk_avoid_cut.setToolTip(tooltip_tr("jsx_extractor.chk_avoid_cut"))

        # JSON options
        self.spin_indent.setToolTip(tooltip_tr("jsx_extractor.spin_indent"))

        # Avoid keys
        self.avoid_keys.setToolTip(tooltip_tr("jsx_extractor.avoid_keys"))
        self.cb_avoid_mode.setToolTip(tooltip_tr("jsx_extractor.cb_avoid_mode"))

        # Action buttons
        self.btn_run.setToolTip(tooltip_tr("jsx_extractor.btn_run"))
        self.btn_save.setToolTip(tooltip_tr("jsx_extractor.btn_save"))
        self.btn_copy.setToolTip(tooltip_tr("jsx_extractor.btn_copy"))
        self.btn_clear.setToolTip(tooltip_tr("jsx_extractor.btn_clear"))

        # Output tabs
        self.out_paths.setToolTip(tooltip_tr("jsx_extractor.out_paths"))
        self.out_json.setToolTip(tooltip_tr("jsx_extractor.out_json"))

        # Status
        self.status_label.setToolTip(tooltip_tr("jsx_extractor.status_label"))

    def _on_mode_changed(self, mode: str) -> None:
        """Enable/disable generic delimiter fields based on mode."""
        is_generic = mode == "generic"
        self.ed_start.setEnabled(is_generic)
        self.ed_end.setEnabled(is_generic)
        self.start_label.setEnabled(is_generic)
        self.end_label.setEnabled(is_generic)

    def _on_browse(self) -> None:
        """Open file/directory browser."""
        path = self.ed_path.text().strip()

        if not path or not os.path.exists(path):
            # Ask to choose either file or dir
            if self.is_file.isChecked():
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Select file", "", "JSX/TSX Files (*.jsx *.tsx *.js *.ts);;All Files (*)"
                )
                if file_path:
                    self.ed_path.setText(file_path)
                else:
                    dir_path = QFileDialog.getExistingDirectory(self, "Select directory")
                    if dir_path:
                        self.ed_path.setText(dir_path)
            else:
                dir_path = QFileDialog.getExistingDirectory(self, "Select directory")
                if dir_path:
                    self.ed_path.setText(dir_path)
        else:
            # Path exists, allow reselect
            if os.path.isfile(path):
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Select file", os.path.dirname(path), "JSX/TSX Files (*.jsx *.tsx *.js *.ts);;All Files (*)"
                )
                if file_path:
                    self.ed_path.setText(file_path)
            else:
                dir_path = QFileDialog.getExistingDirectory(self, "Select directory", path)
                if dir_path:
                    self.ed_path.setText(dir_path)

    def _on_run(self) -> None:
        """Execute extraction."""
        try:
            path = self.ed_path.text().strip()
            if not path:
                QMessageBox.warning(self, tr("jsx.msg_error_title"), tr("jsx.msg_provide_path"))
                return

            # Security: Validate path
            validated_path = self._validate_path_security(path, "access")
            if not validated_path:
                return

            # Check if path exists
            if not os.path.exists(validated_path):
                QMessageBox.warning(self, tr("jsx.msg_error_title"), tr("jsx.msg_path_not_exist").format(path))
                return

            path = validated_path

            # Collect parameters
            param = self.ed_param.text().strip() or ""
            mode = self.cb_mode.currentText()
            start = self.ed_start.text().strip() or None
            end = self.ed_end.text().strip() or None
            include_key = self.chk_include_key.isChecked()
            include_value = self.chk_include_value.isChecked()
            no_std = self.chk_no_standard.isChecked()
            with_quot_marks = self.chk_include_quotation_marks.isChecked()
            only_strings = self.chk_only_strings.isChecked()
            case_style = self.cb_case.currentText()
            upper = self.chk_upper.isChecked()
            limit = self.ed_limit.text().strip() or "all"
            avoid_keys = self.avoid_keys.text().strip()
            avoid_cut = self.chk_avoid_cut.isChecked()
            indent = self.spin_indent.value()
            is_attribute_mode = self.chk_is_attribute_mode.isChecked()
            exts = [e.strip() for e in self.ed_ext.text().split() if e.strip()]
            avoid_mode = self.cb_avoid_mode.currentText()

            self.status_label.setText(tr("jsx.status_extracting"))
            self.status_label.setStyleSheet("color: blue; font-style: italic;")

            # Import Extractor here to avoid circular imports
            from src.extractors import Extractor  # pylint: disable=import-outside-toplevel  # Lazy import

            # Create Extractor instance with all options
            extractor = Extractor(
                param=param,
                mode=mode,
                avoid_keys=avoid_keys,
                avoid_keys_parameter=avoid_mode,
                include_key=include_key,
                include_value=include_value,
                no_standard=no_std,
                convert_to_json=True,  # Always generate JSON for GUI
                with_quotation_marks=with_quot_marks,
                indentation=indent,
                case_style=case_style,
                limit=limit,
                avoid_cut=avoid_cut,
                to_upper=upper,
                only_strings=only_strings,
                is_attribute_mode=is_attribute_mode,
                start_regex=start,
                end_regex=end,
                root_alias=None,
                file_extensions=exts,
            )

            # Run extraction
            text_result, json_result = extractor.run(path)

            # Display results
            self.out_paths.setPlainText(text_result)
            self.out_json.setPlainText(json_result or "{}")

            self.status_label.setText(tr("jsx.status_completed"))
            self.status_label.setStyleSheet("color: green; font-style: italic;")

        except Exception as e:  # pylint: disable=broad-exception-caught  # UI robustness
            QMessageBox.critical(self, tr("jsx.msg_extraction_error_title"), str(e))
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-style: italic;")

    def _on_save(self) -> None:
        """Save outputs to files."""
        try:
            text = self.out_paths.toPlainText()
            js = self.out_json.toPlainText()

            if not text and not js:
                QMessageBox.information(self, tr("jsx.msg_nothing_to_save_title"), tr("jsx.msg_nothing_to_save_msg"))
                return

            # Save paths
            if text:
                fp, _ = QFileDialog.getSaveFileName(self, "Save paths text", "paths.txt", "Text Files (*.txt)")
                if fp:
                    # Security: Validate file extension
                    if not fp.lower().endswith(".txt"):
                        QMessageBox.warning(self, tr("jsx.msg_security_error_title"), tr("jsx.msg_txt_only"))
                        return

                    # Security: Validate path
                    validated_fp = self._validate_path_security(fp, "save")
                    if not validated_fp:
                        return

                    try:
                        with open(validated_fp, "w", encoding="utf-8") as f:
                            f.write(text)
                    except (IOError, OSError, PermissionError) as e:
                        QMessageBox.critical(self, tr("jsx.msg_save_error_title"), f"Failed to save paths: {e}")
                        return

            # Save JSON
            if js:
                fj, _ = QFileDialog.getSaveFileName(self, "Save JSON", "result.json", "JSON Files (*.json)")
                if fj:
                    # Security: Validate file extension
                    if not fj.lower().endswith(".json"):
                        QMessageBox.warning(self, tr("jsx.msg_security_error_title"), tr("jsx.msg_json_only"))
                        return

                    # Security: Validate path
                    validated_fj = self._validate_path_security(fj, "save")
                    if not validated_fj:
                        return

                    try:
                        with open(validated_fj, "w", encoding="utf-8") as f:
                            f.write(js)
                    except (IOError, OSError, PermissionError) as e:
                        QMessageBox.critical(self, tr("jsx.msg_save_error_title"), f"Failed to save JSON: {e}")
                        return

            QMessageBox.information(self, tr("jsx.msg_saved_title"), tr("jsx.msg_saved_success"))
        except Exception as e:  # pylint: disable=broad-exception-caught  # UI robustness
            QMessageBox.critical(self, tr("jsx.msg_save_error_title"), str(e))

    def _on_copy(self) -> None:
        """Copy current tab content to clipboard."""
        from PySide6.QtWidgets import QApplication  # pylint: disable=import-outside-toplevel  # Lazy import

        current = self.tabs.currentWidget()
        text = current.toPlainText()

        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText(tr("jsx.status_copied"))
            self.status_label.setStyleSheet("color: green; font-style: italic;")
        else:
            QMessageBox.information(self, tr("jsx.msg_nothing_to_copy_title"), tr("jsx.msg_nothing_to_copy_msg"))

    def _on_clear(self) -> None:
        """Clear all outputs."""
        self.out_paths.clear()
        self.out_json.clear()
        self.status_label.setText("")
