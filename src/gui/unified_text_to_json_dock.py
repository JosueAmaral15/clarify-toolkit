#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified Text to JSON Converter Dock - FLATTENED VERSION
========================================================

Combines two tools into one with mode switching:
1. Format Conversion (CSV, YAML, INI, TOML, etc. → JSON)
2. JSX/HTML Extraction (extract attributes from code → JSON)

Architecture:
- All widgets directly in main body (no composition)
- Two separate layouts (format_conversion_layout + jsx_extraction_layout)
- Switch between layouts on mode change (hide/show)
- ONE main scrollbar wrapping both layouts
- All 36 features work (10 converters, templates, history, validation, 26 extraction options)

Author: Programmer #3
Date: 2026-01-30
Version: 2.9.117 (Flattened Refactor)
"""

from __future__ import annotations
import json
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QRadioButton, QButtonGroup, QCheckBox,
    QPushButton, QPlainTextEdit, QMessageBox, QDialog, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QTabWidget, QFileDialog, QMenu, QApplication
)
from PySide6.QtGui import QFont, QAction

from .base_dock import BaseDock, FileInputMixin
from src.text_to_json import convert_text_to_json, detect_format
from src.extractors.advanced_extractor import AdvancedExtractor
from src.i18n.translator import tooltip_tr, tr

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


class TemplatesDialog(QDialog):
    """Dialog to show format templates and examples."""
    
    TEMPLATES = {
        # Format Conversion Templates
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
  2,Banana""",
        
        # JSX/HTML Templates
        "JSX Button": """<Button 
  label="Click Me" 
  variant="primary"
  onClick={handleClick}
  disabled={false}
/>""",
        
        "JSX Form": """<Form 
  action="/submit" 
  method="POST"
  onSubmit={handleSubmit}
>
  <Input name="username" placeholder="Enter username" />
  <Input name="password" type="password" />
  <Button type="submit">Submit</Button>
</Form>""",
        
        "HTML Div": """<div 
  className="container" 
  id="main"
  data-testid="main-container"
  style="padding: 20px;"
>
  <h1>Welcome</h1>
  <p>Content here</p>
</div>""",
        
        "JSX Component": """<Card
  title="User Profile"
  subtitle="View details"
  image="/avatar.jpg"
  actions={[
    {label: "Edit", onClick: handleEdit},
    {label: "Delete", onClick: handleDelete}
  ]}
/>""",
        
        "HTML Table": """<table 
  className="data-table"
  border="1"
  cellpadding="5"
>
  <thead>
    <tr>
      <th>Name</th>
      <th>Age</th>
      <th>City</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>John</td>
      <td>30</td>
      <td>New York</td>
    </tr>
  </tbody>
</table>"""
    }
    
    def __init__(self, parent=None, mode="format"):
        super().__init__(parent)
        self.mode = mode  # "format" or "jsx"
        self.setWindowTitle(tr("text_to_json.templates_dialog_title"))
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


class HistoryDialog(QDialog):
    """Dialog to show conversion history (dummy for now)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("text_to_json.history_dialog_title"))


class UnifiedTextToJsonDock(BaseDock, FileInputMixin):
    """
    Unified Text to JSON Converter with two modes - FLATTENED VERSION.
    
    All widgets are created directly in this class (no composition).
    Two separate flat layouts with mode switching.
    """
    
    # Signal emitted when user wants to open result in editor
    open_in_editor_requested = Signal(str)  # JSON string
    
    def __init__(self, parent: QWidgetType | None = None):
        # Initialize state BEFORE calling super().__init__
        self.current_mode = "format_conversion"  # Default mode
        self.conversion_history: List[Dict[str, str]] = []
        self.extraction_history: List[Dict[str, str]] = []  # JSX extraction history
        self.live_preview_timer = QTimer()
        self.live_preview_timer.setSingleShot(True)
        self.live_preview_timer.timeout.connect(self._do_live_preview)
        
        # JSX Extraction state
        self.avoid_keys_parameter = "equals"
        self.EQUALS = "equals"
        self.CONTAINS = "contains"
        
        super().__init__(tr("text_to_json.title", "Text to JSON Converter"), parent)
        self.setObjectName("UnifiedTextToJsonDock")
    
    def _setup_ui(self) -> None:
        """Setup main UI with mode selector and two flattened layouts."""
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)
        
        # Mode selector section at top
        mode_section = self._create_mode_selector()
        main_layout.addLayout(mode_section)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Create ONE scroll area wrapping both layouts
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for tool content (goes inside scroll area)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)
        
        # Create both tool layouts
        self._create_format_conversion_layout()
        self._create_jsx_extraction_layout()
        
        # Add both layouts to container (will hide/show based on mode)
        self.content_layout.addWidget(self.format_conversion_container)
        self.content_layout.addWidget(self.jsx_extraction_container)
        
        # Put container in scroll area
        scroll_area.setWidget(self.content_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area, 1)  # Stretch factor 1
        
        # Set main widget
        self.setWidget(main_widget)
        
        # Connect signals
        self._connect_signals()
        
        # Apply tooltips
        self._apply_tooltips()
        
        # Load default mode
        self._switch_mode(self.current_mode)
    
    def _create_mode_selector(self) -> QHBoxLayout:
        """Create mode selector dropdown at top."""
        layout = QHBoxLayout()
        
        # Mode label
        mode_label = QLabel(tr("text_to_json.mode_label", "Mode:"))
        mode_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(mode_label)
        
        # Mode combo box
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(
            tr("text_to_json.mode_format_conversion", "Format Conversion"), 
            "format_conversion"
        )
        self.mode_combo.addItem(
            tr("text_to_json.mode_jsx_extraction", "JSX/HTML Extraction"), 
            "jsx_extraction"
        )
        self.mode_combo.setToolTip(
            tooltip_tr("text_to_json.mode_tooltip",
                      "Switch between format conversion (CSV, YAML, etc.) and JSX/HTML extraction modes")
        )
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.mode_combo.setMinimumWidth(250)
        layout.addWidget(self.mode_combo)
        
        # Spacer
        layout.addStretch()
        
        return layout
    
    def _on_mode_changed(self, index: int) -> None:
        """Handle mode dropdown change."""
        mode_key = self.mode_combo.itemData(index)
        if mode_key != self.current_mode:
            self._switch_mode(mode_key)
    
    def _switch_mode(self, mode_key: str) -> None:
        """
        Switch between modes by showing/hiding layout containers.
        
        Args:
            mode_key: Either "format_conversion" or "jsx_extraction"
        """
        if mode_key == "format_conversion":
            self.format_conversion_container.show()
            self.jsx_extraction_container.hide()
        elif mode_key == "jsx_extraction":
            self.format_conversion_container.hide()
            self.jsx_extraction_container.show()
        else:
            raise ValueError(f"Unknown mode: {mode_key}")
        
        self.current_mode = mode_key
    
    # ========================================================================
    # FORMAT CONVERSION LAYOUT (from text_to_json_dock.py)
    # ========================================================================
    
    def _create_format_conversion_layout(self) -> None:
        """Create complete Format Conversion layout with all widgets."""
        # Main container
        self.format_conversion_container = QWidget()
        layout = QVBoxLayout(self.format_conversion_container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Input section
        self.fc_input_label = QLabel(tr("text_to_json.lbl_input"))
        self.fc_input_text = QPlainTextEdit()
        self.fc_input_text.setPlaceholderText(tr("text_to_json.input_placeholder"))
        self.fc_input_text.setMinimumHeight(200)
        self.fc_input_text.textChanged.connect(self._on_input_changed)
        
        layout.addWidget(self.fc_input_label)
        layout.addWidget(self.fc_input_text, 2)
        
        # Format selector
        format_row = QHBoxLayout()
        self.fc_format_label = QLabel(tr("text_to_json.lbl_format"))
        self.fc_format_combo = QComboBox()
        self.fc_format_combo.addItems([
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
        format_row.addWidget(self.fc_format_label)
        format_row.addWidget(self.fc_format_combo, 1)
        layout.addLayout(format_row)
        
        # Type inference options
        self.fc_type_group = QGroupBox(tr("text_to_json.group_type_inference"))
        self.fc_type_auto_radio = QRadioButton(tr("text_to_json.radio_auto_detect"))
        self.fc_type_string_radio = QRadioButton(tr("text_to_json.radio_all_strings"))
        self.fc_type_auto_radio.setChecked(True)
        self.fc_type_button_group = QButtonGroup()
        self.fc_type_button_group.addButton(self.fc_type_auto_radio)
        self.fc_type_button_group.addButton(self.fc_type_string_radio)
        
        type_layout = QVBoxLayout()
        type_layout.addWidget(self.fc_type_auto_radio)
        type_layout.addWidget(self.fc_type_string_radio)
        self.fc_type_group.setLayout(type_layout)
        
        # CSV options group
        self.fc_csv_group = QGroupBox(tr("text_to_json.group_csv"))
        self.fc_csv_header_check = QCheckBox(tr("text_to_json.check_first_row_header"))
        self.fc_csv_header_check.setChecked(True)
        
        self.fc_csv_separator_label = QLabel(tr("text_to_json.lbl_separator"))
        self.fc_csv_separator_combo = QComboBox()
        self.fc_csv_separator_combo.addItems([tr("combo.separator_comma"), tr("combo.separator_semicolon"), tr("combo.separator_tab")])
        
        self.fc_csv_format_label = QLabel(tr("text_to_json.lbl_output_format"))
        self.fc_csv_array_objects_radio = QRadioButton(tr("text_to_json.radio_array_objects"))
        self.fc_csv_array_arrays_radio = QRadioButton(tr("text_to_json.radio_array_arrays"))
        self.fc_csv_array_objects_radio.setChecked(True)
        self.fc_csv_format_group = QButtonGroup()
        self.fc_csv_format_group.addButton(self.fc_csv_array_objects_radio)
        self.fc_csv_format_group.addButton(self.fc_csv_array_arrays_radio)
        
        csv_layout = QGridLayout()
        csv_layout.addWidget(self.fc_csv_header_check, 0, 0, 1, 2)
        csv_layout.addWidget(self.fc_csv_separator_label, 1, 0)
        csv_layout.addWidget(self.fc_csv_separator_combo, 1, 1)
        csv_layout.addWidget(self.fc_csv_format_label, 2, 0)
        csv_layout.addWidget(self.fc_csv_array_objects_radio, 2, 1)
        csv_layout.addWidget(self.fc_csv_array_arrays_radio, 3, 1)
        self.fc_csv_group.setLayout(csv_layout)
        
        # Type inference and CSV options in horizontal layout
        groups_row = QHBoxLayout()
        groups_row.addWidget(self.fc_type_group)
        groups_row.addWidget(self.fc_csv_group)
        layout.addLayout(groups_row)
        
        # General options
        self.fc_pretty_print_check = QCheckBox(tr("text_to_json.check_pretty_print"))
        self.fc_pretty_print_check.setChecked(True)
        layout.addWidget(self.fc_pretty_print_check)
        
        self.fc_live_preview_check = QCheckBox(tr("text_to_json.check_live_preview"))
        self.fc_live_preview_check.setChecked(False)
        layout.addWidget(self.fc_live_preview_check)
        
        # Swap checkbox (below live preview)
        self.fc_swap_checkbox = QCheckBox(tr("text_to_json.btn_swap", "Swap (JSON → Text)"))
        self.fc_swap_checkbox.toggled.connect(self._on_swap_toggled)
        layout.addWidget(self.fc_swap_checkbox)
        
        # Action buttons (3x3 grid)
        buttons_layout = QGridLayout()
        
        self.fc_convert_btn = QPushButton(tr("text_to_json.btn_convert"))
        self.fc_convert_btn.clicked.connect(self._on_convert_clicked)
        buttons_layout.addWidget(self.fc_convert_btn, 0, 0)
        
        self.fc_templates_btn = QPushButton(tr("text_to_json.btn_templates"))
        self.fc_templates_btn.clicked.connect(self._on_templates_clicked)
        buttons_layout.addWidget(self.fc_templates_btn, 0, 1)
        
        self.fc_clear_btn = QPushButton(tr("text_to_json.btn_clear"))
        self.fc_clear_btn.clicked.connect(self._on_clear_clicked)
        buttons_layout.addWidget(self.fc_clear_btn, 0, 2)
        
        self.fc_validate_btn = QPushButton(tr("text_to_json.btn_validate"))
        self.fc_validate_btn.clicked.connect(self._on_validate_clicked)
        buttons_layout.addWidget(self.fc_validate_btn, 1, 0)
        
        self.fc_copy_btn = QPushButton(tr("text_to_json.btn_copy"))
        self.fc_copy_btn.clicked.connect(self._on_copy_clicked)
        buttons_layout.addWidget(self.fc_copy_btn, 1, 1)
        
        self.fc_open_editor_btn = QPushButton(tr("text_to_json.btn_open_editor"))
        self.fc_open_editor_btn.clicked.connect(self._on_open_editor_clicked)
        buttons_layout.addWidget(self.fc_open_editor_btn, 1, 2)
        
        self.fc_history_btn = QPushButton(tr("text_to_json.btn_history"))
        self.fc_history_btn.clicked.connect(self._on_history_clicked)
        buttons_layout.addWidget(self.fc_history_btn, 2, 0)
        
        layout.addLayout(buttons_layout)
        
        # Output section
        self.fc_output_label = QLabel(tr("text_to_json.lbl_output"))
        self.fc_output_text = QPlainTextEdit()
        self.fc_output_text.setReadOnly(True)
        self.fc_output_text.setMinimumHeight(200)
        self.fc_output_text.setPlaceholderText(tr("text_to_json.output_placeholder"))
        
        layout.addWidget(self.fc_output_label)
        layout.addWidget(self.fc_output_text, 2)
        
        # Status label
        self.fc_status_label = QLabel("")
        self.fc_status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.fc_status_label)
    
    # ========================================================================
    # JSX EXTRACTION LAYOUT (from advanced_extractor_dock.py)
    # ========================================================================
    
    def _create_jsx_extraction_layout(self) -> None:
        """Create complete JSX Extraction layout with all widgets."""
        # Main container
        self.jsx_extraction_container = QWidget()
        layout = QVBoxLayout(self.jsx_extraction_container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Path/Text input section
        path_layout = QHBoxLayout()
        
        # Input type dropdown (replaces "Is File?" checkbox)
        path_layout.addWidget(QLabel(tr("advanced_extractor.input_type", "Input:")))
        self.jsx_input_type_combo = QComboBox()
        self.jsx_input_type_combo.addItems([
            tr("advanced_extractor.input_directory", "Directory"),
            tr("advanced_extractor.input_file", "File"),
            tr("advanced_extractor.input_text", "Text")
        ])
        self.jsx_input_type_combo.setMaximumWidth(120)
        self.jsx_input_type_combo.currentIndexChanged.connect(self._jsx_on_input_type_changed)
        path_layout.addWidget(self.jsx_input_type_combo)
        
        path_layout.addWidget(QLabel(tr("advanced_extractor.path", "Path:")))
        
        # Path input field (visible for Directory/File mode)
        self.jsx_path_edit = QLineEdit()
        self.jsx_path_edit.setPlaceholderText(tr("advanced_extractor.path_placeholder", "File or directory path"))
        path_layout.addWidget(self.jsx_path_edit, 1)
        
        self.jsx_browse_btn = QPushButton(tr("base.btn_browse", "Browse"))
        self.jsx_browse_btn.setMaximumWidth(100)
        self.jsx_browse_btn.clicked.connect(self._jsx_browse_path)
        path_layout.addWidget(self.jsx_browse_btn)
        
        layout.addLayout(path_layout)
        
        # Text input area (visible only in Text mode)
        self.jsx_text_input = QPlainTextEdit()
        self.jsx_text_input.setPlaceholderText(tr("advanced_extractor.text_placeholder", "Paste HTML/JSX text here..."))
        self.jsx_text_input.setFixedHeight(150)
        self.jsx_text_input.setVisible(False)  # Hidden by default
        layout.addWidget(self.jsx_text_input)
        
        # Mode and parameter section
        mode_layout = QHBoxLayout()
        
        mode_layout.addWidget(QLabel(tr("advanced_extractor.param", "Param/Attribute:")))
        self.jsx_param_edit = QLineEdit()
        self.jsx_param_edit.setPlaceholderText(tr("advanced_extractor.param_placeholder", "e.g., label, title"))
        mode_layout.addWidget(self.jsx_param_edit)
        
        self.jsx_is_attribute_checkbox = QCheckBox(
            tr("advanced_extractor.is_attribute", "Treat as ATTRIBUTE?")
        )
        self.jsx_is_attribute_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.is_attribute_tooltip",
                      "Attribute mode: extract attribute values\nTag-content mode: extract tag contents")
        )
        mode_layout.addWidget(self.jsx_is_attribute_checkbox)
        
        mode_layout.addWidget(QLabel(tr("advanced_extractor.mode", "Mode:")))
        self.jsx_mode_combo = QComboBox()
        self.jsx_mode_combo.addItems([tr("combo.mode_jsx"), tr("combo.mode_generic")])
        self.jsx_mode_combo.currentTextChanged.connect(self._jsx_toggle_generic_fields)
        mode_layout.addWidget(self.jsx_mode_combo)
        
        layout.addLayout(mode_layout)
        
        # Generic delimiters section
        delimiters_layout = QHBoxLayout()
        
        delimiters_layout.addWidget(QLabel(tr("advanced_extractor.start_delim", "Start (regex):")))
        self.jsx_start_edit = QLineEdit("<.*?>")
        delimiters_layout.addWidget(self.jsx_start_edit, 1)
        
        delimiters_layout.addWidget(QLabel(tr("advanced_extractor.end_delim", "End (regex):")))
        self.jsx_end_edit = QLineEdit("</.*?>")
        delimiters_layout.addWidget(self.jsx_end_edit, 1)
        
        delimiters_layout.addWidget(QLabel(tr("advanced_extractor.extensions", "Extensions:")))
        self.jsx_extensions_edit = QLineEdit(".tsx .jsx .js .ts")
        self.jsx_extensions_edit.setPlaceholderText(tr("advanced_extractor.placeholder_extensions"))
        delimiters_layout.addWidget(self.jsx_extensions_edit, 1)
        
        layout.addLayout(delimiters_layout)
        
        # Options checkboxes (11 options in 4 rows)
        # Row 1
        options_row1 = QHBoxLayout()
        self.jsx_include_key_checkbox = QCheckBox(
            tr("advanced_extractor.include_key", "Include key")
        )
        self.jsx_include_key_checkbox.setChecked(True)
        options_row1.addWidget(self.jsx_include_key_checkbox)
        
        self.jsx_include_value_checkbox = QCheckBox(
            tr("advanced_extractor.include_value", "Include value")
        )
        self.jsx_include_value_checkbox.setChecked(True)
        options_row1.addWidget(self.jsx_include_value_checkbox)
        
        self.jsx_no_standard_checkbox = QCheckBox(
            tr("advanced_extractor.no_standard", "Drop standard HTML tags")
        )
        self.jsx_no_standard_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.no_standard_tooltip",
                      "Remove standard HTML tags like div, span, p, etc.")
        )
        options_row1.addWidget(self.jsx_no_standard_checkbox)
        
        self.jsx_only_strings_checkbox = QCheckBox(
            tr("advanced_extractor.only_strings", "Only strings")
        )
        self.jsx_only_strings_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.only_strings_tooltip",
                      "Filter out expressions, variables, and operations")
        )
        options_row1.addWidget(self.jsx_only_strings_checkbox)
        
        layout.addLayout(options_row1)
        
        # Options grid (2 rows x 4 columns)
        options_grid = QGridLayout()
        options_grid.setSpacing(10)
        
        # Row 0
        self.jsx_quotation_marks_checkbox = QCheckBox(
            tr("advanced_extractor.quotation_marks", "Include quotation marks")
        )
        self.jsx_quotation_marks_checkbox.setChecked(True)  # Default: checked
        options_grid.addWidget(self.jsx_quotation_marks_checkbox, 0, 0)
        
        self.jsx_match_all_checkbox = QCheckBox(
            tr("advanced_extractor.match_all", "Match all")
        )
        self.jsx_match_all_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.match_all_tooltip",
                      "Match all occurrences instead of specific parameter")
        )
        options_grid.addWidget(self.jsx_match_all_checkbox, 0, 1)
        
        self.jsx_typescript_export_checkbox = QCheckBox(
            tr("advanced_extractor.typescript_export", "TypeScript export")
        )
        self.jsx_typescript_export_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.typescript_export_tooltip",
                      "Export as TypeScript interface instead of JSON")
        )
        options_grid.addWidget(self.jsx_typescript_export_checkbox, 0, 2)
        
        self.jsx_exclude_numeric_checkbox = QCheckBox(
            tr("advanced_extractor.exclude_numeric", "Exclude numeric keys")
        )
        self.jsx_exclude_numeric_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.exclude_numeric_tooltip",
                      "Filter out keys that are numeric strings")
        )
        options_grid.addWidget(self.jsx_exclude_numeric_checkbox, 0, 3)
        
        # Row 1
        self.jsx_skip_empty_checkbox = QCheckBox(
            tr("advanced_extractor.skip_empty", "Skip empty values")
        )
        self.jsx_skip_empty_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.skip_empty_tooltip",
                      "Skip entries with empty or null values")
        )
        options_grid.addWidget(self.jsx_skip_empty_checkbox, 1, 0)
        
        self.jsx_swap_checkbox = QCheckBox(tr("text_to_json.btn_swap", "Swap (JSON → JSX)"))
        self.jsx_swap_checkbox.toggled.connect(self._jsx_swap_toggled)
        self.jsx_swap_checkbox.setToolTip(
            tooltip_tr("text_to_json.swap_checkbox_jsx", 
                      "Enable swap mode: Convert JSON output back to JSX code")
        )
        options_grid.addWidget(self.jsx_swap_checkbox, 1, 1)
        
        self.jsx_use_class_names_checkbox = QCheckBox(
            tr("advanced_extractor.use_class_names", "HTML tags → class name")
        )
        self.jsx_use_class_names_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.use_class_names_tooltip",
                      "Use class names as keys instead of HTML tags. "
                      "Multiple classes joined with dash. Falls back to tag if no class.")
        )
        options_grid.addWidget(self.jsx_use_class_names_checkbox, 1, 2)
        
        # Column 3 in row 1 is empty for future expansion
        
        layout.addLayout(options_grid)
        
        # Case style and limits section
        case_layout = QHBoxLayout()
        
        case_layout.addWidget(QLabel(tr("advanced_extractor.case", "Case:")))
        self.jsx_case_combo = QComboBox()
        self.jsx_case_combo.addItems([tr("combo.case_snake"), tr("combo.case_camel"), tr("combo.case_pascal"), tr("combo.case_kebab")])
        case_layout.addWidget(self.jsx_case_combo)
        
        self.jsx_uppercase_checkbox = QCheckBox(
            tr("advanced_extractor.uppercase", "Uppercase token")
        )
        case_layout.addWidget(self.jsx_uppercase_checkbox)
        
        case_layout.addWidget(QLabel(tr("advanced_extractor.limit", "Limit:")))
        self.jsx_limit_edit = QLineEdit("all")
        self.jsx_limit_edit.setMaximumWidth(80)
        case_layout.addWidget(self.jsx_limit_edit)
        
        self.jsx_avoid_cut_checkbox = QCheckBox(
            tr("advanced_extractor.avoid_cut", "Avoid cut")
        )
        self.jsx_avoid_cut_checkbox.setToolTip(
            tooltip_tr("advanced_extractor.avoid_cut_tooltip",
                      "Truncate at word boundaries")
        )
        case_layout.addWidget(self.jsx_avoid_cut_checkbox)
        
        case_layout.addWidget(QLabel(tr("advanced_extractor.indent", "Indent:")))
        self.jsx_indent_spin = QSpinBox()
        self.jsx_indent_spin.setRange(0, 16)
        self.jsx_indent_spin.setValue(2)
        self.jsx_indent_spin.setMaximumWidth(60)
        case_layout.addWidget(self.jsx_indent_spin)
        
        layout.addLayout(case_layout)
        
        # Avoid keys section
        avoid_row1 = QHBoxLayout()
        avoid_row1.addWidget(QLabel(
            tr("advanced_extractor.avoid_keys", "Keys/values to avoid (comma-separated):")
        ))
        self.jsx_avoid_keys_edit = QLineEdit()
        self.jsx_avoid_keys_edit.setPlaceholderText(tr("advanced_extractor.placeholder_avoid_keys"))
        avoid_row1.addWidget(self.jsx_avoid_keys_edit, 1)
        layout.addLayout(avoid_row1)
        
        avoid_row2 = QHBoxLayout()
        self.jsx_avoid_equals_radio = QRadioButton(
            tr("advanced_extractor.avoid_equals", "Exact match")
        )
        self.jsx_avoid_contains_radio = QRadioButton(
            tr("advanced_extractor.avoid_contains", "Contains")
        )
        
        self.jsx_avoid_mode_group = QButtonGroup(self)
        self.jsx_avoid_mode_group.addButton(self.jsx_avoid_equals_radio)
        self.jsx_avoid_mode_group.addButton(self.jsx_avoid_contains_radio)
        self.jsx_avoid_equals_radio.setChecked(True)
        
        avoid_row2.addWidget(self.jsx_avoid_equals_radio)
        avoid_row2.addWidget(self.jsx_avoid_contains_radio)
        avoid_row2.addStretch(1)
        layout.addLayout(avoid_row2)
        
        # Output tabs (MOVED BEFORE BUTTONS)
        self.jsx_output_tabs = QTabWidget()
        
        self.jsx_paths_output = QPlainTextEdit()
        self.jsx_paths_output.setReadOnly(True)
        self.jsx_paths_output.setMinimumHeight(300)
        self.jsx_paths_output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.jsx_paths_output.customContextMenuRequested.connect(self._jsx_show_context_menu)
        self.jsx_output_tabs.addTab(
            self.jsx_paths_output,
            tr("advanced_extractor.tab_paths", "Paths")
        )
        
        self.jsx_json_output = QPlainTextEdit()
        self.jsx_json_output.setReadOnly(True)
        self.jsx_json_output.setMinimumHeight(300)
        self.jsx_json_output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.jsx_json_output.customContextMenuRequested.connect(self._jsx_show_context_menu)
        self.jsx_output_tabs.addTab(
            self.jsx_json_output,
            tr("advanced_extractor.tab_json", "JSON")
        )
        
        layout.addWidget(self.jsx_output_tabs, 1)
        
        # Status label (below output tabs, before button grid)
        self.jsx_status_label = QLabel("")
        self.jsx_status_label.setStyleSheet("color: gray;")
        self.jsx_status_label.setWordWrap(True)
        layout.addWidget(self.jsx_status_label)
        
        # Action buttons - Grid Layout (MOVED TO BOTTOM)
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(8)
        
        # Row 1: Primary actions
        self.jsx_run_btn = QPushButton(tr("base.run", "Extract/Convert"))
        self.jsx_run_btn.setMinimumWidth(120)
        self.jsx_run_btn.clicked.connect(self._jsx_run_extraction)
        buttons_grid.addWidget(self.jsx_run_btn, 0, 0)
        
        self.jsx_templates_btn = QPushButton(tr("text_to_json.btn_templates", "Templates"))
        self.jsx_templates_btn.setMinimumWidth(100)
        self.jsx_templates_btn.clicked.connect(self._jsx_show_templates)
        buttons_grid.addWidget(self.jsx_templates_btn, 0, 1)
        
        self.jsx_clear_btn = QPushButton(tr("text_to_json.btn_clear", "Clear"))
        self.jsx_clear_btn.setMinimumWidth(100)
        self.jsx_clear_btn.clicked.connect(self._jsx_clear_all)
        buttons_grid.addWidget(self.jsx_clear_btn, 0, 2)
        
        # Row 2: Output actions
        self.jsx_validate_btn = QPushButton(tr("text_to_json.btn_validate", "Validate JSON"))
        self.jsx_validate_btn.setMinimumWidth(120)
        self.jsx_validate_btn.clicked.connect(self._jsx_validate_json)
        buttons_grid.addWidget(self.jsx_validate_btn, 1, 0)
        
        self.jsx_copy_result_btn = QPushButton(tr("text_to_json.btn_copy", "Copy JSON"))
        self.jsx_copy_result_btn.setMinimumWidth(100)
        self.jsx_copy_result_btn.clicked.connect(self._jsx_copy_json)
        buttons_grid.addWidget(self.jsx_copy_result_btn, 1, 1)
        
        self.jsx_open_editor_btn = QPushButton(tr("text_to_json.btn_open_editor", "Open in Editor"))
        self.jsx_open_editor_btn.setMinimumWidth(120)
        self.jsx_open_editor_btn.clicked.connect(self._jsx_open_in_editor)
        buttons_grid.addWidget(self.jsx_open_editor_btn, 1, 2)
        
        # Row 3: File and advanced actions
        self.jsx_save_btn = QPushButton(tr("base.save", "Save Outputs"))
        self.jsx_save_btn.setMinimumWidth(120)
        self.jsx_save_btn.clicked.connect(self._jsx_save_outputs)
        buttons_grid.addWidget(self.jsx_save_btn, 2, 0)
        
        self.jsx_history_btn = QPushButton(tr("text_to_json.btn_history", "History"))
        self.jsx_history_btn.setMinimumWidth(100)
        self.jsx_history_btn.clicked.connect(self._jsx_show_history)
        buttons_grid.addWidget(self.jsx_history_btn, 2, 1)
        
        self.jsx_swap_btn = QPushButton(tr("text_to_json.btn_swap", "Swap (JSON → JSX)"))
        self.jsx_swap_btn.setMinimumWidth(150)
        self.jsx_swap_btn.clicked.connect(self._jsx_swap_outputs)
        buttons_grid.addWidget(self.jsx_swap_btn, 2, 2)
        
        # Row 4: Copy actions
        self.jsx_copy_paths_btn = QPushButton(tr("base.copy_paths", "Copy Paths"))
        self.jsx_copy_paths_btn.setMinimumWidth(100)
        self.jsx_copy_paths_btn.clicked.connect(self._jsx_copy_paths)
        buttons_grid.addWidget(self.jsx_copy_paths_btn, 3, 0)
        
        self.jsx_copy_all_btn = QPushButton(tr("base.copy_all", "Copy All"))
        self.jsx_copy_all_btn.setMinimumWidth(100)
        self.jsx_copy_all_btn.clicked.connect(self._jsx_copy_all)
        buttons_grid.addWidget(self.jsx_copy_all_btn, 3, 1)
        
        layout.addLayout(buttons_grid)
    
    # ========================================================================
    # SIGNAL CONNECTIONS
    # ========================================================================
    
    def _connect_signals(self) -> None:
        """Connect all signals after UI creation."""
        # JSX Extraction avoid keys mode toggle
        self.jsx_avoid_equals_radio.toggled.connect(self._jsx_update_avoid_mode)
        self.jsx_avoid_contains_radio.toggled.connect(self._jsx_update_avoid_mode)
        
        # Initial state for JSX generic fields
        self._jsx_toggle_generic_fields(self.jsx_mode_combo.currentText())
    
    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips."""
        # Format Conversion tooltips
        self.fc_format_combo.setToolTip(tooltip_tr("text_to_json.format_combo"))
        self.fc_type_auto_radio.setToolTip(tooltip_tr("text_to_json.type_auto_radio"))
        self.fc_type_string_radio.setToolTip(tooltip_tr("text_to_json.type_string_radio"))
        self.fc_csv_header_check.setToolTip(tooltip_tr("text_to_json.csv_header_check"))
        self.fc_csv_separator_combo.setToolTip(tooltip_tr("text_to_json.csv_separator_combo"))
        self.fc_csv_array_objects_radio.setToolTip(tooltip_tr("text_to_json.csv_array_objects_radio"))
        self.fc_csv_array_arrays_radio.setToolTip(tooltip_tr("text_to_json.csv_array_arrays_radio"))
        self.fc_pretty_print_check.setToolTip(tooltip_tr("text_to_json.pretty_print_check"))
        self.fc_live_preview_check.setToolTip(tooltip_tr("text_to_json.live_preview_check"))
        self.fc_convert_btn.setToolTip(tooltip_tr("text_to_json.convert_btn"))
        self.fc_templates_btn.setToolTip(tooltip_tr("text_to_json.templates_btn"))
        self.fc_clear_btn.setToolTip(tooltip_tr("text_to_json.clear_btn"))
        self.fc_validate_btn.setToolTip(tooltip_tr("text_to_json.validate_btn"))
        self.fc_copy_btn.setToolTip(tooltip_tr("text_to_json.copy_btn"))
        self.fc_open_editor_btn.setToolTip(tooltip_tr("text_to_json.open_editor_btn"))
        self.fc_history_btn.setToolTip(tooltip_tr("text_to_json.history_btn"))
        self.fc_swap_checkbox.setToolTip(tooltip_tr("text_to_json.swap_checkbox", "Enable swap mode: Convert JSON back to text format"))
        self.fc_input_text.setToolTip(tooltip_tr("text_to_json.input_text"))
        self.fc_output_text.setToolTip(tooltip_tr("text_to_json.output_text"))
        self.fc_status_label.setToolTip(tooltip_tr("text_to_json.status_label"))
    
    # ========================================================================
    # FORMAT CONVERSION METHODS (from text_to_json_dock.py)
    # ========================================================================
    
    def _on_input_changed(self) -> None:
        """Handle input text changes for live preview."""
        if self.fc_live_preview_check.isChecked():
            self.live_preview_timer.stop()
            self.live_preview_timer.start(500)
    
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
        return format_map.get(self.fc_format_combo.currentText(), "auto")
    
    def _get_csv_separator(self) -> str:
        """Get CSV separator from combo."""
        separator_map = {
            "Comma (,)": ",",
            "Semicolon (;)": ";",
            "Tab (\\t)": "\t"
        }
        return separator_map.get(self.fc_csv_separator_combo.currentText(), ",")
    
    def _on_convert_clicked(self) -> None:
        """Convert text to JSON."""
        input_text = self.fc_input_text.toPlainText().strip()
        
        if not input_text:
            self.show_warning(tr("text_to_json.warn_empty_input_title"), tr("text_to_json.warn_empty_input_msg"))
            return
        
        try:
            format_type = self._get_format_key()
            infer_types = self.fc_type_auto_radio.isChecked()
            
            kwargs = {}
            if format_type == "csv" or format_type == "auto":
                kwargs['has_header'] = self.fc_csv_header_check.isChecked()
                kwargs['delimiter'] = self._get_csv_separator()
                kwargs['array_of_objects'] = self.fc_csv_array_objects_radio.isChecked()
            
            result = convert_text_to_json(input_text, format_type, infer_types, **kwargs)
            
            if self.fc_pretty_print_check.isChecked():
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                json_str = json.dumps(result, ensure_ascii=False)
            
            self.fc_output_text.setPlainText(json_str)
            
            detected_format = detect_format(input_text) if format_type == "auto" else format_type
            self.fc_status_label.setText(f"✓ Conversion successful (format: {detected_format})")
            self.fc_status_label.setStyleSheet("color: green;")
            
            self._add_to_history(input_text, json_str, detected_format)
            
        except Exception as e:
            self.show_error(tr("text_to_json.error_conversion_title"), tr("text_to_json.error_conversion_msg").replace("{error}", str(e)))
            self.fc_status_label.setText(f"✗ Conversion failed: {str(e)}")
            self.fc_status_label.setStyleSheet("color: red;")
    
    def _on_templates_clicked(self) -> None:
        """Show templates dialog."""
        dialog = TemplatesDialog(self)
        if dialog.exec():
            template_text = dialog.get_selected_template()
            self.fc_input_text.setPlainText(template_text)
    
    def _on_clear_clicked(self) -> None:
        """Clear input and output."""
        self.fc_input_text.clear()
        self.fc_output_text.clear()
        self.fc_status_label.setText("")
    
    def _on_validate_clicked(self) -> None:
        """Validate output JSON."""
        json_str = self.fc_output_text.toPlainText().strip()
        
        if not json_str:
            self.show_warning(tr("text_to_json.warn_empty_output_title"), tr("text_to_json.warn_empty_output_validate"))
            return
        
        try:
            json.loads(json_str)
            self.show_info(tr("text_to_json.info_valid_title"), tr("text_to_json.info_valid_msg"))
            self.fc_status_label.setText(tr("text_to_json.status_valid"))
            self.fc_status_label.setStyleSheet("color: green;")
        except json.JSONDecodeError as e:
            self.show_error(tr("text_to_json.error_invalid_title"), tr("text_to_json.error_invalid_msg").replace("{error}", str(e)))
            self.fc_status_label.setText(f"✗ Invalid JSON: {str(e)}")
            self.fc_status_label.setStyleSheet("color: red;")
    
    def _on_copy_clicked(self) -> None:
        """Copy output JSON to clipboard."""
        json_str = self.fc_output_text.toPlainText()
        
        if not json_str:
            self.show_warning(tr("text_to_json.warn_empty_output_title"), tr("text_to_json.warn_empty_output_copy"))
            return
        
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(json_str)
        
        self.show_info(tr("text_to_json.info_copied_title"), tr("text_to_json.info_copied_msg"))
        self.fc_status_label.setText(tr("text_to_json.status_copied"))
        self.fc_status_label.setStyleSheet("color: green;")
    
    def _on_open_editor_clicked(self) -> None:
        """Open result in main editor."""
        json_str = self.fc_output_text.toPlainText()
        
        if not json_str:
            self.show_warning(tr("text_to_json.warn_empty_output_title"), tr("text_to_json.warn_empty_output_editor"))
            return
        
        self.open_in_editor_requested.emit(json_str)
        self.fc_status_label.setText(tr("text_to_json.status_opened_editor"))
        self.fc_status_label.setStyleSheet("color: green;")
    
    def _on_history_clicked(self) -> None:
        """Show conversion history."""
        if not self.conversion_history:
            self.show_info(tr("text_to_json.info_history_empty_title"), tr("text_to_json.info_history_empty_msg"))
            return
        
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
            self.fc_input_text.setPlainText(entry['input'])
            self.fc_output_text.setPlainText(entry['output'])
            dialog.accept()
    
    def _on_swap_toggled(self, checked: bool) -> None:
        """Handle swap checkbox toggle - swap input/output fields and enable swap mode."""
        if checked:
            # Swap mode enabled: JSON → Text
            # Swap the contents of input and output fields
            input_content = self.fc_input_text.toPlainText()
            output_content = self.fc_output_text.toPlainText()
            
            self.fc_input_text.setPlainText(output_content)
            self.fc_output_text.setPlainText(input_content)
            
            # Update labels to reflect swap mode
            self.fc_input_label.setText(tr("text_to_json.lbl_input_swap", "Input (JSON):"))
            self.fc_output_label.setText(tr("text_to_json.lbl_output_swap", "Output (Text):"))
            
            self.fc_status_label.setText(tr("text_to_json.swap_mode_enabled", "Swap mode: JSON → Text"))
            self.fc_status_label.setStyleSheet("color: blue;")
        else:
            # Normal mode: Text → JSON
            # Swap back the contents
            input_content = self.fc_input_text.toPlainText()
            output_content = self.fc_output_text.toPlainText()
            
            self.fc_input_text.setPlainText(output_content)
            self.fc_output_text.setPlainText(input_content)
            
            # Restore original labels
            self.fc_input_label.setText(tr("text_to_json.lbl_input", "Input:"))
            self.fc_output_label.setText(tr("text_to_json.lbl_output", "Output:"))
            
            self.fc_status_label.setText("")
            self.fc_status_label.setStyleSheet("color: gray;")
    
    def _add_to_history(self, input_text: str, output_json: str, format_type: str) -> None:
        """Add conversion to history."""
        entry = {
            'input': input_text,
            'output': output_json,
            'format': format_type
        }
        self.conversion_history.append(entry)
        
        if len(self.conversion_history) > 50:
            self.conversion_history.pop(0)
    
    # ========================================================================
    # JSX EXTRACTION METHODS (from advanced_extractor_dock.py)
    # ========================================================================
    
    def _jsx_toggle_generic_fields(self, mode: str):
        """Enable/disable generic mode fields based on mode selection."""
        is_generic = (mode == "generic")
        self.jsx_start_edit.setEnabled(is_generic)
        self.jsx_end_edit.setEnabled(is_generic)
    
    def _jsx_on_input_type_changed(self, index: int):
        """Handle input type dropdown change (Directory/File/Text)."""
        input_types = ["directory", "file", "text"]
        selected_type = input_types[index]
        
        if selected_type == "text":
            # Text mode: Hide path field, show text area
            self.jsx_path_edit.setVisible(False)
            self.jsx_browse_btn.setText(tr("advanced_extractor.load_file", "Load from File..."))
            self.jsx_text_input.setVisible(True)
            self.jsx_extensions_edit.setEnabled(False)
        else:
            # Directory/File mode: Show path field, hide text area
            self.jsx_path_edit.setVisible(True)
            self.jsx_browse_btn.setText(tr("base.btn_browse", "Browse"))
            self.jsx_text_input.setVisible(False)
            self.jsx_extensions_edit.setEnabled(True)
    
    def _jsx_update_avoid_mode(self):
        """Update avoid keys matching mode."""
        if self.jsx_avoid_equals_radio.isChecked():
            self.avoid_keys_parameter = self.EQUALS
        elif self.jsx_avoid_contains_radio.isChecked():
            self.avoid_keys_parameter = self.CONTAINS
    
    def _jsx_update_status(self, message: str) -> None:
        """
        Update JSX status label with message.
        Auto-clears after 3 seconds if message is not empty.
        Uses gray color matching Format Conversion style.
        """
        self.jsx_status_label.setText(message)
        self.jsx_status_label.setStyleSheet("color: gray;")
        
        # Auto-clear after 3 seconds if message is not empty
        if message:
            QTimer.singleShot(3000, lambda: self.jsx_status_label.setText(""))
    
    def _jsx_browse_path(self):
        """Browse for file or directory, or load file content in Text mode."""
        input_type_index = self.jsx_input_type_combo.currentIndex()
        
        if input_type_index == 2:  # Text mode
            # Load from File... - opens file and pastes content into text area
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                tr("advanced_extractor.load_file_dialog", "Load File Content"),
                "",
                "All Files (*);;HTML Files (*.html *.htm);;JSX/TSX Files (*.jsx *.tsx);;JavaScript Files (*.js *.ts)"
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.jsx_text_input.setPlainText(content)
                except Exception as e:
                    self.show_error(
                        tr("advanced_extractor.error", "Error"),
                        tr("advanced_extractor.load_error", f"Failed to load file: {str(e)}")
                    )
        elif input_type_index == 1:  # File mode
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                tr("advanced_extractor.select_file", "Select file")
            )
            if file_path:
                self.jsx_path_edit.setText(file_path)
        else:  # Directory mode (index 0)
            dir_path = QFileDialog.getExistingDirectory(
                self,
                tr("advanced_extractor.select_dir", "Select directory")
            )
            if dir_path:
                self.jsx_path_edit.setText(dir_path)
    
    def _jsx_run_extraction(self):
        """Execute the extraction with current settings."""
        try:
            input_type_index = self.jsx_input_type_combo.currentIndex()
            
            # Determine input source
            if input_type_index == 2:  # Text mode
                text_content = self.jsx_text_input.toPlainText().strip()
                if not text_content:
                    self.show_warning(
                        tr("advanced_extractor.error", "Error"),
                        tr("advanced_extractor.no_text", "Please provide HTML/JSX text.")
                    )
                    return
                # Use temporary in-memory processing
                path = None
            else:  # Directory or File mode
                path = self.jsx_path_edit.text().strip()
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
                text_content = None
            
            # Collect settings
            param = self.jsx_param_edit.text().strip() or ""
            mode = self.jsx_mode_combo.currentText()
            start_regex = self.jsx_start_edit.text().strip() if mode == "generic" else None
            end_regex = self.jsx_end_edit.text().strip() if mode == "generic" else None
            
            include_key = self.jsx_include_key_checkbox.isChecked()
            include_value = self.jsx_include_value_checkbox.isChecked()
            no_standard = self.jsx_no_standard_checkbox.isChecked()
            only_strings = self.jsx_only_strings_checkbox.isChecked()
            with_quotation_marks = self.jsx_quotation_marks_checkbox.isChecked()
            match_all = self.jsx_match_all_checkbox.isChecked()
            
            case_style = self.jsx_case_combo.currentText()
            to_upper = self.jsx_uppercase_checkbox.isChecked()
            limit = self.jsx_limit_edit.text().strip() or "all"
            avoid_cut = self.jsx_avoid_cut_checkbox.isChecked()
            indent = self.jsx_indent_spin.value()
            
            avoid_keys = self.jsx_avoid_keys_edit.text().strip()
            avoid_keys_param = self.avoid_keys_parameter
            
            typescript_export = self.jsx_typescript_export_checkbox.isChecked()
            exclude_numeric = self.jsx_exclude_numeric_checkbox.isChecked()
            skip_empty = self.jsx_skip_empty_checkbox.isChecked()
            use_class_names = self.jsx_use_class_names_checkbox.isChecked()
            
            is_attribute_mode = self.jsx_is_attribute_checkbox.isChecked()
            exts_text = self.jsx_extensions_edit.text().strip()
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
                match_all=match_all,
                typescript_export=typescript_export,
                exclude_numeric=exclude_numeric,
                skip_empty=skip_empty,
                use_class_names=use_class_names
            )
            
            # Show status: Extracting...
            self._jsx_update_status("Extracting...")
            
            # Run extraction
            if input_type_index == 2:  # Text mode
                # Process text directly without file system
                text_output, json_output = extractor.process_text("TextInput", text_content)
            else:  # Directory/File mode
                text_output, json_output = extractor.run(path)
            
            # Display results
            self.jsx_paths_output.setPlainText(text_output or "")
            self.jsx_json_output.setPlainText(json_output or "")
            
            # Add to extraction history
            input_source = path if path else "TextInput"
            self._jsx_add_to_history(input_source, json_output, mode, param)
            
            # Show success message (dialog + status)
            paths_count = len([line for line in text_output.split('\n') if line.strip()])
            success_msg = f"Extracted {paths_count} paths successfully."
            self._jsx_update_status(f"✓ {success_msg}")
            self.show_info(
                tr("advanced_extractor.success", "Success"),
                tr("advanced_extractor.extracted", success_msg)
            )
            
        except Exception as e:
            error_msg = f"Extraction failed: {str(e)}"
            self._jsx_update_status(f"❌ {error_msg}")
            self.show_error(
                tr("advanced_extractor.error", "Error"),
                tr("advanced_extractor.run_error", error_msg)
            )
    
    def _jsx_save_outputs(self):
        """Save outputs to files."""
        try:
            paths_text = self.jsx_paths_output.toPlainText()
            json_text = self.jsx_json_output.toPlainText()
            
            if not paths_text and not json_text:
                self.show_info(
                    tr("advanced_extractor.nothing_to_save", "Nothing to save"),
                    tr("advanced_extractor.no_outputs", "No outputs to save.")
                )
                return
            
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
            
            self._jsx_update_status("✓ Outputs saved successfully")
            self.show_info(
                tr("advanced_extractor.saved", "Saved"),
                tr("advanced_extractor.outputs_saved", "Outputs saved successfully.")
            )
            
        except Exception as e:
            self._jsx_update_status(f"❌ Failed to save: {str(e)}")
            self.show_error(
                tr("advanced_extractor.error", "Error"),
                tr("advanced_extractor.save_error", f"Failed to save: {str(e)}")
            )
    
    def _jsx_should_filter_line(self, line: str) -> bool:
        """Check if line should be filtered from clipboard copy."""
        s = line.lstrip()
        if s.startswith(">> Sending") or s.startswith(">> SIMULATED") or s.startswith("<<API ERROR"):
            return True
        if re.match(r"^\s*```[A-Za-z0-9_-]*\s*$", s) or s.strip() == "```":
            return True
        return False
    
    def _jsx_copy_all(self):
        """Copy current tab content to clipboard (filtered)."""
        from PySide6.QtWidgets import QApplication
        
        current_widget = self.jsx_output_tabs.currentWidget()
        text = current_widget.toPlainText()
        
        if not text:
            return
        
        lines = text.splitlines()
        filtered = [ln for ln in lines if not self._jsx_should_filter_line(ln)]
        
        compact = []
        prev_blank = False
        for ln in filtered:
            blank = (ln.strip() == "")
            if blank and prev_blank:
                continue
            compact.append(ln)
            prev_blank = blank
        
        QApplication.clipboard().setText("\n".join(compact))
        
        self.show_info(
            tr("advanced_extractor.copied", "Copied"),
            tr("advanced_extractor.copied_message", "Filtered output copied to clipboard.")
        )
    
    def _jsx_show_context_menu(self, position):
        """Show context menu for output text widgets."""
        menu = QMenu(self)
        
        copy_action = QAction(tr("base.copy", "Copy"), self)
        copy_action.triggered.connect(self._jsx_copy_all)
        menu.addAction(copy_action)
        
        export_action = QAction(tr("base.export", "Export"), self)
        export_action.triggered.connect(self._jsx_save_outputs)
        menu.addAction(export_action)
        
        current_widget = self.jsx_output_tabs.currentWidget()
        menu.exec_(current_widget.mapToGlobal(position))
    
    # ========================================================================
    # NEW JSX MODE METHODS - Additional Buttons
    # ========================================================================
    
    def _jsx_show_templates(self):
        """Show templates dialog with JSX/HTML examples."""
        dialog = TemplatesDialog(self, mode="jsx")
        if dialog.exec_() == QDialog.Accepted:
            template = dialog.get_selected_template()
            # For JSX mode, we could load it into path or show it
            # For now, show info message
            self.show_info(
                tr("text_to_json.templates", "Template"),
                tr("text_to_json.template_selected", f"Template selected:\n\n{template[:200]}...")
            )
    
    def _jsx_clear_all(self):
        """Clear all JSX mode fields."""
        self.jsx_path_edit.clear()
        self.jsx_param_edit.clear()
        self.jsx_paths_output.clear()
        self.jsx_json_output.clear()
        self._jsx_update_status("Cleared")
        self.show_info(
            tr("text_to_json.cleared", "Cleared"),
            tr("text_to_json.cleared_message", "All fields cleared.")
        )
    
    def _jsx_validate_json(self):
        """Validate extracted JSON output."""
        json_text = self.jsx_json_output.toPlainText().strip()
        
        if not json_text:
            self.show_warning(
                tr("text_to_json.no_output", "No Output"),
                tr("text_to_json.no_output_message", "No JSON output to validate. Run extraction first.")
            )
            return
        
        try:
            json.loads(json_text)
            self._jsx_update_status("✓ JSON is valid")
            self.show_info(
                tr("text_to_json.valid_json", "Valid JSON"),
                tr("text_to_json.valid_json_message", "The JSON output is valid! ✅")
            )
        except json.JSONDecodeError as e:
            self._jsx_update_status("❌ Invalid JSON")
            self.show_error(
                tr("text_to_json.invalid_json", "Invalid JSON"),
                tr("text_to_json.invalid_json_message", f"JSON validation error:\n\n{str(e)}")
            )
    
    def _jsx_copy_json(self):
        """Copy JSON output to clipboard."""
        json_text = self.jsx_json_output.toPlainText()
        if json_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(json_text)
            self._jsx_update_status("✓ JSON copied to clipboard")
            self.show_info(
                tr("text_to_json.copied", "Copied"),
                tr("text_to_json.copied_message", "JSON output copied to clipboard.")
            )
        else:
            self.show_warning(
                tr("text_to_json.no_output", "No Output"),
                tr("text_to_json.no_output_message", "No JSON output to copy.")
            )
    
    def _jsx_copy_paths(self):
        """Copy paths output to clipboard."""
        paths_text = self.jsx_paths_output.toPlainText()
        if paths_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(paths_text)
            self._jsx_update_status("✓ Paths copied to clipboard")
            self.show_info(
                tr("text_to_json.copied", "Copied"),
                tr("text_to_json.copied_message", "Paths output copied to clipboard.")
            )
        else:
            self.show_warning(
                tr("text_to_json.no_output", "No Output"),
                tr("text_to_json.no_output_message", "No paths output to copy.")
            )
    
    def _jsx_open_in_editor(self):
        """Open extracted JSON in editor."""
        json_text = self.jsx_json_output.toPlainText().strip()
        
        if not json_text:
            self.show_warning(
                tr("text_to_json.no_output", "No Output"),
                tr("text_to_json.no_output_message", "No JSON output to open. Run extraction first.")
            )
            return
        
        # Emit signal to open in editor
        self.open_in_editor_requested.emit(json_text)
        self._jsx_update_status("✓ Opened in editor")
    
    def _jsx_show_history(self):
        """Show extraction history."""
        if not self.extraction_history:
            self.show_info(
                tr("text_to_json.info_history_empty_title", "History Empty"),
                tr("text_to_json.info_history_empty_msg", "No extraction history yet. Run an extraction first.")
            )
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("text_to_json.history_dialog_title", "Extraction History"))
        dialog.resize(700, 450)
        
        layout = QVBoxLayout(dialog)
        
        list_widget = QListWidget()
        for i, entry in enumerate(reversed(self.extraction_history)):
            mode_str = entry.get('mode', 'unknown')
            param_str = entry.get('parameter', 'N/A')
            path_preview = entry['path'].split('/')[-1] if '/' in entry['path'] else entry['path']
            item_text = f"{i+1}. [{mode_str}] {path_preview} (param: {param_str})"
            list_widget.addItem(item_text)
        
        list_widget.itemDoubleClicked.connect(lambda item: self._jsx_load_history_item(item, dialog))
        
        layout.addWidget(QLabel(tr("text_to_json.history_lbl_double_click", "Double-click to load extraction")))
        layout.addWidget(list_widget)
        
        close_btn = QPushButton(tr("text_to_json.btn_close", "Close"))
        close_btn.clicked.connect(dialog.reject)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _jsx_load_history_item(self, item: QListWidgetItem, dialog: QDialog) -> None:
        """Load history item into JSX extraction fields."""
        index = len(self.extraction_history) - 1 - item.listWidget().row(item)
        if 0 <= index < len(self.extraction_history):
            entry = self.extraction_history[index]
            self.jsx_path_edit.setText(entry['path'])
            self.jsx_param_edit.setText(entry.get('parameter', ''))
            self.jsx_json_output.setPlainText(entry['output'])
            
            # Set mode if possible
            mode_str = entry.get('mode', 'JSX')
            mode_index = self.jsx_mode_combo.findText(mode_str)
            if mode_index >= 0:
                self.jsx_mode_combo.setCurrentIndex(mode_index)
            
            dialog.accept()
    
    def _jsx_add_to_history(self, path: str, output_json: str, mode: str, parameter: str) -> None:
        """Add extraction to history."""
        entry = {
            'path': path,
            'output': output_json,
            'mode': mode,
            'parameter': parameter
        }
        self.extraction_history.append(entry)
        
        # Keep history limited to 50 entries
        if len(self.extraction_history) > 50:
            self.extraction_history.pop(0)
    
    def _jsx_swap_outputs(self):
        """Swap JSON output back to JSX code (JSON → JSX conversion)."""
        json_text = self.jsx_json_output.toPlainText().strip()
        
        if not json_text:
            self.show_warning(
                tr("text_to_json.no_output", "No Output"),
                tr("text_to_json.no_output_message", "No JSON output to convert. Run extraction first.")
            )
            return
        
        try:
            # Parse JSON
            json_data = json.loads(json_text)
            
            # Convert JSON to JSX
            jsx_output = self._json_to_jsx(json_data)
            
            # Put JSX output in paths tab (since it's text output)
            self.jsx_paths_output.setPlainText(jsx_output)
            
            # Switch to Paths tab to show result
            self.jsx_output_tabs.setCurrentIndex(0)
            
            self.show_info(
                tr("text_to_json.swap", "Swap Complete"),
                tr("text_to_json.swap_success", f"JSON converted to JSX code! ({len(jsx_output)} characters)")
            )
            
        except json.JSONDecodeError as e:
            self.show_error(
                tr("text_to_json.invalid_json", "Invalid JSON"),
                tr("text_to_json.invalid_json_message", f"Cannot convert invalid JSON:\n\n{str(e)}")
            )
        except Exception as e:
            self.show_error(
                tr("text_to_json.error", "Error"),
                tr("text_to_json.swap_error", f"Swap failed: {str(e)}")
            )
    
    def _jsx_swap_toggled(self, checked: bool) -> None:
        """Handle JSX swap checkbox toggle - automatically trigger swap when checked."""
        if checked:
            # Call the swap method to convert JSON → JSX
            self._jsx_swap_outputs()
        # Note: When unchecked, we don't do anything (user can manually clear if needed)
    
    def _json_to_jsx(self, data: Any, tag_name: str = "Component", indent_level: int = 0) -> str:
        """
        Convert JSON data to JSX code (basic implementation).
        
        Args:
            data: JSON data (dict, list, or primitive)
            tag_name: Tag name for the component
            indent_level: Current indentation level
        
        Returns:
            JSX code string
        """
        indent = "  " * indent_level
        
        if isinstance(data, dict):
            # Dictionary → JSX element with attributes
            if not data:
                return f"{indent}<{tag_name} />"
            
            # Separate text content from attributes
            text_content = data.pop('_text', None) if '_text' in data else None
            children = data.pop('_children', None) if '_children' in data else None
            
            # Build attributes
            attrs = []
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    if isinstance(value, bool):
                        attrs.append(f'{key}={{{str(value).lower()}}}')
                    elif isinstance(value, str):
                        attrs.append(f'{key}="{value}"')
                    else:
                        attrs.append(f'{key}={{{value}}}')
            
            attrs_str = " " + " ".join(attrs) if attrs else ""
            
            # Self-closing tag if no content
            if not text_content and not children:
                return f"{indent}<{tag_name}{attrs_str} />"
            
            # With content
            jsx = f"{indent}<{tag_name}{attrs_str}>\n"
            if text_content:
                jsx += f"{indent}  {text_content}\n"
            if children:
                if isinstance(children, list):
                    for i, child in enumerate(children):
                        jsx += self._json_to_jsx(child, f"Item{i+1}", indent_level + 1) + "\n"
                else:
                    jsx += f"{indent}  {children}\n"
            jsx += f"{indent}</{tag_name}>"
            return jsx
            
        elif isinstance(data, list):
            # List → Multiple JSX elements
            jsx_lines = []
            for i, item in enumerate(data):
                jsx_lines.append(self._json_to_jsx(item, f"{tag_name}{i+1}", indent_level))
            return "\n".join(jsx_lines)
        
        else:
            # Primitive → Text content
            return f"{indent}{data}"
