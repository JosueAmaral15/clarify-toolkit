#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text to JSON Converter Dock

⚠️ NOTE: This file is still used by the Unified Text to JSON Converter
=========================================================================

This dock is embedded in the unified tool as "Format Conversion" mode.
It is NOT deprecated - it's actively used via composition pattern.

Usage:
- Direct: Previously accessible via Tools > Text to JSON Converter menu
- Current: Embedded in unified_text_to_json_dock.py (Mode: Format Conversion)

The unified tool uses this class via composition:
- UnifiedTextToJsonDock creates a TextToJsonDock instance
- Embeds it as a widget in "Format Conversion" mode
- No code duplication - original class is reused

Last Update: 2026-01-30 (v2.9.116)
Status: ACTIVE (used by unified tool)

See: src/gui/unified_text_to_json_dock.py
See: UNIFIED_TOOL_DESIGN_SPECIFICATION_3.md

---

Original Description:

Converts various text formats to JSON with advanced options:
- Key-Value pairs
- Lists (bullet points)
- CSV (with options)
- Python dict literals
- YAML-like format
- INI files
- TOML files
- Java Properties
- TOON (Token-Oriented Object Notation)
- Auto-detect format

Features:
- Live preview with debounce
- Type inference (auto-detect vs all strings)
- CSV advanced options (header, separator, format)
- Templates with examples
- Conversion history
- Validate JSON
- Swap (JSON to text)
- Copy result
- Open in editor

Author: Josué Amaral
Date: 2025-12-01
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy imports
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=attribute-defined-outside-init  # Qt widget pattern
# pylint: disable=line-too-long  # Long regex patterns
# pylint: disable=fixme  # TODO is intentional

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Dict, List

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox,
    QDialog, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPlainTextEdit, QPushButton, QRadioButton, QScrollArea,
    QVBoxLayout, QWidget
)
from PySide6.QtGui import QFont

from src.i18n.translator import tooltip_tr, tr
from src.text_to_json import convert_text_to_json, detect_format
from .base_dock import BaseDock

# Type checking imports
if TYPE_CHECKING:
    pass  # QWidget already imported above


class TemplatesDialog(QDialog):
    """Dialog to show format templates and examples."""

    TEMPLATES = {
        "Key-Value": """name: John Doe
age: 30
city: New York
active: true""",

        "List": """- Apple
- Banana
- Orange
- Mango""",

        "CSV": """name,age,city
John,30,New York
Alice,25,London
Bob,35,Paris""",

        "Python Dict": """{'name': 'John Doe', 'age': 30, 'city': 'New York', 'active': True}""",

        "YAML": """user:
  name: John Doe
  age: 30
  address:
    city: New York
    zip: 10001
  hobbies:
    - coding
    - reading""",

        "INI": """[user]
name=John Doe
age=30
city=New York

[settings]
theme=dark
language=en""",

        "TOML": """[user]
name = "John Doe"
age = 30
city = "New York"

[[projects]]
name = "Project A"
status = "active"

[[projects]]
name = "Project B"
status = "completed" """,

        "Java Properties": """user.name=John Doe
user.age=30
user.city=New York
app.theme=dark
app.language=en""",

        "TOON": """name: John Doe
age: 30
tags[3]: python,coding,llm
items[2]{id,name}:
  1,Apple
  2,Banana"""
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("text_to_json.templates_dialog_title"))
        # Removed resize(500, 600) - v2.9.40.2: caused window sizing issues when used as tab
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Format selector
        self.format_combo = QComboBox()
        self.format_combo.addItems(self.TEMPLATES.keys())
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        layout.addWidget(QLabel(tr("text_to_json.lbl_select_format")))
        layout.addWidget(self.format_combo)

        # Example text
        self.example_text = QPlainTextEdit()
        self.example_text.setReadOnly(True)
        font = QFont("Courier New", 10)
        self.example_text.setFont(font)
        layout.addWidget(QLabel(tr("text_to_json.lbl_example")))
        layout.addWidget(self.example_text)

        # Use button
        self.use_btn = QPushButton(tr("text_to_json.btn_use_template"))
        self.use_btn.clicked.connect(self.accept)
        layout.addWidget(self.use_btn)

        # Close button
        self.close_btn = QPushButton(tr("text_to_json.btn_close"))
        self.close_btn.clicked.connect(self.reject)
        layout.addWidget(self.close_btn)

        # Load first template
        self._on_format_changed(self.format_combo.currentText())

    def _on_format_changed(self, format_name: str):
        """Update example text when format changes."""
        self.example_text.setPlainText(self.TEMPLATES.get(format_name, ""))

    def get_selected_template(self) -> str:
        """Get the currently selected template text."""
        return self.example_text.toPlainText()


class TextToJsonDock(BaseDock):
    """
    Dock widget for text to JSON conversion.

    Supports 10 text formats with advanced options and features.
    """

    # Signal emitted when user wants to open result in editor
    open_in_editor_requested = Signal(str)  # JSON string

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Text to JSON Converter", parent)
        self.conversion_history: List[Dict[str, str]] = []
        self.live_preview_timer = QTimer(self)
        self.live_preview_timer.setSingleShot(True)
        self.live_preview_timer.timeout.connect(self._do_live_preview)

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()  # v2.9.69

    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Input section
        self.input_label = QLabel(tr("text_to_json.lbl_input"))
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText(tr("text_to_json.input_placeholder"))
        self.input_text.setMinimumHeight(200)
        self.input_text.textChanged.connect(self._on_input_changed)

        # Format selector
        self.format_label = QLabel(tr("text_to_json.lbl_format"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Auto-detect",
            "Key-Value pairs",
            "List (bullets)",
            "CSV",
            "Python Dict",
            "YAML",
            "INI file",
            "TOML",
            "Java Properties",
            "TOON"
        ])

        # Type inference options
        self.type_group = QGroupBox(tr("text_to_json.group_type_inference"))
        self.type_auto_radio = QRadioButton(tr("text_to_json.radio_auto_detect"))
        self.type_string_radio = QRadioButton(tr("text_to_json.radio_all_strings"))
        self.type_auto_radio.setChecked(True)
        self.type_button_group = QButtonGroup()
        self.type_button_group.addButton(self.type_auto_radio)
        self.type_button_group.addButton(self.type_string_radio)

        # CSV options group
        self.csv_group = QGroupBox(tr("text_to_json.group_csv"))
        self.csv_header_check = QCheckBox(tr("text_to_json.check_first_row_header"))
        self.csv_header_check.setChecked(True)

        self.csv_separator_label = QLabel(tr("text_to_json.lbl_separator"))
        self.csv_separator_combo = QComboBox()
        self.csv_separator_combo.addItems([tr("combo.separator_comma"), tr("combo.separator_semicolon"), tr("combo.separator_tab")])

        self.csv_format_label = QLabel(tr("text_to_json.lbl_output_format"))
        self.csv_array_objects_radio = QRadioButton(tr("text_to_json.radio_array_objects"))
        self.csv_array_arrays_radio = QRadioButton(tr("text_to_json.radio_array_arrays"))
        self.csv_array_objects_radio.setChecked(True)
        self.csv_format_group = QButtonGroup()
        self.csv_format_group.addButton(self.csv_array_objects_radio)
        self.csv_format_group.addButton(self.csv_array_arrays_radio)

        # General options
        self.pretty_print_check = QCheckBox(tr("text_to_json.check_pretty_print"))
        self.pretty_print_check.setChecked(True)

        self.live_preview_check = QCheckBox(tr("text_to_json.check_live_preview"))
        self.live_preview_check.setChecked(False)

        # Action buttons
        self.convert_btn = QPushButton(tr("text_to_json.btn_convert"))
        self.convert_btn.clicked.connect(self._on_convert_clicked)

        self.templates_btn = QPushButton(tr("text_to_json.btn_templates"))
        self.templates_btn.clicked.connect(self._on_templates_clicked)

        self.clear_btn = QPushButton(tr("text_to_json.btn_clear"))
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        self.validate_btn = QPushButton(tr("text_to_json.btn_validate"))
        self.validate_btn.clicked.connect(self._on_validate_clicked)

        self.copy_btn = QPushButton(tr("text_to_json.btn_copy"))
        self.copy_btn.clicked.connect(self._on_copy_clicked)

        self.open_editor_btn = QPushButton(tr("text_to_json.btn_open_editor"))
        self.open_editor_btn.clicked.connect(self._on_open_editor_clicked)

        self.history_btn = QPushButton(tr("text_to_json.btn_history"))
        self.history_btn.clicked.connect(self._on_history_clicked)

        self.swap_btn = QPushButton(tr("text_to_json.btn_swap"))
        self.swap_btn.clicked.connect(self._on_swap_clicked)

        # Output section
        self.output_label = QLabel(tr("text_to_json.lbl_output"))
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        self.output_text.setPlaceholderText(tr("text_to_json.output_placeholder"))

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")

    def _create_layout(self) -> None:
        """Create and arrange layout."""
        # Type inference group layout
        type_layout = QVBoxLayout()
        type_layout.addWidget(self.type_auto_radio)
        type_layout.addWidget(self.type_string_radio)
        self.type_group.setLayout(type_layout)

        # CSV options group layout
        csv_layout = QGridLayout()
        csv_layout.addWidget(self.csv_header_check, 0, 0, 1, 2)
        csv_layout.addWidget(self.csv_separator_label, 1, 0)
        csv_layout.addWidget(self.csv_separator_combo, 1, 1)
        csv_layout.addWidget(self.csv_format_label, 2, 0)
        csv_layout.addWidget(self.csv_array_objects_radio, 2, 1)
        csv_layout.addWidget(self.csv_array_arrays_radio, 3, 1)
        self.csv_group.setLayout(csv_layout)

        # Options section with scroll area
        scroll_options = QScrollArea()
        scroll_options.setWidgetResizable(True)
        scroll_options.setFrameShape(QFrame.NoFrame)
        scroll_options.setMaximumHeight(300)

        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        # Format row
        format_row = QHBoxLayout()
        format_row.addWidget(self.format_label)
        format_row.addWidget(self.format_combo, 1)
        options_layout.addLayout(format_row)

        # Type inference and CSV options in horizontal layout
        groups_row = QHBoxLayout()
        groups_row.addWidget(self.type_group)
        groups_row.addWidget(self.csv_group)
        options_layout.addLayout(groups_row)

        # Checkboxes
        options_layout.addWidget(self.pretty_print_check)
        options_layout.addWidget(self.live_preview_check)

        # Buttons grid (3 columns)
        buttons_layout = QGridLayout()
        buttons_layout.addWidget(self.convert_btn, 0, 0)
        buttons_layout.addWidget(self.templates_btn, 0, 1)
        buttons_layout.addWidget(self.clear_btn, 0, 2)
        buttons_layout.addWidget(self.validate_btn, 1, 0)
        buttons_layout.addWidget(self.copy_btn, 1, 1)
        buttons_layout.addWidget(self.open_editor_btn, 1, 2)
        buttons_layout.addWidget(self.history_btn, 2, 0)
        buttons_layout.addWidget(self.swap_btn, 2, 1)
        options_layout.addLayout(buttons_layout)

        # Set scroll widget
        scroll_options.setWidget(options_widget)

        # Main layout
        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_text, 2)  # 2/5 space
        self.layout.addWidget(scroll_options)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_text, 2)  # 2/5 space
        self.layout.addWidget(self.status_label)

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips (v2.9.69)."""
        # Format section
        self.format_combo.setToolTip(tooltip_tr("text_to_json.format_combo"))

        # Type inference section
        self.type_auto_radio.setToolTip(tooltip_tr("text_to_json.type_auto_radio"))
        self.type_string_radio.setToolTip(tooltip_tr("text_to_json.type_string_radio"))

        # CSV options section
        self.csv_header_check.setToolTip(tooltip_tr("text_to_json.csv_header_check"))
        self.csv_separator_combo.setToolTip(tooltip_tr("text_to_json.csv_separator_combo"))
        self.csv_array_objects_radio.setToolTip(tooltip_tr("text_to_json.csv_array_objects_radio"))
        self.csv_array_arrays_radio.setToolTip(tooltip_tr("text_to_json.csv_array_arrays_radio"))

        # General options section
        self.pretty_print_check.setToolTip(tooltip_tr("text_to_json.pretty_print_check"))
        self.live_preview_check.setToolTip(tooltip_tr("text_to_json.live_preview_check"))

        # Action buttons section
        self.convert_btn.setToolTip(tooltip_tr("text_to_json.convert_btn"))
        self.templates_btn.setToolTip(tooltip_tr("text_to_json.templates_btn"))
        self.clear_btn.setToolTip(tooltip_tr("text_to_json.clear_btn"))
        self.validate_btn.setToolTip(tooltip_tr("text_to_json.validate_btn"))
        self.copy_btn.setToolTip(tooltip_tr("text_to_json.copy_btn"))
        self.open_editor_btn.setToolTip(tooltip_tr("text_to_json.open_editor_btn"))
        self.history_btn.setToolTip(tooltip_tr("text_to_json.history_btn"))
        self.swap_btn.setToolTip(tooltip_tr("text_to_json.swap_btn"))

        # Input/Output section
        self.input_text.setToolTip(tooltip_tr("text_to_json.input_text"))
        self.output_text.setToolTip(tooltip_tr("text_to_json.output_text"))

        # Status section
        self.status_label.setToolTip(tooltip_tr("text_to_json.status_label"))

    def _on_input_changed(self) -> None:
        """Handle input text changes for live preview."""
        if self.live_preview_check.isChecked():
            # Restart timer (debounce)
            self.live_preview_timer.stop()
            self.live_preview_timer.start(500)  # 500ms delay

    def _do_live_preview(self) -> None:
        """Execute live preview conversion."""
        self._on_convert_clicked()

    def _get_format_key(self) -> str:
        """Get format key from combo selection."""
        format_map = {
            "Auto-detect": "auto",
            "Key-Value pairs": "key_value",
            "List (bullets)": "list",
            "CSV": "csv",
            "Python Dict": "python_dict",
            "YAML": "yaml",
            "INI file": "ini",
            "TOML": "toml",
            "Java Properties": "java_properties",
            "TOON": "toon"
        }
        return format_map.get(self.format_combo.currentText(), "auto")

    def _get_csv_separator(self) -> str:
        """Get CSV separator from combo."""
        separator_map = {
            "Comma (,)": ",",
            "Semicolon (;)": ";",
            "Tab (\\t)": "\t"
        }
        return separator_map.get(self.csv_separator_combo.currentText(), ",")

    def _on_convert_clicked(self) -> None:
        """Convert text to JSON."""
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            self.show_warning(tr("text_to_json.warn_empty_input_title"), tr("text_to_json.warn_empty_input_msg"))
            return

        try:
            # Get options
            format_type = self._get_format_key()
            infer_types = self.type_auto_radio.isChecked()

            # CSV-specific options
            kwargs = {}
            if format_type == "csv" or format_type == "auto":
                kwargs['has_header'] = self.csv_header_check.isChecked()
                kwargs['delimiter'] = self._get_csv_separator()
                kwargs['array_of_objects'] = self.csv_array_objects_radio.isChecked()

            # Convert
            result = convert_text_to_json(input_text, format_type, infer_types, **kwargs)

            # Format JSON
            if self.pretty_print_check.isChecked():
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                json_str = json.dumps(result, ensure_ascii=False)

            # Display result
            self.output_text.setPlainText(json_str)

            # Update status
            detected_format = detect_format(input_text) if format_type == "auto" else format_type
            self.status_label.setText(f"✓ Conversion successful (format: {detected_format})")
            self.status_label.setStyleSheet("color: green;")

            # Add to history
            self._add_to_history(input_text, json_str, detected_format)

        except Exception as e:
            self.show_error(tr("text_to_json.error_conversion_title"), tr("text_to_json.error_conversion_msg").replace("{error}", str(e)))
            self.status_label.setText(f"✗ Conversion failed: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def _on_templates_clicked(self) -> None:
        """Show templates dialog."""
        dialog = TemplatesDialog(self)
        if dialog.exec():
            # User clicked "Use This Template"
            template_text = dialog.get_selected_template()
            self.input_text.setPlainText(template_text)

    def _on_clear_clicked(self) -> None:
        """Clear input and output."""
        self.input_text.clear()
        self.output_text.clear()
        self.status_label.setText("")

    def _on_validate_clicked(self) -> None:
        """Validate output JSON."""
        json_str = self.output_text.toPlainText().strip()

        if not json_str:
            self.show_warning(tr("text_to_json.warn_empty_output_title"), tr("text_to_json.warn_empty_output_validate"))
            return

        try:
            json.loads(json_str)
            self.show_info(tr("text_to_json.info_valid_title"), tr("text_to_json.info_valid_msg"))
            self.status_label.setText(tr("text_to_json.status_valid"))
            self.status_label.setStyleSheet("color: green;")
        except json.JSONDecodeError as e:
            self.show_error(tr("text_to_json.error_invalid_title"), tr("text_to_json.error_invalid_msg").replace("{error}", str(e)))
            self.status_label.setText(f"✗ Invalid JSON: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def _on_copy_clicked(self) -> None:
        """Copy output JSON to clipboard."""
        json_str = self.output_text.toPlainText()

        if not json_str:
            self.show_warning(tr("text_to_json.warn_empty_output_title"), tr("text_to_json.warn_empty_output_copy"))
            return

        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(json_str)

        self.show_info(tr("text_to_json.info_copied_title"), tr("text_to_json.info_copied_msg"))
        self.status_label.setText(tr("text_to_json.status_copied"))
        self.status_label.setStyleSheet("color: green;")

    def _on_open_editor_clicked(self) -> None:
        """Open result in main editor."""
        json_str = self.output_text.toPlainText()

        if not json_str:
            self.show_warning(tr("text_to_json.warn_empty_output_title"), tr("text_to_json.warn_empty_output_editor"))
            return

        # Emit signal to main window
        self.open_in_editor_requested.emit(json_str)
        self.status_label.setText(tr("text_to_json.status_opened_editor"))
        self.status_label.setStyleSheet("color: green;")

    def _on_history_clicked(self) -> None:
        """Show conversion history."""
        if not self.conversion_history:
            self.show_info(tr("text_to_json.info_history_empty_title"), tr("text_to_json.info_history_empty_msg"))
            return

        # Create history dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("text_to_json.history_dialog_title"))
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for i, entry in enumerate(reversed(self.conversion_history)):
            format_str = entry.get('format', 'unknown')
            preview = entry['input'][:50].replace('\n', ' ')
            item_text = f"{i+1}. [{format_str}] {preview}..."
            list_widget.addItem(item_text)

        list_widget.itemDoubleClicked.connect(lambda item: self._load_history_item(item, dialog))

        layout.addWidget(QLabel(tr("text_to_json.history_lbl_double_click")))
        layout.addWidget(list_widget)

        close_btn = QPushButton(tr("text_to_json.btn_close"))
        close_btn.clicked.connect(dialog.reject)
        layout.addWidget(close_btn)

        dialog.exec()

    def _load_history_item(self, item: QListWidgetItem, dialog: QDialog) -> None:
        """Load history item into input."""
        index = len(self.conversion_history) - 1 - item.listWidget().row(item)
        if 0 <= index < len(self.conversion_history):
            entry = self.conversion_history[index]
            self.input_text.setPlainText(entry['input'])
            self.output_text.setPlainText(entry['output'])
            dialog.accept()

    def _on_swap_clicked(self) -> None:
        """Swap JSON to text (reverse conversion)."""
        self.show_info(tr("text_to_json.info_swap_title"), tr("text_to_json.info_swap_msg"))
        # TODO: Implement reverse conversion (JSON → text format)
        # This would require converting JSON back to chosen text format

    def _add_to_history(self, input_text: str, output_json: str, format_type: str) -> None:
        """Add conversion to history."""
        entry = {
            'input': input_text,
            'output': output_json,
            'format': format_type
        }
        self.conversion_history.append(entry)

        # Limit history to 50 entries
        if len(self.conversion_history) > 50:
            self.conversion_history.pop(0)
