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
from .i18n import get_translator, switch_language, tr

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
    JsonRewriterDock, HistoryDock, FileListDock, TutorialsDock,
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
        QLabel, QLineEdit, QCheckBox, QPushButton, QSplitter, QListWidget, QListWidgetItem,
        QFileDialog, QGroupBox, QComboBox, QSpinBox, QTreeWidget, QTreeWidgetItem,
        QPlainTextEdit, QDockWidget, QMessageBox, QTabWidget, QFormLayout, QListView,
        QProgressBar, QDialog, QTextEdit, QScrollArea, QRadioButton, QMenu
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

from src.ui import thread_manager, FeatureType, ProcessingModal

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

    class ResultsTree(QTreeWidget):
        """
        Tree view similar to VS Code's search results:
            File
              line:col  text preview
        v2.9.2: Added context menu with copy, select all, open file(s) and multi-selection support.
        """
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setHeaderLabels(["Match"])
            self.setRootIsDecorated(True)
            self.setColumnCount(1)
            self.setUniformRowHeights(True)
            self._matches_data: Dict[str, List[Tuple[int,int,str]]] = {}
            
            # Enable multi-selection with CTRL/Shift (v2.9.2)
            self.setSelectionMode(QTreeWidget.ExtendedSelection)
            
            # Enable context menu (v2.9.2)
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self._show_context_menu)
            
            # Enable mouse tracking for hover effects (v2.5.1)
            self.setMouseTracking(True)
            self.itemEntered.connect(self._on_item_hover)
            
            # Status label at bottom of tree (v2.5.1)
            self._status_label = None  # Will be set by parent
        
        def set_status_label(self, label):
            """Set the status label widget for showing position info (v2.5.1)."""
            self._status_label = label
        
        def _on_item_hover(self, item: QTreeWidgetItem, column: int):
            """Show position info when hovering over match items (v2.5.1)."""
            if item and item.parent():  # This is a match item (has parent = file item)
                text = item.text(0)
                # Extract line:col from the beginning of text
                if ':' in text:
                    try:
                        pos_part = text.split()[0]  # Get "line:col" part
                        line, col = pos_part.split(':')
                        
                        # Get file path from parent
                        file_path = item.parent().text(0)
                        
                        # Set tooltip
                        tooltip = f"File: {file_path}\nLine: {line}\nColumn: {col}"
                        item.setToolTip(0, tooltip)
                        
                        # Update status label if available
                        if self._status_label:
                            self._status_label.setText(f"📍 Position: Line {line}, Column {col} | File: {file_path}")
                    except:
                        pass
            else:
                # Clear status for non-match items
                if self._status_label:
                    self._status_label.setText("")

        def populate(self, matches: Dict[str, List[Tuple[int,int,str]]], sort_results: bool = False):
            self.setUpdatesEnabled(False)
            try:
                self.clear()
                self._matches_data = matches  # Store for export
                
                # Calculate statistics
                total_files = len(matches)
                total_matches = sum(len(items) for items in matches.values())
                
                # Add summary header at the top
                if total_files > 0:
                    summary = QTreeWidgetItem([f"📊 Results: {total_matches} matches in {total_files} file(s)"])
                    summary.setForeground(0, QColor(0, 150, 0))  # Green color
                    font = summary.font(0)
                    font.setBold(True)
                    summary.setFont(0, font)
                    self.addTopLevelItem(summary)
                
                # Sort file paths if requested (v2.9.5)
                paths = sorted(matches.keys()) if sort_results else matches.keys()
                
                # Add file matches
                for path in paths:
                    items = matches[path]
                    top = QTreeWidgetItem([path])
                    self.addTopLevelItem(top)
                    
                    # Sort items by line number if requested
                    if sort_results:
                        items = sorted(items, key=lambda x: (x[0], x[1]))  # Sort by line, then col
                    
                    for line, col, snippet in items:
                        leaf = QTreeWidgetItem([f"{line}:{col}  {snippet.strip()}"])
                        top.addChild(leaf)
                self.expandAll()
            finally:
                self.setUpdatesEnabled(True)
        
        def print_message(self, message : str = ""):
            self.setUpdatesEnabled(False)
            try:
                self.clear()
                self._matches_data = {}  # Clear data when showing message
                top = QTreeWidgetItem([message])  # Fixed: QTreeWidgetItem expects list of strings
                self.addTopLevelItem(top)
                self.expandAll()
            finally:
                self.setUpdatesEnabled(True)
        
        def get_matches_data(self) -> Dict[str, List[Tuple[int,int,str]]]:
            """Return current matches data for export."""
            return self._matches_data
        
        def export_to_text(self) -> str:
            """
            Export matches to formatted text string.
            Returns empty string if no matches.
            """
            if not self._matches_data:
                return ""
            
            lines = []
            total_files = len(self._matches_data)
            total_matches = sum(len(items) for items in self._matches_data.values())
            
            # Header
            lines.append("=" * 80)
            lines.append("CLARIFY - SEARCH RESULTS")
            lines.append("=" * 80)
            lines.append(f"Total files with matches: {total_files}")
            lines.append(f"Total matches: {total_matches}")
            lines.append("=" * 80)
            lines.append("")
            
            # Results by file
            for file_path, items in self._matches_data.items():
                lines.append(f"📁 {file_path}")
                lines.append(f"   Matches: {len(items)}")
                lines.append("-" * 80)
                
                for line_num, col, snippet in items:
                    lines.append(f"   Line {line_num}, Col {col}:")
                    lines.append(f"      {snippet.strip()}")
                
                lines.append("")
            
            return "\n".join(lines)
        
        def _show_context_menu(self, position):
            """Show context menu at cursor position (v2.9.2)."""
            menu = QMenu(self)
            
            # Get selected items
            selected_items = self.selectedItems()
            has_selection = len(selected_items) > 0
            
            # Copy action
            copy_action = menu.addAction("📋 Copy")
            copy_action.setEnabled(has_selection)
            copy_action.triggered.connect(self._copy_selected)
            
            # Copy all action
            copy_all_action = menu.addAction("📋 Copy All Results")
            copy_all_action.setEnabled(bool(self._matches_data))
            copy_all_action.triggered.connect(self._copy_all)
            
            menu.addSeparator()
            
            # Select all action
            select_all_action = menu.addAction("✅ Select All")
            select_all_action.triggered.connect(self.selectAll)
            
            menu.addSeparator()
            
            # Open file(s) actions
            open_file_action = menu.addAction("📂 Open File")
            open_file_action.setEnabled(has_selection)
            open_file_action.triggered.connect(self._open_selected_files)
            
            open_all_action = menu.addAction("📂 Open All Files")
            open_all_action.setEnabled(bool(self._matches_data))
            open_all_action.triggered.connect(self._open_all_files)
            
            # Show menu at cursor position
            menu.exec_(self.mapToGlobal(position))
        
        def _copy_selected(self):
            """Copy selected items to clipboard (v2.9.2)."""
            selected_items = self.selectedItems()
            if not selected_items:
                return
            
            lines = []
            for item in selected_items:
                # Skip summary header
                if item.text(0).startswith("📊 Results:"):
                    continue
                
                # If it's a file item (no parent)
                if not item.parent():
                    lines.append(f"\n📁 {item.text(0)}")
                    lines.append("-" * 80)
                # If it's a match item (has parent)
                else:
                    lines.append(f"   {item.text(0)}")
            
            text = "\n".join(lines)
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Show feedback
            if self._status_label:
                self._status_label.setText(f"✅ Copied {len(selected_items)} item(s) to clipboard")
                QTimer.singleShot(3000, lambda: self._status_label.setText(""))
        
        def _copy_all(self):
            """Copy all results to clipboard (v2.9.2)."""
            text = self.export_to_text()
            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                
                # Show feedback
                if self._status_label:
                    total_matches = sum(len(items) for items in self._matches_data.values())
                    self._status_label.setText(f"✅ Copied all results ({total_matches} matches) to clipboard")
                    QTimer.singleShot(3000, lambda: self._status_label.setText(""))
        
        def _open_selected_files(self):
            """Open selected files in system default application (v2.9.2)."""
            selected_items = self.selectedItems()
            if not selected_items:
                return
            
            # Collect unique file paths from selection
            file_paths = set()
            for item in selected_items:
                # Skip summary header
                if item.text(0).startswith("📊 Results:"):
                    continue
                
                # If it's a file item (no parent), use it directly
                if not item.parent():
                    file_paths.add(item.text(0))
                # If it's a match item, get parent file path
                else:
                    parent_text = item.parent().text(0)
                    if not parent_text.startswith("📊"):
                        file_paths.add(parent_text)
            
            # Open each file
            opened_count = 0
            for path in file_paths:
                if os.path.isfile(path):
                    try:
                        if sys.platform.startswith("darwin"):
                            os.system(f'open "{path}"')
                        elif os.name == "nt":
                            os.system(f'start "" "{path}"')
                        else:
                            os.system(f'xdg-open "{path}"')
                        opened_count += 1
                    except Exception as e:
                        print(f"Error opening {path}: {e}")
            
            # Show feedback
            if self._status_label and opened_count > 0:
                self._status_label.setText(f"✅ Opened {opened_count} file(s)")
                QTimer.singleShot(3000, lambda: self._status_label.setText(""))
        
        def _open_all_files(self):
            """Open all files from results in system default application (v2.9.2)."""
            if not self._matches_data:
                return
            
            # Ask for confirmation if many files
            file_count = len(self._matches_data)
            if file_count > 10:
                reply = QMessageBox.question(
                    self,
                    "Open Many Files",
                    f"You are about to open {file_count} files. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Open each file
            opened_count = 0
            for path in self._matches_data.keys():
                if os.path.isfile(path):
                    try:
                        if sys.platform.startswith("darwin"):
                            os.system(f'open "{path}"')
                        elif os.name == "nt":
                            os.system(f'start "" "{path}"')
                        else:
                            os.system(f'xdg-open "{path}"')
                        opened_count += 1
                    except Exception as e:
                        print(f"Error opening {path}: {e}")
            
            # Show feedback
            if self._status_label and opened_count > 0:
                self._status_label.setText(f"✅ Opened {opened_count} file(s)")
                QTimer.singleShot(3000, lambda: self._status_label.setText(""))


    # ============================ Code-aware JSON Translator ============================

    class CodeAwareJSONTranslator:
        """
        Translate visible text to {<root>.<path>} using a dictionary (and inverse).
        Goals:
        • Translate only in "code scope" that makes sense:
            - JSX text nodes (between '>' and '<')
            - String literals in code
            and SKIP:
            - Anything inside {...} expressions
            - Inside JSX tags/attributes (<Tag ...>)
            - Type annotations and identifiers like React.ReactNode
        • Configurable root alias (default: 't'), e.g. {t.pages.home.title}
        • Never break existing placeholders; protect existing {root.*} blocks
        • Inverse: turn {root.*} back into original strings using the same dictionary
        """

        _re_jsx_tag = re.compile(r"<[^>]*>")  # a rough "inside tag" region
        _re_placeholder = re.compile(r"\{([A-Za-z_]\w*)(?:\.[A-Za-z0-9_]+)+\}")  # {t.pages.home.title}
        _re_string = re.compile(
            r"""
            (?P<q>['"])                # opening quote
            (?P<body>(?:\\.|(?!\1).)*) # body allowing escapes
            \1                         # closing quote
            """,
            re.VERBOSE | re.DOTALL,
        )

        _SMART_TO_STRAIGHT = str.maketrans({
            "’": "'", "‘": "'", "‛": "'",
            "“": '"', "”": '"', "‟": '"',
        })

        def __init__(self, dictionary: dict, root_name: str = "t"):
            self.root = root_name
            # flat: "pages.contact.hero.subtitle" -> "We\'re here ..."
            self.flat = self._flatten(dictionary)

            # Build variants → key map (multiple textual forms for each value)
            pairs: list[tuple[str, str]] = []
            for key, val in self.flat.items():
                if not isinstance(val, str) or not val.strip():
                    continue
                for vv in self._variants_for_value(val):
                    pairs.append((vv, key))

            # Sort by length (desc) so longer phrases win and avoid partial overlaps
            pairs.sort(key=lambda kv: len(kv[0]), reverse=True)

            # Keep as lists for fast iteration in the scanner
            self._variant_values = [p[0] for p in pairs]
            self._variant_keys   = [p[1] for p in pairs]


        @staticmethod
        def _normalize_quotes(s: str) -> str:
            """Normalize curly quotes to straight, and unescape common HTML entities."""
            if not isinstance(s, str):
                return s
            s2 = s.translate(CodeAwareJSONTranslator._SMART_TO_STRAIGHT)
            # normalize common HTML entities
            s2 = s2.replace("&apos;", "'").replace("&#39;", "'") \
                .replace("&quot;", '"').replace("&#34;", '"')
            return s2

        @staticmethod
        def _unescape_backslashes(s: str) -> str:
            """
            Convert common backslash-escaped quotes into literal quotes, without touching other escapes.
            We handle simple forms: \' and \"
            """
            if not isinstance(s, str):
                return s
            return s.replace(r"\'", "'").replace(r"\"", '"')

        @staticmethod
        def _variants_for_value(v: str) -> list[str]:
            """
            Generate acceptable textual variants for a dictionary value:
            - raw v
            - normalized smart quotes → straight
            - unescaped (\' → ')
            - HTML-entity-decoded variants
            - combinations thereof
            Deduplicated, keep non-empty strings only.
            """
            if not isinstance(v, str) or not v.strip():
                return []

            variants = set()
            base = v

            # 1) raw
            variants.add(base)

            # 2) unescape backslash quotes
            unesc = CodeAwareJSONTranslator._unescape_backslashes(base)
            variants.add(unesc)

            # 3) normalize smart + html entities on both
            for s in (base, unesc):
                s2 = CodeAwareJSONTranslator._normalize_quotes(s)
                variants.add(s2)

                # Also try entity→char then normalize (covers cases like &apos; already in source)
                s3 = (s.replace("&apos;", "'")
                        .replace("&#39;", "'")
                        .replace("&quot;", '"')
                        .replace("&#34;", '"'))
                variants.add(CodeAwareJSONTranslator._normalize_quotes(s3))

            # 4) last-pass trim (no-op if not needed)
            return [x for x in variants if x]

        # ---------- public API ----------

        def translate_text_to_refs(self, content: str) -> str:
            """
            Forward: Replace visible text with {root.path}.
            Only in safe scopes (JSX text nodes and string literals), never inside {...} or tags.
            """
            if not content.strip():
                return content

            # 0) protect existing placeholders so we never touch inside/around them
            content, guards = self._mask_existing_placeholders(content)

            # 1) replace in JSX text nodes (outside tags and outside {...})
            content = self._replace_in_jsx_text_nodes(content)

            # 2) replace in string literals (again skipping {...})
            content = self._replace_in_string_literals(content)

            # 3) unmask placeholders
            content = self._unmask_placeholders(content, guards)
            
            # 4) consolidate fragmented placeholders (auto-fix)
            content = self._consolidate_fragmented_placeholders(content)
            
            return content

        def translate_refs_to_text(self, content: str) -> str:
            """
            Inverse: Replace {root.path.to.key} with dictionary value.
            Only if key exists; otherwise leave as-is.
            """
            def _repl(m: re.Match) -> str:
                alias = m.group(1)
                if alias != self.root:
                    return m.group(0)
                keypath = m.group(0)[1:-1]  # strip {}
                val = self.flat.get(keypath[len(self.root) + 1 :], None) if "." in keypath else None
                return val if isinstance(val, str) else m.group(0)

            return self._re_placeholder.sub(_repl, content)

        # ---------- core steps ----------

        def _replace_in_jsx_text_nodes(self, s: str) -> str:
            """
            Replace plain text BETWEEN '>' and '<', excluding braces blocks and tags.
            """
            out = []
            i = 0
            n = len(s)
            while i < n:
                gt = s.find(">", i)
                if gt == -1:
                    out.append(s[i:])
                    break
                out.append(s[i:gt + 1])  # include '>'
                lt = s.find("<", gt + 1)
                if lt == -1:
                    # trailing text node to EOF
                    segment = s[gt + 1 :]
                    out.append(self._replace_outside_braces(segment))
                    break
                segment = s[gt + 1 : lt]
                out.append(self._replace_outside_braces(segment))
                i = lt
            return "".join(out)

        def _replace_in_string_literals(self, s: str) -> str:
            """
            Replace only inside string literals, but not if the string looks like a type/identifier blob.
            """
            out = []
            last = 0
            for m in self._re_string.finditer(s):
                out.append(s[last : m.start()])
                q = m.group("q")
                body = m.group("body")
                new_body = self._replace_outside_braces(body, inside_string=True)
                out.append(q + new_body + q)
                last = m.end()
            out.append(s[last:])
            return "".join(out)

        def _replace_outside_braces(self, text: str, inside_string: bool = False) -> str:
            """
            Replace occurrences of known values with {root.key} only when NOT inside {...}.
            Heuristics:
            • Skip chunks that obviously look like identifiers/types (contain dots and no spaces)
            • Don’t replace if either neighbor char is alnum or '.' (avoid breaking identifiers)
            """
            if not text.strip():
                return text

            # quick skip: likely code-ish (React.ReactNode etc.) with no spaces
            if not inside_string and "." in text and " " not in text.strip():
                return text

            out = []
            i = 0
            depth = 0
            while i < len(text):
                ch = text[i]
                if ch == "{":
                    depth += 1
                    out.append(ch)
                    i += 1
                    continue
                if ch == "}":
                    depth = max(0, depth - 1)
                    out.append(ch)
                    i += 1
                    continue

                if depth == 0:
                    # Try to match any known variant at this position
                    replaced = False
                    for idx, val in enumerate(self._variant_values):
                        if not val:
                            continue
                        if text.startswith(val, i):
                            left = text[i - 1] if i > 0 else ""
                            right = text[i + len(val)] if i + len(val) < len(text) else ""
                            # neighbors: don’t glue into identifiers or dotted tokens
                            if (left.isalnum() or left == ".") or (right.isalnum() or right == "."):
                                continue
                            key = self._variant_keys[idx]
                            out.append("{" + self.root + "." + key + "}")
                            i += len(val)
                            replaced = True
                            break
                    if replaced:
                        continue


                # default
                out.append(ch)
                i += 1

            return "".join(out)

        # ---------- fragmentation consolidation ----------

        def _consolidate_fragmented_placeholders(self, s: str) -> str:
            """
            Auto-fix fragmented placeholders: merge adjacent placeholders into single unit.
            Example: '{t.our} {t.products}' → '{t.ourProducts}' (if values are "our" and "products")
            
            Algorithm:
            1. Find sequences of 2+ adjacent placeholders (separated only by whitespace)
            2. Retrieve original text values for each placeholder
            3. Generate consolidated key from concatenated values
            4. Replace fragment sequence with single placeholder
            """
            import re
            
            # Pattern: 2 or more placeholders separated by whitespace
            pattern = re.compile(
                r'(\{' + re.escape(self.root) + r'\.[A-Za-z0-9_.]+\})'  # first placeholder
                r'(\s+\{' + re.escape(self.root) + r'\.[A-Za-z0-9_.]+\})+'  # 1+ more placeholders
            )
            
            def consolidate_match(m: re.Match) -> str:
                full_match = m.group(0)
                
                # Extract all placeholder keys
                placeholder_pattern = re.compile(r'\{' + re.escape(self.root) + r'\.([A-Za-z0-9_.]+)\}')
                keys = placeholder_pattern.findall(full_match)
                
                if len(keys) < 2:
                    return full_match  # Not fragmented, keep as-is
                
                # Get original text values
                values = []
                for key in keys:
                    val = self.flat.get(key)
                    if val and isinstance(val, str):
                        values.append(val)
                    else:
                        # Can't consolidate if any key is missing/invalid
                        return full_match
                
                # Generate consolidated key from concatenated text
                # Example: ["Our", "products"] → "ourProducts" (camelCase)
                consolidated_text = ' '.join(values)
                consolidated_key = self._generate_consolidated_key(keys, consolidated_text)
                
                # Return single placeholder
                return '{' + self.root + '.' + consolidated_key + '}'
            
            return pattern.sub(consolidate_match, s)
        
        def _generate_consolidated_key(self, fragment_keys: list[str], consolidated_text: str) -> str:
            """
            Generate a consolidated key name from fragment keys and their combined text.
            
            Strategy:
            1. Use first fragment's path prefix (e.g., "pages.home" from "pages.home.title")
            2. Generate suffix from consolidated text (camelCase)
            3. If result already exists in dict, use it; otherwise create new synthetic key
            """
            # Try to extract common prefix from fragment keys
            if not fragment_keys:
                return "consolidated"
            
            # Split first key by dots to get path components
            parts = fragment_keys[0].split('.')
            
            if len(parts) > 1:
                # Use parent path: "pages.home.title" → prefix "pages.home"
                prefix = '.'.join(parts[:-1])
            else:
                # No parent, use root-level
                prefix = ""
            
            # Generate camelCase suffix from consolidated text
            # Example: "Our products is what you need" → "ourProductsIsWhatYouNeed"
            words = consolidated_text.split()
            if not words:
                suffix = "merged"
            else:
                suffix = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
            
            # Build final key
            if prefix:
                candidate = f"{prefix}.{suffix}"
            else:
                candidate = suffix
            
            # Check if this key already exists in dictionary
            # If yes, use it (perfect match!); if no, use synthetic key
            if candidate in self.flat:
                return candidate
            
            # Synthetic key (mark as auto-generated)
            return f"{prefix}.autoMerged_{suffix}" if prefix else f"autoMerged_{suffix}"

        # ---------- masking helpers ----------

        def _mask_existing_placeholders(self, s: str) -> tuple[str, List[str]]:
            guards: List[str] = []
            def _mask(m: re.Match) -> str:
                idx = len(guards)
                guards.append(m.group(0))
                return f"@@TREF{idx}@@"
            return self._re_placeholder.sub(_mask, s), guards

        def _unmask_placeholders(self, s: str, guards: List[str]) -> str:
            for i, tok in enumerate(guards):
                s = s.replace(f"@@TREF{i}@@", tok)
            return s

        # ---------- dictionary flatten ----------

        def _flatten(self, d: dict, prefix: str = "") -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            for k, v in (d or {}).items():
                kk = f"{prefix}.{k}" if prefix else str(k)
                if isinstance(v, dict):
                    out.update(self._flatten(v, kk))
                else:
                    out[kk] = v
            return out
    
    # Note: JsonTranslateDock now imported from src.gui.json_translate_dock
    # Note: AIProcessorDock now imported from src.gui.ai_processor_dock
    # Note: AIProcessorWorker now imported from src.gui.ai_processor_dock
    # Note: PlaceholderReplacerDock now imported from src.gui.placeholder_replacer_dock
    # Note: TextExtractorDock now imported from src.gui.text_extractor_dock
    # Note: JsonSearchDock now imported from src.gui.json_search_dock
    # Note: JsonCaseConverterDock now imported from src.gui.case_converter_dock

    # Note: JsonRewriterDock now imported from src.gui.json_rewriter_dock

    
        
    class MainWindow(QMainWindow):
        def __init__(self, app: QApplication):
            super().__init__()
            self.app = app
            
            # Initialize logging system (v2.9.58)
            self.logger = get_logger("clarify.app.MainWindow")
            self.logger.info("Initializing Clarify application")
            
            # Initialize error reporter (v2.9.89)
            from .utils.error_reporter import install_error_reporter
            from .gui.error_report_dialog import ErrorReportDialog
            self.error_reporter = install_error_reporter(app_version="2.9.89")
            self.error_dialog = ErrorReportDialog(self)
            self.error_reporter.dialog = self.error_dialog
            self.logger.info("Error reporter installed")
            
            # Initialize crash handler (v2.9.61)
            # Install global exception handler with dialog
            self.crash_handler = install_crash_handler(
                show_dialog=True,
                report_crashes=False  # Opt-in only
            )
            self.logger.info("Crash handler installed")
            
            # Run database migrations BEFORE loading config/settings (v2.9.91)
            from .migration_manager import run_migrations
            migrations_ok = run_migrations()
            if not migrations_ok:
                self.logger.warning("Migrations failed, continuing with current version")
            
            # Initialize translator (Task #24 - v2.9.10)
            self.translator = get_translator()
            self.translator.languageChanged.connect(self._on_language_changed)
            
            self.setWindowTitle(tr("app.title"))
            #self.resize(1080, 720)

            # Initialize settings manager
            from .settings_manager import get_settings
            self.settings = get_settings()
            
            # Initialize QSettings for accessibility (v2.9.40 - compatibility fix)
            from PySide6.QtCore import QSettings
            self.settings.qsettings = QSettings("Clarify", "ClarifyApp")
            
            # Load custom shortcuts (v2.9.33)
            from .shortcut_manager import ShortcutManager
            custom_shortcuts = self.settings.get_custom_shortcuts()
            ShortcutManager.load_custom_shortcuts(custom_shortcuts)
            
            # Initialize Command Manager for Undo/Redo (Task #12 - v2.9.8)
            from .core.command_manager import CommandManager
            self.command_manager = CommandManager(max_history=10)

            # Plugin System (v2.9.109 - Enhanced with metadata and events)
            from .plugin_loader import PluginLoader
            self.plugin_loader = PluginLoader(self)
            discovered = self.plugin_loader.discover_plugins()
            print(f"[PluginSystem] Discovered {len(discovered)} plugin(s)")
            
            # Auto-activate enabled plugins
            activated = self.plugin_loader.activate_all_plugins()
            print(f"[PluginSystem] Activated {activated} plugin(s)")
            
            # Track tool tabs (v2.9.40 - Task: Tools as tabs)
            self.tool_tabs = {}  # Maps tool_name -> (widget, tab_index)

            # REST API (optional - disabled by default, requires fastapi)
            # Uncomment to enable REST API server
            # try:
            #     from .rest_api import ClarifyAPI
            #     self.rest_api = ClarifyAPI(self)
            #     self.rest_api.start()
            # except Exception as e:
            #     print(f"[REST API] Not initialized: {e}")

            # Cloud sync (optional - disabled by default, dummy implementation)
            # Uncomment to enable cloud sync
            # try:
            #     from .cloud_sync import DummyProvider
            #     self.cloud_sync = DummyProvider()
            #     self.cloud_sync.login()
            # except Exception as e:
            #     print(f"[Cloud Sync] Not initialized: {e}")
            
            # Initialize Layout Manager (v2.9.84)
            from .layout_manager import LayoutManager
            self.layout_manager = LayoutManager(self)
            self.logger.info("LayoutManager initialized")

            self._build_icon()
            self._build_ui()
            self._build_menu()
            self._restore_prefs()
            self._apply_saved_settings()
            
            # Register docks with LayoutManager (v2.9.84)
            self._register_docks_with_layout_manager()
            
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
                self.search_panel.ed_repl.setFont(f)
                self.search_panel.ed_query.setFont(f)
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
        
        def _open_file_list(self):
            """Open File List dock (Task #33 - v2.9.11)."""
            DockFactory.create_file_list_dock(self)

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
                self.tab_search = SearchReplacePanel(progress_manager=self.progress_manager)
                
                # Force immediate visibility before inserting
                self.tab_search.setVisible(True)
                self.tab_search.show()
                
                self.tabs.insertTab(0, self.tab_search, "Search / Replace")
                self.tabs.setCurrentIndex(0)
                
                # Force widget rendering (fix invisible widgets bug)
                QApplication.processEvents()
                self.tab_search.updateGeometry()
                self.tab_search.update()
                self.tab_search.repaint()
                
                # Force update of all child widgets
                for child in self.tab_search.findChildren(QWidget):
                    child.setVisible(True)
                    child.updateGeometry()
                    child.update()
        
        def _show_insert(self):
            """Show Insert tab (v2.9.40.2 - reopen if closed)."""
            # Check if tab exists at index 1
            expected_index = 1
            if self.tabs.count() > expected_index and self.tabs.tabText(expected_index) == "Insert":
                self.tabs.setCurrentIndex(expected_index)
            else:
                # Tab was closed, recreate at index 1
                # InsertPanel is an internal class defined in this file, no import needed
                self.tab_insert = InsertPanel(progress_manager=self.progress_manager)
                
                # Force immediate visibility before inserting
                self.tab_insert.setVisible(True)
                self.tab_insert.show()
                
                self.tabs.insertTab(expected_index, self.tab_insert, "Insert")
                self.tabs.setCurrentIndex(expected_index)
                
                # Force widget rendering (fix invisible widgets bug)
                QApplication.processEvents()
                self.tab_insert.updateGeometry()
                self.tab_insert.update()
                self.tab_insert.repaint()
                
                # Force update of all child widgets
                for child in self.tab_insert.findChildren(QWidget):
                    child.setVisible(True)
                    child.updateGeometry()
                    child.update()
        
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
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QRadioButton
            
            # Create selection dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Converter Type")
            dialog.setModal(True)
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title_label = QLabel("<b>Choose the type of converter:</b>")
            layout.addWidget(title_label)
            
            # Radio buttons
            btn_group = QButtonGroup(dialog)
            
            radio_jsx = QRadioButton("JSX Parameter Extractor")
            radio_jsx.setToolTip(
                "Extract parameters and attributes from JSX/TSX files.\n"
                "Scans React component files and generates hierarchical JSON."
            )
            radio_jsx.setChecked(True)  # Default
            btn_group.addButton(radio_jsx)
            layout.addWidget(radio_jsx)
            
            radio_text = QRadioButton("Text Format Converter")
            radio_text.setToolTip(
                "Convert text formats to JSON (CSV, YAML, INI, etc.).\n"
                "Paste text and convert to JSON structure."
            )
            btn_group.addButton(radio_text)
            layout.addWidget(radio_text)
            
            # Description labels
            layout.addSpacing(10)
            desc_jsx = QLabel(
                "• <b>JSX Parameter Extractor:</b> For React/JSX/TSX files<br>"
                "  Extract props, attributes, and tag content from components<br>"
                "  Requires file or directory path"
            )
            desc_jsx.setWordWrap(True)
            layout.addWidget(desc_jsx)
            
            layout.addSpacing(5)
            desc_text = QLabel(
                "• <b>Text Format Converter:</b> For text-based formats<br>"
                "  Convert CSV, YAML, INI, TOML, etc. to JSON<br>"
                "  Paste text directly into the converter"
            )
            desc_text.setWordWrap(True)
            layout.addWidget(desc_text)
            
            # Buttons
            layout.addSpacing(10)
            btn_ok = QPushButton("Open")
            btn_ok.setDefault(True)
            btn_ok.clicked.connect(dialog.accept)
            layout.addWidget(btn_ok)
            
            btn_cancel = QPushButton("Cancel")
            btn_cancel.clicked.connect(dialog.reject)
            layout.addWidget(btn_cancel)
            
            # Show dialog and handle result
            if dialog.exec() == QDialog.Accepted:
                if radio_jsx.isChecked():
                    self._show_jsx_extractor()
                else:
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
        
        def _show_file_list(self):
            """Show File List as tab (create on-demand)."""
            from .gui.tab_manager import TabManager
            TabManager.show_file_list(self)
        
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
            """
            Show plugin manager dialog (v2.9.109).
            
            Lists all discovered plugins with:
            - Name, version, author, description
            - Enable/disable toggle
            - Dependencies list
            """
            from PySide6.QtWidgets import (
                QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                QTableWidget, QTableWidgetItem, QPushButton,
                QHeaderView, QCheckBox, QMessageBox
            )
            from PySide6.QtCore import Qt
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Plugin Manager - Clarify")
            dialog.setMinimumSize(700, 400)
            
            layout = QVBoxLayout()
            
            # Header
            lbl_header = QLabel("Manage installed plugins")
            lbl_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
            layout.addWidget(lbl_header)
            
            # Plugin table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Enabled", "Name", "Version", "Author", "Description"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
            
            metadata_list = self.plugin_loader.get_all_metadata()
            table.setRowCount(len(metadata_list))
            
            for row, metadata in enumerate(metadata_list):
                # Checkbox for enabled/disabled
                chk = QCheckBox()
                chk.setChecked(metadata.enabled)
                chk.stateChanged.connect(
                    lambda state, pid=metadata.id: self._toggle_plugin(pid, state == Qt.Checked)
                )
                table.setCellWidget(row, 0, chk)
                
                # Name
                table.setItem(row, 1, QTableWidgetItem(metadata.name))
                
                # Version
                table.setItem(row, 2, QTableWidgetItem(metadata.version))
                
                # Author
                table.setItem(row, 3, QTableWidgetItem(metadata.author))
                
                # Description
                table.setItem(row, 4, QTableWidgetItem(metadata.description))
            
            layout.addWidget(table)
            
            # Info label
            lbl_info = QLabel(
                f"📦 {len(metadata_list)} plugin(s) discovered | "
                f"{len([m for m in metadata_list if m.enabled])} enabled"
            )
            layout.addWidget(lbl_info)
            
            # Buttons
            btn_layout = QHBoxLayout()
            btn_refresh = QPushButton("🔄 Refresh")
            btn_refresh.clicked.connect(lambda: self._refresh_plugins(dialog))
            btn_close = QPushButton("✅ Close")
            btn_close.clicked.connect(dialog.accept)
            
            btn_layout.addWidget(btn_refresh)
            btn_layout.addStretch()
            btn_layout.addWidget(btn_close)
            
            layout.addLayout(btn_layout)
            dialog.setLayout(layout)
            dialog.exec()
        
        def _toggle_plugin(self, plugin_id: str, enabled: bool):
            """
            Toggle plugin enabled state (v2.9.109).
            
            Args:
                plugin_id: Plugin identifier
                enabled: Enable (True) or disable (False)
            """
            self.plugin_loader.enable_plugin(plugin_id, enabled)
            
            if enabled:
                # Activate plugin
                success = self.plugin_loader.activate_plugin(plugin_id)
                if success:
                    self.statusBar().showMessage(f"Plugin '{plugin_id}' activated", 3000)
                else:
                    self.statusBar().showMessage(f"Failed to activate plugin '{plugin_id}'", 5000)
            else:
                # Deactivate plugin
                self.plugin_loader.deactivate_plugin(plugin_id)
                self.statusBar().showMessage(f"Plugin '{plugin_id}' disabled", 3000)
        
        def _refresh_plugins(self, dialog):
            """
            Refresh plugins list (v2.9.109).
            
            Args:
                dialog: Plugin manager dialog to close and reopen
            """
            dialog.close()
            self.plugin_loader.discover_plugins()
            activated = self.plugin_loader.activate_all_plugins()
            self.statusBar().showMessage(f"Refreshed plugins: {activated} activated", 3000)
            self._show_plugin_manager()
        
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
            
            Forces fresh check (bypasses cache) and shows result message.
            """
            from .update_checker import check_for_updates
            from . import __version__
            
            # Show progress message
            self.statusBar().showMessage("Verificando atualizações...", 0)
            
            # Force fresh check
            has_update, release_info = check_for_updates(__version__, force=True)
            
            if has_update and release_info:
                # Check if user opted to skip this version
                from .gui.update_notification import UpdateNotificationDialog
                
                if UpdateNotificationDialog.should_show_for_version(release_info['version']):
                    self._show_update_dialog(release_info)
                else:
                    # User previously skipped this version
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "Atualização Disponível",
                        f"Nova versão {release_info['version']} disponível, mas você optou por pular esta versão.\n\n"
                        "Para ver novamente, limpe as preferências de atualização."
                    )
            else:
                # No update or error
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Sem Atualizações",
                    f"Você está usando a versão mais recente do Clarify ({__version__})."
                )
            
            self.statusBar().showMessage("Verificação de atualização concluída", 3000)
        
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
        
        def _show_advanced_file_search(self):
            """Show advanced file search dialog (Task #36 - v2.9.11)."""
            from .utils.file_finder import show_advanced_file_search
            
            # Get initial directory (current working directory or last used)
            initial_dir = os.getcwd()
            
            # Show dialog
            results = show_advanced_file_search(self, initial_dir)
            
            if results:
                # User selected files - could integrate with other tools here
                # For now, just show info message
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Search Complete",
                    f"Found and selected {len(results)} items.\n\n"
                    f"First item: {results[0] if results else 'None'}"
                )
        
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
            
            # Check if it's a fixed tab (Search/Replace or Insert)
            if index < 2:  # First two tabs are fixed
                # Allow closing but ask for confirmation
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Close Tab",
                    f"Do you want to close '{tab_title}'?\n\n"
                    f"You can reopen it from the Tools menu.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # Check for unsaved changes (only for Editor)
            if hasattr(widget, 'has_unsaved_changes') and callable(widget.has_unsaved_changes):
                if widget.has_unsaved_changes():
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self,
                        "Unsaved Changes",
                        f"'{tab_title}' has unsaved changes.\n\n"
                        f"Do you want to save before closing?",
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
            
            logger.info(f"Initializing all tabs - Count: {tab_count}, Current: {original_index}")
            
            # Activate each tab briefly to force widget rendering
            for i in range(tab_count):
                tab_name = self.tabs.tabText(i)
                logger.info(f"  Activating tab {i}: '{tab_name}'")
                self.tabs.setCurrentIndex(i)
                # Force immediate processing of events to ensure rendering
                QApplication.processEvents()
                
                # Also force geometry update on the widget
                widget = self.tabs.widget(i)
                if widget:
                    widget.updateGeometry()
                    widget.update()
                    logger.info(f"    Widget updated: {widget.__class__.__name__}")
            
            # Restore original tab
            logger.info(f"Restoring original tab: {original_index}")
            self.tabs.setCurrentIndex(original_index)
            QApplication.processEvents()
            logger.info("Tab initialization complete")
        
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
            
            logger.info(f"Restoring tab state - Saved index: {saved_index}, Tab count: {current_count}")
            
            # Validate saved index - if tab was closed, default to first available tab
            if isinstance(saved_index, int) and 0 <= saved_index < current_count:
                logger.info(f"  Setting tab to saved index: {saved_index}")
                self.tabs.setCurrentIndex(saved_index)
            else:
                # Saved tab no longer exists, activate first tab if any
                if current_count > 0:
                    logger.warning(f"  Saved index {saved_index} invalid! Defaulting to tab 0")
                    self.tabs.setCurrentIndex(0)
                else:
                    logger.warning(f"  No tabs available to activate")

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
            """Show preferences dialog."""
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel, QGroupBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Preferences")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout()
            
            # General settings group
            general_group = QGroupBox("General")
            general_layout = QVBoxLayout()
            
            chk_tooltips = QCheckBox("Show tooltips")
            chk_tooltips.setChecked(self.settings.get("show_tooltips", True))
            
            chk_confirm_exit = QCheckBox("Confirm before exit")
            chk_confirm_exit.setChecked(self.settings.get("confirm_on_exit", True))
            
            chk_auto_save = QCheckBox("Auto-save settings")
            chk_auto_save.setChecked(self.settings.get("auto_save", True))
            
            # Update checker preference (v2.9.45)
            chk_check_updates = QCheckBox("Check for updates on startup")
            chk_check_updates.setChecked(self.settings.qsettings.value("update_checker/enabled", True, type=bool))
            chk_check_updates.setToolTip("Automatically check for new Clarify versions when app starts (checks at most once per 24 hours)")
            
            general_layout.addWidget(chk_tooltips)
            general_layout.addWidget(chk_confirm_exit)
            general_layout.addWidget(chk_auto_save)
            general_layout.addWidget(chk_check_updates)
            general_group.setLayout(general_layout)
            
            layout.addWidget(general_group)
            
            # Buttons
            from PySide6.QtWidgets import QDialogButtonBox
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(lambda: self._save_preferences(
                chk_tooltips.isChecked(),
                chk_confirm_exit.isChecked(),
                chk_auto_save.isChecked(),
                chk_check_updates.isChecked(),
                dialog
            ))
            buttons.rejected.connect(dialog.reject)
            
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            dialog.exec()
        
        def _save_preferences(self, tooltips, confirm_exit, auto_save, check_updates, dialog):
            """Save preferences and close dialog (v2.9.45: added check_updates)."""
            self.settings.update_multiple({
                "show_tooltips": tooltips,
                "confirm_on_exit": confirm_exit,
                "auto_save": auto_save
            })
            
            # Save update checker preference to QSettings (v2.9.45)
            self.settings.qsettings.setValue("update_checker/enabled", check_updates)
            
            dialog.accept()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "Preferences saved successfully!")
        
        def _show_transparency_dialog(self):
            """Show window transparency configuration dialog with live preview."""
            from PySide6.QtWidgets import (
                QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                QPushButton, QSlider, QGroupBox
            )
            from PySide6.QtCore import Qt
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Window Transparency")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout()
            
            # Info label
            info_label = QLabel("Adjust the transparency level for all windows and docks.\n"
                              "0% = Fully transparent, 100% = Fully opaque")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
            
            # Transparency group
            trans_group = QGroupBox("Transparency Level")
            trans_layout = QVBoxLayout()
            
            # Slider
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel("0%"))
            
            self.opacity_slider = QSlider(Qt.Horizontal)
            self.opacity_slider.setRange(0, 100)
            self.opacity_slider.setValue(self._get_saved_opacity())
            self.opacity_slider.setTickPosition(QSlider.TicksBelow)
            self.opacity_slider.setTickInterval(10)
            self.opacity_slider.valueChanged.connect(self._update_transparency_preview)
            slider_layout.addWidget(self.opacity_slider)
            
            slider_layout.addWidget(QLabel("100%"))
            trans_layout.addLayout(slider_layout)
            
            # Value display
            self.opacity_label = QLabel(f"Current: {self.opacity_slider.value()}%")
            self.opacity_label.setAlignment(Qt.AlignCenter)
            self.opacity_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
            trans_layout.addWidget(self.opacity_label)
            
            trans_group.setLayout(trans_layout)
            layout.addWidget(trans_group)
            
            # Buttons
            from PySide6.QtWidgets import QDialogButtonBox
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(lambda: self._save_transparency(dialog))
            buttons.rejected.connect(lambda: self._cancel_transparency(dialog))
            
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            dialog.exec()
        
        def _get_saved_opacity(self):
            """Get saved opacity value from settings (default 100%)."""
            return int(self.settings.get("window_opacity", 100))
        
        def _update_transparency_preview(self, value):
            """Update transparency in real-time for preview."""
            opacity = value / 100.0
            self.setWindowOpacity(opacity)
            self.opacity_label.setText(f"Current: {value}%")
            
            # Apply to all existing docks
            dock_names = ['dock_translate', 'dock_rewriter', 'dock_text_extractor',
                         'dock_placeholder_replacer', 'dock_ai_processor',
                         'dock_json_search', 'dock_case_converter', 'dock_history']
            for dock_name in dock_names:
                if hasattr(self, dock_name):
                    getattr(self, dock_name).setWindowOpacity(opacity)
        
        def _save_transparency(self, dialog):
            """Save transparency setting and close dialog."""
            value = self.opacity_slider.value()
            self.settings.update("window_opacity", value)
            dialog.accept()
        
        def _cancel_transparency(self, dialog):
            """Restore previous transparency and close dialog."""
            saved_opacity = self._get_saved_opacity()
            self._update_transparency_preview(saved_opacity)
            dialog.reject()
        
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
            self.settings.update("language", lang)
        
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
                "search": getattr(self, "search_panel", None),
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
            """Show layout management dialog (v2.9.84)."""
            from PySide6.QtWidgets import (
                QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                QPushButton, QMessageBox, QLabel
            )
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Manage Layouts")
            dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout()
            
            # Label
            label = QLabel("Saved layouts (custom layouts only):")
            layout.addWidget(label)
            
            # List widget
            list_widget = QListWidget()
            custom_layouts = self.layout_manager.get_saved_layouts()
            list_widget.addItems(custom_layouts)
            layout.addWidget(list_widget)
            
            # Buttons
            btn_layout = QHBoxLayout()
            btn_load = QPushButton("Load")
            btn_delete = QPushButton("Delete")
            btn_reset = QPushButton("Reset to Defaults")
            btn_close = QPushButton("Close")
            
            btn_layout.addWidget(btn_load)
            btn_layout.addWidget(btn_delete)
            btn_layout.addWidget(btn_reset)
            btn_layout.addStretch()
            btn_layout.addWidget(btn_close)
            
            layout.addLayout(btn_layout)
            dialog.setLayout(layout)
            
            # Connect buttons
            def load_selected():
                current_item = list_widget.currentItem()
                if current_item:
                    layout_name = current_item.text()
                    if self.layout_manager.load_layout(layout_name):
                        QMessageBox.information(dialog, "Success", f"Layout '{layout_name}' loaded.")
                        dialog.accept()
            
            def delete_selected():
                current_item = list_widget.currentItem()
                if current_item:
                    layout_name = current_item.text()
                    reply = QMessageBox.question(
                        dialog,
                        "Confirm Delete",
                        f"Are you sure you want to delete layout '{layout_name}'?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.layout_manager.delete_layout(layout_name)
                        list_widget.takeItem(list_widget.row(current_item))
            
            def reset_all():
                reply = QMessageBox.question(
                    dialog,
                    "Confirm Reset",
                    "This will delete all custom layouts and restore Standard preset. Continue?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.layout_manager.reset_to_defaults()
                    list_widget.clear()
                    QMessageBox.information(dialog, "Reset Complete", "Layouts reset to defaults.")
                    dialog.accept()
            
            btn_load.clicked.connect(load_selected)
            btn_delete.clicked.connect(delete_selected)
            btn_reset.clicked.connect(reset_all)
            btn_close.clicked.connect(dialog.accept)
            
            dialog.exec()
        
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
            search_label = QLabel("Search:")
            search_box = QLineEdit()
            search_box.setPlaceholderText("Type to filter shortcuts...")
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
            
            customize_btn = QPushButton("Customize...")
            customize_btn.setToolTip("Open shortcuts customization dialog")
            customize_btn.clicked.connect(lambda: (dialog.close(), self._show_shortcuts()))
            
            close_btn = QPushButton("Close")
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
                (self.act_open_file_list, "open_file_list", "Manage file lists"),
                (self.act_advanced_file_search, "advanced_file_search", "Advanced file search"),
                
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
                    "Undo",
                    f"Undone: {self.command_manager.get_redo_description() or 'Last operation'}"
                )
            else:
                QMessageBox.warning(self, "Undo", "Nothing to undo.")
        
        def _redo(self):
            """Redo the last undone command."""
            if self.command_manager.redo():
                self._update_undo_redo_state()
                QMessageBox.information(
                    self,
                    "Redo",
                    f"Redone: {self.command_manager.get_undo_description() or 'Last operation'}"
                )
            else:
                QMessageBox.warning(self, "Redo", "Nothing to redo.")
        
        def _clear_undo_history(self):
            """Clear all undo/redo history."""
            reply = QMessageBox.question(
                self,
                "Clear History",
                "Are you sure you want to clear all undo/redo history?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.command_manager.clear_history()
                self._update_undo_redo_state()
                QMessageBox.information(self, "Success", "Undo/redo history cleared!")
        
        def _update_undo_redo_state(self):
            """Update the enabled state of undo/redo buttons based on history."""
            self.act_undo.setEnabled(self.command_manager.can_undo())
            self.act_redo.setEnabled(self.command_manager.can_redo())
            
            # Update button tooltips with descriptions
            if self.command_manager.can_undo():
                self.act_undo.setToolTip(f"Undo: {self.command_manager.get_undo_description()}")
            else:
                self.act_undo.setToolTip("Nothing to undo")
            
            if self.command_manager.can_redo():
                self.act_redo.setToolTip(f"Redo: {self.command_manager.get_redo_description()}")
            else:
                self.act_redo.setToolTip("Nothing to redo")
        
        def _clear_recent_files(self):
            """Clear recent files list."""
            reply = QMessageBox.question(
                self,
                "Clear Recent Files",
                "Are you sure you want to clear the recent files list?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.settings.clear_recent_files()
                QMessageBox.information(self, "Success", "Recent files cleared!")
        
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
            # Main container widget with vertical layout
            main_container = QWidget()
            main_layout = QVBoxLayout(main_container)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Tabs (top area)
            self.tabs = QTabWidget()
            
            # Enable close buttons on tabs (v2.9.40 - Task: Tools as tabs)
            self.tabs.setTabsClosable(True)
            self.tabs.tabCloseRequested.connect(self._close_tab)
            
            main_layout.addWidget(self.tabs)
            
            # Progress Manager (bottom area - v2.5.0)
            self.progress_manager = ProgressManager(self)
            main_layout.addWidget(self.progress_manager)
            
            # Set main container as central widget
            self.setCentralWidget(main_container)
            
            # Force central widget to be visible and updated
            main_container.setVisible(True)
            main_container.update()
            
            # Status bar (Sprint 8 - v1.1.0)
            self.statusbar = self.statusBar()
            self.statusbar.showMessage("Ready", 3000)

            # Create panels and pass progress_manager reference (using internal classes)
            self.tab_search = SearchReplacePanel(progress_manager=self.progress_manager)
            self.tab_insert = InsertPanel(progress_manager=self.progress_manager)
            
            # Aliases for backward compatibility
            self.search_panel = self.tab_search
            self.insert_panel = self.tab_insert

            self.tabs.addTab(self.tab_search, "Search / Replace")
            self.tabs.addTab(self.tab_insert, "Insert")
            
            # Mark Search/Replace and Insert as not closeable initially (fixed tabs)
            # They will be marked as closeable when saved to QSettings
            # (v2.9.40 - Task: Tools as tabs)

            # Apply tab close button styling based on theme
            self._apply_tab_close_button_style()

            # Docks are created on-demand when user opens them via Tools menu
            # No automatic opening to avoid cluttering the interface at startup
            # (v2.9.40 - Now they open as tabs instead of docks)
        
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
