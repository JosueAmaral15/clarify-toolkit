"""
Advanced Parameter Extractor Dock (v2.9.115)

GUI for the advanced parameter extraction tool from add/main.py.
Provides both JSX/TSX and generic mode extraction with hierarchical JSON generation.
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QMessageBox,
    QFileDialog, QSpinBox, QComboBox, QTabWidget, QPlainTextEdit,
    QRadioButton, QButtonGroup, QApplication, QMenu
)
from PySide6.QtGui import QIcon, QAction
from typing import Optional, List, Tuple, Dict, Any
import os
import re
import json

from src.gui.base_dock import BaseDock, FileInputMixin
from src.extractors.advanced_extractor import AdvancedExtractor
from src.i18n.translator import tr, tooltip_tr


class AdvancedExtractorDock(BaseDock, FileInputMixin):
    """
    Advanced parameter extractor with JSX and generic modes.

    Features:
    - Attribute vs Tag-content extraction modes
    - Case normalization (snake/camel/pascal/kebab)
    - Drop standard HTML tags
    - String literal validation (no expressions)
    - Numeric hierarchy removal with collapse
    - Deep merge for nested JSON
    """

    def __init__(self, parent=None):
        super().__init__(tr("advanced_extractor.title", "Advanced Extractor"), parent)
        self.setObjectName("AdvancedExtractorDock")

        # Avoid keys parameter for radio buttons
        self.avoid_keys_parameter = "equals"
        self.EQUALS = "equals"
        self.CONTAINS = "contains"

    def _setup_ui(self):
        """Setup the complete UI with all controls."""
        # Main layout
        main_layout = QVBoxLayout()

        # Path input section
        path_section = self._create_path_section()
        main_layout.addLayout(path_section)

        # Mode and parameter section
        mode_section = self._create_mode_section()
        main_layout.addLayout(mode_section)

        # Generic delimiters section
        delimiters_section = self._create_delimiters_section()
        main_layout.addLayout(delimiters_section)

        # Options checkboxes (11 options)
        options_section = self._create_options_section()
        main_layout.addLayout(options_section)

        # Case style and limits section
        case_section = self._create_case_section()
        main_layout.addLayout(case_section)

        # Avoid keys section
        avoid_section = self._create_avoid_keys_section()
        main_layout.addLayout(avoid_section)

        # Action buttons
        buttons_section = self._create_buttons_section()
        main_layout.addLayout(buttons_section)

        # Output tabs
        tabs_section = self._create_output_tabs()
        main_layout.addWidget(tabs_section, 1)

        # Copy button
        self.copy_all_btn = QPushButton(tr("base.copy_all", "Copy All"))
        self.copy_all_btn.clicked.connect(self._copy_all)
        main_layout.addWidget(self.copy_all_btn)

        self.layout.addLayout(main_layout)

    def _create_path_section(self) -> QHBoxLayout:
        """Create path input with browse button and file/directory toggle."""
        layout = QHBoxLayout()

        layout.addWidget(QLabel(tr("advanced_extractor.path", "Path:")))

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(tr("advanced_extractor.path_placeholder", "File or directory path"))
        layout.addWidget(self.path_edit, 1)

        self.browse_btn = QPushButton(tr("base.btn_browse", "Browse"))
        self.browse_btn.setMaximumWidth(100)
        self.browse_btn.clicked.connect(self._browse_path)
        layout.addWidget(self.browse_btn)

        self.is_file_checkbox = QCheckBox(tr("advanced_extractor.is_file", "Is file?"))
        layout.addWidget(self.is_file_checkbox)

        return layout

    def _create_mode_section(self) -> QHBoxLayout:
        """Create mode selection and parameter input."""
        layout = QHBoxLayout()

        # Parameter input
        layout.addWidget(QLabel(tr("advanced_extractor.param", "Param/Attribute:")))
        self.param_edit = QLineEdit()
        self.param_edit.setPlaceholderText(tr("advanced_extractor.param_placeholder", "e.g., label, title"))
        layout.addWidget(self.param_edit)

        # Attribute mode checkbox
        self.is_attribute_checkbox = QCheckBox(
            tr("advanced_extractor.is_attribute", "Treat as ATTRIBUTE?")
        )
        self.is_attribute_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.is_attribute_tooltip",
                      "Attribute mode: extract attribute values\nTag-content mode: extract tag contents")
        )
        layout.addWidget(self.is_attribute_checkbox)

        # Mode selector
        layout.addWidget(QLabel(tr("advanced_extractor.mode", "Mode:")))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([tr("combo.mode_jsx"), tr("combo.mode_generic")])
        self.mode_combo.currentTextChanged.connect(self._toggle_generic_fields)
        layout.addWidget(self.mode_combo)

        return layout

    def _create_delimiters_section(self) -> QHBoxLayout:
        """Create generic mode delimiters and extensions."""
        layout = QHBoxLayout()

        # Start delimiter
        layout.addWidget(QLabel(tr("advanced_extractor.start_delim", "Start (regex):")))
        self.start_edit = QLineEdit("<.*?>")
        layout.addWidget(self.start_edit, 1)

        # End delimiter
        layout.addWidget(QLabel(tr("advanced_extractor.end_delim", "End (regex):")))
        self.end_edit = QLineEdit("</.*?>")
        layout.addWidget(self.end_edit, 1)

        # Extensions
        layout.addWidget(QLabel(tr("advanced_extractor.extensions", "Extensions:")))
        self.extensions_edit = QLineEdit(".tsx .jsx .js .ts")
        self.extensions_edit.setPlaceholderText(tr("advanced_extractor.placeholder_extensions"))
        layout.addWidget(self.extensions_edit, 1)

        return layout

    def _create_options_section(self) -> QVBoxLayout:
        """Create all checkboxes for extraction options."""
        container = QVBoxLayout()

        # Row 1: include options
        row1 = QHBoxLayout()
        self.include_key_checkbox = QCheckBox(
            tr("advanced_extractor.include_key", "Include key")
        )
        self.include_key_checkbox.setChecked(True)
        row1.addWidget(self.include_key_checkbox)

        self.include_value_checkbox = QCheckBox(
            tr("advanced_extractor.include_value", "Include value")
        )
        self.include_value_checkbox.setChecked(True)
        row1.addWidget(self.include_value_checkbox)

        self.no_standard_checkbox = QCheckBox(
            tr("advanced_extractor.no_standard", "Drop standard HTML tags")
        )
        self.no_standard_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.no_standard_tooltip",
                      "Remove standard HTML tags like div, span, p, etc.")
        )
        row1.addWidget(self.no_standard_checkbox)

        self.only_strings_checkbox = QCheckBox(
            tr("advanced_extractor.only_strings", "Only strings")
        )
        self.only_strings_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.only_strings_tooltip",
                      "Filter out expressions, variables, and operations")
        )
        row1.addWidget(self.only_strings_checkbox)

        container.addLayout(row1)

        # Row 2: quotation marks and match all
        row2 = QHBoxLayout()
        self.quotation_marks_checkbox = QCheckBox(
            tr("advanced_extractor.quotation_marks", "Include quotation marks")
        )
        row2.addWidget(self.quotation_marks_checkbox)

        self.match_all_checkbox = QCheckBox(
            tr("advanced_extractor.match_all", "Match all")
        )
        self.match_all_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.match_all_tooltip",
                      "Match all occurrences instead of specific parameter")
        )
        row2.addWidget(self.match_all_checkbox)

        container.addLayout(row2)

        return container

    def _create_case_section(self) -> QHBoxLayout:
        """Create case style, uppercase, limit, and indent controls."""
        layout = QHBoxLayout()

        # Case style
        layout.addWidget(QLabel(tr("advanced_extractor.case", "Case:")))
        self.case_combo = QComboBox()
        self.case_combo.addItems([tr("combo.case_snake"), tr("combo.case_camel"), tr("combo.case_pascal"), tr("combo.case_kebab")])
        layout.addWidget(self.case_combo)

        # Uppercase toggle
        self.uppercase_checkbox = QCheckBox(
            tr("advanced_extractor.uppercase", "Uppercase token")
        )
        layout.addWidget(self.uppercase_checkbox)

        # Limit
        layout.addWidget(QLabel(tr("advanced_extractor.limit", "Limit:")))
        self.limit_edit = QLineEdit("all")
        self.limit_edit.setMaximumWidth(80)
        layout.addWidget(self.limit_edit)

        # Avoid cut
        self.avoid_cut_checkbox = QCheckBox(
            tr("advanced_extractor.avoid_cut", "Avoid cut")
        )
        self.avoid_cut_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.avoid_cut_tooltip",
                      "Truncate at word boundaries")
        )
        layout.addWidget(self.avoid_cut_checkbox)

        # Indentation
        layout.addWidget(QLabel(tr("advanced_extractor.indent", "Indent:")))
        self.indent_spin = QSpinBox()
        self.indent_spin.setRange(0, 16)
        self.indent_spin.setValue(2)
        self.indent_spin.setMaximumWidth(60)
        layout.addWidget(self.indent_spin)

        return layout

    def _create_avoid_keys_section(self) -> QVBoxLayout:
        """Create avoid keys input and matching mode."""
        container = QVBoxLayout()

        # Keys input
        row1 = QHBoxLayout()
        row1.addWidget(QLabel(
            tr("advanced_extractor.avoid_keys", "Keys/values to avoid (comma-separated):")
        ))
        self.avoid_keys_edit = QLineEdit()
        self.avoid_keys_edit.setPlaceholderText(tr("advanced_extractor.placeholder_avoid_keys"))
        row1.addWidget(self.avoid_keys_edit, 1)
        container.addLayout(row1)

        # Matching mode
        row2 = QHBoxLayout()
        self.avoid_equals_radio = QRadioButton(
            tr("advanced_extractor.avoid_equals", "Exact match")
        )
        self.avoid_contains_radio = QRadioButton(
            tr("advanced_extractor.avoid_contains", "Contains")
        )

        self.avoid_mode_group = QButtonGroup(self)
        self.avoid_mode_group.addButton(self.avoid_equals_radio)
        self.avoid_mode_group.addButton(self.avoid_contains_radio)
        self.avoid_equals_radio.setChecked(True)

        row2.addWidget(self.avoid_equals_radio)
        row2.addWidget(self.avoid_contains_radio)
        row2.addStretch(1)
        container.addLayout(row2)

        return container

    def _create_buttons_section(self) -> QHBoxLayout:
        """Create action buttons (Run and Save)."""
        layout = QHBoxLayout()
        layout.addStretch(1)

        self.run_btn = QPushButton(tr("base.run", "Run"))
        self.run_btn.setMinimumWidth(100)
        self.run_btn.clicked.connect(self._run_extraction)
        layout.addWidget(self.run_btn)

        self.save_btn = QPushButton(tr("base.save", "Save Outputs"))
        self.save_btn.setMinimumWidth(120)
        self.save_btn.clicked.connect(self._save_outputs)
        layout.addWidget(self.save_btn)

        return layout

    def _create_output_tabs(self) -> QTabWidget:
        """Create output tabs for paths and JSON."""
        self.output_tabs = QTabWidget()

        # Paths tab
        self.paths_output = QPlainTextEdit()
        self.paths_output.setReadOnly(True)
        self.paths_output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.paths_output.customContextMenuRequested.connect(self._show_context_menu)
        self.output_tabs.addTab(
            self.paths_output,
            tr("advanced_extractor.tab_paths", "Paths")
        )

        # JSON tab
        self.json_output = QPlainTextEdit()
        self.json_output.setReadOnly(True)
        self.json_output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.json_output.customContextMenuRequested.connect(self._show_context_menu)
        self.output_tabs.addTab(
            self.json_output,
            tr("advanced_extractor.tab_json", "JSON")
        )

        return self.output_tabs

    def _connect_signals(self):
        """Connect signals after UI creation."""
        # Avoid keys mode toggle
        self.avoid_equals_radio.toggled.connect(self._update_avoid_mode)
        self.avoid_contains_radio.toggled.connect(self._update_avoid_mode)

        # Initial state
        self._toggle_generic_fields(self.mode_combo.currentText())

    def _toggle_generic_fields(self, mode: str):
        """Enable/disable generic mode fields based on mode selection."""
        is_generic = (mode == "generic")
        self.start_edit.setEnabled(is_generic)
        self.end_edit.setEnabled(is_generic)

    def _update_avoid_mode(self):
        """Update avoid keys matching mode."""
        if self.avoid_equals_radio.isChecked():
            self.avoid_keys_parameter = self.EQUALS
        elif self.avoid_contains_radio.isChecked():
            self.avoid_keys_parameter = self.CONTAINS

    def _browse_path(self):
        """Browse for file or directory."""
        path = self.path_edit.text().strip()

        if not path or not os.path.exists(path):
            # No existing path - ask for file or directory
            if self.is_file_checkbox.isChecked():
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    tr("advanced_extractor.select_file", "Select file")
                )
                if file_path:
                    self.path_edit.setText(file_path)
            else:
                dir_path = QFileDialog.getExistingDirectory(
                    self,
                    tr("advanced_extractor.select_dir", "Select directory")
                )
                if dir_path:
                    self.path_edit.setText(dir_path)
        else:
            # Path exists - allow reselection
            if os.path.isfile(path):
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    tr("advanced_extractor.select_file", "Select file"),
                    os.path.dirname(path)
                )
                if file_path:
                    self.path_edit.setText(file_path)
            else:
                dir_path = QFileDialog.getExistingDirectory(
                    self,
                    tr("advanced_extractor.select_dir", "Select directory"),
                    path
                )
                if dir_path:
                    self.path_edit.setText(dir_path)

    def _run_extraction(self):
        """Execute the extraction with current settings."""
        try:
            # Validate path
            path = self.path_edit.text().strip()
            if not path:
                self.show_warning(
                    tr("advanced_extractor.error", "Error"),
                    tr("advanced_extractor.no_path", "Please provide a path.")
                )
                return

            if not os.path.exists(path):
                self.show_warning(
                    tr("advanced_extractor.error", "Error"),
                    tr("advanced_extractor.invalid_path", "Path does not exist.")
                )
                return

            # Collect settings
            param = self.param_edit.text().strip() or ""
            mode = self.mode_combo.currentText()
            start_regex = self.start_edit.text().strip() if mode == "generic" else None
            end_regex = self.end_edit.text().strip() if mode == "generic" else None

            # Checkboxes
            include_key = self.include_key_checkbox.isChecked()
            include_value = self.include_value_checkbox.isChecked()
            no_standard = self.no_standard_checkbox.isChecked()
            only_strings = self.only_strings_checkbox.isChecked()
            with_quotation_marks = self.quotation_marks_checkbox.isChecked()
            match_all = self.match_all_checkbox.isChecked()

            # Case and limits
            case_style = self.case_combo.currentText()
            to_upper = self.uppercase_checkbox.isChecked()
            limit = self.limit_edit.text().strip() or "all"
            avoid_cut = self.avoid_cut_checkbox.isChecked()
            indent = self.indent_spin.value()

            # Avoid keys
            avoid_keys = self.avoid_keys_edit.text().strip()
            avoid_keys_param = self.avoid_keys_parameter

            # Extensions
            is_attribute_mode = self.is_attribute_checkbox.isChecked()
            exts_text = self.extensions_edit.text().strip()
            file_extensions = [e.strip() for e in exts_text.split() if e.strip()]

            # Create extractor
            extractor = AdvancedExtractor(
                param=param,
                mode=mode,
                include_key=include_key,
                include_value=include_value,
                no_standard=no_standard,
                convert_to_json=True,
                with_quotation_marks=with_quotation_marks,
                only_strings=only_strings,
                indentation=indent,
                case_style=case_style,
                limit=limit,
                avoid_keys=avoid_keys,
                avoid_keys_parameter=avoid_keys_param,
                avoid_cut=avoid_cut,
                to_upper=to_upper,
                start_regex=start_regex,
                end_regex=end_regex,
                file_extensions=file_extensions,
                is_attribute_mode=is_attribute_mode,
                match_all=match_all
            )

            # Run extraction
            text_output, json_output = extractor.run(path)

            # Display results
            self.paths_output.setPlainText(text_output or "")
            self.json_output.setPlainText(json_output or "")

            # Show success message
            paths_count = len([line for line in text_output.split('\n') if line.strip()])
            self.show_info(
                tr("advanced_extractor.success", "Success"),
                tr("advanced_extractor.extracted",
                   f"Extracted {paths_count} paths successfully.")
            )

        except Exception as e:
            self.show_error(
                tr("advanced_extractor.error", "Error"),
                tr("advanced_extractor.run_error", f"Extraction failed: {str(e)}")
            )

    def _save_outputs(self):
        """Save outputs to files."""
        try:
            paths_text = self.paths_output.toPlainText()
            json_text = self.json_output.toPlainText()

            if not paths_text and not json_text:
                self.show_info(
                    tr("advanced_extractor.nothing_to_save", "Nothing to save"),
                    tr("advanced_extractor.no_outputs", "No outputs to save.")
                )
                return

            # Save paths
            if paths_text:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    tr("advanced_extractor.save_paths", "Save paths text"),
                    "paths.txt",
                    "Text files (*.txt);;All files (*)"
                )
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(paths_text)

            # Save JSON
            if json_text:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    tr("advanced_extractor.save_json", "Save JSON"),
                    "result.json",
                    "JSON files (*.json);;All files (*)"
                )
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(json_text)

            self.show_info(
                tr("advanced_extractor.saved", "Saved"),
                tr("advanced_extractor.outputs_saved", "Outputs saved successfully.")
            )

        except Exception as e:
            self.show_error(
                tr("advanced_extractor.error", "Error"),
                tr("advanced_extractor.save_error", f"Failed to save: {str(e)}")
            )

    def _should_filter_line(self, line: str) -> bool:
        """Check if line should be filtered from clipboard copy."""
        s = line.lstrip()
        # Remove debug/API lines
        if s.startswith(">> Sending") or s.startswith(">> SIMULATED") or s.startswith("<<API ERROR"):
            return True
        # Remove code fence markers
        if re.match(r"^\s*```[A-Za-z0-9_-]*\s*$", s) or s.strip() == "```":
            return True
        return False

    def _copy_all(self):
        """Copy current tab content to clipboard (filtered)."""
        current_widget = self.output_tabs.currentWidget()
        text = current_widget.toPlainText()

        if not text:
            return

        # Filter lines
        lines = text.splitlines()
        filtered = [ln for ln in lines if not self._should_filter_line(ln)]

        # Collapse multiple blank lines
        compact = []
        prev_blank = False
        for ln in filtered:
            blank = (ln.strip() == "")
            if blank and prev_blank:
                continue
            compact.append(ln)
            prev_blank = blank

        # Copy to clipboard
        QApplication.clipboard().setText("\n".join(compact))

        self.show_info(
            tr("advanced_extractor.copied", "Copied"),
            tr("advanced_extractor.copied_message", "Filtered output copied to clipboard.")
        )

    def _show_context_menu(self, position):
        """Show context menu for output text widgets."""
        menu = QMenu(self)

        # Copy action
        copy_action = QAction(tr("base.copy", "Copy"), self)
        copy_action.triggered.connect(self._copy_all)
        menu.addAction(copy_action)

        # Export action
        export_action = QAction(tr("base.export", "Export"), self)
        export_action.triggered.connect(self._save_outputs)
        menu.addAction(export_action)

        # Show menu
        current_widget = self.output_tabs.currentWidget()
        menu.exec_(current_widget.mapToGlobal(position))
