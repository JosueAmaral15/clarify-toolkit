#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import argparse
from base64 import b64decode
import configparser
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple, Union

# ---------------------------------------------------------------------------
#  Import organized modules (eliminates code duplication)
# ---------------------------------------------------------------------------

# Logging system
from .utils.logger import get_logger

# Error handling & crash reporting (v2.9.61)
from .utils.error_handler import install_crash_handler

# Core functionality: search, replace, insert, filtering
from .core import (
    SearchOptions, preserve_case_like, replace_in_text,
    InsertMode, insert_at_line,
    Condition, filter_files_by_conditions, OPS
)

# Utilities: file operations, text processing, TypeScript/JavaScript
from .utils import (
    walk_files, read_text, write_text, safe_backup_file,
    parse_exclusion_patterns, mask_exclusions, unmask_exclusions,
    load_ts_object, dump_ts_object
)

# JSON Rewriter: types, parser, operations, serializer (includes BUG FIX)
from .rewriter import (
    Obj, JSONNode, parse_json_preserving_duplicates_text, freeze,
    find_object_block, ts_block_to_json_text,
    sanitize_keys_and_values, ts_process_full_preserving,
    dedupe, join_keys, eliminate_duplicates, merge_obj_values,
    avoid_duplicate_child_keys, exclude_numeric_keys, skip_empty_values,
    normalize_escaping, array_to_object_conversion,
    dump_ts_node, dump_ts_obj, collapse_blank_lines
)

# Case Converter: camelCase/PascalCase/snake_case/kebab-case conversion
from .case_converter import JSObjectCaseConverter

# Theme Manager: application theming (light, dark, system)
from .theme_manager import ThemeManager

# Internationalization: runtime language switching (Task #24 - v2.9.10)
from .i18n import get_translator, switch_language, tr, tooltip_tr

# JSON Search: search keys and values in JSON/TS/TSX files
from .json_search import (
    ProjectIndexer, parse_composite_query, resolve_query,
    extract_top_level_objects_from_ts, guess_line_number
)

# Text Extractor: convert HTML/JSX to JSON structures
# Text Extractor: Now fully integrated in TextExtractorDock (no separate module needed)

# Placeholder Replacer: batch text replacement with mappings
from .placeholder_replacer import (
    parse_mapping_file, replace_placeholders, process_file, process_directory
)

# AI Processor: OpenAI and Gemini integration for file processing
from .ai_processor import (
    OpenAIClient, GeminiClient, AVAILABLE_MODELS, count_tokens, estimate_cost,
    has_internet, is_openai_available, is_gemini_available,
    process_file as ai_process_file, process_multiple_files, save_results,
    list_files_recursive as ai_list_files
)

# Modular GUI Docks: hierarchical architecture with base classes and mixins
from .gui import (
    CaseConverterDock, PlaceholderReplacerDock, JsonSearchDock,
    TextExtractorDock, AIProcessorDock, JsonTranslateDock,
    JsonRewriterDock, HistoryDock, FileListDock, FileExplorerDock, TutorialsDock,
    EditorDock, TextToJsonDock, JSXExtractorDock, DockFactory, MenuBuilder, WindowSettings
)

# Progress Management: widgets for displaying task progress (v2.9.114 - Phase 1.1)
from .gui.progress import (
    ProgressBarWidget, ProgressDetailsDialog,
    ProgressManager, OperationHistory
)

# Search/Replace/Insert Panels: worker and components (v2.9.114 - Phase 1.2 & 1.3)
from .gui.panels import (
    SearchWorker, ResultsTree, MatchPanel, MatchListModel,
    SearchReplacePanel, InsertPanel
)

# CLI Module: command-line interface handlers (v2.9.114 - Phase 3.1)
from .cli import build_parser

# JSON Translate Helpers: dictionary-driven translation (v2.9.114 - Phase 3.2)
from .translators import (
    load_translation_dict, flatten_dict_paths, translate_replace_texts,
    read_translation_dict, apply_scoped_translation, process_translate_file,
    mask_existing_placeholders, unmask_existing_placeholders, RE_PLACEHOLDER
)

# ---------------------------------------------------------------------------
#  Optional import of PySide6 (the CLI subcommands work even if PySide6 is missing)
# ---------------------------------------------------------------------------

_PYSIDE = True

try:
    from PySide6.QtCore import (
        Qt, QAbstractTableModel, QModelIndex, QSize, QTimer, Signal, QByteArray, QAbstractListModel, QObject, QThread
        )
    from PySide6.QtGui import QAction, QActionGroup, QFontDatabase, QPixmap, QIcon, QPalette, QColor, QShortcut, QKeySequence
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QDockWidget, QMessageBox
    )
except Exception:
    _PYSIDE = False
    # Create stub classes for when PySide6 is not available
    class QAbstractListModel: pass
    class QAbstractTableModel: pass
    class QWidget: pass
    class QMainWindow: pass
    class QObject: pass
    class QThread: pass
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
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        cfg.write(f)


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

# def cli_search(args: argparse.Namespace) -> int:
#     patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
#     files = list(walk_files(args.path, args.include, args.exclude))
#     files = filter_files_by_conditions(files, [Condition(*c.split(":",2)) for c in args.cond or []])
#     total = 0
#     for p in files:
#         try:
#             text = read_text(p)
#             for m in patt.finditer(text):
#                 # print 1-based line:col and the line excerpt
#                 line = text.count("\n", 0, m.start()) + 1
#                 col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
#                 excerpt = text.splitlines()[line-1]
#                 print(f"{p}:{line}:{col}: {excerpt.strip()}")
#                 total += 1
#         except Exception as e:
#             print(f"[WARN] {p}: {e}", file=sys.stderr)
#     print(f"\n{total} matches.")
#     return 0


# def cli_replace(args: argparse.Namespace) -> int:
#     patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
#     files = list(walk_files(args.path, args.include, args.exclude))
#     files = filter_files_by_conditions(files, [Condition(*c.split(":",2)) for c in args.cond or []])
#     changed = 0
#     for p in files:
#         try:
#             text = read_text(p)
#             new, n = replace_in_text(text, patt, args.replacement, args.preserve_case, 0 if args.all else 1)
#             if n > 0:
#                 if args.dry_run:
#                     print(f"[DRY] {p}: would replace {n} occurrence(s)")
#                 else:
#                     write_text(p, new)
#                     print(f"[OK ] {p}: replaced {n} occurrence(s)")
#                     changed += 1
#         except Exception as e:
#             print(f"[WARN] {p}: {e}", file=sys.stderr)
#     print(f"\nChanged files: {changed}")
#     return 0


# def cli_insert(args: argparse.Namespace) -> int:
#     files = list(walk_files(args.path, args.include, args.exclude))
#     files = filter_files_by_conditions(files, [Condition(*c.split(":",2)) for c in args.cond or []])
#     changed = 0
#     for p in files:
#         try:
#             text = read_text(p)
#             new = insert_at_line(text, args.line, args.text, args.mode)
#             if new != text:
#                 if args.dry_run:
#                     print(f"[DRY] {p}: would modify")
#                 else:
#                     write_text(p, new)
#                     print(f"[OK ] {p}: modified")
#                     changed += 1
#         except Exception as e:
#             print(f"[WARN] {p}: {e}", file=sys.stderr)
#     print(f"\nChanged files: {changed}")
#     return 0


# def cli_dedupe(args: argparse.Namespace) -> int:
#     raw = read_text(args.input)
#     indent = None if args.indent is not None and args.indent <= 0 else args.indent
#     if args.from_ts or args.input.lower().endswith((".ts",".tsx",".js",".jsx")):
#         if args.ts_out:
#             start,end,block = find_object_block(raw)
#             json_text = ts_block_to_json_text(block)
#             data = parse_json_preserving_duplicates_text(json_text)
#             result = join_keys(data) if args.join_keys else dedupe(data)
#             if args.eliminate_duplicates:
#                 result = eliminate_duplicates(result)
#             body_obj = dump_ts_node(result, indent, 0)
#             out = f"export default {body_obj};\n"
#         else:
#             out = ts_process_full_preserving(raw, indent, args.join_keys, args.eliminate_duplicates)
#     else:
#         # JSON in/out
#         data = parse_json_preserving_duplicates_text(raw)
#         result = join_keys(data) if args.join_keys else dedupe(data)
#         if args.eliminate_duplicates:
#             result = eliminate_duplicates(result)

#         def dump_json(n: JSONNode, ind: Optional[int], lvl: int) -> str:
#             if isinstance(n, Obj):
#                 if not n: return "{}"
#                 if ind is None or ind <= 0:
#                     parts = ["{"] + [("," if i else "") + json.dumps(k, ensure_ascii=False) + ":" + dump_json(v, ind, lvl)
#                                      for i,(k,v) in enumerate(n)] + ["}"]
#                     return "".join(parts)
#                 sp = " " * ind
#                 parts = ["{\n"]
#                 for i,(k,v) in enumerate(n):
#                     if i: parts.append(",\n")
#                     parts.append(sp*(lvl+1) + json.dumps(k, ensure_ascii=False) + ": " + dump_json(v, ind, lvl+1))
#                 parts.append("\n" + sp*lvl + "}")
#                 return "".join(parts)
#             if isinstance(n, list):
#                 if not n: return "[]"
#                 if ind is None or ind <= 0:
#                     parts = ["["] + [("," if i else "") + dump_json(v, ind, lvl)
#                                      for i,v in enumerate(n)] + ["]"]
#                     return "".join(parts)
#                 sp = " " * ind
#                 parts = ["[\n"]
#                 for i,v in enumerate(n):
#                     if i: parts.append(",\n")
#                     parts.append(sp*(lvl+1) + dump_json(v, ind, lvl+1))
#                 parts.append("\n" + sp*lvl + "]")
#                 return "".join(parts)
#             return json.dumps(n, ensure_ascii=False)
#         out = dump_json(result, indent, 0) + "\n"

#     if args.no_line_break:
#         out = collapse_blank_lines(out)

#     if args.output:
#         write_text(args.output, out)
#     else:
#         sys.stdout.write(out)
#     return 0


# =============================================================================
#                                   GUI
# =============================================================================

if _PYSIDE:
    # ResultsTree now imported from src.gui.results_tree (Phase 3.11 - Import Tree Analogy: FOLHA)
    from .gui.results_tree import ResultsTree

    # ============================ Code-aware JSON Translator ============================
    # CodeAwareJSONTranslator removed - unused (COM4 - 2026-01-29)
    class MainWindow(QMainWindow):
        def __init__(self, app: QApplication):
            super().__init__()

            # Fix: Configure window flags for Linux compatibility (v2.9.117)
            # Linux window managers (X11/Wayland) require explicit WindowMaximizeButtonHint
            # to show the maximize button [□] in the title bar alongside [_] and [×]
            from PySide6.QtCore import Qt

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

            # Restore last layout (v2.9.84)
            self.layout_manager.restore_last_layout()

            # Force UI update to ensure widgets are properly rendered (fix for invisible widgets on startup)
            self.updateGeometry()
            QApplication.processEvents()

            # Apply accessibility features (v2.9.35)
            self._apply_accessibility()

            # Restore tab state from previous session (v2.9.40)
            self._restore_tab_state()

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
                print(f"Error loading icon from assets: {exc}")
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
                    print("Error loading QPixmap icon data.")
                    # Handle the error, perhaps use a default icon or stop
                    icon = QIcon() # empty icon
                else:
                    # Optional: Resize the pixmap if necessary before creating the QIcon
                    # pixmap = pixmap.scaled(64, 64, aspect_ratio_mode=Qt.KeepAspectRatio)

                    # 4. Create a QIcon from QPixmap
                    icon = QIcon(pixmap)

            except Exception as exc:
                print(f"Error processing base64 string or creating icon: {exc}")
                icon = QIcon() # Empty icon on error

            # 5. Set the icon for the main window
            self.setWindowIcon(icon)

        def _open_trans(self):
            DockFactory.create_json_translate_dock(self)

        def _open_rewrite(self):
            DockFactory.create_json_rewriter_dock(self)

        def _open_text_extractor(self):
            DockFactory.create_text_extractor_dock(self)

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
                'open_in_editor_requested': self._load_json_from_converter
            }
            DockFactory.create_text_to_json_dock(self, signal_connections=signal_connections)

        def _load_json_from_converter(self, json_str: str):
            """Load JSON from text converter into main editor."""
            if not hasattr(self, 'dock_editor'):
                self._open_editor()
            self.dock_editor.load_json_string(json_str)
            self.dock_editor.show()

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
            if not hasattr(self, 'dock_history'):
                self._open_history()

            if checked:
                self.dock_history.show()
            else:
                self.dock_history.hide()

        # Lazy-loading show methods for tools as tabs (v2.9.40)

        def _show_search_replace(self):
            """Show Search/Replace tab (v2.9.40.2 - reopen if closed)."""
            # Check if tab exists at index 0
            if self.tabs.count() > 0 and self.tabs.tabText(0) == "Search / Replace":
                self.tabs.setCurrentIndex(0)
            else:
                # Tab was closed, recreate at index 0 using internal SearchReplacePanel class
                self.tab_search = SearchReplacePanel(parent=self, progress_manager=self.progress_manager)
                self.tabs.insertTab(0, self.tab_search, "Search / Replace")
                self.tabs.setCurrentIndex(0)
                QApplication.processEvents()

        def _show_insert(self):
            """Show Insert tab (v2.9.40.2 - reopen if closed)."""
            # Check if tab exists at index 1
            expected_index = 1
            if self.tabs.count() > expected_index and self.tabs.tabText(expected_index) == "Insert":
                self.tabs.setCurrentIndex(expected_index)
            else:
                # Tab was closed, recreate at index 1
                # InsertPanel is an internal class defined in this file, no import needed
                self.tab_insert = InsertPanel(parent=self, progress_manager=self.progress_manager)
                self.tabs.insertTab(expected_index, self.tab_insert, "Insert")
                self.tabs.setCurrentIndex(expected_index)
                QApplication.processEvents()

        def _show_translate(self):
            """Show JSON Translate as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_translate(self)

        def _show_rewriter(self):
            """Show JSON Rewriter as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_rewriter(self)

        def _show_text_extractor(self):
            """Show Text Extractor as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_text_extractor(self)

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

        def _show_text_to_json(self):
            """Show converter selection dialog and open chosen dock."""
            from .gui.converter_selection_dialog import ConverterSelectionDialog

            converter = ConverterSelectionDialog.get_converter_choice(self)
            if converter == ConverterSelectionDialog.JSX_EXTRACTOR:
                self._show_jsx_extractor()
            elif converter == ConverterSelectionDialog.TEXT_CONVERTER:
                self._show_text_format_converter()

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

        def _show_advanced_extractor(self):
            """Show Advanced Extractor as tab (v2.9.115 - Sprint 2)."""
            from .gui.dock_factory import DockFactory
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
            from .settings_manager import SettingsManager

            # Get Gemini API key from settings
            settings = SettingsManager()
            api_key = settings.get_value('ai_processor/gemini_api_key', '')

            dialog = TutorialAssistantDialog(self, api_key=api_key)
            dialog.show()

        def _about_dialog(self):
            """Show About Clarify dialog."""
            from PySide6.QtWidgets import QMessageBox
            about_text = """<h2>Clarify</h2>
            <p><b>Text Processing Tool</b></p>
            <p>Version: 2.9.64 (Logging System Integration)</p>
            <p>A powerful tool for JSON processing, translation, AI integration, and more.</p>
            <p><a href="https://github.com/JosueAmaral15/clarify">GitHub Repository</a></p>
            <p>© 2025 Josue Amaral</p>
            """
            QMessageBox.about(self, "About Clarify", about_text)

        def _view_logs(self):
            """
            Open log file in default text editor (v2.9.64).

            Uses system default application to open the log file for viewing.
            Falls back to showing path if opening fails.
            """
            from .utils.logger import get_log_file
            from PySide6.QtWidgets import QMessageBox
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
                    subprocess.run(["xdg-open", str(log_file)], check=False)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", str(log_file)], check=False)
                elif system == "Windows":
                    os.startfile(str(log_file))
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

            # Perform check in background thread to avoid blocking startup
            from PySide6.QtCore import QTimer

            # Delay check by 3 seconds to avoid slowing down startup
            QTimer.singleShot(3000, self._perform_update_check)

        def _check_for_updates_manual(self):
            """
            Manual update check triggered from Help menu (v2.9.45).

            Forces fresh check (bypasses cache) and shows result with ManualCheckDialog.
            """
            from .update_checker import check_for_updates
            from . import __version__
            from .gui.update_notification_dialog import ManualCheckDialog
            from PySide6.QtCore import QTimer

            # Create and show dialog
            dialog = ManualCheckDialog(self)
            dialog.show_checking()

            # Process events to show dialog
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()

            # Force fresh check
            has_update, release_info = check_for_updates(__version__, force=True)

            # Build result dict
            result = {
                "success": True,
                "current_version": __version__,
                "update_available": has_update
            }

            if has_update and release_info:
                result["latest_version"] = release_info.get('version', 'Unknown')

                # Check if user opted to skip this version
                from .gui.update_notification_dialog import UpdateNotificationDialog

                if UpdateNotificationDialog.should_show_for_version(release_info['version']):
                    # Show update dialog after a brief delay
                    QTimer.singleShot(1000, lambda: self._show_update_dialog(release_info))

            # Show result in manual check dialog
            dialog.show_result(result)

        def _perform_update_check(self):
            """
            Perform background update check (v2.9.45).

            Called by auto-check timer. Silent operation - only shows dialog if update found.
            """
            from .update_checker import check_for_updates
            from . import __version__

            try:
                has_update, release_info = check_for_updates(__version__, force=False)

                if has_update and release_info:
                    # Check if user opted to skip this version
                    from .gui.update_notification import UpdateNotificationDialog

                    if UpdateNotificationDialog.should_show_for_version(release_info['version']):
                        self._show_update_dialog(release_info)
                    # else: silently skip (user previously opted out)
                # else: no update or error - stay silent

            except Exception as e:
                # Silent failure - don't bother user during startup
                print(f"[Update Check] Failed silently: {e}")

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
            if not hasattr(self, 'dock_editor'):
                from .gui import EditorDock
                self.dock_editor = EditorDock(self)
            self._add_tool_tab(self.dock_editor, "Editor", "editor")

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
            # Check if tool is already open
            if tool_name in self.tool_tabs:
                existing_widget, existing_index = self.tool_tabs[tool_name]
                # Switch to existing tab
                self.tabs.setCurrentIndex(existing_index)
                return existing_index

            # Add new tab
            tab_index = self.tabs.addTab(widget, title)

            # Track the tab
            self.tool_tabs[tool_name] = (widget, tab_index)

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

            # Check for unsaved changes (only for Editor)
            if hasattr(widget, 'has_unsaved_changes') and callable(widget.has_unsaved_changes):
                if widget.has_unsaved_changes():
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self,
                        tr("dialog.unsaved_title"),
                        tr("dialog.unsaved_message", tab_title=tab_title),
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

            # Fix: Restore MainWindow window flags after removing tab (v2.9.117)
            # QDockWidget as tab can interfere with MainWindow flags on Linux
            self._restore_window_flags()

            # Remove from tracking dict
            tool_name_to_remove = None
            for tool_name, (tracked_widget, tracked_index) in self.tool_tabs.items():
                if tracked_widget == widget:
                    tool_name_to_remove = tool_name
                    break

            if tool_name_to_remove:
                del self.tool_tabs[tool_name_to_remove]

                # Update indices of remaining tools
                updated_tools = {}
                for tool_name, (tracked_widget, tracked_index) in self.tool_tabs.items():
                    if tracked_index > index:
                        updated_tools[tool_name] = (tracked_widget, tracked_index - 1)
                    else:
                        updated_tools[tool_name] = (tracked_widget, tracked_index)
                self.tool_tabs = updated_tools

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
                current_flags = self.windowFlags()
                if current_flags != self._desired_window_flags:
                    # Flags were modified - restore them
                    self.setWindowFlags(self._desired_window_flags)
                    # Show window again (setWindowFlags hides window)
                    self.show()

        def _apply_tab_close_button_style(self):
            """Apply theme-appropriate styling to tab close buttons (v2.9.40)."""
            # Get current theme
            current_theme = self.settings.get("theme", "system")

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
            # Get list of open tool names (exclude Search/Replace and Insert)
            open_tools = []
            for tool_name, (widget, index) in self.tool_tabs.items():
                open_tools.append(tool_name)

            # Check if fixed tabs are still open (v2.9.112)
            fixed_tabs_open = {
                "search_replace": self.tabs.count() > 0 and self.tabs.widget(0) == self.tab_search,
                "insert": self.tabs.count() > 1 and self.tabs.widget(1) == self.tab_insert
            }

            # Save to settings
            self.settings.set("tabs_open_tools", open_tools)
            self.settings.set("tabs_fixed_open", fixed_tabs_open)  # Track if fixed tabs are open
            self.settings.set("tabs_current_index", self.tabs.currentIndex())

        def _restore_tab_state(self):
            """Restore tab state from settings on startup (v2.9.40).
            v2.9.112: Don't restore fixed tabs if they were closed."""
            # Check if fixed tabs should be restored (v2.9.112)
            fixed_tabs_open = self.settings.get("tabs_fixed_open", {"search_replace": True, "insert": True})

            # Remove fixed tabs if they were closed in previous session
            if not fixed_tabs_open.get("search_replace", True):
                # Remove Search/Replace tab (index 0)
                if self.tabs.count() > 0 and self.tabs.widget(0) == self.tab_search:
                    self.tabs.removeTab(0)

            if not fixed_tabs_open.get("insert", True):
                # Remove Insert tab (check current index since Search/Replace might be removed)
                for i in range(self.tabs.count()):
                    if self.tabs.widget(i) == self.tab_insert:
                        self.tabs.removeTab(i)
                        break

            # Get list of tools that were open
            open_tools = self.settings.get("tabs_open_tools", [])

            if not open_tools:
                return  # No tabs to restore

            # Reopen each tool
            for tool_name in open_tools:
                # Map tool_name to _show_* method
                method_name = f"_show_{tool_name}"
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method()

            # Restore active tab
            import logging
            logger = logging.getLogger(__name__)

            saved_index = self.settings.get("tabs_current_index", 0)
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
            mode = "system" if action is self.act_theme_system else ("light" if action is self.act_theme_light else "dark")
            apply_theme(QApplication.instance(), mode)
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

        def translate_json(self, data, lang):
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

        def _switch_language(self, lang: str):
            """Switch application language at runtime (Task #24 - v2.9.10, expanded v2.9.43)."""
            # QActionGroup handles radio button behavior automatically - no need to setChecked
            # Just switch language and save preference

            print(f"[Language] Switching to: {lang}")
            print(f"[Language] Current language before switch: {self.translator.current_language}")

            # Switch language
            switch_language(lang)

            print(f"[Language] Current language after switch: {self.translator.current_language}")

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

        def _on_language_changed(self, lang: str):
            """Called when language changes - retranslate all UI (Task #24 - v2.9.10)."""
            self._retranslate_ui()

        def _retranslate_ui(self):
            """Retranslate all UI elements (Task #24 - v2.9.10)."""
            # Window title
            self.setWindowTitle(tr("app.title"))

            # Update menu texts
            self.act_undo.setText(tr("menu.edit.undo"))
            self.act_redo.setText(tr("menu.edit.redo"))
            self.act_open_translate.setText(tr("menu.tools.json_translate"))
            self.act_open_rewriter.setText(tr("menu.tools.json_rewriter"))
            self.act_open_text_extractor.setText(tr("menu.tools.text_extractor"))
            self.act_open_placeholder_replacer.setText(tr("menu.tools.placeholder_replacer"))
            self.act_open_ai_processor.setText(tr("menu.tools.ai_processor"))
            self.act_open_json_search.setText(tr("menu.tools.json_search"))
            self.act_open_case_converter.setText(tr("menu.tools.case_converter"))
            self.act_toggle_history.setText(tr("menu.view.history"))
            self.act_theme_system.setText(tr("menu.themes.system"))
            self.act_theme_light.setText(tr("menu.themes.light"))
            self.act_theme_dark.setText(tr("menu.themes.dark"))

            # Rebuild menu bar to update menu titles
            self.menuBar().clear()
            self._build_menu()

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
                "editor": getattr(self, "editor_dock", None),
                "search": getattr(self, "tab_search", None),
                "replace": getattr(self, "replace_panel", None),
                "insert": getattr(self, "insert_panel", None),
                "set_operations": getattr(self, "set_operations_dock", None),
                "rewriter": getattr(self, "rewriter_dock", None),
                "translate": getattr(self, "translate_dock", None),
                "ai_processor": getattr(self, "ai_processor_dock", None),
                "case_converter": getattr(self, "case_converter_dock", None),
                "json_search": getattr(self, "json_search_dock", None),
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
                from PySide6.QtWidgets import QMessageBox
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
            """Show keyboard shortcuts help page (read-only view)."""
            from .shortcut_manager import ShortcutManager
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QLabel

            dialog = QDialog(self)
            dialog.setWindowTitle("Keyboard Shortcuts Reference")
            dialog.setMinimumSize(700, 600)

            layout = QVBoxLayout()

            # Search box
            search_layout = QHBoxLayout()
            search_label = QLabel(tr("app.lbl_shortcuts_search"))
            search_box = QLineEdit()
            search_box.setPlaceholderText(tr("app.placeholder_shortcuts"))
            search_layout.addWidget(search_label)
            search_layout.addWidget(search_box)
            layout.addLayout(search_layout)

            # Text view
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(ShortcutManager.format_shortcuts_table())
            text_edit.setStyleSheet("font-family: monospace;")
            layout.addWidget(text_edit)

            # Filter function
            def filter_text():
                search_text = search_box.text().lower()
                full_text = ShortcutManager.format_shortcuts_table()

                if not search_text:
                    text_edit.setPlainText(full_text)
                    return

                # Filter lines containing search text
                filtered_lines = []
                for line in full_text.split('\n'):
                    if search_text in line.lower():
                        filtered_lines.append(line)

                text_edit.setPlainText('\n'.join(filtered_lines))

            search_box.textChanged.connect(filter_text)

            # Buttons
            btn_layout = QHBoxLayout()

            customize_btn = QPushButton(tr("app.btn_customize"))
            customize_btn.setToolTip(tooltip_tr("app.tooltip_customize"))
            customize_btn.clicked.connect(lambda: (dialog.close(), self._show_shortcuts()))

            close_btn = QPushButton(tr("app.btn_close"))
            close_btn.clicked.connect(dialog.accept)

            btn_layout.addWidget(customize_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)

            layout.addLayout(btn_layout)

            dialog.setLayout(layout)
            dialog.exec()

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
                (self.act_open_text_extractor, "open_text_extractor", "Extract text from files"),
                (self.act_open_text_to_json, "open_text_to_json", "Convert text to JSON"),
                (self.act_open_placeholder_replacer, "open_placeholder_replacer", "Replace placeholders in text"),
                (self.act_open_translate, "open_translate", "Translate JSON content"),
                (self.act_open_file_explorer, "open_file_explorer", "Unified file explorer with advanced search"),

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

                # Update tooltip with shortcut
                shortcut = ShortcutManager.get_shortcut(shortcut_name)
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
                    f"{tr('app.msg_undo_title')}: {self.command_manager.get_redo_description() or tr('app.msg_success_title')}"
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
                    f"{tr('app.msg_redo_title')}: {self.command_manager.get_undo_description() or tr('app.msg_success_title')}"
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

        def keyPressEvent(self, event):
            """Handle global keyboard shortcuts (v2.9.33 + v2.9.35 accessibility)."""
            from PySide6.QtCore import Qt

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
            from PySide6.QtCore import Qt, QEvent

            # Only handle wheel events
            if event.type() != QEvent.Wheel:
                return super().eventFilter(obj, event)

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
            return super().eventFilter(obj, event)

        def wheelEvent(self, event):
            """Handle mouse wheel for font scaling (v2.9.35)."""
            from PySide6.QtCore import Qt

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
        print("\nPySide6 is not installed; install it or use the CLI subcommands.", file=sys.stderr)
        return 2

    # Set Qt attributes before creating QApplication
    from PySide6.QtCore import Qt
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)

    app = QApplication(sys.argv)
    win = MainWindow(app)
    win.resize(1200, 400)
    win.show()

    # Force immediate rendering of all widgets (fix for invisible widgets on startup)
    win.repaint()
    app.processEvents()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
