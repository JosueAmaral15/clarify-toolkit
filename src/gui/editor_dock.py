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

from PySide6.QtCore import Qt, Signal, QRegularExpression, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QFileDialog, QMessageBox, QTabWidget, QLineEdit,
    QCheckBox, QPlainTextEdit, QMenu, QToolBar, QApplication
)
from PySide6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
    QTextCursor, QPalette, QAction, QKeySequence
)

from .base_dock import BaseDock
from .json_editor_tab import JsonEditorTab
from src.i18n.translator import tooltip_tr


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
    - Edit-only mode (sandbox editing without file backing)
    
    Pattern: State (GoF) - edit_only_mode changes save behavior
    """
    
    modified_changed = Signal(bool)  # Emitted when modified state changes
    edit_only_changed = Signal(bool)  # Emitted when edit-only mode changes
    auto_saved = Signal()  # Emitted when file is auto-saved
    
    def __init__(self, file_path: Optional[str] = None, parent=None, edit_only_mode: bool = False):
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        self.edit_only_mode = edit_only_mode  # State pattern: changes behavior
        self.auto_save_enabled = False  # Auto-save feature flag
        
        # Auto-save timer (3 seconds after last modification)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.setInterval(3000)  # 3 seconds
        self.auto_save_timer.timeout.connect(self._auto_save)
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar for edit-only features
        self._setup_toolbar()
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabStopDistance(40)  # 4 spaces equivalent
        self.editor.textChanged.connect(self._on_text_changed)
        
        # Monospace font
        font = QFont("Courier New", 10)
        self.editor.setFont(font)
        
        layout.addWidget(self.editor)
        
        # Apply visual indicators if edit-only
        self._update_visual_indicators()
        
        # Syntax highlighter
        self.highlighter = None
        if file_path:
            self._setup_highlighter()
        
        # Apply tooltips
        self._apply_tab_tooltips()
    
    def _apply_tab_tooltips(self):
        """Apply internationalized tooltips to EditorTab widgets."""
        # Text Editor
        self.editor.setToolTip(tooltip_tr("editor.editor"))
        
        # Toolbar Buttons
        self.btn_copy.setToolTip(tooltip_tr("editor.btn_copy"))
        self.btn_export.setToolTip(tooltip_tr("editor.btn_export"))
        self.btn_enable_saving.setToolTip(tooltip_tr("editor.btn_enable_saving"))
    
    def _setup_toolbar(self):
        """Setup toolbar with edit-only mode buttons."""
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { border: none; padding: 2px; }")
        
        # Copy to Clipboard button
        self.btn_copy = QPushButton("📋 Copy")
        self.btn_copy.clicked.connect(self._copy_to_clipboard)
        toolbar.addWidget(self.btn_copy)
        
        # Export to File button
        self.btn_export = QPushButton("💾 Export")
        self.btn_export.clicked.connect(self._export_to_file)
        toolbar.addWidget(self.btn_export)
        
        # Enable File Saving button (only visible in edit-only mode)
        self.btn_enable_saving = QPushButton("🔓 Enable Saving")
        self.btn_enable_saving.clicked.connect(self._enable_file_saving)
        toolbar.addWidget(self.btn_enable_saving)
        
        self.layout().addWidget(toolbar)
        self.toolbar = toolbar
        
        # Update button visibility
        self._update_toolbar_visibility()
    
    def _update_toolbar_visibility(self):
        """Update toolbar button visibility based on mode."""
        # Enable Saving button only visible in edit-only mode
        self.btn_enable_saving.setVisible(self.edit_only_mode)
        
        # Copy/Export always visible but more prominent in edit-only
        if self.edit_only_mode:
            self.btn_copy.setStyleSheet("font-weight: bold;")
            self.btn_export.setStyleSheet("font-weight: bold;")
        else:
            self.btn_copy.setStyleSheet("")
            self.btn_export.setStyleSheet("")
    
    def _copy_to_clipboard(self):
        """Copy editor content to clipboard (Command pattern)."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.editor.toPlainText())
        # Visual feedback
        self.btn_copy.setText("✓ Copied!")
        QTimer.singleShot(1500, lambda: self.btn_copy.setText("📋 Copy"))
    
    def _export_to_file(self):
        """Export content to file (Command pattern)."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export File",
            "",
            "All Files (*);;JSON Files (*.json);;Text Files (*.txt);;Python (*.py)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            # Visual feedback
            self.btn_export.setText("✓ Exported!")
            QTimer.singleShot(1500, lambda: self.btn_export.setText("💾 Export"))
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export file:\n{e}")
    
    def _enable_file_saving(self):
        """Convert edit-only tab to normal file-backed editor."""
        reply = QMessageBox.question(
            self,
            "Enable File Saving",
            "This will convert the editor to file-backed mode.\n\nYou'll need to choose a file location to save to.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Trigger Save As to get file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save File As",
                "",
                "All Files (*);;JSON Files (*.json);;Text Files (*.txt);;Python (*.py)"
            )
            
            if file_path:
                # Save content
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.editor.toPlainText())
                    
                    # Update state
                    self.edit_only_mode = False
                    self.file_path = file_path
                    self.is_modified = False
                    self._setup_highlighter()
                    self._update_visual_indicators()
                    self._update_toolbar_visibility()
                    self.edit_only_changed.emit(False)
                    self.modified_changed.emit(False)
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{e}")
    
    def _update_visual_indicators(self):
        """Update visual indicators for edit-only mode."""
        if self.edit_only_mode:
            # Golden border (indicator #3)
            self.editor.setStyleSheet("""
                QTextEdit {
                    border: 3px solid #FFD700;
                    background-color: #FFF8DC;
                }
            """)
        else:
            # Normal border
            self.editor.setStyleSheet("")
    
    def toggle_edit_only_mode(self):
        """Toggle edit-only mode on/off (State pattern transition)."""
        if not self.edit_only_mode and self.file_path:
            # Cannot enable edit-only if file is already backed
            reply = QMessageBox.question(
                self,
                "Enable Edit-Only Mode",
                "This will disconnect the editor from the file.\n\nChanges will not be saved automatically.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.edit_only_mode = not self.edit_only_mode
        self._update_visual_indicators()
        self._update_toolbar_visibility()
        self.edit_only_changed.emit(self.edit_only_mode)
    
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
        
        # Reset auto-save timer if enabled
        if self.auto_save_enabled and self.file_path and not self.edit_only_mode:
            self.auto_save_timer.start()  # Restart 3s countdown
    
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
        """Get display title with modified and edit-only indicators."""
        title = self.get_tab_title()
        
        # Edit-only indicator (visual indicator #1)
        if self.edit_only_mode:
            title = "🔒 " + title
        
        # Modified indicator
        if self.is_modified:
            title += " *"
        
        return title
    
    def get_status_text(self) -> str:
        """Get status bar text with mode indicator."""
        status = "Text Editor"
        if self.edit_only_mode:
            status = "Edit-Only Mode"  # Visual indicator #4
        return status
    
    def set_auto_save(self, enabled: bool):
        """Enable or disable auto-save for this tab."""
        self.auto_save_enabled = enabled
        
        # Stop timer if disabling
        if not enabled:
            self.auto_save_timer.stop()
        # Start timer if enabling and file is modified
        elif self.file_path and not self.edit_only_mode and self.is_modified:
            self.auto_save_timer.start()
    
    def _auto_save(self):
        """Auto-save file if conditions are met."""
        # Only auto-save if:
        # 1. Auto-save is enabled
        # 2. File has a path (not untitled)
        # 3. Not in edit-only mode
        # 4. File is modified
        if not self.auto_save_enabled:
            return
        
        if not self.file_path:
            return
        
        if self.edit_only_mode:
            return
        
        if not self.is_modified:
            return
        
        # Perform save
        success = self.save_file()
        
        if success:
            self.auto_saved.emit()  # Signal for status update


class EditorDock(BaseDock):
    """
    Dock widget for integrated file editor.
    
    Features:
    - Tabbed interface for multiple files
    - Syntax highlighting for common file types
    - Open/Save/Save As functionality
    - Edit-only mode for sandbox editing
    - Context menu for mode switching
    - Keyboard shortcuts (Ctrl+Shift+E for edit-only)
    - Find/Replace (basic)
    - Recent files list
    """
    
    def __init__(self, parent=None):
        # Initialize attributes BEFORE super().__init__() which calls _setup_ui()
        self.recent_files: List[str] = []
        self.max_recent = 10
        self.untitled_counter = 0  # Counter for Untitled-N tabs
        
        # Load auto-save preference from QSettings
        from PySide6.QtCore import QSettings
        self.settings = QSettings("Clarify", "EditorDock")
        self.auto_save_enabled = self.settings.value("auto_save_enabled", False, type=bool)
        
        # NOW call super().__init__() which triggers _setup_ui()
        super().__init__("File Editor", parent)
    
    def _setup_ui(self):
        """Setup UI components."""
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_new = QPushButton("New")
        self.btn_open = QPushButton("Open...")
        self.btn_save = QPushButton("Save")
        self.btn_save_as = QPushButton("Save As...")
        self.btn_close_tab = QPushButton("Close Tab")
        
        # Auto-save checkbox
        self.chk_auto_save = QCheckBox("Auto-save")
        self.chk_auto_save.setChecked(self.auto_save_enabled)
        
        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_open)
        toolbar.addWidget(self.btn_save)
        toolbar.addWidget(self.btn_save_as)
        toolbar.addWidget(self.btn_close_tab)
        toolbar.addWidget(QLabel("  "))  # Spacer
        toolbar.addWidget(self.chk_auto_save)
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
        
        # Apply tooltips
        self._apply_tooltips()
    
    def _apply_tooltips(self):
        """Apply internationalized tooltips to all widgets."""
        # Toolbar Buttons
        self.btn_new.setToolTip(tooltip_tr("editor.btn_new"))
        self.btn_open.setToolTip(tooltip_tr("editor.btn_open"))
        self.btn_save.setToolTip(tooltip_tr("editor.btn_save"))
        self.btn_save_as.setToolTip(tooltip_tr("editor.btn_save_as"))
        self.btn_close_tab.setToolTip(tooltip_tr("editor.btn_close_tab"))
        
        # Auto-save Option
        self.chk_auto_save.setToolTip(tooltip_tr("editor.chk_auto_save"))
        
        # Tab Widget
        self.tab_widget.setToolTip(tooltip_tr("editor.tab_widget"))
        
        # Status Label
        self.lbl_status.setToolTip(tooltip_tr("editor.lbl_status"))
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.btn_new.clicked.connect(self._new_file)
        self.btn_open.clicked.connect(self._open_file)
        self.btn_save.clicked.connect(self._save_file)
        self.btn_save_as.clicked.connect(self._save_file_as)
        self.btn_close_tab.clicked.connect(self._close_current_tab)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Auto-save checkbox
        self.chk_auto_save.stateChanged.connect(self._on_auto_save_toggled)
        
        # Context menu on tabs
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self._show_tab_context_menu)
    
    def _show_tab_context_menu(self, pos):
        """Show context menu on tab right-click."""
        # Get tab at position
        tab_bar = self.tab_widget.tabBar()
        index = tab_bar.tabAt(pos)
        
        if index < 0:
            return
        
        tab = self.tab_widget.widget(index)
        if not hasattr(tab, 'edit_only_mode'):
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # Toggle edit-only action
        if tab.edit_only_mode:
            action_text = "Disable Edit-Only Mode"
        else:
            action_text = "Enable Edit-Only Mode"
        
        toggle_action = QAction(action_text, self)
        toggle_action.triggered.connect(lambda: self._toggle_edit_only_for_tab(index))
        menu.addAction(toggle_action)
        
        # Show menu
        menu.exec_(tab_bar.mapToGlobal(pos))
    
    def _new_file(self, edit_only: bool = False):
        """Create new untitled file."""
        # Increment counter for unique names
        self.untitled_counter += 1
        
        # Create text editor tab
        tab = EditorTab(None, self, edit_only_mode=edit_only)
        tab.modified_changed.connect(lambda modified: self._update_tab_title(tab))
        tab.edit_only_changed.connect(lambda: self._update_tab_title(tab))
        
        # Apply auto-save setting to new tab
        tab.set_auto_save(self.auto_save_enabled)
        if self.auto_save_enabled:
            tab.auto_saved.connect(lambda: self._on_auto_saved(tab))
        
        # Set custom title with counter
        if self.untitled_counter > 1:
            custom_title = f"Untitled-{self.untitled_counter}"
        else:
            custom_title = "Untitled"
        
        # Override get_tab_title temporarily
        original_get_tab_title = tab.get_tab_title
        tab.get_tab_title = lambda: custom_title if not tab.file_path else original_get_tab_title()
        
        index = self.tab_widget.addTab(tab, tab.get_display_title())
        self.tab_widget.setCurrentIndex(index)
        
        mode_text = "Edit-Only" if edit_only else "Normal"
        self.lbl_status.setText(f"New {mode_text} file created")
    
    def _toggle_edit_only_for_tab(self, index: int):
        """Toggle edit-only mode for specific tab."""
        tab = self.tab_widget.widget(index)
        if hasattr(tab, 'toggle_edit_only_mode'):
            tab.toggle_edit_only_mode()
            self._update_tab_title(tab)
            self._on_tab_changed(index)
    
    def _open_file(self):
        """Open existing file with optional edit-only mode."""
        # Create custom dialog with edit-only checkbox
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Open File")
        dialog.setNameFilters([
            "All Files (*)",
            "JSON Files (*.json)",
            "Text Files (*.txt)",
            "Python (*.py)",
            "JavaScript (*.js)",
            "TypeScript (*.ts)",
            "HTML (*.html *.htm)",
            "React (*.jsx *.tsx)"
        ])
        dialog.setFileMode(QFileDialog.ExistingFile)
        
        # Add checkbox for edit-only mode
        chk_edit_only = QCheckBox("Open in Edit-Only Mode (no file changes)")
        dialog.layout().addWidget(chk_edit_only)
        
        if not dialog.exec_():
            return
        
        file_paths = dialog.selectedFiles()
        if not file_paths:
            return
        
        file_path = file_paths[0]
        edit_only = chk_edit_only.isChecked()
        
        # Check if already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'file_path') and tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                self.lbl_status.setText(f"File already open: {os.path.basename(file_path)}")
                return
        
        # Create appropriate tab based on file extension
        tab = self._create_tab_for_file(file_path, edit_only)
        
        if not tab.load_file(file_path):
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{file_path}")
            return
        
        # If edit-only, disconnect from file
        if edit_only:
            tab.file_path = None  # Disconnect from file
        
        tab.modified_changed.connect(lambda modified: self._update_tab_title(tab))
        tab.edit_only_changed.connect(lambda: self._update_tab_title(tab))
        
        # Apply auto-save setting to new tab
        tab.set_auto_save(self.auto_save_enabled)
        if self.auto_save_enabled:
            tab.auto_saved.connect(lambda: self._on_auto_saved(tab))
        
        # Use display title (includes JSON icon if JSON file, 🔒 if edit-only)
        index = self.tab_widget.addTab(tab, tab.get_display_title())
        self.tab_widget.setCurrentIndex(index)
        
        # Add to recent files (only if not edit-only)
        if not edit_only:
            self._add_recent_file(file_path)
        
        # Update status with editor type and mode
        editor_type = "JSON Editor" if isinstance(tab, JsonEditorTab) else "Text Editor"
        mode_text = " (Edit-Only)" if edit_only else ""
        self.lbl_status.setText(f"Opened in {editor_type}{mode_text}: {os.path.basename(file_path)}")
    
    def _create_tab_for_file(self, file_path: str, edit_only: bool = False):
        """
        Create appropriate tab type based on file extension.
        
        Pattern: Factory Method (GoF)
        - Creates JsonEditorTab for .json files
        - Creates EditorTab for other files
        - Supports edit_only mode for both
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            # JSON file → use JSON editor with advanced features
            return JsonEditorTab(file_path, self, edit_only_mode=edit_only)
        else:
            # Other files → use simple text editor
            return EditorTab(file_path, self, edit_only_mode=edit_only)
    
    def _save_file(self):
        """Save current file (State pattern: behavior depends on edit_only_mode)."""
        tab = self.tab_widget.currentWidget()
        if not tab:
            return
        
        # Check if edit-only mode (State pattern)
        if hasattr(tab, 'edit_only_mode') and tab.edit_only_mode:
            # Edit-only: open Save As dialog to convert to file-backed
            reply = QMessageBox.question(
                self,
                "Edit-Only Mode",
                "This editor is in Edit-Only mode.\n\nSave will convert it to a file-backed editor.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._save_file_as()
            return
        
        if not tab.file_path:
            self._save_file_as()
            return
        
        # Handle different tab types
        if isinstance(tab, JsonEditorTab):
            success, error_msg = tab.save_file()
            if success:
                self._update_tab_title(tab)
                self.lbl_status.setText(f"Saved: {os.path.basename(tab.file_path)}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{error_msg}")
        else:
            # EditorTab
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
            "All Files (*);;JSON Files (*.json);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;TypeScript (*.ts);;HTML (*.html)"
        )
        
        if not file_path:
            return
        
        # Handle different tab types
        if isinstance(tab, JsonEditorTab):
            success, error_msg = tab.save_file(file_path)
            if success:
                self._update_tab_title(tab)
                self.lbl_status.setText(f"Saved as: {os.path.basename(file_path)}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{error_msg}")
        else:
            # EditorTab
            if tab.save_file(file_path):
                self._update_tab_title(tab)
                self.lbl_status.setText(f"Saved as: {os.path.basename(file_path)}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{file_path}")
    
    def _close_current_tab(self):
        """Close currently active tab."""
        self._close_tab(self.tab_widget.currentIndex())
    
    def _close_tab(self, index: int):
        """Close tab at index with edit-only mode handling."""
        if index < 0:
            return
        
        tab = self.tab_widget.widget(index)
        
        # Check if modified
        if hasattr(tab, 'is_modified') and tab.is_modified:
            # Special handling for edit-only tabs (requirement #6)
            if hasattr(tab, 'edit_only_mode') and tab.edit_only_mode:
                msg = QMessageBox(self)
                msg.setWindowTitle("Close Edit-Only Tab")
                msg.setText(f"'{tab.get_tab_title()}' has unsaved changes.")
                msg.setInformativeText("What would you like to do?")
                
                btn_save = msg.addButton("Save to File", QMessageBox.ActionRole)
                btn_clipboard = msg.addButton("Copy to Clipboard", QMessageBox.ActionRole)
                btn_discard = msg.addButton("Discard", QMessageBox.DestructiveRole)
                btn_cancel = msg.addButton("Cancel", QMessageBox.RejectRole)
                
                msg.exec_()
                clicked = msg.clickedButton()
                
                if clicked == btn_save:
                    # Save to file
                    self.tab_widget.setCurrentIndex(index)
                    self._save_file_as()
                    # Check if actually saved (file_path set)
                    if not tab.file_path:
                        return  # User cancelled save, don't close
                elif clicked == btn_clipboard:
                    # Copy to clipboard
                    clipboard = QApplication.clipboard()
                    clipboard.setText(tab.editor.toPlainText())
                    self.lbl_status.setText("Content copied to clipboard")
                elif clicked == btn_cancel:
                    return
                # btn_discard falls through to remove tab
            else:
                # Normal file-backed tab
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
                        # Handle different tab types
                        if isinstance(tab, JsonEditorTab):
                            success, _ = tab.save_file()
                        else:
                            success = tab.save_file()
                        
                        if not success:
                            return  # Don't close if save failed
                elif reply == QMessageBox.Cancel:
                    return
        
        self.tab_widget.removeTab(index)
        self.lbl_status.setText(f"Closed: {tab.get_tab_title()}")
    
    def _on_tab_changed(self, index: int):
        """Handle tab change with edit-only mode indicators."""
        if index >= 0:
            tab = self.tab_widget.widget(index)
            
            # Get editor type
            if isinstance(tab, JsonEditorTab):
                editor_type = "JSON Editor"
            else:
                editor_type = "Text Editor"
            
            # Get mode status (visual indicator #4)
            if hasattr(tab, 'edit_only_mode') and tab.edit_only_mode:
                mode_text = " - Edit-Only Mode"
                # Change status label color (visual indicator #2)
                self.lbl_status.setStyleSheet("color: #FF8C00; font-weight: bold;")  # Orange
            else:
                mode_text = ""
                self.lbl_status.setStyleSheet("color: #6A9955;")  # Green (normal)
            
            if hasattr(tab, 'file_path') and tab.file_path:
                self.lbl_status.setText(f"{editor_type}{mode_text}: {os.path.basename(tab.file_path)}")
            else:
                self.lbl_status.setText(f"{editor_type}{mode_text}: {tab.get_tab_title()}")
        else:
            self.lbl_status.setText("Ready")
            self.lbl_status.setStyleSheet("color: #6A9955;")
    
    def _update_tab_title(self, tab: EditorTab):
        """Update tab title based on modified state."""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, tab.get_display_title())
    
    def _on_auto_save_toggled(self, state):
        """Handle auto-save checkbox toggle."""
        enabled = (state == Qt.Checked)
        self.auto_save_enabled = enabled
        
        # Save preference to QSettings
        self.settings.setValue("auto_save_enabled", enabled)
        
        # Apply to all open tabs
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'set_auto_save'):
                tab.set_auto_save(enabled)
                # Connect auto_saved signal for status update
                if enabled and not tab.auto_saved.receivers(self._on_auto_saved):
                    tab.auto_saved.connect(lambda t=tab: self._on_auto_saved(t))
        
        # Update status
        status_text = "Auto-save enabled" if enabled else "Auto-save disabled"
        self.lbl_status.setText(status_text)
    
    def _on_auto_saved(self, tab: EditorTab):
        """Handle auto-save completion."""
        if hasattr(tab, 'file_path') and tab.file_path:
            filename = os.path.basename(tab.file_path)
            self.lbl_status.setText(f"💾 Auto-saved: {filename}")
            
            # Reset status after 2 seconds
            QTimer.singleShot(2000, lambda: self._on_tab_changed(self.tab_widget.currentIndex()))
    
    def _add_recent_file(self, file_path: str):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:self.max_recent]
    
    def open_file_path(self, file_path: str, edit_only: bool = False):
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
            if hasattr(tab, 'file_path') and tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return
        
        # Create appropriate tab based on file extension
        tab = self._create_tab_for_file(file_path, edit_only)
        
        if tab.load_file(file_path):
            # If edit-only, disconnect from file
            if edit_only:
                tab.file_path = None
            
            tab.modified_changed.connect(lambda modified: self._update_tab_title(tab))
            tab.edit_only_changed.connect(lambda: self._update_tab_title(tab))
            index = self.tab_widget.addTab(tab, tab.get_display_title())
            self.tab_widget.setCurrentIndex(index)
            
            if not edit_only:
                self._add_recent_file(file_path)
            
            editor_type = "JSON Editor" if isinstance(tab, JsonEditorTab) else "Text Editor"
            mode_text = " (Edit-Only)" if edit_only else ""
            self.lbl_status.setText(f"Opened in {editor_type}{mode_text}: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{file_path}")
    
    def has_unsaved_changes(self) -> bool:
        """
        Check if any tab has unsaved changes (v2.9.40).
        
        Returns:
            True if any tab is modified and not saved, False otherwise
        """
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'modified') and tab.modified:
                # Only consider real unsaved changes (file-backed tabs)
                if hasattr(tab, 'file_path') and tab.file_path:
                    return True
        return False
    
    def save_file(self):
        """Public API for saving current file (v2.9.40)."""
        self._save_file()
