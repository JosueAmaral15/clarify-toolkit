"""
Editor Dock - Clarify Editor

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

Refactored in v2.9.114 (Phase 2.5):
- Extracted SyntaxHighlighter → src/gui/widgets/syntax_highlighter.py
- Extracted EditorTab → src/gui/widgets/editor_tab.py
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy QSettings import

from __future__ import annotations

import difflib
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from PySide6.QtCore import (
    QDir, QEvent, QFile, QFileSystemWatcher, QModelIndex, QObject, QSize, Qt,
    QThread, QUrl,
    QTimer, Slot
)
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QDialog, QHBoxLayout, QInputDialog, QLineEdit, QMenuBar,
    QListWidget, QListWidgetItem, QPushButton, QRadioButton, QSpinBox,
    QVBoxLayout, QWidget,
    QLabel, QFileDialog, QMessageBox, QTextEdit, QTabWidget,
    QCheckBox, QFileSystemModel, QFrame, QMenu, QApplication, QSplitter,
    QTreeView, QSizePolicy, QStyle, QToolBar
)
from PySide6.QtGui import (
    QAction, QColor, QDesktopServices, QIcon, QKeySequence, QPainter, QTextCursor,
    QTextDocument,
    QTextOption
)

from src.i18n.translator import get_translator, tooltip_tr, tr
from src.editor_recovery import (
    DEFAULT_RETENTION_HOURS,
    RecoveryPruneReport,
    RecoverySnapshotError,
    UnsavedRecoveryStore,
)
from src.editor_notes import TemporaryNoteError, TemporaryNoteStore
from src.editor_reference_updates import (
    ReferenceUpdateError,
    analyze_rename_references,
    apply_reference_updates,
)
from src.core.editor_find import (
    MAX_QUERY_CHARS,
    FindOptions,
    FindValidationError,
    control_escape_preview,
    find_matches,
    replacement_for_match,
)
from src.product_identity import EDITOR_NAME
from src.shortcut_manager import ShortcutManager
from src.utils.atomic_files import write_text_atomically

from .base_dock import BaseDock
from .editor_recovery_lifecycle import EditorRecoveryLifecycle
from .json_editor_tab import JsonEditorTab
from .widgets import EditorTab


class _ExternalReloadError(RuntimeError):
    """A stable external-file revision could not be read safely."""

    def __init__(self, reason: str, detail: str = ""):
        super().__init__(detail or reason)
        self.reason = reason
        self.detail = detail


class _EditorFindHistory:
    """Private bounded query/replacement history for one open editor buffer."""

    def __init__(self, max_entries: int = 5):
        self.max_entries = max(1, int(max_entries))
        self.entries: list[tuple[str, str]] = []

    def remember(self, query: str, replacement: str = "") -> None:
        query = str(query)[:MAX_QUERY_CHARS]
        replacement = str(replacement)[:MAX_QUERY_CHARS]
        if not query:
            return
        entry = (query, replacement)
        self.entries = [item for item in self.entries if item != entry]
        self.entries.insert(0, entry)
        del self.entries[self.max_entries :]

    def current(self) -> tuple[str, str]:
        return self.entries[0] if self.entries else ("", "")

    def clear(self) -> None:
        self.entries.clear()


class _EditorFindDialog(QDialog):
    """Bounded find/find-and-replace dialog for one editor document."""

    def __init__(
        self,
        editor,
        replace_enabled: bool = False,
        parent=None,
        *,
        file_path: str | None = None,
        state: dict | None = None,
        state_changed=None,
        history: _EditorFindHistory | None = None,
        selection_query: str = "",
        close_requested=None,
        presentation_toggle_requested=None,
    ):
        super().__init__(parent)
        self.editor = editor
        self.replace_enabled = replace_enabled
        self.file_path = file_path
        self.state = state if state is not None else {}
        self._state_changed = state_changed
        self.history = history if history is not None else _EditorFindHistory()
        self._selection_query = str(selection_query)[:MAX_QUERY_CHARS]
        self._history_index = -1 if self._selection_query else 0
        self.matches = ()
        self.current_match_index = -1
        self._result_truncated = False
        self._scope_fallback = False
        self._mutating = False
        self._close_requested = close_requested
        self._presentation_toggle_requested = presentation_toggle_requested
        self._presentation_mode = "floating"
        self._shutting_down = False
        self._translation_connected = False

        self.setMinimumWidth(560)
        self._setup_ui()
        self._restore_state()
        self._connect_signals()
        get_translator().languageChanged.connect(self._retranslate_ui)
        self._translation_connected = True
        self._retranslate_ui()
        self._recalculate_matches()
        if self.find_input.text():
            self._sync_current_match_to_cursor()
        self._update_history_button()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        find_layout = QHBoxLayout()
        self.lbl_find = QLabel()
        find_layout.addWidget(self.lbl_find)
        self.find_input = QLineEdit()
        self.find_input.setMaxLength(MAX_QUERY_CHARS)
        find_layout.addWidget(self.find_input)
        self.btn_previous_value = QPushButton()
        find_layout.addWidget(self.btn_previous_value)
        layout.addLayout(find_layout)

        self.replace_input = QLineEdit()
        self.replace_input.setMaxLength(MAX_QUERY_CHARS)
        replace_layout = QHBoxLayout()
        self.lbl_replace = QLabel()
        replace_layout.addWidget(self.lbl_replace)
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        self.chk_case_sensitive = QCheckBox()
        self.chk_whole_word = QCheckBox()
        self.chk_regex = QCheckBox()
        self.chk_interpret_escapes = QCheckBox()
        options_layout.addWidget(self.chk_case_sensitive)
        options_layout.addWidget(self.chk_whole_word)
        options_layout.addWidget(self.chk_regex)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        layout.addWidget(self.chk_interpret_escapes)
        self.lbl_escape_preview = QLabel("")
        self.lbl_escape_preview.setWordWrap(True)
        layout.addWidget(self.lbl_escape_preview)

        scope_layout = QHBoxLayout()
        self.lbl_find_scope = QLabel()
        scope_layout.addWidget(self.lbl_find_scope)
        self.scope_group = QButtonGroup(self)
        self.radio_all_text = QRadioButton()
        self.radio_only_strings = QRadioButton()
        self.radio_only_variables = QRadioButton()
        self.radio_only_comments = QRadioButton()
        for scope, button in (
            ("all", self.radio_all_text),
            ("strings", self.radio_only_strings),
            ("variables", self.radio_only_variables),
            ("comments", self.radio_only_comments),
        ):
            self.scope_group.addButton(button)
            button.setProperty("find_scope", scope)
            scope_layout.addWidget(button)
        scope_layout.addStretch()
        layout.addLayout(scope_layout)

        inverted_layout = QHBoxLayout()
        self.chk_inverted = QCheckBox()
        inverted_layout.addWidget(self.chk_inverted)
        self.lbl_inverted_unit = QLabel()
        inverted_layout.addWidget(self.lbl_inverted_unit)
        self.cmb_inverted_unit = QComboBox()
        for key in ("line", "token", "interval"):
            self.cmb_inverted_unit.addItem("", key)
        self.cmb_inverted_unit.setEnabled(False)
        inverted_layout.addWidget(self.cmb_inverted_unit)
        inverted_layout.addStretch()
        layout.addLayout(inverted_layout)

        line_layout = QHBoxLayout()
        self.lbl_start_line = QLabel()
        line_layout.addWidget(self.lbl_start_line)
        self.start_line = QSpinBox()
        self.start_line.setRange(0, self._plain_text_line_count())
        line_layout.addWidget(self.start_line)
        self.lbl_end_line = QLabel()
        line_layout.addWidget(self.lbl_end_line)
        self.end_line = QSpinBox()
        self.end_line.setRange(0, self._plain_text_line_count())
        line_layout.addWidget(self.end_line)
        line_layout.addStretch()
        layout.addLayout(line_layout)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

        btn_layout = QHBoxLayout()
        self.btn_find_previous = QPushButton()
        self.btn_find_next = QPushButton()
        btn_layout.addWidget(self.btn_find_previous)
        btn_layout.addWidget(self.btn_find_next)

        self.btn_replace = QPushButton()
        self.btn_replace_all = QPushButton()
        btn_layout.addWidget(self.btn_replace)
        btn_layout.addWidget(self.btn_replace_all)

        self.btn_clear = QPushButton()
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        self.btn_toggle_presentation = QPushButton()
        btn_layout.addWidget(self.btn_toggle_presentation)
        self.btn_close = QPushButton()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        for button in self.findChildren(QPushButton):
            button.setAutoDefault(False)
            button.setDefault(False)
        self.find_input.installEventFilter(self)
        self._update_replace_visibility()

    def _connect_signals(self):
        self.find_input.textChanged.connect(self._recalculate_matches)
        self.find_input.textEdited.connect(self._on_value_edited)
        self.replace_input.textEdited.connect(self._on_value_edited)
        self.chk_case_sensitive.toggled.connect(self._on_options_changed)
        self.chk_whole_word.toggled.connect(self._on_options_changed)
        self.chk_regex.toggled.connect(self._on_options_changed)
        self.chk_interpret_escapes.toggled.connect(self._on_options_changed)
        self.replace_input.textChanged.connect(self._update_escape_preview)
        self.scope_group.buttonToggled.connect(self._on_scope_toggled)
        self.chk_inverted.toggled.connect(self._on_inverted_toggled)
        self.cmb_inverted_unit.currentIndexChanged.connect(
            self._on_options_changed
        )
        self.start_line.valueChanged.connect(self._recalculate_matches)
        self.end_line.valueChanged.connect(self._recalculate_matches)
        self._connect_editor_signals()
        self.btn_previous_value.clicked.connect(self._restore_previous_value)
        self.btn_clear.clicked.connect(self._clear_find_state)
        self.btn_find_previous.clicked.connect(self._find_previous)
        self.btn_find_next.clicked.connect(self._find_next)
        self.btn_close.clicked.connect(self.close)
        self.btn_toggle_presentation.clicked.connect(
            self._request_presentation_toggle
        )
        self.btn_replace.clicked.connect(self._replace_current)
        self.btn_replace_all.clicked.connect(self._replace_all)

    def _connect_editor_signals(self) -> None:
        self.editor.textChanged.connect(self._on_editor_text_changed)
        self.editor.cursorPositionChanged.connect(
            self._on_editor_cursor_position_changed
        )

    def _disconnect_editor_signals(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        for signal, slot in (
            (editor.textChanged, self._on_editor_text_changed),
            (
                editor.cursorPositionChanged,
                self._on_editor_cursor_position_changed,
            ),
        ):
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass

    def bind_editor(
        self,
        editor,
        *,
        replace_enabled: bool,
        file_path: str | None,
        history: _EditorFindHistory,
        selection_query: str = "",
    ) -> None:
        """Retarget this one session to an active Editor buffer or split."""
        history_changed = history is not self.history
        editor_changed = editor is not self.editor
        if history_changed:
            self._remember_current_values()
        if editor_changed:
            self._disconnect_editor_signals()
            self.editor = editor
            self._connect_editor_signals()

        self.replace_enabled = bool(replace_enabled)
        self.file_path = file_path
        self.history = history
        self._selection_query = str(selection_query)[:MAX_QUERY_CHARS]
        self._history_index = -1 if self._selection_query else 0
        self._update_replace_visibility()
        self._retranslate_ui()

        line_count = self._plain_text_line_count()
        self.start_line.setMaximum(line_count)
        self.end_line.setMaximum(line_count)
        if self._selection_query:
            self.find_input.setText(self._selection_query)
            self.find_input.selectAll()
        elif history_changed:
            query, replacement = self.history.current()
            self.find_input.setText(query)
            self.replace_input.setText(replacement)
        self._recalculate_matches()
        if self.find_input.text():
            self._sync_current_match_to_cursor()
        self._update_history_button()

    def _request_presentation_toggle(self) -> None:
        if self._presentation_toggle_requested is not None:
            self._presentation_toggle_requested()

    def _update_replace_visibility(self) -> None:
        for widget in (
            self.lbl_replace,
            self.replace_input,
            self.btn_replace,
            self.btn_replace_all,
        ):
            widget.setVisible(self.replace_enabled)

    def set_presentation_mode(self, mode: str) -> None:
        """Refresh controls after the owner reparents this same session."""
        self._presentation_mode = (
            "floating" if mode == "floating" else "docked"
        )
        self._retranslate_ui()

    def _retranslate_ui(self, _language=None) -> None:
        title_key = (
            "editor.find_replace_dialog_title"
            if self.replace_enabled
            else "editor.find_dialog_title"
        )
        self.setWindowTitle(tr(title_key))
        controls = (
            (self.lbl_find, "editor.lbl_find"),
            (self.lbl_replace, "editor.lbl_replace"),
            (self.chk_case_sensitive, "editor.chk_case_sensitive"),
            (self.chk_whole_word, "editor.chk_whole_word"),
            (self.chk_regex, "editor.chk_regex"),
            (self.chk_interpret_escapes, "editor.chk_interpret_escapes"),
            (self.lbl_find_scope, "editor.lbl_find_scope"),
            (self.radio_all_text, "editor.scope_all_text"),
            (self.radio_only_strings, "editor.scope_only_strings"),
            (self.radio_only_variables, "editor.scope_only_variables"),
            (self.radio_only_comments, "editor.scope_only_comments"),
            (self.chk_inverted, "editor.chk_inverted_search"),
            (self.lbl_inverted_unit, "editor.lbl_inverted_unit"),
            (self.lbl_start_line, "editor.lbl_start_line"),
            (self.lbl_end_line, "editor.lbl_end_line"),
            (self.btn_previous_value, "editor.btn_find_previous_value"),
            (self.btn_find_previous, "editor.btn_find_previous"),
            (self.btn_find_next, "editor.btn_find_next"),
            (self.btn_replace, "editor.btn_replace"),
            (self.btn_replace_all, "editor.btn_replace_all"),
            (self.btn_clear, "editor.btn_find_clear"),
            (self.btn_close, "editor.btn_close"),
        )
        for widget, key in controls:
            widget.setText(tr(key))
        for index, key in enumerate(("line", "token", "interval")):
            self.cmb_inverted_unit.setItemText(
                index,
                tr(f"editor.inverted_unit_{key}"),
            )
        self.start_line.setSpecialValueText(tr("editor.line_first"))
        self.end_line.setSpecialValueText(tr("editor.line_last"))
        toggle_key = (
            "editor.btn_find_dock"
            if self._presentation_mode == "floating"
            else "editor.btn_find_float"
        )
        self.btn_toggle_presentation.setText(tr(toggle_key))
        self.btn_toggle_presentation.setAccessibleName(tr(toggle_key))
        self.btn_previous_value.setToolTip(
            tr("editor.tooltip_find_previous_value")
        )
        self._update_escape_preview()
        self._update_status()

    def _restore_state(self) -> None:
        self.chk_case_sensitive.setChecked(bool(self.state.get("case_sensitive", False)))
        self.chk_whole_word.setChecked(bool(self.state.get("whole_word", False)))
        self.chk_regex.setChecked(bool(self.state.get("regex", False)))
        self.chk_interpret_escapes.setChecked(
            bool(self.state.get("interpret_escapes", False))
        )
        self.chk_interpret_escapes.setEnabled(not self.chk_regex.isChecked())
        scope = self.state.get("scope", "all")
        scope_buttons = {
            "all": self.radio_all_text,
            "strings": self.radio_only_strings,
            "variables": self.radio_only_variables,
            "comments": self.radio_only_comments,
        }
        scope_buttons.get(scope, self.radio_all_text).setChecked(True)
        inverted_unit = self.state.get("inverted_unit", "line")
        unit_index = self.cmb_inverted_unit.findData(inverted_unit)
        self.cmb_inverted_unit.setCurrentIndex(max(0, unit_index))
        inverted = bool(self.state.get("inverted", False))
        self.chk_inverted.setChecked(inverted)
        self.cmb_inverted_unit.setEnabled(inverted)
        if self._selection_query:
            query, replacement = self._selection_query, ""
        else:
            query, replacement = self.history.current()
        self.find_input.setText(query)
        if self.replace_enabled:
            self.replace_input.setText(replacement)

    def _save_state(self) -> None:
        self.state.update(
            {
                "case_sensitive": self.chk_case_sensitive.isChecked(),
                "whole_word": self.chk_whole_word.isChecked(),
                "regex": self.chk_regex.isChecked(),
                "interpret_escapes": self.chk_interpret_escapes.isChecked(),
                "scope": self._selected_scope(),
                "inverted": self.chk_inverted.isChecked(),
                "inverted_unit": self.cmb_inverted_unit.currentData() or "line",
            }
        )
        if self._state_changed is not None:
            self._state_changed(dict(self.state))

    def _selected_scope(self) -> str:
        button = self.scope_group.checkedButton()
        return button.property("find_scope") if button is not None else "all"

    def _options(self) -> FindOptions:
        return FindOptions(
            case_sensitive=self.chk_case_sensitive.isChecked(),
            whole_word=self.chk_whole_word.isChecked(),
            regex=self.chk_regex.isChecked(),
            interpret_escapes=self.chk_interpret_escapes.isChecked(),
            scope=self._selected_scope(),
            start_line=self.start_line.value() or None,
            end_line=self.end_line.value() or None,
            inverted=self.chk_inverted.isChecked(),
            inverted_unit=self.cmb_inverted_unit.currentData() or "line",
        )

    def _on_options_changed(self, _checked=False) -> None:
        self.chk_interpret_escapes.setEnabled(not self.chk_regex.isChecked())
        self._save_state()
        self._recalculate_matches()

    def _update_escape_preview(self, *_args) -> None:
        """Show how literal controls will be interpreted before navigation."""
        if self.chk_regex.isChecked():
            message = tr("editor.find_regex_escape_preview")
        elif not self.chk_interpret_escapes.isChecked():
            message = ""
        else:
            try:
                query = control_escape_preview(self.find_input.text())
                if self.replace_enabled:
                    replacement = control_escape_preview(self.replace_input.text())
                    message = tr("editor.find_escape_preview_with_replace").format(
                        query=query,
                        replacement=replacement,
                    )
                else:
                    message = tr("editor.find_escape_preview").format(query=query)
            except FindValidationError as error:
                message = tr("editor.find_error").format(error=error)
        self.lbl_escape_preview.setText(message)
        self.lbl_escape_preview.setAccessibleName(message)

    def _on_scope_toggled(self, _button, checked: bool) -> None:
        if checked:
            self._on_options_changed()

    def _on_inverted_toggled(self, checked: bool) -> None:
        self.cmb_inverted_unit.setEnabled(checked)
        self._on_options_changed()

    def _plain_text_line_count(self) -> int:
        """Use the same newline semantics as the pure matcher."""
        return self.editor.toPlainText().count("\n") + 1

    def _on_editor_text_changed(self) -> None:
        if self._mutating:
            return
        line_count = self._plain_text_line_count()
        self.start_line.setMaximum(line_count)
        self.end_line.setMaximum(line_count)
        self._recalculate_matches()
        self._sync_current_match_to_cursor()

    def _on_editor_cursor_position_changed(self) -> None:
        if not self._mutating and self.matches:
            self._sync_current_match_to_cursor()

    def _on_value_edited(self, _text: str) -> None:
        self._history_index = -1
        self._update_history_button()

    def _recalculate_matches(self, *_args) -> bool:
        self._update_escape_preview()
        query = self.find_input.text()
        self.matches = ()
        self.current_match_index = -1
        self._result_truncated = False
        self._scope_fallback = False
        if not query:
            self._update_status()
            return False
        try:
            result = find_matches(
                self.editor.toPlainText(),
                query,
                self._options(),
                file_path=self.file_path,
            )
        except FindValidationError as error:
            self.lbl_status.setText(
                tr("editor.find_error").format(error=error)
            )
            self._update_buttons()
            return False
        self.matches = result.matches
        self._result_truncated = result.truncated
        self._scope_fallback = result.scope_fallback
        self._update_status()
        return bool(self.matches)

    def _update_buttons(self) -> None:
        enabled = bool(self.matches)
        self.btn_find_previous.setEnabled(enabled)
        self.btn_find_next.setEnabled(enabled)
        if self.replace_enabled:
            replacement_enabled = enabled and not self.chk_inverted.isChecked()
            self.btn_replace.setEnabled(replacement_enabled)
            self.btn_replace_all.setEnabled(replacement_enabled)

    def _sync_current_match_to_cursor(self) -> None:
        """Report the nearest match without moving or selecting editor text."""
        if not self.matches:
            self.current_match_index = -1
            self._update_status()
            return

        cursor = self.editor.textCursor()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()
        exact_selection = next(
            (
                index
                for index, match in enumerate(self.matches)
                if match.start == selection_start and match.end == selection_end
            ),
            None,
        )
        if exact_selection is not None and cursor.hasSelection():
            self.current_match_index = exact_selection
        else:
            position = cursor.position()

            def distance(match) -> int:
                if position < match.start:
                    return match.start - position
                if position > match.end:
                    return position - match.end
                return 0

            self.current_match_index = min(
                range(len(self.matches)),
                key=lambda index: (distance(self.matches[index]), index),
            )
        self._update_status()

    def _remember_current_values(self) -> None:
        query = self.find_input.text()
        if self.replace_enabled:
            replacement = self.replace_input.text()
        else:
            replacement = next(
                (
                    prior_replacement
                    for prior_query, prior_replacement in self.history.entries
                    if prior_query == query
                ),
                "",
            )
        self.history.remember(
            query,
            replacement,
        )
        self._history_index = 0
        self._update_history_button()

    def _update_history_button(self) -> None:
        has_selection = bool(self._selection_query)
        self.btn_previous_value.setVisible(not has_selection)
        next_index = self._history_index + 1
        self.btn_previous_value.setEnabled(
            not has_selection and next_index < len(self.history.entries)
        )

    def _restore_previous_value(self) -> bool:
        if self._selection_query:
            return False
        next_index = self._history_index + 1
        if next_index >= len(self.history.entries):
            self._update_history_button()
            return False
        self._history_index = next_index
        query, replacement = self.history.entries[next_index]
        self.find_input.setText(query)
        if self.replace_enabled:
            self.replace_input.setText(replacement)
        self._sync_current_match_to_cursor()
        self._update_history_button()
        return True

    def _clear_find_state(self) -> None:
        self.history.clear()
        self._history_index = 0
        self.find_input.clear()
        self.replace_input.clear()
        self.matches = ()
        self.current_match_index = -1
        self._result_truncated = False
        self._scope_fallback = False
        self._update_status()
        self._update_history_button()

    def _update_status(self) -> None:
        if not self.find_input.text():
            status = ""
        elif not self.matches:
            status = tr("editor.find_no_matches")
        elif self.current_match_index >= 0:
            status = tr("editor.find_position").format(
                current=self.current_match_index + 1,
                total=len(self.matches),
            )
        elif self._result_truncated:
            status = tr("editor.find_match_count_limited").format(
                count=len(self.matches)
            )
        else:
            status = tr("editor.find_match_count").format(count=len(self.matches))
        if self._scope_fallback and self.find_input.text():
            suffix = tr("editor.find_scope_fallback")
            status = f"{status} {suffix}".strip()
        if (
            self.replace_enabled
            and self.chk_inverted.isChecked()
            and self.find_input.text()
        ):
            suffix = tr("editor.find_inverted_replace_disabled")
            status = f"{status} {suffix}".strip()
        self.lbl_status.setText(status)
        self._update_buttons()

    def _select_current_match(self) -> bool:
        if not self.matches or self.current_match_index < 0:
            return False
        match = self.matches[self.current_match_index]
        cursor = self.editor.textCursor()
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self._update_status()
        return True

    def _find_next(self) -> bool:
        self._remember_current_values()
        if not self.matches and not self._recalculate_matches():
            return False
        if self.current_match_index < 0:
            position = self.editor.textCursor().selectionEnd()
            self.current_match_index = next(
                (
                    index
                    for index, match in enumerate(self.matches)
                    if match.start >= position
                ),
                0,
            )
        else:
            self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        return self._select_current_match()

    def _find_previous(self) -> bool:
        self._remember_current_values()
        if not self.matches and not self._recalculate_matches():
            return False
        if self.current_match_index < 0:
            position = self.editor.textCursor().selectionStart()
            candidates = [
                index
                for index, match in enumerate(self.matches)
                if match.end <= position
            ]
            self.current_match_index = candidates[-1] if candidates else len(self.matches) - 1
        else:
            self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        return self._select_current_match()

    def _replace_current(self):
        self._remember_current_values()
        if self.chk_inverted.isChecked():
            self._update_status()
            return
        if not self.find_input.text() or not self.matches:
            return
        if self.current_match_index < 0 and not self._find_next():
            return
        match = self.matches[self.current_match_index]
        text = self.editor.toPlainText()
        try:
            replacement = replacement_for_match(
                text[match.start:match.end],
                self.find_input.text(),
                self.replace_input.text(),
                self._options(),
            )
        except FindValidationError as error:
            self.lbl_status.setText(tr("editor.find_error").format(error=error))
            return
        cursor = self.editor.textCursor()
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.KeepAnchor)
        self._mutating = True
        cursor.insertText(replacement)
        self._mutating = False
        self._recalculate_matches()
        if self.matches:
            self.current_match_index = next(
                (
                    index
                    for index, candidate in enumerate(self.matches)
                    if candidate.start >= match.start + len(replacement)
                ),
                0,
            )
            self._select_current_match()
        else:
            self.lbl_status.setText(tr("editor.replace_one_complete"))

    def _replace_all(self):
        self._remember_current_values()
        if self.chk_inverted.isChecked():
            self._update_status()
            return
        if not self.find_input.text() or not self.matches:
            return
        text = self.editor.toPlainText()
        count = len(self.matches)
        try:
            for match in reversed(self.matches):
                replacement = replacement_for_match(
                    text[match.start:match.end],
                    self.find_input.text(),
                    self.replace_input.text(),
                    self._options(),
                )
                text = text[:match.start] + replacement + text[match.end:]
        except FindValidationError as error:
            self.lbl_status.setText(tr("editor.find_error").format(error=error))
            return
        cursor = self.editor.textCursor()
        self._mutating = True
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.insertText(text)
        cursor.endEditBlock()
        self._mutating = False
        self._recalculate_matches()
        self.lbl_status.setText(tr("editor.replace_all_complete").format(count=count))

    def eventFilter(self, watched, event):  # pylint: disable=invalid-name
        """Route query-field Enter keys through exactly one navigation path."""
        if (
            watched is self.find_input
            and event.type() == QEvent.Type.KeyPress
            and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
        ):
            navigation_modifiers = event.modifiers() & (
                Qt.KeyboardModifier.ShiftModifier
                | Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.AltModifier
                | Qt.KeyboardModifier.MetaModifier
            )
            if navigation_modifiers not in (
                Qt.KeyboardModifier.NoModifier,
                Qt.KeyboardModifier.ShiftModifier,
            ):
                return False
            if not event.isAutoRepeat():
                if navigation_modifiers == Qt.KeyboardModifier.ShiftModifier:
                    self._find_previous()
                else:
                    self._find_next()
            event.accept()
            return True
        return super().eventFilter(watched, event)

    def closeEvent(self, event):  # pylint: disable=invalid-name
        self._remember_current_values()
        if self._close_requested is not None and not self._shutting_down:
            event.ignore()
            self._close_requested()
            return
        self._disconnect_editor_signals()
        if self._translation_connected:
            try:
                get_translator().languageChanged.disconnect(
                    self._retranslate_ui
                )
            except (RuntimeError, TypeError):
                pass
            self._translation_connected = False
        super().closeEvent(event)

    def shutdown(self) -> None:
        """Release session callbacks before the owning Editor is destroyed."""
        if self._shutting_down:
            return
        self._shutting_down = True
        self._close_requested = None
        self._presentation_toggle_requested = None
        self.close()


class _LineNumberArea(QWidget):
    """Gutter widget painted beside a QTextEdit viewport."""

    def __init__(self, controller):
        super().__init__(controller.editor)
        self.controller = controller
        self.setObjectName("editor_line_number_area")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def sizeHint(self):
        return QSize(self.controller.width(), 0)

    def paintEvent(self, event):
        self.controller.paint(event)


class _LineNumberController(QObject):
    """Adds a lightweight line-number gutter to a QTextEdit."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.area = _LineNumberArea(self)
        self.enabled = False

        self.editor.installEventFilter(self)
        self.editor.verticalScrollBar().valueChanged.connect(lambda _value: self.update())
        self.editor.textChanged.connect(self.update)
        self.editor.document().blockCountChanged.connect(lambda _count: self.update())
        self.area.hide()

    def width(self) -> int:
        digits = len(str(max(1, self.editor.document().blockCount())))
        return 12 + self.editor.fontMetrics().horizontalAdvance("9") * digits

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        self.area.setVisible(enabled)
        self.editor.setViewportMargins(self.width() if enabled else 0, 0, 0, 0)
        self.update()

    def update(self):
        if not self.enabled:
            return
        self.editor.setViewportMargins(self.width(), 0, 0, 0)
        viewport_rect = self.editor.viewport().geometry()
        self.area.setGeometry(0, viewport_rect.y(), self.width(), viewport_rect.height())
        self.area.update()

    def eventFilter(self, watched, event):
        if watched is self.editor and event.type() in (QEvent.Resize, QEvent.Show):
            self.update()
        return False

    def paint(self, event):
        painter = QPainter(self.area)
        background_color, text_color = self._theme_colors()
        painter.fillRect(event.rect(), background_color)
        painter.setPen(text_color)
        painter.setFont(self.editor.font())

        block = self.editor.document().firstBlock()
        font_height = self.editor.fontMetrics().height()

        while block.isValid():
            cursor = QTextCursor(block)
            rect = self.editor.cursorRect(cursor)
            y = rect.top()

            if y > self.editor.viewport().height():
                break
            if y + rect.height() >= 0:
                painter.drawText(
                    0,
                    y,
                    self.width() - 4,
                    max(rect.height(), font_height),
                    Qt.AlignRight,
                    str(block.blockNumber() + 1),
                )

            block = block.next()

    def _theme_colors(self) -> tuple[QColor, QColor]:
        """Return gutter colors that match the editor's current light/dark palette."""
        base_color = self.editor.palette().color(self.editor.backgroundRole())
        if base_color.lightness() < 128:
            return QColor("#252526"), QColor("#858585")
        return QColor("#f4f4f4"), QColor("#6b7280")


class _ExplorerFolderLabel(QLabel):
    """Keep the character cap separate from the available sidebar width."""

    def set_folder_name(self, name):
        self._caption = name if len(name) <= 24 else name[:21] + "..."
        self._refresh_caption()

    def _refresh_caption(self):
        caption = getattr(self, "_caption", "")
        if self.isVisible():
            caption = self.fontMetrics().elidedText(caption, Qt.ElideRight, self.contentsRect().width())
        self.setText(caption)

    def resizeEvent(self, event):  # pylint: disable=invalid-name
        super().resizeEvent(event)
        self._refresh_caption()

    def showEvent(self, event):  # pylint: disable=invalid-name
        super().showEvent(event)
        self._refresh_caption()


class _EditorStatusIndicator(QLabel):
    """Fixed-width accessible status text that elides without shifting layout."""

    def __init__(self, object_name: str, width: int, parent=None):
        super().__init__(parent)
        self._full_text = ""
        self.setObjectName(object_name)
        self.setFixedWidth(width)
        self.setMargin(4)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

    def set_value(self, text: str) -> None:
        """Publish complete accessible text and an elided visible caption."""
        self._full_text = str(text)
        self.setAccessibleName(self._full_text)
        self.setToolTip(self._full_text)
        self._refresh_text()

    def _refresh_text(self) -> None:
        available = max(1, self.contentsRect().width())
        visible = self.fontMetrics().elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            available,
        )
        super().setText(visible)

    def resizeEvent(self, event):  # pylint: disable=invalid-name
        super().resizeEvent(event)
        self._refresh_text()


class _TemporaryNotesDialog(QDialog):
    """Searchable, keyboard-navigable actions for bounded temporary notes."""

    def __init__(self, notes, parent=None):
        super().__init__(parent)
        self.requested_action = ""
        self.selected_note_id = ""
        self.setWindowTitle(tr("editor.temp_notes_title"))
        self.setMinimumSize(560, 380)

        layout = QVBoxLayout(self)
        self.search_box = QLineEdit(self)
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setPlaceholderText(tr("editor.temp_notes_search"))
        self.search_box.setAccessibleName(tr("editor.temp_notes_search"))
        layout.addWidget(self.search_box)

        self.note_list = QListWidget(self)
        self.note_list.setSortingEnabled(True)
        self.note_list.setAccessibleName(tr("editor.temp_notes_title"))
        for note in notes:
            item = QListWidgetItem(
                f"{note.title} - {note.updated_at[:19]} - {note.note_id[:8]}"
            )
            item.setData(Qt.ItemDataRole.UserRole, note.note_id)
            self.note_list.addItem(item)
        layout.addWidget(self.note_list, 1)

        buttons = QHBoxLayout()
        self.restore_button = QPushButton(tr("editor.temp_note_restore"), self)
        self.rename_button = QPushButton(tr("editor.explorer_rename"), self)
        self.export_button = QPushButton(tr("editor.btn_export"), self)
        self.delete_button = QPushButton(tr("editor.temp_note_delete"), self)
        self.close_button = QPushButton(tr("app.btn_close"), self)
        for button in (
            self.restore_button,
            self.rename_button,
            self.export_button,
            self.delete_button,
        ):
            buttons.addWidget(button)
        buttons.addStretch()
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

        self.search_box.textChanged.connect(self._filter_notes)
        self.note_list.itemSelectionChanged.connect(self._update_actions)
        self.note_list.itemDoubleClicked.connect(
            lambda _item: self._choose("restore")
        )
        self.restore_button.clicked.connect(lambda: self._choose("restore"))
        self.rename_button.clicked.connect(lambda: self._choose("rename"))
        self.export_button.clicked.connect(lambda: self._choose("export"))
        self.delete_button.clicked.connect(lambda: self._choose("delete"))
        self.close_button.clicked.connect(self.reject)
        if self.note_list.count():
            self.note_list.setCurrentRow(0)
        self._update_actions()

    def _filter_notes(self, text: str) -> None:
        needle = text.strip().casefold()
        for index in range(self.note_list.count()):
            item = self.note_list.item(index)
            item.setHidden(bool(needle and needle not in item.text().casefold()))
        current = self.note_list.currentItem()
        if current is None or current.isHidden():
            self.note_list.clearSelection()
            for index in range(self.note_list.count()):
                item = self.note_list.item(index)
                if not item.isHidden():
                    self.note_list.setCurrentItem(item)
                    break
        self._update_actions()

    def _update_actions(self) -> None:
        current = self.note_list.currentItem()
        enabled = current is not None and not current.isHidden()
        for button in (
            self.restore_button,
            self.rename_button,
            self.export_button,
            self.delete_button,
        ):
            button.setEnabled(enabled)

    def _choose(self, action: str) -> None:
        item = self.note_list.currentItem()
        if item is None or item.isHidden():
            return
        self.requested_action = action
        self.selected_note_id = str(item.data(Qt.ItemDataRole.UserRole) or "")
        if self.selected_note_id:
            self.accept()


class EditorDock(BaseDock):
    """
    Dock widget for integrated file editor.

    Features:
    - Tabbed interface for multiple files
    - Syntax highlighting for common file types
    - File actions through a local File menu bar
    - Edit-only mode for sandbox editing
    - Context menu for mode switching
    - Keyboard shortcuts (Ctrl+Shift+E for edit-only)
    - Find/Replace (basic)
    - Recent files list
    """

    TEMP_NOTE_AUTOSAVE_INTERVAL_MS = 500

    _LANGUAGE_BY_SUFFIX = {
        ".bash": "Shell Script",
        ".c": "C",
        ".cc": "C++",
        ".cfg": "INI",
        ".cpp": "C++",
        ".css": "CSS",
        ".cxx": "C++",
        ".go": "Go",
        ".h": "C Header",
        ".hpp": "C++ Header",
        ".htm": "HTML",
        ".html": "HTML",
        ".ini": "INI",
        ".ipynb": "Jupyter Notebook",
        ".java": "Java",
        ".js": "JavaScript",
        ".json": "JSON",
        ".jsx": "React JSX",
        ".kt": "Kotlin",
        ".less": "Less",
        ".lua": "Lua",
        ".md": "Markdown",
        ".php": "PHP",
        ".py": "Python",
        ".r": "R",
        ".rb": "Ruby",
        ".rs": "Rust",
        ".sass": "Sass",
        ".scss": "SCSS",
        ".sh": "Shell Script",
        ".sql": "SQL",
        ".toml": "TOML",
        ".toon": "TOON",
        ".ts": "TypeScript",
        ".tsx": "React TSX",
        ".xml": "XML",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".zsh": "Zsh",
    }
    _LANGUAGE_BY_FILE_TYPE = {
        "bash": "Shell Script",
        "htm": "HTML",
        "html": "HTML",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "json": "JSON",
        "jsx": "React JSX",
        "py": "Python",
        "python": "Python",
        "ts": "TypeScript",
        "tsx": "React TSX",
        "typescript": "TypeScript",
    }

    _ACTION_SPECS = {
        "new": {"text_key": "editor.btn_new", "shortcut_action": "new_file"},
        "open": {"text_key": "editor.btn_open", "shortcut_action": "open_file"},
        "open_path": {"text_key": "editor.btn_open_path", "shortcut_action": "editor.file.open_path"},
        "open_folder": {"text_key": "editor.btn_open_folder", "shortcut_action": "editor.file.open_folder"},
        "close_folder": {"text_key": "editor.btn_close_folder", "shortcut_action": "editor.file.close_folder"},
        "restore_folder_sessions": {
            "text_key": "editor.chk_restore_folder_sessions",
            "checkable": True,
            "shortcut_action": "editor.file.restore_folder_sessions",
        },
        "clear_folder_sessions": {"text_key": "editor.btn_clear_folder_sessions", "shortcut_action": "editor.file.clear_folder_sessions"},
        "recover_unsaved": {"text_key": "editor.btn_recover_unsaved", "shortcut_action": "editor.file.recover_unsaved"},
        "recovery_retention": {"text_key": "editor.btn_recovery_retention", "shortcut_action": "editor.file.recovery_retention"},
        "save_temp_note": {"text_key": "editor.btn_save_temp_note", "shortcut_action": "editor.file.save_temp_note"},
        "manage_temp_notes": {"text_key": "editor.btn_manage_temp_notes", "shortcut_action": "editor.file.manage_temp_notes"},
        "temp_note_retention": {"text_key": "editor.btn_temp_note_retention", "shortcut_action": "editor.file.temp_note_retention"},
        "save": {"text_key": "editor.btn_save", "shortcut_action": "save_file"},
        "save_as": {"text_key": "editor.btn_save_as", "shortcut_action": "save_as"},
        "compare_with_saved": {"text_key": "editor.btn_compare_with_saved", "shortcut_action": "editor.file.compare_with_saved"},
        "reload_from_disk": {"text_key": "editor.btn_reload_from_disk", "shortcut_action": "editor.file.reload_from_disk"},
        "enable_saving": {"text_key": "editor.btn_enable_saving", "shortcut_action": "editor.file.enable_saving"},
        "export": {"text_key": "editor.btn_export", "shortcut_action": "editor.file.export"},
        "close_tab": {"text_key": "editor.btn_close_tab", "shortcut_action": "close_tab"},
        "auto_save": {"text_key": "editor.chk_auto_save", "checkable": True, "shortcut_action": "editor.file.auto_save"},
        "undo": {"text_key": "editor.btn_undo", "shortcut_action": "undo"},
        "redo": {
            "text_key": "editor.btn_redo",
            "shortcut_action": "redo",
            "shortcut_context": Qt.ShortcutContext.WidgetWithChildrenShortcut,
        },
        "cut": {"text_key": "editor.btn_cut", "shortcut_action": "cut"},
        "copy": {"text_key": "editor.btn_copy", "shortcut_action": "copy"},
        "paste": {"text_key": "editor.btn_paste", "shortcut_action": "paste"},
        "delete": {"text_key": "editor.btn_delete", "shortcut_action": "editor.edit.delete"},
        "select_all": {"text_key": "editor.btn_select_all", "shortcut_action": "select_all"},
        "select_line": {"text_key": "editor.btn_select_line", "shortcut_action": "editor.edit.select_line"},
        "find": {"text_key": "editor.btn_find", "shortcut_action": "find"},
        "find_replace": {"text_key": "editor.btn_find_replace", "shortcut_action": "replace"},
        "go_to_line": {"text_key": "editor.btn_go_to_line", "shortcut_action": "editor.edit.go_to_line"},
        "duplicate_line": {"text_key": "editor.btn_duplicate_line", "shortcut_action": "editor.edit.duplicate_line"},
        "toggle_line_comment": {"text_key": "editor.btn_toggle_line_comment", "shortcut_action": "editor.edit.toggle_line_comment"},
        "indent": {"text_key": "editor.btn_indent", "shortcut_action": "editor.edit.indent"},
        "outdent": {"text_key": "editor.btn_outdent", "shortcut_action": "editor.edit.outdent"},
        "indent_use_tabs": {"text_key": "editor.chk_indent_use_tabs", "checkable": True, "shortcut_action": "editor.edit.indent_use_tabs"},
        "indent_width": {"text_key": "editor.btn_indent_width", "shortcut_action": "editor.edit.indent_width"},
        "move_line_up": {"text_key": "editor.btn_move_line_up", "shortcut_action": "editor.edit.move_line_up"},
        "move_line_down": {"text_key": "editor.btn_move_line_down", "shortcut_action": "editor.edit.move_line_down"},
        "insert_datetime": {"text_key": "editor.btn_insert_datetime", "shortcut_action": "editor.edit.insert_datetime"},
        "trim_trailing_spaces": {"text_key": "editor.btn_trim_trailing_spaces", "shortcut_action": "editor.edit.trim_trailing_spaces"},
        "word_wrap": {"text_key": "editor.chk_word_wrap", "checkable": True, "shortcut_action": "editor.view.word_wrap"},
        "render_whitespace": {"text_key": "editor.chk_render_whitespace", "checkable": True, "shortcut_action": "editor.view.render_whitespace"},
        "show_line_numbers": {"text_key": "editor.chk_show_line_numbers", "checkable": True, "shortcut_action": "editor.view.show_line_numbers"},
        "show_explorer": {"text_key": "editor.chk_show_explorer", "checkable": True, "shortcut_action": "editor.view.show_explorer"},
        "small_text": {"text_key": "editor.btn_small_text", "shortcut_action": "zoom_out"},
        "large_text": {"text_key": "editor.btn_large_text", "shortcut_action": "zoom_in"},
        "normal_size": {"text_key": "editor.btn_normal_size", "shortcut_action": "reset_zoom"},
        "previous_file_tab": {
            "text_key": "editor.btn_previous_file_tab",
            "shortcut_action": "previous_file_tab",
        },
        "next_file_tab": {
            "text_key": "editor.btn_next_file_tab",
            "shortcut_action": "next_file_tab",
        },
        "json_format_2": {"text_key": "editor.btn_json_format_2"},
        "json_format_4": {"text_key": "editor.btn_json_format_4"},
        "json_minify": {"text_key": "editor.btn_json_minify"},
        "json_validate": {"text_key": "editor.btn_json_validate"},
        "json_validate_schema": {"text_key": "editor.btn_json_validate_schema"},
        "json_generate_schema": {"text_key": "editor.btn_json_generate_schema"},
        "json_set_active_schema": {"text_key": "editor.btn_json_set_active_schema"},
        "json_clear_active_schema": {"text_key": "editor.btn_json_clear_active_schema"},
        "json_insert_missing_required": {"text_key": "editor.btn_json_insert_missing_required"},
        "json_search": {"text_key": "editor.btn_json_search"},
        "json_collapse_tree": {"text_key": "editor.btn_json_collapse_tree"},
        "json_expand_tree": {"text_key": "editor.btn_json_expand_tree"},
    }

    _MENU_SPECS = {
        "file": {
            "attr": "menu_file",
            "title_key": "editor.menu_file",
            "items": (
                "new", "open", "open_path", "open_folder", "close_folder",
                "recover_unsaved",
                "recovery_retention", None, "save_temp_note",
                "manage_temp_notes", "temp_note_retention", None,
                "save", "save_as", "compare_with_saved",
                "reload_from_disk", "enable_saving", "export", "close_tab",
                None, "auto_save", "restore_folder_sessions",
                "clear_folder_sessions",
            ),
        },
        "edit": {
            "attr": "menu_edit",
            "title_key": "editor.menu_edit",
            "items": (
                "undo", "redo", None, "cut", "copy", "paste", "delete",
                "select_all", "select_line", None, "find", "find_replace",
                "go_to_line",
                None, "duplicate_line", "toggle_line_comment", "indent",
                "outdent", "indent_use_tabs", "indent_width",
                "move_line_up", "move_line_down",
                "insert_datetime", "trim_trailing_spaces",
            ),
        },
        "view": {
            "attr": "menu_view",
            "title_key": "editor.menu_view",
            "items": (
                "show_explorer", None,
                "previous_file_tab", "next_file_tab", None,
                "word_wrap", "render_whitespace", "show_line_numbers",
                None, "small_text", "large_text", "normal_size",
            ),
        },
        "json": {
            "attr": "menu_json",
            "title_key": "editor.menu_json",
            "items": (
                "json_format_2", "json_format_4", "json_minify",
                None, "json_validate", "json_validate_schema", "json_generate_schema",
                None, "json_set_active_schema", "json_clear_active_schema",
                "json_insert_missing_required",
                None, "json_search",
                None, "json_collapse_tree", "json_expand_tree",
            ),
        },
    }

    _ACTION_ENABLE_RULES = {
        "save": "has_tab",
        "save_as": "has_tab",
        "save_temp_note": "has_editor",
        "compare_with_saved": "has_file_path",
        "reload_from_disk": "can_reload_from_disk",
        "enable_saving": "is_edit_only",
        "close_tab": "has_tab",
        "export": "has_editor",
        "undo": "has_editor",
        "redo": "has_editor",
        "cut": "has_editor",
        "copy": "has_editor",
        "paste": "has_editor",
        "delete": "has_editor",
        "select_all": "has_editor",
        "select_line": "has_editor",
        "find": "has_editor",
        "find_replace": "has_editor",
        "go_to_line": "has_editor",
        "duplicate_line": "has_editor",
        "toggle_line_comment": "has_editor",
        "indent": "has_editor",
        "outdent": "has_editor",
        "move_line_up": "has_editor",
        "move_line_down": "has_editor",
        "insert_datetime": "has_editor",
        "trim_trailing_spaces": "has_editor",
        "small_text": "has_editor",
        "large_text": "has_editor",
        "normal_size": "has_editor",
        "previous_file_tab": "has_tab",
        "next_file_tab": "has_tab",
        "json_format_2": "is_json_tab",
        "json_format_4": "is_json_tab",
        "json_minify": "is_json_tab",
        "json_validate": "is_json_tab",
        "json_validate_schema": "is_json_tab",
        "json_generate_schema": "is_json_tab",
        "json_set_active_schema": "is_json_tab",
        "json_clear_active_schema": "has_active_schema",
        "json_insert_missing_required": "has_active_schema",
        "json_search": "is_json_tab",
        "json_collapse_tree": "is_json_tab",
        "json_expand_tree": "is_json_tab",
    }

    _ACTION_CHECKED_ATTRIBUTES = {
        "auto_save": "auto_save_enabled",
        "word_wrap": "word_wrap_enabled",
        "render_whitespace": "render_whitespace_enabled",
        "show_line_numbers": "show_line_numbers_enabled",
        "show_explorer": "show_explorer_enabled",
        "indent_use_tabs": "indent_use_tabs",
        "restore_folder_sessions": "folder_sessions_enabled",
    }

    _QUICK_TOOLBAR_ITEMS = (
        "new", "open", "save", None,
        "undo", "redo", None,
        "cut", "copy", "paste", None,
        "find", "find_replace",
    )
    _QUICK_TOOLBAR_ICONS = {
        "new": ("document-new", QStyle.StandardPixmap.SP_FileIcon),
        "open": ("document-open", QStyle.StandardPixmap.SP_DialogOpenButton),
        "save": ("document-save", QStyle.StandardPixmap.SP_DialogSaveButton),
        "undo": ("edit-undo", QStyle.StandardPixmap.SP_ArrowBack),
        "redo": ("edit-redo", QStyle.StandardPixmap.SP_ArrowForward),
        "cut": ("edit-cut", QStyle.StandardPixmap.SP_DialogCancelButton),
        "copy": ("edit-copy", QStyle.StandardPixmap.SP_FileIcon),
        "paste": ("edit-paste", QStyle.StandardPixmap.SP_DialogApplyButton),
        "find": ("edit-find", QStyle.StandardPixmap.SP_FileDialogContentsView),
        "find_replace": ("edit-find-replace", QStyle.StandardPixmap.SP_BrowserReload),
    }

    MAX_EXTERNAL_FILE_WATCHES = 128
    MAX_EXTERNAL_DIR_WATCHES = 128
    MAX_TYPED_PATH_CHARS = 4096
    MAX_TYPED_FILE_BYTES = 16 * 1024 * 1024
    MAX_FOLDER_SESSIONS = 20
    MAX_FOLDER_SESSION_FILES = 20
    MAX_FOLDER_SESSIONS_BYTES = 256 * 1024
    MAX_FIND_HISTORY_BUFFERS = 20
    MAX_FIND_HISTORY_ENTRIES = 5
    handles_unsaved_tab_close = True

    def __init__(self, parent=None):
        # Initialize attributes BEFORE super().__init__() which calls _setup_ui()
        self.recent_files: List[str] = []
        self.recent_folders: List[str] = []
        self.max_recent = 10
        self.normal_text_font_size = 10
        self.min_text_font_size = 6
        self.max_text_font_size = 48
        self._last_active_editor = None

        # Load auto-save preference from QSettings
        from PySide6.QtCore import QSettings
        self.settings = QSettings("Clarify", "EditorDock")
        self.recent_files = self._load_recent_paths("recent_files")
        self.recent_folders = self._load_recent_paths("recent_folders")
        find_scope = self.settings.value("find/scope", "all", type=str)
        inverted_unit = self.settings.value(
            "find/inverted_unit", "line", type=str
        )
        self.find_state = {
            "case_sensitive": self.settings.value(
                "find/case_sensitive", False, type=bool
            ),
            "whole_word": self.settings.value("find/whole_word", False, type=bool),
            "regex": self.settings.value("find/regex", False, type=bool),
            "scope": (
                find_scope
                if find_scope in {"all", "strings", "variables", "comments"}
                else "all"
            ),
            "inverted": self.settings.value("find/inverted", False, type=bool),
            "inverted_unit": (
                inverted_unit
                if inverted_unit in {"line", "token", "interval"}
                else "line"
            ),
        }
        self._persisted_tab_order = self._load_persisted_tab_order()
        self._restoring_tab_order = False
        self.folder_sessions_enabled = self.settings.value(
            "folder_sessions_enabled", True, type=bool
        )
        self._folder_sessions = self._load_folder_sessions()
        self._folder_session_ready = False
        self._restoring_folder_session = False
        self.auto_save_enabled = self.settings.value("auto_save_enabled", False, type=bool)
        self.show_line_numbers_enabled = self.settings.value("show_line_numbers_enabled", False, type=bool)
        self.word_wrap_enabled = self.settings.value("word_wrap_enabled", True, type=bool)
        self.render_whitespace_enabled = self.settings.value("render_whitespace_enabled", False, type=bool)
        self.indent_use_tabs = self.settings.value("indent_use_tabs", False, type=bool)
        self.indent_width = max(
            1, min(8, self.settings.value("indent_width", 4, type=int))
        )
        self.show_explorer_enabled = self.settings.value(
            "show_explorer_enabled", True, type=bool
        )
        self.explorer_root_path = self.settings.value(
            "explorer_root_path", str(Path.home()), type=str
        )
        self.recovery_retention_hours = max(
            1,
            min(
                30 * 24,
                self.settings.value(
                    "recovery_retention_hours",
                    DEFAULT_RETENTION_HOURS,
                    type=int,
                ),
            ),
        )
        self.recovery_store = UnsavedRecoveryStore(
            retention_hours=self.recovery_retention_hours
        )
        self.temp_note_retention_days = max(
            0,
            min(
                3650,
                self.settings.value("temp_note_retention_days", 0, type=int),
            ),
        )
        self.temp_note_store = TemporaryNoteStore()
        self._temp_note_startup_failure = False
        if self.temp_note_retention_days:
            try:
                self.temp_note_store.prune(self.temp_note_retention_days)
            except (OSError, TemporaryNoteError):
                self._temp_note_startup_failure = True
        self._restored_recovery_ids: set[str] = set()
        self._recovery_suspended = False
        self._recovery_failures = 0
        self._recovery_offer_dismissed = False
        self._last_recovery_prune_report = RecoveryPruneReport()
        self._recovery_already_open_count = 0
        self._last_reference_update = None
        self._find_history_by_buffer: dict[str, _EditorFindHistory] = {}
        self._find_dialog = None
        find_presentation_mode = self.settings.value(
            "find/presentation_mode", "docked", type=str
        )
        self._find_presentation_mode = (
            find_presentation_mode
            if find_presentation_mode in {"docked", "floating"}
            else "docked"
        )

        # NOW call super().__init__() which triggers _setup_ui()
        super().__init__(EDITOR_NAME, parent)
        self._recovery_lifecycle = EditorRecoveryLifecycle(self)
        self._folder_session_ready = True
        self._restore_folder_session(self.explorer_root_path)
        self._refresh_recovery_offer()
        if self._temp_note_startup_failure:
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))

    def _setup_ui(self):
        """Setup UI components."""
        menu_row = QHBoxLayout()

        self.menu_bar = QMenuBar()
        self.menu_bar.setObjectName("editor_menu_bar")
        self.menu_bar.setNativeMenuBar(False)
        self.menu_bar.setStyleSheet("""
            QMenuBar#editor_menu_bar {
                background-color: transparent;
                border: none;
            }
            QMenuBar#editor_menu_bar::item {
                padding: 6px 16px;
                background-color: transparent;
                color: palette(window-text);
            }
            QMenuBar#editor_menu_bar::item:selected,
            QMenuBar#editor_menu_bar::item:pressed {
                background-color: palette(button);
                border-radius: 3px;
            }
        """)
        self._action_by_id = {}
        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_view_menu()
        self._setup_json_menu()
        self._setup_quick_toolbar()
        self._refresh_editor_menus()
        self._setup_external_file_watcher()

        menu_row.addWidget(self.menu_bar)
        menu_row.addStretch()

        self.layout.addLayout(menu_row)
        self.layout.addWidget(self.quick_toolbar)
        self._setup_recovery_offer()
        self.layout.addWidget(self.recovery_offer)

        # Tab widget for multiple files
        self.editor_splitter = QSplitter(Qt.Horizontal)
        self.editor_splitter.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._setup_explorer_panel()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.editor_workspace_splitter = QSplitter(Qt.Horizontal)
        self.editor_workspace_splitter.addWidget(self.tab_widget)
        self._setup_split_panel()
        self.editor_splitter.addWidget(self.explorer_panel)
        self.editor_splitter.addWidget(self.editor_workspace_splitter)
        self.editor_splitter.setStretchFactor(0, 0)
        self.editor_splitter.setStretchFactor(1, 1)
        self.editor_splitter.setSizes([240, 760])
        self.explorer_panel.setVisible(self.show_explorer_enabled)
        self.layout.addWidget(self.editor_splitter, 1)

        self._find_panel_host = QFrame(self.main_widget)
        self._find_panel_host.setObjectName("editor_find_panel_host")
        self._find_panel_host.setFrameShape(QFrame.Shape.StyledPanel)
        self._find_panel_layout = QVBoxLayout(self._find_panel_host)
        self._find_panel_layout.setContentsMargins(0, 0, 0, 0)
        self._find_panel_host.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._find_panel_host.hide()
        self.layout.addWidget(self._find_panel_host)

        # Status bar
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel(tr("editor.lbl_status_ready"))
        self.lbl_status.setStyleSheet("color: #6A9955;")
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        self.status_indent_label = _EditorStatusIndicator(
            "editor_status_indent", 116, self.main_widget
        )
        self.status_cursor_label = _EditorStatusIndicator(
            "editor_status_cursor", 124, self.main_widget
        )
        self.status_language_label = _EditorStatusIndicator(
            "editor_status_language", 152, self.main_widget
        )
        status_layout.addWidget(self.status_indent_label)
        status_layout.addWidget(self.status_cursor_label)
        status_layout.addWidget(self.status_language_label)
        self.layout.addLayout(status_layout)

        self._status_translation_connected = True
        get_translator().languageChanged.connect(self._retranslate_editor_ui)
        self._update_editor_status_indicators()

        self._recovery_timer = QTimer(self)
        self._recovery_timer.setSingleShot(True)
        self._recovery_timer.setInterval(1500)
        self._recovery_timer.timeout.connect(self._on_recovery_timeout)
        try:
            self.recovery_store.prune()
        except (OSError, RecoverySnapshotError):
            self.lbl_status.setText(tr("editor.status_recovery_skipped").format(count=1))

        # Apply tooltips
        self._apply_tooltips()

    def _apply_tooltips(self):
        """Apply internationalized tooltips to all widgets."""
        self.menu_bar.setToolTip(tooltip_tr("editor.menu_bar"))

        for menu_spec in self._MENU_SPECS.values():
            menu = getattr(self, menu_spec["attr"])
            menu.menuAction().setToolTip(tooltip_tr(menu_spec["title_key"]))

        for action_id, action in self._action_by_id.items():
            action.setToolTip(tooltip_tr(self._ACTION_SPECS[action_id]["text_key"]))

        self._refresh_quick_toolbar_accessibility()

        self.menu_recent_files.menuAction().setToolTip(
            tooltip_tr("editor.menu_recent_files")
        )
        self.menu_recent_folders.menuAction().setToolTip(
            tooltip_tr("editor.menu_recent_folders")
        )

        # Tab Widget
        self.tab_widget.setToolTip(tooltip_tr("editor.tab_widget"))

        # Status Label
        self.lbl_status.setToolTip(tooltip_tr("editor.lbl_status"))

    def _setup_quick_toolbar(self) -> None:
        """Expose frequent commands through their existing shared actions."""
        self.quick_toolbar = QToolBar(self.main_widget)
        self.quick_toolbar.setObjectName("editor_quick_toolbar")
        self.quick_toolbar.setMovable(False)
        self.quick_toolbar.setFloatable(False)
        self.quick_toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.quick_toolbar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.quick_toolbar.setIconSize(QSize(20, 20))
        self.quick_toolbar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.quick_toolbar.setStyleSheet(
            "QToolBar#editor_quick_toolbar { border: none; padding: 2px; }"
        )

        for action_id in self._QUICK_TOOLBAR_ITEMS:
            if action_id is None:
                self.quick_toolbar.addSeparator()
                continue
            action = self._action_by_id[action_id]
            theme_name, fallback = self._QUICK_TOOLBAR_ICONS[action_id]
            fallback_icon = self.style().standardIcon(fallback)
            action.setIcon(QIcon.fromTheme(theme_name, fallback_icon))
            self.quick_toolbar.addAction(action)

    def _setup_recovery_offer(self) -> None:
        """Create a non-modal startup decision bar for pending snapshots."""
        self.recovery_offer = QFrame(self.main_widget)
        self.recovery_offer.setObjectName("editor_recovery_offer")
        self.recovery_offer.setFrameShape(QFrame.Shape.StyledPanel)
        self.recovery_offer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        offer_layout = QHBoxLayout(self.recovery_offer)
        offer_layout.setContentsMargins(8, 4, 8, 4)
        self.lbl_recovery_offer = QLabel(self.recovery_offer)
        self.lbl_recovery_offer.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_recovery_offer.setWordWrap(True)
        offer_layout.addWidget(self.lbl_recovery_offer, 1)
        self.btn_recovery_offer_recover = QPushButton(self.recovery_offer)
        self.btn_recovery_offer_discard = QPushButton(self.recovery_offer)
        self.btn_recovery_offer_cancel = QPushButton(self.recovery_offer)
        offer_layout.addWidget(self.btn_recovery_offer_recover)
        offer_layout.addWidget(self.btn_recovery_offer_discard)
        offer_layout.addWidget(self.btn_recovery_offer_cancel)
        self.recovery_offer.setProperty("pending_count", 0)
        self.recovery_offer.hide()
        self._retranslate_recovery_offer()

    def _refresh_quick_toolbar_accessibility(self) -> None:
        """Keep full translated names available while button text stays hidden."""
        self.quick_toolbar.setAccessibleName(tr("editor.quick_toolbar"))
        self.quick_toolbar.setToolTip(tooltip_tr("editor.quick_toolbar"))
        for action_id in self._QUICK_TOOLBAR_ITEMS:
            if action_id is None:
                continue
            action = self._action_by_id[action_id]
            button = self.quick_toolbar.widgetForAction(action)
            if button is None:
                continue
            button.setAccessibleName(action.text())
            button.setAccessibleDescription(action.toolTip())

    def _retranslate_recovery_offer(self) -> None:
        """Refresh the recovery bar without reading persistent storage."""
        count = int(self.recovery_offer.property("pending_count") or 0)
        self.lbl_recovery_offer.setText(
            tr("editor.recovery_dialog_message").format(count=count)
        )
        controls = (
            (self.btn_recovery_offer_recover, "editor.btn_recover_all"),
            (self.btn_recovery_offer_discard, "editor.btn_discard_all"),
            (self.btn_recovery_offer_cancel, "editor.btn_cancel"),
        )
        for button, key in controls:
            text = tr(key)
            button.setText(text)
            button.setAccessibleName(text)
        self.recovery_offer.setAccessibleName(
            tr("editor.recovery_dialog_title")
        )

    def _setup_explorer_panel(self) -> None:
        """Create a lazy filesystem navigation tree for the editor sidebar."""
        self.explorer_panel = QFrame()
        self.explorer_panel.setMinimumWidth(180)
        self.explorer_panel.setMaximumWidth(480)
        self.explorer_panel.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        explorer_layout = QVBoxLayout(self.explorer_panel)
        explorer_layout.setContentsMargins(0, 0, 4, 0)
        header = QHBoxLayout()
        header.setSpacing(8)
        self.explorer_title_label = QLabel(tr("editor.lbl_explorer"))
        self.explorer_title_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )
        self.explorer_folder_label = _ExplorerFolderLabel()
        self.explorer_folder_label.setTextFormat(Qt.TextFormat.PlainText)
        self.explorer_folder_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        header.addWidget(self.explorer_title_label)
        header.addWidget(self.explorer_folder_label, 1)
        explorer_layout.addLayout(header)

        self.explorer_model = QFileSystemModel(self.explorer_panel)
        self.explorer_model.setFilter(
            QDir.AllDirs | QDir.Files | QDir.Hidden | QDir.NoDotAndDotDot
        )
        self.explorer_model.directoryLoaded.connect(self._sync_explorer_root_index)
        self.explorer_tree = QTreeView(self.explorer_panel)
        self.explorer_tree.setModel(self.explorer_model)
        self.explorer_tree.setHeaderHidden(True)
        for column in range(1, self.explorer_model.columnCount()):
            self.explorer_tree.hideColumn(column)
        self.explorer_tree.doubleClicked.connect(self._open_explorer_index)
        self.explorer_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.explorer_tree.customContextMenuRequested.connect(
            self._show_explorer_context_menu
        )
        self.explorer_tree.setToolTip(tooltip_tr("editor.explorer_tree"))
        explorer_layout.addWidget(self.explorer_tree)
        self._set_explorer_root(self.explorer_root_path, persist=False)

    def _setup_split_panel(self) -> None:
        """Create a hidden secondary view that never owns a document."""
        self.split_panel = QFrame(self.editor_workspace_splitter)
        split_layout = QVBoxLayout(self.split_panel)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_header = QHBoxLayout()
        self.split_title = QLabel("")
        self.split_close_button = QPushButton("×")
        self.split_close_button.setFixedSize(28, 28)
        self.split_close_button.setToolTip(tr("editor.split_close"))
        self.split_close_button.clicked.connect(self._close_split_view)
        split_header.addWidget(self.split_title, 1)
        split_header.addWidget(self.split_close_button)
        split_layout.addLayout(split_header)
        self._split_source_tab = None
        self.split_editor = QTextEdit(self.split_panel)
        self.split_editor.setAcceptRichText(False)
        self.split_editor.installEventFilter(self)
        self.split_editor.cursorPositionChanged.connect(
            self._update_editor_status_indicators
        )
        self._apply_indentation_to_editor(self.split_editor)
        split_layout.addWidget(self.split_editor, 1)
        self.editor_workspace_splitter.addWidget(self.split_panel)
        self.split_panel.hide()

    def _set_explorer_root(
        self,
        folder_path: str,
        *,
        persist: bool = True,
        restore_session: bool = True,
        save_previous: bool = True,
    ) -> bool:
        """Set a validated folder as the lazy explorer root."""
        normalized = self._normalized_file_path(folder_path)
        if not normalized or not os.path.isdir(normalized):
            normalized = str(Path.home())
        previous = self._normalized_file_path(
            getattr(self, "explorer_root_path", "")
        )
        changing_root = bool(previous and previous != normalized)
        switching_session = (
            changing_root
            and self._folder_session_ready
            and self.folder_sessions_enabled
        )
        if switching_session:
            if not self._checkpoint_unsaved_tabs():
                self.lbl_status.setText(tr("editor.status_folder_session_failed"))
                return False
            if save_previous and not self._save_folder_session(previous):
                self.lbl_status.setText(tr("editor.status_folder_session_failed"))
                return False
            self._detach_folder_tabs(previous)
        root_index = self.explorer_model.setRootPath(normalized)
        self.explorer_tree.setRootIndex(root_index)
        self.explorer_root_path = normalized
        folder_name = Path(normalized).name or normalized
        self.explorer_folder_label.set_folder_name(folder_name)
        self.explorer_folder_label.setToolTip(normalized)
        if persist:
            self.settings.setValue("explorer_root_path", normalized)
        if (
            changing_root
            and restore_session
            and self._folder_session_ready
            and self.folder_sessions_enabled
        ):
            self._restore_folder_session(normalized)
        return os.path.isdir(normalized)

    def _open_explorer_folder(self) -> None:
        """Choose the navigation root without invoking a recursive search."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            tr("editor.dialog_open_folder_title"),
            self.explorer_root_path,
        )
        if folder_path:
            if self._set_explorer_root(folder_path):
                self._add_recent_folder(folder_path)
                self._set_explorer_visible(True)

    def _close_explorer_folder(self) -> bool:
        """Checkpoint and detach the current Explorer root without losing buffers."""
        current = self._normalized_file_path(self.explorer_root_path)
        home = self._normalized_file_path(str(Path.home()))
        if not current or current == home:
            return False
        if not self._set_explorer_root(home, restore_session=False):
            self.lbl_status.setText(tr("editor.status_folder_closed_recovery_failed"))
            return False
        self.lbl_status.setText(tr("editor.status_folder_closed"))
        return True

    def _sync_explorer_root_index(self, _loaded_path: str) -> None:
        """Keep the selected root bound across loads without changing visibility."""
        root_index = self.explorer_model.index(self.explorer_root_path)
        if root_index.isValid() and root_index != self.explorer_tree.rootIndex():
            self.explorer_tree.setRootIndex(root_index)

    def _open_explorer_index(self, index) -> None:
        """Open files from the sidebar through the editor's existing API."""
        if not index.isValid() or self.explorer_model.isDir(index):
            return
        file_path = self.explorer_model.filePath(index)
        if os.path.isfile(file_path):
            self.open_file_path(file_path)

    def _show_explorer_context_menu(self, pos) -> None:
        index = self.explorer_tree.indexAt(pos)
        if not index.isValid():
            return
        self._build_explorer_context_menu(index).exec(
            self.explorer_tree.viewport().mapToGlobal(pos)
        )

    def _build_explorer_context_menu(self, index) -> QMenu:
        """Build actions appropriate to the selected file-system item."""
        menu = QMenu(self)
        menu.setToolTipsVisible(True)
        path = self._normalized_file_path(self.explorer_model.filePath(index))
        is_directory = self.explorer_model.isDir(index)
        is_root = path == self._normalized_file_path(self.explorer_root_path)
        absolute_path, relative_path, unavailable_key = self._safe_path_copy_values(
            path
        )

        def add(action_id: str, text_key: str, callback, enabled: bool = True):
            action = menu.addAction(tr(text_key))
            action.setData(action_id)
            action.setEnabled(enabled)
            action.triggered.connect(lambda _checked=False: callback())
            return action

        add("open", "editor.explorer_open", lambda: self.open_file_path(path), not is_directory)
        add(
            "open_side",
            "editor.explorer_open_side",
            lambda: self._open_explorer_to_side(path),
            not is_directory,
        )
        menu.addSeparator()
        add(
            "new_file",
            "editor.explorer_new_file",
            lambda: self._prompt_create_explorer_item(path, folder=False),
            is_directory,
        )
        add(
            "new_folder",
            "editor.explorer_new_folder",
            lambda: self._prompt_create_explorer_item(path, folder=True),
            is_directory,
        )
        add(
            "rename",
            "editor.explorer_rename",
            lambda: self._rename_explorer_path(path),
            not is_root,
        )
        add(
            "undo_reference_update",
            "editor.explorer_undo_reference_update",
            self._undo_last_reference_update,
            self._last_reference_update is not None,
        )
        add(
            "delete",
            "editor.explorer_delete",
            lambda: self._delete_explorer_path(path),
            not is_root,
        )
        menu.addSeparator()
        add("reveal", "editor.explorer_reveal", lambda: self._reveal_explorer_path(path))
        absolute_action = add(
            "copy_absolute",
            "editor.explorer_copy_absolute",
            lambda: self._copy_safe_path(path, relative=False),
            absolute_path is not None,
        )
        relative_action = add(
            "copy_relative",
            "editor.explorer_copy_relative",
            lambda: self._copy_safe_path(path, relative=True),
            relative_path is not None,
        )
        if unavailable_key:
            reason = tr(unavailable_key)
            self._set_action_unavailable_reason(absolute_action, reason)
            self._set_action_unavailable_reason(relative_action, reason)
        menu.addSeparator()
        analysis_available = self._analysis_host() is not None
        analyze_action = add(
            "analyze",
            "editor.explorer_analyze",
            lambda: self._analyze_explorer_path(path),
            analysis_available,
        )
        if not analysis_available:
            analyze_action.setToolTip(tr("editor.explorer_analyze_unavailable"))
        return menu

    def _open_explorer_to_side(self, path: str) -> bool:
        if not self.open_file_path(path):
            return False
        return self._show_split_view(self.tab_widget.currentWidget(), Qt.Horizontal)

    def _relative_explorer_path(self, path: str) -> str | None:
        """Return a path relative to the canonical root without escaping it."""
        _absolute, relative, _reason = self._safe_path_copy_values(path)
        return relative

    def _safe_path_copy_values(
        self, path: str | None
    ) -> tuple[str | None, str | None, str | None]:
        """Resolve bounded copy values inside the canonical Explorer root."""
        normalized = self._normalized_file_path(path)
        if not normalized or not os.path.exists(normalized):
            return None, None, "editor.path_copy_unavailable_missing"
        try:
            lexical_root = self._normalized_file_path(self.explorer_root_path)
            canonical_root = os.path.realpath(lexical_root)
            canonical_target = os.path.realpath(normalized)
            if os.path.commonpath([canonical_root, canonical_target]) != canonical_root:
                reason = (
                    "editor.path_copy_unavailable_symlink"
                    if os.path.commonpath([lexical_root, normalized]) == lexical_root
                    else "editor.path_copy_unavailable_external"
                )
                return None, None, reason
            return normalized, os.path.relpath(canonical_target, canonical_root), None
        except (OSError, ValueError):
            return None, None, "editor.path_copy_unavailable_external"

    def _tab_path_copy_values(
        self, tab
    ) -> tuple[str | None, str | None, str | None]:
        """Resolve copy values only for a normal file-backed editor tab."""
        if tab is None:
            return None, None, "editor.path_copy_unavailable_untitled"
        if getattr(tab, "_clarify_temp_note_id", ""):
            return None, None, "editor.path_copy_unavailable_temp_note"
        file_path = getattr(tab, "file_path", None)
        if not file_path:
            return None, None, "editor.path_copy_unavailable_untitled"
        return self._safe_path_copy_values(file_path)

    @staticmethod
    def _set_action_unavailable_reason(action: QAction, reason: str) -> None:
        """Expose why a disabled path action cannot run."""
        action.setToolTip(reason)
        action.setStatusTip(reason)
        action.setWhatsThis(reason)

    def _copy_safe_path(self, path: str, *, relative: bool) -> bool:
        """Revalidate an Explorer path immediately before publishing it."""
        absolute_path, relative_path, reason_key = self._safe_path_copy_values(path)
        value = relative_path if relative else absolute_path
        if value is None:
            if reason_key:
                self.lbl_status.setText(tr(reason_key))
            return False
        return self._copy_path(value)

    def _copy_tab_path(self, tab, *, relative: bool) -> bool:
        """Revalidate a clicked tab identity immediately before copying it."""
        absolute_path, relative_path, reason_key = self._tab_path_copy_values(tab)
        value = relative_path if relative else absolute_path
        if value is None:
            if reason_key:
                self.lbl_status.setText(tr(reason_key))
            return False
        return self._copy_path(value)

    @staticmethod
    def _validate_explorer_name(name: str) -> str:
        candidate = name.strip()
        if (
            not candidate
            or candidate in {".", ".."}
            or len(candidate) > 255
            or "\x00" in candidate
            or "/" in candidate
            or "\\" in candidate
        ):
            raise ValueError(tr("editor.explorer_invalid_name"))
        return candidate

    def _prompt_create_explorer_item(self, directory: str, *, folder: bool) -> bool:
        key = "editor.explorer_new_folder" if folder else "editor.explorer_new_file"
        name, accepted = QInputDialog.getText(self, tr(key), tr("editor.explorer_name_prompt"))
        if not accepted:
            return False
        try:
            created = self._create_explorer_item(directory, name, folder=folder)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, tr("editor.msg_error_title"), str(error))
            return False
        if not folder:
            self.open_file_path(created)
        return True

    def _create_explorer_item(self, directory: str, name: str, *, folder: bool) -> str:
        """Create one empty item exclusively inside a selected directory."""
        parent = self._normalized_file_path(directory)
        if not os.path.isdir(parent) or os.path.islink(parent):
            raise ValueError(tr("editor.explorer_directory_required"))
        candidate = self._validate_explorer_name(name)
        path = os.path.join(parent, candidate)
        if os.path.lexists(path):
            raise FileExistsError(tr("editor.explorer_name_exists").format(name=candidate))
        if folder:
            os.mkdir(path, mode=0o700)
        else:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(descriptor)
        return path

    def _rename_explorer_path(self, path: str, new_name: str | None = None) -> bool:
        """Rename locally without overwriting and update open-tab identities."""
        old_path = self._normalized_file_path(path)
        if old_path == self._normalized_file_path(self.explorer_root_path):
            return False
        if not os.path.lexists(old_path):
            return False
        if new_name is None:
            new_name, accepted = QInputDialog.getText(
                self,
                tr("editor.explorer_rename"),
                tr("editor.explorer_name_prompt"),
                text=os.path.basename(old_path),
            )
            if not accepted:
                return False
        try:
            candidate = self._validate_explorer_name(new_name)
            new_path = os.path.join(os.path.dirname(old_path), candidate)
            if os.path.lexists(new_path):
                raise FileExistsError(
                    tr("editor.explorer_name_exists").format(name=candidate)
                )
            was_directory = os.path.isdir(old_path) and not os.path.islink(old_path)
            os.rename(old_path, new_path)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, tr("editor.msg_error_title"), str(error))
            return False
        self._remap_open_tab_paths(old_path, new_path, include_children=was_directory)
        self._persist_tab_order()
        self._save_folder_session(self.explorer_root_path)
        self._checkpoint_unsaved_tabs()
        self._handle_reference_updates_after_rename(
            old_path, new_path, is_directory=was_directory
        )
        return True

    def _modified_open_paths(self) -> set[str]:
        """Return file paths whose in-memory contents must never be overwritten."""
        modified = set()
        for tab in self._all_tab_objects():
            file_path = self._normalized_file_path(getattr(tab, "file_path", None))
            if not file_path:
                continue
            document_modified = bool(
                hasattr(tab, "editor") and tab.editor.document().isModified()
            )
            if getattr(tab, "is_modified", False) or document_modified:
                modified.add(file_path)
        return modified

    def _confirm_reference_update_plan(self, plan) -> bool:
        """Show a bounded preview and require explicit confirmation before writes."""
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Question)
        dialog.setWindowTitle(tr("editor.reference_update_preview_title"))
        dialog.setText(
            tr("editor.reference_update_preview_message").format(
                changes=plan.change_count,
                files=len(plan.updates),
            )
        )
        dialog.setDetailedText(plan.preview())
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        return dialog.exec() == QMessageBox.Yes

    def _report_reference_update_plan(self, plan, *, applied: bool) -> None:
        """Report unsupported, ambiguous or skipped references without hiding them."""
        if applied:
            self.lbl_status.setText(
                tr("editor.status_reference_updates_applied").format(
                    changes=plan.change_count,
                    files=len(plan.updates),
                )
            )
        elif plan.change_count:
            self.lbl_status.setText(tr("editor.status_reference_updates_declined"))
        else:
            self.lbl_status.setText(tr("editor.status_reference_updates_none"))
        if not plan.issues:
            return
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Information)
        dialog.setWindowTitle(tr("editor.reference_update_issues_title"))
        dialog.setText(
            tr("editor.reference_update_issues_message").format(
                count=len(plan.issues)
            )
        )
        dialog.setDetailedText("\n".join(plan.issues))
        dialog.exec()

    def _handle_reference_updates_after_rename(
        self, old_path: str, new_path: str, *, is_directory: bool
    ) -> None:
        """Analyze one completed rename and apply only its confirmed safe plan."""
        try:
            plan = analyze_rename_references(
                self.explorer_root_path,
                old_path,
                new_path,
                is_directory=is_directory,
                excluded_paths=self._modified_open_paths(),
            )
        except ReferenceUpdateError as error:
            QMessageBox.warning(
                self,
                tr("editor.reference_update_error_title"),
                tr("editor.reference_update_analysis_failed").format(error=error),
            )
            return
        if not plan.updates:
            self._report_reference_update_plan(plan, applied=False)
            return
        if not self._confirm_reference_update_plan(plan):
            self._report_reference_update_plan(plan, applied=False)
            return
        try:
            self._last_reference_update = apply_reference_updates(plan)
        except ReferenceUpdateError as error:
            QMessageBox.warning(
                self,
                tr("editor.reference_update_error_title"),
                tr("editor.reference_update_apply_failed").format(error=error),
            )
            return
        self._refresh_tabs_after_reference_update(self._last_reference_update.paths)
        self._report_reference_update_plan(plan, applied=True)

    def _refresh_tabs_after_reference_update(self, paths) -> None:
        """Reload only clean affected tabs and refresh their watcher baselines."""
        affected = {self._normalized_file_path(path) for path in paths}
        for tab in self._all_tab_objects():
            tab_path = self._normalized_file_path(getattr(tab, "file_path", None))
            if tab_path not in affected:
                continue
            if getattr(tab, "is_modified", False) or tab.editor.document().isModified():
                continue
            cursor_position = tab.editor.textCursor().position()
            if not tab.load_file(tab_path):
                self._check_tab_external_state(tab)
                continue
            cursor = tab.editor.textCursor()
            cursor.setPosition(min(cursor_position, tab.editor.document().characterCount() - 1))
            tab.editor.setTextCursor(cursor)
            self._track_tab_disk_state(tab)
            self._update_tab_title(tab)

    def _undo_last_reference_update(self) -> bool:
        """Undo the latest rename reference transaction unless files changed later."""
        transaction = self._last_reference_update
        if transaction is None:
            return False
        reply = QMessageBox.question(
            self,
            tr("editor.reference_update_undo_title"),
            tr("editor.reference_update_undo_message").format(
                files=len(transaction.files)
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return False
        try:
            transaction.rollback()
        except ReferenceUpdateError as error:
            QMessageBox.warning(
                self,
                tr("editor.reference_update_error_title"),
                tr("editor.reference_update_undo_failed").format(error=error),
            )
            return False
        self._refresh_tabs_after_reference_update(transaction.paths)
        self._last_reference_update = None
        self.lbl_status.setText(tr("editor.status_reference_updates_undone"))
        return True

    def _remap_open_tab_paths(
        self, old_path: str, new_path: str, *, include_children: bool
    ) -> None:
        for tab in self._all_tab_objects():
            tab_path = self._normalized_file_path(getattr(tab, "file_path", None))
            if not tab_path:
                continue
            replacement = None
            if tab_path == old_path:
                replacement = new_path
            elif include_children:
                try:
                    if os.path.commonpath([old_path, tab_path]) == old_path:
                        replacement = os.path.join(
                            new_path, os.path.relpath(tab_path, old_path)
                        )
                except ValueError:
                    pass
            if replacement is None:
                continue
            tab.file_path = replacement
            self._track_tab_disk_state(tab)
            self._update_tab_title(tab)

    def _delete_explorer_path(self, path: str) -> bool:
        """Move one item to the platform trash after explicit confirmation."""
        normalized = self._normalized_file_path(path)
        if (
            normalized == self._normalized_file_path(self.explorer_root_path)
            or not os.path.lexists(normalized)
        ):
            return False
        reply = QMessageBox.question(
            self,
            tr("editor.explorer_delete_title"),
            tr("editor.explorer_delete_confirm").format(name=os.path.basename(normalized)),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return False
        result = QFile.moveToTrash(normalized)
        success = result[0] if isinstance(result, tuple) else bool(result)
        if not success:
            QMessageBox.warning(
                self,
                tr("editor.msg_error_title"),
                tr("editor.explorer_trash_failed"),
            )
            return False
        for tab in self._all_tab_objects():
            self._check_tab_external_state(tab)
            self._update_tab_title(tab)
        return True

    @staticmethod
    def _copy_path(path: str) -> bool:
        app = QApplication.instance()
        if (
            not isinstance(path, str)
            or not path
            or app is None
            or QThread.currentThread() != app.thread()
        ):
            return False
        QApplication.clipboard().setText(path)
        return True

    @staticmethod
    def _reveal_explorer_path(path: str) -> bool:
        target = path if os.path.isdir(path) else os.path.dirname(path)
        return bool(QDesktopServices.openUrl(QUrl.fromLocalFile(target)))

    def _analysis_host(self):
        host = self.window()
        return host if callable(getattr(host, "_show_algorithm_analysis", None)) else None

    def _analyze_explorer_path(self, path: str) -> bool:
        """Run only the bounded local preflight; provider work remains explicit."""
        host = self._analysis_host()
        if host is None:
            return False
        host._show_algorithm_analysis()
        analysis = getattr(host, "dock_algorithm_analysis", None)
        if analysis is None:
            return False
        analysis.path_input.setText(path)
        analysis.run_preflight()
        return True

    def _set_explorer_visible(self, visible: bool) -> None:
        """Show or hide the editor explorer and persist the preference."""
        self.show_explorer_enabled = visible
        self.explorer_panel.setVisible(visible)
        self.settings.setValue("show_explorer_enabled", visible)
        self._refresh_editor_menus()

    def _connect_signals(self):
        """Connect widget signals."""
        handlers = self._action_signal_handlers()
        missing_handlers = set(self._action_by_id) - set(handlers)
        if missing_handlers:
            missing_text = ", ".join(sorted(missing_handlers))
            raise RuntimeError(f"Editor action(s) missing handler: {missing_text}")

        for action_id, handler in handlers.items():
            self._action_by_id[action_id].triggered.connect(handler)

        self.btn_recovery_offer_recover.clicked.connect(
            self._recover_pending_snapshots
        )
        self.btn_recovery_offer_discard.clicked.connect(
            self._discard_pending_snapshots
        )
        self.btn_recovery_offer_cancel.clicked.connect(
            self._dismiss_recovery_offer
        )

        self._file_watcher.fileChanged.connect(self._on_watched_file_changed)
        self._file_watcher.directoryChanged.connect(self._on_watched_directory_changed)

        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Context menu on tabs
        self.tab_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setContextMenuPolicy(Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._show_tab_context_menu)
        tab_bar.tabMoved.connect(self._on_tab_moved)

    def _setup_external_file_watcher(self) -> None:
        """Create bounded watchers for files currently open in editor tabs."""
        self._file_watcher = QFileSystemWatcher(self)
        self._watched_file_paths: set[str] = set()
        self._watched_dir_paths: set[str] = set()

    @staticmethod
    def _normalized_file_path(file_path: str | None) -> str:
        """Return a stable absolute path for comparison and watcher registration."""
        if not file_path:
            return ""
        return os.path.abspath(os.path.normpath(file_path))

    def _load_persisted_tab_order(self) -> list[str]:
        """Load a bounded file-backed tab order without opening any files."""
        raw_value = self.settings.value("tab_order", "", type=str)
        try:
            values = json.loads(raw_value) if raw_value else []
        except (TypeError, json.JSONDecodeError):
            return []
        if not isinstance(values, list):
            return []
        order = []
        for value in values:
            if not isinstance(value, str) or len(value) > self.MAX_TYPED_PATH_CHARS:
                continue
            normalized = self._normalized_file_path(value)
            if normalized and normalized not in order:
                order.append(normalized)
            if len(order) >= 20:
                break
        return order

    @staticmethod
    def _canonical_path(path: str | None) -> str:
        normalized = EditorDock._normalized_file_path(path)
        return os.path.realpath(normalized) if normalized else ""

    @classmethod
    def _path_is_inside_root(cls, path: str | None, root: str | None) -> bool:
        """Compare canonical paths without allowing a sibling-prefix escape."""
        canonical_path = cls._canonical_path(path)
        canonical_root = cls._canonical_path(root)
        if not canonical_path or not canonical_root:
            return False
        try:
            return os.path.commonpath([canonical_root, canonical_path]) == canonical_root
        except ValueError:
            return False

    def _load_folder_sessions(self) -> list[dict]:
        """Load bounded path-only folder sessions from Editor settings."""
        raw_value = self.settings.value("folder_sessions", "", type=str)
        if not raw_value or len(raw_value.encode("utf-8")) > self.MAX_FOLDER_SESSIONS_BYTES:
            return []
        try:
            values = json.loads(raw_value)
        except (TypeError, json.JSONDecodeError, UnicodeError):
            return []
        if not isinstance(values, list):
            return []

        sessions = []
        roots = set()
        for value in values:
            if not isinstance(value, dict):
                continue
            root = value.get("root", "")
            files = value.get("files", [])
            if (
                not isinstance(root, str)
                or len(root) > self.MAX_TYPED_PATH_CHARS
                or not isinstance(files, list)
            ):
                continue
            canonical_root = self._canonical_path(root)
            if not canonical_root or canonical_root in roots:
                continue
            bounded_files = []
            for path in files:
                if (
                    isinstance(path, str)
                    and len(path) <= self.MAX_TYPED_PATH_CHARS
                    and self._path_is_inside_root(path, canonical_root)
                ):
                    canonical_file = self._canonical_path(path)
                    if canonical_file not in bounded_files:
                        bounded_files.append(canonical_file)
                if len(bounded_files) >= self.MAX_FOLDER_SESSION_FILES:
                    break
            active = self._canonical_path(value.get("active", ""))
            split = value.get("split")
            if not isinstance(split, dict):
                split = None
            else:
                split_path = self._canonical_path(split.get("path", ""))
                orientation = split.get("orientation", "")
                if split_path not in bounded_files or orientation not in {
                    "horizontal",
                    "vertical",
                }:
                    split = None
                else:
                    split = {"path": split_path, "orientation": orientation}
            sessions.append(
                {
                    "root": canonical_root,
                    "files": bounded_files,
                    "active": active if active in bounded_files else "",
                    "split": split,
                    "updated_at": str(value.get("updated_at", ""))[:64],
                }
            )
            roots.add(canonical_root)
            if len(sessions) >= self.MAX_FOLDER_SESSIONS:
                break
        return sessions

    def _store_folder_sessions(self) -> bool:
        """Persist path references within one explicit total byte budget."""
        sessions = self._folder_sessions[: self.MAX_FOLDER_SESSIONS]
        while sessions:
            payload = json.dumps(sessions, ensure_ascii=False, separators=(",", ":"))
            if len(payload.encode("utf-8")) <= self.MAX_FOLDER_SESSIONS_BYTES:
                self._folder_sessions = sessions
                self.settings.setValue("folder_sessions", payload)
                return True
            sessions.pop()
        self._folder_sessions = []
        self.settings.setValue("folder_sessions", "[]")
        return not bool(sessions)

    def _tab_folder_identity(self, tab) -> str:
        """Return a file/session identity without treating recovery as a file."""
        return self._canonical_path(
            getattr(tab, "file_path", "")
            or getattr(tab, "_clarify_folder_source_path", "")
            or getattr(tab, "_clarify_recovery_source_path", "")
        )

    def _tab_folder_root(self, tab) -> str:
        """Return the canonical workspace owner assigned to one editor tab."""
        if tab is None:
            return ""
        if hasattr(tab, "_clarify_folder_root"):
            return self._canonical_path(getattr(tab, "_clarify_folder_root", ""))
        identity = self._tab_folder_identity(tab)
        current_root = self._canonical_path(self.explorer_root_path)
        if identity and self._path_is_inside_root(identity, current_root):
            setattr(tab, "_clarify_folder_root", current_root)
            return current_root
        return ""

    def _assign_tab_folder_root(self, tab, root: str | None = None) -> str:
        """Assign ownership only when a tab identity is inside the workspace."""
        canonical_root = self._canonical_path(root or self.explorer_root_path)
        identity = self._tab_folder_identity(tab)
        assigned = (
            canonical_root
            if identity and self._path_is_inside_root(identity, canonical_root)
            else ""
        )
        setattr(tab, "_clarify_folder_root", assigned)
        return assigned

    def _detach_folder_tabs(self, root: str) -> int:
        """Remove one workspace's tabs while retaining their recovery snapshots."""
        canonical_root = self._canonical_path(root)
        tabs = [
            tab
            for tab in self._all_tab_objects()
            if self._tab_folder_root(tab) == canonical_root
        ]
        if self._split_source_tab in tabs:
            self._close_split_view()
        for tab in reversed(tabs):
            snapshot_id = getattr(tab, "_clarify_recovery_id", "")
            if snapshot_id:
                self._restored_recovery_ids.discard(snapshot_id)
            self._discard_find_history(tab)
            self._clear_tab_disk_state(tab, refresh_watchers=False)
            for timer in tab.findChildren(QTimer):
                timer.stop()
            index = self.tab_widget.indexOf(tab)
            if index >= 0:
                self.tab_widget.removeTab(index)
            tab.deleteLater()
        self._renumber_untitled_tabs()
        self._last_active_editor = (
            getattr(self.tab_widget.currentWidget(), "editor", None)
            if self.tab_widget.count()
            else None
        )
        self._refresh_external_file_watchers()
        self._refresh_editor_menus()
        self._persist_tab_order()
        return len(tabs)

    def _save_folder_session(self, root: str | None = None) -> bool:
        """Save bounded references, active identity and shared split layout."""
        if (
            not self.folder_sessions_enabled
            or self._restoring_folder_session
            or not self._folder_session_ready
        ):
            return False
        canonical_root = self._canonical_path(root or self.explorer_root_path)
        if not canonical_root:
            return False

        files = []
        for tab in self._all_tab_objects():
            path = self._tab_folder_identity(tab)
            if path and self._tab_folder_root(tab) == canonical_root:
                if path not in files:
                    files.append(path)
            if len(files) >= self.MAX_FOLDER_SESSION_FILES:
                break

        active = self._tab_folder_identity(self.tab_widget.currentWidget())
        if active not in files:
            active = ""
        split = None
        split_path = self._tab_folder_identity(self._split_source_tab)
        if split_path in files and not self.split_panel.isHidden():
            split = {
                "path": split_path,
                "orientation": (
                    "vertical"
                    if self.editor_workspace_splitter.orientation() == Qt.Vertical
                    else "horizontal"
                ),
            }
        session = {
            "root": canonical_root,
            "files": files,
            "active": active,
            "split": split,
            "updated_at": datetime.now().astimezone().isoformat(),
        }
        self._folder_sessions = [
            item for item in self._folder_sessions if item.get("root") != canonical_root
        ]
        self._folder_sessions.insert(0, session)
        del self._folder_sessions[self.MAX_FOLDER_SESSIONS :]
        return self._store_folder_sessions()

    def _session_for_root(self, root: str) -> dict | None:
        canonical_root = self._canonical_path(root)
        return next(
            (
                session
                for session in self._folder_sessions
                if session.get("root") == canonical_root
            ),
            None,
        )

    def _recovery_snapshots_by_source(self) -> dict[str, object] | None:
        """Index snapshots by source, preferring a dirty buffer over a reference."""
        try:
            snapshots = self.recovery_store.list()
        except (OSError, RecoverySnapshotError):
            self.lbl_status.setText(
                tr("editor.status_recovery_skipped").format(count=1)
            )
            return None
        indexed = {}
        for snapshot in snapshots:
            source = self._canonical_path(snapshot.file_path)
            current = indexed.get(source)
            if source and (
                current is None
                or (snapshot.kind == "buffer" and current.kind != "buffer")
            ):
                indexed[source] = snapshot
        return indexed

    def _restore_folder_session(self, root: str) -> int:
        """Restore valid references, preferring recovery copies for dirty files."""
        if not self.folder_sessions_enabled or self._restoring_folder_session:
            return 0
        session = self._session_for_root(root)
        if not session:
            return 0
        canonical_root = self._canonical_path(root)
        recovery = self._recovery_snapshots_by_source()
        if recovery is None:
            return 0
        tabs_by_path = {
            self._tab_folder_identity(tab): tab for tab in self._all_tab_objects()
        }
        restored = 0
        skipped = 0
        self._restoring_folder_session = True
        try:
            for path in session["files"][: self.MAX_FOLDER_SESSION_FILES]:
                if not self._path_is_inside_root(path, canonical_root):
                    skipped += 1
                    continue
                tab = tabs_by_path.get(path)
                snapshot = recovery.get(path)
                if tab is None and snapshot is not None and snapshot.kind == "buffer":
                    if snapshot.snapshot_id in self._restored_recovery_ids:
                        skipped += 1
                        continue
                    tab = self._restore_recovery_snapshot(snapshot)
                    if tab is not None:
                        setattr(tab, "_clarify_folder_source_path", path)
                elif tab is None:
                    if (
                        not os.path.isfile(path)
                        or os.path.islink(path)
                        or not os.access(path, os.R_OK)
                    ):
                        skipped += 1
                        continue
                    if self.open_file_path(path):
                        tab = self.tab_widget.currentWidget()
                if tab is None:
                    skipped += 1
                    continue
                self._assign_tab_folder_root(tab, canonical_root)
                if (
                    snapshot is not None
                    and snapshot.kind == "reference"
                    and tuple(snapshot.source_signature or ())
                    == tuple(self.recovery_store.source_signature(path) or ())
                ):
                    setattr(tab, "_clarify_recovery_id", snapshot.snapshot_id)
                tabs_by_path[path] = tab
                restored += 1

            ordered_tabs = [
                tabs_by_path[path]
                for path in session["files"]
                if path in tabs_by_path
            ]
            target_indices = sorted(
                self.tab_widget.indexOf(tab)
                for tab in ordered_tabs
                if self.tab_widget.indexOf(tab) >= 0
            )
            for target_index, tab in zip(target_indices, ordered_tabs):
                current_index = self.tab_widget.indexOf(tab)
                if current_index >= 0 and current_index != target_index:
                    self.tab_widget.tabBar().moveTab(current_index, target_index)

            active_tab = tabs_by_path.get(session.get("active", ""))
            if active_tab is not None:
                self.tab_widget.setCurrentWidget(active_tab)
            split = session.get("split")
            split_tab = tabs_by_path.get(split.get("path", "")) if split else None
            if split_tab is not None:
                orientation = (
                    Qt.Vertical
                    if split.get("orientation") == "vertical"
                    else Qt.Horizontal
                )
                self._show_split_view(split_tab, orientation)
        finally:
            self._restoring_folder_session = False
        self._persist_tab_order()
        if skipped:
            self.lbl_status.setText(
                tr("editor.status_folder_session_partial").format(
                    restored=restored, skipped=skipped
                )
            )
        elif restored:
            self.lbl_status.setText(
                tr("editor.status_folder_session_restored").format(count=restored)
            )
        return restored

    def _set_folder_sessions_enabled(self, enabled: bool) -> None:
        self.folder_sessions_enabled = bool(enabled)
        self.settings.setValue(
            "folder_sessions_enabled", self.folder_sessions_enabled
        )
        if self.folder_sessions_enabled:
            self._save_folder_session()
        self._refresh_editor_menus()

    def _clear_folder_sessions(self, *, confirm: bool = True) -> bool:
        if confirm:
            reply = QMessageBox.question(
                self,
                tr("editor.clear_folder_sessions_title"),
                tr("editor.clear_folder_sessions_message"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False
        self._folder_sessions = []
        self.settings.setValue("folder_sessions", "[]")
        self.lbl_status.setText(tr("editor.status_folder_sessions_cleared"))
        return True

    def _persist_tab_order(self) -> None:
        """Persist only bounded path references, never document content."""
        if self._restoring_tab_order:
            return
        order = []
        for index in range(self.tab_widget.count()):
            path = self._normalized_file_path(
                getattr(self.tab_widget.widget(index), "file_path", None)
            )
            if path and path not in order:
                order.append(path)
            if len(order) >= 20:
                break
        self._persisted_tab_order = order
        self.settings.setValue("tab_order", json.dumps(order, ensure_ascii=False))

    def _apply_persisted_tab_order(self) -> None:
        """Reorder already-open tabs by stored identity without changing ownership."""
        if not self._persisted_tab_order or self.tab_widget.count() < 2:
            return
        rank = {path: index for index, path in enumerate(self._persisted_tab_order)}
        tabs = self._all_tab_objects()
        known = [
            tab
            for tab in tabs
            if self._normalized_file_path(getattr(tab, "file_path", None)) in rank
        ]
        known.sort(
            key=lambda tab: rank[
                self._normalized_file_path(getattr(tab, "file_path", None))
            ]
        )
        ordered = known + [tab for tab in tabs if tab not in known]
        current = self.tab_widget.currentWidget()
        self._restoring_tab_order = True
        try:
            for target_index, tab in enumerate(ordered):
                current_index = self.tab_widget.indexOf(tab)
                if current_index != target_index:
                    self.tab_widget.tabBar().moveTab(current_index, target_index)
            if current is not None:
                self.tab_widget.setCurrentWidget(current)
        finally:
            self._restoring_tab_order = False

    def _on_tab_moved(self, _from_index: int, _to_index: int) -> None:
        self._renumber_untitled_tabs()
        self._persist_tab_order()

    def _select_explorer_path(self, file_path: str | None) -> bool:
        """Reveal a current file only when it is inside the active Explorer root."""
        normalized = self._normalized_file_path(file_path)
        root = self._normalized_file_path(self.explorer_root_path)
        if not normalized or not os.path.exists(normalized):
            self.explorer_tree.clearSelection()
            self.explorer_tree.setCurrentIndex(QModelIndex())
            return False
        try:
            inside_root = os.path.commonpath(
                [os.path.realpath(root), os.path.realpath(normalized)]
            ) == os.path.realpath(root)
        except ValueError:
            inside_root = False
        if not inside_root:
            self.explorer_tree.clearSelection()
            self.explorer_tree.setCurrentIndex(QModelIndex())
            return False
        index = self.explorer_model.index(normalized)
        if not index.isValid():
            return False
        self.explorer_tree.setCurrentIndex(index)
        self.explorer_tree.scrollTo(index, QTreeView.PositionAtCenter)
        parent = index.parent()
        if parent.isValid():
            self.explorer_tree.expand(parent)
        return True

    @staticmethod
    def _file_disk_signature(file_path: str | None):
        """Return lightweight file identity/content-change metadata."""
        normalized_path = EditorDock._normalized_file_path(file_path)
        if not normalized_path:
            return None

        try:
            stat_result = os.stat(normalized_path)
        except OSError:
            return None

        return EditorDock._stat_disk_signature(stat_result)

    @staticmethod
    def _stat_disk_signature(stat_result):
        """Return comparable metadata for a path or open file descriptor."""
        return (
            stat_result.st_mtime_ns,
            stat_result.st_size,
            getattr(stat_result, 'st_ino', 0),
            getattr(stat_result, 'st_dev', 0),
            getattr(stat_result, 'st_ctime_ns', 0),
        )

    def _read_stable_reload_text(self, file_path: str) -> tuple[str, tuple[int, ...]]:
        """Read one bounded UTF-8 revision without accepting a concurrent replacement."""
        before_path = self._file_disk_signature(file_path)
        if before_path is None:
            raise _ExternalReloadError("missing")
        if before_path[1] > self.MAX_TYPED_FILE_BYTES:
            raise _ExternalReloadError("too_large")

        try:
            with open(file_path, "rb") as file_obj:
                before_fd = self._stat_disk_signature(os.fstat(file_obj.fileno()))
                payload = file_obj.read(self.MAX_TYPED_FILE_BYTES + 1)
                after_fd = self._stat_disk_signature(os.fstat(file_obj.fileno()))
        except OSError as error:
            raise _ExternalReloadError("read", str(error)) from error

        after_path = self._file_disk_signature(file_path)
        if len(payload) > self.MAX_TYPED_FILE_BYTES:
            raise _ExternalReloadError("too_large")
        if (
            before_path != before_fd
            or before_fd != after_fd
            or after_path != after_fd
        ):
            raise _ExternalReloadError("changed_again")
        try:
            return payload.decode("utf-8"), after_fd
        except UnicodeDecodeError as error:
            raise _ExternalReloadError("decode", str(error)) from error

    def _tab_tracked_file_path(self, tab) -> str:
        """Return the file-backed path currently tracked for a tab."""
        return getattr(tab, '_clarify_disk_path', '') or self._normalized_file_path(
            getattr(tab, 'file_path', None)
        )

    def _track_tab_disk_state(self, tab) -> None:
        """Refresh the saved-on-disk baseline for a file-backed tab."""
        if tab is None:
            return

        file_path = self._normalized_file_path(getattr(tab, 'file_path', None))
        if not file_path or getattr(tab, 'edit_only_mode', False):
            self._clear_tab_disk_state(tab, refresh_watchers=False)
            self._refresh_external_file_watchers()
            return

        signature = self._file_disk_signature(file_path)
        setattr(tab, '_clarify_disk_path', file_path)
        setattr(tab, '_clarify_disk_signature', signature)
        setattr(tab, '_clarify_recovery_source_signature',
                self.recovery_store.source_signature(file_path))
        self._set_tab_external_state(tab, "clean" if signature is not None else "missing")
        self._refresh_external_file_watchers()

    def _clear_tab_disk_state(self, tab, refresh_watchers: bool = True) -> None:
        """Remove Clarify Editor disk-tracking metadata from a tab."""
        if tab is None:
            return

        setattr(tab, '_clarify_disk_path', '')
        setattr(tab, '_clarify_disk_signature', None)
        setattr(tab, '_clarify_external_state', "clean")
        if hasattr(tab, '_clarify_auto_save_paused_for_external_change'):
            delattr(tab, '_clarify_auto_save_paused_for_external_change')

        if refresh_watchers:
            self._refresh_external_file_watchers()

    def _set_tab_external_state(self, tab, state: str) -> None:
        """Set external-change state and pause auto-save while user decision is needed."""
        previous_state = getattr(tab, '_clarify_external_state', "clean")
        setattr(tab, '_clarify_external_state', state)

        if state != "clean":
            self._pause_tab_auto_save_for_external_change(tab)
        elif (
            previous_state != "clean"
            and getattr(tab, '_clarify_auto_save_paused_for_external_change', False)
        ):
            if hasattr(tab, '_clarify_auto_save_paused_for_external_change'):
                delattr(tab, '_clarify_auto_save_paused_for_external_change')
            if self.auto_save_enabled:
                self._apply_auto_save_to_tab(tab)

    def _pause_tab_auto_save_for_external_change(self, tab) -> None:
        """Prevent auto-save from overwriting disk while an external change is unresolved."""
        if getattr(tab, '_clarify_auto_save_paused_for_external_change', False):
            return

        if hasattr(tab, 'set_auto_save'):
            tab.set_auto_save(False)
        elif hasattr(tab, 'auto_save_timer'):
            tab.auto_save_timer.stop()

        setattr(tab, '_clarify_auto_save_paused_for_external_change', True)

    def _refresh_external_file_watchers(self) -> None:
        """Watch open files and their parent folders without scanning folder trees."""
        if (self._recovery_suspended or not hasattr(self, '_file_watcher')
                or not hasattr(self, 'tab_widget')):
            return

        desired_files: set[str] = set()
        desired_dirs: set[str] = set()

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            if getattr(tab, 'edit_only_mode', False):
                continue

            file_path = self._tab_tracked_file_path(tab)
            if not file_path:
                continue

            parent_dir = os.path.dirname(file_path)
            if os.path.exists(file_path) and len(desired_files) < self.MAX_EXTERNAL_FILE_WATCHES:
                desired_files.add(file_path)
            if os.path.isdir(parent_dir) and len(desired_dirs) < self.MAX_EXTERNAL_DIR_WATCHES:
                desired_dirs.add(parent_dir)

        self._replace_watched_paths(self._watched_file_paths, desired_files)
        self._replace_watched_paths(self._watched_dir_paths, desired_dirs)

    def _replace_watched_paths(self, current_paths: set[str], desired_paths: set[str]) -> None:
        """Synchronize one QFileSystemWatcher path set with desired paths."""
        for old_path in sorted(current_paths - desired_paths):
            self._file_watcher.removePath(old_path)
            current_paths.discard(old_path)

        for new_path in sorted(desired_paths - current_paths):
            if self._file_watcher.addPath(new_path):
                current_paths.add(new_path)

    def _on_watched_file_changed(self, file_path: str) -> None:
        """Handle QFileSystemWatcher notifications for file content changes."""
        if self._recovery_suspended:
            return
        self._check_external_state_for_path(file_path)
        self._refresh_external_file_watchers()

    def _on_watched_directory_changed(self, directory_path: str) -> None:
        """Handle parent-folder notifications such as file removal or rename."""
        if self._recovery_suspended:
            return
        normalized_dir = self._normalized_file_path(directory_path)
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            file_path = self._tab_tracked_file_path(tab)
            if file_path and os.path.dirname(file_path) == normalized_dir:
                self._check_tab_external_state(tab)
                self._update_tab_title(tab)

        self._show_external_status_for_current_tab()
        self._refresh_editor_menus()
        self._refresh_external_file_watchers()

    def _check_external_state_for_path(self, file_path: str) -> bool:
        """Check all tabs backed by a given path for external changes."""
        normalized_path = self._normalized_file_path(file_path)
        affected = False

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            if self._tab_tracked_file_path(tab) != normalized_path:
                continue

            self._check_tab_external_state(tab)
            self._update_tab_title(tab)
            affected = True

        if affected:
            self._show_external_status_for_current_tab()
            self._refresh_editor_menus()

        return affected

    def _check_tab_external_state(self, tab) -> str:
        """Compare the current file state with the tab's last known disk baseline."""
        if tab is None or getattr(tab, 'edit_only_mode', False):
            return "clean"

        file_path = self._normalized_file_path(getattr(tab, 'file_path', None))
        if not file_path:
            self._clear_tab_disk_state(tab, refresh_watchers=False)
            return "clean"

        tracked_path = getattr(tab, '_clarify_disk_path', '')
        if tracked_path and tracked_path != file_path:
            self._track_tab_disk_state(tab)
            return getattr(tab, '_clarify_external_state', "clean")

        baseline_signature = getattr(tab, '_clarify_disk_signature', None)
        current_signature = self._file_disk_signature(file_path)

        if baseline_signature is None and current_signature is not None:
            setattr(tab, '_clarify_disk_path', file_path)
            setattr(tab, '_clarify_disk_signature', current_signature)
            self._set_tab_external_state(tab, "clean")
            return "clean"

        if current_signature is None:
            self._set_tab_external_state(tab, "missing")
            return "missing"

        if current_signature != baseline_signature:
            self._set_tab_external_state(tab, "modified")
            return "modified"

        self._set_tab_external_state(tab, "clean")
        return "clean"

    def _display_title_for_tab(self, tab) -> str:
        """Return the user-visible tab title with external-change badges."""
        title = tab.get_display_title()
        external_state = getattr(tab, '_clarify_external_state', "clean")
        if external_state == "modified":
            return f"{title} [external]"
        if external_state == "missing":
            return f"{title} [missing]"
        return title

    def _show_external_status_for_current_tab(self) -> bool:
        """Show the current tab's external-change state in the status bar."""
        tab = self.tab_widget.currentWidget()
        if tab is None:
            return False

        external_state = getattr(tab, '_clarify_external_state', "clean")
        if external_state == "clean":
            return False

        file_path = self._tab_tracked_file_path(tab)
        filename = os.path.basename(file_path) if file_path else tab.get_tab_title()

        if external_state == "modified":
            self.lbl_status.setStyleSheet("color: #DCDCAA; font-weight: bold;")
            message = tr("editor.external_reload.status_modified").format(
                file=filename
            )
            self.lbl_status.setText(message)
            self.lbl_status.setAccessibleDescription(message)
            return True

        self.lbl_status.setStyleSheet("color: #F44747; font-weight: bold;")
        message = tr("editor.external_reload.status_missing").format(
            file=filename
        )
        self.lbl_status.setText(message)
        self.lbl_status.setAccessibleDescription(message)
        return True

    def _save_decision_for_external_change(self, tab) -> str:
        """Ask whether Save should overwrite an unresolved external disk change."""
        external_state = self._check_tab_external_state(tab)
        if external_state == "clean":
            return "save"

        file_path = self._tab_tracked_file_path(tab)
        filename = os.path.basename(file_path) if file_path else tab.get_tab_title()
        message_key = (
            "editor.external_reload.changed"
            if external_state == "modified"
            else "editor.external_reload.missing"
        )

        dialog = QMessageBox(self)
        dialog.setWindowTitle(tr("editor.external_reload.title"))
        dialog.setText(tr(message_key).format(file=filename))
        dialog.setInformativeText(tr("editor.external_reload.save_prompt"))
        btn_keep = dialog.addButton(
            tr("editor.external_reload.keep_editor"), QMessageBox.AcceptRole
        )
        btn_save_as = dialog.addButton(tr("editor.btn_save_as"), QMessageBox.ActionRole)
        btn_cancel = dialog.addButton(tr("editor.btn_cancel"), QMessageBox.RejectRole)

        dialog.exec_()
        clicked = dialog.clickedButton()
        if clicked == btn_keep:
            return "save"
        if clicked == btn_save_as:
            return "save_as"
        if clicked == btn_cancel:
            return "cancel"
        return "cancel"

    def _apply_auto_save_to_tab(self, tab) -> None:
        """Apply current auto-save setting and connect status updates once."""
        if not hasattr(tab, 'set_auto_save'):
            return

        tab.set_auto_save(self.auto_save_enabled)
        if (
            self.auto_save_enabled
            and hasattr(tab, 'auto_saved')
            and not getattr(tab, '_editor_dock_auto_saved_connected', False)
        ):
            tab.auto_saved.connect(lambda t=tab: self._on_auto_saved(t))
            setattr(tab, '_editor_dock_auto_saved_connected', True)

    def _apply_line_numbers_to_tab(self, tab) -> None:
        """Apply current line-number visibility to a tab editor."""
        if not hasattr(tab, 'editor'):
            return

        controller = getattr(tab.editor, '_clarify_line_numbers', None)
        if controller is None:
            controller = _LineNumberController(tab.editor)
            setattr(tab.editor, '_clarify_line_numbers', controller)

        controller.set_enabled(self.show_line_numbers_enabled)

    def _apply_word_wrap_to_tab(self, tab) -> None:
        """Apply current word-wrap setting to a tab editor."""
        if not hasattr(tab, 'editor'):
            return

        wrap_mode = (
            QTextEdit.LineWrapMode.WidgetWidth
            if self.word_wrap_enabled
            else QTextEdit.LineWrapMode.NoWrap
        )
        tab.editor.setLineWrapMode(wrap_mode)

    def _apply_render_whitespace_to_tab(self, tab) -> None:
        """Apply current whitespace rendering setting to a tab editor."""
        if not hasattr(tab, 'editor'):
            return

        option = tab.editor.document().defaultTextOption()
        flags = option.flags()
        if self.render_whitespace_enabled:
            flags |= QTextOption.Flag.ShowTabsAndSpaces
        else:
            flags &= ~QTextOption.Flag.ShowTabsAndSpaces
        option.setFlags(flags)
        tab.editor.document().setDefaultTextOption(option)
        tab.editor.viewport().update()

    def _prepare_tab_for_dock(self, tab) -> None:
        """Wire tab signals and hide tab-local file/edit controls."""
        if not getattr(tab, "_clarify_buffer_identity", ""):
            setattr(tab, "_clarify_buffer_identity", uuid.uuid4().hex)
        if hasattr(tab, 'toolbar'):
            tab.toolbar.setVisible(False)

        if hasattr(tab, 'modified_changed'):
            tab.modified_changed.connect(lambda _modified=False, t=tab: self._update_tab_title(t))
        if hasattr(tab, 'editor'):
            tab.editor.textChanged.connect(self._recovery_lifecycle.schedule)
            if not getattr(tab, "_clarify_temp_note_autosave_connected", False):
                tab.editor.textChanged.connect(
                    lambda t=tab: self._schedule_temp_note_autosave(t)
                )
                setattr(tab, "_clarify_temp_note_autosave_connected", True)
            if not getattr(tab, '_clarify_status_signals_connected', False):
                tab.editor.cursorPositionChanged.connect(
                    lambda t=tab: self._on_editor_status_cursor_changed(t)
                )
                tab.editor.textChanged.connect(
                    lambda t=tab: self._on_editor_status_content_changed(t)
                )
                setattr(tab, '_clarify_status_signals_connected', True)
            if not getattr(tab, '_clarify_indent_filter_installed', False):
                tab.editor.installEventFilter(self)
                setattr(tab, '_clarify_indent_filter_installed', True)
        if hasattr(tab, 'edit_only_changed'):
            tab.edit_only_changed.connect(lambda _enabled=False, t=tab: self._on_tab_mode_changed(t))
        if (
            isinstance(tab, JsonEditorTab)
            and hasattr(tab, 'validation_changed')
            and not getattr(tab, '_clarify_schema_validation_connected', False)
        ):
            tab.validation_changed.connect(
                lambda is_valid, _message="", t=tab: self._on_json_validation_changed(t, is_valid)
            )
            setattr(tab, '_clarify_schema_validation_connected', True)

        self._apply_auto_save_to_tab(tab)
        self._apply_word_wrap_to_tab(tab)
        self._apply_render_whitespace_to_tab(tab)
        self._apply_line_numbers_to_tab(tab)
        self._apply_indentation_to_tab(tab)

    def eventFilter(self, watched, event):  # pylint: disable=invalid-name
        """Apply bounded editor key behavior without stealing global shortcuts."""
        if event.type() == QEvent.Type.FocusIn and self._tab_for_editor(watched) is not None:
            self._last_active_editor = watched
            self._update_editor_status_indicators()
            if self._find_session_is_visible():
                self._bind_find_session_to_active_editor()
        if event.type() == QEvent.Type.KeyPress:
            modifiers = event.modifiers()
            unsupported = modifiers & (
                Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.AltModifier
                | Qt.KeyboardModifier.MetaModifier
            )
            tab = self._tab_for_editor(watched)
            key = event.key()
            if tab is not None and self._event_matches_shortcut(event, "redo"):
                self._last_active_editor = watched
                self.action_redo.trigger()
                return True
            if (
                tab is not None
                and not watched.isReadOnly()
                and not unsupported
                and key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab)
            ):
                is_outdent = (
                    key == Qt.Key.Key_Backtab
                    or bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
                )
                cursor = watched.textCursor()
                if is_outdent:
                    self._outdent_tab_lines(tab, editor=watched)
                elif cursor.hasSelection():
                    self._indent_tab_lines(tab, editor=watched)
                else:
                    cursor.insertText(self._indent_unit())
                return True
            if (
                tab is not None
                and not watched.isReadOnly()
                and not unsupported
                and key in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            ):
                self._insert_indented_newline(watched)
                return True
            if tab is not None and not unsupported and key == Qt.Key.Key_Home:
                self._move_to_smart_home(
                    watched,
                    keep_anchor=bool(
                        modifiers & Qt.KeyboardModifier.ShiftModifier
                    ),
                )
                return True
        return super().eventFilter(watched, event)

    @staticmethod
    def _event_matches_shortcut(event, action_name: str) -> bool:
        """Match one editor key event against the active configurable shortcut."""
        pressed = QKeySequence(event.keyCombination())
        return any(
            pressed.matches(shortcut) == QKeySequence.SequenceMatch.ExactMatch
            for shortcut in ShortcutManager.get_key_sequences(action_name)
        )

    @staticmethod
    def _insert_indented_newline(editor) -> None:
        """Split the current line while inheriting its existing indentation."""
        cursor = editor.textCursor()
        block = cursor.block()
        line = block.text()
        column = max(0, cursor.position() - block.position())
        prefix_length = len(line) - len(line.lstrip(" \t"))
        inherited_prefix = line[:min(column, prefix_length)]
        cursor.beginEditBlock()
        cursor.insertText(f"\n{inherited_prefix}")
        cursor.endEditBlock()
        editor.setTextCursor(cursor)

    @staticmethod
    def _move_to_smart_home(editor, *, keep_anchor: bool) -> None:
        """Toggle within the current visual line without editing the document."""
        cursor = editor.textCursor()
        block = cursor.block()
        text = block.text()
        current_column = max(
            0,
            min(len(text), cursor.position() - block.position()),
        )
        visual_start = 0
        visual_end = len(text)
        layout = block.layout()
        if layout is not None and layout.lineCount() > 0:
            visual_line = layout.lineForTextPosition(current_column)
            if visual_line.isValid():
                visual_start = max(0, min(len(text), visual_line.textStart()))
                visual_end = max(
                    visual_start,
                    min(
                        len(text),
                        visual_start + visual_line.textLength(),
                    ),
                )

        visual_text = text[visual_start:visual_end]
        stripped_visual_text = visual_text.lstrip(" \t")
        first_text_column = (
            visual_start + len(visual_text) - len(stripped_visual_text)
            if stripped_visual_text
            else visual_start
        )
        target_column = (
            visual_start
            if current_column == first_text_column
            else first_text_column
        )
        move_mode = (
            QTextCursor.MoveMode.KeepAnchor
            if keep_anchor
            else QTextCursor.MoveMode.MoveAnchor
        )
        cursor.setPosition(block.position() + target_column, move_mode)
        editor.setTextCursor(cursor)

    def _tab_for_editor(self, editor):
        """Return the open tab that owns an editor widget."""
        if editor is self.split_editor:
            return self._split_source_tab
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            if getattr(tab, 'editor', None) is editor:
                return tab
        return None

    def _active_editor_for_tab(self, tab):
        """Return the focused view for a tab, including its split view."""
        if (
            self._last_active_editor is self.split_editor
            and self._split_source_tab is tab
            and not self.split_panel.isHidden()
        ):
            return self.split_editor
        return tab.editor

    @staticmethod
    def _first_editor_line(tab) -> str:
        """Read at most one bounded block for extensionless shebang detection."""
        editor = getattr(tab, "editor", None)
        if editor is None:
            return ""
        block = editor.document().firstBlock()
        return block.text()[:512] if block.isValid() else ""

    def _language_path_suffix(self, tab) -> str:
        """Return explicit suffix metadata without scanning document content."""
        candidates = (
            getattr(tab, "file_path", ""),
            getattr(tab, "_clarify_language_extension", ""),
            getattr(tab, "_clarify_display_name", ""),
        )
        for candidate in candidates:
            if not candidate:
                continue
            suffix = os.path.splitext(str(candidate))[1].lower()
            if suffix:
                return suffix
        return ""

    @staticmethod
    def _language_from_shebang(first_line: str) -> str | None:
        """Recognize common extensionless scripts from one bounded first line."""
        line = first_line.strip().lower()
        if not line.startswith("#!"):
            return None
        checks = (
            (("python",), "Python"),
            (("node", "deno"), "JavaScript"),
            (("bash", "/sh", " sh"), "Shell Script"),
            (("zsh",), "Zsh"),
            (("ruby",), "Ruby"),
            (("php",), "PHP"),
            (("lua",), "Lua"),
            (("rscript",), "R"),
        )
        for markers, language in checks:
            if any(marker in line for marker in markers):
                return language
        return None

    def _language_for_tab(self, tab) -> str:
        """Resolve language from existing tab metadata with a bounded fallback."""
        if tab is None:
            return tr("editor.status_language_plain_text")
        if isinstance(tab, JsonEditorTab):
            return "JSON"

        suffix = self._language_path_suffix(tab)
        if suffix:
            return self._LANGUAGE_BY_SUFFIX.get(
                suffix,
                tr("editor.status_language_plain_text"),
            )

        highlighter = getattr(tab, "highlighter", None)
        file_type = str(getattr(highlighter, "file_type", "") or "").lower()
        if file_type in self._LANGUAGE_BY_FILE_TYPE:
            return self._LANGUAGE_BY_FILE_TYPE[file_type]

        return self._language_from_shebang(
            self._first_editor_line(tab)
        ) or tr("editor.status_language_plain_text")

    def _language_depends_on_content(self, tab) -> bool:
        """Only extensionless, metadata-free tabs need first-line rechecks."""
        if tab is None or isinstance(tab, JsonEditorTab):
            return False
        if self._language_path_suffix(tab):
            return False
        highlighter = getattr(tab, "highlighter", None)
        file_type = str(getattr(highlighter, "file_type", "") or "").lower()
        return file_type not in self._LANGUAGE_BY_FILE_TYPE

    def _on_editor_status_cursor_changed(self, tab) -> None:
        """Refresh only when the emitting view owns the active cursor."""
        if tab is not self.tab_widget.currentWidget():
            return
        if self._active_editor_for_tab(tab) is getattr(tab, "editor", None):
            self._update_editor_status_indicators()

    def _on_editor_status_content_changed(self, tab) -> None:
        """Recheck only bounded content-dependent language metadata."""
        if (
            tab is self.tab_widget.currentWidget()
            and self._language_depends_on_content(tab)
        ):
            self._update_editor_status_indicators()

    def _update_editor_status_indicators(self) -> None:
        """Publish indentation, active cursor and language without parsing files."""
        indent_key = (
            "editor.status_indent_tabs"
            if self.indent_use_tabs
            else "editor.status_indent_spaces"
        )
        self.status_indent_label.set_value(
            tr(indent_key).format(width=self.indent_width)
        )

        tab = self.tab_widget.currentWidget()
        editor = (
            self._active_editor_for_tab(tab)
            if tab is not None and hasattr(tab, "editor")
            else None
        )
        if editor is None:
            cursor_text = tr("editor.status_cursor_unavailable")
        else:
            cursor = editor.textCursor()
            cursor_text = tr("editor.status_cursor_position").format(
                line=cursor.blockNumber() + 1,
                column=cursor.positionInBlock() + 1,
            )
        self.status_cursor_label.set_value(cursor_text)
        self.status_language_label.set_value(
            tr("editor.status_language").format(
                language=self._language_for_tab(tab)
            )
        )

    def _retranslate_status_info(self, _language=None) -> None:
        """Refresh indicator templates after a runtime language switch."""
        self._update_editor_status_indicators()

    def _retranslate_editor_ui(self, language=None) -> None:
        """Retranslate the local menu, shared actions, toolbar and status row."""
        for menu_spec in self._MENU_SPECS.values():
            getattr(self, menu_spec["attr"]).setTitle(tr(menu_spec["title_key"]))
        for action_id, action in self._action_by_id.items():
            action.setText(tr(self._ACTION_SPECS[action_id]["text_key"]))
        self.menu_recent_files.setTitle(tr("editor.menu_recent_files"))
        self.menu_recent_folders.setTitle(tr("editor.menu_recent_folders"))
        self._apply_tooltips()
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            refresh_accessibility = getattr(
                tab, "_update_mode_accessibility", None
            )
            if callable(refresh_accessibility):
                refresh_accessibility()
        self._retranslate_recovery_offer()
        self._retranslate_status_info(language)

    def _indent_unit(self) -> str:
        return "\t" if self.indent_use_tabs else " " * self.indent_width

    def _apply_indentation_to_tab(self, tab) -> None:
        if not hasattr(tab, 'editor'):
            return
        self._apply_indentation_to_editor(tab.editor)

    def _apply_indentation_to_editor(self, editor) -> None:
        space_width = editor.fontMetrics().horizontalAdvance(" ")
        editor.setTabStopDistance(max(1, space_width * self.indent_width))

    def _set_indent_use_tabs(self, enabled: bool) -> None:
        self.indent_use_tabs = bool(enabled)
        self.settings.setValue("indent_use_tabs", self.indent_use_tabs)
        self._refresh_editor_menus()
        self._update_editor_status_indicators()

    def _set_indent_width(self, width: int | None = None) -> bool:
        if width is None:
            width, accepted = QInputDialog.getInt(
                self,
                tr("editor.indent_width_title"),
                tr("editor.indent_width_prompt"),
                self.indent_width,
                1,
                8,
            )
            if not accepted:
                return False
        self.indent_width = max(1, min(8, int(width)))
        self.settings.setValue("indent_width", self.indent_width)
        for index in range(self.tab_widget.count()):
            self._apply_indentation_to_tab(self.tab_widget.widget(index))
        self._apply_indentation_to_editor(self.split_editor)
        self._update_editor_status_indicators()
        return True

    def _setup_file_menu(self) -> None:
        """Create the local File menu bar actions."""
        self._setup_editor_menu("file")
        self.menu_recent_files = QMenu(tr("editor.menu_recent_files"), self.menu_file)
        self.menu_recent_folders = QMenu(
            tr("editor.menu_recent_folders"), self.menu_file
        )
        self.menu_recent_files.menuAction().setData("recent_files_menu")
        self.menu_recent_folders.menuAction().setData("recent_folders_menu")
        self.menu_file.insertMenu(self.action_recover_unsaved, self.menu_recent_files)
        self.menu_file.insertMenu(self.action_recover_unsaved, self.menu_recent_folders)
        self.menu_recent_files.aboutToShow.connect(self._refresh_recent_menus)
        self.menu_recent_folders.aboutToShow.connect(self._refresh_recent_menus)
        self._refresh_recent_menus()

    def _setup_edit_menu(self) -> None:
        """Create the local Edit menu bar actions."""
        self._setup_editor_menu("edit")

    def _setup_view_menu(self) -> None:
        """Create the local View menu bar actions."""
        self._setup_editor_menu("view")

    def _setup_json_menu(self) -> None:
        """Create the local JSON menu bar actions."""
        self._setup_editor_menu("json")

    def _setup_editor_menu(self, menu_id: str) -> None:
        """Build one editor menu from the declarative menu/action specs."""
        menu_spec = self._MENU_SPECS[menu_id]
        menu = self.menu_bar.addMenu(tr(menu_spec["title_key"]))
        setattr(self, menu_spec["attr"], menu)

        for item in menu_spec["items"]:
            if item is None:
                menu.addSeparator()
                continue
            menu.addAction(self._create_editor_action(item))

    def _create_editor_action(self, action_id: str) -> QAction:
        """Create and register a QAction while preserving action_* attributes."""
        spec = self._ACTION_SPECS[action_id]
        action = QAction(tr(spec["text_key"]), self)
        action.setData(action_id)
        action.setCheckable(bool(spec.get("checkable", False)))

        shortcuts = spec.get("shortcuts")
        if shortcuts:
            action.setShortcuts([QKeySequence(item) for item in shortcuts])
        elif spec.get("shortcut_action"):
            action.setShortcuts(
                ShortcutManager.get_key_sequences(spec["shortcut_action"])
            )
        else:
            shortcut = spec.get("shortcut")
            if shortcut is not None:
                if isinstance(shortcut, str):
                    shortcut = QKeySequence(shortcut)
                action.setShortcut(shortcut)

        if action.shortcuts():
            action.setShortcutContext(
                spec.get(
                    "shortcut_context",
                    Qt.ShortcutContext.WidgetWithChildrenShortcut,
                )
            )
            self.addAction(action)
            menu_id = next(
                (
                    candidate
                    for candidate, menu_spec in self._MENU_SPECS.items()
                    if action_id in menu_spec["items"]
                ),
                "edit",
            )
            shortcut_action = spec.get("shortcut_action")
            ShortcutManager.register_action(
                action,
                shortcut_action or f"editor.{action_id}",
                category=f"Editor {menu_id.title()}",
                managed=bool(shortcut_action),
            )

        setattr(self, f"action_{action_id}", action)
        self._action_by_id[action_id] = action
        return action

    def _action_signal_handlers(self):
        """Return QAction handlers keyed by action id."""
        return {
            "new": lambda _checked=False: self._new_file(),
            "open": lambda _checked=False: self._open_file(),
            "open_path": lambda _checked=False: self._open_file_by_path(),
            "open_folder": lambda _checked=False: self._open_explorer_folder(),
            "close_folder": lambda _checked=False: self._close_explorer_folder(),
            "restore_folder_sessions": self._set_folder_sessions_enabled,
            "clear_folder_sessions": lambda _checked=False: self._clear_folder_sessions(),
            "recover_unsaved": lambda _checked=False: self._show_recovery_dialog(),
            "recovery_retention": lambda _checked=False: self._set_recovery_retention(),
            "save_temp_note": lambda _checked=False: self._save_current_as_temp_note(),
            "manage_temp_notes": lambda _checked=False: self._show_temp_notes_dialog(),
            "temp_note_retention": lambda _checked=False: self._set_temp_note_retention(),
            "save": lambda _checked=False: self._save_file(),
            "save_as": lambda _checked=False: self._save_file_as(),
            "compare_with_saved": lambda _checked=False: self._compare_current_tab_with_saved(),
            "reload_from_disk": lambda _checked=False: self._reload_current_tab_from_disk(),
            "enable_saving": lambda _checked=False: self._enable_saving_current_tab(),
            "export": lambda _checked=False: self._export_current_tab(),
            "close_tab": lambda _checked=False: self._close_current_tab(),
            "auto_save": lambda checked: self._set_auto_save_enabled(checked),
            "undo": lambda _checked=False: self._undo_current_tab(),
            "redo": lambda _checked=False: self._redo_current_tab(),
            "cut": lambda _checked=False: self._cut_current_tab(),
            "copy": lambda _checked=False: self._copy_current_tab(),
            "paste": lambda _checked=False: self._paste_current_tab(),
            "delete": lambda _checked=False: self._delete_current_selection(),
            "select_all": lambda _checked=False: self._select_all_current_tab(),
            "select_line": lambda _checked=False: self._select_current_line(),
            "find": lambda _checked=False: self._show_find_dialog(False),
            "find_replace": lambda _checked=False: self._show_find_dialog(True),
            "go_to_line": lambda _checked=False: self._show_go_to_line_dialog(),
            "duplicate_line": lambda _checked=False: self._duplicate_current_line_or_selection(),
            "toggle_line_comment": lambda _checked=False: self._toggle_line_comment_current_tab(),
            "indent": lambda _checked=False: self._indent_current_lines(),
            "outdent": lambda _checked=False: self._outdent_current_lines(),
            "indent_use_tabs": lambda checked: self._set_indent_use_tabs(checked),
            "indent_width": lambda _checked=False: self._set_indent_width(),
            "move_line_up": lambda _checked=False: self._move_current_lines(-1),
            "move_line_down": lambda _checked=False: self._move_current_lines(1),
            "insert_datetime": lambda _checked=False: self._insert_datetime_current_tab(),
            "trim_trailing_spaces": lambda _checked=False: self._trim_trailing_spaces_current_tab(),
            "word_wrap": lambda checked: self._set_word_wrap_enabled(checked),
            "render_whitespace": lambda checked: self._set_render_whitespace_enabled(checked),
            "show_line_numbers": lambda checked: self._set_show_line_numbers_enabled(checked),
            "show_explorer": lambda checked: self._set_explorer_visible(checked),
            "small_text": lambda _checked=False: self._change_current_text_size(-1),
            "large_text": lambda _checked=False: self._change_current_text_size(1),
            "normal_size": lambda _checked=False: self._set_current_text_size(self.normal_text_font_size),
            "previous_file_tab": lambda _checked=False: self._previous_file_tab(),
            "next_file_tab": lambda _checked=False: self._next_file_tab(),
            "json_format_2": lambda _checked=False: self._format_current_json_tab(2),
            "json_format_4": lambda _checked=False: self._format_current_json_tab(4),
            "json_minify": lambda _checked=False: self._format_current_json_tab(None),
            "json_validate": lambda _checked=False: self._validate_current_json_tab(),
            "json_validate_schema": lambda _checked=False: self._validate_current_json_tab_with_schema(),
            "json_generate_schema": lambda _checked=False: self._show_generated_json_schema(),
            "json_set_active_schema": lambda _checked=False: self._set_active_json_schema_for_current_tab(),
            "json_clear_active_schema": lambda _checked=False: self._clear_active_json_schema_for_current_tab(),
            "json_insert_missing_required": lambda _checked=False: (
                self._insert_missing_required_fields_for_current_tab()
            ),
            "json_search": lambda _checked=False: self._search_current_json_tab(),
            "json_collapse_tree": lambda _checked=False: self._set_current_json_tree_expanded(False),
            "json_expand_tree": lambda _checked=False: self._set_current_json_tree_expanded(True),
        }

    def _refresh_editor_menus(self) -> None:
        """Refresh File/Edit menu action states for the current tab."""
        tab = self.tab_widget.currentWidget() if hasattr(self, 'tab_widget') else None
        context = {
            "has_tab": tab is not None,
            "has_editor": tab is not None and hasattr(tab, 'editor'),
            "has_file_path": tab is not None and bool(getattr(tab, 'file_path', None)),
            "can_reload_from_disk": (
                tab is not None
                and bool(getattr(tab, 'file_path', None))
                and os.path.exists(getattr(tab, 'file_path', ''))
                and not bool(getattr(tab, 'edit_only_mode', False))
            ),
            "is_json_tab": isinstance(tab, JsonEditorTab),
            "has_active_schema": isinstance(tab, JsonEditorTab) and bool(
                getattr(tab, '_clarify_active_schema_text', None)
            ),
            "is_edit_only": tab is not None and bool(getattr(tab, 'edit_only_mode', False)),
        }

        for action_id, rule in self._ACTION_ENABLE_RULES.items():
            self._action_by_id[action_id].setEnabled(context[rule])

        for action_id, attr_name in self._ACTION_CHECKED_ATTRIBUTES.items():
            self._set_action_checked(action_id, bool(getattr(self, attr_name)))

    def _set_action_checked(self, action_id: str, checked: bool) -> None:
        """Set a checkable action state without re-triggering its handler."""
        action = self._action_by_id[action_id]
        action.blockSignals(True)
        action.setChecked(checked)
        action.blockSignals(False)

    def _show_tab_context_menu(self, pos):
        """Show context menu on tab right-click."""
        tab_bar = self.tab_widget.tabBar()
        index = tab_bar.tabAt(pos)
        if index < 0:
            return
        self._build_tab_context_menu(index).exec(tab_bar.mapToGlobal(pos))

    def _build_tab_context_menu(self, index: int) -> QMenu:
        """Build a translated context menu bound to the clicked tab object."""
        menu = QMenu(self)
        menu.setToolTipsVisible(True)
        tab = self.tab_widget.widget(index)
        if tab is None:
            return menu

        def add(action_id: str, text_key: str, callback, enabled: bool = True):
            action = menu.addAction(tr(text_key))
            action.setData(action_id)
            action.setEnabled(enabled)
            action.triggered.connect(lambda _checked=False: callback())
            return action

        add("close", "editor.tab_close", lambda: self._close_tab_object(tab))
        add(
            "close_others",
            "editor.tab_close_others",
            lambda: self._close_tab_objects(
                [
                    self.tab_widget.widget(position)
                    for position in range(self.tab_widget.count())
                    if self.tab_widget.widget(position) is not tab
                ]
            ),
            self.tab_widget.count() > 1,
        )
        add(
            "close_all",
            "editor.tab_close_all",
            lambda: self._close_tab_objects(self._all_tab_objects()),
        )
        add(
            "close_left",
            "editor.tab_close_left",
            lambda: self._close_tab_objects(
                [self.tab_widget.widget(position) for position in range(index)]
            ),
            index > 0,
        )
        add(
            "close_right",
            "editor.tab_close_right",
            lambda: self._close_tab_objects(
                [
                    self.tab_widget.widget(position)
                    for position in range(index + 1, self.tab_widget.count())
                ]
            ),
            index < self.tab_widget.count() - 1,
        )
        menu.addSeparator()
        absolute_path, relative_path, unavailable_key = self._tab_path_copy_values(tab)
        absolute_action = add(
            "copy_absolute",
            "editor.explorer_copy_absolute",
            lambda: self._copy_tab_path(tab, relative=False),
            absolute_path is not None,
        )
        relative_action = add(
            "copy_relative",
            "editor.explorer_copy_relative",
            lambda: self._copy_tab_path(tab, relative=True),
            relative_path is not None,
        )
        if unavailable_key:
            reason = tr(unavailable_key)
            self._set_action_unavailable_reason(absolute_action, reason)
            self._set_action_unavailable_reason(relative_action, reason)
        menu.addSeparator()
        add(
            "split_down",
            "editor.tab_split_down",
            lambda: self._show_split_view(tab, Qt.Vertical),
            hasattr(tab, "editor"),
        )
        add(
            "split_right",
            "editor.tab_split_right",
            lambda: self._show_split_view(tab, Qt.Horizontal),
            hasattr(tab, "editor"),
        )
        if hasattr(tab, "edit_only_mode"):
            menu.addSeparator()
            key = (
                "editor.tab_disable_edit_only"
                if tab.edit_only_mode
                else "editor.tab_enable_edit_only"
            )
            add(
                "toggle_edit_only",
                key,
                lambda: self._toggle_edit_only_for_tab(self.tab_widget.indexOf(tab)),
            )
        return menu

    def _all_tab_objects(self) -> list:
        return [self.tab_widget.widget(index) for index in range(self.tab_widget.count())]

    @staticmethod
    def _is_dense_untitled_tab(tab) -> bool:
        """Return whether a tab needs an order-derived visible Untitled name."""
        return bool(
            tab is not None
            and not getattr(tab, "file_path", None)
            and not getattr(tab, "_clarify_display_name", "")
            and not getattr(tab, "_clarify_temp_note_id", "")
        )

    @staticmethod
    def _is_legacy_untitled_title(title: str) -> bool:
        """Recognize prior sparse Untitled labels without treating them as IDs."""
        if title == "Untitled":
            return True
        prefix = "Untitled-"
        suffix = title[len(prefix) :] if title.startswith(prefix) else ""
        return bool(suffix.isdigit() and int(suffix) >= 2)

    def _renumber_untitled_tabs(self) -> None:
        """Refresh mutable Untitled labels from current visual tab order."""
        ordinal = 0
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            if self._is_dense_untitled_tab(tab):
                ordinal += 1
                title = "Untitled" if ordinal == 1 else f"Untitled-{ordinal}"
                setattr(tab, "_clarify_untitled_display_name", title)
            elif hasattr(tab, "_clarify_untitled_display_name"):
                delattr(tab, "_clarify_untitled_display_name")
            self.tab_widget.setTabText(index, self._display_title_for_tab(tab))
        if self._split_source_tab is not None:
            self.split_title.setText(
                self._display_title_for_tab(self._split_source_tab)
            )

    def _close_tab_object(self, tab) -> bool:
        index = self.tab_widget.indexOf(tab)
        return index < 0 or self._close_tab(index)

    def _close_tab_objects(self, tabs: list) -> bool:
        """Close tabs in visual order and stop immediately on cancellation."""
        for tab in list(tabs):
            if tab is not None and not self._close_tab_object(tab):
                return False
        return True

    def _show_split_view(self, tab, orientation: Qt.Orientation) -> bool:
        """Show a second view over the source tab's existing QTextDocument."""
        if tab is None or not hasattr(tab, "editor"):
            return False
        self.editor_workspace_splitter.setOrientation(orientation)
        self.split_editor.setDocument(tab.editor.document())
        self.split_editor.setReadOnly(tab.editor.isReadOnly())
        self.split_editor.setFont(tab.editor.font())
        self.split_editor.setLineWrapMode(tab.editor.lineWrapMode())
        self._apply_indentation_to_editor(self.split_editor)
        self._split_source_tab = tab
        self.split_title.setText(self._display_title_for_tab(tab))
        self.split_title.setToolTip(getattr(tab, "file_path", "") or tab.get_tab_title())
        self.split_panel.show()
        self.editor_workspace_splitter.setSizes([1, 1])
        self.split_editor.setFocus()
        self._last_active_editor = self.split_editor
        self._update_editor_status_indicators()
        if self._find_session_is_visible():
            self._bind_find_session_to_active_editor()
        return True

    def _close_split_view(self) -> None:
        """Detach the shared document before its owning tab can be deleted."""
        source_tab = self._split_source_tab
        if self._split_source_tab is not None:
            self.split_editor.setDocument(QTextDocument(self.split_editor))
        self._split_source_tab = None
        self.split_title.clear()
        self.split_panel.hide()
        self._last_active_editor = getattr(source_tab, "editor", None)
        self.tab_widget.setFocus()
        self._update_editor_status_indicators()
        if self._find_session_is_visible():
            self._bind_find_session_to_active_editor()

    def _new_file(self, edit_only: bool = False):
        """Create new untitled file."""
        # Create text editor tab
        tab = EditorTab(None, self, edit_only_mode=edit_only)
        self._prepare_tab_for_dock(tab)

        index = self.tab_widget.addTab(tab, tab.get_display_title())
        self._renumber_untitled_tabs()
        self.tab_widget.setCurrentIndex(index)
        self._refresh_editor_menus()

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
        dialog.setWindowTitle(tr("editor.dialog_open_title"))
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

        # Add checkbox for edit-only mode using option widget
        chk_edit_only = QCheckBox(tr("editor.chk_edit_only"))
        layout = dialog.layout()
        if layout:
            layout.addWidget(chk_edit_only, layout.rowCount(), 0, 1, -1)

        if not dialog.exec_():
            return

        file_paths = dialog.selectedFiles()
        if not file_paths:
            return

        file_path = file_paths[0]
        edit_only = chk_edit_only.isChecked() if layout else False
        self.open_file_path(file_path, edit_only=edit_only)

    def _open_file_by_path(self) -> bool:
        """Prompt for a path and open it through the public editor API."""
        value, accepted = QInputDialog.getText(
            self,
            tr("editor.open_path_title"),
            tr("editor.open_path_prompt"),
        )
        if not accepted:
            return False

        try:
            file_path = self._resolve_typed_file_path(value)
        except ValueError as error:
            QMessageBox.warning(self, tr("editor.open_path_error_title"), str(error))
            return False
        return self.open_file_path(file_path)

    def _resolve_typed_file_path(self, value: str) -> str:
        """Resolve and validate a user-entered file path without invoking a shell."""
        raw_value = value.strip() if isinstance(value, str) else ""
        if not raw_value:
            raise ValueError(tr("editor.open_path_empty"))
        if len(raw_value) > self.MAX_TYPED_PATH_CHARS:
            raise ValueError(tr("editor.open_path_too_long"))
        if "\x00" in raw_value:
            raise ValueError(tr("editor.open_path_invalid"))

        expanded = os.path.expanduser(raw_value)
        if not os.path.isabs(expanded):
            expanded = os.path.join(self.explorer_root_path, expanded)
        normalized = self._normalized_file_path(expanded)

        if os.path.islink(normalized):
            raise ValueError(tr("editor.open_path_symlink"))
        if not os.path.exists(normalized):
            raise ValueError(tr("editor.open_path_missing").format(path=normalized))
        if os.path.isdir(normalized):
            raise ValueError(tr("editor.open_path_directory").format(path=normalized))
        if not os.path.isfile(normalized):
            raise ValueError(tr("editor.open_path_unsupported").format(path=normalized))
        if not os.access(normalized, os.R_OK):
            raise ValueError(tr("editor.open_path_unreadable").format(path=normalized))
        try:
            size = os.path.getsize(normalized)
        except OSError as error:
            raise ValueError(
                tr("editor.open_path_stat_failed").format(error=error)
            ) from error
        if size > self.MAX_TYPED_FILE_BYTES:
            raise ValueError(
                tr("editor.open_path_too_large").format(
                    limit=self.MAX_TYPED_FILE_BYTES // (1024 * 1024)
                )
            )
        return normalized

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

    def _settle_successful_save(self, tab, file_path: str, *, save_as: bool) -> bool:
        """Commit all Editor state only after the file write has succeeded."""
        normalized_path = self._normalized_file_path(file_path)
        tab.file_path = normalized_path
        tab.is_modified = False
        if hasattr(tab, 'editor'):
            tab.editor.document().setModified(False)
        if hasattr(tab, 'auto_save_timer'):
            tab.auto_save_timer.stop()

        was_edit_only = bool(getattr(tab, 'edit_only_mode', False))
        if was_edit_only:
            tab.edit_only_mode = False
            if hasattr(tab, '_update_visual_indicators'):
                tab._update_visual_indicators()
            if hasattr(tab, '_update_toolbar_visibility'):
                tab._update_toolbar_visibility()

        self._track_tab_disk_state(tab)
        self._assign_tab_folder_root(tab)
        self._add_recent_file(normalized_path)
        self._persist_tab_order()
        self._discard_recovery_for_tab(tab)
        self._renumber_untitled_tabs()
        self._update_tab_title(tab)
        self._refresh_editor_menus()
        action = "Saved as" if save_as else "Saved"
        self.lbl_status.setText(f"{action}: {os.path.basename(normalized_path)}")
        if was_edit_only and hasattr(tab, 'edit_only_changed'):
            tab.edit_only_changed.emit(False)
        return True

    def _save_file(self):
        """Save current file (State pattern: behavior depends on edit_only_mode)."""
        tab = self.tab_widget.currentWidget()
        if not tab:
            return False

        if getattr(tab, "_clarify_temp_note_id", ""):
            return self._save_temp_note_tab(tab)

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
                return self._save_file_as()
            return False

        if not tab.file_path:
            return self._save_file_as()

        save_decision = self._save_decision_for_external_change(tab)
        if save_decision == "save_as":
            return self._save_file_as()
        if save_decision != "save":
            return False

        # Handle different tab types
        if isinstance(tab, JsonEditorTab):
            success, error_msg = tab.save_file()
            if success:
                return self._settle_successful_save(tab, tab.file_path, save_as=False)
            else:
                QMessageBox.critical(self, tr("editor.msg_error_title"), tr("editor.msg_save_failed").format(error_msg))
        else:
            # EditorTab
            if tab.save_file():
                return self._settle_successful_save(tab, tab.file_path, save_as=False)
            else:
                QMessageBox.critical(
                    self, tr("editor.msg_error_title"),
                    tr("editor.msg_save_failed_path").format(tab.file_path)
                )
        return False

    def _save_file_as(self):
        """Save current file with new name."""
        tab = self.tab_widget.currentWidget()
        if not tab:
            return False

        if (
            getattr(tab, "_clarify_temp_note_id", "")
            and (getattr(tab, "is_modified", False) or tab.editor.document().isModified())
            and not self._save_temp_note_tab(tab)
        ):
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*);;JSON Files (*.json);;Text Files (*.txt);;"
            "Python (*.py);;JavaScript (*.js);;TypeScript (*.ts);;HTML (*.html)"
        )

        if not file_path:
            return False

        # Handle different tab types
        if isinstance(tab, JsonEditorTab):
            success, error_msg = tab.save_file(file_path)
            if success:
                if not self._finalize_temp_note_conversion(tab):
                    return False
                return self._settle_successful_save(tab, file_path, save_as=True)
            else:
                QMessageBox.critical(self, tr("editor.msg_error_title"), tr("editor.msg_save_failed").format(error_msg))
                return False
        else:
            # EditorTab
            if tab.save_file(file_path):
                if not self._finalize_temp_note_conversion(tab):
                    return False
                return self._settle_successful_save(tab, file_path, save_as=True)
            else:
                QMessageBox.critical(
                    self, tr("editor.msg_error_title"),
                    tr("editor.msg_save_failed_path").format(file_path)
                )
                return False

    def _undo_current_tab(self):
        """Undo the last change in the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        tab.editor.undo()
        self.lbl_status.setText(tr("editor.status_undone"))

    def _redo_current_tab(self):
        """Redo the last undone change in the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return False

        editor = self._active_editor_for_tab(tab)
        if editor.isReadOnly() or not editor.document().isRedoAvailable():
            return False

        editor.redo()
        self.lbl_status.setText(tr("editor.status_redone"))
        return True

    def _copy_current_tab(self):
        """Copy current editor content to clipboard."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        QApplication.clipboard().setText(tab.editor.toPlainText())
        self.lbl_status.setText(tr("editor.status_copied"))

    def _cut_current_tab(self):
        """Cut selected text from the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        tab.editor.cut()
        self.lbl_status.setText(tr("editor.status_cut"))

    def _paste_current_tab(self):
        """Paste clipboard text into the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        tab.editor.paste()
        self.lbl_status.setText(tr("editor.status_pasted"))

    def _delete_current_selection(self):
        """Delete selected text or the next character in the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        cursor = tab.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        else:
            cursor.deleteChar()
        self.lbl_status.setText(tr("editor.status_deleted"))

    def _select_all_current_tab(self):
        """Select all text in the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        tab.editor.selectAll()
        self.lbl_status.setText(tr("editor.status_selected_all"))

    def _select_current_line(self):
        """Select the current line using the conventional Ctrl+L command."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return
        cursor = tab.editor.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        tab.editor.setTextCursor(cursor)

    def _duplicate_current_line_or_selection(self):
        """Duplicate the selected text or current line."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        cursor = tab.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText().replace("\u2029", "\n")
            cursor.setPosition(cursor.selectionEnd())
            cursor.insertText(selected_text)
        else:
            line_cursor = QTextCursor(cursor)
            line_cursor.select(QTextCursor.LineUnderCursor)
            line_text = line_cursor.selectedText()
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n" + line_text)

        self.lbl_status.setText(tr("editor.status_line_duplicated"))

    @staticmethod
    def _split_line_ending(line: str) -> tuple[str, str]:
        """Split a line into body and line ending."""
        if line.endswith("\r\n"):
            return line[:-2], "\r\n"
        if line.endswith("\n"):
            return line[:-1], "\n"
        if line.endswith("\r"):
            return line[:-1], "\r"
        return line, ""

    @staticmethod
    def _line_start_position(lines: list[str], line_index: int) -> int:
        """Return text position at the start of a 0-based line index."""
        bounded_index = max(0, min(line_index, len(lines)))
        return sum(len(line) for line in lines[:bounded_index])

    @staticmethod
    def _selected_line_range(editor) -> tuple[list[str], int, int]:
        """Return document lines and selected/current 0-based line range."""
        text = editor.toPlainText()
        lines = text.splitlines(keepends=True) or [""]
        cursor = editor.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        if cursor.hasSelection() and end > start and end <= len(text) and text[end - 1] == "\n":
            end -= 1

        start_line = text.count("\n", 0, start)
        end_line = text.count("\n", 0, end)
        return lines, min(start_line, len(lines) - 1), min(end_line, len(lines) - 1)

    @staticmethod
    def _replace_editor_text(
        editor,
        new_text: str,
        cursor_position: int = 0,
        anchor_position: int | None = None,
    ) -> None:
        """Replace text as one undoable edit and restore cursor or selection."""
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.insertText(new_text)
        cursor.endEditBlock()
        bounded_position = max(0, min(cursor_position, len(new_text)))
        if anchor_position is not None and anchor_position != cursor_position:
            bounded_anchor = max(0, min(anchor_position, len(new_text)))
            cursor.setPosition(bounded_anchor)
            cursor.setPosition(bounded_position, QTextCursor.KeepAnchor)
        else:
            cursor.setPosition(bounded_position)
        editor.setTextCursor(cursor)

    @staticmethod
    def _map_position_after_prefix_edits(
        position: int,
        edits: list[tuple[int, int, int]],
    ) -> int:
        """Map a text position after line-prefix insertions/removals."""
        delta = 0
        for start, removed, inserted in edits:
            if position < start:
                break
            current_start = start + delta
            if position <= start + removed:
                return current_start + inserted
            delta += inserted - removed
        return position + delta

    @staticmethod
    def _comment_tokens_for_path(file_path: str | None) -> tuple[str, str]:
        """Return line-comment tokens for a file path."""
        suffix = os.path.splitext(file_path or "")[1].lower()
        if suffix in {".html", ".htm", ".xml", ".svg"}:
            return "<!-- ", " -->"
        if suffix in {".css", ".scss", ".sass", ".less"}:
            return "/* ", " */"
        if suffix in {
            ".py", ".sh", ".bash", ".zsh", ".fish", ".yml", ".yaml",
            ".toml", ".ini", ".conf", ".cfg", ".env", ".md", ".txt",
        }:
            return "# ", ""
        return "// ", ""

    @staticmethod
    def _line_is_commented(line: str, prefix: str, suffix: str) -> bool:
        """Return whether a line is commented with the provided tokens."""
        body, _ending = EditorDock._split_line_ending(line)
        indent_len = len(body) - len(body.lstrip(" \t"))
        content = body[indent_len:]
        if suffix:
            return content.startswith(prefix) and content.endswith(suffix)
        return content.startswith(prefix)

    @staticmethod
    def _comment_line(line: str, prefix: str, suffix: str) -> str:
        """Comment one line while preserving indentation and newline."""
        body, ending = EditorDock._split_line_ending(line)
        indent_len = len(body) - len(body.lstrip(" \t"))
        return f"{body[:indent_len]}{prefix}{body[indent_len:]}{suffix}{ending}"

    @staticmethod
    def _uncomment_line(line: str, prefix: str, suffix: str) -> str:
        """Uncomment one line if it uses the provided tokens."""
        body, ending = EditorDock._split_line_ending(line)
        indent_len = len(body) - len(body.lstrip(" \t"))
        content = body[indent_len:]
        if suffix and content.startswith(prefix) and content.endswith(suffix):
            content = content[len(prefix):-len(suffix)]
        elif not suffix and content.startswith(prefix):
            content = content[len(prefix):]
        return f"{body[:indent_len]}{content}{ending}"

    def _toggle_line_comment_current_tab(self):
        """Toggle line comments for current or selected lines."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        editor = tab.editor
        lines, start_line, end_line = self._selected_line_range(editor)
        prefix, suffix = self._comment_tokens_for_path(getattr(tab, 'file_path', None))
        selected_lines = lines[start_line:end_line + 1]
        non_empty_lines = [line for line in selected_lines if line.strip()]
        should_uncomment = bool(non_empty_lines) and all(
            self._line_is_commented(line, prefix, suffix) for line in non_empty_lines
        )

        for index in range(start_line, end_line + 1):
            if should_uncomment:
                lines[index] = self._uncomment_line(lines[index], prefix, suffix)
            else:
                lines[index] = self._comment_line(lines[index], prefix, suffix)

        self._replace_editor_text(
            editor,
            "".join(lines),
            self._line_start_position(lines, start_line),
        )
        self.lbl_status.setText(tr("editor.status_line_comment_toggled"))

    def _indent_current_lines(self):
        """Indent current or selected lines with the configured unit."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        self._indent_tab_lines(tab, editor=self._active_editor_for_tab(tab))

    def _indent_tab_lines(self, tab, *, editor=None) -> None:
        """Indent one tab's current/selected lines while preserving selection."""
        editor = editor or tab.editor
        original_cursor = editor.textCursor()
        original_position = original_cursor.position()
        original_anchor = original_cursor.anchor()
        lines, start_line, end_line = self._selected_line_range(editor)
        original_starts = [self._line_start_position(lines, index) for index in range(len(lines))]
        unit = self._indent_unit()
        edits = []
        for index in range(start_line, end_line + 1):
            edits.append((original_starts[index], 0, len(unit)))
            lines[index] = unit + lines[index]

        self._replace_editor_text(
            editor,
            "".join(lines),
            self._map_position_after_prefix_edits(original_position, edits),
            self._map_position_after_prefix_edits(original_anchor, edits),
        )
        self.lbl_status.setText(
            tr("editor.status_lines_indented").format(count=end_line - start_line + 1)
        )

    @staticmethod
    def _outdent_line(line: str) -> tuple[str, int]:
        """Remove one indentation level from a line."""
        if line.startswith("\t"):
            return line[1:], 1
        leading_spaces = len(line) - len(line.lstrip(" "))
        remove_count = min(4, leading_spaces)
        return line[remove_count:], remove_count

    def _outdent_current_lines(self):
        """Outdent current or selected lines by one indentation level."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        self._outdent_tab_lines(tab, editor=self._active_editor_for_tab(tab))

    def _outdent_tab_lines(self, tab, *, editor=None) -> None:
        """Outdent one tab's current/selected lines while preserving selection."""
        editor = editor or tab.editor
        original_cursor = editor.textCursor()
        original_position = original_cursor.position()
        original_anchor = original_cursor.anchor()
        lines, start_line, end_line = self._selected_line_range(editor)
        original_starts = [self._line_start_position(lines, index) for index in range(len(lines))]
        edits = []
        for index in range(start_line, end_line + 1):
            original_line = lines[index]
            if original_line.startswith("\t"):
                remove_count = 1
            else:
                leading_spaces = len(original_line) - len(original_line.lstrip(" "))
                remove_count = min(self.indent_width, leading_spaces)
            edits.append((original_starts[index], remove_count, 0))
            lines[index] = original_line[remove_count:]

        self._replace_editor_text(
            editor,
            "".join(lines),
            self._map_position_after_prefix_edits(original_position, edits),
            self._map_position_after_prefix_edits(original_anchor, edits),
        )
        self.lbl_status.setText(
            tr("editor.status_lines_outdented").format(count=end_line - start_line + 1)
        )

    def _move_current_lines(self, direction: int):
        """Move current or selected lines up or down."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        editor = tab.editor
        lines, start_line, end_line = self._selected_line_range(editor)
        if (direction < 0 and start_line == 0) or (direction > 0 and end_line >= len(lines) - 1):
            self.lbl_status.setText(tr("editor.status_line_not_moved"))
            return

        moving_lines = lines[start_line:end_line + 1]
        if direction < 0:
            new_lines = (
                lines[:start_line - 1]
                + moving_lines
                + [lines[start_line - 1]]
                + lines[end_line + 1:]
            )
            new_start_line = start_line - 1
            status_key = "editor.status_line_moved_up"
        else:
            new_lines = (
                lines[:start_line]
                + [lines[end_line + 1]]
                + moving_lines
                + lines[end_line + 2:]
            )
            new_start_line = start_line + 1
            status_key = "editor.status_line_moved_down"

        self._replace_editor_text(
            editor,
            "".join(new_lines),
            self._line_start_position(new_lines, new_start_line),
        )
        self.lbl_status.setText(tr(status_key))

    def _insert_datetime_current_tab(self):
        """Insert the current local date and time at the cursor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tab.editor.textCursor().insertText(timestamp)
        self.lbl_status.setText(tr("editor.status_datetime_inserted"))

    @staticmethod
    def _trim_line_trailing_spaces(line: str) -> tuple[str, int]:
        """Trim trailing spaces/tabs before a line ending."""
        newline = ""
        body = line
        if line.endswith("\r\n"):
            body = line[:-2]
            newline = "\r\n"
        elif line.endswith("\n"):
            body = line[:-1]
            newline = "\n"
        elif line.endswith("\r"):
            body = line[:-1]
            newline = "\r"

        trimmed_body = body.rstrip(" \t")
        return trimmed_body + newline, len(body) - len(trimmed_body)

    def _trim_trailing_spaces_current_tab(self):
        """Remove trailing spaces and tabs from the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        editor = tab.editor
        original_text = editor.toPlainText()
        trimmed_lines = []
        removed_count = 0
        for line in original_text.splitlines(keepends=True):
            trimmed_line, removed = self._trim_line_trailing_spaces(line)
            trimmed_lines.append(trimmed_line)
            removed_count += removed

        trimmed_text = "".join(trimmed_lines)
        if trimmed_text != original_text:
            cursor = editor.textCursor()
            position = min(cursor.position(), len(trimmed_text))
            cursor.beginEditBlock()
            cursor.select(QTextCursor.Document)
            cursor.insertText(trimmed_text)
            cursor.setPosition(position)
            cursor.endEditBlock()
            editor.setTextCursor(cursor)

        self.lbl_status.setText(
            tr("editor.status_trailing_spaces_trimmed").format(count=removed_count)
        )

    def _set_current_text_size(self, size: int):
        """Set text font size for the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        bounded_size = max(self.min_text_font_size, min(self.max_text_font_size, size))
        font = tab.editor.font()
        font.setPointSize(bounded_size)
        tab.editor.setFont(font)

        controller = getattr(tab.editor, '_clarify_line_numbers', None)
        if controller is not None:
            controller.update()

        self.lbl_status.setText(tr("editor.status_text_size").format(size=bounded_size))

    def _change_current_text_size(self, delta: int):
        """Increment or decrement current editor text font size."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        current_size = tab.editor.font().pointSize()
        if current_size <= 0:
            current_size = self.normal_text_font_size

        self._set_current_text_size(current_size + delta)

    def _show_find_dialog(self, replace_enabled: bool):
        """Show the workspace's one modeless Find/Replace session."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        editor = self._active_editor_for_tab(tab)
        selected_query = editor.textCursor().selectedText()
        selected_query = selected_query.replace("\u2029", "\n").replace(
            "\u2028", "\n"
        )

        if self._find_dialog is None:
            self._find_dialog = _EditorFindDialog(
                editor,
                replace_enabled,
                self._find_panel_host,
                file_path=getattr(tab, "file_path", None),
                state=self.find_state,
                state_changed=self._persist_find_state,
                history=self._find_history_for_tab(tab),
                selection_query=selected_query,
                close_requested=self._hide_find_session,
                presentation_toggle_requested=self._toggle_find_presentation,
            )
            self._find_dialog.setAttribute(Qt.WA_DeleteOnClose, False)
            self._find_panel_layout.addWidget(self._find_dialog)
        else:
            self._find_dialog.bind_editor(
                editor,
                replace_enabled=replace_enabled,
                file_path=getattr(tab, "file_path", None),
                history=self._find_history_for_tab(tab),
                selection_query=selected_query,
            )

        self._apply_find_presentation(show=True)
        self._find_dialog.find_input.setFocus(
            Qt.FocusReason.ShortcutFocusReason
        )
        if selected_query:
            self._find_dialog.find_input.selectAll()

    def _find_session_is_visible(self) -> bool:
        dialog = self._find_dialog
        return bool(dialog is not None and not dialog.isHidden())

    def _bind_find_session_to_active_editor(self) -> bool:
        """Retarget a visible session after a tab or split focus change."""
        if self._find_dialog is None:
            return False
        tab = self.tab_widget.currentWidget()
        if tab is None or not hasattr(tab, "editor"):
            return False
        editor = self._active_editor_for_tab(tab)
        self._find_dialog.bind_editor(
            editor,
            replace_enabled=self._find_dialog.replace_enabled,
            file_path=getattr(tab, "file_path", None),
            history=self._find_history_for_tab(tab),
        )
        return True

    def _apply_find_presentation(self, *, show: bool) -> None:
        """Reparent the same session between its lower and window hosts."""
        dialog = self._find_dialog
        if dialog is None:
            return
        dialog.hide()
        if self._find_presentation_mode == "floating":
            self._find_panel_layout.removeWidget(dialog)
            self._find_panel_host.hide()
            dialog.setParent(self, Qt.WindowType.Dialog)
            dialog.setMinimumWidth(560)
            geometry = self.settings.value("find/floating_geometry")
            if geometry:
                dialog.restoreGeometry(geometry)
        else:
            dialog.setParent(self._find_panel_host, Qt.WindowType.Widget)
            if self._find_panel_layout.indexOf(dialog) < 0:
                self._find_panel_layout.addWidget(dialog)
            dialog.setMinimumWidth(0)
            self._find_panel_host.setVisible(show)
        dialog.set_presentation_mode(self._find_presentation_mode)
        if show:
            dialog.show()
            if self._find_presentation_mode == "floating":
                dialog.raise_()
                dialog.activateWindow()

    def _toggle_find_presentation(self) -> None:
        """Persist and apply the other presentation without cloning state."""
        dialog = self._find_dialog
        if dialog is None:
            return
        if self._find_presentation_mode == "floating":
            self.settings.setValue(
                "find/floating_geometry", dialog.saveGeometry()
            )
            self._find_presentation_mode = "docked"
        else:
            self._find_presentation_mode = "floating"
        self.settings.setValue(
            "find/presentation_mode", self._find_presentation_mode
        )
        self._apply_find_presentation(show=True)
        dialog.find_input.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _hide_find_session(self) -> None:
        """Hide the reusable session without retaining a second UI."""
        dialog = self._find_dialog
        if dialog is None:
            return
        dialog._remember_current_values()
        if self._find_presentation_mode == "floating":
            self.settings.setValue(
                "find/floating_geometry", dialog.saveGeometry()
            )
        dialog.hide()
        self._find_panel_host.hide()
        tab = self.tab_widget.currentWidget()
        if tab is not None and hasattr(tab, "editor"):
            self._active_editor_for_tab(tab).setFocus(
                Qt.FocusReason.ShortcutFocusReason
            )

    def _shutdown_find_session(self) -> None:
        """Disconnect and delete the one session during owner teardown."""
        dialog = self._find_dialog
        if dialog is None:
            return
        if self._find_presentation_mode == "floating" and dialog.isVisible():
            self.settings.setValue(
                "find/floating_geometry", dialog.saveGeometry()
            )
        self._find_dialog = None
        dialog.shutdown()
        dialog.deleteLater()
        self._find_panel_host.hide()

    @staticmethod
    def _find_buffer_identity(tab) -> str:
        identity = getattr(tab, "_clarify_find_identity", "")
        if not identity:
            identity = uuid.uuid4().hex
            setattr(tab, "_clarify_find_identity", identity)
        return identity

    def _find_history_for_tab(self, tab) -> _EditorFindHistory:
        identity = self._find_buffer_identity(tab)
        history = self._find_history_by_buffer.pop(identity, None)
        if history is None:
            history = _EditorFindHistory(self.MAX_FIND_HISTORY_ENTRIES)
        self._find_history_by_buffer[identity] = history
        while len(self._find_history_by_buffer) > self.MAX_FIND_HISTORY_BUFFERS:
            oldest_identity = next(iter(self._find_history_by_buffer))
            self._find_history_by_buffer.pop(oldest_identity)
        return history

    def _discard_find_history(self, tab) -> None:
        identity = getattr(tab, "_clarify_find_identity", "")
        if identity:
            self._find_history_by_buffer.pop(identity, None)

    def _select_relative_file_tab(self, offset: int) -> bool:
        """Select an Editor file tab relative to the current one."""
        count = self.tab_widget.count()
        if count <= 0:
            return False
        current = max(0, self.tab_widget.currentIndex())
        self.tab_widget.setCurrentIndex((current + offset) % count)
        tab = self.tab_widget.currentWidget()
        editor = getattr(tab, "editor", None)
        if editor is not None:
            editor.setFocus(Qt.FocusReason.ShortcutFocusReason)
        return True

    def _previous_file_tab(self) -> bool:
        return self._select_relative_file_tab(-1)

    def _next_file_tab(self) -> bool:
        return self._select_relative_file_tab(1)

    def _persist_find_state(self, state: dict) -> None:
        """Persist the global Clarify Editor match preferences."""
        scope = state.get("scope", "all")
        if scope not in {"all", "strings", "variables", "comments"}:
            scope = "all"
        inverted_unit = state.get("inverted_unit", "line")
        if inverted_unit not in {"line", "token", "interval"}:
            inverted_unit = "line"
        self.find_state = {
            "case_sensitive": bool(state.get("case_sensitive", False)),
            "whole_word": bool(state.get("whole_word", False)),
            "regex": bool(state.get("regex", False)),
            "scope": scope,
            "inverted": bool(state.get("inverted", False)),
            "inverted_unit": inverted_unit,
        }
        for key, value in self.find_state.items():
            self.settings.setValue(f"find/{key}", value)

    def _show_go_to_line_dialog(self):
        """Show a dialog for jumping to a specific editor line."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        line_count = max(1, tab.editor.document().blockCount())
        current_line = tab.editor.textCursor().blockNumber() + 1
        line_number, accepted = QInputDialog.getInt(
            self,
            tr("editor.go_to_line_dialog_title"),
            tr("editor.go_to_line_prompt").format(max=line_count),
            current_line,
            1,
            line_count,
            1,
        )

        if accepted:
            self._go_to_line_in_current_tab(line_number)

    def _go_to_line_in_current_tab(self, line_number: int) -> bool:
        """Move the current editor cursor to a 1-based line number."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return False

        editor = tab.editor
        line_count = max(1, editor.document().blockCount())
        target_line = max(1, min(line_number, line_count))
        block = editor.document().findBlockByLineNumber(target_line - 1)
        if not block.isValid():
            return False

        cursor = QTextCursor(block)
        editor.setTextCursor(cursor)
        editor.ensureCursorVisible()
        editor.setFocus()
        self.lbl_status.setText(
            tr("editor.status_go_to_line").format(line=target_line, max=line_count)
        )
        return True

    def apply_confirmed_voice_command(self, command: dict) -> bool:
        """Apply a command already reviewed and confirmed in the voice tool."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, "editor"):
            return False
        action = command.get("action")
        if action == "insert_text":
            tab.editor.textCursor().insertText(str(command.get("text", "")))
            self.lbl_status.setText("Confirmed voice text inserted")
            return True
        if action == "go_to_line":
            return self._go_to_line_in_current_tab(int(command.get("line", 1)))
        if action == "save":
            return bool(self._save_file())
        return False

    def _current_json_tab(self):
        """Return the current tab when it is a JsonEditorTab."""
        tab = self.tab_widget.currentWidget()
        if isinstance(tab, JsonEditorTab):
            return tab
        return None

    def _replace_json_tab_text(self, tab: JsonEditorTab, text: str) -> None:
        """Replace JSON tab text, mark it modified, and refresh validation/title."""
        if tab.editor.toPlainText() != text:
            tab.editor.blockSignals(True)
            tab.editor.setPlainText(text)
            tab.editor.blockSignals(False)
            tab.is_modified = True
            tab.modified_changed.emit(True)

        tab._validate()
        self._update_tab_title(tab)

    def _format_current_json_tab(self, indent: int | None) -> bool:
        """Format or minify the active JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        text = tab.editor.toPlainText()
        if indent is None:
            success, result = tab.validator.minify_json(text)
        else:
            success, result = tab.validator.format_json(text, indent)

        if not success:
            self.lbl_status.setText(tr("editor.status_json_format_failed"))
            QMessageBox.warning(self, tr("json_editor.msg_format_error_title"), result)
            return False

        self._replace_json_tab_text(tab, result)
        if indent is None:
            self.lbl_status.setText(tr("editor.status_json_minified"))
        else:
            self.lbl_status.setText(
                tr("editor.status_json_formatted").format(spaces=indent)
            )
        return True

    def _validate_current_json_tab(self) -> bool:
        """Validate the active JSON tab and update the dock status bar."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        result = tab.validator.validate(tab.editor.toPlainText())
        tab._validate()
        if result.is_valid:
            self.lbl_status.setText(tr("editor.status_json_valid"))
            return True

        self.lbl_status.setText(
            tr("editor.status_json_invalid").format(
                line=result.line,
                col=result.col,
                error=result.error_msg,
            )
        )
        return False

    @staticmethod
    def _format_json_schema_path(path) -> str:
        """Format a jsonschema absolute_path into a concise JSONPath-like label."""
        label = "$"
        for part in path:
            if isinstance(part, int):
                label += f"[{part}]"
            else:
                label += f".{part}"
        return label

    @classmethod
    def _format_json_schema_errors(cls, errors) -> str:
        """Format a small validation error summary for UI and tests."""
        error_list = list(errors)
        lines = [
            f"{cls._format_json_schema_path(error.absolute_path)}: {error.message}"
            for error in error_list[:5]
        ]
        if len(error_list) > 5:
            lines.append(f"... {len(error_list) - 5} more error(s)")
        return "\n".join(lines)

    @classmethod
    def _validate_json_text_with_schema(cls, json_text: str, schema_text: str) -> tuple[bool, str]:
        """Validate JSON document text against JSON Schema text."""
        is_valid, message, _path = cls._validate_json_text_with_schema_detail(
            json_text,
            schema_text,
        )
        return is_valid, message

    @classmethod
    def _validate_json_text_with_schema_detail(
        cls,
        json_text: str,
        schema_text: str,
    ) -> tuple[bool, str, tuple]:
        """Validate JSON document text and return the first schema error path."""
        try:
            instance = json.loads(json_text)
        except json.JSONDecodeError as exc:
            return (
                False,
                f"JSON parse error at line {exc.lineno}, col {exc.colno}: {exc.msg}",
                (),
            )

        try:
            schema = json.loads(schema_text)
        except json.JSONDecodeError as exc:
            return (
                False,
                f"Schema parse error at line {exc.lineno}, col {exc.colno}: {exc.msg}",
                (),
            )

        try:
            from jsonschema import SchemaError
            from jsonschema.validators import validator_for
        except ImportError:
            return False, "JSON Schema validation requires the jsonschema package.", ()

        try:
            validator_cls = validator_for(schema)
            validator_cls.check_schema(schema)
            validator = validator_cls(schema)
            errors = sorted(
                validator.iter_errors(instance),
                key=lambda error: tuple(str(part) for part in error.absolute_path),
            )
        except SchemaError as exc:
            return False, f"Invalid schema: {exc.message}", ()
        except Exception as exc:
            return False, f"Schema validation error: {exc}", ()

        if errors:
            first_error_path = tuple(errors[0].absolute_path)
            return False, cls._format_json_schema_errors(errors), first_error_path
        return True, "", ()

    def _validate_current_json_tab_with_schema(self) -> bool:
        """Validate the active JSON tab against a selected JSON Schema file."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        schema_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("editor.schema_dialog_title"),
            "",
            tr("editor.schema_dialog_filter"),
        )
        if not schema_path:
            return False

        try:
            with open(schema_path, 'r', encoding='utf-8') as file_obj:
                schema_text = file_obj.read()
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("editor.msg_error_title"),
                tr("editor.schema_read_error").format(error=str(exc)),
            )
            return False

        is_valid, message, path = self._validate_json_text_with_schema_detail(
            tab.editor.toPlainText(),
            schema_text,
        )
        if is_valid:
            tab.clear_diagnostic("json_schema")
            tab.lbl_validation.setText("✓ Valid JSON")
            tab.lbl_validation.setStyleSheet("color: #6A9955; font-weight: bold;")
            self.lbl_status.setText(tr("editor.status_json_schema_valid"))
            QMessageBox.information(
                self,
                tr("editor.schema_valid_title"),
                tr("editor.schema_valid_message"),
            )
            return True

        self.lbl_status.setText(tr("editor.status_json_schema_invalid"))
        tab.show_schema_diagnostic(message, path)
        QMessageBox.warning(
            self,
            tr("editor.schema_invalid_title"),
            tr("editor.schema_invalid_message").format(error=message),
        )
        return False

    @staticmethod
    def _active_json_schema_label(tab: JsonEditorTab) -> str:
        """Return a short label for the active schema on a JSON tab."""
        schema_path = getattr(tab, '_clarify_active_schema_path', None)
        if schema_path:
            return os.path.basename(schema_path)
        return "schema"

    def _set_active_json_schema_for_tab(
        self,
        tab: JsonEditorTab,
        schema_text: str,
        schema_path: str | None = None,
    ) -> None:
        """Store active JSON Schema metadata on a tab."""
        setattr(tab, '_clarify_active_schema_text', schema_text)
        setattr(tab, '_clarify_active_schema_path', schema_path)
        tab.set_schema_completion_candidates_from_schema_text(schema_text)

    def _validate_json_tab_against_active_schema(
        self,
        tab: JsonEditorTab,
        show_message: bool = False,
    ) -> bool:
        """Validate one JSON tab against its active schema."""
        schema_text = getattr(tab, '_clarify_active_schema_text', None)
        if not schema_text:
            return False

        schema_label = self._active_json_schema_label(tab)
        is_valid, message, path = self._validate_json_text_with_schema_detail(
            tab.editor.toPlainText(),
            schema_text,
        )
        if is_valid:
            tab.clear_diagnostic("json_schema")
            tab.lbl_validation.setText("✓ Valid JSON")
            tab.lbl_validation.setStyleSheet("color: #6A9955; font-weight: bold;")
            self.lbl_status.setText(
                tr("editor.status_json_active_schema_valid").format(schema=schema_label)
            )
            if show_message:
                QMessageBox.information(
                    self,
                    tr("editor.active_schema_valid_title"),
                    tr("editor.active_schema_valid_message").format(schema=schema_label),
                )
            return True

        self.lbl_status.setText(
            tr("editor.status_json_active_schema_invalid").format(schema=schema_label)
        )
        tab.show_schema_diagnostic(message, path)
        if show_message:
            QMessageBox.warning(
                self,
                tr("editor.active_schema_invalid_title"),
                tr("editor.active_schema_invalid_message").format(
                    schema=schema_label,
                    error=message,
                ),
            )
        return False

    def _on_json_validation_changed(self, tab: JsonEditorTab, is_valid: bool) -> None:
        """Revalidate active schema after the JSON tab syntax validator runs."""
        if tab is not self.tab_widget.currentWidget():
            return
        if not is_valid:
            return
        if not getattr(tab, '_clarify_active_schema_text', None):
            return

        self._validate_json_tab_against_active_schema(tab, show_message=False)

    def _set_active_json_schema_for_current_tab(self) -> bool:
        """Choose and store an active schema for the current JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        schema_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("editor.active_schema_dialog_title"),
            "",
            tr("editor.schema_dialog_filter"),
        )
        if not schema_path:
            return False

        try:
            with open(schema_path, 'r', encoding='utf-8') as file_obj:
                schema_text = file_obj.read()
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("editor.msg_error_title"),
                tr("editor.schema_read_error").format(error=str(exc)),
            )
            return False

        self._set_active_json_schema_for_tab(tab, schema_text, schema_path)
        self._refresh_editor_menus()
        schema_label = self._active_json_schema_label(tab)
        self.lbl_status.setText(
            tr("editor.status_json_active_schema_set").format(schema=schema_label)
        )
        self._validate_json_tab_against_active_schema(tab, show_message=True)
        return True

    def _clear_active_json_schema_for_current_tab(self) -> bool:
        """Clear the active schema from the current JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        schema_label = self._active_json_schema_label(tab)
        setattr(tab, '_clarify_active_schema_text', None)
        setattr(tab, '_clarify_active_schema_path', None)
        tab.clear_diagnostic("json_schema")
        tab.clear_schema_completion_candidates()
        self._refresh_editor_menus()
        self.lbl_status.setText(
            tr("editor.status_json_active_schema_cleared").format(schema=schema_label)
        )
        return True

    @classmethod
    def _placeholder_for_json_schema(cls, schema: dict):
        """Return a conservative placeholder value for a JSON Schema fragment."""
        if not isinstance(schema, dict):
            return None

        if "default" in schema:
            return json.loads(json.dumps(schema["default"], ensure_ascii=False))
        if "const" in schema:
            return json.loads(json.dumps(schema["const"], ensure_ascii=False))
        if isinstance(schema.get("enum"), list) and schema["enum"]:
            return json.loads(json.dumps(schema["enum"][0], ensure_ascii=False))

        for composition_key in ("oneOf", "anyOf"):
            options = schema.get(composition_key)
            if isinstance(options, list):
                for option in options:
                    if isinstance(option, dict):
                        return cls._placeholder_for_json_schema(option)

        schema_type = schema.get("type")
        if isinstance(schema_type, list):
            schema_type = next((item for item in schema_type if item != "null"), "null")

        if schema_type is None:
            if isinstance(schema.get("properties"), dict):
                schema_type = "object"
            elif "items" in schema:
                schema_type = "array"

        placeholders = {
            "string": "",
            "integer": 0,
            "number": 0.0,
            "boolean": False,
            "array": [],
            "object": {},
            "null": None,
        }
        return placeholders.get(schema_type)

    @classmethod
    def _insert_missing_required_fields_from_schema(
        cls,
        json_text: str,
        schema_text: str,
    ) -> tuple[bool, str, list[str]]:
        """Insert top-level missing required fields using a JSON Schema."""
        try:
            document = json.loads(json_text)
        except json.JSONDecodeError as exc:
            return (
                False,
                f"JSON parse error at line {exc.lineno}, col {exc.colno}: {exc.msg}",
                [],
            )

        try:
            schema = json.loads(schema_text)
        except json.JSONDecodeError as exc:
            return (
                False,
                f"Schema parse error at line {exc.lineno}, col {exc.colno}: {exc.msg}",
                [],
            )

        if not isinstance(document, dict):
            return False, "Quick fix requires the current JSON root to be an object.", []
        if not isinstance(schema, dict):
            return False, "Quick fix requires the active schema root to be an object schema.", []

        schema_type = schema.get("type")
        schema_types = schema_type if isinstance(schema_type, list) else [schema_type]
        if schema_type is not None and "object" not in schema_types:
            return False, "Quick fix requires the active schema root to be an object schema.", []

        required_fields = schema.get("required", [])
        if not isinstance(required_fields, list):
            return False, "Schema required field must be a list.", []

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}

        missing_fields = [
            field
            for field in required_fields
            if isinstance(field, str) and field not in document
        ]
        if not missing_fields:
            return True, json_text, []

        updated_document = dict(document)
        for field in missing_fields:
            field_schema = properties.get(field, {})
            updated_document[field] = cls._placeholder_for_json_schema(field_schema)

        updated_text = json.dumps(updated_document, indent=2, ensure_ascii=False)
        return True, updated_text, missing_fields

    def _insert_missing_required_fields_for_current_tab(self) -> bool:
        """Insert top-level required fields missing from the active JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        schema_text = getattr(tab, '_clarify_active_schema_text', None)
        if not schema_text:
            return False

        success, result, inserted_fields = self._insert_missing_required_fields_from_schema(
            tab.editor.toPlainText(),
            schema_text,
        )
        if not success:
            self.lbl_status.setText(tr("editor.status_json_required_insert_failed"))
            QMessageBox.warning(
                self,
                tr("editor.insert_missing_required_failed_title"),
                tr("editor.insert_missing_required_failed_message").format(error=result),
            )
            return False

        if not inserted_fields:
            self.lbl_status.setText(tr("editor.status_json_required_none"))
            QMessageBox.information(
                self,
                tr("editor.insert_missing_required_none_title"),
                tr("editor.insert_missing_required_none_message"),
            )
            return True

        field_list = ", ".join(inserted_fields)
        reply = QMessageBox.question(
            self,
            tr("editor.insert_missing_required_title"),
            tr("editor.insert_missing_required_message").format(fields=field_list),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return False

        self._replace_json_tab_text(tab, result)
        self.lbl_status.setText(
            tr("editor.status_json_required_inserted").format(fields=field_list)
        )
        return True

    @classmethod
    def _merge_json_schemas(cls, schemas: list[dict]) -> dict:
        """Merge inferred schemas into one permissive schema."""
        schemas = [schema for schema in schemas if schema]
        if not schemas:
            return {}

        unique = {
            json.dumps(schema, sort_keys=True, ensure_ascii=False): schema
            for schema in schemas
        }
        if len(unique) == 1:
            return next(iter(unique.values()))

        schema_types = {schema.get("type") for schema in schemas}
        if schema_types == {"object"}:
            property_schemas: dict[str, list[dict]] = {}
            required_sets = []
            for schema in schemas:
                for key, value_schema in schema.get("properties", {}).items():
                    property_schemas.setdefault(key, []).append(value_schema)
                required_sets.append(set(schema.get("required", [])))

            merged = {"type": "object"}
            if property_schemas:
                merged["properties"] = {
                    key: cls._merge_json_schemas(values)
                    for key, values in sorted(property_schemas.items())
                }
            if required_sets:
                required = sorted(set.intersection(*required_sets))
                if required:
                    merged["required"] = required
            return merged

        if schema_types == {"array"}:
            item_schemas = [
                schema["items"]
                for schema in schemas
                if "items" in schema
            ]
            merged = {"type": "array"}
            if item_schemas:
                merged["items"] = cls._merge_json_schemas(item_schemas)
            return merged

        if len(schema_types) == 1 and None not in schema_types:
            return {"type": next(iter(schema_types))}

        grouped_schemas: dict[str, list[dict]] = {}
        for schema in schemas:
            grouped_schemas.setdefault(str(schema.get("type")), []).append(schema)
        if len(grouped_schemas) > 1:
            merged_groups = [
                cls._merge_json_schemas(grouped_schemas[key])
                for key in sorted(grouped_schemas)
            ]
            unique_groups = {
                json.dumps(schema, sort_keys=True, ensure_ascii=False): schema
                for schema in merged_groups
            }
            return {
                "anyOf": [
                    unique_groups[key]
                    for key in sorted(unique_groups)
                ]
            }

        return {
            "anyOf": [
                unique[key]
                for key in sorted(unique)
            ]
        }

    @classmethod
    def _infer_json_schema(cls, value) -> dict:
        """Infer a basic JSON Schema fragment from a Python JSON value."""
        if isinstance(value, dict):
            schema = {"type": "object"}
            if value:
                schema["properties"] = {
                    key: cls._infer_json_schema(item)
                    for key, item in sorted(value.items())
                }
                schema["required"] = sorted(value)
            return schema

        if isinstance(value, list):
            schema = {"type": "array"}
            if value:
                schema["items"] = cls._merge_json_schemas([
                    cls._infer_json_schema(item)
                    for item in value
                ])
            return schema

        if isinstance(value, bool):
            return {"type": "boolean"}
        if value is None:
            return {"type": "null"}
        if isinstance(value, int):
            return {"type": "integer"}
        if isinstance(value, float):
            return {"type": "number"}
        return {"type": "string"}

    @classmethod
    def _generate_json_schema_text(cls, json_text: str) -> tuple[bool, str]:
        """Generate a formatted JSON Schema from JSON document text."""
        try:
            value = json.loads(json_text)
        except json.JSONDecodeError as exc:
            return (
                False,
                f"JSON parse error at line {exc.lineno}, col {exc.colno}: {exc.msg}",
            )

        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            **cls._infer_json_schema(value),
        }
        return True, json.dumps(schema, indent=2, ensure_ascii=False)

    def _save_generated_json_schema(self, schema_text: str) -> bool:
        """Save generated schema text to a selected file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("editor.generate_schema_save_title"),
            "",
            tr("editor.schema_dialog_filter"),
        )
        if not file_path:
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as file_obj:
                file_obj.write(schema_text)
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("editor.msg_error_title"),
                tr("editor.generate_schema_save_error").format(error=str(exc)),
            )
            return False

        self.lbl_status.setText(
            tr("editor.status_json_schema_saved").format(file=os.path.basename(file_path))
        )
        return True

    def _show_generated_json_schema(self) -> bool:
        """Generate and display a basic JSON Schema for the active JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        success, result = self._generate_json_schema_text(tab.editor.toPlainText())
        if not success:
            self.lbl_status.setText(tr("editor.status_json_schema_generate_failed"))
            QMessageBox.warning(
                self,
                tr("editor.generate_schema_error_title"),
                tr("editor.generate_schema_parse_error").format(error=result),
            )
            return False

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("editor.generate_schema_dialog_title"))
        dialog.resize(820, 620)

        layout = QVBoxLayout(dialog)
        schema_view = QTextEdit()
        schema_view.setReadOnly(True)
        schema_view.setAcceptRichText(False)
        schema_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        schema_view.setFont(tab.editor.font())
        schema_view.setPlainText(result)
        layout.addWidget(schema_view)

        button_row = QHBoxLayout()
        button_row.addStretch()

        btn_copy = QPushButton(tr("editor.btn_copy_schema"))
        btn_copy.clicked.connect(lambda _checked=False: (
            QApplication.clipboard().setText(result),
            self.lbl_status.setText(tr("editor.status_json_schema_copied")),
        ))
        button_row.addWidget(btn_copy)

        btn_save = QPushButton(tr("editor.btn_save_schema"))
        btn_save.clicked.connect(lambda _checked=False: self._save_generated_json_schema(result))
        button_row.addWidget(btn_save)

        btn_close = QPushButton(tr("editor.btn_close"))
        btn_close.clicked.connect(dialog.close)
        button_row.addWidget(btn_close)
        layout.addLayout(button_row)

        self.lbl_status.setText(tr("editor.status_json_schema_generated"))
        dialog.exec()
        return True

    def _search_current_json_tab(self) -> bool:
        """Open the JSON search dialog for the active JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        tab._show_search()
        return True

    def _set_current_json_tree_expanded(self, expanded: bool) -> bool:
        """Expand or collapse the JSON tree in the active JSON tab."""
        tab = self._current_json_tab()
        if tab is None:
            return False

        if expanded:
            tab.tree.expandAll()
            self.lbl_status.setText(tr("editor.status_json_tree_expanded"))
        else:
            tab.tree.collapseAll()
            self.lbl_status.setText(tr("editor.status_json_tree_collapsed"))
        return True

    def _export_current_tab(self):
        """Export current editor content to a chosen file."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("editor_tab.export_dialog_title"),
            "",
            tr("editor_tab.export_dialog_filter")
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tab.editor.toPlainText())
            self.lbl_status.setText(f"Exported: {os.path.basename(file_path)}")
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("editor_tab.export_error_title"),
                tr("editor_tab.export_error_message").format(exc)
            )

    @staticmethod
    def _build_saved_file_diff(file_path: str, saved_text: str, current_text: str) -> str:
        """Build a unified diff between the on-disk file and the editor buffer."""
        filename = os.path.basename(file_path) if file_path else "Untitled"
        diff_lines = difflib.unified_diff(
            saved_text.splitlines(keepends=True),
            current_text.splitlines(keepends=True),
            fromfile=f"{filename} (saved)",
            tofile=f"{filename} (current)",
        )
        return "".join(diff_lines)

    def _compare_current_tab_with_saved(self):
        """Compare current editor content with the file currently saved on disk."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        file_path = getattr(tab, 'file_path', None)
        if not file_path:
            QMessageBox.information(
                self,
                tr("editor.compare_no_file_title"),
                tr("editor.compare_no_file_message"),
            )
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file_obj:
                saved_text = file_obj.read()
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("editor.msg_error_title"),
                tr("editor.compare_read_error").format(error=str(exc)),
            )
            return

        current_text = tab.editor.toPlainText()
        if saved_text == current_text:
            self.lbl_status.setText(tr("editor.status_compare_no_changes"))
            QMessageBox.information(
                self,
                tr("editor.compare_no_changes_title"),
                tr("editor.compare_no_changes_message"),
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("editor.compare_dialog_title"))
        dialog.resize(900, 600)

        layout = QVBoxLayout(dialog)
        diff_view = QTextEdit()
        diff_view.setReadOnly(True)
        diff_view.setAcceptRichText(False)
        diff_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        diff_view.setFont(tab.editor.font())
        diff_view.setPlainText(
            self._build_saved_file_diff(file_path, saved_text, current_text)
        )
        layout.addWidget(diff_view)

        button_row = QHBoxLayout()
        button_row.addStretch()
        btn_close = QPushButton(tr("editor.btn_close"))
        btn_close.clicked.connect(dialog.close)
        button_row.addWidget(btn_close)
        layout.addLayout(button_row)

        self.lbl_status.setText(tr("editor.status_compare_changes"))
        dialog.exec()

    def _reload_current_tab_from_disk(self) -> bool:
        """Reload the current file-backed tab from disk."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return False

        file_path = self._normalized_file_path(getattr(tab, 'file_path', None))
        if not file_path:
            QMessageBox.information(
                self,
                tr("editor.compare_no_file_title"),
                tr("editor.compare_no_file_message"),
            )
            return False

        if not os.path.exists(file_path):
            self._check_tab_external_state(tab)
            self._update_tab_title(tab)
            self._show_external_status_for_current_tab()
            QMessageBox.warning(
                self,
                tr("editor.external_reload.missing_title"),
                tr("editor.external_reload.missing_path").format(path=file_path),
            )
            return False

        if getattr(tab, 'is_modified', False):
            reply = QMessageBox.question(
                self,
                tr("editor.external_reload.reload_title"),
                tr("editor.external_reload.reload_dirty"),
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False

        cursor = tab.editor.textCursor()
        cursor_position = cursor.position()
        anchor_position = cursor.anchor()

        try:
            content, loaded_signature = self._read_stable_reload_text(file_path)
        except _ExternalReloadError as error:
            message_key = f"editor.external_reload.error_{error.reason}"
            message = tr(message_key).format(
                path=file_path,
                limit=self.MAX_TYPED_FILE_BYTES // (1024 * 1024),
                error=error.detail,
            )
            QMessageBox.warning(
                self,
                tr("editor.external_reload.error_title"),
                message,
            )
            self._check_tab_external_state(tab)
            self._update_tab_title(tab)
            self._show_external_status_for_current_tab()
            return False

        if self._file_disk_signature(file_path) != loaded_signature:
            QMessageBox.warning(
                self,
                tr("editor.external_reload.error_title"),
                tr("editor.external_reload.error_changed_again").format(
                    path=file_path, limit=0, error=""
                ),
            )
            self._check_tab_external_state(tab)
            self._update_tab_title(tab)
            self._show_external_status_for_current_tab()
            return False

        if not tab.load_text_content(content, file_path):
            QMessageBox.critical(
                self,
                tr("editor.file_open_error_title"),
                tr("editor.file_open_error").format(file=file_path),
            )
            return False

        cursor = tab.editor.textCursor()
        document_limit = max(0, tab.editor.document().characterCount() - 1)
        cursor.setPosition(min(anchor_position, document_limit))
        cursor.setPosition(
            min(cursor_position, document_limit),
            QTextCursor.KeepAnchor
            if anchor_position != cursor_position
            else QTextCursor.MoveAnchor,
        )
        tab.editor.setTextCursor(cursor)

        setattr(tab, '_clarify_disk_path', file_path)
        setattr(tab, '_clarify_disk_signature', loaded_signature)
        current_signature = self._file_disk_signature(file_path)
        if current_signature == loaded_signature:
            setattr(
                tab,
                '_clarify_recovery_source_signature',
                self.recovery_store.source_signature(file_path),
            )
            self._set_tab_external_state(tab, "clean")
        else:
            setattr(tab, '_clarify_recovery_source_signature', None)
            self._set_tab_external_state(tab, "modified")
        self._refresh_external_file_watchers()
        self._update_tab_title(tab)
        self._refresh_editor_menus()
        self.lbl_status.setStyleSheet("color: #6A9955;")
        if current_signature == loaded_signature:
            message = tr("editor.external_reload.reloaded").format(
                file=os.path.basename(file_path)
            )
            self.lbl_status.setText(message)
            self.lbl_status.setAccessibleDescription(message)
        else:
            self._show_external_status_for_current_tab()
        return True

    def _enable_saving_current_tab(self):
        """Convert the current edit-only tab into a file-backed tab."""
        tab = self.tab_widget.currentWidget()
        if not tab or not getattr(tab, 'edit_only_mode', False):
            return

        if hasattr(tab, '_enable_file_saving'):
            tab._enable_file_saving()
            self._track_tab_disk_state(tab)
        else:
            reply = QMessageBox.question(
                self,
                tr("editor_tab.enable_saving_title"),
                tr("editor_tab.enable_saving_message"),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes and self._save_file_as():
                tab.edit_only_mode = False
                if hasattr(tab, 'edit_only_changed'):
                    tab.edit_only_changed.emit(False)
                self._track_tab_disk_state(tab)

        self._refresh_editor_menus()

    def _close_current_tab(self):
        """Close currently active tab."""
        return self._close_tab(self.tab_widget.currentIndex())

    def _close_tab(self, index: int) -> bool:
        """Close tab at index with edit-only mode handling."""
        if index < 0:
            return False

        tab = self.tab_widget.widget(index)

        if (
            getattr(tab, "_clarify_temp_note_id", "")
            and (getattr(tab, "is_modified", False) or tab.editor.document().isModified())
            and not self._save_temp_note_tab(tab)
        ):
            return False

        # Check if modified
        if hasattr(tab, 'is_modified') and tab.is_modified:
            # Special handling for edit-only tabs (requirement #6)
            if hasattr(tab, 'edit_only_mode') and tab.edit_only_mode:
                msg = QMessageBox(self)
                msg.setWindowTitle(tr("editor.dialog_close_edit_title"))
                msg.setText(f"'{tab.get_tab_title()}' has unsaved changes.")
                msg.setInformativeText("What would you like to do?")

                btn_save = msg.addButton(tr("editor.btn_save_to_file"), QMessageBox.ActionRole)
                btn_clipboard = msg.addButton(tr("editor.btn_copy_to_clipboard"), QMessageBox.ActionRole)
                msg.addButton(tr("editor.btn_discard"), QMessageBox.DestructiveRole)
                btn_cancel = msg.addButton(tr("editor.btn_cancel"), QMessageBox.RejectRole)

                msg.exec_()
                clicked = msg.clickedButton()

                if clicked == btn_save:
                    # Save to file
                    self.tab_widget.setCurrentIndex(index)
                    self._save_file_as()
                    # Check if actually saved (file_path set)
                    if not tab.file_path or tab.is_modified:
                        return False  # User cancelled save, don't close
                elif clicked == btn_clipboard:
                    # Copy to clipboard
                    clipboard = QApplication.clipboard()
                    clipboard.setText(tab.editor.toPlainText())
                    self.lbl_status.setText(tr("editor.status_copied"))
                elif clicked == btn_cancel:
                    return False
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
                        if not tab.file_path or tab.is_modified:
                            return False
                    else:
                        # Handle different tab types
                        if isinstance(tab, JsonEditorTab):
                            success, _ = tab.save_file()
                        else:
                            success = tab.save_file()

                        if not success:
                            return False  # Don't close if save failed
                elif reply == QMessageBox.Cancel:
                    return False

        if not self._discard_recovery_for_tab(tab):
            return False
        if tab is self._split_source_tab:
            self._close_split_view()
        self._discard_find_history(tab)
        self._clear_tab_disk_state(tab, refresh_watchers=False)
        for timer in tab.findChildren(QTimer):
            timer.stop()
        title = tab.get_tab_title()
        self.tab_widget.removeTab(index)
        self._renumber_untitled_tabs()
        tab.deleteLater()
        self._refresh_external_file_watchers()
        self.lbl_status.setText(f"Closed: {title}")
        self._refresh_editor_menus()
        self._persist_tab_order()
        return True

    def _on_tab_changed(self, index: int):
        """Handle tab change with edit-only mode indicators."""
        self._update_editor_status_indicators()
        if index >= 0:
            tab = self.tab_widget.widget(index)
            if self._find_session_is_visible():
                self._bind_find_session_to_active_editor()
            self._check_tab_external_state(tab)
            self._update_tab_title(tab)
            self._refresh_editor_menus()
            self._select_explorer_path(getattr(tab, "file_path", None))

            if self._show_external_status_for_current_tab():
                return

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
            self._shutdown_find_session()
            self._refresh_editor_menus()
            self.lbl_status.setText(tr("editor.lbl_status_ready"))
            self.lbl_status.setStyleSheet("color: #6A9955;")

    def _update_tab_title(self, tab: EditorTab):
        """Update tab title based on modified state."""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, self._display_title_for_tab(tab))
        if tab is self._split_source_tab:
            self.split_title.setText(self._display_title_for_tab(tab))
        if tab is self.tab_widget.currentWidget():
            self._update_editor_status_indicators()

    def _on_tab_mode_changed(self, tab: EditorTab):
        """Refresh title, status, and menu state after tab mode changes."""
        self._track_tab_disk_state(tab)
        self._update_tab_title(tab)
        index = self.tab_widget.indexOf(tab)
        if index == self.tab_widget.currentIndex():
            self._on_tab_changed(index)
        else:
            self._refresh_editor_menus()

    def _set_auto_save_enabled(self, enabled: bool):
        """Apply auto-save preference to the dock and all open tabs."""
        self.auto_save_enabled = enabled

        # Save preference to QSettings
        self.settings.setValue("auto_save_enabled", enabled)

        # Apply to all open tabs
        for i in range(self.tab_widget.count()):
            self._apply_auto_save_to_tab(self.tab_widget.widget(i))

        # Update status
        status_text = "Auto-save enabled" if enabled else "Auto-save disabled"
        self.lbl_status.setText(status_text)
        self._refresh_editor_menus()

    def _on_tab_recovery_state_changed(self, tab, modified: bool) -> None:
        """Schedule a snapshot for changed tabs or clear one after saving."""
        if modified:
            if not self._recovery_suspended:
                self._recovery_timer.start()
        else:
            self._discard_recovery_for_tab(tab)

    @Slot()
    def _on_recovery_timeout(self) -> None:
        if not self._recovery_suspended:
            self._checkpoint_unsaved_tabs()

    def _checkpoint_unsaved_tabs(self) -> bool:
        """Persist buffers or saved-file references, without unbounded extraction."""
        self._recovery_timer.stop()
        skipped = 0
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            if not hasattr(tab, "editor"):
                continue
            if (
                getattr(tab, "_clarify_temp_note_id", "")
                and not getattr(tab, "is_modified", False)
                and not tab.editor.document().isModified()
            ):
                self._discard_recovery_for_tab(tab)
                continue

            snapshot_id = getattr(tab, "_clarify_recovery_id", "")
            if not snapshot_id:
                snapshot_id = uuid.uuid4().hex
                setattr(tab, "_clarify_recovery_id", snapshot_id)

            display_name = getattr(
                tab, "_clarify_display_name", tab.get_tab_title()
            )
            extension = os.path.splitext(display_name)[1] or os.path.splitext(
                getattr(tab, "file_path", "") or ""
            )[1] or ".txt"
            try:
                file_path = getattr(tab, "file_path", "") or ""
                cursor = tab.editor.textCursor().position()
                if file_path and not getattr(tab, "is_modified", False):
                    self.recovery_store.save_reference(
                        snapshot_id, title=display_name, file_path=file_path,
                        extension=extension, cursor_position=cursor,
                        source_signature=getattr(tab, '_clarify_recovery_source_signature', None),
                    )
                else:
                    # Qt counts UTF-16 units. Reject huge documents before making a
                    # Python string; the store then checks the exact UTF-8 size.
                    if tab.editor.document().characterCount() - 1 > self.recovery_store.max_document_bytes:
                        raise RecoverySnapshotError("Document exceeds bounded extraction limit")
                    self.recovery_store.save(
                        snapshot_id, title=display_name, content=tab.editor.toPlainText(),
                        file_path=file_path or getattr(tab, '_clarify_recovery_source_path', ''),
                        extension=extension, cursor_position=cursor,
                    )
            except (RecoverySnapshotError, OSError, UnicodeError):
                skipped += 1

        self._recovery_failures = skipped
        if skipped:
            self.lbl_status.setText(
                tr("editor.status_recovery_skipped").format(count=skipped)
            )
            logging.getLogger(__name__).warning("Editor recovery checkpoint failed for %d document(s)", skipped)
        return skipped == 0

    def _discard_recovery_for_tab(self, tab) -> bool:
        """Discard a tab's local recovery snapshot when no longer needed."""
        snapshot_id = getattr(tab, "_clarify_recovery_id", "") if tab else ""
        if snapshot_id:
            try:
                self.recovery_store.discard(snapshot_id)
                self._restored_recovery_ids.discard(snapshot_id)
            except (OSError, RecoverySnapshotError):
                self.lbl_status.setText(tr("editor.status_recovery_skipped").format(count=1))
                return False
        return True

    def _flush_recovery_on_close(self, *, final=False) -> bool:
        """Normal close may be refused; final Qt shutdown can only report failure."""
        notes_saved = self._flush_temp_note_autosaves()
        recovery_saved = self._checkpoint_unsaved_tabs()
        success = notes_saved and recovery_saved
        if recovery_saved:
            self._save_folder_session()
        if success or final:
            self._recovery_suspended = True
            for timer in self.findChildren(QTimer):
                timer.stop()
            watched = self._file_watcher.files() + self._file_watcher.directories()
            if watched:
                self._file_watcher.removePaths(watched)
            self._watched_file_paths.clear()
            self._watched_dir_paths.clear()
            for index in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(index)
                if hasattr(tab, 'set_auto_save'):
                    tab.set_auto_save(False)
        return success

    def request_tab_close(self) -> bool:
        """Closing the whole tool keeps buffers; individual tab discard does not."""
        return self._flush_recovery_on_close()

    def closeEvent(self, event):
        if not self.request_tab_close():
            event.ignore()
            return
        self._shutdown_find_session()
        if getattr(self, "_status_translation_connected", False):
            try:
                get_translator().languageChanged.disconnect(
                    self._retranslate_editor_ui
                )
            except (RuntimeError, TypeError):
                pass
            self._status_translation_connected = False
        self._find_history_by_buffer.clear()
        super().closeEvent(event)

    def _pending_recovery_snapshots(self):
        """Return snapshots not already represented by this Editor instance."""
        try:
            snapshots, report = self.recovery_store.list_with_report()
            active_ids = {
                getattr(self.tab_widget.widget(index), "_clarify_recovery_id", "")
                for index in range(self.tab_widget.count())
            }
            active_ids.discard("")
            represented_ids = self._restored_recovery_ids | active_ids
            if report.removed or snapshots:
                self._last_recovery_prune_report = report
            self._recovery_already_open_count = sum(
                snapshot.snapshot_id in represented_ids for snapshot in snapshots
            )
            return [
                snapshot
                for snapshot in snapshots
                if snapshot.snapshot_id not in represented_ids
            ]
        except (OSError, RecoverySnapshotError):
            self._last_recovery_prune_report = RecoveryPruneReport()
            self._recovery_already_open_count = 0
            self.lbl_status.setText(tr("editor.recovery_store_unavailable"))
            return None

    def _recovery_empty_message(self) -> str:
        """Explain why the latest bounded recovery inventory is empty."""
        report = self._last_recovery_prune_report
        details = []
        if report.expired:
            details.append(
                tr("editor.recovery_reason_expired").format(count=report.expired)
            )
        if report.invalid:
            details.append(
                tr("editor.recovery_reason_invalid").format(count=report.invalid)
            )
        if report.over_quota:
            details.append(
                tr("editor.recovery_reason_quota").format(count=report.over_quota)
            )
        if self._recovery_already_open_count:
            details.append(
                tr("editor.recovery_reason_already_open").format(
                    count=self._recovery_already_open_count
                )
            )
        if not details:
            return tr("editor.recovery_none_message")
        return tr("editor.recovery_none_detailed_message").format(
            details="; ".join(details)
        )

    def _refresh_recovery_offer(self) -> bool:
        """Expose pending snapshots without blocking the Editor workspace."""
        snapshots = self._pending_recovery_snapshots()
        count = len(snapshots) if snapshots is not None else 0
        self.recovery_offer.setProperty("pending_count", count)
        self._retranslate_recovery_offer()
        visible = bool(count and not self._recovery_offer_dismissed)
        self.recovery_offer.setVisible(visible)
        return visible

    def _recover_pending_snapshots(self) -> int:
        """Restore every available pending snapshot as an unsaved tab."""
        snapshots = self._pending_recovery_snapshots()
        if snapshots is None:
            self.recovery_offer.hide()
            return 0
        recovered = sum(
            self._restore_recovery_snapshot(snapshot) is not None
            for snapshot in snapshots
        )
        failed = len(snapshots) - recovered
        self._recovery_offer_dismissed = False
        self._refresh_recovery_offer()
        if failed:
            self.lbl_status.setText(
                tr("editor.recovery_unavailable").format(count=failed)
            )
        else:
            self.lbl_status.setText(
                tr("editor.status_recovered_documents").format(count=recovered)
            )
        return recovered

    def _discard_pending_snapshots(self) -> int:
        """Discard only snapshots not represented by active tabs."""
        snapshots = self._pending_recovery_snapshots()
        if snapshots is None:
            self.recovery_offer.hide()
            return 0
        discarded = 0
        failures = 0
        for snapshot in snapshots:
            try:
                self.recovery_store.discard(snapshot.snapshot_id)
                discarded += 1
            except (OSError, RecoverySnapshotError):
                failures += 1
        self._recovery_offer_dismissed = False
        self._refresh_recovery_offer()
        if failures:
            self.lbl_status.setText(
                tr("editor.status_recovery_skipped").format(count=failures)
            )
        return discarded

    def _dismiss_recovery_offer(self) -> None:
        """Keep pending snapshots for a later explicit decision."""
        self._recovery_offer_dismissed = True
        self.recovery_offer.hide()

    def _show_recovery_dialog(self) -> None:
        """Offer to recover or discard all currently available snapshots."""
        snapshots = self._pending_recovery_snapshots()
        if snapshots is None:
            return
        if not snapshots:
            QMessageBox.information(
                self,
                tr("editor.recovery_none_title"),
                self._recovery_empty_message(),
            )
            return

        dialog = QMessageBox(self)
        dialog.setWindowTitle(tr("editor.recovery_dialog_title"))
        dialog.setText(
            tr("editor.recovery_dialog_message").format(count=len(snapshots))
        )
        recover_button = dialog.addButton(
            tr("editor.btn_recover_all"), QMessageBox.AcceptRole
        )
        discard_button = dialog.addButton(
            tr("editor.btn_discard_all"), QMessageBox.DestructiveRole
        )
        dialog.addButton(tr("editor.btn_cancel"), QMessageBox.RejectRole)
        dialog.exec_()

        if dialog.clickedButton() == discard_button:
            try:
                for snapshot in snapshots:
                    self.recovery_store.discard(snapshot.snapshot_id)
            except (OSError, RecoverySnapshotError):
                self.lbl_status.setText(tr("editor.status_recovery_skipped").format(count=1))
                return
            self._restored_recovery_ids.clear()
            self._recovery_offer_dismissed = False
            self._refresh_recovery_offer()
            return
        if dialog.clickedButton() != recover_button:
            return

        recovered = sum(self._restore_recovery_snapshot(snapshot) is not None for snapshot in snapshots)
        if recovered != len(snapshots):
            QMessageBox.warning(self, tr("editor.recovery_dialog_title"),
                                tr("editor.recovery_unavailable").format(count=len(snapshots) - recovered))
        self.lbl_status.setText(
            tr("editor.status_recovered_documents").format(count=recovered)
        )
        self._recovery_offer_dismissed = False
        self._refresh_recovery_offer()

    def _restore_recovery_snapshot(self, snapshot):
        """Restore one snapshot as an unsaved tab, never over its source file."""
        try:
            content = (self.recovery_store.read_reference(snapshot)
                       if snapshot.kind == "reference" else snapshot.content)
        except (RecoverySnapshotError, OSError):
            self.lbl_status.setText(tr("editor.recovery_unavailable").format(count=1))
            return None
        display_name = tr("editor.recovered_name").format(name=snapshot.title)
        tab = self.load_generated_content(
            content,
            display_name,
            extension=snapshot.extension,
        )
        if (
            not snapshot.file_path
            and self._is_legacy_untitled_title(snapshot.title)
        ):
            if hasattr(tab, "_clarify_display_name"):
                delattr(tab, "_clarify_display_name")
            self._renumber_untitled_tabs()
        setattr(tab, "_clarify_recovery_id", snapshot.snapshot_id)
        setattr(tab, "_clarify_recovery_source_path", snapshot.file_path)
        cursor = tab.editor.textCursor()
        cursor.setPosition(min(snapshot.cursor_position, tab.editor.document().characterCount() - 1))
        tab.editor.setTextCursor(cursor)
        self._restored_recovery_ids.add(snapshot.snapshot_id)
        return tab

    def _set_recovery_retention(self) -> None:
        """Let the user adjust snapshot retention from 1 hour to 30 days."""
        hours, accepted = QInputDialog.getInt(
            self,
            tr("editor.recovery_retention_title"),
            tr("editor.recovery_retention_message"),
            self.recovery_retention_hours,
            1,
            24 * 30,
        )
        if not accepted:
            return
        self.recovery_retention_hours = hours
        self.recovery_store.retention_hours = hours
        try:
            self.recovery_store.prune()
        except (OSError, RecoverySnapshotError):
            self.lbl_status.setText(tr("editor.status_recovery_skipped").format(count=1))
        self.settings.setValue("recovery_retention_hours", hours)

    def _open_temp_note_tab(self, note_id: str):
        return next(
            (
                tab
                for tab in self._all_tab_objects()
                if getattr(tab, "_clarify_temp_note_id", "") == note_id
            ),
            None,
        )

    @staticmethod
    def _temp_note_extension(tab) -> str:
        language_extension = getattr(tab, "_clarify_language_extension", "") or ""
        if language_extension.startswith(".") and len(language_extension) > 1:
            return language_extension
        candidates = (
            getattr(tab, "file_path", "") or "",
            getattr(tab, "_clarify_display_name", "") or "",
            tab.get_tab_title(),
        )
        return next(
            (os.path.splitext(value)[1] for value in candidates if os.path.splitext(value)[1]),
            ".txt",
        )

    def _ensure_temp_note_autosave_timer(self, tab) -> QTimer:
        timer = getattr(tab, "_clarify_temp_note_autosave_timer", None)
        if timer is None:
            timer = QTimer(tab)
            timer.setSingleShot(True)
            timer.setInterval(self.TEMP_NOTE_AUTOSAVE_INTERVAL_MS)
            timer.timeout.connect(lambda t=tab: self._autosave_temp_note(t))
            setattr(tab, "_clarify_temp_note_autosave_timer", timer)
        return timer

    def _autosave_temp_note(self, tab) -> bool:
        """Ignore queued timer delivery after conversion, deletion or close."""
        if (
            self._recovery_suspended
            or self.tab_widget.indexOf(tab) < 0
            or not getattr(tab, "_clarify_temp_note_id", "")
        ):
            return False
        return self._save_temp_note_tab(tab)

    def _schedule_temp_note_autosave(self, tab) -> None:
        if (
            not self._recovery_suspended
            and getattr(tab, "_clarify_temp_note_id", "")
            and self.tab_widget.indexOf(tab) >= 0
        ):
            self._ensure_temp_note_autosave_timer(tab).start()

    def _adopt_temp_note(self, tab, note) -> None:
        timer = self._ensure_temp_note_autosave_timer(tab)
        timer.stop()
        if hasattr(tab, "auto_save_timer"):
            tab.auto_save_timer.stop()
        tab.file_path = None
        setattr(tab, "_clarify_temp_note_id", note.note_id)
        setattr(tab, "_clarify_temp_note_title", note.title)
        setattr(tab, "_clarify_display_name", note.title)
        setattr(tab, "_clarify_language_extension", note.extension)
        setattr(tab, "_clarify_folder_root", "")
        for attribute in (
            "_clarify_folder_source_path",
            "_clarify_recovery_source_path",
            "_clarify_recovery_source_signature",
        ):
            if hasattr(tab, attribute):
                delattr(tab, attribute)
        if getattr(tab, "edit_only_mode", False):
            tab.edit_only_mode = False
            if hasattr(tab, "_update_visual_indicators"):
                tab._update_visual_indicators()
            if hasattr(tab, "_update_toolbar_visibility"):
                tab._update_toolbar_visibility()
        tab.is_modified = False
        tab.editor.document().setModified(False)
        self._clear_tab_disk_state(tab, refresh_watchers=False)
        if self._discard_recovery_for_tab(tab) and hasattr(
            tab, "_clarify_recovery_id"
        ):
            delattr(tab, "_clarify_recovery_id")
        if hasattr(tab, "modified_changed"):
            tab.modified_changed.emit(False)
        self._refresh_external_file_watchers()
        self._renumber_untitled_tabs()
        self._persist_tab_order()
        self._refresh_editor_menus()

    def _save_temp_note_tab(self, tab, *, title: str | None = None) -> bool:
        """Atomically save one bounded buffer while retaining note identity."""
        if tab is None or self.tab_widget.indexOf(tab) < 0 or not hasattr(tab, "editor"):
            return False
        timer = getattr(tab, "_clarify_temp_note_autosave_timer", None)
        if timer is not None:
            timer.stop()
        if tab.editor.document().characterCount() - 1 > self.temp_note_store.max_note_bytes:
            self.lbl_status.setText(tr("editor.status_temp_note_too_large"))
            return False
        note_id = getattr(tab, "_clarify_temp_note_id", "") or uuid.uuid4().hex
        note_title = title if title is not None else getattr(
            tab, "_clarify_temp_note_title", ""
        )
        if not str(note_title).strip():
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        try:
            note = self.temp_note_store.save(
                note_id,
                title=str(note_title),
                content=tab.editor.toPlainText(),
                extension=self._temp_note_extension(tab),
            )
        except (OSError, UnicodeError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        self._adopt_temp_note(tab, note)
        self.lbl_status.setText(
            tr("editor.status_temp_note_saved").format(title=note.title)
        )
        return True

    def _flush_temp_note_autosaves(self) -> bool:
        """Flush every pending note before any Editor or application close path."""
        success = True
        for tab in self._all_tab_objects():
            if not getattr(tab, "_clarify_temp_note_id", ""):
                continue
            timer = getattr(tab, "_clarify_temp_note_autosave_timer", None)
            pending = bool(timer is not None and timer.isActive())
            modified = bool(
                getattr(tab, "is_modified", False)
                or tab.editor.document().isModified()
            )
            if (pending or modified) and not self._save_temp_note_tab(tab):
                success = False
        return success

    def _finalize_temp_note_conversion(self, tab) -> bool:
        """Remove note storage only after Save As has written the normal file."""
        note_id = getattr(tab, "_clarify_temp_note_id", "")
        if not note_id:
            return True
        try:
            self.temp_note_store.discard(note_id)
        except (OSError, TemporaryNoteError):
            tab.file_path = None
            tab.is_modified = False
            tab.editor.document().setModified(False)
            if hasattr(tab, "auto_save_timer"):
                tab.auto_save_timer.stop()
            self._clear_tab_disk_state(tab)
            self._update_tab_title(tab)
            self._refresh_editor_menus()
            self.lbl_status.setText(
                tr("editor.status_temp_note_conversion_failure")
            )
            return False
        timer = getattr(tab, "_clarify_temp_note_autosave_timer", None)
        if timer is not None:
            timer.stop()
        for attribute in (
            "_clarify_temp_note_id",
            "_clarify_temp_note_title",
            "_clarify_display_name",
        ):
            if hasattr(tab, attribute):
                delattr(tab, attribute)
        return True

    def _save_current_as_temp_note(self, title: str | None = None) -> bool:
        """Adopt the current buffer as a private, autosaved temporary note."""
        tab = self.tab_widget.currentWidget()
        if tab is None or not hasattr(tab, "editor"):
            return False
        if title is None:
            default_title = getattr(tab, "_clarify_temp_note_title", "") or tab.get_tab_title()
            title, accepted = QInputDialog.getText(
                self,
                tr("editor.temp_note_title"),
                tr("editor.temp_note_title_prompt"),
                text=default_title,
            )
            if not accepted:
                return False
        return self._save_temp_note_tab(tab, title=title)

    def _restore_temp_note(self, note_id: str):
        """Open a note as an unsaved buffer, never as a normal file."""
        for tab in self._all_tab_objects():
            if getattr(tab, "_clarify_temp_note_id", "") == note_id:
                self.tab_widget.setCurrentWidget(tab)
                return tab
        try:
            note = self.temp_note_store.get(note_id)
        except (OSError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return None
        tab = self.load_generated_content(
            note.content,
            note.title,
            extension=note.extension,
        )
        self._adopt_temp_note(tab, note)
        self.lbl_status.setText(
            tr("editor.status_temp_note_restored").format(title=note.title)
        )
        return tab

    def _delete_temp_note(self, note_id: str, *, confirm: bool = True) -> bool:
        try:
            note = self.temp_note_store.get(note_id)
        except (OSError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        if confirm:
            reply = QMessageBox.question(
                self,
                tr("editor.temp_note_delete_title"),
                tr("editor.temp_note_delete_message").format(title=note.title),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False
        try:
            self.temp_note_store.discard(note_id)
        except (OSError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        for tab in self._all_tab_objects():
            if getattr(tab, "_clarify_temp_note_id", "") == note_id:
                delattr(tab, "_clarify_temp_note_id")
                if hasattr(tab, "_clarify_temp_note_title"):
                    delattr(tab, "_clarify_temp_note_title")
                timer = getattr(tab, "_clarify_temp_note_autosave_timer", None)
                if timer is not None:
                    timer.stop()
                tab.is_modified = True
                tab.editor.document().setModified(True)
                self._recovery_timer.start()
                if hasattr(tab, "modified_changed"):
                    tab.modified_changed.emit(True)
                self._update_tab_title(tab)
        self.lbl_status.setText(
            tr("editor.status_temp_note_deleted").format(title=note.title)
        )
        return True

    def _rename_temp_note(self, note_id: str, title: str) -> bool:
        tab = self._open_temp_note_tab(note_id)
        if tab is not None:
            return self._save_temp_note_tab(tab, title=title)
        try:
            note = self.temp_note_store.get(note_id)
            renamed = self.temp_note_store.save(
                note.note_id,
                title=title,
                content=note.content,
                extension=note.extension,
            )
        except (OSError, UnicodeError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        self.lbl_status.setText(
            tr("editor.status_temp_note_saved").format(title=renamed.title)
        )
        return True

    def _export_temp_note(self, note_id: str, file_path: str | None = None) -> bool:
        tab = self._open_temp_note_tab(note_id)
        if tab is not None and (
            getattr(tab, "is_modified", False) or tab.editor.document().isModified()
        ):
            if not self._save_temp_note_tab(tab):
                return False
        try:
            note = self.temp_note_store.get(note_id)
        except (OSError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        if file_path is None:
            file_path, _selected_filter = QFileDialog.getSaveFileName(
                self,
                tr("editor.btn_export"),
                f"{note.title}{note.extension}",
                "All Files (*)",
            )
        if not file_path:
            return False
        try:
            write_text_atomically(file_path, note.content)
        except (OSError, UnicodeError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        self.lbl_status.setText(
            tr("editor.status_temp_note_exported").format(
                name=os.path.basename(file_path)
            )
        )
        return True

    def _show_temp_notes_dialog(self) -> None:
        try:
            notes = self.temp_note_store.list()
        except (OSError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return
        if not notes:
            QMessageBox.information(
                self,
                tr("editor.temp_notes_title"),
                tr("editor.temp_notes_empty"),
            )
            return
        dialog = _TemporaryNotesDialog(notes, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        note_id = dialog.selected_note_id
        if dialog.requested_action == "restore":
            self._restore_temp_note(note_id)
        elif dialog.requested_action == "delete":
            self._delete_temp_note(note_id)
        elif dialog.requested_action == "rename":
            try:
                note = self.temp_note_store.get(note_id)
            except (OSError, TemporaryNoteError):
                self.lbl_status.setText(tr("editor.status_temp_note_failure"))
                return
            title, accepted = QInputDialog.getText(
                self,
                tr("editor.temp_note_title"),
                tr("editor.temp_note_title_prompt"),
                text=note.title,
            )
            if accepted:
                self._rename_temp_note(note_id, title)
        elif dialog.requested_action == "export":
            self._export_temp_note(note_id)

    def _set_temp_note_retention(self, days: int | None = None) -> bool:
        """Set optional updated-at retention; zero always means manual deletion."""
        if days is None:
            days, accepted = QInputDialog.getInt(
                self,
                tr("editor.temp_note_retention_title"),
                tr("editor.temp_note_retention_prompt"),
                self.temp_note_retention_days,
                0,
                3650,
            )
            if not accepted:
                return False
        days = max(0, min(3650, int(days)))
        try:
            expired = self.temp_note_store.expired(days)
        except (OSError, TemporaryNoteError):
            self.lbl_status.setText(tr("editor.status_temp_note_failure"))
            return False
        if expired:
            reply = QMessageBox.question(
                self,
                tr("editor.temp_note_retention_title"),
                tr("editor.temp_note_retention_confirm").format(count=len(expired)),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False
            try:
                self.temp_note_store.prune(days)
            except (OSError, TemporaryNoteError):
                self.lbl_status.setText(tr("editor.status_temp_note_failure"))
                return False
        self.temp_note_retention_days = days
        self.settings.setValue("temp_note_retention_days", days)
        self.lbl_status.setText(
            tr(
                "editor.status_temp_note_retention_manual"
                if days == 0
                else "editor.status_temp_note_retention_days"
            ).format(days=days)
        )
        return True

    def _set_show_line_numbers_enabled(self, enabled: bool):
        """Apply line-number visibility to the dock and all open tabs."""
        self.show_line_numbers_enabled = enabled
        self.settings.setValue("show_line_numbers_enabled", enabled)

        for i in range(self.tab_widget.count()):
            self._apply_line_numbers_to_tab(self.tab_widget.widget(i))

        status_text = tr("editor.status_line_numbers_shown") if enabled else tr("editor.status_line_numbers_hidden")
        self.lbl_status.setText(status_text)
        self._refresh_editor_menus()

    def _set_word_wrap_enabled(self, enabled: bool):
        """Apply word-wrap visibility to the dock and all open tabs."""
        self.word_wrap_enabled = enabled
        self.settings.setValue("word_wrap_enabled", enabled)

        for i in range(self.tab_widget.count()):
            self._apply_word_wrap_to_tab(self.tab_widget.widget(i))

        status_text = (
            tr("editor.status_word_wrap_enabled")
            if enabled
            else tr("editor.status_word_wrap_disabled")
        )
        self.lbl_status.setText(status_text)
        self._refresh_editor_menus()

    def _set_render_whitespace_enabled(self, enabled: bool):
        """Apply whitespace rendering to the dock and all open tabs."""
        self.render_whitespace_enabled = enabled
        self.settings.setValue("render_whitespace_enabled", enabled)

        for i in range(self.tab_widget.count()):
            self._apply_render_whitespace_to_tab(self.tab_widget.widget(i))

        status_text = (
            tr("editor.status_render_whitespace_enabled")
            if enabled
            else tr("editor.status_render_whitespace_disabled")
        )
        self.lbl_status.setText(status_text)
        self._refresh_editor_menus()

    def _on_auto_save_toggled(self, state):
        """Compatibility handler for older checkbox-based auto-save calls."""
        self._set_auto_save_enabled(state == Qt.Checked)

    def _on_auto_saved(self, tab: EditorTab):
        """Handle auto-save completion."""
        if hasattr(tab, 'file_path') and tab.file_path:
            self._track_tab_disk_state(tab)
            self._update_tab_title(tab)
            filename = os.path.basename(tab.file_path)
            self.lbl_status.setText(f"💾 Auto-saved: {filename}")

            # Reset status after 2 seconds
            QTimer.singleShot(2000, self, lambda: self._on_tab_changed(self.tab_widget.currentIndex()))

    def _load_recent_paths(self, settings_key: str) -> List[str]:
        """Load a bounded, normalized path list from QSettings."""
        raw_value = self.settings.value(settings_key, "", type=str)
        try:
            values = json.loads(raw_value) if raw_value else []
        except (TypeError, json.JSONDecodeError):
            values = []
        if not isinstance(values, list):
            return []

        paths: List[str] = []
        for value in values:
            if not isinstance(value, str) or len(value) > self.MAX_TYPED_PATH_CHARS:
                continue
            normalized = self._normalized_file_path(value)
            if normalized and normalized not in paths:
                paths.append(normalized)
            if len(paths) >= self.max_recent:
                break
        return paths

    def _store_recent_paths(self, settings_key: str, paths: List[str]) -> None:
        """Persist one bounded recent-path list as explicit JSON."""
        self.settings.setValue(
            settings_key,
            json.dumps(paths[: self.max_recent], ensure_ascii=False),
        )

    def _add_recent_path(self, path: str, *, folder: bool) -> None:
        """Add a normalized path to the appropriate MRU list."""
        normalized = self._normalized_file_path(path)
        if not normalized:
            return
        paths = self.recent_folders if folder else self.recent_files
        if normalized in paths:
            paths.remove(normalized)
        paths.insert(0, normalized)
        del paths[self.max_recent :]
        self._store_recent_paths("recent_folders" if folder else "recent_files", paths)

    def _add_recent_file(self, file_path: str) -> None:
        """Add a file to the persistent recent-files list."""
        self._add_recent_path(file_path, folder=False)

    def _add_recent_folder(self, folder_path: str) -> None:
        """Add a folder to the persistent recent-folders list."""
        self._add_recent_path(folder_path, folder=True)

    def _prune_recent_paths(self) -> None:
        """Remove stale entries without crossing the file/folder lists."""
        recent_files = [path for path in self.recent_files if os.path.isfile(path)]
        recent_folders = [
            path for path in self.recent_folders if os.path.isdir(path)
        ]
        if recent_files != self.recent_files:
            self.recent_files = recent_files
            self._store_recent_paths("recent_files", self.recent_files)
        if recent_folders != self.recent_folders:
            self.recent_folders = recent_folders
            self._store_recent_paths("recent_folders", self.recent_folders)

    @staticmethod
    def _recent_path_label(path: str) -> str:
        """Return a concise menu label while keeping the full path as tooltip."""
        name = Path(path).name or path
        return name.replace("&", "&&")

    def _populate_recent_menu(
        self,
        menu: QMenu,
        paths: List[str],
        opener,
        clear_handler,
    ) -> None:
        """Populate one bounded recent menu with fresh QAction instances."""
        menu.clear()
        if not paths:
            empty_action = menu.addAction(tr("editor.recent_none"))
            empty_action.setEnabled(False)
        else:
            for path in paths:
                action = menu.addAction(self._recent_path_label(path))
                action.setToolTip(path)
                action.triggered.connect(
                    lambda _checked=False, selected=path: opener(selected)
                )
        menu.addSeparator()
        clear_action = menu.addAction(tr("editor.clear_recent"))
        clear_action.setEnabled(bool(paths))
        clear_action.triggered.connect(clear_handler)

    def _refresh_recent_menus(self) -> None:
        """Prune stale entries and rebuild both recent-path menus."""
        self._prune_recent_paths()
        self._populate_recent_menu(
            self.menu_recent_files,
            self.recent_files,
            self.open_file_path,
            self._clear_recent_files,
        )
        self._populate_recent_menu(
            self.menu_recent_folders,
            self.recent_folders,
            self._open_recent_folder,
            self._clear_recent_folders,
        )

    def _clear_recent_files(self) -> None:
        """Clear only the recent-files history."""
        self.recent_files.clear()
        self._store_recent_paths("recent_files", self.recent_files)
        self._refresh_recent_menus()

    def _clear_recent_folders(self) -> None:
        """Clear only the recent-folders history."""
        self.recent_folders.clear()
        self._store_recent_paths("recent_folders", self.recent_folders)
        self._refresh_recent_menus()

    def _open_recent_folder(self, folder_path: str) -> bool:
        """Restore a recent Explorer root if it still exists."""
        normalized = self._normalized_file_path(folder_path)
        if not os.path.isdir(normalized):
            self._prune_recent_paths()
            self._refresh_recent_menus()
            return False
        if not self._set_explorer_root(normalized):
            return False
        self._add_recent_folder(normalized)
        self._set_explorer_visible(True)
        return True

    def open_file_path(self, file_path: str, edit_only: bool = False) -> bool:
        """
        Open file from external call (e.g., from search results).

        Public API method for integration with other tools.
        """
        normalized_path = self._normalized_file_path(file_path)
        if not normalized_path or not os.path.isfile(normalized_path):
            QMessageBox.warning(
                self, tr("editor.msg_file_not_found_title"),
                tr("editor.msg_file_not_found_msg").format(normalized_path or file_path)
            )
            return False

        # Check if already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            open_path = self._normalized_file_path(getattr(tab, 'file_path', None))
            if open_path and open_path == normalized_path:
                self.tab_widget.setCurrentIndex(i)
                return True

        # Create appropriate tab based on file extension
        tab = self._create_tab_for_file(normalized_path, edit_only)

        if tab.load_file(normalized_path):
            # If edit-only, disconnect from file
            if edit_only:
                tab.file_path = None

            self._prepare_tab_for_dock(tab)
            self._assign_tab_folder_root(tab)
            self.tab_widget.addTab(tab, self._display_title_for_tab(tab))
            self._renumber_untitled_tabs()
            if not edit_only:
                self._track_tab_disk_state(tab)
                self._update_tab_title(tab)
            self._apply_persisted_tab_order()
            self.tab_widget.setCurrentWidget(tab)
            self._refresh_editor_menus()

            if not edit_only:
                self._add_recent_file(normalized_path)

            editor_type = "JSON Editor" if isinstance(tab, JsonEditorTab) else "Text Editor"
            mode_text = " (Edit-Only)" if edit_only else ""
            self.lbl_status.setText(
                f"Opened in {editor_type}{mode_text}: {os.path.basename(normalized_path)}"
            )
            return True
        else:
            QMessageBox.critical(
                self,
                tr("editor_dock.error_title"),
                tr("editor.file_open_error").format(file=normalized_path),
            )
            tab.deleteLater()
            return False

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

    def load_generated_content(
        self,
        content: str,
        display_name: str = "Untitled.txt",
        *,
        extension: str | None = None,
        edit_only: bool = False,
    ):
        """
        Load generated tool output into a new editor tab.

        Unlike open_file_path(), this does not create or track a real file on
        disk. The optional extension controls the editor type used for syntax
        and JSON-specific behavior.
        """
        normalized_extension = (extension or os.path.splitext(display_name)[1] or ".txt").lower()
        if normalized_extension and not normalized_extension.startswith("."):
            normalized_extension = f".{normalized_extension}"

        if normalized_extension == ".json":
            tab = JsonEditorTab(None, self, edit_only_mode=edit_only)
        else:
            tab = EditorTab(None, self, edit_only_mode=edit_only)

        setattr(tab, "_clarify_display_name", display_name)
        setattr(tab, "_clarify_language_extension", normalized_extension)
        self._prepare_tab_for_dock(tab)
        tab.editor.setPlainText(content)
        tab.is_modified = not edit_only

        index = self.tab_widget.addTab(tab, self._display_title_for_tab(tab))
        self._renumber_untitled_tabs()
        self.tab_widget.setCurrentIndex(index)
        self._refresh_editor_menus()

        editor_type = "JSON Editor" if isinstance(tab, JsonEditorTab) else "Text Editor"
        mode_text = " (Edit-Only)" if edit_only else ""
        self.lbl_status.setText(f"Loaded generated content in {editor_type}{mode_text}: {display_name}")
        return tab
    
    def load_json_string(self, json_str: str):
        """
        Load JSON string content into a new normal-mode tab named 'Untitled.txt'.
        User can edit and save the content.
        
        Args:
            json_str: JSON string content to load
        """
        # Create new NORMAL-mode tab (not edit-only)
        tab = EditorTab(None, self, edit_only_mode=False)
        self._prepare_tab_for_dock(tab)
        
        # Set content using the underlying QTextEdit
        tab.editor.setPlainText(json_str)
        
        # Mark as modified so user knows to save
        tab.is_modified = True
        
        # Add tab with name "Untitled.txt"
        index = self.tab_widget.addTab(tab, "Untitled.txt")
        self._renumber_untitled_tabs()
        self.tab_widget.setCurrentIndex(index)
        self._refresh_editor_menus()
        
        self.lbl_status.setText("Content loaded from Format Converter")
