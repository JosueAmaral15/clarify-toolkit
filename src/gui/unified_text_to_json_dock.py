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
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QRadioButton, QButtonGroup, QCheckBox,
    QPushButton, QPlainTextEdit, QMessageBox, QDialog, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QTabWidget, QFileDialog, QMenu, QApplication,
    QProgressDialog, QTextEdit
)
from PySide6.QtGui import QFont, QAction, QShortcut, QKeySequence, QTextCursor, QTextCharFormat, QColor

from .base_dock import BaseDock, FileInputMixin
from .extraction_worker import ExtractionWorker
from src.text_to_json import convert_text_to_json, detect_format
from src.extractors.advanced_extractor import AdvancedExtractor
from src.i18n.translator import tooltip_tr, tr

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


class TextSearchDialog(QDialog):
    """Search dialog for text input with regex, case-sensitive, and whole-word options."""
    
    def __init__(self, parent=None, text_widget=None):
        super().__init__(parent)
        self.text_widget = text_widget
        self.matches = []  # List of (start, end) tuples
        self.current_match_index = -1
        
        self.setWindowTitle("Search in Text")
        self.setModal(False)  # Non-modal so user can edit text while searching
        self.resize(450, 200)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup search dialog UI."""
        layout = QVBoxLayout(self)
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Find:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._find_next)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Options checkboxes
        options_layout = QHBoxLayout()
        self.regex_checkbox = QCheckBox("Regex")
        self.regex_checkbox.toggled.connect(self._on_options_changed)
        options_layout.addWidget(self.regex_checkbox)
        
        self.case_checkbox = QCheckBox("Case sensitive")
        self.case_checkbox.toggled.connect(self._on_options_changed)
        options_layout.addWidget(self.case_checkbox)
        
        self.whole_word_checkbox = QCheckBox("Whole word")
        self.whole_word_checkbox.toggled.connect(self._on_options_changed)
        options_layout.addWidget(self.whole_word_checkbox)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Match counter
        self.counter_label = QLabel("No matches")
        self.counter_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.counter_label)
        
        # Navigation buttons
        buttons_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self._find_previous)
        self.prev_button.setEnabled(False)
        buttons_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self._find_next)
        self.next_button.setEnabled(False)
        buttons_layout.addWidget(self.next_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def showEvent(self, event):
        """When dialog shows, focus search input and select current word if any."""
        super().showEvent(event)
        self.search_input.setFocus()
        
        # Pre-fill with selected text if any
        if self.text_widget and self.text_widget.textCursor().hasSelection():
            selected_text = self.text_widget.textCursor().selectedText()
            if selected_text:
                self.search_input.setText(selected_text)
                self.search_input.selectAll()
    
    def _on_search_text_changed(self):
        """Handle search text change."""
        self._find_all_matches()
    
    def _on_options_changed(self):
        """Handle search option change."""
        self._find_all_matches()
    
    def _find_all_matches(self):
        """Find all matches based on current search text and options."""
        if not self.text_widget:
            return
        
        search_text = self.search_input.text()
        if not search_text:
            self._clear_highlights()
            self.matches = []
            self.current_match_index = -1
            self._update_ui()
            return
        
        text = self.text_widget.toPlainText()
        self.matches = []
        
        use_regex = self.regex_checkbox.isChecked()
        case_sensitive = self.case_checkbox.isChecked()
        whole_word = self.whole_word_checkbox.isChecked()
        
        if use_regex:
            # Regex search
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_text, flags)
                for match in pattern.finditer(text):
                    # Check whole word if needed
                    if whole_word:
                        if not self._is_whole_word_match(text, match.start(), match.end()):
                            continue
                    self.matches.append((match.start(), match.end()))
            except re.error:
                # Invalid regex
                self.counter_label.setText("Invalid regex pattern")
                self.counter_label.setStyleSheet("color: red;")
                self._clear_highlights()
                return
        else:
            # Plain text search
            if not case_sensitive:
                text_lower = text.lower()
                search_lower = search_text.lower()
            else:
                text_lower = text
                search_lower = search_text
            
            start = 0
            while True:
                pos = text_lower.find(search_lower, start)
                if pos == -1:
                    break
                
                end = pos + len(search_text)
                
                # Check whole word if needed
                if whole_word:
                    if not self._is_whole_word_match(text, pos, end):
                        start = pos + 1
                        continue
                
                self.matches.append((pos, end))
                start = pos + 1
        
        # Reset to first match
        if self.matches:
            self.current_match_index = 0
        else:
            self.current_match_index = -1
        
        self._highlight_all_matches()
        self._update_ui()
    
    def _is_whole_word_match(self, text, start, end):
        """Check if match is a whole word."""
        before_ok = start == 0 or not text[start - 1].isalnum()
        after_ok = end >= len(text) or not text[end].isalnum()
        return before_ok and after_ok
    
    def _highlight_all_matches(self):
        """Highlight all matches in text widget."""
        if not self.text_widget or not self.matches:
            self._clear_highlights()
            return
        
        extra_selections = []
        
        for i, (start, end) in enumerate(self.matches):
            selection = QTextEdit.ExtraSelection()
            
            cursor = self.text_widget.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            
            # Different color for current match
            if i == self.current_match_index:
                # Orange for current match
                format = QTextCharFormat()
                format.setBackground(QColor(255, 165, 0, 150))
            else:
                # Yellow for other matches
                format = QTextCharFormat()
                format.setBackground(QColor(255, 255, 0, 100))
            
            selection.cursor = cursor
            selection.format = format
            extra_selections.append(selection)
        
        self.text_widget.setExtraSelections(extra_selections)
        
        # Scroll to current match
        if self.current_match_index >= 0:
            start, end = self.matches[self.current_match_index]
            cursor = self.text_widget.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            self.text_widget.setTextCursor(cursor)
            self.text_widget.ensureCursorVisible()
    
    def _clear_highlights(self):
        """Clear all highlights from text widget."""
        if self.text_widget:
            self.text_widget.setExtraSelections([])
    
    def _find_next(self):
        """Navigate to next match."""
        if not self.matches:
            return
        
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._highlight_all_matches()
        self._update_ui()
    
    def _find_previous(self):
        """Navigate to previous match."""
        if not self.matches:
            return
        
        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self._highlight_all_matches()
        self._update_ui()
    
    def _update_ui(self):
        """Update UI based on current state."""
        has_matches = len(self.matches) > 0
        
        self.prev_button.setEnabled(has_matches)
        self.next_button.setEnabled(has_matches)
        
        if has_matches:
            self.counter_label.setText(f"Match {self.current_match_index + 1} of {len(self.matches)}")
            self.counter_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            search_text = self.search_input.text()
            if search_text:
                self.counter_label.setText("No matches found")
                self.counter_label.setStyleSheet("color: red;")
            else:
                self.counter_label.setText("Enter text to search")
                self.counter_label.setStyleSheet("color: gray; font-style: italic;")
    
    def closeEvent(self, event):
        """Clear highlights when dialog closes."""
        self._clear_highlights()
        super().closeEvent(event)


class JSXTextSearchDialog(TextSearchDialog):
    """Modal search dialog specifically for JSX text input field."""
    
    def __init__(self, parent=None, text_widget=None):
        super().__init__(parent, text_widget)
        self.setModal(True)  # Make it modal
        self.setWindowTitle(tr("text_search.title_jsx", "Search in JSX Text Input"))


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
        """Update example text and output tab name when format changes."""
        self.example_text.setPlainText(self.TEMPLATES.get(format_name, ""))
        
        # Update parent dock's output tab name to match selected format
        if self.parent() and hasattr(self.parent(), 'jsx_output_tabs'):
            # Tab index 1 is the JSON/format output tab (index 0 is Paths)
            self.parent().jsx_output_tabs.setTabText(1, format_name)
    
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
    open_in_editor_and_switch_requested = Signal(str, bool)  # (content, switch_to_file)
    
    def __init__(self, parent: QWidgetType | None = None):
        # Initialize JSX extraction state BEFORE calling super().__init__
        self.extraction_history: List[Dict[str, str]] = []
        self.avoid_keys_parameter = "equals"
        self.EQUALS = "equals"
        self.CONTAINS = "contains"
        
        # Initialize recent paths list (for Recent button feature)
        from PySide6.QtCore import QSettings
        self.settings = QSettings("Clarify", "TextToJsonConverter")
        self.jsx_recent_paths = self.settings.value("jsx_recent_paths", [], type=list)
        if not isinstance(self.jsx_recent_paths, list):
            self.jsx_recent_paths = []
        
        # Flag to prevent signal processing during cleanup
        self._extraction_cleaning_up = False
        
        super().__init__(tr("text_to_json.title", "Format Converter"), parent)
        self.setObjectName("UnifiedTextToJsonDock")
    
    def _setup_ui(self) -> None:
        """Setup main UI with JSX extraction layout only."""
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)
        
        # Create ONE scroll area wrapping JSX layout
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
        
        # Create only JSX extraction layout
        self._create_jsx_extraction_layout()
        
        # Add JSX layout to container
        self.content_layout.addWidget(self.jsx_extraction_container)
        
        # Put container in scroll area
        scroll_area.setWidget(self.content_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area, 1)  # Stretch factor 1
        
        # Set main widget
        self.setWidget(main_widget)
        
        # Setup CTRL+F shortcut for text search
        self.search_shortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        self.search_shortcut.activated.connect(self._on_search_shortcut)
        
        # Connect signals
        self._connect_signals()
        
        # Apply tooltips
        self._apply_tooltips()
    
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
        
        # Recent button (same as File Explorer)
        self.jsx_recent_btn = QPushButton(tr("file_list.btn_recent", "Recent"))
        self.jsx_recent_btn.setMaximumWidth(100)
        self.jsx_recent_btn.clicked.connect(self._jsx_show_recent_menu)
        path_layout.addWidget(self.jsx_recent_btn)
        
        # Search button (only visible in Text mode)
        self.jsx_search_btn = QPushButton(tr("text_search.btn_search", "Search"))
        self.jsx_search_btn.setMaximumWidth(100)
        self.jsx_search_btn.clicked.connect(self._jsx_open_search_dialog)
        self.jsx_search_btn.setVisible(False)  # Hidden by default
        self.jsx_search_btn.setToolTip(tr("text_search.tooltip_search", "Search in text input (Ctrl+F)"))
        path_layout.addWidget(self.jsx_search_btn)
        
        self.jsx_browse_btn = QPushButton(tr("base.btn_browse", "Browse"))
        self.jsx_browse_btn.setMaximumWidth(200)  # Increased for "Load from File..." text
        self.jsx_browse_btn.clicked.connect(self._jsx_browse_path)
        path_layout.addWidget(self.jsx_browse_btn)
        
        layout.addLayout(path_layout)
        
        # Text input area (visible only in Text mode)
        self.jsx_text_input = QPlainTextEdit()
        self.jsx_text_input.setPlaceholderText(tr("advanced_extractor.text_placeholder", "Paste HTML/JSX text here..."))
        self.jsx_text_input.setFixedHeight(150)
        self.jsx_text_input.setVisible(False)  # Hidden by default
        layout.addWidget(self.jsx_text_input)
        
        # Setup Ctrl+F shortcut for text input (only works when text input has focus)
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self.jsx_text_input)
        search_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        search_shortcut.activated.connect(self._jsx_open_search_dialog)
        
        # Mode and parameter section
        mode_layout = QHBoxLayout()
        
        mode_layout.addWidget(QLabel(tr("advanced_extractor.param", "Param/Attribute:")))
        self.jsx_param_edit = QLineEdit()
        self.jsx_param_edit.setPlaceholderText(tr("advanced_extractor.param_placeholder", "e.g., label, title (or leave empty/* for all)"))
        self.jsx_param_edit.setToolTip(
            "Specify which attribute/parameter to extract.\n"
            "Leave empty or use '*' to extract all (same as 'Match all' checkbox)."
        )
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
                      "Override Parameter field and extract ALL attributes/content.\n"
                      "Note: Parameter field empty or '*' automatically enables this.")
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
        
        # Avoid cut direction dropdown
        self.jsx_avoid_cut_direction_combo = QComboBox()
        self.jsx_avoid_cut_direction_combo.addItems(["Before", "After"])
        self.jsx_avoid_cut_direction_combo.setCurrentIndex(0)  # Default: Before
        self.jsx_avoid_cut_direction_combo.setMaximumWidth(80)
        self.jsx_avoid_cut_direction_combo.setToolTip(
            tooltip_tr("advanced_extractor.avoid_cut_direction",
                      "Before: cut at last word boundary before limit\nAfter: cut at next word boundary after limit")
        )
        self.jsx_avoid_cut_direction_combo.setEnabled(False)  # Disabled by default
        case_layout.addWidget(self.jsx_avoid_cut_direction_combo)
        
        # Connect avoid_cut checkbox to enable/disable direction combo
        self.jsx_avoid_cut_checkbox.toggled.connect(self._jsx_on_avoid_cut_toggled)
        
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
        
        self.jsx_open_switch_btn = QPushButton(tr("text_to_json.btn_open_switch", "Open in Editor and Switch"))
        self.jsx_open_switch_btn.setMinimumWidth(120)
        self.jsx_open_switch_btn.clicked.connect(self._jsx_open_in_editor_and_switch)
        buttons_grid.addWidget(self.jsx_open_switch_btn, 2, 2)
        
        # Note: Swap button removed - using checkbox instead (in options grid)
        
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
        """Apply internationalized tooltips for JSX mode."""
        # Note: JSX tooltips are already set inline during widget creation
        pass
    
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
            # Text mode: Hide path field, show text area and search button
            self.jsx_path_edit.setVisible(False)
            self.jsx_browse_btn.setText(tr("advanced_extractor.load_file", "Load from File..."))
            self.jsx_text_input.setVisible(True)
            self.jsx_search_btn.setVisible(True)
            self.jsx_extensions_edit.setEnabled(False)
        else:
            # Directory/File mode: Show path field, hide text area and search button
            self.jsx_path_edit.setVisible(True)
            self.jsx_browse_btn.setText(tr("base.btn_browse", "Browse"))
            self.jsx_text_input.setVisible(False)
            self.jsx_search_btn.setVisible(False)
            self.jsx_extensions_edit.setEnabled(True)
    
    def _jsx_update_avoid_mode(self):
        """Update avoid keys matching mode."""
        if self.jsx_avoid_equals_radio.isChecked():
            self.avoid_keys_parameter = self.EQUALS
        elif self.jsx_avoid_contains_radio.isChecked():
            self.avoid_keys_parameter = self.CONTAINS
    
    def _jsx_on_avoid_cut_toggled(self, checked: bool) -> None:
        """Enable/disable the avoid cut direction dropdown based on checkbox state."""
        self.jsx_avoid_cut_direction_combo.setEnabled(checked)
    
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
                self._jsx_load_file_to_text(file_path)
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
    
    def _jsx_show_recent_menu(self):
        """Show recent paths menu - mode-aware behavior."""
        if not self.jsx_recent_paths:
            QMessageBox.information(
                self,
                tr("file_list.recent_none_title", "No Recent Paths"),
                tr("file_list.recent_none_message", "No recent paths yet. Browse for files or directories to build your recent list.")
            )
            return
        
        # Get current input mode
        input_mode_index = self.jsx_input_type_combo.currentIndex()
        is_text_mode = (input_mode_index == 2)
        
        # Filter recent paths based on mode
        if is_text_mode:
            # Text mode: Show only files (not directories)
            filtered_paths = [p for p in self.jsx_recent_paths if os.path.isfile(p)]
            if not filtered_paths:
                QMessageBox.information(
                    self,
                    tr("file_list.recent_no_files_title", "No Recent Files"),
                    tr("file_list.recent_no_files_message", "No recent files found. Only files can be loaded in Text mode.")
                )
                return
            paths_to_show = filtered_paths
        else:
            # Directory/File mode: Show all
            paths_to_show = self.jsx_recent_paths
        
        menu = QMenu(self)
        for path in paths_to_show:
            action = QAction(path, self)
            if is_text_mode:
                # Text mode: Load file content
                action.triggered.connect(lambda checked, p=path: self._jsx_load_file_to_text(p))
            else:
                # Directory/File mode: Set path
                action.triggered.connect(lambda checked, p=path: self.jsx_path_edit.setText(p))
            menu.addAction(action)
        
        menu.addSeparator()
        clear_action = QAction(tr("file_list.recent_clear", "Clear Recent"), self)
        clear_action.triggered.connect(self._jsx_clear_recent)
        menu.addAction(clear_action)
        
        menu.exec(self.jsx_recent_btn.mapToGlobal(self.jsx_recent_btn.rect().bottomLeft()))
    
    def _jsx_load_file_to_text(self, file_path: str):
        """Load file content into text input (Text mode only)."""
        if not os.path.isfile(file_path):
            QMessageBox.warning(
                self,
                tr("text_to_json.not_file_title", "Not a File"),
                tr("text_to_json.not_file_message", f"Path is not a file:\n{file_path}")
            )
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.jsx_text_input.setPlainText(content)
                
                # Update hidden path field (for tracking)
                self.jsx_path_edit.setText(file_path)
                
                # Add to recent list
                self._jsx_add_to_recent(file_path)
                
                self._jsx_update_status(tr("text_to_json.file_loaded", f"File loaded: {os.path.basename(file_path)}"))
                
        except UnicodeDecodeError:
            # Binary file error
            QMessageBox.warning(
                self,
                tr("text_to_json.binary_file_title", "Cannot Load Binary File"),
                tr("text_to_json.binary_file_message", f"Cannot load binary file as text:\n{file_path}\n\nPlease select a text file.")
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr("text_to_json.load_error_title", "Load Error"),
                tr("text_to_json.load_error_message", f"Failed to load file:\n{file_path}\n\nError: {str(e)}")
            )
    
    def _jsx_clear_recent(self):
        """Clear recent paths list."""
        self.jsx_recent_paths = []
        self.settings.setValue("jsx_recent_paths", self.jsx_recent_paths)
        QMessageBox.information(
            self,
            tr("file_list.cleared_title", "Cleared"),
            tr("file_list.cleared_message", "Recent paths cleared.")
        )
    
    def _jsx_add_to_recent(self, path: str):
        """Add path to recent list."""
        if not path or not os.path.exists(path):
            return
        
        # Remove if already exists
        if path in self.jsx_recent_paths:
            self.jsx_recent_paths.remove(path)
        
        # Add to beginning
        self.jsx_recent_paths.insert(0, path)
        
        # Keep last 10
        self.jsx_recent_paths = self.jsx_recent_paths[:10]
        
        # Save to settings
        self.settings.setValue("jsx_recent_paths", self.jsx_recent_paths)
    
    def _jsx_run_extraction(self):
        """Execute the extraction with current settings using worker thread."""
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
                
                # Add to recent paths
                self._jsx_add_to_recent(path)
                
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
            avoid_cut_direction = self.jsx_avoid_cut_direction_combo.currentText().lower()
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
            
            # Store settings for history (captured before threading)
            self._extraction_settings = {
                'param': param,
                'mode': mode,
                'input_type': ['Directory', 'File', 'Text'][input_type_index],
                'case_style': case_style,
                'limit': limit,
                'avoid_cut': avoid_cut,
                'avoid_cut_direction': avoid_cut_direction,
                'to_upper': to_upper,
                'indent': indent,
                'include_key': include_key,
                'include_value': include_value,
                'no_standard': no_standard,
                'only_strings': only_strings,
                'with_quotation_marks': with_quotation_marks,
                'match_all': match_all,
                'typescript_export': typescript_export,
                'exclude_numeric': exclude_numeric,
                'skip_empty': skip_empty,
                'use_class_names': use_class_names,
                'is_attribute_mode': is_attribute_mode,
                'avoid_keys': avoid_keys,
                'avoid_keys_param': avoid_keys_param,
                'file_extensions': file_extensions,
                'start_regex': start_regex,
                'end_regex': end_regex
            }
            self._extraction_input_source = path if path else "TextInput"
            
            # Create extractor
            # Note: match_all is auto-derived from param in AdvancedExtractor
            # Note: typescript_export, exclude_numeric, skip_empty, use_class_names 
            #       are handled by ExtractionWorker, not AdvancedExtractor
            extractor = AdvancedExtractor(
                param=param,
                mode=mode,
                avoid_keys=avoid_keys,
                avoid_keys_parameter=avoid_keys_param,
                include_key=include_key,
                include_value=include_value,
                no_standard=no_standard,
                convert_to_json=True,
                with_quotation_marks=with_quotation_marks,
                indentation=indent,
                case_style=case_style,
                limit=limit,
                avoid_cut=avoid_cut,
                avoid_cut_direction=avoid_cut_direction,
                to_upper=to_upper,
                only_strings=only_strings,
                is_attribute_mode=is_attribute_mode,
                start_regex=start_regex,
                end_regex=end_regex,
                file_extensions=file_extensions
            )
            
            # Create progress dialog
            self._extraction_cleaning_up = False  # Reset cleanup flag
            self._extraction_progress = QProgressDialog(
                "Initializing extraction...",
                "Cancel",
                0, 100,
                self
            )
            self._extraction_progress.setWindowTitle("Extracting...")
            self._extraction_progress.setWindowModality(Qt.WindowModal)
            self._extraction_progress.setMinimumDuration(0)
            self._extraction_progress.setMinimumWidth(400)
            self._extraction_progress.setMaximumWidth(600)
            self._extraction_progress.show()
            
            # Create worker thread
            self._extraction_thread = QThread(self)
            self._extraction_worker = ExtractionWorker(extractor)
            self._extraction_worker.moveToThread(self._extraction_thread)
            
            # Connect signals
            self._extraction_worker.progress.connect(self._on_extraction_progress)
            self._extraction_worker.progress_detailed.connect(self._on_extraction_progress_detailed)
            self._extraction_worker.finished.connect(self._on_extraction_finished)
            self._extraction_worker.error.connect(self._on_extraction_error)
            
            # Connect progress dialog cancel to worker cleanup
            self._extraction_progress.canceled.connect(self._on_extraction_canceled)
            
            # Start thread and trigger extraction
            self._extraction_thread.started.connect(
                lambda: self._extraction_worker.execute_extraction(
                    path, text_content, input_type_index,
                    typescript_export, with_quotation_marks, indent
                )
            )
            self._extraction_thread.start()
            
            # Update status
            self._jsx_update_status("Extracting...")
            
        except Exception as e:
            error_msg = f"Extraction failed: {str(e)}"
            self._jsx_update_status(f"❌ {error_msg}")
            self.show_error(
                tr("advanced_extractor.error", "Error"),
                tr("advanced_extractor.run_error", error_msg)
            )
    
    def _on_extraction_progress(self, message: str):
        """Handle progress updates from extraction worker."""
        if self._extraction_cleaning_up:
            return
        
        # Cache reference locally (atomic) to prevent TOCTOU race
        progress = self._extraction_progress
        if progress is None:
            return
        
        try:
            progress.setLabelText(message)
        except RuntimeError:
            pass  # Qt object was deleted
    
    def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
        """Handle detailed progress updates from extraction worker."""
        if self._extraction_cleaning_up:
            return
        
        # Cache reference locally (atomic) to prevent TOCTOU race
        progress = self._extraction_progress
        if progress is None:
            return
        
        try:
            progress.setMaximum(total)
            progress.setValue(current)
            progress.setLabelText(f"[{current}/{total}] {message}")
        except RuntimeError:
            pass  # Qt object was deleted
    
    def _on_extraction_finished(self, text_output: str, json_output: str):
        """Handle extraction completion."""
        try:
            # Display results
            self.jsx_paths_output.setPlainText(text_output or "")
            self.jsx_json_output.setPlainText(json_output or "")
            
            # Add to history
            if hasattr(self, '_extraction_settings'):
                self._jsx_add_to_history(
                    self._extraction_input_source,
                    json_output,
                    self._extraction_settings
                )
            
            # Show success message
            # Count actual paths (exclude comment lines starting with #)
            paths_count = len([
                line for line in text_output.split('\n') 
                if line.strip() and not line.strip().startswith('#')
            ])
            
            # Check for "(no matches)" message
            if text_output.strip() == "(no matches)" or paths_count == 0:
                success_msg = "Extraction completed with no matches found."
            elif paths_count == 1:
                success_msg = "Extracted 1 path successfully."
            else:
                success_msg = f"Extracted {paths_count} paths successfully."
            
            self._jsx_update_status(f"✓ {success_msg}")
            self.show_info(
                tr("advanced_extractor.success", "Success"),
                tr("advanced_extractor.extracted", success_msg)
            )
            
        finally:
            self._cleanup_extraction_thread()
    
    def _on_extraction_error(self, error_msg: str):
        """Handle extraction error."""
        # Don't show status/dialog for user cancellation (already shown)
        if "canceled by user" in error_msg.lower():
            # Cancellation already handled in _on_extraction_canceled
            self._cleanup_extraction_thread()
            return
        
        # Show error for actual failures
        self._jsx_update_status(f"❌ Extraction failed: {error_msg}")
        self.show_error(
            tr("advanced_extractor.error", "Error"),
            tr("advanced_extractor.run_error", f"Extraction failed: {error_msg}")
        )
        self._cleanup_extraction_thread()
    
    def _on_extraction_canceled(self):
        """Handle extraction cancellation."""
        # Set cleanup flag immediately
        self._extraction_cleaning_up = True
        
        # Block signals at Qt level FIRST to stop queued signals
        if hasattr(self, '_extraction_worker') and self._extraction_worker is not None:
            self._extraction_worker.blockSignals(True)
        if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
            self._extraction_progress.blockSignals(True)
        
        # Stop worker
        if hasattr(self, '_extraction_worker') and self._extraction_worker is not None:
            self._extraction_worker._cancel_requested = True
        
        self._jsx_update_status("Extraction canceled")
        self._cleanup_extraction_thread()
    
    def _cleanup_extraction_thread(self):
        """Clean up worker thread and progress dialog."""
        # Set cleanup flag
        self._extraction_cleaning_up = True
        
        # Block signals at Qt level to prevent queued signals from being delivered
        if hasattr(self, '_extraction_worker') and self._extraction_worker is not None:
            self._extraction_worker.blockSignals(True)
        
        # Close progress dialog first (before setting to None)
        if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
            self._extraction_progress.blockSignals(True)  # Block canceled signal
            self._extraction_progress.close()
            self._extraction_progress = None
        
        if hasattr(self, '_extraction_thread') and self._extraction_thread is not None:
            self._extraction_thread.quit()
            self._extraction_thread.wait(5000)  # Wait up to 5 seconds
            if self._extraction_thread.isRunning():
                self._extraction_thread.terminate()
            self._extraction_thread = None
        
        if hasattr(self, '_extraction_worker'):
            self._extraction_worker = None
        
        # Reset cleanup flag
        self._extraction_cleaning_up = False
    
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
        """Copy BOTH tabs content to clipboard (Paths + blank line + JSON)."""
        from PySide6.QtWidgets import QApplication
        
        # Get content from BOTH tabs
        paths_text = self.jsx_paths_output.toPlainText()
        json_text = self.jsx_json_output.toPlainText()
        
        # Debug logging removed - was using print() which violates SIMPLICITY_PROTOCOL_3
        # These were: print(f"DEBUG _jsx_copy_all() | Paths tab has {len(paths_text)} chars")
        #             print(f"DEBUG _jsx_copy_all() | JSON tab has {len(json_text)} chars")
        
        if not paths_text and not json_text:
            self.show_warning(
                tr("advanced_extractor.error", "Error"),
                "No content to copy. Please run extraction first."
            )
            return
        
        # Combine both outputs: Paths, blank line, then JSON
        combined_parts = []
        
        # Add Paths content (filtered)
        if paths_text:
            paths_lines = paths_text.splitlines()
            paths_filtered = [ln for ln in paths_lines if not self._jsx_should_filter_line(ln)]
            
            # Compact consecutive blank lines
            paths_compact = []
            prev_blank = False
            for ln in paths_filtered:
                blank = (ln.strip() == "")
                if blank and prev_blank:
                    continue
                paths_compact.append(ln)
                prev_blank = blank
            
            combined_parts.append("\n".join(paths_compact))
        
        # Add JSON content (filtered)
        if json_text:
            json_lines = json_text.splitlines()
            json_filtered = [ln for ln in json_lines if not self._jsx_should_filter_line(ln)]
            
            # Compact consecutive blank lines
            json_compact = []
            prev_blank = False
            for ln in json_filtered:
                blank = (ln.strip() == "")
                if blank and prev_blank:
                    continue
                json_compact.append(ln)
                prev_blank = blank
            
            combined_parts.append("\n".join(json_compact))
        
        # Join with blank line separator (two newlines = blank line between)
        result = "\n\n".join(combined_parts)
        
        QApplication.clipboard().setText(result)
        
        # Debug logging removed - was using print() which violates SIMPLICITY_PROTOCOL_3
        # Was: print(f"DEBUG _jsx_copy_all() | Combined {len(result)} characters (Paths + JSON)")
        
        self.show_info(
            tr("advanced_extractor.copied", "Copied"),
            tr("advanced_extractor.copied_message", f"Copied both Paths and JSON output to clipboard ({len(result)} chars).")
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
    
    def _jsx_open_search_dialog(self):
        """Open modal search dialog for JSX text input (Ctrl+F)."""
        dialog = JSXTextSearchDialog(self, self.jsx_text_input)
        dialog.exec()
    
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
    
    def _jsx_open_in_editor_and_switch(self):
        """Open current tab content in editor and switch to the file."""
        # Detect which tab is currently active
        current_index = self.jsx_output_tabs.currentIndex()
        
        # Get content based on active tab (0 = Paths, 1 = JSON)
        if current_index == 0:
            # Paths tab is active
            content = self.jsx_paths_output.toPlainText().strip()
            tab_name = "Paths"
        else:
            # JSON tab is active
            content = self.jsx_json_output.toPlainText().strip()
            tab_name = "JSON"
        
        if not content:
            self.show_warning(
                tr("text_to_json.no_output", "No Output"),
                tr("text_to_json.no_output_message", f"No {tab_name} output to open. Run extraction first.")
            )
            return
        
        # Emit signal to open in editor AND switch to file
        self.open_in_editor_and_switch_requested.emit(content, True)
        self._jsx_update_status(f"✓ Opened {tab_name} in editor and switched")
    
    
    def _jsx_show_history(self):
        """Show extraction history with detailed settings and changes."""
        if not self.extraction_history:
            self.show_info(
                tr("text_to_json.info_history_empty_title", "History Empty"),
                tr("text_to_json.info_history_empty_msg", "No extraction history yet. Run an extraction first.")
            )
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("text_to_json.history_dialog_title", "Extraction History"))
        dialog.resize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        list_widget = QListWidget()
        
        for i, entry in enumerate(reversed(self.extraction_history)):
            settings = entry.get('settings', {})
            mode_str = settings.get('mode', 'unknown')
            param_str = settings.get('param', 'N/A')
            input_type = settings.get('input_type', 'Unknown')
            path_preview = entry['path'].split('/')[-1] if '/' in entry['path'] else entry['path']
            
            # Brief display
            item_text = f"{i+1}. [{mode_str}] {path_preview} (param: {param_str})"
            
            # Build detailed tooltip with all settings
            tooltip_lines = [
                f"=== Entry #{i+1} ===",
                f"Path: {entry['path']}",
                f"Input Type: {input_type}",
                f"",
                "Settings:",
                f"  Mode: {mode_str}",
                f"  Parameter: {param_str}",
                f"  Attribute Mode: {'Yes' if settings.get('is_attribute_mode') else 'No'}",
                f"  Match All: {'Yes' if settings.get('match_all') else 'No'}",
                f"  Case Style: {settings.get('case_style', 'N/A')}",
                f"  Uppercase: {'Yes' if settings.get('to_upper') else 'No'}",
                f"  Limit: {settings.get('limit', 'all')}",
                f"  Avoid Cut: {'Yes' if settings.get('avoid_cut') else 'No'}",
                f"  Avoid Cut Direction: {settings.get('avoid_cut_direction', 'N/A')}",
                f"  Indent: {settings.get('indent', 2)}",
                f"  Include Key: {'Yes' if settings.get('include_key') else 'No'}",
                f"  Include Value: {'Yes' if settings.get('include_value') else 'No'}",
                f"  Drop Standard Tags: {'Yes' if settings.get('no_standard') else 'No'}",
                f"  Only Strings: {'Yes' if settings.get('only_strings') else 'No'}",
                f"  With Quotes: {'Yes' if settings.get('with_quotation_marks') else 'No'}",
                f"  TypeScript Export: {'Yes' if settings.get('typescript_export') else 'No'}",
                f"  Exclude Numeric: {'Yes' if settings.get('exclude_numeric') else 'No'}",
                f"  Skip Empty: {'Yes' if settings.get('skip_empty') else 'No'}",
                f"  Use Class Names: {'Yes' if settings.get('use_class_names') else 'No'}",
                f"  Avoid Keys: {settings.get('avoid_keys', 'None')}",
                f"  File Extensions: {', '.join(settings.get('file_extensions', [])) or 'All'}"
            ]
            
            # Show what changed from previous entry
            if i < len(self.extraction_history) - 1:
                prev_entry = self.extraction_history[len(self.extraction_history) - 1 - (i + 1)]
                prev_settings = prev_entry.get('settings', {})
                changes = []
                
                # Compare all settings
                for key in settings:
                    if key not in ['start_regex', 'end_regex']:  # Skip regex for brevity
                        curr_val = settings.get(key)
                        prev_val = prev_settings.get(key)
                        if curr_val != prev_val:
                            changes.append(f"    {key}: {prev_val} → {curr_val}")
                
                if changes:
                    tooltip_lines.append("")
                    tooltip_lines.append(f"Changes from previous entry:")
                    tooltip_lines.extend(changes)
                else:
                    tooltip_lines.append("")
                    tooltip_lines.append("(No settings changed from previous)")
            
            item = QListWidgetItem(item_text)
            item.setToolTip("\n".join(tooltip_lines))
            list_widget.addItem(item)
        
        list_widget.itemDoubleClicked.connect(lambda item: self._jsx_load_history_item(item, dialog))
        
        layout.addWidget(QLabel(tr("text_to_json.history_lbl_double_click", "Double-click to load extraction. Hover for full details.")))
        layout.addWidget(list_widget)
        
        close_btn = QPushButton(tr("text_to_json.btn_close", "Close"))
        close_btn.clicked.connect(dialog.reject)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _jsx_load_history_item(self, item: QListWidgetItem, dialog: QDialog) -> None:
        """Load history item into JSX extraction fields with all settings."""
        index = len(self.extraction_history) - 1 - item.listWidget().row(item)
        if 0 <= index < len(self.extraction_history):
            entry = self.extraction_history[index]
            settings = entry.get('settings', {})
            
            # Restore path/input
            self.jsx_path_edit.setText(entry['path'])
            
            # Restore output
            self.jsx_json_output.setPlainText(entry['output'])
            
            # Restore all settings that affect output
            self.jsx_param_edit.setText(settings.get('param', ''))
            
            # Mode
            mode_str = settings.get('mode', 'JSX')
            mode_index = self.jsx_mode_combo.findText(mode_str)
            if mode_index >= 0:
                self.jsx_mode_combo.setCurrentIndex(mode_index)
            
            # Case settings
            case_style = settings.get('case_style', 'snake')
            case_index = self.jsx_case_combo.findText(case_style)
            if case_index >= 0:
                self.jsx_case_combo.setCurrentIndex(case_index)
            
            self.jsx_uppercase_checkbox.setChecked(settings.get('to_upper', False))
            self.jsx_limit_edit.setText(str(settings.get('limit', 'all')))
            self.jsx_avoid_cut_checkbox.setChecked(settings.get('avoid_cut', False))
            
            direction = settings.get('avoid_cut_direction', 'before')
            direction_index = 0 if direction == 'before' else 1
            self.jsx_avoid_cut_direction_combo.setCurrentIndex(direction_index)
            
            self.jsx_indent_spin.setValue(settings.get('indent', 2))
            
            # Checkboxes
            self.jsx_include_key_checkbox.setChecked(settings.get('include_key', True))
            self.jsx_include_value_checkbox.setChecked(settings.get('include_value', True))
            self.jsx_no_standard_checkbox.setChecked(settings.get('no_standard', False))
            self.jsx_only_strings_checkbox.setChecked(settings.get('only_strings', False))
            self.jsx_quotation_marks_checkbox.setChecked(settings.get('with_quotation_marks', True))
            self.jsx_match_all_checkbox.setChecked(settings.get('match_all', False))
            self.jsx_typescript_export_checkbox.setChecked(settings.get('typescript_export', False))
            self.jsx_exclude_numeric_checkbox.setChecked(settings.get('exclude_numeric', False))
            self.jsx_skip_empty_checkbox.setChecked(settings.get('skip_empty', False))
            self.jsx_use_class_names_checkbox.setChecked(settings.get('use_class_names', False))
            self.jsx_is_attribute_checkbox.setChecked(settings.get('is_attribute_mode', False))
            
            # Avoid keys
            self.jsx_avoid_keys_edit.setText(settings.get('avoid_keys', ''))
            avoid_keys_param = settings.get('avoid_keys_param', 'contains')
            if avoid_keys_param == 'equals':
                self.jsx_avoid_equals_radio.setChecked(True)
            else:
                self.jsx_avoid_contains_radio.setChecked(True)
            
            # File extensions
            file_exts = settings.get('file_extensions', [])
            self.jsx_extensions_edit.setText(' '.join(file_exts))
            
            dialog.accept()
    
    def _jsx_add_to_history(self, path: str, output_json: str, settings: dict) -> None:
        """Add extraction to history with full settings metadata."""
        entry = {
            'path': path,
            'output': output_json,
            'settings': settings
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
    
    # ========================================================================
    # TEXT SEARCH FEATURE (CTRL+F)
    # ========================================================================
    
    def _on_search_shortcut(self):
        """Handle CTRL+F / Cmd+F shortcut."""
        # Only open search if Text mode is active
        selected_type = self.jsx_input_type_combo.currentData()
        if selected_type == "text":
            self._open_text_search()
    
    def _open_text_search(self):
        """Open search dialog for text mode."""
        if not hasattr(self, '_text_search_dialog') or self._text_search_dialog is None:
            self._text_search_dialog = TextSearchDialog(self, self.jsx_text_input)
        
        self._text_search_dialog.show()
        self._text_search_dialog.raise_()
        self._text_search_dialog.activateWindow()
