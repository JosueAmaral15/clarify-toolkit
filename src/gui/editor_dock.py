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
import os
from datetime import datetime
from typing import List

from PySide6.QtCore import QEvent, QObject, QRegularExpression, QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QInputDialog, QLineEdit, QMenuBar, QPushButton,
    QVBoxLayout, QWidget,
    QLabel, QFileDialog, QMessageBox, QTextEdit, QTabWidget,
    QCheckBox, QMenu, QApplication
)
from PySide6.QtGui import (
    QAction, QColor, QKeySequence, QPainter, QTextCursor, QTextDocument,
    QTextOption
)

from src.i18n.translator import tooltip_tr, tr

from .base_dock import BaseDock
from .json_editor_tab import JsonEditorTab
from .widgets import EditorTab


class _EditorFindDialog(QDialog):
    """Simple find/find-and-replace dialog for the active editor."""

    def __init__(self, editor, replace_enabled: bool = False, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.replace_enabled = replace_enabled

        title_key = "editor.find_replace_dialog_title" if replace_enabled else "editor.find_dialog_title"
        self.setWindowTitle(tr(title_key))
        self.setMinimumWidth(420)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel(tr("editor.lbl_find")))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)

        self.replace_input = QLineEdit()
        if self.replace_enabled:
            replace_layout = QHBoxLayout()
            replace_layout.addWidget(QLabel(tr("editor.lbl_replace")))
            replace_layout.addWidget(self.replace_input)
            layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        self.chk_case_sensitive = QCheckBox(tr("editor.chk_case_sensitive"))
        self.chk_whole_word = QCheckBox(tr("editor.chk_whole_word"))
        self.chk_regex = QCheckBox(tr("editor.chk_regex"))
        options_layout.addWidget(self.chk_case_sensitive)
        options_layout.addWidget(self.chk_whole_word)
        options_layout.addWidget(self.chk_regex)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

        btn_layout = QHBoxLayout()
        self.btn_find_next = QPushButton(tr("editor.btn_find_next"))
        btn_layout.addWidget(self.btn_find_next)

        if self.replace_enabled:
            self.btn_replace = QPushButton(tr("editor.btn_replace"))
            self.btn_replace_all = QPushButton(tr("editor.btn_replace_all"))
            btn_layout.addWidget(self.btn_replace)
            btn_layout.addWidget(self.btn_replace_all)

        btn_layout.addStretch()
        self.btn_close = QPushButton(tr("editor.btn_close"))
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self.btn_find_next.clicked.connect(self._find_next)
        self.find_input.returnPressed.connect(self._find_next)
        self.btn_close.clicked.connect(self.close)

        if self.replace_enabled:
            self.btn_replace.clicked.connect(self._replace_current)
            self.btn_replace_all.clicked.connect(self._replace_all)

    def _find_flags(self):
        flags = QTextDocument.FindFlags()
        if self.chk_case_sensitive.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.chk_whole_word.isChecked():
            flags |= QTextDocument.FindWholeWords
        return flags

    def _find_target(self):
        text = self.find_input.text()
        if not text:
            return None

        if not self.chk_regex.isChecked():
            return text

        options = QRegularExpression.PatternOptions()
        if not self.chk_case_sensitive.isChecked():
            options |= QRegularExpression.CaseInsensitiveOption

        regex = QRegularExpression(text, options)
        if not regex.isValid():
            self.lbl_status.setText(
                tr("editor.find_invalid_regex").format(error=regex.errorString())
            )
            return None
        return regex

    def _find_next(self) -> bool:
        target = self._find_target()
        if target is None:
            return False

        if self.editor.find(target, self._find_flags()):
            self.lbl_status.setText("")
            return True

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.setTextCursor(cursor)

        if self.editor.find(target, self._find_flags()):
            self.lbl_status.setText("")
            return True

        self.lbl_status.setText(tr("editor.find_no_matches"))
        return False

    @staticmethod
    def _is_word_char(character: str) -> bool:
        return bool(character) and (character.isalnum() or character == "_")

    def _selection_is_whole_word(self) -> bool:
        cursor = self.editor.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        text = self.editor.toPlainText()
        previous_char = text[start - 1] if start > 0 else ""
        next_char = text[end] if end < len(text) else ""
        return not self._is_word_char(previous_char) and not self._is_word_char(next_char)

    def _selection_matches_find_text(self) -> bool:
        find_text = self.find_input.text()
        selected_text = self.editor.textCursor().selectedText()

        if self.chk_whole_word.isChecked() and not self._selection_is_whole_word():
            return False

        if self.chk_regex.isChecked():
            target = self._find_target()
            if target is None:
                return False
            match = target.match(selected_text)
            return (
                match.hasMatch()
                and match.capturedStart() == 0
                and match.capturedEnd() == len(selected_text)
            )

        if self.chk_case_sensitive.isChecked():
            return selected_text == find_text
        return selected_text.lower() == find_text.lower()

    def _replace_current(self):
        if not self.find_input.text():
            return

        if not self.editor.textCursor().hasSelection() or not self._selection_matches_find_text():
            if not self._find_next():
                return

        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            self.lbl_status.setText(tr("editor.replace_one_complete"))

    def _replace_all(self):
        find_text = self.find_input.text()
        if not find_text:
            return

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.setTextCursor(cursor)

        count = 0
        target = self._find_target()
        if target is None:
            return

        while self.editor.find(target, self._find_flags()):
            cursor = self.editor.textCursor()
            if not cursor.hasSelection():
                break
            cursor.insertText(self.replace_input.text())
            count += 1

        self.lbl_status.setText(tr("editor.replace_all_complete").format(count=count))


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
        return super().eventFilter(watched, event)

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

    _ACTION_SPECS = {
        "new": {"text_key": "editor.btn_new"},
        "open": {"text_key": "editor.btn_open"},
        "save": {"text_key": "editor.btn_save"},
        "save_as": {"text_key": "editor.btn_save_as"},
        "compare_with_saved": {"text_key": "editor.btn_compare_with_saved"},
        "enable_saving": {"text_key": "editor.btn_enable_saving"},
        "export": {"text_key": "editor.btn_export"},
        "close_tab": {"text_key": "editor.btn_close_tab"},
        "auto_save": {"text_key": "editor.chk_auto_save", "checkable": True},
        "undo": {"text_key": "editor.btn_undo", "shortcut": QKeySequence.StandardKey.Undo},
        "redo": {"text_key": "editor.btn_redo", "shortcut": QKeySequence.StandardKey.Redo},
        "cut": {"text_key": "editor.btn_cut"},
        "copy": {"text_key": "editor.btn_copy"},
        "paste": {"text_key": "editor.btn_paste"},
        "delete": {"text_key": "editor.btn_delete", "shortcut": QKeySequence.StandardKey.Delete},
        "select_all": {"text_key": "editor.btn_select_all", "shortcut": QKeySequence.StandardKey.SelectAll},
        "find": {"text_key": "editor.btn_find"},
        "find_replace": {"text_key": "editor.btn_find_replace"},
        "go_to_line": {"text_key": "editor.btn_go_to_line", "shortcut": "Ctrl+G"},
        "duplicate_line": {"text_key": "editor.btn_duplicate_line", "shortcut": "Ctrl+D"},
        "toggle_line_comment": {"text_key": "editor.btn_toggle_line_comment", "shortcut": "Ctrl+/"},
        "indent": {"text_key": "editor.btn_indent", "shortcut": "Ctrl+]"},
        "outdent": {"text_key": "editor.btn_outdent", "shortcut": "Ctrl+["},
        "move_line_up": {"text_key": "editor.btn_move_line_up", "shortcut": "Alt+Up"},
        "move_line_down": {"text_key": "editor.btn_move_line_down", "shortcut": "Alt+Down"},
        "insert_datetime": {"text_key": "editor.btn_insert_datetime", "shortcut": "F5"},
        "trim_trailing_spaces": {"text_key": "editor.btn_trim_trailing_spaces"},
        "word_wrap": {"text_key": "editor.chk_word_wrap", "checkable": True},
        "render_whitespace": {"text_key": "editor.chk_render_whitespace", "checkable": True},
        "show_line_numbers": {"text_key": "editor.chk_show_line_numbers", "checkable": True},
        "small_text": {"text_key": "editor.btn_small_text"},
        "large_text": {"text_key": "editor.btn_large_text"},
        "normal_size": {"text_key": "editor.btn_normal_size"},
    }

    _MENU_SPECS = {
        "file": {
            "attr": "menu_file",
            "title_key": "editor.menu_file",
            "items": (
                "new", "open", "save", "save_as", "compare_with_saved",
                "enable_saving", "export", "close_tab", None, "auto_save",
            ),
        },
        "edit": {
            "attr": "menu_edit",
            "title_key": "editor.menu_edit",
            "items": (
                "undo", "redo", None, "cut", "copy", "paste", "delete",
                "select_all", None, "find", "find_replace", "go_to_line",
                None, "duplicate_line", "toggle_line_comment", "indent",
                "outdent", "move_line_up", "move_line_down",
                "insert_datetime", "trim_trailing_spaces",
            ),
        },
        "view": {
            "attr": "menu_view",
            "title_key": "editor.menu_view",
            "items": (
                "word_wrap", "render_whitespace", "show_line_numbers",
                None, "small_text", "large_text", "normal_size",
            ),
        },
    }

    _ACTION_ENABLE_RULES = {
        "save": "has_tab",
        "save_as": "has_tab",
        "compare_with_saved": "has_file_path",
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
    }

    _ACTION_CHECKED_ATTRIBUTES = {
        "auto_save": "auto_save_enabled",
        "word_wrap": "word_wrap_enabled",
        "render_whitespace": "render_whitespace_enabled",
        "show_line_numbers": "show_line_numbers_enabled",
    }

    def __init__(self, parent=None):
        # Initialize attributes BEFORE super().__init__() which calls _setup_ui()
        self.recent_files: List[str] = []
        self.max_recent = 10
        self.untitled_counter = 0  # Counter for Untitled-N tabs
        self.normal_text_font_size = 10
        self.min_text_font_size = 6
        self.max_text_font_size = 48

        # Load auto-save preference from QSettings
        from PySide6.QtCore import QSettings
        self.settings = QSettings("Clarify", "EditorDock")
        self.auto_save_enabled = self.settings.value("auto_save_enabled", False, type=bool)
        self.show_line_numbers_enabled = self.settings.value("show_line_numbers_enabled", False, type=bool)
        self.word_wrap_enabled = self.settings.value("word_wrap_enabled", True, type=bool)
        self.render_whitespace_enabled = self.settings.value("render_whitespace_enabled", False, type=bool)

        # NOW call super().__init__() which triggers _setup_ui()
        super().__init__("Clarify Editor", parent)

    def _setup_ui(self):
        """Setup UI components."""
        # Toolbar
        toolbar = QHBoxLayout()

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
        self._refresh_editor_menus()

        toolbar.addWidget(self.menu_bar)
        toolbar.addStretch()

        self.layout.addLayout(toolbar)

        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.layout.addWidget(self.tab_widget)

        # Status bar
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel(tr("editor.lbl_status_ready"))
        self.lbl_status.setStyleSheet("color: #6A9955;")
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        self.layout.addLayout(status_layout)

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

        # Tab Widget
        self.tab_widget.setToolTip(tooltip_tr("editor.tab_widget"))

        # Status Label
        self.lbl_status.setToolTip(tooltip_tr("editor.lbl_status"))

    def _connect_signals(self):
        """Connect widget signals."""
        handlers = self._action_signal_handlers()
        missing_handlers = set(self._action_by_id) - set(handlers)
        if missing_handlers:
            missing_text = ", ".join(sorted(missing_handlers))
            raise RuntimeError(f"Editor action(s) missing handler: {missing_text}")

        for action_id, handler in handlers.items():
            self._action_by_id[action_id].triggered.connect(handler)

        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Context menu on tabs
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self._show_tab_context_menu)

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
        if hasattr(tab, 'toolbar'):
            tab.toolbar.setVisible(False)

        if hasattr(tab, 'modified_changed'):
            tab.modified_changed.connect(lambda _modified=False, t=tab: self._update_tab_title(t))
        if hasattr(tab, 'edit_only_changed'):
            tab.edit_only_changed.connect(lambda _enabled=False, t=tab: self._on_tab_mode_changed(t))

        self._apply_auto_save_to_tab(tab)
        self._apply_word_wrap_to_tab(tab)
        self._apply_render_whitespace_to_tab(tab)
        self._apply_line_numbers_to_tab(tab)

    def _setup_file_menu(self) -> None:
        """Create the local File menu bar actions."""
        self._setup_editor_menu("file")

    def _setup_edit_menu(self) -> None:
        """Create the local Edit menu bar actions."""
        self._setup_editor_menu("edit")

    def _setup_view_menu(self) -> None:
        """Create the local View menu bar actions."""
        self._setup_editor_menu("view")

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

        shortcut = spec.get("shortcut")
        if shortcut is not None:
            if isinstance(shortcut, str):
                shortcut = QKeySequence(shortcut)
            action.setShortcut(shortcut)

        setattr(self, f"action_{action_id}", action)
        self._action_by_id[action_id] = action
        return action

    def _action_signal_handlers(self):
        """Return QAction handlers keyed by action id."""
        return {
            "new": lambda _checked=False: self._new_file(),
            "open": lambda _checked=False: self._open_file(),
            "save": lambda _checked=False: self._save_file(),
            "save_as": lambda _checked=False: self._save_file_as(),
            "compare_with_saved": lambda _checked=False: self._compare_current_tab_with_saved(),
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
            "find": lambda _checked=False: self._show_find_dialog(False),
            "find_replace": lambda _checked=False: self._show_find_dialog(True),
            "go_to_line": lambda _checked=False: self._show_go_to_line_dialog(),
            "duplicate_line": lambda _checked=False: self._duplicate_current_line_or_selection(),
            "toggle_line_comment": lambda _checked=False: self._toggle_line_comment_current_tab(),
            "indent": lambda _checked=False: self._indent_current_lines(),
            "outdent": lambda _checked=False: self._outdent_current_lines(),
            "move_line_up": lambda _checked=False: self._move_current_lines(-1),
            "move_line_down": lambda _checked=False: self._move_current_lines(1),
            "insert_datetime": lambda _checked=False: self._insert_datetime_current_tab(),
            "trim_trailing_spaces": lambda _checked=False: self._trim_trailing_spaces_current_tab(),
            "word_wrap": lambda checked: self._set_word_wrap_enabled(checked),
            "render_whitespace": lambda checked: self._set_render_whitespace_enabled(checked),
            "show_line_numbers": lambda checked: self._set_show_line_numbers_enabled(checked),
            "small_text": lambda _checked=False: self._change_current_text_size(-1),
            "large_text": lambda _checked=False: self._change_current_text_size(1),
            "normal_size": lambda _checked=False: self._set_current_text_size(self.normal_text_font_size),
        }

    def _refresh_editor_menus(self) -> None:
        """Refresh File/Edit menu action states for the current tab."""
        tab = self.tab_widget.currentWidget() if hasattr(self, 'tab_widget') else None
        context = {
            "has_tab": tab is not None,
            "has_editor": tab is not None and hasattr(tab, 'editor'),
            "has_file_path": tab is not None and bool(getattr(tab, 'file_path', None)),
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
        self._prepare_tab_for_dock(tab)

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
            QMessageBox.critical(
                self, tr("editor.file_open_error_title"),
                tr("editor.file_open_error").format(file=file_path)
            )
            return

        # If edit-only, disconnect from file
        if edit_only:
            tab.file_path = None  # Disconnect from file

        self._prepare_tab_for_dock(tab)

        # Use display title (includes JSON icon if JSON file, 🔒 if edit-only)
        index = self.tab_widget.addTab(tab, tab.get_display_title())
        self.tab_widget.setCurrentIndex(index)
        self._refresh_editor_menus()

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
                QMessageBox.critical(self, tr("editor.msg_error_title"), tr("editor.msg_save_failed").format(error_msg))
        else:
            # EditorTab
            if tab.save_file():
                self._update_tab_title(tab)
                self.lbl_status.setText(f"Saved: {os.path.basename(tab.file_path)}")
            else:
                QMessageBox.critical(
                    self, tr("editor.msg_error_title"),
                    tr("editor.msg_save_failed_path").format(tab.file_path)
                )

    def _save_file_as(self):
        """Save current file with new name."""
        tab = self.tab_widget.currentWidget()
        if not tab:
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
                self._update_tab_title(tab)
                self.lbl_status.setText(f"Saved as: {os.path.basename(file_path)}")
                self._refresh_editor_menus()
                return True
            else:
                QMessageBox.critical(self, tr("editor.msg_error_title"), tr("editor.msg_save_failed").format(error_msg))
                return False
        else:
            # EditorTab
            if tab.save_file(file_path):
                self._update_tab_title(tab)
                self.lbl_status.setText(f"Saved as: {os.path.basename(file_path)}")
                self._refresh_editor_menus()
                return True
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
            return

        tab.editor.redo()
        self.lbl_status.setText(tr("editor.status_redone"))

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
    def _replace_editor_text(editor, new_text: str, cursor_position: int = 0) -> None:
        """Replace editor text as a single undoable edit and restore cursor position."""
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.insertText(new_text)
        cursor.endEditBlock()
        cursor.setPosition(max(0, min(cursor_position, len(new_text))))
        editor.setTextCursor(cursor)

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
        """Indent current or selected lines by four spaces."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        editor = tab.editor
        lines, start_line, end_line = self._selected_line_range(editor)
        for index in range(start_line, end_line + 1):
            lines[index] = "    " + lines[index]

        self._replace_editor_text(
            editor,
            "".join(lines),
            self._line_start_position(lines, start_line) + 4,
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

        editor = tab.editor
        lines, start_line, end_line = self._selected_line_range(editor)
        for index in range(start_line, end_line + 1):
            lines[index] = self._outdent_line(lines[index])[0]

        self._replace_editor_text(
            editor,
            "".join(lines),
            self._line_start_position(lines, start_line),
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
        """Show find or find-and-replace dialog for the current editor."""
        tab = self.tab_widget.currentWidget()
        if not tab or not hasattr(tab, 'editor'):
            return

        dialog = _EditorFindDialog(tab.editor, replace_enabled, self)
        dialog.exec()

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

    def _enable_saving_current_tab(self):
        """Convert the current edit-only tab into a file-backed tab."""
        tab = self.tab_widget.currentWidget()
        if not tab or not getattr(tab, 'edit_only_mode', False):
            return

        if hasattr(tab, '_enable_file_saving'):
            tab._enable_file_saving()
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

        self._refresh_editor_menus()

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
                    if not tab.file_path:
                        return  # User cancelled save, don't close
                elif clicked == btn_clipboard:
                    # Copy to clipboard
                    clipboard = QApplication.clipboard()
                    clipboard.setText(tab.editor.toPlainText())
                    self.lbl_status.setText(tr("editor.status_copied"))
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
        self._refresh_editor_menus()

    def _on_tab_changed(self, index: int):
        """Handle tab change with edit-only mode indicators."""
        self._refresh_editor_menus()
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
            self.lbl_status.setText(tr("editor.lbl_status_ready"))
            self.lbl_status.setStyleSheet("color: #6A9955;")

    def _update_tab_title(self, tab: EditorTab):
        """Update tab title based on modified state."""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, tab.get_display_title())

    def _on_tab_mode_changed(self, tab: EditorTab):
        """Refresh title, status, and menu state after tab mode changes."""
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
            QMessageBox.warning(
                self, tr("editor.msg_file_not_found_title"),
                tr("editor.msg_file_not_found_msg").format(file_path)
            )
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

            self._prepare_tab_for_dock(tab)
            index = self.tab_widget.addTab(tab, tab.get_display_title())
            self.tab_widget.setCurrentIndex(index)
            self._refresh_editor_menus()

            if not edit_only:
                self._add_recent_file(file_path)

            editor_type = "JSON Editor" if isinstance(tab, JsonEditorTab) else "Text Editor"
            mode_text = " (Edit-Only)" if edit_only else ""
            self.lbl_status.setText(f"Opened in {editor_type}{mode_text}: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, tr("editor_dock.error_title"), f"Failed to open file:\n{file_path}")

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
        self.tab_widget.setCurrentIndex(index)
        self._refresh_editor_menus()
        
        self.lbl_status.setText("Content loaded from Format Converter")
