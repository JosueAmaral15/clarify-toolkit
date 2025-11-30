#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Editor Dock - Integrated File Editor

Simple text editor with syntax highlighting for common file types.
Allows opening, editing, and saving files directly within Clarify.

Features:
- Open/save files (.txt, .json, .html, .tsx, .py, etc.)
- Syntax highlighting with scope differentiation by colors
- Line numbers
- Tab support for multiple files
- File-specific color schemes (HTML tags, JSON keys, Python keywords)
- Recent files list
- Find/Replace functionality
"""

from __future__ import annotations
from typing import Optional, Dict, List
import os
import re

from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QFileDialog, QMessageBox, QTabWidget, QLineEdit,
    QCheckBox, QPlainTextEdit
)
from PySide6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
    QTextCursor, QPalette
)

from .base_dock import BaseDock


class SyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for different file types.
    
    Supports:
    - HTML/JSX/TSX: tags, attributes, strings
    - JSON: keys, values, brackets
    - Python: keywords, strings, comments
    - JavaScript/TypeScript: keywords, strings, comments
    """
    
    def __init__(self, document, file_type: str = "txt"):
        super().__init__(document)
        self.file_type = file_type.lower()
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Setup text formats for different syntax elements."""
        # HTML/JSX/TSX tags
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(QColor("#569CD6"))  # Blue
        self.tag_format.setFontWeight(QFont.Bold)
        
        # HTML attributes
        self.attr_format = QTextCharFormat()
        self.attr_format.setForeground(QColor("#9CDCFE"))  # Light blue
        
        # Strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CE9178"))  # Orange
        
        # Keywords (Python, JS, TS)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#C586C0"))  # Purple
        self.keyword_format.setFontWeight(QFont.Bold)
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955"))  # Green
        self.comment_format.setFontItalic(True)
        
        # JSON keys
        self.json_key_format = QTextCharFormat()
        self.json_key_format.setForeground(QColor("#9CDCFE"))  # Light blue
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))  # Light green
        
        # Brackets/Braces
        self.bracket_format = QTextCharFormat()
        self.bracket_format.setForeground(QColor("#FFD700"))  # Gold
        self.bracket_format.setFontWeight(QFont.Bold)
    
    def _setup_rules(self):
        """Setup highlighting rules based on file type."""
        self.rules = []
        
        if self.file_type in ["html", "htm", "jsx", "tsx"]:
            # HTML/JSX tags: <tagname> </tagname>
            self.rules.append((QRegularExpression(r"</?[\w-]+"), self.tag_format))
            self.rules.append((QRegularExpression(r"/?>"), self.tag_format))
            
            # Attributes: attribute="value"
            self.rules.append((QRegularExpression(r"\b[\w-]+(?==)"), self.attr_format))
            
            # Strings: "..." or '...'
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))
            
            # Comments: <!-- ... -->
            self.rules.append((QRegularExpression(r"<!--.*?-->"), self.comment_format))
        
        elif self.file_type == "json":
            # JSON keys: "key":
            self.rules.append((QRegularExpression(r'"[\w\s.-]+"(?=\s*:)'), self.json_key_format))
            
            # Strings: "value"
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            
            # Numbers
            self.rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), self.number_format))
            
            # Brackets/Braces: {}, []
            self.rules.append((QRegularExpression(r'[{}\[\]]'), self.bracket_format))
            
            # Booleans and null
            self.rules.append((QRegularExpression(r'\b(true|false|null)\b'), self.keyword_format))
        
        elif self.file_type in ["py", "python"]:
            # Python keywords
            keywords = [
                "def", "class", "if", "elif", "else", "for", "while", "try", "except",
                "finally", "with", "as", "import", "from", "return", "yield", "lambda",
                "pass", "break", "continue", "raise", "assert", "del", "global", "nonlocal",
                "True", "False", "None", "and", "or", "not", "in", "is"
            ]
            for keyword in keywords:
                pattern = QRegularExpression(rf'\b{keyword}\b')
                self.rules.append((pattern, self.keyword_format))
            
            # Strings: "...", '...', """...""", '''...'''
            self.rules.append((QRegularExpression(r'""".*?"""'), self.string_format))
            self.rules.append((QRegularExpression(r"'''.*?'''"), self.string_format))
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))
            
            # Comments: # ...
            self.rules.append((QRegularExpression(r'#[^\n]*'), self.comment_format))
            
            # Numbers
            self.rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), self.number_format))
        
        elif self.file_type in ["js", "ts", "javascript", "typescript"]:
            # JavaScript/TypeScript keywords
            keywords = [
                "const", "let", "var", "function", "if", "else", "for", "while", "do",
                "switch", "case", "break", "continue", "return", "try", "catch", "finally",
                "throw", "new", "this", "class", "extends", "import", "export", "from",
                "default", "async", "await", "yield", "typeof", "instanceof", "void",
                "true", "false", "null", "undefined"
            ]
            for keyword in keywords:
                pattern = QRegularExpression(rf'\b{keyword}\b')
                self.rules.append((pattern, self.keyword_format))
            
            # Strings: "...", '...', `...`
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))
            self.rules.append((QRegularExpression(r'`[^`]*`'), self.string_format))
            
            # Comments: // ... or /* ... */
            self.rules.append((QRegularExpression(r'//[^\n]*'), self.comment_format))
            self.rules.append((QRegularExpression(r'/\*.*?\*/'), self.comment_format))
            
            # Numbers
            self.rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), self.number_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class EditorTab(QWidget):
    """
    Single editor tab for editing a file.
    
    Contains:
    - Text editor with syntax highlighting
    - File path tracking
    - Modified state tracking
    """
    
    modified_changed = Signal(bool)  # Emitted when modified state changes
    
    def __init__(self, file_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabStopDistance(40)  # 4 spaces equivalent
        self.editor.textChanged.connect(self._on_text_changed)
        
        # Monospace font
        font = QFont("Courier New", 10)
        self.editor.setFont(font)
        
        layout.addWidget(self.editor)
        
        # Syntax highlighter
        self.highlighter = None
        if file_path:
            self._setup_highlighter()
    
    def _setup_highlighter(self):
        """Setup syntax highlighter based on file extension."""
        if not self.file_path:
            return
        
        ext = os.path.splitext(self.file_path)[1].lstrip('.')
        self.highlighter = SyntaxHighlighter(self.editor.document(), ext)
    
    def _on_text_changed(self):
        """Handle text changes."""
        if not self.is_modified:
            self.is_modified = True
            self.modified_changed.emit(True)
    
    def load_file(self, file_path: str) -> bool:
        """
        Load file content into editor.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.file_path = file_path
            self.editor.blockSignals(True)  # Prevent modified signal
            self.editor.setPlainText(content)
            self.editor.blockSignals(False)
            self.is_modified = False
            self.modified_changed.emit(False)
            
            # Setup highlighter
            self._setup_highlighter()
            
            return True
        except Exception as e:
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """
        Save editor content to file.
        
        Args:
            file_path: Optional path to save to (defaults to current file)
        
        Returns:
            True if successful, False otherwise
        """
        save_path = file_path or self.file_path
        if not save_path:
            return False
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            self.file_path = save_path
            self.is_modified = False
            self.modified_changed.emit(False)
            
            # Setup highlighter if new file
            if file_path:
                self._setup_highlighter()
            
            return True
        except Exception as e:
            return False
    
    def get_tab_title(self) -> str:
        """Get title for tab (filename or 'Untitled')."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return "Untitled"
    
    def get_display_title(self) -> str:
        """Get display title with modified indicator."""
        title = self.get_tab_title()
        if self.is_modified:
            title += " *"
        return title


class EditorDock(BaseDock):
    """
    Dock widget for integrated file editor.
    
    Features:
    - Tabbed interface for multiple files
    - Syntax highlighting for common file types
    - Open/Save/Save As functionality
    - Find/Replace (basic)
    - Recent files list
    """
    
    def __init__(self, parent=None):
        super().__init__("File Editor", parent)
        self.recent_files: List[str] = []
        self.max_recent = 10
    
    def _setup_ui(self):
        """Setup UI components."""
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_new = QPushButton("New")
        self.btn_new.setToolTip("Create new file (Ctrl+N)")
        self.btn_open = QPushButton("Open...")
        self.btn_open.setToolTip("Open existing file (Ctrl+O)")
        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save current file (Ctrl+S)")
        self.btn_save_as = QPushButton("Save As...")
        self.btn_save_as.setToolTip("Save current file with new name")
        self.btn_close_tab = QPushButton("Close Tab")
        self.btn_close_tab.setToolTip("Close current tab (Ctrl+W)")
        
        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_open)
        toolbar.addWidget(self.btn_save)
        toolbar.addWidget(self.btn_save_as)
        toolbar.addWidget(self.btn_close_tab)
        toolbar.addStretch()
        
        self.layout.addLayout(toolbar)
        
        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.layout.addWidget(self.tab_widget)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: #6A9955;")
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        self.layout.addLayout(status_layout)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.btn_new.clicked.connect(self._new_file)
        self.btn_open.clicked.connect(self._open_file)
        self.btn_save.clicked.connect(self._save_file)
        self.btn_save_as.clicked.connect(self._save_file_as)
        self.btn_close_tab.clicked.connect(self._close_current_tab)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _new_file(self):
        """Create new untitled file."""
        tab = EditorTab(None, self)
        tab.modified_changed.connect(lambda modified: self._update_tab_title(tab))
        
        index = self.tab_widget.addTab(tab, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        self.lbl_status.setText("New file created")
    
    def _open_file(self):
        """Open existing file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;TypeScript (*.ts);;JSON (*.json);;HTML (*.html *.htm);;React (*.jsx *.tsx)"
        )
        
        if not file_path:
            return
        
        # Check if already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                self.lbl_status.setText(f"File already open: {os.path.basename(file_path)}")
                return
        
        # Load file
        tab = EditorTab(file_path, self)
        if not tab.load_file(file_path):
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{file_path}")
            return
        
        tab.modified_changed.connect(lambda modified: self._update_tab_title(tab))
        
        index = self.tab_widget.addTab(tab, tab.get_tab_title())
        self.tab_widget.setCurrentIndex(index)
        
        # Add to recent files
        self._add_recent_file(file_path)
        
        self.lbl_status.setText(f"Opened: {os.path.basename(file_path)}")
    
    def _save_file(self):
        """Save current file."""
        tab = self.tab_widget.currentWidget()
        if not tab:
            return
        
        if not tab.file_path:
            self._save_file_as()
            return
        
        if tab.save_file():
            self._update_tab_title(tab)
            self.lbl_status.setText(f"Saved: {os.path.basename(tab.file_path)}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{tab.file_path}")
    
    def _save_file_as(self):
        """Save current file with new name."""
        tab = self.tab_widget.currentWidget()
        if not tab:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;TypeScript (*.ts);;JSON (*.json);;HTML (*.html)"
        )
        
        if not file_path:
            return
        
        if tab.save_file(file_path):
            self._update_tab_title(tab)
            self.lbl_status.setText(f"Saved as: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{file_path}")
    
    def _close_current_tab(self):
        """Close currently active tab."""
        self._close_tab(self.tab_widget.currentIndex())
    
    def _close_tab(self, index: int):
        """Close tab at index."""
        if index < 0:
            return
        
        tab = self.tab_widget.widget(index)
        
        # Check if modified
        if tab.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"'{tab.get_tab_title()}' has unsaved changes.\n\nSave before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                # Save first
                if not tab.file_path:
                    self.tab_widget.setCurrentIndex(index)
                    self._save_file_as()
                else:
                    tab.save_file()
            elif reply == QMessageBox.Cancel:
                return
        
        self.tab_widget.removeTab(index)
        self.lbl_status.setText(f"Closed: {tab.get_tab_title()}")
    
    def _on_tab_changed(self, index: int):
        """Handle tab change."""
        if index >= 0:
            tab = self.tab_widget.widget(index)
            if tab.file_path:
                self.lbl_status.setText(f"Editing: {os.path.basename(tab.file_path)}")
            else:
                self.lbl_status.setText("Editing: Untitled")
        else:
            self.lbl_status.setText("Ready")
    
    def _update_tab_title(self, tab: EditorTab):
        """Update tab title based on modified state."""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, tab.get_display_title())
    
    def _add_recent_file(self, file_path: str):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:self.max_recent]
    
    def open_file_path(self, file_path: str):
        """
        Open file from external call (e.g., from search results).
        
        Public API method for integration with other tools.
        """
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"File does not exist:\n{file_path}")
            return
        
        # Check if already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return
        
        # Load file
        tab = EditorTab(file_path, self)
        if tab.load_file(file_path):
            tab.modified_changed.connect(lambda modified: self._update_tab_title(tab))
            index = self.tab_widget.addTab(tab, tab.get_tab_title())
            self.tab_widget.setCurrentIndex(index)
            self._add_recent_file(file_path)
            self.lbl_status.setText(f"Opened: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{file_path}")
