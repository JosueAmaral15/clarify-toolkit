"""
JSON Editor Tab - Advanced JSON Editing with Tree Navigation

Complete JSON editor with:
- Real-time validation with error indicators
- Tree view for hierarchical navigation
- Format JSON (2/4 spaces indentation)
- Search by key/value
- Collapse/Expand nodes
- Syntax highlighting

Patterns:
- Facade (GoF): Simplifies JSON editing operations
- Composite (GoF): Tree structure for JSON hierarchy
- Command (GoF): Search operations
- Observer (GoF): Signals for state changes

Refactored in v2.9.114 (Phase 2.6):
- Extracted JsonTreeWidget → src/gui/widgets/json_tree_widget.py
- Extracted JsonSearchDialog → src/gui/dialogs/json_search_dialog.py
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy SyntaxHighlighter import
# pylint: disable=broad-exception-caught  # GUI robustness

from __future__ import annotations

import os
import json
from typing import Optional, Tuple

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QSplitter, QMessageBox, QComboBox
)
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor, QTextFormat

from src.core.insert import insert_at_line
from src.gui.panels import InsertPanel, RegexInsertPanel
from src.i18n.translator import tr, tooltip_tr

from .dialogs import JsonSearchDialog
from .json_validator import JsonValidator
from .widgets import JsonTreeWidget, SyntaxHighlighter


class JsonEditorTab(QWidget):
    """
    Complete JSON editor tab with validation, tree view, and search.

    Pattern: Facade (GoF)
    - Provides unified interface to JSON editing subsystems
    - Simplifies interaction between validator, tree, search

    Pattern: Observer (GoF)
    - Emits signals for modified state, validation state

    Features:
    - Real-time validation with visual indicators
    - Tree view for navigation
    - Format JSON (2/4 spaces)
    - Search by key/value
    - Syntax highlighting (reuses existing SyntaxHighlighter)
    """

    modified_changed = Signal(bool)
    validation_changed = Signal(bool, str)  # (is_valid, error_msg)
    edit_only_changed = Signal(bool)  # Emitted when edit-only mode changes

    def __init__(self, file_path: Optional[str] = None, parent=None, edit_only_mode: bool = False):
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        self.edit_only_mode = edit_only_mode  # State pattern: changes save behavior
        self.validator = JsonValidator()
        self._diagnostic_selections: dict[str, list[QTextEdit.ExtraSelection]] = {}
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.setInterval(500)  # 500ms debounce

        self._setup_ui()
        self._connect_signals()

        if file_path:
            self.load_file(file_path)

    def _setup_ui(self):
        """Setup JSON editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QHBoxLayout()

        self.btn_format = QPushButton(tr("json_editor.btn_format"))
        self.btn_format.setToolTip(tooltip_tr("json_editor.tooltip_format"))

        self.combo_indent = QComboBox()
        self.combo_indent.addItems([
            tr("json_editor.combo_2spaces"), tr("json_editor.combo_4spaces"),
            tr("json_editor.combo_minify")
        ])
        self.combo_indent.setToolTip(tooltip_tr("json_editor.tooltip_indent"))

        self.btn_validate = QPushButton(tr("json_editor.btn_validate"))
        self.btn_validate.setToolTip(tooltip_tr("json_editor.tooltip_validate"))

        self.btn_search = QPushButton(tr("json_editor.btn_search"))
        self.btn_search.setToolTip(tooltip_tr("json_editor.tooltip_search"))

        self.btn_collapse = QPushButton(tr("json_editor.btn_collapse"))
        self.btn_collapse.setToolTip(tooltip_tr("json_editor.tooltip_collapse"))
        self.btn_expand = QPushButton(tr("json_editor.btn_expand"))
        self.btn_expand.setToolTip(tooltip_tr("json_editor.tooltip_expand"))

        toolbar.addWidget(self.btn_format)
        toolbar.addWidget(self.combo_indent)
        toolbar.addWidget(self.btn_validate)
        toolbar.addWidget(self.btn_search)
        toolbar.addWidget(self.btn_collapse)
        toolbar.addWidget(self.btn_expand)
        toolbar.addStretch()

        # Insert Panel button (v2.9.110)
        self.btn_insert_panel = QPushButton(tr("json_editor.btn_insert_panel"))
        self.btn_insert_panel.setToolTip(tooltip_tr("json_editor.tooltip_insert_panel"))
        toolbar.addWidget(self.btn_insert_panel)

        # Regex Insert Panel button (v2.9.111)
        self.btn_regex_insert = QPushButton(tr("json_editor.btn_regex_insert"))
        self.btn_regex_insert.setToolTip(tooltip_tr("json_editor.tooltip_regex_insert"))
        toolbar.addWidget(self.btn_regex_insert)

        layout.addLayout(toolbar)

        # Insert Panel (v2.9.110 - collapsible below toolbar)
        self.insert_panel = InsertPanel(self, "json_editor_insert")
        self.insert_panel.insert_requested.connect(self._handle_insert)
        self.insert_panel.setVisible(False)  # Hidden by default
        layout.addWidget(self.insert_panel)

        # Regex Insert Panel (v2.9.111 - collapsible below toolbar)
        self.regex_insert_panel = RegexInsertPanel(self, "json_editor_regex_insert")
        self.regex_insert_panel.insert_requested.connect(self._handle_regex_insert)
        self.regex_insert_panel.setVisible(False)  # Hidden by default
        layout.addWidget(self.regex_insert_panel)

        # Splitter: Editor (70%) | Tree View (30%)
        splitter = QSplitter(Qt.Horizontal)

        # Left: Editor with validation indicator
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        # Validation status
        self.lbl_validation = QLabel(tr("json_editor.lbl_valid"))
        self.lbl_validation.setStyleSheet("color: #6A9955; font-weight: bold;")
        self.lbl_validation.setToolTip(tooltip_tr("json_editor.tooltip_validation_status"))
        editor_layout.addWidget(self.lbl_validation)

        # Text editor
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabStopDistance(40)
        self.editor.setToolTip(tooltip_tr("json_editor.tooltip_editor"))
        font = QFont("Courier New", 10)
        self.editor.setFont(font)
        editor_layout.addWidget(self.editor)

        splitter.addWidget(editor_container)

        # Right: Tree view
        self.tree = JsonTreeWidget()
        self.tree.setToolTip(tooltip_tr("json_editor.tooltip_tree"))
        splitter.addWidget(self.tree)

        # Set initial splitter sizes (70% editor, 30% tree)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

        # Setup syntax highlighter
        self.highlighter = SyntaxHighlighter(self.editor.document(), "json")

    def _connect_signals(self):
        self.btn_regex_insert.clicked.connect(self._toggle_regex_insert_panel)
        # """Connect signals."""  # Commented placeholder
        self.editor.textChanged.connect(self._on_text_changed)
        self.validation_timer.timeout.connect(self._validate)
        self.tree.node_clicked.connect(self._jump_to_line)

        self.btn_insert_panel.clicked.connect(self._toggle_insert_panel)

        self.btn_format.clicked.connect(self._format_json)
        self.btn_validate.clicked.connect(self._validate)
        self.btn_search.clicked.connect(self._show_search)
        self.btn_collapse.clicked.connect(self.tree.collapseAll)
        self.btn_expand.clicked.connect(self.tree.expandAll)

    def _on_text_changed(self):
        """Handle text changes - mark as modified and schedule validation."""
        if not self.is_modified:
            self.is_modified = True
            self.modified_changed.emit(True)

        # Schedule validation (debounced)
        self.validation_timer.start()

    def _apply_diagnostic_selections(self) -> None:
        """Apply all active diagnostic highlights to the text editor."""
        selections = []
        for source in sorted(self._diagnostic_selections):
            selections.extend(self._diagnostic_selections[source])
        self.editor.setExtraSelections(selections)

    def clear_diagnostic(self, source: str | None = None) -> None:
        """Clear one diagnostic source or all active diagnostic highlights."""
        if source is None:
            self._diagnostic_selections.clear()
        else:
            self._diagnostic_selections.pop(source, None)
        self._apply_diagnostic_selections()

    def _cursor_for_line_col(self, line: int, col: int) -> QTextCursor | None:
        """Return a cursor positioned at a 1-based line and column."""
        block = self.editor.document().findBlockByNumber(max(0, line - 1))
        if not block.isValid():
            return None

        block_text_length = len(block.text())
        column_offset = min(max(0, col - 1), max(0, block_text_length))
        cursor = QTextCursor(block)
        cursor.setPosition(block.position() + column_offset)
        return cursor

    def show_diagnostic(
        self,
        line: int,
        col: int,
        message: str,
        source: str = "json",
        length: int = 1,
    ) -> None:
        """Show a line highlight and wave underline for a validation diagnostic."""
        cursor = self._cursor_for_line_col(line, col)
        if cursor is None:
            self.clear_diagnostic(source)
            return

        line_selection = QTextEdit.ExtraSelection()
        line_selection.cursor = QTextCursor(cursor.block())
        line_selection.format.setBackground(QColor(244, 71, 71, 32))
        line_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        if message:
            line_selection.format.setToolTip(message)

        underline_selection = QTextEdit.ExtraSelection()
        underline_selection.cursor = QTextCursor(cursor)
        underline_length = max(1, length)
        underline_selection.cursor.movePosition(
            QTextCursor.NextCharacter,
            QTextCursor.KeepAnchor,
            underline_length,
        )
        underline_format = QTextCharFormat()
        underline_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        underline_format.setUnderlineColor(QColor("#F44747"))
        if message:
            underline_format.setToolTip(message)
        underline_selection.format = underline_format

        self._diagnostic_selections[source] = [line_selection, underline_selection]
        self._apply_diagnostic_selections()

    def _line_col_for_json_path(self, path: tuple) -> tuple[int, int]:
        """Best-effort lookup for a JSONPath-like tuple in the editor text."""
        if not path:
            return (1, 1)

        text = self.editor.toPlainText()
        first_key = next((part for part in path if isinstance(part, str)), None)
        if not first_key:
            return (1, 1)

        needle = json.dumps(first_key, ensure_ascii=False)
        offset = text.find(needle)
        if offset < 0:
            return (1, 1)

        before = text[:offset]
        line = before.count("\n") + 1
        line_start = before.rfind("\n") + 1
        col = offset - line_start + 1
        return (line, col)

    def show_schema_diagnostic(self, message: str, path: tuple = ()) -> None:
        """Show a schema validation diagnostic at the best matching JSON location."""
        first_line = message.splitlines()[0] if message else "Schema validation error"
        self.lbl_validation.setText(f"✗ Schema error: {first_line}")
        self.lbl_validation.setStyleSheet("color: #F44747; font-weight: bold;")
        line, col = self._line_col_for_json_path(path)
        length = 1
        first_key = next((part for part in path if isinstance(part, str)), None)
        if first_key:
            length = len(json.dumps(first_key, ensure_ascii=False))
        self.show_diagnostic(line, col, message, source="json_schema", length=length)

    def _validate(self):
        """
        Validate JSON and update UI indicators.

        Pattern: Strategy (validation algorithm)
        """
        text = self.editor.toPlainText()
        result = self.validator.validate(text)

        if result.is_valid:
            self.lbl_validation.setText("✓ Valid JSON")
            self.lbl_validation.setStyleSheet("color: #6A9955; font-weight: bold;")
            self.editor.setStyleSheet("")
            self.clear_diagnostic("json")
            self.clear_diagnostic("json_schema")

            # Update tree view
            self.tree.build_tree(text)

            self.validation_changed.emit(True, "")
        else:
            error_text = f"✗ Invalid JSON (line {result.line}, col {result.col}): {result.error_msg}"
            self.lbl_validation.setText(error_text)
            self.lbl_validation.setStyleSheet("color: #F44747; font-weight: bold;")
            self.editor.setStyleSheet("QTextEdit { border: 2px solid #F44747; }")
            self.show_diagnostic(result.line, result.col, error_text, source="json")
            self.clear_diagnostic("json_schema")

            self.validation_changed.emit(False, error_text)

    def _format_json(self):
        """Format JSON with selected indentation."""
        text = self.editor.toPlainText()
        indent_choice = self.combo_indent.currentText()

        if indent_choice == "Minify":
            success, result = self.validator.minify_json(text)
        else:
            indent = 2 if "2" in indent_choice else 4
            success, result = self.validator.format_json(text, indent)

        if success:
            self.editor.blockSignals(True)
            self.editor.setPlainText(result)
            self.editor.blockSignals(False)
            self._validate()
        else:
            QMessageBox.warning(self, tr("json_editor.msg_format_error_title"), result)

    def _show_search(self):
        """Show search dialog."""
        dialog = JsonSearchDialog(self.editor, self)
        dialog.exec()

    def _jump_to_line(self, line: int):
        """Jump editor cursor to specified line."""
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(line - 1):
            cursor.movePosition(QTextCursor.Down)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _toggle_insert_panel(self):
        """Toggle Insert Panel visibility (v2.9.110)."""
        if self.insert_panel.isVisible():
            self.insert_panel.setVisible(False)
            self.btn_insert_panel.setText("📝 Insert")
        else:
            self.insert_panel.setVisible(True)
            self.btn_insert_panel.setText("✕ Close Insert")
            # Set line number to current cursor position
            cursor = self.editor.textCursor()
            block_number = cursor.blockNumber() + 1  # 1-based
            self.insert_panel.set_line_number(block_number)

    def _handle_insert(self, line_no, text, mode):
        """
        Handle insert in editor text (v2.9.110).

        Pattern: Command (GoF)
        Args:
            line_no: Target line number (1-based)
            text: Text to insert
            mode: Insertion mode (LEFT, RIGHT, REPLACE, INSERT_ABOVE, INSERT_BELOW)
        """
        content = self.editor.toPlainText()

        try:
            # Execute insertion
            new_content = insert_at_line(content, line_no, text, mode)

            # Update editor
            self.editor.blockSignals(True)
            self.editor.setPlainText(new_content)
            self.editor.blockSignals(False)

            # Mark as modified
            self._on_text_changed()

            # Hide panel
            self.insert_panel.setVisible(False)
            self.btn_insert_panel.setText("📝 Insert")

            # Show feedback
            QMessageBox.information(
                self,
                tr("json_editor.msg_insert_complete_title"),
                tr("json_editor.msg_insert_complete").format(line=line_no, mode=mode)
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("json_editor.msg_insert_error_title"),
                tr("json_editor.msg_insert_error").format(error=str(exc))
            )

    def _toggle_regex_insert_panel(self):
        """Toggle Regex Insert Panel visibility (v2.9.111)."""
        if self.regex_insert_panel.isVisible():
            self.regex_insert_panel.setVisible(False)
            self.btn_regex_insert.setText("🎯 Regex Insert")
        else:
            # Hide other panels
            self.insert_panel.setVisible(False)
            self.btn_insert_panel.setText("📝 Insert")

            # Show regex panel
            self.regex_insert_panel.setVisible(True)
            self.btn_regex_insert.setText("✕ Close Regex Insert")

            # Set source text for regex capture
            self.regex_insert_panel.set_source_text(self.editor.toPlainText())

    def _handle_regex_insert(self, target_key, new_key, new_value, position):
        """
        Handle regex insert in JSON (v2.9.111).

        Advanced JSON manipulation:
        - Finds target_key in JSON
        - Inserts new key/value based on position
        - Maintains JSON structure and formatting

        Args:
            target_key: Existing JSON key to target
            new_key: New key name
            new_value: New value (already processed with registers)
            position: "Inside (as child)", "Before (sibling)", "After (sibling)"
        """
        content = self.editor.toPlainText()

        try:
            # Parse JSON to validate
            json_obj = json.loads(content)

            # Find target key in JSON
            target_found, target_path = self._find_key_in_json(json_obj, target_key)

            if not target_found:
                QMessageBox.warning(
                    self,
                    tr("json_editor.msg_target_not_found_title"),
                    tr("json_editor.msg_target_not_found").format(
                        key=target_key,
                        available=', '.join(self._get_all_keys(json_obj)[:10])
                    )
                )
                return

            # Insert based on position
            if "Inside" in position:
                # Insert as child of target key
                new_json = self._insert_inside(json_obj, target_path, new_key, new_value)
            elif "Before" in position:
                # Insert before target key (sibling)
                new_json = self._insert_before(json_obj, target_path, new_key, new_value)
            else:  # "After"
                # Insert after target key (sibling)
                new_json = self._insert_after(json_obj, target_path, new_key, new_value)

            # Format and update editor
            formatted = json.dumps(new_json, indent=2, ensure_ascii=False)
            self.editor.blockSignals(True)
            self.editor.setPlainText(formatted)
            self.editor.blockSignals(False)

            # Mark as modified
            self._on_text_changed()

            # Hide panel
            self.regex_insert_panel.setVisible(False)
            self.btn_regex_insert.setText("🎯 Regex Insert")

            # Show feedback
            QMessageBox.information(
                self,
                tr("json_editor.msg_regex_insert_complete_title"),
                tr("json_editor.msg_regex_insert_complete").format(
                    key=new_key,
                    value=new_value,
                    position=position.lower(),
                    target=target_key
                )
            )

        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self,
                tr("json_editor.msg_json_error_title"),
                tr("json_editor.msg_json_error").format(error=str(e))
            )
        except Exception as _:
            QMessageBox.critical(
                self,
                tr("json_editor.msg_insert_error_title"),
                tr("json_editor.msg_regex_insert_error").format(error=str(e))
            )

    def _find_key_in_json(self, obj, key, path=None):
        """
        Find key in JSON recursively.

        Returns:
            Tuple of (found: bool, path: list)
        """
        if path is None:
            path = []

        if isinstance(obj, dict):
            if key in obj:
                return (True, path + [key])

            for k, v in obj.items():
                found, found_path = self._find_key_in_json(v, key, path + [k])
                if found:
                    return (found, found_path)

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                found, found_path = self._find_key_in_json(item, key, path + [i])
                if found:
                    return (found, found_path)

        return (False, [])

    def _get_all_keys(self, obj, keys=None):
        """Get all keys in JSON recursively."""
        if keys is None:
            keys = []

        if isinstance(obj, dict):
            keys.extend(obj.keys())
            for v in obj.values():
                self._get_all_keys(v, keys)
        elif isinstance(obj, list):
            for item in obj:
                self._get_all_keys(item, keys)

        return keys

    def _insert_inside(self, obj, path, new_key, new_value):
        """Insert as child of target key."""
        # Navigate to target
        target = obj
        for key in path:
            target = target[key]

        # Ensure target is dict
        if not isinstance(target, dict):
            raise ValueError(f"Target '{path[-1]}' is not an object, cannot insert inside")

        # Insert new key
        target[new_key] = self._parse_value(new_value)
        return obj

    def _insert_before(self, obj, path, new_key, new_value):
        """Insert before target key (sibling)."""
        if len(path) < 2:
            # Root level insert
            new_obj = {new_key: self._parse_value(new_value)}
            new_obj.update(obj)
            return new_obj

        # Navigate to parent
        parent = obj
        for key in path[:-1]:
            parent = parent[key]

        target_key = path[-1]

        # Rebuild dict with new key before target
        if isinstance(parent, dict):
            new_parent = {}
            for k, v in parent.items():
                if k == target_key:
                    new_parent[new_key] = self._parse_value(new_value)
                new_parent[k] = v

            # Update parent reference
            if len(path) == 1:
                return new_parent
            else:
                # Navigate and update
                temp = obj
                for key in path[:-2]:
                    temp = temp[key]
                temp[path[-2]] = new_parent

        return obj

    def _insert_after(self, obj, path, new_key, new_value):
        """Insert after target key (sibling)."""
        if len(path) < 2:
            # Root level insert
            obj[new_key] = self._parse_value(new_value)
            return obj

        # Navigate to parent
        parent = obj
        for key in path[:-1]:
            parent = parent[key]

        target_key = path[-1]

        # Rebuild dict with new key after target
        if isinstance(parent, dict):
            new_parent = {}
            for k, v in parent.items():
                new_parent[k] = v
                if k == target_key:
                    new_parent[new_key] = self._parse_value(new_value)

            # Update parent reference
            if len(path) == 1:
                return new_parent
            else:
                temp = obj
                for key in path[:-2]:
                    temp = temp[key]
                temp[path[-2]] = new_parent

        return obj

    def _parse_value(self, value_str: str):
        """
        Parse value string to appropriate JSON type.

        Attempts to parse as:
        1. JSON (for objects/arrays)
        2. Number
        3. Boolean
        4. Null
        5. String (default)
        """
        value_str = value_str.strip()

        # Try JSON parse (objects, arrays, etc.)
        if value_str.startswith('{') or value_str.startswith('['):
            try:
                return json.loads(value_str)
            except Exception:
                pass

        # Try number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except Exception:
            pass

        # Try boolean
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False

        # Try null
        if value_str.lower() == 'null':
            return None

        # Default to string
        return value_str

    def load_file(self, file_path: str) -> bool:
        """Load JSON file into editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.file_path = file_path
            self.editor.blockSignals(True)
            self.editor.setPlainText(content)
            self.editor.blockSignals(False)
            self.is_modified = False
            self.modified_changed.emit(False)

            # Validate and build tree
            self._validate()

            return True
        except Exception as _:
            return False

    def save_file(self, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save editor content to file.

        Returns:
            Tuple of (success, error_message)
        """
        save_path = file_path or self.file_path
        if not save_path:
            return (False, "No file path specified")

        # Validate before save
        text = self.editor.toPlainText()
        result = self.validator.validate(text)

        if not result.is_valid:
            # Warning: Invalid JSON - allow save anyway
            reply = QMessageBox.question(
                self,
                "Invalid JSON",
                f"JSON is invalid:\n{result.error_msg}\n\nSave anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return (False, "Save cancelled by user")

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

            self.file_path = save_path
            self.is_modified = False
            self.modified_changed.emit(False)

            return (True, "")
        except Exception as exc:
            return (False, str(exc))

    def get_tab_title(self) -> str:
        """Get title for tab."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return "Untitled.json"

    def get_display_title(self) -> str:
        """Get display title with modified indicator, JSON icon, and edit-only indicator."""
        title = "🗎 " + self.get_tab_title()  # JSON icon

        # Edit-only indicator (visual indicator #1)
        if self.edit_only_mode:
            title = "🔒 " + title

        if self.is_modified:
            title += " *"
        return title

    def get_status_text(self) -> str:
        """Get status bar text with mode indicator."""
        status = "JSON Editor"
        if self.edit_only_mode:
            status = "JSON Editor - Edit-Only Mode"  # Visual indicator #4
        return status

    def toggle_edit_only_mode(self):
        """Toggle edit-only mode on/off (State pattern transition)."""
        # JsonEditorTab inherits EditorTab functionality but can override
        # For now, just emit signal - EditorDock will handle
        self.edit_only_mode = not self.edit_only_mode
        self.edit_only_changed.emit(self.edit_only_mode)
