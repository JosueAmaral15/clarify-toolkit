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
    dump_ts_node, dump_ts_obj, collapse_blank_lines
)

# Case Converter: camelCase/PascalCase/snake_case/kebab-case conversion
from .case_converter import JSObjectCaseConverter

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
    JsonRewriterDock
)

# ---------------------------------------------------------------------------
#  Optional import of PySide6 (the CLI subcommands work even if PySide6 is missing)
# ---------------------------------------------------------------------------

_PYSIDE = True

try:
    from PySide6.QtCore import (
        Qt, QAbstractTableModel, QModelIndex, QSize, QTimer, Signal, QByteArray, QAbstractListModel, QObject, QThread
        )
    from PySide6.QtGui import QAction, QFontDatabase, QPixmap, QIcon, QPalette, QColor
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

# ---------- Exclusion masking (skip-regex) ----------

# --- NEW: robust value → regex compiler for dictionary texts (handles quotes/apostrophes) ---

def _escape_variants_for_quotes(s: str) -> list[str]:
    """
    Return regex-safe variants of the same text so we can match values written with
    real quotes/apostrophes or with escaped forms (\" \').
    """
    # Base escaped
    base = re.escape(s)

    # If text contains double quotes, also allow escaped-double-quote variant
    variants = { base }
    if '"' in s:
        variants.add(re.escape(s.replace('"', '\\"')))
    if "'" in s:
        variants.add(re.escape(s.replace("'", "\\'")))

    # Also handle cases where the source file has “already-escaped” strings in TS/JS blocks
    # (e.g., We\\'re). We accept both one and two backslashes before quotes.
    if "\\\"" in s or "\\\'" in s:
        variants.add(re.escape(s.replace("\\\"", "\"").replace("\\\'", "'")))
    return list(variants)

def _compile_value_union_regex(value_to_key: dict[str, str]) -> re.Pattern:
    """
    Build a single alternation regex with named groups for each value.
    We sort by length (desc) to prefer the longest phrase first.
    """
    # Sort items by length of value, desc
    items = sorted(value_to_key.items(), key=lambda kv: len(kv[0]), reverse=True)

    parts = []
    group_names = []  # keep for debug if needed
    idx = 0
    for val, _key in items:
        if not val:
            continue
        # produce variants for quotes/apostrophes
        variants = _escape_variants_for_quotes(val)
        # fold multiple variants into a small alternation
        if len(variants) == 1:
            body = variants[0]
        else:
            body = "(?:" + "|".join(variants) + ")"
        gname = f"V{idx}"
        parts.append(f"(?P<{gname}>{body})")
        group_names.append(gname)
        idx += 1

    if not parts:
        # something degenerate but keep a harmless regex
        return re.compile(r"(?!x)x")

    # We’re replacing *visible text* in scoped chunks, so we don’t anchor with word boundaries.
    # The masking of {t.…} ensures we won’t replace inside placeholders.
    big = "|".join(parts)
    return re.compile(big)


# ---------- JSON Translate — GUI helpers (scope, masking, backup) ----------

RE_PLACEHOLDER = re.compile(r"\{([A-Za-z_]\w*)(?:\.[A-Za-z0-9_]+)+\}")
_TAG_OPEN_RE  = re.compile(r"<\s*([A-Za-z][\w:-]*)[^>]*?>", re.DOTALL)
_TAG_CLOSE_RE = re.compile(r"</\s*([A-Za-z][\w:-]*)\s*>", re.DOTALL)

def _apply_scoped_translation_tag_balanced(content: str, fn_transform) -> str:
    """
    Tag-balanced scope:
      - Scan for tags <name ...> and </name>
      - When an opening tag is found, find its *matching* closing tag of the same name,
        counting nested occurrences of the same tag.
      - Apply fn_transform to the *inner* content (after open tag, before close tag).
      - Leave tags themselves untouched.
    We process outermost-to-innermost to ensure all text within elements is covered.
    """
    out = []
    i = 0
    n = len(content)

    while i < n:
        m_open = _TAG_OPEN_RE.search(content, i)
        if not m_open:
            out.append(content[i:])
            break

        # Write everything before the opening tag
        out.append(content[i:m_open.start()])

        tag_name = m_open.group(1)
        tag_open_end = m_open.end()

        # Find matching closing tag for tag_name (with nesting of the *same* tag)
        depth = 1
        j = tag_open_end
        while j < n and depth > 0:
            m_next_open  = _TAG_OPEN_RE.search(content, j)
            m_next_close = _TAG_CLOSE_RE.search(content, j)

            if not m_next_close and not m_next_open:
                # unmatched => give up and dump the rest
                out.append(content[m_open.start():])
                return "".join(out)

            # choose the nearest next tag of any kind
            candidates = [m for m in (m_next_open, m_next_close) if m]
            m_next = min(candidates, key=lambda m: m.start())

            if m_next.re is _TAG_OPEN_RE and m_next.group(1) == tag_name:
                depth += 1
                j = m_next.end()
                continue

            if m_next.re is _TAG_CLOSE_RE and m_next.group(1) == tag_name:
                depth -= 1
                j = m_next.end()
                if depth == 0:
                    # We have a full <tag> ... </tag> region
                    open_tag  = content[m_open.start():tag_open_end]
                    inner     = content[tag_open_end:m_next.start()]
                    close_tag = content[m_next.start():j]

                    out.append(open_tag)
                    out.append(fn_transform(inner))
                    out.append(close_tag)

                    i = j
                    break

                continue

            # A different tag; skip past it and continue searching
            j = m_next.end()

        # If loop exited without finding matching close (depth > 0), append rest and break
        if depth > 0:
            out.append(content[m_open.start():])
            break

    return "".join(out)

def mask_existing_placeholders(text: str) -> tuple[str, list[str]]:
    """Protect existing {root.path} so we don't touch/duplicate them."""
    guards: list[str] = []
    def _mask(m: re.Match) -> str:
        idx = len(guards); guards.append(m.group(0))
        return f"@@TREF{idx}@@"
    return RE_PLACEHOLDER.sub(_mask, text), guards

def unmask_existing_placeholders(text: str, guards: list[str]) -> str:
    for i, tok in enumerate(guards):
        text = text.replace(f"@@TREF{i}@@", tok)
    return text

def apply_scoped_translation(content: str,
                             start_rx: str,
                             end_rx: str,
                             fn_transform) -> str:
    """
    Apply 'fn_transform' ONLY to chunks between start/end delimiters.

    If delimiters look like generic HTML/JSX tags (start '<...>' / end '</...>'),
    we switch to a tag-balanced mode: pair opening tag <name ...> with </name>, honoring nesting
    of the *same* tag, and transform the entire element's *inner* content.

    Otherwise we fall back to simple flat pairing using the provided regexes.
    """
    start_rx = (start_rx or "").strip()
    end_rx = (end_rx or "").strip()

    if not start_rx or not end_rx:
        # no scope => transform whole file
        return fn_transform(content)

    # Detect "generic tag" mode
    generic_tag_mode = (
        start_rx == "<[^>]*?>" and end_rx == "</[^>]*?>"
    ) or (
        start_rx.startswith("<") and end_rx.startswith("</")
    )

    if generic_tag_mode:
        return _apply_scoped_translation_tag_balanced(content, fn_transform)

    # Fallback: flat regex pairing (previous behavior)
    start = re.compile(start_rx, re.DOTALL)
    end = re.compile(end_rx, re.DOTALL)

    out = []
    i = 0
    n = len(content)

    while i < n:
        mstart = start.search(content, i)
        if not mstart:
            out.append(content[i:])
            break
        out.append(content[i:mstart.start()])
        mend = end.search(content, mstart.end())
        if not mend:
            out.append(content[mstart.start():])
            break

        before = content[mstart.start():mstart.end()]
        inner  = content[mstart.end():mend.start()]
        after  = content[mend.start():mend.end()]

        out.append(before)
        out.append(fn_transform(inner))
        out.append(after)

        i = mend.end()

    return "".join(out)

def process_translate_file(path: str,
                           dictionary: dict,
                           root_alias: str,
                           start_rx: str,
                           end_rx: str,
                           make_backup: bool,
                           dont_override: bool,
                           inverse: bool,
                           exclude_patterns: list[str]) -> tuple[bool, Optional[str]]:
    """
    Load file, translate (forward or inverse) honoring scope, options, and exclusions.
    Returns (changed, error_message).
    """
    try:
        original = read_text(path)
        content = original

        def _one_chunk(chunk: str) -> str:
            # 1) Mask exclusions so they are never touched
            chunk, excl_guards = mask_exclusions(chunk, exclude_patterns)

            # 2) Optionally protect existing {root.*} placeholders
            if dont_override and not inverse:
                chunk, tref_guards = mask_existing_placeholders(chunk)
            else:
                tref_guards = []

            # 3) Run translation (forward or inverse)
            if inverse:
                changed = translate_replace_texts(chunk, dictionary, root_name=root_alias, inverse=True)
            else:
                changed = translate_replace_texts(chunk, dictionary, root_name=root_alias, inverse=False)

            # 4) Unmask in reverse order (placeholders first, then exclusions)
            if tref_guards:
                changed = unmask_existing_placeholders(changed, tref_guards)
            changed = unmask_exclusions(changed, excl_guards)

            return changed

        new_content = apply_scoped_translation(content, start_rx, end_rx, _one_chunk)

        if new_content != original:
            if make_backup:
                safe_backup_file(path)
            write_text(path, new_content)
            return True, None
        return False, None
    except Exception as e:
        return False, str(e)

# def process_translate_file(path: str,
#                            dictionary: dict,
#                            root_alias: str,
#                            start_rx: str,
#                            end_rx: str,
#                            make_backup: bool,
#                            dont_override: bool,
#                            inverse: bool,
#                            exclude_patterns: list[str]) -> tuple[bool, Optional[str]]:

#     try:
#         original = read_text(path)

#         def _one_chunk(chunk: str) -> str:
#             # 1) never touch user-excluded regions
#             chunk, excl_guards = mask_exclusions(chunk, exclude_patterns)

#             # 2) protect existing {t.*} **only on forward**
#             tref_guards = []
#             if dont_override and not inverse:                    # ← changed line
#                 chunk, tref_guards = mask_existing_placeholders(chunk)

#             # 3) translate
#             changed = translate_replace_texts(
#                 chunk, dictionary, root_name=root_alias, inverse=inverse
#             )

#             # 4) unmask
#             if tref_guards:
#                 changed = unmask_existing_placeholders(changed, tref_guards)
#             changed = unmask_exclusions(changed, excl_guards)
#             return changed

#         new_content = apply_scoped_translation(original, start_rx, end_rx, _one_chunk)
#         if new_content != original:
#             if make_backup:
#                 safe_backup_file(path)
#             write_text(path, new_content)
#             return True, None
#         return False, None
#     except Exception as e:
#         return False, str(e)


# =============================== Match Model/Panel ===============================
# Only define GUI classes if PySide6 is available
if _PYSIDE:
    class MatchListModel(QAbstractListModel):
        def __init__(self, items: List[str] = None):
            super().__init__()
            self.items = items or []

        def data(self, index: QModelIndex, role=Qt.DisplayRole):
            if role == Qt.DisplayRole:
                return self.items[index.row()]
            return None

        def rowCount(self, parent=QModelIndex()):
            return len(self.items)

        def set_items(self, items: List[str]):
            self.beginResetModel()
            self.items = list(items)
            self.endResetModel()

    class MatchPanel(QWidget):
        """
        Shared 'Match results' panel used by both Search/Replace and Insert tabs.
        """
        def __init__(self, parent=None):
            super().__init__(parent)
            v = QVBoxLayout(self)
            top = QHBoxLayout()
            self.lbl_count = QLabel("Matches: 0")
            self.btn_refresh = QPushButton("Refresh")
            self.btn_open_dir = QPushButton("Open Folder…")
            top.addWidget(self.lbl_count)
            top.addStretch(1)
            top.addWidget(self.btn_refresh)
            top.addWidget(self.btn_open_dir)
            v.addLayout(top)

            self.model = MatchListModel([])
            self.view = QListView()
            self.view.setModel(self.model)
            v.addWidget(self.view, 1)

            self.current_root: Optional[str] = None
            self.btn_open_dir.clicked.connect(self._open_dir_for_selected)

        def set_results(self, root: str, files: List[str]):
            self.current_root = root
            self.model.set_items(files)
            self.lbl_count.setText(f"Matches: {len(files)}")

        def selected_path(self) -> Optional[str]:
            idxs = self.view.selectedIndexes()
            if not idxs:
                return None
            return self.model.items[idxs[0].row()]

        def _open_dir_for_selected(self):
            path = self.selected_path()
            if not path:
                QMessageBox.information(self, "Open", "Select a file in the list.")
                return
            # Open in OS file manager
            if sys.platform.startswith("darwin"):
                os.system(f'open -R "{path}"')
            elif os.name == "nt":
                os.system(f'explorer /select,"{path}"')
            else:
                os.system(f'xdg-open "{os.path.dirname(path)}"')
            
# =============================================================================
#                        SEARCH / REPLACE CORE (CLI + GUI)
# =============================================================================

# =============================================================================
#                         ADVANCED FILTERS (CONDITIONALS)
# =============================================================================

OPS = {
    "contains": lambda a, b: b in a,
    "not contains": lambda a, b: b not in a,
    "equals": lambda a, b: a == b,
    "not equals": lambda a, b: a != b,
    "starts with": lambda a, b: a.startswith(b),
    "ends with": lambda a, b: a.endswith(b),
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}

# =============================================================================
#                              INSERT TEXT ENGINE
# =============================================================================

# =============================== Preferences ===============================
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

def apply_system_theme(app: QApplication):
    app.setStyle("Fusion")
    app.setPalette(app.style().standardPalette())

def apply_light_theme(app: QApplication):
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(255, 255, 255))
    pal.setColor(QPalette.WindowText, QColor(0, 0, 0))
    pal.setColor(QPalette.Base, QColor(245, 245, 245))
    pal.setColor(QPalette.AlternateBase, QColor(235, 235, 235))
    pal.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    pal.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    pal.setColor(QPalette.Text, QColor(0, 0, 0))
    pal.setColor(QPalette.Button, QColor(240, 240, 240))
    pal.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    pal.setColor(QPalette.Highlight, QColor(38, 79, 120))
    pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # app.setStyleSheet("""
    #         QGroupBox { border: 1px solid #d6d6dc; border-radius: 6px; margin-top: 8px; }
    #         QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #111; }
    #         QListView, QPlainTextEdit, QTextEdit, QLineEdit { border: 1px solid #d6d6dc; border-radius: 4px; }
    #     """)
    app.setPalette(pal)

def apply_dark_theme(app: QApplication):
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(45, 45, 45))
    pal.setColor(QPalette.WindowText, QColor(240, 240, 240))
    pal.setColor(QPalette.Base, QColor(35, 35, 35))
    pal.setColor(QPalette.AlternateBase, QColor(55, 55, 55))
    pal.setColor(QPalette.ToolTipBase, QColor(65, 65, 65))
    pal.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
    pal.setColor(QPalette.Text, QColor(240, 240, 240))
    pal.setColor(QPalette.Button, QColor(60, 60, 60))
    pal.setColor(QPalette.ButtonText, QColor(240, 240, 240))
    pal.setColor(QPalette.Highlight, QColor(90, 120, 190))
    pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    # app.setStyleSheet("""
    #     QGroupBox { border: 1px solid #3a3a40; border-radius: 6px; margin-top: 8px; }
    #     QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #d0d0d6; }
    #     QListView, QPlainTextEdit, QTextEdit, QLineEdit { border: 1px solid #3a3a40; border-radius: 4px; }
    # """)
    app.setPalette(pal)
        
def apply_theme(app: QApplication, mode: str):
    """
    mode: "system" | "light" | "dark"
    """
    if mode == "light":
        apply_light_theme(app)
    elif mode == "dark":
        apply_dark_theme(app)
    else: # system
        apply_system_theme(app)

# =============================================================================
#                 JSON TRANSLATE (dictionary-driven replacement)
# =============================================================================

def load_translation_dict(path: str) -> Dict[str, Any]:
    """
    Load a dictionary file (JSON / TS/JS object literal).
    If it's TS/JS, we try to find the main { ... } and parse it to JSON.
    """
    text = read_text(path)
    if path.lower().endswith((".json",)):
        return json.loads(text)

    # Fallback: naive TS/JS extraction (re-usable from dedupe machinery below)
    start, end, block = find_object_block(text)
    block_json = ts_block_to_json_text(block)
    return json.loads(block_json)


def flatten_dict_paths(d: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    """
    Flatten a nested dict into {"a.b.c": "value"} for leaf strings.
    """
    out: Dict[str, str] = {}
    for k, v in (d or {}).items():
        kk = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten_dict_paths(v, kk))
        else:
            out[kk] = v if v is not None else ""
    return out


# def translate_replace_texts(content: str,
#                             dictionary: Dict[str, Any],
#                             open_tag: str = "{",
#                             close_tag: str = "}") -> str:
#     """
#     Replace visible texts BETWEEN tags by dictionary keys, e.g.:
#       "<p>Submit</p>"  →  "<p>{t.common.buttons.submit}</p>"
#     Strategy:
#       - Build value→key map from the dictionary by flattening.
#       - For every value (longest first), replace occurrences that are not inside existing braces.
#     NOTE: This is a heuristic; for precise HTML/TSX you’d use a real parser. Good enough for batch refactors.
#     """
#     flat = flatten_dict_paths(dictionary)
#     val2key: Dict[str, str] = {}
#     for k, v in flat.items():
#         if isinstance(v, str) and v.strip():
#             val2key[v] = k

#     # Sort by descending length to prefer longer matches first.
#     items = sorted(val2key.items(), key=lambda kv: len(kv[0]), reverse=True)

#     def _outside_braces(text: str, pos: int, span: int) -> bool:
#         # crude: ensure no '{' or '}' inside the window; avoids replacing existing {t...}
#         window = text[max(0, pos-1):pos+span+1]
#         return ("{" not in window) and ("}" not in window)

#     s = content
#     for val, key in items:
#         if not val:
#             continue
#         pat = re.escape(val)
#         for m in list(re.finditer(pat, s)):
#             if _outside_braces(s, m.start(), len(val)):
#                 s = s[:m.start()] + f"{open_tag}t.{key}{close_tag}" + s[m.end():]
#     return s


def translate_replace_texts(content: str,
                            dictionary: Dict[str, Any],
                            root_name: str = "t",
                            inverse: bool = False) -> str:
    """
    Wrapper around CodeAwareJSONTranslator.
    - forward  (inverse=False): text → {root.path}
    - inverse  (inverse=True):  {root.path} → text
    """
    tr = CodeAwareJSONTranslator(dictionary, root_name=root_name)
    if inverse:
        return tr.translate_refs_to_text(content)
    return tr.translate_text_to_refs(content)

# def translate_replace_texts(content: str,
#                             dictionary: Dict[str, Any],
#                             root_name: str = "t",
#                             inverse: bool = False) -> str:
#     """
#     Forward:  text  → {root.path}
#     Inverse:  {root.path} → text

#     Improvements:
#       - matches dictionary values even when they use quotes/apostrophes or escaped quotes
#       - prefers longer matches first
#       - never touches already existing {root.*} placeholders (they are masked by caller)
#     """
#     flat = flatten_dict_paths(dictionary)

#     if inverse:
#         # {root.foo.bar} -> actual text
#         # Build regex for {root.something...}
#         ref_rx = re.compile(r"\{"+re.escape(root_name)+r"\.([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)\}")
#         def _repl_ref(m: re.Match) -> str:
#             path = m.group(1)
#             return flat.get(path, m.group(0))
#         return ref_rx.sub(_repl_ref, content)

#     # Forward direction: text -> {root.path}
#     # Build value→key map
#     val2key: Dict[str, str] = {}
#     for k, v in flat.items():
#         if isinstance(v, str) and v.strip():
#             val2key[v] = k

#     if not val2key:
#         return content

#     rx = _compile_value_union_regex(val2key)

#     def _replace(m: re.Match) -> str:
#         # Find which group hit and map back to original value->key
#         gdict = m.groupdict()
#         # Determine the *actual* matched surface text, then find the canonical key by
#         # looking up which source value(s) produced this group index. We built groups
#         # in the same order as items sorted by length; we can reconstruct by scanning.
#         # Simpler: use the matched text to look up the original value ignoring escaping.
#         matched = m.group(0)
#         # Normalize escape variants back to a canonical candidate set
#         # Try exact/escaped/unescaped matches against val2key keys
#         candidates = []
#         for val, key in val2key.items():
#             if matched == val \
#                or matched.replace('\\"', '"').replace("\\'", "'") == val \
#                or matched == val.replace('"', '\\"') \
#                or matched == val.replace("'", "\\'"):
#                 candidates.append((val, key))
#         # Prefer the longest val among candidates
#         if candidates:
#             key = max(candidates, key=lambda t: len(t[0]))[1]
#             return "{%s.%s}" % (root_name, key)
#         # Fallback: best-effort direct mapping by picking first named group that matched
#         for name, text in gdict.items():
#             if text is not None:
#                 # Find original value whose variants could produce this text
#                 for val, key in val2key.items():
#                     if text == val:
#                         return "{%s.%s}" % (root_name, key)
#                     if text.replace('\\"', '"').replace("\\'", "'") == val:
#                         return "{%s.%s}" % (root_name, key)
#         return matched  # no change

#     return rx.sub(_replace, content)



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


def cli_search(args: argparse.Namespace) -> int:
    patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    conds = parse_conditions(args.cond)
    files = filter_files_by_conditions(files, conds)
    total = 0
    for p in files:
        try:
            text = read_text(p)
            for m in patt.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                print(f"{p}:{line}:{col}")
                total += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\n{total} matches.")
    return 0

def cli_replace(args: argparse.Namespace) -> int:
    patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    conds = parse_conditions(args.cond)
    files = filter_files_by_conditions(files, conds)
    changed = 0
    for p in files:
        try:
            text = read_text(p)
            new, n = replace_in_text(text, patt, args.replacement, args.preserve_case, 0 if args.all else 1)
            if n > 0:
                if args.dry_run:
                    print(f"[DRY] {p}: would replace {n}")
                else:
                    write_text(p, new); changed += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0

def cli_insert(args: argparse.Namespace) -> int:
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    conds = parse_conditions(args.cond)
    files = filter_files_by_conditions(files, conds)
    changed = 0
    for p in files:
        try:
            old = read_text(p)
            new = insert_at_line(old, args.line, args.text, args.mode)
            if new != old:
                if args.dry_run:
                    print(f"[DRY] {p}: would modify")
                else:
                    write_text(p, new); changed += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0

# def cli_translate(args: argparse.Namespace) -> int:
#     files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
#     d = read_translation_dict(args.dictionary)
#     changed = 0
#     for p in files:
#         try:
#             old = read_text(p)
#             new = translate_replace_texts(old, d)
#             if new != old:
#                 if args.dry_run:
#                     print(f"[DRY] {p}: would translate")
#                 else:
#                     write_text(p, new); changed += 1
#         except Exception as e:
#             print(f"[WARN] {p}: {e}", file=sys.stderr)
#     print(f"\nChanged files: {changed}")
#     return 0

def cli_translate(args: argparse.Namespace) -> int:
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    d = read_translation_dict(args.dictionary)

    root_name = getattr(args, "root", "t")
    inverse = getattr(args, "inverse", False)

    changed = 0
    for p in files:
        try:
            old = read_text(p)
            new = translate_replace_texts(old, d, root_name=root_name, inverse=inverse)
            if new != old:
                if args.dry_run:
                    print(f"[DRY] {p}: would translate")
                else:
                    write_text(p, new); changed += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0

def cli_dedupe(args: argparse.Namespace) -> int:
    raw = read_text(args.input)
    indent = None if args.indent is not None and args.indent <= 0 else args.indent
    if args.from_ts or args.input.lower().endswith((".ts",".tsx",".js",".jsx")):
        if args.ts_out:
            start,end,block = find_object_block(raw)
            json_text = ts_block_to_json_text(block)
            data = parse_json_preserving_duplicates_text(json_text)
            result = join_keys(data) if args.join_keys else dedupe(data)
            if args.eliminate_duplicates:
                result = eliminate_duplicates(result)
            body = dump_ts_node(result, indent, 0)
            out = f"export default {body};\n"
        else:
            out = ts_process_full_preserving(raw, indent, args.join_keys, args.eliminate_duplicates)
    else:
        data = parse_json_preserving_duplicates_text(raw)
        result = join_keys(data) if args.join_keys else dedupe(data)
        if args.eliminate_duplicates:
            result = eliminate_duplicates(result)

        def dump_json(n: JSONNode, ind: Optional[int], lvl: int) -> str:
            if isinstance(n, Obj):
                if not n: return "{}"
                if ind is None or ind <= 0:
                    parts = ["{"] + [("," if i else "") + json.dumps(k, ensure_ascii=False) + ":" + dump_json(v, ind, lvl)
                                     for i,(k,v) in enumerate(n)] + ["}"]
                    return "".join(parts)
                sp = " " * ind
                parts = ["{\n"]
                for i,(k,v) in enumerate(n):
                    if i: parts.append(",\n")
                    parts.append(sp*(lvl+1) + json.dumps(k, ensure_ascii=False) + ": " + dump_json(v, ind, lvl+1))
                parts.append("\n" + sp*lvl + "}")
                return "".join(parts)
            if isinstance(n, list):
                if not n: return "[]"
                if ind is None or ind <= 0:
                    parts = ["["] + [("," if i else "") + dump_json(v, ind, lvl)
                                     for i,v in enumerate(n)] + ["]"]
                    return "".join(parts)
                sp = " " * ind
                parts = ["[\n"]
                for i,v in enumerate(n):
                    if i: parts.append(",\n")
                    parts.append(sp*(lvl+1) + dump_json(v, ind, lvl+1))
                parts.append("\n" + sp*lvl + "]")
                return "".join(parts)
            return json.dumps(n, ensure_ascii=False)
        out = dump_json(result, indent, 0) + "\n"

    if args.no_line_break:
        out = collapse_blank_lines(out)

    if args.output:
        write_text(args.output, out)
    else:
        sys.stdout.write(out)
    return 0


# Helpers for CLI args
def split_globs(s: Optional[str]) -> List[str]:
    if not s: return []
    return [p.strip() for p in re.split(r"[;,]", s) if p.strip()]

def parse_conditions(items: Optional[List[str]]) -> List[Condition]:
    out: List[Condition] = []
    for raw in (items or []):
        # format: FIELD:OP:VALUE  e.g., content:contains:React
        parts = raw.split(":", 2)
        if len(parts) == 3:
            out.append(Condition(parts[0].strip(), parts[1].strip(), parts[2]))
    return out

def build_file_list(root: str, include_globs: List[str], exclude_globs: List[str]) -> List[str]:
    files: List[str] = []
    for r, _, fs in os.walk(root):
        for f in fs:
            full = os.path.join(r, f)
            if include_globs:
                if not any(fnmatch.fnmatch(full, pat) for pat in include_globs):
                    continue
            if exclude_globs and any(fnmatch.fnmatch(full, pat) for pat in exclude_globs):
                continue
            files.append(full)
    return files


# =============================================================================
#                                   GUI
# =============================================================================

if _PYSIDE:
    
    # =========================================================================
    # Progress System Classes (v2.5.0)
    # =========================================================================
    
    class ProgressDetailsDialog(QDialog):
        """
        Expanded dialog showing detailed progress information.
        Shown when user clicks the expand button on a progress bar.
        Enhanced with time estimation and statistics (v2.5.0+).
        """
        def __init__(self, task_name: str, parent=None):
            super().__init__(parent)
            self.setWindowTitle(f"Progress Details - {task_name}")
            self.setModal(False)
            self.resize(600, 450)
            
            # Time tracking
            from datetime import datetime
            self.start_time = datetime.now()
            self.last_update_time = self.start_time
            
            layout = QVBoxLayout(self)
            
            # Task name label
            name_label = QLabel(f"<h3>{task_name}</h3>")
            layout.addWidget(name_label)
            
            # Progress bar (larger)
            self.progress_bar = QProgressBar()
            self.progress_bar.setMinimumHeight(30)
            layout.addWidget(self.progress_bar)
            
            # Status label with time estimation
            self.status_label = QLabel("Initializing...")
            layout.addWidget(self.status_label)
            
            # Statistics label (NEW - v2.5.0+)
            self.stats_label = QLabel("Speed: calculating...")
            self.stats_label.setStyleSheet("color: #666; font-size: 10px;")
            layout.addWidget(self.stats_label)
            
            # Details text (log area)
            details_label = QLabel("<b>Processing Details:</b>")
            layout.addWidget(details_label)
            
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumBlockCount(1000)  # Limit log size
            layout.addWidget(self.details_text)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            self.btn_minimize = QPushButton("↓ Minimize to Bar")
            self.btn_minimize.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_minimize)
            
            # Pause/Resume button (NEW - v2.5.0+)
            self.btn_pause = QPushButton("⏸ Pause")
            self.btn_pause.setCheckable(True)
            btn_layout.addWidget(self.btn_pause)
            
            self.btn_cancel = QPushButton("✖ Cancel Task")
            self.btn_cancel.clicked.connect(self.reject)
            btn_layout.addWidget(self.btn_cancel)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
        
        def update_progress(self, current: int, total: int, message: str = ""):
            """Update progress bar, status, and statistics (v2.5.0+)."""
            from datetime import datetime
            
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            
            percent = (current / total * 100) if total > 0 else 0
            status = f"Progress: {current}/{total} ({percent:.1f}%)"
            
            # Calculate time estimation (NEW - v2.5.0+)
            now = datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            
            if current > 0 and total > 0:
                # Calculate ETA
                speed = current / elapsed if elapsed > 0 else 0
                remaining = total - current
                eta_seconds = remaining / speed if speed > 0 else 0
                
                # Format time strings
                def format_time(seconds):
                    if seconds < 60:
                        return f"{int(seconds)}s"
                    elif seconds < 3600:
                        return f"{int(seconds / 60)}m {int(seconds % 60)}s"
                    else:
                        hours = int(seconds / 3600)
                        minutes = int((seconds % 3600) / 60)
                        return f"{hours}h {minutes}m"
                
                elapsed_str = format_time(elapsed)
                eta_str = format_time(eta_seconds) if eta_seconds > 0 else "calculating..."
                
                status += f" | Elapsed: {elapsed_str} | ETA: {eta_str}"
                
                # Update statistics label
                speed_str = f"{speed:.2f} files/sec" if speed >= 1 else f"{speed*60:.1f} files/min"
                self.stats_label.setText(f"Speed: {speed_str} | Total time: {elapsed_str}")
            
            if message:
                status += f"\n{message}"
            
            self.status_label.setText(status)
            self.last_update_time = now
        
        def add_log(self, message: str):
            """Add a log entry to details text."""
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.details_text.append(f"[{timestamp}] {message}")
    
    
    class OperationHistory:
        """
        Manages persistent history of operations (v2.5.0+).
        Saves to ~/.clarify_history.json
        """
        def __init__(self):
            from pathlib import Path
            self.history_file = Path.home() / ".clarify_history.json"
            self.history = self._load_history()
        
        def _load_history(self):
            """Load history from disk."""
            import json
            if self.history_file.exists():
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    return []
            return []
        
        def _save_history(self):
            """Save history to disk."""
            import json
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.history[-1000:], f, indent=2)  # Keep last 1000
            except Exception as e:
                print(f"Failed to save history: {e}")
        
        def add_operation(self, operation_type: str, details: dict):
            """Add operation to history."""
            from datetime import datetime
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": operation_type,
                "details": details
            }
            self.history.append(entry)
            self._save_history()
        
        def get_recent(self, count: int = 10):
            """Get recent operations."""
            return self.history[-count:]
        
        def clear(self):
            """Clear all history."""
            self.history = []
            self._save_history()
    
    
    class ProgressBarWidget(QWidget):
        """
        Individual progress bar widget with:
        - Task name label
        - Progress bar
        - Status label (current file/action)
        - Statistics label (speed, ETA) - NEW v2.5.0+
        - Expand button (↗)
        - Close button (✖)
        - Pause button (⏸) - NEW v2.5.0+
        """
        # Signals
        expand_requested = Signal(str)  # task_id
        close_requested = Signal(str)   # task_id
        cancel_requested = Signal(str)  # task_id
        pause_requested = Signal(str, bool)  # task_id, is_paused - NEW v2.5.0+
        
        def __init__(self, task_id: str, task_name: str, parent=None):
            super().__init__(parent)
            self.task_id = task_id
            self.task_name = task_name
            self.details_dialog = None
            
            # Time tracking (NEW - v2.5.0+)
            from datetime import datetime
            self.start_time = datetime.now()
            self.is_paused = False
            
            # Main layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(3)
            
            # Top row: task name + buttons
            top_layout = QHBoxLayout()
            
            self.name_label = QLabel(f"<b>{task_name}</b>")
            top_layout.addWidget(self.name_label)
            
            top_layout.addStretch()
            
            # Pause button (NEW - v2.5.0+)
            self.btn_pause = QPushButton("⏸")
            self.btn_pause.setFixedSize(25, 25)
            self.btn_pause.setCheckable(True)
            self.btn_pause.setToolTip("Pause/Resume task")
            self.btn_pause.clicked.connect(self._on_pause_clicked)
            top_layout.addWidget(self.btn_pause)
            
            # Expand button
            self.btn_expand = QPushButton("↗")
            self.btn_expand.setFixedSize(25, 25)
            self.btn_expand.setToolTip("Expand to detailed view")
            self.btn_expand.clicked.connect(self._on_expand_clicked)
            top_layout.addWidget(self.btn_expand)
            
            # Close button
            self.btn_close = QPushButton("✖")
            self.btn_close.setFixedSize(25, 25)
            self.btn_close.setToolTip("Close progress bar")
            self.btn_close.clicked.connect(self._on_close_clicked)
            top_layout.addWidget(self.btn_close)
            
            layout.addLayout(top_layout)
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)
            
            # Status label (current action)
            self.status_label = QLabel("Starting...")
            self.status_label.setStyleSheet("color: #666; font-size: 10px;")
            layout.addWidget(self.status_label)
            
            # Statistics label (NEW - v2.5.0+)
            self.stats_label = QLabel("")
            self.stats_label.setStyleSheet("color: #888; font-size: 9px;")
            layout.addWidget(self.stats_label)
            
            # Add border
            self.setStyleSheet("""
                ProgressBarWidget {
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    background-color: #f9f9f9;
                }
            """)
        
        def update_progress(self, current: int, total: int, message: str = ""):
            """Update progress bar, status, and statistics (v2.5.0+)."""
            from datetime import datetime
            
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            
            # Calculate statistics (NEW - v2.5.0+)
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if current > 0 and elapsed > 0:
                speed = current / elapsed
                remaining = total - current
                eta_seconds = remaining / speed if speed > 0 else 0
                
                # Format statistics
                if eta_seconds < 60:
                    eta_str = f"{int(eta_seconds)}s"
                elif eta_seconds < 3600:
                    eta_str = f"{int(eta_seconds / 60)}m"
                else:
                    eta_str = f"{int(eta_seconds / 3600)}h"
                
                speed_str = f"{speed:.1f}/s" if speed >= 1 else f"{speed*60:.1f}/min"
                self.stats_label.setText(f"Speed: {speed_str} | ETA: {eta_str}")
            
            if message:
                # Truncate long paths
                if len(message) > 60:
                    message = "..." + message[-57:]
                self.status_label.setText(message)
            
            # Update details dialog if open
            if self.details_dialog and self.details_dialog.isVisible():
                self.details_dialog.update_progress(current, total, message)
        
        def add_log(self, message: str):
            """Add log entry to details dialog if open."""
            if self.details_dialog and self.details_dialog.isVisible():
                self.details_dialog.add_log(message)
        
        def set_complete(self, success: bool = True):
            """Mark task as complete and show notification (v2.5.0+)."""
            self.progress_bar.setValue(self.progress_bar.maximum())
            if success:
                self.status_label.setText("✓ Completed")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self._show_notification("Task Complete", f"{self.task_name} finished successfully")
            else:
                self.status_label.setText("✖ Failed")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self._show_notification("Task Failed", f"{self.task_name} failed or was cancelled")
        
        def _show_notification(self, title: str, message: str):
            """Show desktop notification (v2.5.0+)."""
            try:
                # Try using plyer for cross-platform notifications
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Clarify",
                    timeout=5
                )
            except ImportError:
                # Fallback: use system notification if available
                try:
                    import subprocess
                    import platform
                    system = platform.system()
                    if system == "Linux":
                        subprocess.run(["notify-send", title, message], check=False)
                    elif system == "Darwin":  # macOS
                        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'], check=False)
                    # Windows would use win10toast, but skipping for now
                except Exception:
                    pass  # Notifications not available, silently continue
        
        def _on_pause_clicked(self):
            """Handle pause button clicked (v2.5.0+)."""
            self.is_paused = self.btn_pause.isChecked()
            if self.is_paused:
                self.btn_pause.setText("▶")
                self.btn_pause.setToolTip("Resume task")
                self.status_label.setText("⏸ Paused")
            else:
                self.btn_pause.setText("⏸")
                self.btn_pause.setToolTip("Pause task")
            
            self.pause_requested.emit(self.task_id, self.is_paused)
        
        def _on_expand_clicked(self):
            """Show detailed progress dialog."""
            if not self.details_dialog:
                self.details_dialog = ProgressDetailsDialog(self.task_name, self)
                self.details_dialog.rejected.connect(lambda: self.cancel_requested.emit(self.task_id))
            
            # Update dialog with current state
            current = self.progress_bar.value()
            total = self.progress_bar.maximum()
            self.details_dialog.update_progress(current, total, self.status_label.text())
            
            self.details_dialog.show()
            self.details_dialog.raise_()
            self.details_dialog.activateWindow()
        
        def _on_close_clicked(self):
            """Request to close this progress bar."""
            self.close_requested.emit(self.task_id)
    
    
    class ProgressManager(QWidget):
        """
        Manager widget that displays multiple progress bars at the bottom of the window.
        Features:
        - Scrollable area for multiple progress bars
        - Auto-hide when no active tasks
        - Can be expanded/collapsed
        """
        def __init__(self, parent=None):
            super().__init__(parent)
            self.active_tasks = {}  # task_id -> ProgressBarWidget
            
            # Main layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Header (collapsible)
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(5, 2, 5, 2)
            
            self.header_label = QLabel("<b>Active Tasks (0)</b>")
            header_layout.addWidget(self.header_label)
            
            header_layout.addStretch()
            
            self.btn_toggle = QPushButton("▼")
            self.btn_toggle.setFixedSize(20, 20)
            self.btn_toggle.setToolTip("Show/Hide progress bars")
            self.btn_toggle.clicked.connect(self._toggle_visibility)
            header_layout.addWidget(self.btn_toggle)
            
            layout.addLayout(header_layout)
            
            # Scroll area for progress bars
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setMaximumHeight(250)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # Container for progress bars
            self.bars_container = QWidget()
            self.bars_layout = QVBoxLayout(self.bars_container)
            self.bars_layout.setSpacing(5)
            self.bars_layout.setContentsMargins(5, 5, 5, 5)
            self.bars_layout.addStretch()
            
            self.scroll_area.setWidget(self.bars_container)
            layout.addWidget(self.scroll_area)
            
            # Initially hidden
            self.hide()
        
        def add_task(self, task_id: str, task_name: str) -> ProgressBarWidget:
            """Add a new task and return its progress bar widget."""
            if task_id in self.active_tasks:
                return self.active_tasks[task_id]
            
            progress_widget = ProgressBarWidget(task_id, task_name, self)
            progress_widget.close_requested.connect(self._on_task_close_requested)
            progress_widget.cancel_requested.connect(self._on_task_cancel_requested)
            
            # Insert before stretch
            self.bars_layout.insertWidget(self.bars_layout.count() - 1, progress_widget)
            
            self.active_tasks[task_id] = progress_widget
            self._update_header()
            self.show()
            
            return progress_widget
        
        def remove_task(self, task_id: str):
            """Remove a completed or cancelled task."""
            if task_id not in self.active_tasks:
                return
            
            widget = self.active_tasks.pop(task_id)
            self.bars_layout.removeWidget(widget)
            widget.deleteLater()
            
            self._update_header()
            
            # Hide if no more tasks
            if not self.active_tasks:
                self.hide()
        
        def get_task_widget(self, task_id: str) -> ProgressBarWidget:
            """Get progress widget for a specific task."""
            return self.active_tasks.get(task_id)
        
        def _update_header(self):
            """Update header label with task count."""
            count = len(self.active_tasks)
            self.header_label.setText(f"<b>Active Tasks ({count})</b>")
        
        def _toggle_visibility(self):
            """Toggle scroll area visibility."""
            visible = self.scroll_area.isVisible()
            self.scroll_area.setVisible(not visible)
            self.btn_toggle.setText("▲" if not visible else "▼")
        
        def _on_task_close_requested(self, task_id: str):
            """Handle close button clicked on a progress bar."""
            self.remove_task(task_id)
        
        def _on_task_cancel_requested(self, task_id: str):
            """Handle cancel request from details dialog."""
            # Emit signal to cancel the actual task
            # This will be connected to worker.cancel() by the panel
            widget = self.get_task_widget(task_id)
            if widget:
                widget.set_complete(success=False)
                # Actual cancellation is handled by the panel that created the task
    
    
    class SearchWorker(QObject):
        # Signals with enhanced progress tracking (v2.5.0+)
        progress = Signal(str)  # Current file being processed
        progress_detailed = Signal(int, int, str)  # (current, total, message) for progress bar
        done = Signal(dict)  # Final results
        error = Signal(str)  # Error messages

        def __init__(self, pattern_text: str, iter_files_fn, search_options_factory, 
                     is_multi_query: bool = False, multi_query_processor=None):
            super().__init__()
            self.pattern_text = pattern_text
            self.iter_files_fn = iter_files_fn
            self.search_options_factory = search_options_factory
            self.is_multi_query = is_multi_query  # v2.8.0
            self.multi_query_processor = multi_query_processor  # v2.8.0
            self._cancel = False
            self._paused = False  # NEW - v2.5.0+

        def cancel(self):
            self._cancel = True
        
        def pause(self):
            """Pause processing (v2.5.0+)."""
            self._paused = True
        
        def resume(self):
            """Resume processing (v2.5.0+)."""
            self._paused = False

        def run(self):
            """Executa o processamento pesado fora da GUI thread com progresso detalhado e pausar/retomar (v2.5.0+).
            v2.8.0: Suporte para multi-query search."""
            import time
            
            matches: Dict[str, List[Tuple[int, int, str]]] = {}
            
            # Collect all files first to know total count
            files_to_process = list(self.iter_files_fn())
            total_files = len(files_to_process)
            
            for idx, p in enumerate(files_to_process, 1):
                # Check for cancellation
                if self._cancel:
                    break
                
                # Check for pause (NEW - v2.5.0+)
                while self._paused and not self._cancel:
                    time.sleep(0.1)  # Wait while paused
                
                try:
                    # Emit detailed progress (current, total, message)
                    self.progress.emit(p)  # Legacy signal for backward compatibility
                    self.progress_detailed.emit(idx, total_files, p)
                    
                    text = read_text(p)
                    lst: List[Tuple[int, int, str]] = []
                    
                    # v2.8.0: Multi-query search support
                    if self.is_multi_query and self.multi_query_processor:
                        # Use MultiQueryProcessor for multiple patterns
                        query_matches = self.multi_query_processor.search_in_text(text)
                        # Convert from (line, col, snippet, query_line_num) to (line, col, snippet)
                        lst = [(line, col, snippet) for line, col, snippet, _ in query_matches]
                    else:
                        # Single pattern search (original behavior)
                        for m in self.pattern_text.finditer(text):
                            line = text.count("\n", 0, m.start()) + 1
                            col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                            snippet = text.splitlines()[line - 1] if line - 1 < len(text.splitlines()) else ""
                            lst.append((line, col, snippet))
                    
                    if lst:
                        matches[p] = lst
                except Exception as e:
                    self.error.emit(f"[WARN] {p}: {e}")
                    # continue to next files
            
            self.done.emit(matches)

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

        def populate(self, matches: Dict[str, List[Tuple[int,int,str]]]):
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
                
                # Add file matches
                for path, items in matches.items():
                    top = QTreeWidgetItem([path])
                    self.addTopLevelItem(top)
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


    class SearchReplacePanel(QWidget):
        """
        Left-hand panel: path + include/exclude + search & replace controls.
        Right-hand panel: results.
        Now with integrated progress bar system (v2.5.0).
        """
        request_preview = Signal(dict)   # emits {"matches": {path: [(line,col,snip), ...], ...}}

        def __init__(self, parent=None, progress_manager=None):
            super().__init__(parent)
            root = QVBoxLayout(self)
            self.processing_search = False
            self.progress_manager = progress_manager
            self._current_task_id = None
            self._processing_modal = None  # Modal de progresso
            
            # Path row
            column = QVBoxLayout()
            row = QHBoxLayout()
            row.addWidget(QLabel("Root path:"))
            self.ed_path = QLineEdit()
            self.ed_path.setToolTip("Enter the directory path or file path to search in")
            self.btn_browse = QPushButton("Browse…")
            self.btn_browse.setToolTip("Open file browser to select a directory or file")
            row.addWidget(self.ed_path, 1)
            row.addWidget(self.btn_browse)
            column.addLayout(row)
            self.is_file = QCheckBox("Is File?")
            self.is_file.setToolTip("Check this if you want to process a single file instead of a directory")
            column.addWidget(self.is_file)
            root.addLayout(column)

            # File extension filter (v2.9.0, v2.9.1 - optional)
            row = QHBoxLayout()
            self.chk_use_ext_filter = QCheckBox("Use extension filter")
            self.chk_use_ext_filter.setChecked(True)  # Default: enabled
            self.chk_use_ext_filter.setToolTip("Enable simple extension filtering (.py,.js,.tsx)")
            row.addWidget(self.chk_use_ext_filter)
            row.addWidget(QLabel("Extensions:"))
            self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
            self.ed_extensions.setPlaceholderText("e.g., .py,.js,.tsx (leave empty for all)")
            self.ed_extensions.setToolTip("Filter files by extensions. Examples:\n"
                                         "  .py          - Only Python files\n"
                                         "  .jsx,.tsx    - React files\n"
                                         "  .js,.ts      - JavaScript/TypeScript\n"
                                         "Leave empty to include all file types")
            row.addWidget(self.ed_extensions)
            root.addLayout(row)
            
            # Include/Exclude globs (advanced)
            row = QHBoxLayout()
            row.addWidget(QLabel("Include globs (advanced, comma-separated):"))
            self.ed_inc = QLineEdit()
            self.ed_inc.setPlaceholderText("e.g., *.test.*, **/src/** (leave empty for all)")
            self.ed_inc.setToolTip("Advanced glob patterns to include specific files.\nExamples:\n  *.test.*    - Test files\n  **/src/**   - Files in src folders")
            root.addLayout(row)
            root.addWidget(self.ed_inc)
            row = QHBoxLayout()
            row.addWidget(QLabel("Exclude globs (comma-separated):"))
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            self.ed_exc.setToolTip("Glob patterns to exclude folders/files.\nDefault excludes common build/dependency folders")
            root.addLayout(row)
            root.addWidget(self.ed_exc)

            # Search field + toggles
            gb = QGroupBox("Search")
            g = QGridLayout(gb)
            g.addWidget(QLabel("Query:"), 0, 0)
            self.ed_query = QLineEdit()
            self.ed_query.setToolTip("Enter the text pattern to search for in files")
            self.chk_case = QCheckBox("Case sensitive")
            self.chk_case.setToolTip("Match exact case (A ≠ a)")
            self.chk_word = QCheckBox("Whole word")
            self.chk_word.setToolTip("Match only complete words (not partial matches)")
            self.chk_regex = QCheckBox("Regex")
            self.chk_regex.setToolTip("Treat query as a regular expression pattern")
            self.chk_multi_query = QCheckBox("Multi-line")  # v2.8.0
            self.chk_multi_query.setToolTip("Enable multi-line query mode:\n"
                                           "- Each line is a separate search\n"
                                           "- Lines starting with # are comments\n"
                                           "- Empty lines are ignored")
            self.btn_search = QPushButton("Search/Cancel")
            self.btn_search.setToolTip("Start search operation or cancel if already running")
            g.addWidget(self.ed_query, 0, 1, 1, 3)
            g.addWidget(self.chk_case, 1, 0)
            g.addWidget(self.chk_word, 1, 1)
            g.addWidget(self.chk_regex, 1, 2)
            g.addWidget(self.chk_multi_query, 1, 3)  # v2.8.0
            g.addWidget(self.btn_search, 2, 3)  # Moved to row 2
            
            # Connect multi-query checkbox to switch input mode
            self.chk_multi_query.toggled.connect(self._toggle_multi_query_mode)
            
            root.addWidget(gb)

            # Replace extras (optional)
            gb2 = QGroupBox("Replace (enable if needed)")
            g2 = QGridLayout(gb2)
            g2.addWidget(QLabel("Replacement:"), 0, 0)
            self.ed_repl = QLineEdit()
            self.ed_repl.setToolTip("Enter the replacement text (supports regex capture groups like $1, $2)")
            self.chk_preserve = QCheckBox("Preserve case")
            self.chk_preserve.setToolTip("Maintain the original case pattern when replacing")
            self.btn_replace_one = QPushButton("Replace first per file")
            self.btn_replace_one.setToolTip("Replace only the first occurrence in each file")
            self.btn_replace_all = QPushButton("Replace all")
            self.btn_replace_all.setToolTip("Replace all occurrences in all matching files")
            g2.addWidget(self.ed_repl, 0, 1, 1, 3)
            g2.addWidget(self.chk_preserve, 1, 0)
            g2.addWidget(self.btn_replace_one, 1, 2)
            g2.addWidget(self.btn_replace_all, 1, 3)
            root.addWidget(gb2)

            # Advanced conditions (collapsible style via group box)
            gb3 = QGroupBox("Advanced conditions (when operating on a folder)")
            g3 = QGridLayout(gb3)
            
            # Add AND/OR selector at the top
            lbl_logic = QLabel("Logic Operator:")
            self.combo_logic_op = QComboBox()
            self.combo_logic_op.addItems(["AND", "OR"])
            self.combo_logic_op.setToolTip("AND: All conditions must match\nOR: At least one condition must match")
            logic_layout = QHBoxLayout()
            logic_layout.addWidget(lbl_logic)
            logic_layout.addWidget(self.combo_logic_op)
            logic_layout.addStretch()
            g3.addLayout(logic_layout, 0, 0, 1, 8)
            
            # Add headers (now starting from row 1)
            g3.addWidget(QLabel("Field"), 1, 0)
            g3.addWidget(QLabel("Operator"), 1, 1)
            g3.addWidget(QLabel("Value"), 1, 2)
            g3.addWidget(QLabel("Scope"), 1, 3)
            g3.addWidget(QLabel("Scope Param"), 1, 4)
            g3.addWidget(QLabel("Case"), 1, 5)
            g3.addWidget(QLabel("Word"), 1, 6)
            g3.addWidget(QLabel("Regex"), 1, 7)
            
            self.cond_list: List[Tuple[QComboBox, QComboBox, QLineEdit, QComboBox, QLineEdit, QCheckBox, QCheckBox, QCheckBox]] = []
            for row_i in range(2, 5):  # three rows to start; users can reuse them (row 0 is logic operator, row 1 is headers)
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
                cb_op = QComboBox(); cb_op.addItems(["", "contains", "not contains", "equals", "not equals",
                                                     "starts with", "ends with", ">", "<", ">=", "<="])
                ed_val = QLineEdit()
                cb_scope = QComboBox(); cb_scope.addItems(["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag"])
                ed_scope_val = QLineEdit()
                ed_scope_val.setPlaceholderText("e.g., 'begin,end' or 'div'")
                
                # Checkboxes for matching options
                chk_case = QCheckBox()
                chk_case.setChecked(True)  # Default: case sensitive
                chk_case.setToolTip("Case sensitive")
                chk_word = QCheckBox()
                chk_word.setToolTip("Match whole word")
                chk_regex = QCheckBox()
                chk_regex.setToolTip("Use regular expression")
                
                g3.addWidget(cb_field, row_i, 0)
                g3.addWidget(cb_op,    row_i, 1)
                g3.addWidget(ed_val,   row_i, 2)
                g3.addWidget(cb_scope, row_i, 3)
                g3.addWidget(ed_scope_val, row_i, 4)
                g3.addWidget(chk_case, row_i, 5)
                g3.addWidget(chk_word, row_i, 6)
                g3.addWidget(chk_regex, row_i, 7)
                self.cond_list.append((cb_field, cb_op, ed_val, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex))
            root.addWidget(gb3)

            # Results on the right
            self.results = ResultsTree()
            
            # Results panel with save button
            results_layout = QVBoxLayout()
            results_header = QHBoxLayout()
            results_label = QLabel("Search Results")
            results_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            self.btn_save_results = QPushButton("💾 Save Results")
            self.btn_save_results.setToolTip("Save all search results to a formatted text file with statistics")
            self.btn_save_results.clicked.connect(self._save_results)
            results_header.addWidget(results_label)
            results_header.addStretch()
            results_header.addWidget(self.btn_save_results)
            results_layout.addLayout(results_header)
            results_layout.addWidget(self.results)
            
            # Status bar at bottom showing position info (v2.5.1)
            self.results_status = QLabel("")
            self.results_status.setStyleSheet("padding: 4px; background-color: #f0f0f0; color: #333; font-size: 10pt;")
            self.results_status.setMinimumHeight(25)
            results_layout.addWidget(self.results_status)
            
            # Connect status label to results tree
            self.results.set_status_label(self.results_status)
            
            results_widget = QWidget()
            results_widget.setLayout(results_layout)

            splitter = QSplitter()
            left = QWidget(); left.setLayout(root)
            splitter.addWidget(left)
            splitter.addWidget(results_widget)
            splitter.setSizes([500, 800])

            wroot = QVBoxLayout(self)
            wroot.setContentsMargins(0, 0, 0, 0)
            wroot.addWidget(splitter)

            # Connect
            self.is_file.stateChanged.connect(self.change_advanced_conditions)
            self.btn_browse.clicked.connect(self._browse)
            self.btn_search.clicked.connect(self._start_search_threaded)
            self.btn_replace_one.clicked.connect(lambda: self._do_replace(all_=False))
            self.btn_replace_all.clicked.connect(lambda: self._do_replace(all_=True))

        def change_advanced_conditions(self):
            self.enable_buttons(not self.is_file.isChecked(), include_buttons = False)
        
        def _browse(self):
            if self.is_file.isChecked():
                #self.enable_buttons(False, include_buttons = False)
                path, _ = QFileDialog.getOpenFileName(self, "Select dictionary", "", "JSON/TS (*.json *.ts *.tsx *.js *.jsx);;All (*)")
            else:
                #self.enable_buttons(True, include_buttons = False)
                path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
            
            if path:
                self.ed_path.setText(path)
            
        def _conds(self) -> tuple[List[Condition], str]:
            """Return conditions and logic operator (AND/OR)"""
            out: List[Condition] = []
            if not self.is_file.isChecked():
                for cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex in self.cond_list:
                    f = cb_field.currentText().strip()
                    o = cb_op.currentText().strip()
                    v = ed.text().strip()
                    scope_type = cb_scope.currentText().strip()
                    scope_val = ed_scope_val.text().strip()
                    case_sensitive = chk_case.isChecked()
                    whole_word = chk_word.isChecked()
                    use_regex = chk_regex.isChecked()
                    if f and o and v:
                        out.append(Condition(f, o, v, scope_type, scope_val, case_sensitive, whole_word, use_regex))
            logic_op = self.combo_logic_op.currentText()
            return out, logic_op
        
        def _iter_files(self) -> List[str]:
            path = self.ed_path.text().strip()
            
            # v2.9.0, v2.9.1: Handle extension filter (optional)
            use_ext_filter = self.chk_use_ext_filter.isChecked()
            extensions_text = self.ed_extensions.text().strip() if use_ext_filter else ""
            ed_inc_text = self.ed_inc.text().strip()
            
            # Build include globs from extensions if enabled and provided
            if use_ext_filter and extensions_text:
                # Parse extensions (comma or semicolon separated)
                extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
                # Ensure extensions start with dot
                extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
                # Convert to glob patterns
                ext_globs = [f"*{ext}" for ext in extensions]
                
                # Combine with user-provided include globs if any
                if ed_inc_text:
                    inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
                    inc.extend(ext_globs)
                else:
                    inc = ext_globs
            else:
                # No extension filter, use include globs or default
                if ed_inc_text:
                    inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
                else:
                    inc = ["*.*"]  # Default: all files
                
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            conds, logic_op = self._conds()
            return filter_files_by_conditions(files, conds, logic_op)

        # def _do_search(self):
        #     try:
        #         patt = SearchOptions(self.chk_case.isChecked(),
        #                              self.chk_word.isChecked(),
        #                              self.chk_regex.isChecked()).compile(self.ed_query.text())
        #     except ValueError as e:
        #         QMessageBox.critical(self, "Invalid pattern", str(e)); return

        #     matches: Dict[str, List[Tuple[int,int,str]]] = {}
        #     for p in self._iter_files():
        #         try:
        #             text = read_text(p)
        #             lst: List[Tuple[int,int,str]] = []
        #             for m in patt.finditer(text):
        #                 line = text.count("\n", 0, m.start()) + 1
        #                 col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
        #                 snippet = text.splitlines()[line-1]
        #                 lst.append((line, col, snippet))
        #             if lst:
        #                 matches[p] = lst
        #         except Exception as e:
        #             print(f"[WARN] {p}: {e}", file=sys.stderr)
        #     self.results.populate(matches)
        
        def _toggle_multi_query_mode(self, enabled: bool):
            """Toggle between single-line and multi-line query mode (v2.8.0)"""
            if enabled:
                # Switch to QPlainTextEdit for multi-line
                current_text = self.ed_query.text()
                
                # Replace QLineEdit with QPlainTextEdit
                layout = self.ed_query.parent().layout()
                item_index = layout.indexOf(self.ed_query)
                self.ed_query.hide()
                
                if not hasattr(self, 'ed_query_multi'):
                    self.ed_query_multi = QPlainTextEdit()
                    self.ed_query_multi.setMaximumHeight(120)
                    self.ed_query_multi.setPlaceholderText(
                        "Enter multiple queries (one per line)\n"
                        "# Lines starting with # are comments\n"
                        "Example:\n"
                        "  function.*test\n"
                        "  class\\s+\\w+\n"
                        "  # This is a comment"
                    )
                    layout.addWidget(self.ed_query_multi, 0, 1, 1, 3)
                
                self.ed_query_multi.setPlainText(current_text)
                self.ed_query_multi.show()
            else:
                # Switch back to QLineEdit for single-line
                if hasattr(self, 'ed_query_multi'):
                    current_text = self.ed_query_multi.toPlainText().strip()
                    # Take only first non-empty line
                    first_line = next((line for line in current_text.split('\n') 
                                      if line.strip() and not line.strip().startswith('#')), "")
                    self.ed_query.setText(first_line)
                    self.ed_query_multi.hide()
                
                self.ed_query.show()
        
        def enable_buttons(self, state, include_buttons=True, include_advanced_conditions = True):
            if include_buttons:
                self.btn_browse.setEnabled(state)
                self.btn_replace_one.setEnabled(state)
                self.btn_replace_all.setEnabled(state)
            
            if include_advanced_conditions:
                for cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex in self.cond_list:
                    cb_field.setEnabled(state)
                    cb_op.setEnabled(state)
                    ed.setEnabled(state)
                    ed.setReadOnly(not state)
                    cb_scope.setEnabled(state)
                    ed_scope_val.setEnabled(state)
                    ed_scope_val.setReadOnly(not state)
                    chk_case.setEnabled(state)
                    chk_word.setEnabled(state)
                    chk_regex.setEnabled(state)
        
        def _start_search_threaded(self):
            if not self.processing_search:
                # Verifica se feature já está rodando
                if not thread_manager.can_start_feature(FeatureType.SEARCH_REPLACE):
                    QMessageBox.warning(
                        self, 
                        "Already Running",
                        "Search/Replace is already running. Please wait or cancel the current operation."
                    )
                    return
                
                self.results.print_message("Loading...")
                
                # Get query text (v2.8.0 - support multi-query)
                is_multi_query = self.chk_multi_query.isChecked() and hasattr(self, 'ed_query_multi')
                if is_multi_query:
                    query_text = self.ed_query_multi.toPlainText()
                else:
                    query_text = self.ed_query.text()
                
                # v2.8.0: Prepare multi-query processor or single pattern
                pattern_text = None
                multi_query_processor = None
                
                if is_multi_query:
                    # Import and create MultiQueryProcessor
                    from src.core.multi_query import MultiQueryProcessor
                    try:
                        multi_query_processor = MultiQueryProcessor(
                            multi_line_text=query_text,
                            case_sensitive=self.chk_case.isChecked(),
                            whole_word=self.chk_word.isChecked(),
                            use_regex=self.chk_regex.isChecked()
                        )
                        # Validate queries
                        is_valid, error_msg = multi_query_processor.validate()
                        if not is_valid:
                            self.error.emit(f"Invalid queries: {error_msg}")
                            self.done.emit({})
                            return
                        
                        # Check if there are any queries
                        if multi_query_processor.get_query_count() == 0:
                            self.error.emit("No valid queries found. Add at least one search pattern.")
                            self.done.emit({})
                            return
                    except Exception as e:
                        self.error.emit(f"Multi-query error: {e}")
                        self.done.emit({})
                        return
                else:
                    # Single query mode - compile pattern
                    try:
                        pattern_text = SearchOptions(self.chk_case.isChecked(),
                            self.chk_word.isChecked(),
                            self.chk_regex.isChecked()).compile(query_text)
                    except Exception as e:
                        self.error.emit(f"Invalid pattern: {e}")
                        self.done.emit({})
                        return
                
                # Create processing modal (v2.7.0, v2.8.0 - multi-query info)
                self._processing_modal = ProcessingModal(
                    title="Search/Replace Processing",
                    parent=self,
                    show_progress=True,
                    show_cancel=True
                )
                if is_multi_query:
                    query_count = multi_query_processor.get_query_count()
                    self._processing_modal.set_title(f"Searching Files ({query_count} queries)...")
                    self._processing_modal.set_status(f"Initializing multi-query search with {query_count} patterns...")
                else:
                    self._processing_modal.set_title("Searching Files...")
                    self._processing_modal.set_status("Initializing search...")
                self._processing_modal.start_loading_animation()
                self._processing_modal.show()
                
                # Create progress bar (v2.5.0, v2.8.0) - mantido para compatibilidade
                if self.progress_manager:
                    import uuid
                    self._current_task_id = f"search_{uuid.uuid4().hex[:8]}"
                    if is_multi_query:
                        query_count = multi_query_processor.get_query_count()
                        task_label = f"Multi-Search ({query_count} queries)"
                    else:
                        task_label = f"Search: {self.ed_query.text()[:30]}"
                    self._current_progress_widget = self.progress_manager.add_task(
                        self._current_task_id,
                        task_label
                    )
                
                # Create thread and worker (v2.8.0 - multi-query support)
                self._search_thread = QThread(self)
                self._search_worker = SearchWorker(
                    pattern_text=pattern_text,
                    iter_files_fn=self._iter_files,
                    search_options_factory=lambda a,b,c: SearchOptions(a,b,c),
                    is_multi_query=is_multi_query,
                    multi_query_processor=multi_query_processor
                )
                self._search_worker.moveToThread(self._search_thread)
                
                # Register thread with ThreadManager
                import uuid
                thread_id = f"search_replace_{uuid.uuid4().hex[:8]}"
                if not thread_manager.start_thread(
                    thread_id=thread_id,
                    thread=self._search_thread,
                    worker=self._search_worker,
                    feature=FeatureType.SEARCH_REPLACE,
                    cancel_callback=lambda: self._search_worker.cancel()
                ):
                    QMessageBox.warning(self, "Error", "Failed to start search thread.")
                    if self._processing_modal:
                        self._processing_modal.close()
                        self._processing_modal = None
                    return

                # Connections
                self._search_thread.started.connect(self._search_worker.run)
                self._search_worker.done.connect(self._on_search_done)
                self._search_worker.progress.connect(self._on_search_progress)
                self._search_worker.progress_detailed.connect(self._on_search_progress_detailed)  # v2.5.0
                self._search_worker.error.connect(self._on_search_error)

                # Connect cancel from modal to worker (v2.7.0)
                if self._processing_modal:
                    self._processing_modal.cancel_requested.connect(
                        lambda: self._search_worker.cancel()
                    )
                
                # Connect cancel and pause from progress bar to worker (v2.5.0+)
                if self._current_progress_widget:
                    self._current_progress_widget.cancel_requested.connect(
                        lambda _: self._search_worker.cancel()
                    )
                    self._current_progress_widget.pause_requested.connect(
                        lambda _, paused: self._search_worker.pause() if paused else self._search_worker.resume()
                    )

                # Cleanup
                self._search_worker.done.connect(self._search_thread.quit)
                self._search_worker.done.connect(self._search_worker.deleteLater)
                self._search_thread.finished.connect(self._search_thread.deleteLater)

                self._search_thread.start()
                self.enable_buttons(False)
                self.processing_search = True
            else:
                # Cancela processamento em andamento
                if self._search_worker:
                    self._search_worker.cancel()
                self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
                self.processing_search = False

        def _on_search_progress(self, current_path: str):
            """Legacy progress handler - kept for compatibility."""
            pass

        def _on_search_progress_detailed(self, current: int, total: int, message: str):
            """New detailed progress handler (v2.5.0)."""
            # Update processing modal (v2.7.0)
            if self._processing_modal:
                progress = int((current / total * 100)) if total > 0 else 0
                self._processing_modal.set_progress(progress)
                self._processing_modal.set_status(f"Processing {current}/{total} files")
                self._processing_modal.log_message(message)
            
            # Update progress widget (v2.5.0) - mantido para compatibilidade
            if self._current_progress_widget:
                self._current_progress_widget.update_progress(current, total, message)
                self._current_progress_widget.add_log(f"Processing: {message}")

        def _on_search_error(self, msg: str):
            """Handle search errors."""
            # Update processing modal (v2.7.0)
            if self._processing_modal:
                self._processing_modal.log_message(f"ERROR: {msg}")
            
            # Update progress widget (v2.5.0) - mantido para compatibilidade
            if self._current_progress_widget:
                self._current_progress_widget.add_log(f"ERROR: {msg}")
            print(msg)

        def _on_search_done(self, matches: dict):
            """Handle search completion with history tracking (v2.5.0+)."""
            self.results.populate(matches)
            self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
            self.processing_search = False
            
            # Mark processing modal as complete (v2.7.0)
            if self._processing_modal:
                self._processing_modal.mark_completed(
                    success=True,
                    message=f"Search completed successfully!\nFound matches in {len(matches)} file(s)."
                )
                # Modal permanece aberta para usuário revisar logs e fechar manualmente
            
            # Mark progress as complete (v2.5.0)
            if self._current_progress_widget:
                self._current_progress_widget.set_complete(success=True)
                self._current_progress_widget.add_log(f"Search completed: {len(matches)} files with matches")
            
            # Save to history (NEW - v2.5.0+)
            try:
                history = OperationHistory()
                history.add_operation("search", {
                    "query": self.ed_query.text(),
                    "path": self.ed_path.text(),
                    "files_matched": len(matches),
                    "total_matches": sum(len(items) for items in matches.values()),
                    "case_sensitive": self.chk_case.isChecked(),
                    "whole_word": self.chk_word.isChecked(),
                    "regex": self.chk_regex.isChecked()
                })
            except Exception as e:
                print(f"Failed to save history: {e}")
            
            # Don't auto-remove progress bar - let user close it manually
        
        def _save_results(self):
            """Save search results to a text file."""
            matches_data = self.results.get_matches_data()
            
            if not matches_data:
                QMessageBox.information(self, "No Results", 
                    "No search results to save. Please perform a search first.")
                return
            
            # Ask user for file location
            default_filename = "clarify_search_results.txt"
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Search Results", 
                default_filename,
                "Text Files (*.txt);;All Files (*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            try:
                # Export matches to text
                text_content = self.results.export_to_text()
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                total_files = len(matches_data)
                total_matches = sum(len(items) for items in matches_data.values())
                
                QMessageBox.information(self, "Results Saved", 
                    f"Search results saved successfully!\n\n"
                    f"File: {file_path}\n"
                    f"Total files: {total_files}\n"
                    f"Total matches: {total_matches}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                    f"Failed to save results:\n{str(e)}")

        def _do_replace(self, all_: bool):
            try:
                patt = SearchOptions(self.chk_case.isChecked(),
                                     self.chk_word.isChecked(),
                                     self.chk_regex.isChecked()).compile(self.ed_query.text())
            except ValueError as e:
                QMessageBox.critical(self, "Invalid pattern", str(e)); return

            repl = self.ed_repl.text()
            preserve = self.chk_preserve.isChecked()
            count_files = 0
            for p in self._iter_files():
                try:
                    text = read_text(p)
                    new, n = replace_in_text(text, patt, repl, preserve, 0 if all_ else 1)
                    if n > 0:
                        write_text(p, new)
                        count_files += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            QMessageBox.information(self, "Replace", f"Modified files: {count_files}")
            self.results.print_message()


    class InsertPanel(QWidget):
        request_status = Signal(str)

        def __init__(self, parent=None, progress_manager=None):
            super().__init__(parent)
            layout = QGridLayout(self)
            self.processing_search = False
            self.progress_manager = progress_manager
            self._current_task_id = None
            self._current_progress_widget = None
            self._processing_modal = None  # Modal de progresso (v2.7.0)
            
            layout.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit()
            self.ed_path.setToolTip("Enter the directory path or file path for insertion")
            self.btn_browse = QPushButton("Browse…")
            self.btn_browse.setToolTip("Open file browser to select a directory or file")
            layout.addWidget(self.ed_path, 0, 1, 1, 3)
            layout.addWidget(self.btn_browse, 0, 4)
            
            self.is_file = QCheckBox("Is File?")
            self.is_file.setToolTip("Check this if you want to process a single file instead of a directory")
            layout.addWidget(self.is_file, 1, 0)
            
            # Extension filter (v2.9.0, v2.9.1 - optional)
            self.chk_use_ext_filter = QCheckBox("Use extension filter")
            self.chk_use_ext_filter.setChecked(True)
            self.chk_use_ext_filter.setToolTip("Enable simple extension filtering")
            layout.addWidget(self.chk_use_ext_filter, 2, 0)
            layout.addWidget(QLabel("Extensions:"), 2, 1)
            self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
            self.ed_extensions.setPlaceholderText("e.g., .py,.js,.tsx (leave empty for all)")
            self.ed_extensions.setToolTip("Filter files by extensions")
            layout.addWidget(self.ed_extensions, 2, 2, 1, 3)
            
            layout.addWidget(QLabel("Include globs (advanced):"), 3, 0)
            self.ed_inc = QLineEdit()
            self.ed_inc.setPlaceholderText("e.g., *.test.*, **/src/**")
            self.ed_inc.setToolTip("Advanced glob patterns to include specific files")
            layout.addWidget(self.ed_inc, 3, 1, 1, 4)

            layout.addWidget(QLabel("Exclude globs:"), 4, 0)
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            self.ed_exc.setToolTip("Glob patterns to exclude folders/files")
            layout.addWidget(self.ed_exc, 4, 1, 1, 4)

            # Search/Lookup section (new feature)
            gb_lookup = QGroupBox("Line Lookup (optional - leave empty to use line number)")
            g_lookup = QGridLayout(gb_lookup)
            g_lookup.addWidget(QLabel("Search query:"), 0, 0)
            self.ed_query = QLineEdit()
            self.ed_query.setPlaceholderText("Enter text to search for line position")
            self.ed_query.setToolTip("Search for text to determine insertion position dynamically")
            g_lookup.addWidget(self.ed_query, 0, 1, 1, 3)
            
            self.chk_lookup_case = QCheckBox("Case sensitive")
            self.chk_lookup_case.setToolTip("Match exact case in lookup query")
            self.chk_lookup_word = QCheckBox("Whole word")
            self.chk_lookup_word.setToolTip("Match only complete words in lookup")
            self.chk_lookup_regex = QCheckBox("Regex")
            self.chk_lookup_regex.setToolTip("Treat lookup query as a regular expression")
            g_lookup.addWidget(self.chk_lookup_case, 1, 0)
            g_lookup.addWidget(self.chk_lookup_word, 1, 1)
            g_lookup.addWidget(self.chk_lookup_regex, 1, 2)
            
            self.cb_lookup_occurrence = QComboBox()
            self.cb_lookup_occurrence.addItems(["First", "Last", "All"])
            self.cb_lookup_occurrence.setToolTip("Which occurrence to use for insertion")
            g_lookup.addWidget(QLabel("Occurrence:"), 1, 3)
            g_lookup.addWidget(self.cb_lookup_occurrence, 1, 4)
            layout.addWidget(gb_lookup, 5, 0, 1, 5)

            layout.addWidget(QLabel("Line number (1-based):"), 6, 0)
            self.spin_line = QSpinBox(); self.spin_line.setRange(1, 10_000_000); self.spin_line.setValue(1)
            self.spin_line.setToolTip("Manual line number (used only if search query is empty)")
            layout.addWidget(self.spin_line, 6, 1)

            layout.addWidget(QLabel("Insert text:"), 7, 0)
            self.ed_text = QPlainTextEdit()
            self.ed_text.setToolTip("Enter the text content to insert into files")
            layout.addWidget(self.ed_text, 7, 1, 1, 4)

            layout.addWidget(QLabel("Mode:"), 8, 0)
            self.cb_mode = QComboBox()
            self.cb_mode.addItems([InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE,
                                   InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW])
            self.cb_mode.setToolTip("Choose insertion mode:\n  left: Insert before line\n  right: Insert after line\n  replace: Replace line\n  insert-above: Add new line above\n  insert-below: Add new line below")
            layout.addWidget(self.cb_mode, 8, 1)

            self._debounce_timer = QTimer(self)
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.setInterval(300)
            self._debounce_timer.timeout.connect(self._start_search_threaded)
            
            # Advanced conditions (same as Search/Replace, including `content`)
            gb3 = QGroupBox("Advanced conditions (folder mode)")
            g3 = QGridLayout(gb3)
            
            # Add AND/OR selector at the top
            lbl_logic = QLabel("Logic Operator:")
            self.combo_logic_op = QComboBox()
            self.combo_logic_op.addItems(["AND", "OR"])
            self.combo_logic_op.setToolTip("AND: All conditions must match\nOR: At least one condition must match")
            self.combo_logic_op.currentTextChanged.connect(self._schedule_live_refresh)
            logic_layout = QHBoxLayout()
            logic_layout.addWidget(lbl_logic)
            logic_layout.addWidget(self.combo_logic_op)
            logic_layout.addStretch()
            g3.addLayout(logic_layout, 0, 0, 1, 8)
            
            # Add headers (now starting from row 1)
            g3.addWidget(QLabel("Field"), 1, 0)
            g3.addWidget(QLabel("Operator"), 1, 1)
            g3.addWidget(QLabel("Value"), 1, 2)
            g3.addWidget(QLabel("Scope"), 1, 3)
            g3.addWidget(QLabel("Scope Param"), 1, 4)
            g3.addWidget(QLabel("Case"), 1, 5)
            g3.addWidget(QLabel("Word"), 1, 6)
            g3.addWidget(QLabel("Regex"), 1, 7)
            
            self.cond_list: List[Tuple[QComboBox, QComboBox, QLineEdit, QComboBox, QLineEdit, QCheckBox, QCheckBox, QCheckBox]] = []
            for row_i in range(2, 5):  # three rows to start (row 0 is logic operator, row 1 is headers)
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
                cb_field.currentTextChanged.connect(self._schedule_live_refresh)
                cb_op = QComboBox(); cb_op.addItems(["", "contains", "not contains", "equals", "not equals",
                                                     "starts with", "ends with", ">", "<", ">=", "<="])
                cb_op.currentTextChanged.connect(self._schedule_live_refresh)
                ed_val = QLineEdit()
                ed_val.textChanged.connect(self._schedule_live_refresh)
                cb_scope = QComboBox(); cb_scope.addItems(["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag"])
                cb_scope.currentTextChanged.connect(self._schedule_live_refresh)
                ed_scope_val = QLineEdit()
                ed_scope_val.setPlaceholderText("e.g., 'begin,end' or 'div'")
                ed_scope_val.textChanged.connect(self._schedule_live_refresh)
                
                # Checkboxes for matching options
                chk_case = QCheckBox()
                chk_case.setChecked(True)  # Default: case sensitive
                chk_case.setToolTip("Case sensitive")
                chk_case.stateChanged.connect(self._schedule_live_refresh)
                chk_word = QCheckBox()
                chk_word.setToolTip("Match whole word")
                chk_word.stateChanged.connect(self._schedule_live_refresh)
                chk_regex = QCheckBox()
                chk_regex.setToolTip("Use regular expression")
                chk_regex.stateChanged.connect(self._schedule_live_refresh)
                
                g3.addWidget(cb_field, row_i, 0)
                g3.addWidget(cb_op, row_i, 1)
                g3.addWidget(ed_val, row_i, 2)
                g3.addWidget(cb_scope, row_i, 3)
                g3.addWidget(ed_scope_val, row_i, 4)
                g3.addWidget(chk_case, row_i, 5)
                g3.addWidget(chk_word, row_i, 6)
                g3.addWidget(chk_regex, row_i, 7)
                self.cond_list.append((cb_field, cb_op, ed_val, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex))
            layout.addWidget(gb3, 9, 0, 1, 5)
            
            self.btn_apply = QPushButton("Apply to files")
            self.btn_apply.setToolTip("Execute insertion operation on all matching files")
            layout.addWidget(self.btn_apply, 10, 4)

            # Results on the right
            self.results = ResultsTree()
            
            # Results panel with save button
            results_layout = QVBoxLayout()
            results_header = QHBoxLayout()
            results_label = QLabel("Match Results")
            results_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            self.btn_save_results = QPushButton("💾 Save Results")
            self.btn_save_results.setToolTip("Save all match results to a text file")
            self.btn_save_results.clicked.connect(self._save_results)
            results_header.addWidget(results_label)
            results_header.addStretch()
            results_header.addWidget(self.btn_save_results)
            results_layout.addLayout(results_header)
            results_layout.addWidget(self.results)
            
            # Status bar at bottom showing position info (v2.5.1)
            self.results_status = QLabel("")
            self.results_status.setStyleSheet("padding: 4px; background-color: #f0f0f0; color: #333; font-size: 10pt;")
            self.results_status.setMinimumHeight(25)
            results_layout.addWidget(self.results_status)
            
            # Connect status label to results tree
            self.results.set_status_label(self.results_status)
            
            results_widget = QWidget()
            results_widget.setLayout(results_layout)
            
            splitter = QSplitter()
            left = QWidget(); left.setLayout(layout)
            splitter.addWidget(left)
            splitter.addWidget(results_widget)
            splitter.setSizes([500, 800])

            wroot = QVBoxLayout(self)
            wroot.setContentsMargins(0, 0, 0, 0)
            wroot.addWidget(splitter)
            
            self.is_file.stateChanged.connect(self.change_advanced_conditions)
            self.btn_browse.clicked.connect(self._browse)
            self.btn_apply.clicked.connect(self._apply)

        def change_advanced_conditions(self):
            self.enable_buttons(not self.is_file.isChecked(), include_buttons = False)

        def _browse(self):
            if self.is_file.isChecked():
                path, _ = QFileDialog.getOpenFileName(self, "Select dictionary", "", "JSON/TS (*.json *.ts *.tsx *.js *.jsx);;All (*)")
                #self.enable_buttons(False, include_buttons = False)
            else:
                path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
                #self.enable_buttons(True, include_buttons = False)
            
            if path:
                self.ed_path.setText(path)

        # def _files(self) -> List[str]: # version 1
        #     path = self.ed_path.text().strip()
        #     inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
        #     exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
        #     files = walk_files(path, inc, exc)
        #     return list(files)
        
        def _conds(self) -> tuple[List[Condition], str]:
            """Return conditions and logic operator (AND/OR)"""
            out: List[Condition] = []
            if not self.is_file.isChecked():
                for cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex in self.cond_list:
                    f = cb_field.currentText().strip()
                    o = cb_op.currentText().strip()
                    v = ed.text().strip()
                    scope_type = cb_scope.currentText().strip()
                    scope_val = ed_scope_val.text().strip()
                    case_sensitive = chk_case.isChecked()
                    whole_word = chk_word.isChecked()
                    use_regex = chk_regex.isChecked()
                    if f and o and v:
                        out.append(Condition(f, o, v, scope_type, scope_val, case_sensitive, whole_word, use_regex))
            logic_op = self.combo_logic_op.currentText()
            return out, logic_op
        
        def enable_buttons(self,state, include_buttons=True, include_advanced_conditions = True):
            if include_buttons:
                self.btn_browse.setEnabled(state)
                
            if include_advanced_conditions:
                for cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex in self.cond_list:
                    cb_field.setEnabled(state)
                    cb_op.setEnabled(state)
                    ed.setEnabled(state)
                    ed.setReadOnly(not state)
                    cb_scope.setEnabled(state)
                    ed_scope_val.setEnabled(state)
                    ed_scope_val.setReadOnly(not state)
                    chk_case.setEnabled(state)
                    chk_word.setEnabled(state)
                    chk_regex.setEnabled(state)
            
        def reset_advanced_conditions(self):
            for cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex in self.cond_list:
                cb_field.clear()
                cb_op.setCurrentIndex(0)
                ed.setCurrentIndex(0)
                cb_scope.setCurrentIndex(0)
                ed_scope_val.clear()
                chk_case.setChecked(True)
                chk_word.setChecked(False)
                chk_regex.setChecked(False)
        
        def _iter_files(self) -> List[str]:
            path = self.ed_path.text().strip()
            
            # v2.9.0, v2.9.1: Handle extension filter (optional)
            use_ext_filter = self.chk_use_ext_filter.isChecked()
            extensions_text = self.ed_extensions.text().strip() if use_ext_filter else ""
            ed_inc_text = self.ed_inc.text().strip()
            
            # Build include globs from extensions if enabled and provided
            if use_ext_filter and extensions_text:
                extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
                extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
                ext_globs = [f"*{ext}" for ext in extensions]
                
                if ed_inc_text:
                    inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
                    inc.extend(ext_globs)
                else:
                    inc = ext_globs
            else:
                if ed_inc_text:
                    inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
                else:
                    inc = ["*.*"]
                
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            return filter_files_by_conditions(files, self._conds())

        def _schedule_live_refresh(self):
            if not self._conds():  # only trigger if there's at least 1 valid rule
                return
            # Only do live preview when path is a directory:
            p = self.ed_path.text().strip()
            if not p or os.path.isfile(p):
                return
            self._debounce_timer.start()
        
        def _start_search_threaded(self):
            if not self.processing_search:
                words = "|".join([ed.text().strip() for k, n, ed in self.cond_list if ed.text().strip()])
                if words:
                    self.results.print_message("Loading...")
                    
                    try:
                        pattern_text = SearchOptions(False, False, True).compile(rf"(?:{words})")
                    except Exception as e:
                        self.error.emit(f"Invalid pattern: {e}")
                        self.done.emit({})
                        return
                    
                    # Create progress bar (v2.5.0)
                    if self.progress_manager:
                        import uuid
                        self._current_task_id = f"insert_search_{uuid.uuid4().hex[:8]}"
                        self._current_progress_widget = self.progress_manager.add_task(
                            self._current_task_id,
                            f"Match Search: {words[:30]}"
                        )
                    
                    # Create thread and worker
                    self._search_thread = QThread(self)
                    self._search_worker = SearchWorker(
                        pattern_text=pattern_text,
                        iter_files_fn=self._iter_files,
                        search_options_factory=lambda a,b,c: SearchOptions(a,b,c)
                    )
                    self._search_worker.moveToThread(self._search_thread)

                    # Connections
                    self._search_thread.started.connect(self._search_worker.run)
                    self._search_worker.done.connect(self._on_search_done)
                    self._search_worker.progress.connect(self._on_search_progress)
                    self._search_worker.progress_detailed.connect(self._on_search_progress_detailed)  # v2.5.0
                    self._search_worker.error.connect(self._on_search_error)

                    # Connect cancel and pause from progress bar to worker (v2.5.0+)
                    if self._current_progress_widget:
                        self._current_progress_widget.cancel_requested.connect(
                            lambda _: self._search_worker.cancel()
                        )
                        self._current_progress_widget.pause_requested.connect(
                            lambda _, paused: self._search_worker.pause() if paused else self._search_worker.resume()
                        )

                    # Cleanup
                    self._search_worker.done.connect(self._search_thread.quit)
                    self._search_worker.done.connect(self._search_worker.deleteLater)
                    self._search_thread.finished.connect(self._search_thread.deleteLater)

                    self._search_thread.start()
                    self.enable_buttons(False)
                    self.processing_search = True
            else:
                self._search_worker.cancel()
                self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
                self.processing_search = False

        def _on_search_progress(self, current_path: str):
            """Legacy progress handler."""
            pass

        def _on_search_progress_detailed(self, current: int, total: int, message: str):
            """New detailed progress handler (v2.5.0)."""
            if self._current_progress_widget:
                self._current_progress_widget.update_progress(current, total, message)
                self._current_progress_widget.add_log(f"Processing: {message}")

        def _on_search_error(self, msg: str):
            """Handle search errors."""
            if self._current_progress_widget:
                self._current_progress_widget.add_log(f"ERROR: {msg}")
            print(msg)

        def _on_search_done(self, matches: dict):
            """Handle search completion with history tracking (v2.5.0+)."""
            self.results.populate(matches)
            self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
            self.processing_search = False
            
            # Mark progress as complete (v2.5.0)
            if self._current_progress_widget:
                self._current_progress_widget.set_complete(success=True)
                self._current_progress_widget.add_log(f"Search completed: {len(matches)} files with matches")
            
            # Save to history (NEW - v2.5.0+)
            try:
                history = OperationHistory()
                history.add_operation("insert_search", {
                    "path": self.ed_path.text(),
                    "files_matched": len(matches),
                    "total_matches": sum(len(items) for items in matches.values())
                })
            except Exception as e:
                print(f"Failed to save history: {e}")
        
        # def _do_search(self):
        #     try:
        #         patt = SearchOptions(False,
        #                              False,
        #                              False).compile(self.ed_text.toPlainText())
        #     except ValueError as e:
        #         QMessageBox.critical(self, "Invalid pattern", str(e)); return
            
        #     matches: Dict[str, List[Tuple[int,int,str]]] = {}
        #     for p in self._iter_files():
        #         print(f"TESTE {p}")
        #         try:
        #             text = read_text(p)
        #             lst: List[Tuple[int,int,str]] = []
        #             for m in patt.finditer(text):
        #                 line = text.count("\n", 0, m.start()) + 1
        #                 col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
        #                 snippet = text.splitlines()[line-1]
        #                 lst.append((line, col, snippet))
        #             if lst:
        #                 matches[p] = lst
        #         except Exception as e:
        #             print(f"[WARN] {p}: {e}", file=sys.stderr)
        #     self.results.populate(matches)
        
        def _files(self) -> List[str]:
            path = self.ed_path.text().strip()
            inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            return filter_files_by_conditions(files, self._conds())
        
        def _find_line_by_query(self, text: str, query: str) -> List[int]:
            """
            Find line numbers matching the query.
            Returns list of 1-based line numbers.
            """
            if not query:
                return []
            
            case_sensitive = self.chk_lookup_case.isChecked()
            whole_word = self.chk_lookup_word.isChecked()
            use_regex = self.chk_lookup_regex.isChecked()
            
            lines = text.splitlines()
            matches = []
            
            for i, line in enumerate(lines, start=1):
                if self._line_matches_query(line, query, case_sensitive, whole_word, use_regex):
                    matches.append(i)
            
            return matches
        
        def _line_matches_query(self, line: str, query: str, case_sensitive: bool, 
                                 whole_word: bool, use_regex: bool) -> bool:
            """
            Check if a line matches the query with given options.
            """
            try:
                if use_regex:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    pattern = query
                    if whole_word:
                        pattern = r'\b' + pattern + r'\b'
                    return bool(re.search(pattern, line, flags))
                else:
                    search_line = line if case_sensitive else line.lower()
                    search_query = query if case_sensitive else query.lower()
                    
                    if whole_word:
                        pattern = r'\b' + re.escape(search_query) + r'\b'
                        flags = 0 if case_sensitive else re.IGNORECASE
                        return bool(re.search(pattern, line, flags))
                    else:
                        return search_query in search_line
            except re.error:
                return False

        def _apply(self):
            query = self.ed_query.text().strip()
            manual_line = self.spin_line.value()
            insert_text = self.ed_text.toPlainText()
            mode = self.cb_mode.currentText()
            occurrence = self.cb_lookup_occurrence.currentText()
            
            count = 0
            skipped = 0
            
            for p in self._files():
                try:
                    old = read_text(p)
                    
                    # Determine line number(s) to use
                    if query:
                        # Use lookup/search mode
                        line_matches = self._find_line_by_query(old, query)
                        
                        if not line_matches:
                            skipped += 1
                            continue
                        
                        # Determine which occurrence to use
                        if occurrence == "First":
                            target_lines = [line_matches[0]]
                        elif occurrence == "Last":
                            target_lines = [line_matches[-1]]
                        else:  # "All"
                            target_lines = line_matches
                    else:
                        # Use manual line number
                        target_lines = [manual_line]
                    
                    # Apply insertion to each target line
                    new = old
                    # When applying to multiple lines, process from bottom to top
                    # to avoid line number shifts
                    for line in sorted(target_lines, reverse=True):
                        new = insert_at_line(new, line, insert_text, mode)
                    
                    if new != old:
                        write_text(p, new)
                        count += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
                    skipped += 1
            
            msg = f"Modified files: {count}"
            if skipped > 0:
                msg += f"\nSkipped files (no match): {skipped}"
            if query:
                msg += f"\n\nUsed search query: '{query}'"
                msg += f"\nOccurrence mode: {occurrence}"
            else:
                msg += f"\n\nUsed line number: {manual_line}"
            
            QMessageBox.information(self, "Insert", msg)
            self._start_search_threaded()
        
        def _save_results(self):
            """Save match results to a text file."""
            matches_data = self.results.get_matches_data()
            
            if not matches_data:
                QMessageBox.information(self, "No Results", 
                    "No match results to save. Advanced conditions must be set to see preview results.")
                return
            
            # Ask user for file location
            default_filename = "clarify_insert_matches.txt"
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Match Results", 
                default_filename,
                "Text Files (*.txt);;All Files (*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            try:
                # Export matches to text
                text_content = self.results.export_to_text()
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                total_files = len(matches_data)
                total_matches = sum(len(items) for items in matches_data.values())
                
                QMessageBox.information(self, "Results Saved", 
                    f"Match results saved successfully!\n\n"
                    f"File: {file_path}\n"
                    f"Total files: {total_files}\n"
                    f"Total matches: {total_matches}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                    f"Failed to save results:\n{str(e)}")

    # class InsertPanel(QWidget):
    #     """
    #     Insert functionality + live match panel (same component as Search/Replace).
    #     Live updates when:
    #     - Path is a directory; and
    #     - At least one Advanced Options row has a non-empty 'Value' (or Field).
    #     - Triggers on editingFinished/toggles for the controls.
    #     """
    #     def __init__(self, parent=None):
    #         super().__init__(parent)
    #         self._build_ui()
    #         self._wire()
    #         self._matches: List[str] = []

    #     def _build_ui(self):
    #         layout = QVBoxLayout(self)

    #         # Path and line controls
    #         r1 = QHBoxLayout()
    #         self.ed_path = QLineEdit()
    #         self.btn_browse = QPushButton("Browse…")
    #         r1.addWidget(QLabel("Path:"))
    #         r1.addWidget(self.ed_path, 1)
    #         r1.addWidget(self.btn_browse)
    #         layout.addLayout(r1)

    #         r2 = QHBoxLayout()
    #         self.spin_line = QSpinBox(); self.spin_line.setRange(1, 10_000_000); self.spin_line.setValue(1)
    #         self.ed_text = QLineEdit()
    #         r2.addWidget(QLabel("Line #:"))
    #         r2.addWidget(self.spin_line)
    #         r2.addWidget(QLabel("Text:"))
    #         r2.addWidget(self.ed_text, 1)
    #         layout.addLayout(r2)

    #         # Insert modes
    #         r3 = QHBoxLayout()
    #         self.cmb_mode = QComboBox()
    #         self.cmb_mode.addItems([
    #             "Insert left of line",
    #             "Insert right of line",
    #             "Push line down and insert",
    #             "Insert on next line (push rest)",
    #             "Replace line content"
    #         ])
    #         self.btn_apply = QPushButton("Apply")
    #         r3.addWidget(QLabel("Mode:"))
    #         r3.addWidget(self.cmb_mode, 1)
    #         r3.addStretch(1)
    #         r3.addWidget(self.btn_apply)
    #         layout.addLayout(r3)

    #         # Advanced Options
    #         adv = QGroupBox("Advanced Options (folder mode)")
    #         adv_lay = QFormLayout(adv)
    #         self.adv_field1 = QLineEdit(); self.adv_op1 = QComboBox(); self.adv_val1 = QLineEdit()
    #         self.adv_op1.addItems(["contains", "contained-in", "equals", "not-equals"])
    #         adv_lay.addRow("Field #1 / Op / Value:", self._row3(self.adv_field1, self.adv_op1, self.adv_val1))
    #         self.adv_field2 = QLineEdit(); self.adv_op2 = QComboBox(); self.adv_val2 = QLineEdit()
    #         self.adv_op2.addItems(["contains", "contained-in", "equals", "not-equals"])
    #         adv_lay.addRow("Field #2 / Op / Value:", self._row3(self.adv_field2, self.adv_op2, self.adv_val2))
    #         layout.addWidget(adv)

    #         # Include/Exclude (so we mirror Search)
    #         f_row = QHBoxLayout()
    #         self.ed_includes = QLineEdit()
    #         self.ed_excludes = QLineEdit()
    #         f_row.addWidget(QLabel("Include globs (comma):"))
    #         f_row.addWidget(self.ed_includes, 1)
    #         f_row.addWidget(QLabel("Exclude globs (comma):"))
    #         f_row.addWidget(self.ed_excludes, 1)
    #         layout.addLayout(f_row)

    #         # Splitter: same Match panel + preview
    #         spl = QSplitter(Qt.Vertical)
    #         self.match_panel = MatchPanel()
    #         self.preview = QPlainTextEdit()
    #         self.preview.setReadOnly(True)
    #         spl.addWidget(self.match_panel)
    #         spl.addWidget(self.preview)
    #         spl.setSizes([280, 240])
    #         layout.addWidget(spl, 1)

    #     def _row3(self, a: QWidget, b: QWidget, c: QWidget) -> QWidget:
    #         w = QWidget()
    #         h = QHBoxLayout(w)
    #         h.setContentsMargins(0,0,0,0)
    #         h.addWidget(a, 1); h.addWidget(b); h.addWidget(c, 1)
    #         return w

    #     def _wire(self):
    #         self.btn_browse.clicked.connect(self._browse)
    #         self.btn_apply.clicked.connect(self._apply)
    #         self.match_panel.btn_refresh.clicked.connect(self._live_refresh)
    #         self.match_panel.view.clicked.connect(self._on_select_match)

    #         # Live refresh on advanced options end-edit; also on include/exclude edits.
    #         for w in [self.adv_field1, self.adv_val1, self.adv_field2, self.adv_val2,
    #                 self.ed_includes, self.ed_excludes]:
    #             w.editingFinished.connect(self._live_refresh)
    #         self.adv_op1.currentIndexChanged.connect(self._live_refresh)
    #         self.adv_op2.currentIndexChanged.connect(self._live_refresh)
    #         self.ed_path.editingFinished.connect(self._live_refresh)

    #     def _browse(self):
    #         path = QFileDialog.getExistingDirectory(self, "Select folder (folder mode)")
    #         if path:
    #             self.ed_path.setText(path)
    #             self._live_refresh()

    #     def _parse_globs(self, text: str) -> List[str]:
    #         return [s.strip() for s in text.split(",") if s.strip()]

    #     def _has_any_advanced_value(self) -> bool:
    #         return any([
    #             self.adv_field1.text().strip(), self.adv_val1.text().strip(),
    #             self.adv_field2.text().strip(), self.adv_val2.text().strip()
    #         ])

    #     def _advanced_ok(self, file_path: str, text: str) -> bool:
    #         def eval_line(field: str, op: str, val: str) -> bool:
    #             if not field and not val:
    #                 return True
    #             hay_fn = os.path.basename(file_path)
    #             hay_ct = text
    #             needle = val
    #             def contains(h, n): return (n in h)
    #             def contained_in(h, n): return (h in n)
    #             def equals(h, n): return (h == n)
    #             def not_equals(h, n): return (h != n)
    #             ops = {
    #                 "contains": contains,
    #                 "contained-in": contained_in,
    #                 "equals": equals,
    #                 "not-equals": not_equals
    #             }
    #             fun = ops.get(op, contains)
    #             target = hay_ct if field.lower() in ("content","text","body") else hay_fn
    #             return fun(target, needle)

    #         ok1 = eval_line(self.adv_field1.text().strip(), self.adv_op1.currentText(), self.adv_val1.text().strip())
    #         ok2 = eval_line(self.adv_field2.text().strip(), self.adv_op2.currentText(), self.adv_val2.text().strip())
    #         return ok1 and ok2

    #     def _live_refresh(self):
    #         root = self.ed_path.text().strip()
    #         if not (root and os.path.isdir(root)):
    #             self.match_panel.set_results(root, [])
    #             self.preview.clear()
    #             return
    #         # Only refresh if there's at least one advanced value filled
    #         if not self._has_any_advanced_value():
    #             self.match_panel.set_results(root, [])
    #             self.preview.clear()
    #             return
    #         inc = self._parse_globs(self.ed_includes.text())
    #         exc = self._parse_globs(self.ed_excludes.text())
    #         found: List[str] = []
    #         for f in build_file_list(root, inc, exc):
    #             try:
    #                 with open(f, "r", encoding="utf-8", errors="replace") as fh:
    #                     txt = fh.read()
    #                 if self._advanced_ok(f, txt):
    #                     found.append(f)
    #             except Exception:
    #                 pass
    #         self._matches = found
    #         self.match_panel.set_results(root, found)
    #         self.preview.clear()

    #     def _on_select_match(self):
    #         path = self.match_panel.selected_path()
    #         if not path:
    #             self.preview.clear()
    #             return
    #         try:
    #             with open(path, "r", encoding="utf-8", errors="replace") as fh:
    #                 self.preview.setPlainText(fh.read())
    #         except Exception as e:
    #             self.preview.setPlainText(f"<<Error reading {path}: {e}>>")

    #     def _apply(self):
    #         root = self.ed_path.text().strip()
    #         if not root:
    #             QMessageBox.warning(self, "Insert", "Path is required.")
    #             return
    #         text = self.ed_text.text()
    #         line_no = self.spin_line.value()
    #         mode = self.cmb_mode.currentText()

    #         targets: List[str] = []
    #         if os.path.isfile(root):
    #             targets = [root]
    #         elif os.path.isdir(root):
    #             # Use current matches if any; otherwise, all files
    #             targets = self._matches[:] if self._matches else build_file_list(root, [], [])

    #         changed = 0
    #         for f in targets:
    #             try:
    #                 with open(f, "r", encoding="utf-8", errors="replace") as fh:
    #                     lines = fh.read().splitlines()
    #                 idx = max(0, min(line_no-1, len(lines)))
    #                 if mode.startswith("Insert left"):
    #                     if idx < len(lines):
    #                         lines[idx] = text + lines[idx]
    #                     else:
    #                         while len(lines) < idx:
    #                             lines.append("")
    #                         lines.append(text)
    #                 elif mode.startswith("Insert right"):
    #                     if idx < len(lines):
    #                         lines[idx] = lines[idx] + text
    #                     else:
    #                         while len(lines) < idx:
    #                             lines.append("")
    #                         lines.append(text)
    #                 elif mode.startswith("Push line down and insert"):
    #                     while len(lines) < idx:
    #                         lines.append("")
    #                     # insert text at idx, push old content down
    #                     if idx < len(lines):
    #                         lines.insert(idx, text)
    #                     else:
    #                         lines.append(text)
    #                 elif mode.startswith("Insert on next line"):
    #                     while len(lines) < idx:
    #                         lines.append("")
    #                     if idx < len(lines):
    #                         lines.insert(idx+1, text)
    #                     else:
    #                         lines.append(text)
    #                 else:
    #                     # Replace line content
    #                     while len(lines) < idx:
    #                         lines.append("")
    #                     if idx < len(lines):
    #                         lines[idx] = text
    #                     else:
    #                         lines.append(text)

    #                 with open(f, "w", encoding="utf-8") as fw:
    #                     fw.write("\n".join(lines) + "\n")
    #                 changed += 1
    #             except Exception:
    #                 pass
    #         QMessageBox.information(self, "Insert", f"Files modified: {changed}")
    #         self._live_refresh()

    
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
            self.setWindowTitle("Clarify - JSON file management system")
            #self.resize(1080, 720)

            # Initialize settings manager
            from .settings_manager import get_settings
            self.settings = get_settings()

            # Plugin loader
            from .plugin_loader import PluginLoader
            self.plugin_loader = PluginLoader(self)
            self.plugin_loader.discover_plugins()
            self.plugin_loader.activate_plugins()

            # REST API (opcional)
            try:
                from .rest_api import ClarifyAPI
                self.rest_api = ClarifyAPI(self)
                self.rest_api.start()
            except Exception as e:
                print(f"[REST API] Não inicializada: {e}")

            # Cloud sync (opcional)
            try:
                from .cloud_sync import DummyProvider
                self.cloud_sync = DummyProvider()
                self.cloud_sync.login()
            except Exception as e:
                print(f"[Cloud Sync] Não inicializado: {e}")

            self._build_icon()
            self._build_ui()
            self._build_menu()
            self._setup_shortcuts()
            self._restore_prefs()
            self._apply_saved_settings()

            # Nice monospaced font for preview-ish widgets
            try:
                f = QFontDatabase.systemFont(QFontDatabase.FixedFont)
                self.search_panel.ed_repl.setFont(f)
                self.search_panel.ed_query.setFont(f)
                self.insert_panel.ed_text.setFont(f)
            except Exception:
                pass
        
        def _build_icon(self):
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
            self.dock_translate = JsonTranslateDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_translate)
            self.dock_translate.hide()
            # dock.show()

        def _open_rewrite(self):
            self.dock_rewriter = JsonRewriterDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_rewriter)
            self.dock_rewriter.hide()
            #dock.show()

        def _open_text_extractor(self):
            self.dock_text_extractor = TextExtractorDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_text_extractor)
            self.dock_text_extractor.hide()
        
        def _open_placeholder_replacer(self):
            self.dock_placeholder_replacer = PlaceholderReplacerDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_placeholder_replacer)
            self.dock_placeholder_replacer.hide()
        
        def _open_ai_processor(self):
            self.dock_ai_processor = AIProcessorDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_ai_processor)
            self.dock_ai_processor.hide()

        def _open_json_search(self):
            self.dock_json_search = JsonSearchDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_json_search)
            self.dock_json_search.hide()

        def _open_case_converter(self):
            self.dock_case_converter = CaseConverterDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_case_converter)
            self.dock_case_converter.hide()

        def _build_menu(self):
            bar = self.menuBar()

            m_file = bar.addMenu("File")
            act_exit = QAction("Exit", self)
            act_exit.triggered.connect(self.close)
            m_file.addAction(act_exit)

            m_tools = bar.addMenu("Tools")
            self.act_open_translate = QAction("Open JSON Translate", self)
            self.act_open_rewriter = QAction("Open JSON Rewriter", self)
            self.act_open_text_extractor = QAction("Open Text Extractor", self)
            self.act_open_placeholder_replacer = QAction("Open Placeholder Replacer", self)
            self.act_open_ai_processor = QAction("Open AI File Processor", self)
            self.act_open_json_search = QAction("Open JSON Search", self)
            self.act_open_case_converter = QAction("Open Case Converter", self)
            m_tools.addAction(self.act_open_translate)
            m_tools.addAction(self.act_open_rewriter)
            m_tools.addAction(self.act_open_text_extractor)
            m_tools.addAction(self.act_open_placeholder_replacer)
            m_tools.addAction(self.act_open_ai_processor)
            m_tools.addAction(self.act_open_json_search)
            m_tools.addAction(self.act_open_case_converter)

            self.act_open_translate.triggered.connect(lambda: self.dock_translate.show())
            self.act_open_rewriter.triggered.connect(lambda: self.dock_rewriter.show())
            self.act_open_text_extractor.triggered.connect(lambda: self.dock_text_extractor.show())
            self.act_open_placeholder_replacer.triggered.connect(lambda: self.dock_placeholder_replacer.show())
            self.act_open_ai_processor.triggered.connect(lambda: self.dock_ai_processor.show())
            self.act_open_json_search.triggered.connect(lambda: self.dock_json_search.show())
            self.act_open_case_converter.triggered.connect(lambda: self.dock_case_converter.show())

            m_themes = bar.addMenu("Themes")
            self.act_theme_system = QAction("System", self, checkable=True)
            self.act_theme_light = QAction("Light", self, checkable=True)
            self.act_theme_dark = QAction("Dark", self, checkable=True)
            grp = [self.act_theme_system, self.act_theme_light, self.act_theme_dark]
            for a in grp:
                m_themes.addAction(a)
                a.triggered.connect(lambda _, x=a: self._apply_theme_action(x))
            self.act_theme_system.setChecked(True)

            m_settings = bar.addMenu("Settings")
            act_preferences = QAction("Preferences...", self)
            act_shortcuts = QAction("Keyboard Shortcuts...", self)
            act_clear_recent = QAction("Clear Recent Files", self)
            m_settings.addAction(act_preferences)
            m_settings.addAction(act_shortcuts)
            m_settings.addSeparator()
            m_settings.addAction(act_clear_recent)
            act_preferences.triggered.connect(self._show_preferences)
            act_shortcuts.triggered.connect(self._show_shortcuts)
            act_clear_recent.triggered.connect(self._clear_recent_files)
            

            # Plugins menu
            m_plugins = bar.addMenu("Plugins")
            for plugin in getattr(self, "plugin_loader", []).plugins:
                act = QAction(f"{plugin.name}", self)
                act.setToolTip(plugin.description)
                act.triggered.connect(lambda _, p=plugin: p.activate(self))
                m_plugins.addAction(act)

            m_about = bar.addMenu("About")
            act_about = QAction("About Clarify", self)
            m_about.addAction(act_about)
            act_about.triggered.connect(self._about_dialog)

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

        def _about_dialog(self):
            QMessageBox.information(self, "About",
                                    "Clarify\n\nJSON file management system\nPurpose: search, replace, insert and JSON utilities.\n"
                                    "Author: Josué Amaral\nVersion: 1.1.0 (2025)")
        
        def _setup_shortcuts(self):
            """Setup keyboard shortcuts."""
            from .shortcut_manager import ShortcutManager
            from PySide6.QtGui import QShortcut
            
            # Exit shortcut
            shortcut_exit = QShortcut(ShortcutManager.get_key_sequence("exit"), self)
            shortcut_exit.activated.connect(self.close)
            
            # Help shortcut
            shortcut_help = QShortcut(ShortcutManager.get_key_sequence("help"), self)
            shortcut_help.activated.connect(self._show_shortcuts)
            
            # About shortcut
            shortcut_about = QShortcut(ShortcutManager.get_key_sequence("about"), self)
            shortcut_about.activated.connect(self._about_dialog)
        
        def _apply_saved_settings(self):
            """Apply saved settings on startup."""
            # Apply saved theme
            theme_mode = self.settings.get("theme", "system")
            if theme_mode == "light":
                self.act_theme_light.setChecked(True)
                apply_theme(QApplication.instance(), "light")
            elif theme_mode == "dark":
                self.act_theme_dark.setChecked(True)
                apply_theme(QApplication.instance(), "dark")
            else:
                self.act_theme_system.setChecked(True)
                apply_theme(QApplication.instance(), "system")
        
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
            
            general_layout.addWidget(chk_tooltips)
            general_layout.addWidget(chk_confirm_exit)
            general_layout.addWidget(chk_auto_save)
            general_group.setLayout(general_layout)
            
            layout.addWidget(general_group)
            
            # Buttons
            from PySide6.QtWidgets import QDialogButtonBox
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(lambda: self._save_preferences(
                chk_tooltips.isChecked(),
                chk_confirm_exit.isChecked(),
                chk_auto_save.isChecked(),
                dialog
            ))
            buttons.rejected.connect(dialog.reject)
            
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            dialog.exec()
        
        def _save_preferences(self, tooltips, confirm_exit, auto_save, dialog):
            """Save preferences and close dialog."""
            self.settings.update_multiple({
                "show_tooltips": tooltips,
                "confirm_on_exit": confirm_exit,
                "auto_save": auto_save
            })
            dialog.accept()
            QMessageBox.information(self, "Success", "Preferences saved successfully!")
        
        def _show_shortcuts(self):
            """Show keyboard shortcuts dialog."""
            from .shortcut_manager import ShortcutManager
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Keyboard Shortcuts")
            dialog.setMinimumSize(600, 500)
            
            layout = QVBoxLayout()
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(ShortcutManager.format_shortcuts_table())
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            
            layout.addWidget(text_edit)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
        
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
        
        def closeEvent(self, event):
            """Handle window close event with thread cleanup (v2.7.0)."""
            # Check if there are any active threads
            active_threads = thread_manager.get_active_threads()
            has_active_threads = any(count > 0 for count in active_threads.values())
            
            if has_active_threads:
                # Warn user about active threads
                reply = QMessageBox.warning(
                    self,
                    "Active Processing",
                    "There are still active operations running:\n\n" + 
                    "\n".join([f"- {feature.value}: {count} active" 
                              for feature, count in active_threads.items() if count > 0]) +
                    "\n\nDo you want to cancel all operations and exit?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    event.ignore()
                    return
                
                # User confirmed, wait for threads to finish
                self.statusBar().showMessage("Canceling active operations...")
                if not thread_manager.wait_all_threads(timeout_ms=5000):
                    # Some threads didn't finish in time
                    reply = QMessageBox.critical(
                        self,
                        "Force Close",
                        "Some operations did not finish in time.\n\n"
                        "Force close application? (may cause data loss)",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.No:
                        event.ignore()
                        return
                    
                    # Force cleanup
                    thread_manager.force_cleanup()
            
            # Normal exit confirmation
            if self.settings.get("confirm_on_exit", True):
                reply = QMessageBox.question(
                    self,
                    "Exit Clarify",
                    "Are you sure you want to exit?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Save window geometry
                    self.settings.set("window_geometry", self.saveGeometry().toHex().data().decode())
                    event.accept()
                else:
                    event.ignore()
            else:
                # Save window geometry
                self.settings.set("window_geometry", self.saveGeometry().toHex().data().decode())
                event.accept()

        def _build_ui(self):
            # Main container widget with vertical layout
            main_container = QWidget()
            main_layout = QVBoxLayout(main_container)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Tabs (top area)
            self.tabs = QTabWidget()
            main_layout.addWidget(self.tabs)
            
            # Progress Manager (bottom area - v2.5.0)
            self.progress_manager = ProgressManager(self)
            main_layout.addWidget(self.progress_manager)
            
            # Set main container as central widget
            self.setCentralWidget(main_container)
            
            # Status bar (Sprint 8 - v1.1.0)
            self.statusbar = self.statusBar()
            self.statusbar.showMessage("Ready", 3000)

            # Create panels and pass progress_manager reference
            self.tab_search = SearchReplacePanel(progress_manager=self.progress_manager)
            self.tab_insert = InsertPanel(progress_manager=self.progress_manager)

            self.tabs.addTab(self.tab_search, "Search / Replace")
            self.tabs.addTab(self.tab_insert, "Insert")

            # Docks (Tools menu toggles them)
            self._open_trans()
            self._open_rewrite()
            self._open_text_extractor()
            self._open_placeholder_replacer()
            self._open_ai_processor()
            self._open_json_search()
            self._open_case_converter()
        
        def _restore_prefs(self):
            cfg = load_prefs()
            mode = cfg.get("THEME", "mode", fallback="system")
            if mode == "light":
                self.act_theme_light.setChecked(True)
            elif mode == "dark":
                self.act_theme_dark.setChecked(True)
            else:
                self.act_theme_system.setChecked(True)
            apply_theme(QApplication.instance(), mode)
            
        
# =============================================================================
#                                  ARGPARSE
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Search/Replace/Insert + JSON Translate/Dedupe — GUI or CLI"
    )
    sub = p.add_subparsers(dest="cmd")

    # GUI
    p.add_argument("--gui", action="store_true", help="Launch GUI (default if no cmd).")

    # search
    ps = sub.add_parser("search", help="Search in a file/folder")
    ps.add_argument("path", help="File or folder")
    ps.add_argument("query", help="Search string or regex")
    ps.add_argument("--case", action="store_true", help="Case sensitive")
    ps.add_argument("--word", action="store_true", help="Whole word")
    ps.add_argument("--regex", action="store_true", help="Interpret query as regex")
    ps.add_argument("--include", nargs="*", default=None, help="Include globs (*.ts *.tsx …)")
    ps.add_argument("--exclude", nargs="*", default=None, help="Exclude globs (node_modules …)")
    ps.add_argument("--cond", nargs="*", help="Advanced conditions like field:op:value "
                                                  "(field=filename|path|ext|size|mtime) (op like contains, equals, >, …)")
    ps.set_defaults(func=cli_search)

    # replace
    pr = sub.add_parser("replace", help="Replace text")
    pr.add_argument("path", help="File or folder")
    pr.add_argument("query", help="Search string or regex")
    pr.add_argument("replacement", help="Replacement text")
    pr.add_argument("--all", action="store_true", help="Replace all (default: first per file)")
    pr.add_argument("--preserve-case", action="store_true", help="Mimic match casing in replacement")
    pr.add_argument("--case", action="store_true")
    pr.add_argument("--word", action="store_true")
    pr.add_argument("--regex", action="store_true")
    pr.add_argument("--include", nargs="*", default=None)
    pr.add_argument("--exclude", nargs="*", default=None)
    pr.add_argument("--cond", nargs="*", help="Advanced conditions (field:op:value)")
    pr.add_argument("--dry-run", action="store_true")
    pr.set_defaults(func=cli_replace)

    # insert
    pi = sub.add_parser("insert", help="Insert text at a given line")
    pi.add_argument("path")
    pi.add_argument("line", type=int)
    pi.add_argument("text")
    pi.add_argument("--mode", choices=[InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE,
                                       InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW],
                    default=InsertMode.INSERT_BELOW)
    pi.add_argument("--include", nargs="*", default=None)
    pi.add_argument("--exclude", nargs="*", default=None)
    pi.add_argument("--cond", nargs="*", help="Advanced conditions (field:op:value)")
    pi.add_argument("--dry-run", action="store_true")
    pi.set_defaults(func=cli_insert)

    # translate
    pt = sub.add_parser("translate", help="Replace texts by keys from a JSON/TS dictionary")
    pt.add_argument("path")
    pt.add_argument("dictionary")
    pt.add_argument("--include", nargs="*", default=None)
    pt.add_argument("--exclude", nargs="*", default=None)
    pt.add_argument("--dry-run", action="store_true")
    pt.add_argument("--root", default="t", help="Root alias for placeholders (default: t)")
    pt.add_argument("--inverse", action="store_true", help="Inverse mode: {t.path} → text")
    pt.set_defaults(func=cli_translate)

    # dedupe
    pd = sub.add_parser("dedupe", help="JSON/TS rewriter (dedupe/join/eliminate)")
    pd.add_argument("input")
    pd.add_argument("-o", "--output")
    pd.add_argument("-i", "--indent", type=int, default=2)
    pd.add_argument("-f", "--from-ts", action="store_true", help="TS/JS mode preserving file")
    pd.add_argument("-t", "--ts-out", action="store_true", help="Emit export default { … };")
    pd.add_argument("-j", "--join-keys", action="store_true", help="Join identical keys")
    pd.add_argument("-e", "--eliminate-duplicates", action="store_true", help="Eliminate global duplicates")
    pd.add_argument("-b", "--no-line-break", action="store_true", help="Remove blank blanklines in output")
    pd.set_defaults(func=cli_dedupe)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    # If a subcommand is present, run as CLI-only.
    if argv and argv[0] in {"search","replace","insert","translate","dedupe"}:
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
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
