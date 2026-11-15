#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=no-name-in-module  # PySide6 uses dynamic module structure
# pylint: disable=import-outside-toplevel  # Intentional lazy loading to avoid circular imports
# pylint: disable=broad-exception-caught  # UI code needs broad exception handling
# pylint: disable=too-few-public-methods  # Simple utility classes are acceptable
# pylint: disable=missing-class-docstring  # Qt stub classes don't need docstrings
# pylint: disable=missing-function-docstring  # Internal Qt wrappers
# pylint: disable=invalid-name  # Qt naming conventions (_PYSIDE, Qt, Signal)
# pylint: disable=logging-fstring-interpolation  # F-strings clearer than lazy %
# pylint: disable=redefined-outer-name  # Local loggers in methods acceptable

"""
TextWorkbench — GUI + CLI for project-wide search/replace/insert + JSON translate/dedupe
----------------------------------------------------------------------------------------
function: character search, replacement, and organization program.
Author: Josué Amaral
Date: 2025/10/01

This program combines:
  1) VS-Code–like Search panel (case/whole-word/regex, include/exclude globs).
  2) Replace (single / replace-all) with preserve-case.
  3) Conditional filtering when operating on folders (filename/path/extension/size/mtime with operators).
  4) Insert text at a specific line with 5 placement modes.
  5) Tools → JSON Translate (map texts using a JSON/TS dictionary file).
  6) Tools → JSON Rewriter (dedupe identical pairs, optionally join keys, optionally eliminate
     globally duplicated values; supports TS/JS object literals and pure JSON). Includes:
        --join-keys, --eliminate-duplicates, --no-line-break, --from-ts, --ts-out, --indent, etc.
  7) CLI subcommands for headless processing (search/replace/insert/translate/dedupe).

Run with a GUI (default) or with subcommands for CLI-only processing.

Dependencies:
  - PySide6 (GUI). The CLI works without PySide6 if you run subcommands only.
  - Pure standard library for the rest.

New in this version:
  • Insert panel now has Advanced Conditions (including `content`).
  • Menu bar: File→Exit, About (single action), Themes→Light/Dark/System.

Run GUI:
    python clarify.py

Run CLI examples:
    python clarify.py search  ./src  --query "foo" --include "*.ts;*.tsx" --cond "ext:equals:ts"
    python clarify.py replace ./src  --query "foo" --replacement "bar" --all
    python clarify.py insert  ./src  --line 1 --text "HEADER" --mode insert_above \
        --cond "content:contains:React" --include "*.tsx"
    python clarify.py translate ./web --dictionary dict.ts
    python clarify.py dedupe en.ts --from-ts --join-keys --eliminate-duplicates --no-line-break -o en2.ts --indent 2

Programming Tasks:
    See docs/TASKS.md for complete list of programming tasks organized by priority
    (MUST HAVE, SHOULD HAVE, COULD HAVE, WOULD HAVE LATER).

    Key completed features:
    - [X] Thread-based file search
    - [X] Case/whole-word/regex search with preserve-case replacement
    - [X] Advanced conditional filtering (filename, path, ext, size, mtime, content)
    - [X] 5 insertion modes with conditional filters
    - [X] JSON Translate with scope support and placeholder protection
    - [X] JSON Rewriter with dedupe/join/eliminate + CRITICAL BUG FIX for Obj type
"""

from __future__ import annotations
from base64 import b64decode
import configparser
import json
import os
import sys
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
#  Import organized modules (eliminates code duplication)
# ---------------------------------------------------------------------------

# Logging system
from .utils.logger import get_logger

# Error handling & crash reporting (v2.9.61)
# (install_crash_handler removed - unused)

# Core functionality: search, replace, insert, filtering
# (All removed - unused in app.py, only used by imported modules)

# Utilities: file operations, text processing, TypeScript/JavaScript
from .utils import read_text

# JSON Rewriter: types, parser, operations, serializer (includes BUG FIX)
from .rewriter import find_object_block, ts_block_to_json_text

# Case Converter: application theming (light, dark, system)
# (JSObjectCaseConverter removed - unused)

# Theme Manager: application theming (light, dark, system)
from .theme_manager import ThemeManager

# Internationalization: runtime language switching (Task #24 - v2.9.10)
from .i18n import switch_language, tr, tooltip_tr
from .product_identity import EDITOR_NAME, PRODUCT_NAME

# JSON Search: search keys and values in JSON/TS/TSX files
# (All removed - unused in app.py)

# Text Extractor: Now fully integrated in TextExtractorDock (no separate module needed)

# Placeholder Replacer: batch text replacement with mappings
# (All removed - unused in app.py)

# AI Processor: OpenAI and Gemini integration for file processing
# (process_file removed - unused)

# Modular GUI Docks: hierarchical architecture with base classes and mixins
from .gui import DockFactory, MenuBuilder, WindowSettings

# Progress Management: widgets for displaying task progress (v2.9.114 - Phase 1.1)
# (All removed - unused in app.py)

# Search/Replace/Insert Panels: worker and components (v2.9.114 - Phase 1.2 & 1.3)
from .gui.panels import InsertPanel

# CLI Module: command-line interface handlers (v2.9.114 - Phase 3.1)
from .cli import build_parser

# JSON Translate Helpers: dictionary-driven translation (v2.9.114 - Phase 3.2)
# (All removed - unused in app.py)

# Initialize logger after all imports
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
#  Optional import of PySide6 (the CLI subcommands work even if PySide6 is missing)
# ---------------------------------------------------------------------------

_PYSIDE = True

try:
    from PySide6.QtCore import QByteArray, QEvent, Qt
    from PySide6.QtGui import QAction, QFontDatabase, QPixmap, QIcon
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QDockWidget, QMessageBox
    )
except Exception:
    _PYSIDE = False
    # Create stub classes for when PySide6 is not available
    class QAbstractListModel:
        pass

    class QAbstractTableModel:
        pass

    class QWidget:
        pass

    class QMainWindow:
        pass

    class QObject:
        pass

    class QThread:
        pass

    QModelIndex = None
    Qt = None
    Signal = None


# =============================================================================
#                    THREAD MANAGER & PROCESSING MODAL IMPORTS
# =============================================================================

# Removed unused imports: thread_manager, FeatureType, ProcessingModal (COM4 - 2026-01-29)

# =============================================================================
#                    JSON TRANSLATE HELPERS (not yet in modules)
# =============================================================================

CONFIG_PATH = os.path.expanduser("~/.config/clarify.conf")

def load_prefs() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        cfg.read(CONFIG_PATH)
    return cfg

def save_prefs(cfg: configparser.ConfigParser):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            cfg.write(f)
        logger.debug(f"Preferences saved to {CONFIG_PATH}")
    except (IOError, OSError, PermissionError) as e:
        logger.error(f"Failed to save preferences to {CONFIG_PATH}: {e}")
        raise RuntimeError(f"Cannot save preferences: {e}") from e


# =============================== Utility: theming ===============================
# Theme functions delegated to ThemeManager for better organization

def apply_theme(app: QApplication, mode: str):
    """
    Apply theme to application.
    mode: "system" | "light" | "dark"
    """
    ThemeManager.apply_theme(app, mode)

# =============================================================================
#                   JSON REWRITER (dedupe / join / eliminate)
#        (condensed, self-contained port of your earlier CLI implementation)
# =============================================================================

def read_translation_dict(path: str) -> Dict[str, Any]:
    text = read_text(path)
    if path.lower().endswith(".json"):
        return json.loads(text)
    # TS/JS object literal — find largest {…:…} block and coerce to JSON-ish
    _start, _end, block = find_object_block(text)
    block_json = ts_block_to_json_text(block)
    return json.loads(block_json)

# =============================================================================
#                                CLI SUBCOMMANDS
# =============================================================================

# NOTE: CLI commands refactored to src/cli/commands.py (v2.9.114)
# Original implementations removed - see git history if needed



# =============================================================================
#                                   GUI
# =============================================================================

if _PYSIDE:
    # ResultsTree removed - unused (COM4)

    def _restore_qt_window_flags(window, desired_flags) -> bool:
        """
        Restore Qt window flags while preserving visibility and window state.

        setWindowFlags() hides the window and can drop maximized/fullscreen state
        on some Linux window managers, so restore the state explicitly.
        """
        if window.windowFlags() == desired_flags:
            return False

        was_visible = window.isVisible()
        window_state = window.windowState()

        window.setWindowFlags(desired_flags)
        window.setWindowState(window_state)

        if was_visible:
            if window_state & Qt.WindowFullScreen:
                window.showFullScreen()
            elif window_state & Qt.WindowMaximized:
                window.showMaximized()
            elif window_state & Qt.WindowMinimized:
                window.showMinimized()
            else:
                window.show()

        return True

    # ============================ Code-aware JSON Translator ============================
    # CodeAwareJSONTranslator removed - unused (COM4 - 2026-01-29)
    class MainWindow(QMainWindow):
        def __init__(self, app: QApplication):
            super().__init__()

            # Initialize attributes (prevent pylint warnings)
            self.ICON_BASE_64 = None
            self.tab_search = None
            self.dock_file_explorer = None
            self.tab_insert = None
            self.dock_text_to_json = None
            self.dock_set_operations = None
            self.dock_calculator = None
            self.dock_formula_builder = None
            self.dock_advanced_extractor = None
            self.dock_editor = None
            self.dock_clock = None
            self.dock_terminal = None
            self.dock_lynx = None
            self.dock_information_structure = None
            self.dock_editorial_repair = None
            self.dock_boolean_logic = None
            self.dock_voice_programming = None
            self.dock_algorithm_analysis = None
            self.tool_tabs = {}
            self._restoring_tabs = True
            self.resize(1200, 800)

            # Fix: Configure window flags for Linux compatibility (v2.9.117)
            # Linux window managers (X11/Wayland) require explicit WindowMaximizeButtonHint
            # to show the maximize button [□] in the title bar alongside [_] and [×]

            # Store desired window flags for restoration later (prevent QDockWidget interference)
            self._desired_window_flags = (
                Qt.Window |
                Qt.WindowMinimizeButtonHint |
                Qt.WindowMaximizeButtonHint |
                Qt.WindowCloseButtonHint
            )
            self.setWindowFlags(self._desired_window_flags)

            # Initialize all core systems using InitializationManager (Phase 3.7)
            from .gui.initialization_manager import InitializationManager
            InitializationManager.initialize_all(self, app)

            # Install global event filter for Shift+Scroll horizontal scrolling (v2.9.115)
            app.installEventFilter(self)

            # Force UI update to ensure widgets are properly rendered (fix for invisible widgets on startup)
            self.updateGeometry()
            QApplication.processEvents()

            # Apply accessibility features (v2.9.35)
            self._apply_accessibility()

            # Restore tab state from previous session (v2.9.40)
            self._restore_tab_state()
            self._register_docks_with_layout_manager()
            self.layout_manager.restore_last_layout()

            # Force initialization of all tabs to prevent lazy rendering issues
            # Qt doesn't render widgets in non-visible tabs until they're activated
            # This causes invisible widgets bug - force show all tabs once
            # Must be called AFTER _restore_tab_state() to initialize all tabs including restored ones
            self._initialize_all_tabs()

            # Auto-check for updates on startup (v2.9.45)
            self._auto_check_for_updates()

            # Nice monospaced font for preview-ish widgets
            try:
                f = QFontDatabase.systemFont(QFontDatabase.FixedFont)
                self.tab_search.set_editor_fonts(f)
                self.insert_panel.ed_text.setFont(f)
            except Exception:
                pass

        def _build_icon(self):
            """Load application icon from assets directory."""
            try:
                from pathlib import Path

                # Try to load the new SVG icon first
                icon_path = Path(__file__).parent.parent / "assets" / "icons" / "icon.svg"
                if icon_path.exists():
                    icon = QIcon(str(icon_path))
                    self.setWindowIcon(icon)
                    return

                # Fallback to PNG if SVG not supported
                icon_path = Path(__file__).parent.parent / "assets" / "icons" / "icon.png"
                if icon_path.exists():
                    icon = QIcon(str(icon_path))
                    self.setWindowIcon(icon)
                    return

                # Final fallback to embedded base64 icon (legacy)
                self._build_icon_fallback()

            except Exception as exc:
                logger.warning(f"Error loading icon from assets: {exc}")
                self._build_icon_fallback()

        def _build_icon_fallback(self):
            """Fallback icon loading using base64 (legacy)."""
            self.ICON_BASE_64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAD40lEQVR4nO2bv07cMBzHv3HSgzu6sB/qTFk6FfUB+gCor4FUqVIXJCYkhiJVQuI1EN07dKyuLJUQYka6vUt7R6+J3eFwznFsx0ns5HLcd7kj/hN/P/7ZTnw4QIFe7O6zojzLrPu7UWBK1yZ23bgsHQjlRZV5xhiArjAJEAR5ayoImQtq4xSMMTCazCGwJYcQzM0HJJx/BiSXRQQR6WtioJSCJgloEuNhOvPSXl/a7PdAwggkDEEIgW60p1ezvc9AE4oknmE6+eu7rV7VH2wgjHogYRYCjwICrK55AJhO/iKJZ6AJhTiHcc+5AULp6pjnSiFQmksLxN5njCKJY0x+TxptYFMaPB8gjKLMxJiJAMYYaBI33rCmRJP4cTlfKAXAl7plm+3Hp2Nn5R+ms8Vy/ihhGWQ5OiZtX+7j17tRrcbZipsYHg1Ll5G1eKCbrwhESrWqfPtyP/PZlGyjwZhP8mh4EFJLNt1kJADmaKgyXNJVgDGK5N8Mkz8P2symHi+CsP31u77s2zfp97ImhkfD0mV2P71MV4JSAAA1BJ15k2mdbq53rPOKUVAGQi0AQBaCyrzKuNjLZfLLxmwmQlOZwdYmwme9egAA/dgXzYimrw5vlfUcXOwZy4tmqq4CXgCoJDdeZ1onDkOs5+Z6p5RxWePTcTMAeKN5r5c1zyVGhFynC3kBYGNeDnWuoryuIcgA8tslJSVPYLKhg4s9rXldugpKlRXFRrUBcKnGvMm4LDGv+N1l+KtUawiI4VnHfNl71ZHzIaCSa/M+5QVAl1QZgC78ffU+D33Xk+E6AtpuQNtaA2i7AW1rDcBFJeLMX/UlqC1VBuBrWdLJx5sh4GkIdCkKnAGweaMr0tXhbePwagGQh0EdCGJeuZyv8AccRoAJggmEKp3XcXJ27n2O8bIjBNTfEjs5O0+vfX71enl3hAD1ilDlpUhlHgA+/PxRo3Vm5SJg48u3XCZb+rotccB+W5zXozJ9/PG9VTtMKtwUrQMA0D8XVIHoA4IMQPvjqO+9OFG6X4aOkR8OJ2fnTiKBSxsBLgBUmcFV95UhANUjwXoIuIoAGwg291JBAMqDaA2Ai/pcQGhkV9iXXI59rk4B8KHOAZCjoG5UlP4foWWQy6HQuQhwrTWAzF+KUxYrJ8mjAEB9zGTVNPe48EnEhICEbbSpMW32e+lRGq7MEFj1CCBhlPMY3d+N0sdh1QGjsmpqm7ys+oMNkDDMeLy/GwXa5wDT5kbXlJ4bIvkOjoA5CVcHJZcNVtGhKcO5wdU9Nmd5bjAAeZwxSRhiK4pW5uBkJrvq4pM9OivqSR+eFtV1EEXH5/8DsBV3DcmuUHgAAAAASUVORK5CYII="
            try:
                # 2. Decode Base64 string to bytes
                icon_data = b64decode(self.ICON_BASE_64)

                # 3. Load the image bytes into a QPixmap
                pixmap = QPixmap()
                if not pixmap.loadFromData(QByteArray(icon_data)):
                    logger.error("Error loading QPixmap icon data.")
                    # Handle the error, perhaps use a default icon or stop
                    icon = QIcon() # empty icon
                else:
                    # Optional: Resize the pixmap if necessary before creating the QIcon
                    # pixmap = pixmap.scaled(64, 64, aspect_ratio_mode=Qt.KeepAspectRatio)

                    # 4. Create a QIcon from QPixmap
                    icon = QIcon(pixmap)

            except Exception as exc:
                logger.error(f"Error processing base64 string or creating icon: {exc}")
                icon = QIcon() # Empty icon on error

            # 5. Set the icon for the main window
            self.setWindowIcon(icon)

        def _open_trans(self):
            DockFactory.create_json_translate_dock(self)

        def _open_rewrite(self):
            DockFactory.create_json_rewriter_dock(self)

        def _open_placeholder_replacer(self):
            DockFactory.create_placeholder_replacer_dock(self)

        def _open_ai_processor(self):
            DockFactory.create_ai_processor_dock(self)

        def _open_json_search(self):
            DockFactory.create_json_search_dock(self)

        def _open_case_converter(self):
            DockFactory.create_case_converter_dock(self)

        def _open_jsx_extractor(self):
            """Open JSX Parameter Extractor dock."""
            DockFactory.create_jsx_extractor_dock(self)

        def _open_text_to_json(self):
            """Open Text to JSON Converter dock (Task #49 - v2.9.24)."""
            signal_connections = {
                'open_in_editor_requested': self._load_json_from_converter,
                'open_in_editor_and_switch_requested': self._load_json_from_converter_and_switch
            }
            DockFactory.create_text_to_json_dock(self, signal_connections=signal_connections)

        def _load_json_from_converter(self, json_str: str):
            """Load JSON from text converter into main editor (stays in Text to JSON dock)."""
            # Open Clarify Editor as a dedicated tab (not as dock)
            if not hasattr(self, 'dock_editor') or self.dock_editor is None:
                from .gui import EditorDock
                self.dock_editor = EditorDock(self)
                self._add_tool_tab(self.dock_editor, EDITOR_NAME, "editor")
            self.dock_editor.load_generated_content(
                json_str,
                "Generated output.json",
                extension=".json",
            )
            # Don't switch - stay in Text to JSON tab
        
        def _load_json_from_converter_and_switch(self, content: str, output_kind="json"):
            """Load content from text converter into main editor and switch to Editor tab."""
            self._show_editor()

            normalized_kind = output_kind.lower() if isinstance(output_kind, str) else "json"
            if normalized_kind == "paths":
                display_name = "Generated paths.txt"
                extension = ".txt"
            else:
                display_name = "Generated output.json"
                extension = ".json"

            self.dock_editor.load_generated_content(
                content,
                display_name,
                extension=extension,
            )
            
            # SWITCH to Editor tab
            if hasattr(self, 'tool_tabs') and "editor" in self.tool_tabs:
                _widget, editor_tab_index = self.tool_tabs["editor"]
                self.tabs.setCurrentIndex(editor_tab_index)
            
            # Note: Not switching to File Explorer - user confirmed "go to Editor"

        def _open_file_explorer(self):
            """Open File Explorer dock (unified File List + Advanced Search - v2.9.115)."""
            DockFactory.create_file_explorer_dock(self)

        def _open_history(self):
            DockFactory.create_history_dock(self)

        def _open_tutorials(self):
            DockFactory.create_tutorials_dock(self)

        def _open_editor(self):
            DockFactory.create_editor_dock(self)

        def _open_google_translate(self):
            """Open Google Translate dock."""
            DockFactory.create_google_translate_dock(self)

        def _toggle_history(self, checked: bool):
            """Toggle history dock visibility."""
            if getattr(self, 'dock_history', None) is None:
                if not checked:
                    return
                self._open_history()

            if checked:
                self.dock_history.show()
            else:
                self.dock_history.hide()

        # Lazy-loading show methods for tools as tabs (v2.9.40)

        def _show_search_replace(self):
            """Compatibility entry: the compact mode of the one file workspace."""
            from .gui.tab_manager import TabManager
            TabManager.show_tool_tab(self, "file_explorer")
            self.dock_file_explorer.set_workspace_mode("compact")

        def _show_insert(self):
            """Reveal or reopen Insert by identity, including layout-hidden tabs."""
            if self.tab_insert is None:
                self.tab_insert = InsertPanel(parent=self, progress_manager=self.progress_manager)
            self.insert_panel = self.tab_insert
            self._add_tool_tab(self.tab_insert, tr("ui_builder.tab_insert"), "insert")

        def _show_translate(self):
            """Show JSON Translate as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_translate(self)

        def _show_rewriter(self):
            """Show JSON Rewriter as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_rewriter(self)

        def _show_placeholder_replacer(self):
            """Show Placeholder Replacer as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_placeholder_replacer(self)

        def _show_ai_processor(self):
            """Show AI Processor as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_ai_processor(self)

        def _show_json_search(self):
            """Show JSON Search as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_json_search(self)

        def _show_case_converter(self):
            """Show Case Converter as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_case_converter(self)

        def _show_google_translate(self):
            """Show Google Translate as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_google_translate(self)
            dock = self.dock_google_translate
            if not getattr(dock, "_editor_output_connected", False):
                dock.open_in_editor_requested.connect(
                    self._load_translation_in_editor
                )
                dock._editor_output_connected = True

        def _load_translation_in_editor(self, content: str, display_name: str):
            """Open a translation result as an unsaved text editor tab."""
            self._show_editor()
            self.dock_editor.load_generated_content(
                content,
                display_name,
                extension=".txt",
            )

        def _show_text_to_json(self):
            """Show Unified Text to JSON Converter (Format Conversion + JSX Extraction)."""
            if not hasattr(self, 'dock_unified_text_to_json'):
                from .gui.unified_text_to_json_dock import UnifiedTextToJsonDock
                self.dock_unified_text_to_json = UnifiedTextToJsonDock(self)
                # Connect signals for editor integration
                self.dock_unified_text_to_json.open_in_editor_requested.connect(self._load_json_from_converter)
                self.dock_unified_text_to_json.open_in_editor_and_switch_requested.connect(self._load_json_from_converter_and_switch)
            self._add_tool_tab(self.dock_unified_text_to_json, "Format Converter", "unified_text_to_json")

        def _show_jsx_extractor(self):
            """Show JSX Parameter Extractor as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_jsx_extractor(self)

        def _show_text_format_converter(self):
            """Show Text Format Converter as tab (create on-demand)."""
            if not hasattr(self, 'dock_text_to_json'):
                from .gui import TextToJsonDock
                self.dock_text_to_json = TextToJsonDock(self)
                self.dock_text_to_json.open_in_editor_requested.connect(self._load_json_from_converter)
            self._add_tool_tab(self.dock_text_to_json, "Text to JSON", "text_to_json")

        def _show_file_explorer(self):
            """Show File Explorer as tab (unified File List + Advanced Search - v2.9.115)."""
            from .gui.tab_manager import TabManager
            TabManager.show_file_explorer(self)

        def _show_set_operations(self):
            """Show JSON Set Operations as tab (v2.9.32 / v2.9.40)."""
            if not hasattr(self, 'dock_set_operations') or self.dock_set_operations is None:
                from .gui import SetOperationsDock
                self.dock_set_operations = SetOperationsDock(self)

                # Connect to Calculator if exists (v2.9.98)
                if hasattr(self, 'dock_calculator') and self.dock_calculator:
                    self.dock_set_operations.store_in_calculator_requested.connect(
                        self.dock_calculator.store_result
                    )
            self._add_tool_tab(self.dock_set_operations, "Set Operations", "set_operations")

        def _show_calculator(self):
            """Show Calculator Memory as tab (v2.9.98/v2.9.101)."""
            if not hasattr(self, 'dock_calculator') or self.dock_calculator is None:
                from .gui.calculator_dock import CalculatorDock
                self.dock_calculator = CalculatorDock(self)

                # Connect to Set Operations if exists (v2.9.98)
                if hasattr(self, 'dock_set_operations') and self.dock_set_operations:
                    # Bi-directional connection (v2.9.98 + v2.9.101)
                    # Set Operations → Calculator (store result)
                    self.dock_set_operations.store_in_calculator_requested.connect(
                        self.dock_calculator.store_result
                    )
                    # Calculator → Set Operations (send data to File A)
                    self.dock_calculator.send_to_set_operations.connect(
                        self.dock_set_operations.receive_calculator_data
                    )
            self._add_tool_tab(self.dock_calculator, "Calculator", "calculator")

        def _show_formula_builder(self):
            """Show Formula Builder as tab (v2.9.108)."""
            if not hasattr(self, 'dock_formula_builder') or self.dock_formula_builder is None:
                from .gui import FormulaDock
                self.dock_formula_builder = FormulaDock(self)
            self._add_tool_tab(self.dock_formula_builder, "Formula Builder", "formula_builder")

        def _show_clock(self):
            """Show the clock, stopwatch, and countdown utility."""
            if self.dock_clock is None:
                from .gui import ClockDock

                self.dock_clock = ClockDock(self)
            self._add_tool_tab(self.dock_clock, "Clock", "clock")

        def _show_terminal(self):
            """Show the bounded integrated command runner."""
            if self.dock_terminal is None:
                from .gui import TerminalDock

                self.dock_terminal = TerminalDock(self)
            self._add_tool_tab(self.dock_terminal, "Terminal", "terminal")

        def _show_lynx(self):
            """Show the optional Lynx text browser integration."""
            if self.dock_lynx is None:
                from .gui import LynxDock

                self.dock_lynx = LynxDock(self)
            self._add_tool_tab(self.dock_lynx, "Lynx", "lynx")

        def _show_information_structure(self):
            """Show bounded folder, code, database, text, and document maps."""
            if self.dock_information_structure is None:
                from .gui import InformationStructureDock

                self.dock_information_structure = InformationStructureDock(self)
                self.dock_information_structure.open_in_editor_requested.connect(
                    self._load_information_structure_in_editor
                )
            self._add_tool_tab(
                self.dock_information_structure,
                "Information Structure",
                "information_structure",
            )

        def _load_information_structure_in_editor(self, content: str, display_name: str):
            self._show_editor()
            self.dock_editor.load_generated_content(content, display_name, extension=".json")

        def _show_editorial_repair(self):
            """Show independent, review-first editorial sessions."""
            if self.dock_editorial_repair is None:
                from .gui import EditorialRepairDock

                self.dock_editorial_repair = EditorialRepairDock(self)
                self.dock_editorial_repair.prepare_ai_requested.connect(
                    self._prepare_editorial_ai_review
                )
                self.dock_editorial_repair.google_translate_requested.connect(
                    self._prepare_editorial_translation
                )
            self._add_tool_tab(self.dock_editorial_repair, "Editorial Repair", "editorial_repair")

        def _prepare_editorial_ai_review(self, prompt: str, paths: list, max_bytes: int):
            self._show_ai_processor()
            self.dock_ai_processor.prepare_file_explorer_explanation(prompt, paths, max_bytes)

        def _prepare_editorial_translation(self, text: str):
            self._show_google_translate()
            self.dock_google_translate.chk_file_mode.setChecked(False)
            self.dock_google_translate.text_input.setPlainText(text)

        def _show_boolean_logic(self):
            """Show truth-table generation and exact bounded minimization."""
            if self.dock_boolean_logic is None:
                from .gui import BooleanLogicDock

                self.dock_boolean_logic = BooleanLogicDock(self)
            self._add_tool_tab(self.dock_boolean_logic, "Boolean Logic", "boolean_logic")

        def _show_voice_programming(self):
            """Show confirmation-gated programming dictation commands."""
            if self.dock_voice_programming is None:
                from .gui import VoiceProgrammingDock

                self.dock_voice_programming = VoiceProgrammingDock(self)
                self.dock_voice_programming.confirmed_command.connect(
                    self._apply_confirmed_voice_command
                )
            self._add_tool_tab(self.dock_voice_programming, "Voice Programming", "voice_programming")

        def _apply_confirmed_voice_command(self, command: dict):
            self._show_editor()
            self.dock_editor.apply_confirmed_voice_command(command)

        def _show_algorithm_analysis(self):
            """Show local preflight and AI Processor preparation for algorithms."""
            if self.dock_algorithm_analysis is None:
                from .gui import AlgorithmAnalysisDock

                self.dock_algorithm_analysis = AlgorithmAnalysisDock(self)
                self.dock_algorithm_analysis.prepare_ai_requested.connect(
                    self._prepare_editorial_ai_review
                )
            self._add_tool_tab(
                self.dock_algorithm_analysis, "Algorithm Analysis", "algorithm_analysis"
            )

        def _show_advanced_extractor(self):
            """Show Advanced Extractor as tab (v2.9.115 - Sprint 2)."""
            if not hasattr(self, 'dock_advanced_extractor') or self.dock_advanced_extractor is None:
                self.dock_advanced_extractor = DockFactory.create_advanced_extractor_dock(self)
            self._add_tool_tab(self.dock_advanced_extractor, "Advanced Extractor", "advanced_extractor")

        def _show_tutorials(self):
            """Show tutorials as tab (Task #45 - v2.9.15 / v2.9.40)."""
            from .gui.tab_manager import TabManager
            TabManager.show_tutorials(self)

        def _show_ai_assistant(self):
            """Show AI Tutorial Assistant dialog (v2.9.92)."""
            from .gui.tutorial_assistant_dialog import TutorialAssistantDialog
            from shiboken6 import isValid
            dialog = getattr(self, '_tutorial_assistant_dialog', None)
            if dialog is None or not isValid(dialog):
                api_key = self.settings.get('ai_processor/gemini_api_key', '')
                dialog = TutorialAssistantDialog(self, api_key=api_key)
                self._tutorial_assistant_dialog = dialog
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()

        def _about_dialog(self):
            """Show the product About dialog."""
            about_text = f"""<h2>{PRODUCT_NAME}</h2>
            <p><b>Text Processing Tool</b></p>
            <p>Version: 2.9.64 (Logging System Integration)</p>
            <p>A powerful tool for JSON processing, translation, AI integration, and more.</p>
            <p><a href="https://github.com/JosueAmaral15/clarify">GitHub Repository</a></p>
            <p>© 2025 Josue Amaral</p>
            """
            QMessageBox.about(self, f"About {PRODUCT_NAME}", about_text)

        def _view_logs(self):
            """
            Open log file in default text editor (v2.9.64).

            Uses system default application to open the log file for viewing.
            Falls back to showing path if opening fails.
            """
            from .utils.logger import get_log_file
            import subprocess
            import platform

            log_file = get_log_file()

            if not log_file.exists():
                QMessageBox.warning(
                    self,
                    "No Logs Found",
                    f"Log file does not exist yet:\n{log_file}\n\n"
                    "Logs will be created when the application performs operations."
                )
                return

            # Open log file in default application
            try:
                system = platform.system()
                if system == "Linux":
                    subprocess.run(["xdg-open", str(log_file)], check=False, timeout=5)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", str(log_file)], check=False, timeout=5)
                elif system == "Windows":
                    os.startfile(str(log_file))  # pylint: disable=no-member  # Windows only
                else:
                    # Fallback: show path
                    QMessageBox.information(
                        self,
                        "Log File Location",
                        f"Log file path:\n{log_file}\n\n"
                        "Please open it manually in your text editor."
                    )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Opening Logs",
                    f"Failed to open log file:\n{log_file}\n\n"
                    f"Error: {e}\n\n"
                    "You can open it manually."
                )

        # Plugin System Methods (v2.9.109)

        def _show_plugin_manager(self):
            """Show plugin manager dialog (Phase 3.10)."""
            from .gui.plugin_manager_dialog import PluginManagerDialog
            PluginManagerDialog.show_plugin_manager(self.plugin_loader, self)

        def _toggle_plugin(self, plugin_id: str, enabled: bool):
            """Use the same checked lifecycle transition as the manager dialog."""
            success = self.plugin_loader.set_plugin_enabled(plugin_id, enabled)
            MenuBuilder.sync_plugin_actions(self)
            if not success:
                QMessageBox.warning(self, tr("dialog.plugin_manager.activation_failed"),
                                    tr("plugin_manager.toggle_failed").format(plugin_id))
            return success

        def _emit_plugin_event(self, event_name: str, data: dict):
            """
            Emit event to all active plugins (v2.9.109).

            Args:
                event_name: Event identifier
                data: Event data dictionary
            """
            if hasattr(self, 'plugin_loader'):
                self.plugin_loader.emit_event(event_name, data)

        # Update Checker Methods (v2.9.45)

        def _auto_check_for_updates(self):
            """
            Auto-check for updates on startup if enabled (v2.9.45).

            Respects user preferences:
            - update_checker/enabled (default: True)
            - Skips if checked within 24h (cache)
            - Silent operation (no errors shown)
            """
            # Check if auto-update is enabled
            enabled = self.settings.qsettings.value("update_checker/enabled", True, type=bool)
            if not enabled:
                return

            from PySide6.QtCore import QTimer
            self._update_timer = QTimer(self)
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self._perform_update_check)
            self._update_timer.start(3000)

        def _check_for_updates_manual(self):
            """
            Manual update check triggered from Help menu (v2.9.45).

            Forces fresh check (bypasses cache) and shows result with ManualCheckDialog.
            """
            from .gui.update_notification_dialog import ManualCheckDialog
            if getattr(self, "_manual_update_dialog", None) is None:
                self._manual_update_dialog = ManualCheckDialog(self)
            self._manual_update_dialog.show_checking()
            self._start_update_check(force=True)

        def _perform_update_check(self):
            """
            Perform background update check (v2.9.45).

            Called by auto-check timer. Silent operation - only shows dialog if update found.
            """
            self._start_update_check(force=False)

        def _start_update_check(self, force):
            from . import __version__
            from .gui.update_check_controller import UpdateCheckController

            if getattr(self, "_updates_closed", False):
                return
            if not hasattr(self, "_update_controller"):
                self._update_controller = UpdateCheckController(self)
                self._update_controller.completed.connect(self._on_update_checked)
            self._update_controller.start(__version__, force=force)

        def _on_update_checked(self, result):
            if getattr(self, "_updates_closed", False):
                return
            dialog = getattr(self, "_manual_update_dialog", None)
            if dialog is not None:
                dialog.show_result(result)
            info = result.get("release_info")
            if result.get("update_available") and info:
                from .gui.update_notification import UpdateNotificationDialog
                if UpdateNotificationDialog.should_show_for_version(info["version"]):
                    self._show_update_dialog(info)

        def _show_update_dialog(self, release_info: dict):
            """
            Show update notification dialog (v2.9.45).

            Args:
                release_info: Dict with keys: version, url, changelog_url, body, published_at
            """
            from .gui.update_notification import show_update_notification

            show_update_notification(
                parent=self,
                latest_version=release_info.get('version', ''),
                release_url=release_info.get('url', ''),
                changelog_url=release_info.get('changelog_url', ''),
                release_notes=release_info.get('body', ''),
                published_at=release_info.get('published_at', '')
            )

        def _show_editor(self):
            """Show editor as tab (Task #46 - v2.9.16 / v2.9.40)."""
            if not hasattr(self, 'dock_editor') or self.dock_editor is None:
                from .gui import EditorDock
                self.dock_editor = EditorDock(self)
            self._add_tool_tab(self.dock_editor, EDITOR_NAME, "editor")

        # ============================================================================
        # Tab Management System (v2.9.40 - Task: Tools as tabs)
        # ============================================================================

        def _add_tool_tab(self, widget: QWidget, title: str, tool_name: str) -> int:
            """
            Add a tool as a tab in the main QTabWidget.

            Args:
                widget: The tool widget to add
                title: Tab title to display
                tool_name: Internal tool name for tracking

            Returns:
                Tab index where the tool was added
            """
            widget.setProperty("clarify_tool_id", tool_name)
            from .gui.tab_manager import TabManager
            tool_window_manager = TabManager.ensure_tool_window_manager(self)
            if tool_window_manager.activate_detached(widget):
                return -1
            TabManager.prepare_embedded_tool(widget)
            title = TabManager.translated_title(tool_name) or title
            manager = getattr(self, "layout_manager", None)
            if manager is not None:
                manager.register_dock(tool_name, widget)
            existing = self.tabs.indexOf(widget)
            if existing >= 0:
                tool_window_manager.register_attached(widget)
                self.tool_tabs[tool_name] = (widget, existing)
                self.tabs.setTabVisible(existing, True)
                self.tabs.setCurrentIndex(existing)
                self._save_tab_state()
                return existing
            # Add new tab
            tab_index = self.tabs.addTab(widget, title)

            # Track the tab
            self.tool_tabs[tool_name] = (widget, tab_index)
            tool_window_manager.register_attached(widget)

            # Switch to new tab
            self.tabs.setCurrentIndex(tab_index)

            # Fix: Restore MainWindow window flags after adding tab (v2.9.117)
            # QDockWidget as tab can interfere with MainWindow flags on Linux
            self._restore_window_flags()

            # Save tab state to QSettings
            self._save_tab_state()

            return tab_index

        def _close_tab(self, index: int):
            """
            Close tab at given index with confirmation if needed.

            Args:
                index: Tab index to close
            """
            # Get widget at index
            widget = self.tabs.widget(index)
            tab_title = self.tabs.tabText(index)
            if hasattr(widget, "request_tab_close") and not widget.request_tab_close():
                return

            # Check for unsaved changes (only for Editor)
            if (not getattr(widget, 'handles_unsaved_tab_close', False)
                    and hasattr(widget, 'has_unsaved_changes') and callable(widget.has_unsaved_changes)):
                if widget.has_unsaved_changes():
                    reply = QMessageBox.question(
                        self,
                        tr("dialog.unsaved_title"),
                        tr("dialog.unsaved_message", tab_title=tab_title),  # pylint: disable=unexpected-keyword-arg
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                        QMessageBox.Save
                    )

                    if reply == QMessageBox.Cancel:
                        return
                    elif reply == QMessageBox.Save:
                        # Try to save
                        if hasattr(widget, 'save_file') and callable(widget.save_file):
                            widget.save_file()

            # Remove tab
            self.tabs.removeTab(index)
            tool_window_manager = getattr(self, "tool_window_manager", None)
            if tool_window_manager is not None:
                tool_window_manager.forget(widget)

            # Fix: Restore MainWindow window flags after removing tab (v2.9.117)
            # QDockWidget as tab can interfere with MainWindow flags on Linux
            self._restore_window_flags()

            # Remove from tracking dict
            self.tool_tabs = {
                name: (tracked, self.tabs.indexOf(tracked))
                for name, (tracked, _old_index) in self.tool_tabs.items()
                if tracked is not widget and (
                    self.tabs.indexOf(tracked) >= 0
                    or (tool_window_manager is not None
                        and tool_window_manager.is_detached(tracked))
                )
            }

            # Save tab state to QSettings
            self._save_tab_state()

        def _initialize_all_tabs(self):
            """
            Force initialization of all tabs to prevent lazy rendering issues.

            Qt uses lazy rendering - widgets in non-visible tabs are not rendered
            until the tab is activated. This causes invisible widgets on startup.
            Solution: Temporarily activate each tab to force rendering, then restore.

            Reference: Common Qt issue with QTabWidget lazy initialization
            """
            import logging
            logger = logging.getLogger(__name__)

            # Store current tab index
            original_index = self.tabs.currentIndex()
            tab_count = self.tabs.count()

            logger.info("Initializing all tabs - Count: %s, Current: %s", tab_count, original_index)

            # Activate each tab briefly to force widget rendering
            for i in range(tab_count):
                if not self.tabs.isTabVisible(i):
                    continue
                tab_name = self.tabs.tabText(i)
                logger.info("  Activating tab %s: '%s'", i, tab_name)
                self.tabs.setCurrentIndex(i)
                # Force immediate processing of events to ensure rendering
                QApplication.processEvents()

                # Also force geometry update on the widget
                widget = self.tabs.widget(i)
                if widget:
                    widget.updateGeometry()
                    widget.update()
                    logger.info("    Widget updated: %s", widget.__class__.__name__)

            # Restore original tab
            logger.info("Restoring original tab: %s", original_index)
            self.tabs.setCurrentIndex(original_index)
            QApplication.processEvents()
            logger.info("Tab initialization complete")

        def _restore_window_flags(self):
            """
            Restore MainWindow window flags to desired state (v2.9.117).

            Purpose: QDockWidget used as tab widget can interfere with MainWindow
            window flags on Linux, causing maximize button to disappear.

            This method ensures window flags are always restored after tab operations
            (add/remove tabs) to maintain consistent window controls.

            Called after:
            - Adding a tool as tab (_add_tool_tab)
            - Removing a tab (_close_tab)
            - Any operation that might affect window flags
            """
            if hasattr(self, '_desired_window_flags'):
                _restore_qt_window_flags(self, self._desired_window_flags)

        def _apply_tab_close_button_style(self):
            """Apply theme-appropriate styling to tab close buttons (v2.9.40)."""
            # Get current theme
            from .appearance_defaults import DEFAULT_THEME

            current_theme = self.settings.get("theme", DEFAULT_THEME)

            # Define close button colors based on theme
            if current_theme == "dark":
                close_btn_color = "#B0B0B0"  # Light gray for dark mode
                close_btn_hover = "#FFFFFF"
            else:  # light or system
                close_btn_color = "#505050"  # Dark gray for light mode
                close_btn_hover = "#000000"

            # Apply QSS styling to QTabWidget close buttons
            tab_style = f"""
                QTabWidget::close-button {{
                    image: none;
                    background: {close_btn_color};
                    border-radius: 2px;
                    width: 16px;
                    height: 16px;
                }}
                QTabWidget::close-button:hover {{
                    background: {close_btn_hover};
                }}
            """
            self.tabs.setStyleSheet(tab_style)

        def _save_tab_state(self):
            """Save current tab state to settings (v2.9.40).
            v2.9.112: Don't save fixed tabs (Search/Replace, Insert) - only save if they're still open."""
            if getattr(self, "_restoring_tabs", False):
                return
            tool_window_manager = getattr(self, "tool_window_manager", None)
            open_widgets = (
                tool_window_manager.ordered_open_widgets()
                if tool_window_manager is not None
                else [self.tabs.widget(index) for index in range(self.tabs.count())]
            )
            open_tools = [widget.property("clarify_tool_id") for widget in open_widgets
                          if widget.property("clarify_tool_id") not in (None, "insert")]

            # Check if fixed tabs are still open (v2.9.112)
            fixed_tabs_open = {
                "search_replace": self.tab_search is not None and (
                    self.tabs.indexOf(self.tab_search) >= 0
                    or (tool_window_manager is not None
                        and tool_window_manager.is_detached(self.tab_search))
                ),
                "insert": self.tab_insert is not None and (
                    self.tabs.indexOf(self.tab_insert) >= 0
                    or (tool_window_manager is not None
                        and tool_window_manager.is_detached(self.tab_insert))
                )
            }

            # Save to settings
            self.settings.set("tabs_open_tools", open_tools)
            self.settings.set("tabs_fixed_open", fixed_tabs_open)  # Track if fixed tabs are open
            self.settings.set("tabs_current_index", self.tabs.currentIndex())
            current = self.tabs.currentWidget()
            self.settings.set("tabs_current_tool", current.property("clarify_tool_id") if current else None)

        def _restore_tab_state(self):
            """Do not overwrite the saved snapshot while rebuilding its tabs."""
            self._restoring_tabs = True
            try:
                self._restore_tab_state_impl()
            finally:
                self._restoring_tabs = False

        def _restore_tab_state_impl(self):
            """Restore tab state from settings on startup (v2.9.40).
            v2.9.112: Don't restore fixed tabs if they were closed."""
            # Check if fixed tabs should be restored (v2.9.112)
            fixed_tabs_open = self.settings.get("tabs_fixed_open", {"search_replace": True, "insert": True})
            saved_index = self.settings.get("tabs_current_index", 0)
            saved_tool = self.settings.get("tabs_current_tool", None)

            # Remove fixed tabs if they were closed in previous session
            if not fixed_tabs_open.get("search_replace", True):
                index = self.tabs.indexOf(self.tab_search)
                if index >= 0:
                    self.tabs.removeTab(index)
                    self.tool_tabs.pop("file_explorer", None)

            if not fixed_tabs_open.get("insert", True):
                # Remove Insert tab (check current index since Search/Replace might be removed)
                for i in range(self.tabs.count()):
                    if self.tabs.widget(i) == self.tab_insert:
                        self.tabs.removeTab(i)
                        break

            # Get list of tools that were open
            open_tools = self.settings.get("tabs_open_tools", [])

            # Reopen each tool
            for tool_name in open_tools:
                if tool_name == "file_explorer":
                    from .gui.tab_manager import TabManager
                    TabManager.show_tool_tab(self, "file_explorer")
                    continue
                # Map tool_name to _show_* method
                method_name = f"_show_{tool_name}"
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method()

            # Restore active tab
            import logging
            logger = logging.getLogger(__name__)

            for index in range(self.tabs.count()):
                if saved_tool and self.tabs.widget(index).property("clarify_tool_id") == saved_tool:
                    saved_index = index
                    break
            current_count = self.tabs.count()

            logger.info("Restoring tab state - Saved index: %s, Tab count: %s", saved_index, current_count)

            # Validate saved index - if tab was closed, default to first available tab
            if isinstance(saved_index, int) and 0 <= saved_index < current_count:
                logger.info("  Setting tab to saved index: %s", saved_index)
                self.tabs.setCurrentIndex(saved_index)
            else:
                # Saved tab no longer exists, activate first tab if any
                if current_count > 0:
                    logger.warning("  Saved index %s invalid! Defaulting to tab 0", saved_index)
                    self.tabs.setCurrentIndex(0)
                else:
                    logger.warning("  No tabs available to activate")

        def _build_menu(self):
            """Build application menus using MenuBuilder (v2.9.114 - Phase 3.4)."""
            MenuBuilder.build_all_menus(self)

        def _apply_theme_action(self, action: QAction):
            for a in (self.act_theme_system, self.act_theme_light, self.act_theme_dark):
                a.setChecked(a is action)
            if action is self.act_theme_system:
                mode = "system"
            elif action is self.act_theme_light:
                mode = "light"
            else:
                mode = "dark"
            apply_theme(QApplication.instance(), mode)
            self.settings.set("theme", mode)
            self._apply_tab_close_button_style()
            # persist
            cfg = load_prefs()
            if not cfg.has_section("THEME"):
                cfg.add_section("THEME")
            cfg["THEME"]["mode"] = mode
            save_prefs(cfg)

        def _next_tab(self):
            """Switch to next tab (Ctrl+PgDown) - v2.9.113."""
            current = self.tabs.currentIndex()
            total = self.tabs.count()
            if total > 0:
                next_index = (current + 1) % total
                self.tabs.setCurrentIndex(next_index)

        def _previous_tab(self):
            """Switch to previous tab (Ctrl+PgUp) - v2.9.113."""
            current = self.tabs.currentIndex()
            total = self.tabs.count()
            if total > 0:
                prev_index = (current - 1) % total
                self.tabs.setCurrentIndex(prev_index)

        def _apply_saved_settings(self):
            """Apply saved settings using WindowSettings (v2.9.114 - Phase 3.5)."""
            WindowSettings.apply_saved_settings(self)

        def get_current_json(self):
            """Get current JSON data (placeholder for plugin integration)."""
            return None

        def translate_json(self, data, _lang):
            """Translate JSON data (placeholder for API integration)."""
            return data

        def _show_preferences(self):
            """Show preferences dialog (Phase 3.10)."""
            from .gui.preferences_dialog import PreferencesDialog
            PreferencesDialog.show_preferences(self.settings, self)

        def _show_transparency_dialog(self):
            """Show window transparency configuration dialog (Phase 3.10)."""
            from .gui.transparency_dialog import TransparencyDialog
            TransparencyDialog.show_transparency_dialog(self)

        def _show_settings_reset(self):
            """Preview and reset only explicitly supported preference categories."""
            from .gui.settings_reset_dialog import show_settings_reset
            show_settings_reset(self)

        def _switch_language(self, lang: str):
            """Switch application language at runtime (Task #24 - v2.9.10, expanded v2.9.43)."""
            # QActionGroup handles radio button behavior automatically - no need to setChecked
            # Just switch language and save preference

            logger.debug(f"Switching language to: {lang}")
            logger.debug(f"Current language before switch: {self.translator.current_language}")

            # Switch language
            switch_language(lang)

            logger.debug(f"Current language after switch: {self.translator.current_language}")

            # Save preference
            self.settings.set("language", lang)

        def _toggle_error_reporting(self, checked: bool):
            """Toggle error reporting on/off (v2.9.89)."""
            self.settings.qsettings.setValue("error_reporting/enabled", checked)
            status = "enabled" if checked else "disabled"
            QMessageBox.information(
                self,
                "Error Reporting",
                f"Error reporting has been {status}."
            )

        def _toggle_system_info(self, checked: bool):
            """Toggle system info inclusion in error reports (v2.9.89)."""
            self.settings.qsettings.setValue("error_reporting/include_system_info", checked)

        def _toggle_auto_github(self, checked: bool):
            """Toggle auto-open GitHub Issues on error (v2.9.89)."""
            self.settings.qsettings.setValue("error_reporting/auto_open_github", checked)

        def _show_config_editor(self):
            """Show Configuration File Editor dialog (v2.9.90)."""
            from .gui.config_editor_dialog import ConfigEditorDialog
            dialog = ConfigEditorDialog(self)
            dialog.exec()

        def _on_language_changed(self, _lang: str):
            """Called when language changes - retranslate all UI (Task #24 - v2.9.10)."""
            self._retranslate_ui()

        def _retranslate_ui(self):
            """Retranslate all UI elements (Task #24 - v2.9.10)."""
            self.setWindowTitle(tr("app.title"))
            self._build_menu()
            from .gui.tab_manager import TabManager
            for index in range(self.tabs.count()):
                widget = self.tabs.widget(index)
                title = TabManager.translated_title(widget.property("clarify_tool_id"))
                if title is not None:
                    self.tabs.setTabText(index, title)
            tool_window_manager = getattr(self, "tool_window_manager", None)
            if tool_window_manager is not None:
                tool_window_manager.retranslate_ui()

        def _show_shortcuts(self):
            """Show keyboard shortcuts customization dialog (v2.9.33)."""
            from .gui import ShortcutsDialog

            dialog = ShortcutsDialog(self)
            dialog.shortcuts_changed.connect(self._on_shortcuts_changed)
            dialog.exec()

        def _register_docks_with_layout_manager(self):
            """
            Register all dock widgets with the LayoutManager (v2.9.84).

            Called after _build_ui() to register all docks.
            """
            # Register main docks
            dock_mapping = {
                "editor": getattr(self, "dock_editor", None),
                "file_explorer": getattr(self, "dock_file_explorer", None),
                "insert": getattr(self, "insert_panel", None),
                "set_operations": getattr(self, "dock_set_operations", None),
                "rewriter": getattr(self, "dock_rewriter", None),
                "translate": getattr(self, "dock_translate", None),
                "ai_processor": getattr(self, "dock_ai_processor", None),
                "case_converter": getattr(self, "dock_case_converter", None),
                "json_search": getattr(self, "dock_json_search", None),
            }

            # Register only existing docks
            for dock_name, dock_widget in dock_mapping.items():
                if dock_widget is not None:
                    self.layout_manager.register_dock(dock_name, dock_widget)

            self.logger.info(f"Registered {len([d for d in dock_mapping.values() if d])} docks with LayoutManager")

            # Force update of all registered docks to ensure proper rendering
            for dock_widget in dock_mapping.values():
                if dock_widget is not None:
                    dock_widget.update()
                    dock_widget.repaint()

        def _save_current_layout(self):
            """Save current layout with a custom name (v2.9.84)."""
            from PySide6.QtWidgets import QInputDialog

            layout_name, ok = QInputDialog.getText(
                self,
                tr("menu.view.layouts.save"),
                "Enter layout name:",
                text="My Custom Layout"
            )

            if ok and layout_name.strip():
                self.layout_manager.save_layout(layout_name.strip())
                self.logger.info(f"Layout saved: {layout_name}")

                # Show confirmation
                QMessageBox.information(
                    self,
                    "Layout Saved",
                    f"Layout '{layout_name}' has been saved successfully."
                )

        def _manage_layouts(self):
            """Show layout management dialog (Phase 3.10)."""
            from .gui.layout_manager_dialog import LayoutManagerDialog
            LayoutManagerDialog.show_layout_manager(self.layout_manager, self)

        def _new_from_template(self):
            """Create new project from template (v2.9.63)."""
            from .gui.template_dialog import TemplateDialog

            dialog = TemplateDialog(self)
            dialog.exec()

        def _customize_shortcuts(self):
            """Show keyboard shortcuts customization dialog (v2.9.62)."""
            from .gui.shortcut_customizer import ShortcutCustomizerDialog
            from .shortcut_manager import ShortcutManager

            dialog = ShortcutCustomizerDialog(self)

            def on_shortcuts_changed(custom_shortcuts):
                # Save to settings
                self.settings.save_custom_shortcuts(custom_shortcuts)
                # Apply to ShortcutManager
                ShortcutManager.load_custom_shortcuts(custom_shortcuts)
                # Log change
                self.logger.info(f"Shortcuts customized: {len(custom_shortcuts)} modified")

            dialog.shortcutsChanged.connect(on_shortcuts_changed)
            dialog.exec()

        def _show_keyboard_shortcuts_help(self):
            """Present the single non-blocking effective shortcut reference."""
            from shiboken6 import isValid

            from .gui.shortcut_reference_dialog import ShortcutReferenceDialog

            dialog = getattr(self, "_shortcut_reference_dialog", None)
            if dialog is None or not isValid(dialog):
                dialog = ShortcutReferenceDialog(self)
                dialog.customize_requested.connect(self._show_shortcuts)
                self._shortcut_reference_dialog = dialog
            dialog.present()

        def _on_shortcuts_changed(self, new_custom_shortcuts: dict):
            """Handle shortcuts changed from dialog (v2.9.33)."""
            from .shortcut_manager import ShortcutManager

            # Update ShortcutManager
            ShortcutManager.load_custom_shortcuts(new_custom_shortcuts)

            # Save to settings
            self.settings.set_custom_shortcuts(new_custom_shortcuts)

            # Reapply shortcuts to all actions
            self._apply_shortcuts_to_menu()

            # Show confirmation
            QMessageBox.information(
                self,
                "Shortcuts Updated",
                f"Keyboard shortcuts have been updated.\n\n"
                f"{len(new_custom_shortcuts)} custom shortcut(s) active.\n\n"
                "Restart may be required for some shortcuts to take effect."
            )

        def _apply_shortcuts_to_menu(self):
            """Apply shortcuts to all menu actions and update tooltips (v2.9.33)."""
            from .shortcut_manager import ShortcutManager

            # Mapping: (action, shortcut_name, tooltip_description)
            shortcuts_map = [
                # File menu
                (self.act_open_editor, "open_editor", "Open integrated file editor"),

                # Edit menu
                (self.act_undo, "undo", "Undo last operation"),
                (self.act_redo, "redo", "Redo last undone operation"),

                # Tools menu
                (self.act_open_json_search, "open_json_search", "Search and filter JSON data"),
                (self.act_open_rewriter, "open_json_rewriter", "Rewrite JSON structure"),
                (self.act_open_set_operations, "open_set_operations", "Perform set operations on JSON"),
                (self.act_open_ai_processor, "open_ai_processor", "Process JSON with AI"),
                (self.act_open_case_converter, "open_case_converter", "Convert text case"),
                (self.act_open_text_to_json, "open_text_to_json", "Convert text to JSON / Extract from JSX"),
                (self.act_open_placeholder_replacer, "open_placeholder_replacer", "Replace placeholders in text"),
                (self.act_open_translate, "open_translate", "Translate JSON content"),
                (self.act_open_file_explorer, "open_file_explorer", "Unified file explorer with advanced search"),
                (self.act_open_advanced_extractor, "open_advanced_extractor", "Extract JSX/HTML with advanced options"),

                # View menu
                (self.act_toggle_history, "toggle_history", "Show/hide operation history"),
            ]

            # Add tutorials if available
            if hasattr(self, 'act_open_tutorials'):
                shortcuts_map.append((self.act_open_tutorials, "tutorials", "Browse tutorials"))

            # Apply shortcuts and tooltips
            for action, shortcut_name, description in shortcuts_map:
                # Apply shortcut
                ShortcutManager.add_shortcut_to_action(action, shortcut_name)

                # Keep a translated base; QAction defaults an unset tooltip to its label.
                current_tip = action.toolTip()
                description = (action.property("clarify_tooltip_base")
                               or (current_tip if current_tip != action.text() else "")
                               or action.statusTip()
                               or tr(f"shortcuts.desc.{shortcut_name}", "")
                               or description)
                action.setProperty("clarify_tooltip_base", description)
                shortcut = ShortcutManager.get_key_sequence(shortcut_name).toString()
                if shortcut:
                    tooltip = f"{description} ({shortcut})"
                else:
                    tooltip = description
                action.setToolTip(tooltip)

        # Undo/Redo Methods (Task #12 - v2.9.8)

        def _undo(self):
            """Undo the last command."""
            if self.command_manager.undo():
                self._update_undo_redo_state()
                QMessageBox.information(
                    self,
                    tr("app.msg_undo_title"),
                    f"{tr('app.msg_undo_title')}: "
                    f"{self.command_manager.get_redo_description() or tr('app.msg_success_title')}"
                )
            else:
                QMessageBox.warning(self, tr("app.msg_undo_title"), tr("app.msg_undo_nothing"))

        def _redo(self):
            """Redo the last undone command."""
            if self.command_manager.redo():
                self._update_undo_redo_state()
                QMessageBox.information(
                    self,
                    tr("app.msg_redo_title"),
                    f"{tr('app.msg_redo_title')}: "
                    f"{self.command_manager.get_undo_description() or tr('app.msg_success_title')}"
                )
            else:
                QMessageBox.warning(self, tr("app.msg_redo_title"), tr("app.msg_redo_nothing"))

        def _clear_undo_history(self):
            """Clear all undo/redo history."""
            reply = QMessageBox.question(
                self,
                tr("app.msg_clear_history_title"),
                tr("app.msg_clear_history_confirm"),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.command_manager.clear_history()
                self._update_undo_redo_state()
                QMessageBox.information(self, tr("app.msg_success_title"), tr("app.msg_clear_history_success"))

        def _update_undo_redo_state(self):
            """Update the enabled state of undo/redo buttons based on history."""
            self.act_undo.setEnabled(self.command_manager.can_undo())
            self.act_redo.setEnabled(self.command_manager.can_redo())

            # Update button tooltips with descriptions
            if self.command_manager.can_undo():
                self.act_undo.setToolTip(f"{tr('app.msg_undo_title')}: {self.command_manager.get_undo_description()}")
            else:
                self.act_undo.setToolTip(tr("app.tooltip_undo_nothing"))

            if self.command_manager.can_redo():
                self.act_redo.setToolTip(f"{tr('app.msg_redo_title')}: {self.command_manager.get_redo_description()}")
            else:
                self.act_redo.setToolTip(tr("app.tooltip_redo_nothing"))

        def _clear_recent_files(self):
            """Clear recent files list."""
            reply = QMessageBox.question(
                self,
                tr("app.msg_clear_recent_title"),
                tr("app.msg_clear_recent_confirm"),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.settings.clear_recent_files()
                QMessageBox.information(self, tr("app.msg_success_title"), tr("app.msg_clear_recent_success"))

        def keyPressEvent(self, event):  # pylint: disable=too-many-return-statements
            """Handle global keyboard shortcuts (v2.9.33 + v2.9.35 accessibility)."""

            key = event.key()
            modifiers = event.modifiers()

            # Ctrl+Tab - Next dock (menu order)
            if key == Qt.Key_Tab and modifiers == Qt.ControlModifier:
                self._navigate_next_dock()
                event.accept()
                return

            # Ctrl+Shift+Tab - Previous dock (menu order)
            elif key == Qt.Key_Tab and modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
                self._navigate_prev_dock()
                event.accept()
                return

            # Ctrl+PageDown - Next dock (dynamic/creation order)
            elif key == Qt.Key_PageDown and modifiers == Qt.ControlModifier:
                self._navigate_next_dock_dynamic()
                event.accept()
                return

            # Ctrl+PageUp - Previous dock (dynamic/creation order)
            elif key == Qt.Key_PageUp and modifiers == Qt.ControlModifier:
                self._navigate_prev_dock_dynamic()
                event.accept()
                return

            # Ctrl+1-9 - Jump to specific dock
            elif modifiers == Qt.ControlModifier:
                if Qt.Key_1 <= key <= Qt.Key_9:
                    dock_index = key - Qt.Key_1  # 0-based
                    self._jump_to_dock(dock_index)
                    event.accept()
                    return
                # Ctrl+0 - Reset font size (v2.9.35)
                elif key == Qt.Key_0:
                    self._reset_font_size()
                    event.accept()
                    return

            # F11 - Fullscreen
            elif key == Qt.Key_F11:
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()
                event.accept()
                return

            # Pass to parent for default handling
            super().keyPressEvent(event)

        def eventFilter(self, obj, event):
            """Global event filter for Shift+Scroll horizontal scrolling (v2.9.115)."""
            # Only handle wheel events
            if event.type() != QEvent.Wheel:
                return False

            # Shift+Scroll OR Ctrl+Shift+Scroll - Horizontal scroll
            if event.modifiers() == Qt.ShiftModifier or event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
                # Get widget under mouse
                widget = QApplication.widgetAt(event.globalPosition().toPoint())
                if widget:
                    # Find scrollable parent (QTextEdit, QTableWidget, etc.)
                    scrollable = widget
                    while scrollable and not hasattr(scrollable, 'horizontalScrollBar'):
                        scrollable = scrollable.parentWidget()

                    if scrollable and hasattr(scrollable, 'horizontalScrollBar'):
                        scrollbar = scrollable.horizontalScrollBar()
                        if scrollbar and scrollbar.isVisible():
                            # Scroll horizontally
                            delta = event.angleDelta().y()  # Use vertical wheel movement
                            step = scrollbar.singleStep() * 3  # Scroll 3 steps at a time

                            if delta > 0:
                                # Scroll left
                                scrollbar.setValue(scrollbar.value() - step)
                            else:
                                # Scroll right
                                scrollbar.setValue(scrollbar.value() + step)

                # Consume event completely - prevent vertical scroll when Shift is pressed
                return True  # Event handled, don't propagate

            # Pass to parent for default handling
            return False

        def wheelEvent(self, event):
            """Handle mouse wheel for font scaling (v2.9.35)."""

            # Ctrl+Scroll - Font scaling
            if event.modifiers() == Qt.ControlModifier:
                from .accessibility_manager import AccessibilityManager

                if event.angleDelta().y() > 0:
                    # Scroll up - increase font
                    new_size = AccessibilityManager.increase_font_size(
                        QApplication.instance(),
                        self.settings.qsettings
                    )
                    self.statusBar().showMessage(f"Font size: {new_size}pt", 2000)
                else:
                    # Scroll down - decrease font
                    new_size = AccessibilityManager.decrease_font_size(
                        QApplication.instance(),
                        self.settings.qsettings
                    )
                    self.statusBar().showMessage(f"Font size: {new_size}pt", 2000)

                event.accept()
                return

            # Pass to parent for default handling
            super().wheelEvent(event)

        def _reset_font_size(self):
            """Reset font size to default (v2.9.35)."""
            from .accessibility_manager import AccessibilityManager

            new_size = AccessibilityManager.reset_font_size(
                QApplication.instance(),
                self.settings.qsettings
            )
            self.statusBar().showMessage(f"Font size reset to {new_size}pt", 2000)

        def _apply_accessibility(self):
            """Apply accessibility features (v2.9.35)."""
            from .accessibility_manager import AccessibilityManager

            # Apply focus indicators globally
            AccessibilityManager.apply_focus_indicators(QApplication.instance())

            # Enable screen reader support
            AccessibilityManager.enable_screen_reader_support(QApplication.instance())

            # Load and apply saved font size
            font_size = AccessibilityManager.get_font_size(self.settings.qsettings)
            AccessibilityManager.apply_font_size(QApplication.instance(), font_size)

        def _get_all_docks(self):
            """Get list of all QDockWidget instances (v2.9.33)."""
            docks = []
            for attr_name in dir(self):
                if attr_name.startswith('dock_'):
                    dock = getattr(self, attr_name, None)
                    if dock and isinstance(dock, QDockWidget):
                        docks.append(dock)
            return docks

        def _get_visible_docks(self):
            """Get list of visible QDockWidget instances (v2.9.33)."""
            return [dock for dock in self._get_all_docks() if dock.isVisible()]

        def _get_dock_by_menu_order(self):
            """Get docks in menu order (v2.9.33)."""
            # Order matches Tools menu
            ordered_names = [
                'dock_json_search',      # 1
                'dock_rewriter',         # 2
                'dock_set_operations',   # 3
                'dock_ai_processor',     # 4
                'dock_case_converter',   # 5
                'dock_text_extractor',   # 6
                'dock_text_to_json',     # 7
                'dock_placeholder_replacer',  # 8
                'dock_translate',        # 9
            ]

            docks = []
            for name in ordered_names:
                dock = getattr(self, name, None)
                if dock and isinstance(dock, QDockWidget):
                    docks.append(dock)
            return docks

        def _navigate_next_dock(self):
            """Navigate to next dock in menu order (v2.9.33)."""
            visible_docks = self._get_visible_docks()
            if not visible_docks:
                return

            # Find current focused dock
            focused_dock = None
            for dock in visible_docks:
                if dock.widget() and dock.widget().hasFocus():
                    focused_dock = dock
                    break

            # Get all docks in menu order
            ordered_docks = self._get_dock_by_menu_order()
            visible_ordered = [d for d in ordered_docks if d in visible_docks]

            if not visible_ordered:
                return

            # Find next dock
            if focused_dock and focused_dock in visible_ordered:
                current_idx = visible_ordered.index(focused_dock)
                next_idx = (current_idx + 1) % len(visible_ordered)
                next_dock = visible_ordered[next_idx]
            else:
                # No dock focused, go to first
                next_dock = visible_ordered[0]

            self._focus_dock(next_dock)

        def _navigate_prev_dock(self):
            """Navigate to previous dock in menu order (v2.9.33)."""
            visible_docks = self._get_visible_docks()
            if not visible_docks:
                return

            # Find current focused dock
            focused_dock = None
            for dock in visible_docks:
                if dock.widget() and dock.widget().hasFocus():
                    focused_dock = dock
                    break

            # Get all docks in menu order
            ordered_docks = self._get_dock_by_menu_order()
            visible_ordered = [d for d in ordered_docks if d in visible_docks]

            if not visible_ordered:
                return

            # Find previous dock
            if focused_dock and focused_dock in visible_ordered:
                current_idx = visible_ordered.index(focused_dock)
                prev_idx = (current_idx - 1) % len(visible_ordered)
                prev_dock = visible_ordered[prev_idx]
            else:
                # No dock focused, go to last
                prev_dock = visible_ordered[-1]

            self._focus_dock(prev_dock)

        def _navigate_next_dock_dynamic(self):
            """Navigate to next dock in creation order (v2.9.33)."""
            visible_docks = self._get_visible_docks()
            if not visible_docks:
                return

            # Find current focused dock
            focused_dock = None
            for dock in visible_docks:
                if dock.widget() and dock.widget().hasFocus():
                    focused_dock = dock
                    break

            # Find next dock
            if focused_dock and focused_dock in visible_docks:
                current_idx = visible_docks.index(focused_dock)
                next_idx = (current_idx + 1) % len(visible_docks)
                next_dock = visible_docks[next_idx]
            else:
                # No dock focused, go to first
                next_dock = visible_docks[0]

            self._focus_dock(next_dock)

        def _navigate_prev_dock_dynamic(self):
            """Navigate to previous dock in creation order (v2.9.33)."""
            visible_docks = self._get_visible_docks()
            if not visible_docks:
                return

            # Find current focused dock
            focused_dock = None
            for dock in visible_docks:
                if dock.widget() and dock.widget().hasFocus():
                    focused_dock = dock
                    break

            # Find previous dock
            if focused_dock and focused_dock in visible_docks:
                current_idx = visible_docks.index(focused_dock)
                prev_idx = (current_idx - 1) % len(visible_docks)
                prev_dock = visible_docks[prev_idx]
            else:
                # No dock focused, go to last
                prev_dock = visible_docks[-1]

            self._focus_dock(prev_dock)

        def _jump_to_dock(self, dock_index: int):
            """Jump to specific dock by index (0-based) (v2.9.33)."""
            ordered_docks = self._get_dock_by_menu_order()

            if 0 <= dock_index < len(ordered_docks):
                dock = ordered_docks[dock_index]

                # If dock is not visible, show it (Q10 answer: open if not open)
                if not dock.isVisible():
                    dock.show()

                self._focus_dock(dock)
            # If dock doesn't exist, ignore silently (Q3 answer)

        def _focus_dock(self, dock: QDockWidget):
            """Focus on a dock widget (v2.9.33)."""
            if not dock or not dock.isVisible():
                return

            # Raise the dock
            dock.raise_()
            dock.activateWindow()

            # Focus the widget inside
            if dock.widget():
                dock.widget().setFocus()

            # Update status bar
            self.statusBar().showMessage(f"Focused: {dock.windowTitle()}", 2000)

        def closeEvent(self, event):
            """Handle window close event using WindowSettings (v2.9.114 - Phase 3.5)."""
            WindowSettings.handle_close_event(self, event)
            if event.isAccepted():
                tool_window_manager = getattr(self, "tool_window_manager", None)
                if tool_window_manager is not None:
                    tool_window_manager.reattach_all(activate=False)
                self._updates_closed = True
                timer = getattr(self, "_update_timer", None)
                if timer is not None:
                    timer.stop()

        def _build_ui(self):
            """Build UI using UIBuilder (Phase 3.9)."""
            from .gui.ui_builder import UIBuilder
            UIBuilder.build_all(self)

        def _restore_prefs(self):
            """Restore preferences using WindowSettings (v2.9.114 - Phase 3.5)."""
            WindowSettings.restore_prefs(self)


# =============================================================================
#                                  ARGPARSE
# =============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    # If a subcommand is present, run as CLI-only.
    if argv and argv[0] in {"search","replace","insert","translate","gtranslate","dedupe"}:
        args = parser.parse_args(argv)
        return args.func(args)

    # Otherwise, run the GUI (PySide6 must be available)
    if not _PYSIDE:
        parser.print_help(sys.stderr)
        logger.error("PySide6 is not installed; install it or use the CLI subcommands.")
        return 2

    # Set Qt attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)

    app = QApplication(sys.argv)
    win = MainWindow(app)
    win.show()

    # Force immediate rendering of all widgets (fix for invisible widgets on startup)
    win.repaint()
    app.processEvents()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
