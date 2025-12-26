"""
Reusable search/replace widgets for File Explorer integration.

Extracted from search_replace_panel.py to enable component reuse.
Part of v2.9.116 integration: Search/Replace → File Explorer.

Author: Josué Amaral
Date: 2025/12/25
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QCheckBox, QPushButton, QLabel, QGroupBox, QComboBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont


class FileNameQueryPanel(QWidget):
    """
    Widget for file name pattern input with regex support.
    
    Signals:
        pattern_changed: Emitted when pattern text changes
        clear_requested: Emitted when clear button is clicked
    """
    
    pattern_changed = Signal(str)
    clear_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("File Name:")
        label.setToolTip("Filename pattern (supports wildcards: *.py, test_*.json)")
        layout.addWidget(label)
        
        # Pattern input
        self.ed_pattern = QLineEdit()
        self.ed_pattern.setPlaceholderText("*.py, test_*.json, **/*.txt")
        self.ed_pattern.textChanged.connect(self.pattern_changed.emit)
        layout.addWidget(self.ed_pattern, stretch=1)
        
        # Clear button
        btn_clear = QPushButton("Clear")
        btn_clear.setToolTip("Clear filename pattern")
        btn_clear.clicked.connect(self._on_clear)
        layout.addWidget(btn_clear)
    
    def _on_clear(self):
        self.ed_pattern.clear()
        self.clear_requested.emit()
    
    def get_pattern(self) -> str:
        """Get current filename pattern."""
        return self.ed_pattern.text().strip()
    
    def set_pattern(self, pattern: str):
        """Set filename pattern."""
        self.ed_pattern.setText(pattern)
    
    def clear(self):
        """Clear filename pattern (v2.9.117)."""
        self.ed_pattern.clear()


class ContentQueryPanel(QWidget):
    """
    Multi-line text editor for content search queries.
    
    Signals:
        query_changed: Emitted when query text changes
    """
    
    query_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("Content Search:")
        label.setToolTip("Search for text within file contents (multi-line supported)")
        layout.addWidget(label)
        
        # Text editor
        self.ed_query = QTextEdit()
        self.ed_query.setPlaceholderText("Search text...\nMulti-line supported")
        self.ed_query.setMaximumHeight(80)
        self.ed_query.textChanged.connect(lambda: self.query_changed.emit(self.get_query()))
        layout.addWidget(self.ed_query)
    
    def get_query(self) -> str:
        """Get current search query."""
        return self.ed_query.toPlainText()
    
    def set_query(self, query: str):
        """Set search query."""
        self.ed_query.setPlainText(query)
    
    def set_font(self, font: QFont):
        """Set monospaced font for editor."""
        self.ed_query.setFont(font)
    
    def clear(self):
        """Clear search query (v2.9.117)."""
        self.ed_query.clear()


class SearchOptionsPanel(QWidget):
    """
    Checkboxes for search options (case-sensitive, whole-word, regex).
    
    Signals:
        options_changed: Emitted when any option changes
    """
    
    options_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Options:")
        layout.addWidget(label)
        
        # Case-sensitive
        self.chk_case = QCheckBox("Case Sensitive")
        self.chk_case.setToolTip("Match case exactly")
        self.chk_case.toggled.connect(self._emit_options)
        layout.addWidget(self.chk_case)
        
        # Whole word
        self.chk_word = QCheckBox("Whole Word")
        self.chk_word.setToolTip("Match whole words only")
        self.chk_word.toggled.connect(self._emit_options)
        layout.addWidget(self.chk_word)
        
        # Regex
        self.chk_regex = QCheckBox("Regex")
        self.chk_regex.setToolTip("Use regular expressions")
        self.chk_regex.toggled.connect(self._emit_options)
        layout.addWidget(self.chk_regex)
        
        layout.addStretch()
    
    def _emit_options(self):
        self.options_changed.emit(self.get_options())
    
    def get_options(self) -> dict:
        """Get current search options."""
        return {
            'case_sensitive': self.chk_case.isChecked(),
            'whole_word': self.chk_word.isChecked(),
            'regex': self.chk_regex.isChecked()
        }
    
    def set_options(self, options: dict):
        """Set search options."""
        self.chk_case.setChecked(options.get('case_sensitive', False))
        self.chk_word.setChecked(options.get('whole_word', False))
        self.chk_regex.setChecked(options.get('regex', False))


class ReplacePanel(QWidget):
    """
    Panel with replace text editor and action buttons.
    
    Signals:
        replace_first_requested: Emitted when "Replace First" is clicked
        replace_all_requested: Emitted when "Replace All" is clicked
    """
    
    replace_first_requested = Signal()
    replace_all_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("Replace With:")
        label.setToolTip("Replacement text (multi-line supported)")
        layout.addWidget(label)
        
        # Text editor
        self.ed_replace = QTextEdit()
        self.ed_replace.setPlaceholderText("Replacement text...\nMulti-line supported")
        self.ed_replace.setMaximumHeight(80)
        layout.addWidget(self.ed_replace)
        
        # Options row
        options_layout = QHBoxLayout()
        
        self.chk_preserve_case = QCheckBox("Preserve Case")
        self.chk_preserve_case.setToolTip("Maintain original case pattern in replacements")
        options_layout.addWidget(self.chk_preserve_case)
        
        options_layout.addStretch()
        
        # Action buttons
        self.btn_replace_first = QPushButton("Replace First")
        self.btn_replace_first.setToolTip("Replace first occurrence only")
        self.btn_replace_first.clicked.connect(self.replace_first_requested.emit)
        options_layout.addWidget(self.btn_replace_first)
        
        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.setToolTip("Replace all occurrences")
        self.btn_replace_all.clicked.connect(self.replace_all_requested.emit)
        options_layout.addWidget(self.btn_replace_all)
        
        layout.addLayout(options_layout)
    
    def get_replacement(self) -> str:
        """Get replacement text."""
        return self.ed_replace.toPlainText()
    
    def set_replacement(self, text: str):
        """Set replacement text."""
        self.ed_replace.setPlainText(text)
    
    def get_preserve_case(self) -> bool:
        """Check if preserve case is enabled."""
        return self.chk_preserve_case.isChecked()
    
    def set_preserve_case(self, enabled: bool):
        """Set preserve case option."""
        self.chk_preserve_case.setChecked(enabled)
    
    def set_font(self, font: QFont):
        """Set monospaced font for editor."""
        self.ed_replace.setFont(font)
    
    def set_buttons_enabled(self, enabled: bool):
        """Enable/disable action buttons."""
        self.btn_replace_first.setEnabled(enabled)
        self.btn_replace_all.setEnabled(enabled)


class ConditionsGrid(QWidget):
    """
    Dynamic grid for advanced search conditions with AND/OR logic.
    
    Signals:
        conditions_changed: Emitted when conditions are modified
    """
    
    conditions_changed = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.condition_rows = []
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header row
        header_layout = QHBoxLayout()
        
        # Logic operator
        label_logic = QLabel("Logic:")
        header_layout.addWidget(label_logic)
        
        self.combo_logic = QComboBox()
        self.combo_logic.addItems(["AND", "OR"])
        self.combo_logic.setToolTip("Logical operator between conditions")
        self.combo_logic.currentTextChanged.connect(self._emit_conditions)
        header_layout.addWidget(self.combo_logic)
        
        header_layout.addStretch()
        
        # Buttons
        btn_add = QPushButton("+ Add Condition")
        btn_add.setToolTip("Add new condition row")
        btn_add.clicked.connect(self.add_condition_row)
        header_layout.addWidget(btn_add)
        
        btn_clear = QPushButton("Clear All")
        btn_clear.setToolTip("Remove all conditions")
        btn_clear.clicked.connect(self.clear_conditions)
        header_layout.addWidget(btn_clear)
        
        layout.addLayout(header_layout)
        
        # Conditions container (for dynamic rows)
        self.conditions_container = QWidget()
        self.conditions_layout = QVBoxLayout(self.conditions_container)
        self.conditions_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.conditions_container)
        
        # Add initial row
        self.add_condition_row()
    
    def add_condition_row(self):
        """Add a new condition row."""
        # TODO: Implement condition row widget with fields:
        # - Field (filename, path, ext, size, mtime, content)
        # - Operator (=, !=, contains, >, <, etc)
        # - Value (text input)
        # - Scope (all/any for content search)
        # - Options (case, word, regex checkboxes)
        # - Delete button
        pass
    
    def clear_conditions(self):
        """Remove all condition rows."""
        for row in self.condition_rows:
            row.deleteLater()
        self.condition_rows.clear()
        self._emit_conditions()
    
    def _emit_conditions(self):
        conditions = self.get_conditions()
        self.conditions_changed.emit(conditions)
    
    def get_conditions(self) -> list:
        """Get all conditions as list of dicts."""
        # TODO: Collect data from all condition rows
        return []
    
    def get_logic_operator(self) -> str:
        """Get selected logic operator (AND/OR)."""
        return self.combo_logic.currentText()
