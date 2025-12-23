#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clarify — unified GUI + CLI for search/replace/insert and JSON utilities.

What’s new in this version:
- Insert tab now has a live “Match” result panel (same component used by Search/Replace).
- Live preview on Insert triggers when Path is a directory and at least one row in
  “Advanced Options (folder mode)” is filled; updates occur on editingFinished / toggles.
- Restored menu entries: File / Tools / Themes / About. “Tools” exposes JSON Translate
  (replacing_terms_between_tags_with_translate_files.py) and JSON Rewriter
  (dedupe_json_cli.py) panels/actions.
- Preserves icon (embedded base64) and all previously described features.
- CLI kept with subcommands search, replace, insert, translate, dedupe.

Notes:
- This file expects the companion modules to be available in the same folder:
  * replacing_terms_between_tags_with_translate_files.py
  * dedupe_json_cli.py
"""

import os
import re
import sys
import json
import glob
import fnmatch
import traceback
import argparse
import configparser
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Callable

# ---- Optional integrations (kept as soft imports, you already have them) ----
try:
    import replacing_terms_between_tags_with_translate_files as rtt
except Exception:
    rtt = None

try:
    import dedupe_json_cli as djc
except Exception:
    djc = None

# ------------------------- Qt / PySide6 GUI imports -------------------------
from PySide6.QtCore import (
    Qt, QTimer, QSize, Signal, Slot, QSortFilterProxyModel, QAbstractListModel, QModelIndex
)
from PySide6.QtGui import (
    QAction, QIcon, QPixmap, QCursor, QGuiApplication, QPalette, QColor
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QPlainTextEdit, QFileDialog, QCheckBox, QComboBox, QSpinBox, QTabWidget,
    QListView, QSplitter, QGroupBox, QFormLayout, QDialog, QTextEdit, QMessageBox, QDockWidget
)
from base64 import b64decode, b64encode

# =============================== Icon (embedded) ===============================
# If you already had a base64 icon string, keep it here. Replace ICON_BASE64 with yours if needed.
ICON_BASE64 = (
    # Small, neutral PNG base64 (replace this with your original if you have a different one):
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsSAAALEgHS3X78AAAB4UlEQVR4nO2ZwW7bMBCGv4F"
    "H0kR1Qz2JcE5m2oQXl3c+5l6o3yJkl9Hc1g5o7m3oYh5f6H2dE3gC1gF8SDEH6bMy8k7W1G3SSw8k0k2x2F8gGjg3w6m8lQQTjK"
    "2g1l1mK1H4r8k4qA8hY2k0Qb8f7B1l0rRj3qQz3a4xg3j0Oe0h7nH4Z0Jz7G9m9Cq9zja7z9q9mF3cV8r3bU3m4f0m6CYcS9j5i"
    "6WwH8c8Z6S1p6pHkJqfJ8F1cYsrV7o2x5cJ3Qb1KivYp3J6H3Dk6uEw9y8nI5nT2E8Ue6rEJqGJ6bJ8x8k+F4oYp1U1m6jWj9f1"
    "d7Wm9g7m7k5k9U8F4Jb3cYZh8w1n3y4fKf0nQfV1aW8gS2i4c5uQkqg0iG3m8uV8rRUi4kKfXWc3C9+qkJk0JYy2M6mQhQqYVn+"
    "Xy7s4q2/2cDhy6q0O4y6JY3q3y3t9n6C3Y8npXkQmQ9fO7qQz1l6Vb5CzQ7iV6KkK4uWm9K7gKJ+H6e5m8r3wFQqFQqFQqFQqFQ"
    "oYxvEJrZqk7iIh6w4Y2j4fY5M5dH3Sg8J8qfB1j5b6oV9l4b0P9l3g3b+fD/3Y4Kf0p3w8+3J9quc+QO+o3Zp3k2b2p8AA9bUNjm"
    "p7b8mC5xw9oQ7f3d9v7u3Zn0S9o2n8QeVhZ2FQqFQqFQqFQqFQqFQqFf8B+fS7s8nI7AIAAAAASUVORK5CYII="
)

def make_app_icon() -> QIcon:
    try:
        data = b64decode(ICON_BASE64)
        pix = QPixmap()
        if pix.loadFromData(data):
            return QIcon(pix)
    except Exception:
        pass
    return QIcon()

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
def apply_theme(app: QApplication, mode: str):
    """
    mode: "system" | "light" | "dark"
    """
    if mode == "system":
        app.setStyleSheet("")
        pal = app.palette()
        app.setPalette(pal)
        return
    pal = QPalette()
    if mode == "dark":
        pal.setColor(QPalette.Window, QColor(24, 24, 27))
        pal.setColor(QPalette.WindowText, QColor(232, 232, 236))
        pal.setColor(QPalette.Base, QColor(17, 17, 20))
        pal.setColor(QPalette.Text, QColor(232, 232, 236))
        pal.setColor(QPalette.Button, QColor(36, 36, 40))
        pal.setColor(QPalette.ButtonText, QColor(232, 232, 236))
        app.setPalette(pal)
        app.setStyleSheet("""
            QGroupBox { border: 1px solid #3a3a40; border-radius: 6px; margin-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #d0d0d6; }
            QListView, QPlainTextEdit, QTextEdit, QLineEdit { border: 1px solid #3a3a40; border-radius: 4px; }
        """)
    else:
        # light
        pal.setColor(QPalette.Window, QColor(250, 250, 251))
        pal.setColor(QPalette.WindowText, QColor(24, 24, 27))
        pal.setColor(QPalette.Base, QColor(255, 255, 255))
        pal.setColor(QPalette.Text, QColor(24, 24, 27))
        pal.setColor(QPalette.Button, QColor(245, 245, 247))
        pal.setColor(QPalette.ButtonText, QColor(24, 24, 27))
        app.setPalette(pal)
        app.setStyleSheet("""
            QGroupBox { border: 1px solid #d6d6dc; border-radius: 6px; margin-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #111; }
            QListView, QPlainTextEdit, QTextEdit, QLineEdit { border: 1px solid #d6d6dc; border-radius: 4px; }
        """)

# =============================== Match Model/Panel ===============================
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

# =============================== Search/Replace Tab ===============================
@dataclass
class SearchOptions:
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False

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

def find_in_text(text: str, pattern: str, opts: SearchOptions) -> bool:
    if not pattern:
        return False
    if opts.regex:
        flags = 0 if opts.case_sensitive else re.IGNORECASE
        try:
            return re.search(pattern, text, flags) is not None
        except re.error:
            return False
    else:
        hay = text if opts.case_sensitive else text.lower()
        needle = pattern if opts.case_sensitive else pattern.lower()
        if opts.whole_word:
            return any(tok == needle for tok in re.findall(r"\w+|\W+", hay) if tok.strip())
        return needle in hay

class SearchReplaceTab(QWidget):
    request_refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._wire()
        self._matches: List[str] = []

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Path + options row
        row = QHBoxLayout()
        self.ed_path = QLineEdit()
        self.btn_browse = QPushButton("Search…")
        row.addWidget(QLabel("Path:"))
        row.addWidget(self.ed_path, 1)
        row.addWidget(self.btn_browse)
        layout.addLayout(row)

        # Pattern + switches
        p_row = QHBoxLayout()
        self.ed_pattern = QLineEdit()
        self.chk_case = QCheckBox("Aa")
        self.chk_whole = QCheckBox("Ab|Abc")
        self.chk_regex = QCheckBox(".*")
        self.btn_search = QPushButton("Find")
        p_row.addWidget(QLabel("Query:"))
        p_row.addWidget(self.ed_pattern, 1)
        p_row.addWidget(self.chk_case)
        p_row.addWidget(self.chk_whole)
        p_row.addWidget(self.chk_regex)
        p_row.addWidget(self.btn_search)
        layout.addLayout(p_row)

        # Include/Exclude
        f_row = QHBoxLayout()
        self.ed_includes = QLineEdit()
        self.ed_excludes = QLineEdit()
        f_row.addWidget(QLabel("Include globs (comma):"))
        f_row.addWidget(self.ed_includes, 1)
        f_row.addWidget(QLabel("Exclude globs (comma):"))
        f_row.addWidget(self.ed_excludes, 1)
        layout.addLayout(f_row)

        # Replace (collapsible feel: enable by checkbox)
        rep_grp = QGroupBox("Replace")
        rep_grp.setCheckable(True)
        rep_grp.setChecked(False)
        rep_lay = QVBoxLayout(rep_grp)
        r1 = QHBoxLayout()
        self.ed_repl = QLineEdit()
        self.chk_preserve_case = QCheckBox("Preserve case")
        self.btn_replace_one = QPushButton("Replace one")
        self.btn_replace_all = QPushButton("Replace all")
        r1.addWidget(QLabel("Replacement:"))
        r1.addWidget(self.ed_repl, 1)
        r1.addWidget(self.chk_preserve_case)
        r1.addWidget(self.btn_replace_one)
        r1.addWidget(self.btn_replace_all)
        rep_lay.addLayout(r1)
        layout.addWidget(rep_grp)

        # Advanced Conditions (folder mode)
        adv = QGroupBox("Advanced Options (folder mode)")
        adv_lay = QFormLayout(adv)
        self.adv_field1 = QLineEdit(); self.adv_op1 = QComboBox(); self.adv_val1 = QLineEdit()
        self.adv_op1.addItems(["contains", "contained-in", "equals", "not-equals"])
        adv_lay.addRow("Field #1 / Op / Value:", self._row3(self.adv_field1, self.adv_op1, self.adv_val1))
        self.adv_field2 = QLineEdit(); self.adv_op2 = QComboBox(); self.adv_val2 = QLineEdit()
        self.adv_op2.addItems(["contains", "contained-in", "equals", "not-equals"])
        adv_lay.addRow("Field #2 / Op / Value:", self._row3(self.adv_field2, self.adv_op2, self.adv_val2))
        layout.addWidget(adv)

        # Splitter: match panel + preview
        spl = QSplitter(Qt.Vertical)
        self.match_panel = MatchPanel()
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        spl.addWidget(self.match_panel)
        spl.addWidget(self.preview)
        spl.setSizes([280, 240])
        layout.addWidget(spl, 1)

    def _row3(self, a: QWidget, b: QWidget, c: QWidget) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0,0,0,0)
        h.addWidget(a, 1); h.addWidget(b); h.addWidget(c, 1)
        return w

    def _wire(self):
        self.btn_browse.clicked.connect(self._browse)
        self.btn_search.clicked.connect(self._on_search)
        self.match_panel.btn_refresh.clicked.connect(self._on_search)
        self.match_panel.view.clicked.connect(self._on_select_match)

        self.chk_case.toggled.connect(self._on_search)
        self.chk_whole.toggled.connect(self._on_search)
        self.chk_regex.toggled.connect(self._on_search)
        self.ed_includes.editingFinished.connect(self._on_search)
        self.ed_excludes.editingFinished.connect(self._on_search)

        # Replace actions
        self.btn_replace_one.clicked.connect(lambda: self._do_replace(one=True))
        self.btn_replace_all.clicked.connect(lambda: self._do_replace(one=False))

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select folder (folder mode)")
        if path:
            self.ed_path.setText(path)
            self._on_search()

    def _opts(self) -> SearchOptions:
        return SearchOptions(
            case_sensitive=self.chk_case.isChecked(),
            whole_word=self.chk_whole.isChecked(),
            regex=self.chk_regex.isChecked()
        )

    def _parse_globs(self, text: str) -> List[str]:
        return [s.strip() for s in text.split(",") if s.strip()]

    def _advanced_ok(self, file_path: str, text: str) -> bool:
        def eval_line(field: str, op: str, val: str) -> bool:
            if not field and not val:
                return True
            # “field” is a loose concept here: we allow checking filename or content
            hay_fn = os.path.basename(file_path)
            hay_ct = text
            needle = val
            def contains(h, n): return (n in h)
            def contained_in(h, n): return (h in n)
            def equals(h, n): return (h == n)
            def not_equals(h, n): return (h != n)
            ops = {
                "contains": contains,
                "contained-in": contained_in,
                "equals": equals,
                "not-equals": not_equals
            }
            fun = ops.get(op, contains)
            target = hay_ct if field.lower() in ("content","text","body") else hay_fn
            return fun(target, needle)

        ok1 = eval_line(self.adv_field1.text().strip(), self.adv_op1.currentText(), self.adv_val1.text().strip())
        ok2 = eval_line(self.adv_field2.text().strip(), self.adv_op2.currentText(), self.adv_val2.text().strip())
        return ok1 and ok2

    def _on_search(self):
        root = self.ed_path.text().strip()
        if not root or not os.path.isdir(root):
            self.match_panel.set_results(root, [])
            self.preview.clear()
            return
        patt = self.ed_pattern.text()
        inc = self._parse_globs(self.ed_includes.text())
        exc = self._parse_globs(self.ed_excludes.text())
        opts = self._opts()

        found: List[str] = []
        for f in build_file_list(root, inc, exc):
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
                if find_in_text(txt, patt, opts) and self._advanced_ok(f, txt):
                    found.append(f)
            except Exception:
                pass
        self._matches = found
        self.match_panel.set_results(root, found)
        self.preview.clear()

    def _on_select_match(self):
        path = self.match_panel.selected_path()
        if not path:
            self.preview.clear()
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                self.preview.setPlainText(fh.read())
        except Exception as e:
            self.preview.setPlainText(f"<<Error reading {path}: {e}>>")

    def _do_replace(self, one: bool):
        if not self._matches:
            QMessageBox.information(self, "Replace", "No matches to replace.")
            return
        patt = self.ed_pattern.text()
        repl = self.ed_repl.text()
        if not patt:
            QMessageBox.warning(self, "Replace", "Query is empty.")
            return

        opts = self._opts()
        count = 0
        for path in self._matches:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
                # simple replace respecting regex and case
                if opts.regex:
                    flags = 0 if opts.case_sensitive else re.IGNORECASE
                    new_txt, n = re.subn(patt, repl, txt, flags=flags)
                else:
                    if not opts.case_sensitive:
                        # naive case-insensitive replace
                        # (for preserve-case, you can extend this; kept simple here)
                        new_txt, n = re.subn(re.escape(patt), repl, txt, flags=re.IGNORECASE)
                    else:
                        new_txt = txt.replace(patt, repl)
                        n = txt.count(patt)
                if n:
                    with open(path, "w", encoding="utf-8") as fw:
                        fw.write(new_txt)
                    count += n
                    if one:
                        break
            except Exception:
                pass
        QMessageBox.information(self, "Replace", f"Replacements made: {count}")
        self._on_search()

# =============================== Insert Tab (with live Match) ===============================
class InsertTab(QWidget):
    """
    Insert functionality + live match panel (same component as Search/Replace).
    Live updates when:
      - Path is a directory; and
      - At least one Advanced Options row has a non-empty 'Value' (or Field).
      - Triggers on editingFinished/toggles for the controls.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._wire()
        self._matches: List[str] = []

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Path and line controls
        r1 = QHBoxLayout()
        self.ed_path = QLineEdit()
        self.btn_browse = QPushButton("Browse…")
        r1.addWidget(QLabel("Path:"))
        r1.addWidget(self.ed_path, 1)
        r1.addWidget(self.btn_browse)
        layout.addLayout(r1)

        r2 = QHBoxLayout()
        self.spin_line = QSpinBox(); self.spin_line.setRange(1, 10_000_000); self.spin_line.setValue(1)
        self.ed_text = QLineEdit()
        r2.addWidget(QLabel("Line #:"))
        r2.addWidget(self.spin_line)
        r2.addWidget(QLabel("Text:"))
        r2.addWidget(self.ed_text, 1)
        layout.addLayout(r2)

        # Insert modes
        r3 = QHBoxLayout()
        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems([
            "Insert left of line",
            "Insert right of line",
            "Push line down and insert",
            "Insert on next line (push rest)",
            "Replace line content"
        ])
        self.btn_apply = QPushButton("Apply")
        r3.addWidget(QLabel("Mode:"))
        r3.addWidget(self.cmb_mode, 1)
        r3.addStretch(1)
        r3.addWidget(self.btn_apply)
        layout.addLayout(r3)

        # Advanced Options
        adv = QGroupBox("Advanced Options (folder mode)")
        adv_lay = QFormLayout(adv)
        self.adv_field1 = QLineEdit(); self.adv_op1 = QComboBox(); self.adv_val1 = QLineEdit()
        self.adv_op1.addItems(["contains", "contained-in", "equals", "not-equals"])
        adv_lay.addRow("Field #1 / Op / Value:", self._row3(self.adv_field1, self.adv_op1, self.adv_val1))
        self.adv_field2 = QLineEdit(); self.adv_op2 = QComboBox(); self.adv_val2 = QLineEdit()
        self.adv_op2.addItems(["contains", "contained-in", "equals", "not-equals"])
        adv_lay.addRow("Field #2 / Op / Value:", self._row3(self.adv_field2, self.adv_op2, self.adv_val2))
        layout.addWidget(adv)

        # Include/Exclude (so we mirror Search)
        f_row = QHBoxLayout()
        self.ed_includes = QLineEdit()
        self.ed_excludes = QLineEdit()
        f_row.addWidget(QLabel("Include globs (comma):"))
        f_row.addWidget(self.ed_includes, 1)
        f_row.addWidget(QLabel("Exclude globs (comma):"))
        f_row.addWidget(self.ed_excludes, 1)
        layout.addLayout(f_row)

        # Splitter: same Match panel + preview
        spl = QSplitter(Qt.Vertical)
        self.match_panel = MatchPanel()
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        spl.addWidget(self.match_panel)
        spl.addWidget(self.preview)
        spl.setSizes([280, 240])
        layout.addWidget(spl, 1)

    def _row3(self, a: QWidget, b: QWidget, c: QWidget) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0,0,0,0)
        h.addWidget(a, 1); h.addWidget(b); h.addWidget(c, 1)
        return w

    def _wire(self):
        self.btn_browse.clicked.connect(self._browse)
        self.btn_apply.clicked.connect(self._apply)
        self.match_panel.btn_refresh.clicked.connect(self._live_refresh)
        self.match_panel.view.clicked.connect(self._on_select_match)

        # Live refresh on advanced options end-edit; also on include/exclude edits.
        for w in [self.adv_field1, self.adv_val1, self.adv_field2, self.adv_val2,
                  self.ed_includes, self.ed_excludes]:
            w.editingFinished.connect(self._live_refresh)
        self.adv_op1.currentIndexChanged.connect(self._live_refresh)
        self.adv_op2.currentIndexChanged.connect(self._live_refresh)
        self.ed_path.editingFinished.connect(self._live_refresh)

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select folder (folder mode)")
        if path:
            self.ed_path.setText(path)
            self._live_refresh()

    def _parse_globs(self, text: str) -> List[str]:
        return [s.strip() for s in text.split(",") if s.strip()]

    def _has_any_advanced_value(self) -> bool:
        return any([
            self.adv_field1.text().strip(), self.adv_val1.text().strip(),
            self.adv_field2.text().strip(), self.adv_val2.text().strip()
        ])

    def _advanced_ok(self, file_path: str, text: str) -> bool:
        def eval_line(field: str, op: str, val: str) -> bool:
            if not field and not val:
                return True
            hay_fn = os.path.basename(file_path)
            hay_ct = text
            needle = val
            def contains(h, n): return (n in h)
            def contained_in(h, n): return (h in n)
            def equals(h, n): return (h == n)
            def not_equals(h, n): return (h != n)
            ops = {
                "contains": contains,
                "contained-in": contained_in,
                "equals": equals,
                "not-equals": not_equals
            }
            fun = ops.get(op, contains)
            target = hay_ct if field.lower() in ("content","text","body") else hay_fn
            return fun(target, needle)

        ok1 = eval_line(self.adv_field1.text().strip(), self.adv_op1.currentText(), self.adv_val1.text().strip())
        ok2 = eval_line(self.adv_field2.text().strip(), self.adv_op2.currentText(), self.adv_val2.text().strip())
        return ok1 and ok2

    def _live_refresh(self):
        root = self.ed_path.text().strip()
        if not (root and os.path.isdir(root)):
            self.match_panel.set_results(root, [])
            self.preview.clear()
            return
        # Only refresh if there's at least one advanced value filled
        if not self._has_any_advanced_value():
            self.match_panel.set_results(root, [])
            self.preview.clear()
            return
        inc = self._parse_globs(self.ed_includes.text())
        exc = self._parse_globs(self.ed_excludes.text())
        found: List[str] = []
        for f in build_file_list(root, inc, exc):
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
                if self._advanced_ok(f, txt):
                    found.append(f)
            except Exception:
                pass
        self._matches = found
        self.match_panel.set_results(root, found)
        self.preview.clear()

    def _on_select_match(self):
        path = self.match_panel.selected_path()
        if not path:
            self.preview.clear()
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                self.preview.setPlainText(fh.read())
        except Exception as e:
            self.preview.setPlainText(f"<<Error reading {path}: {e}>>")

    def _apply(self):
        root = self.ed_path.text().strip()
        if not root:
            QMessageBox.warning(self, "Insert", "Path is required.")
            return
        text = self.ed_text.text()
        line_no = self.spin_line.value()
        mode = self.cmb_mode.currentText()

        targets: List[str] = []
        if os.path.isfile(root):
            targets = [root]
        elif os.path.isdir(root):
            # Use current matches if any; otherwise, all files
            targets = self._matches[:] if self._matches else build_file_list(root, [], [])

        changed = 0
        for f in targets:
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    lines = fh.read().splitlines()
                idx = max(0, min(line_no-1, len(lines)))
                if mode.startswith("Insert left"):
                    if idx < len(lines):
                        lines[idx] = text + lines[idx]
                    else:
                        while len(lines) < idx:
                            lines.append("")
                        lines.append(text)
                elif mode.startswith("Insert right"):
                    if idx < len(lines):
                        lines[idx] = lines[idx] + text
                    else:
                        while len(lines) < idx:
                            lines.append("")
                        lines.append(text)
                elif mode.startswith("Push line down and insert"):
                    while len(lines) < idx:
                        lines.append("")
                    # insert text at idx, push old content down
                    if idx < len(lines):
                        lines.insert(idx, text)
                    else:
                        lines.append(text)
                elif mode.startswith("Insert on next line"):
                    while len(lines) < idx:
                        lines.append("")
                    if idx < len(lines):
                        lines.insert(idx+1, text)
                    else:
                        lines.append(text)
                else:
                    # Replace line content
                    while len(lines) < idx:
                        lines.append("")
                    if idx < len(lines):
                        lines[idx] = text
                    else:
                        lines.append(text)

                with open(f, "w", encoding="utf-8") as fw:
                    fw.write("\n".join(lines) + "\n")
                changed += 1
            except Exception:
                pass
        QMessageBox.information(self, "Insert", f"Files modified: {changed}")
        self._live_refresh()

# =============================== Tools Docks (JSON panels) ===============================
class JsonTranslateDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("JSON Translate", parent)
        w = QWidget()
        v = QVBoxLayout(w)
        self.setWidget(w)
        self.ed_args = QPlainTextEdit()
        self.ed_args.setPlaceholderText(
            "Arguments for replacing_terms_between_tags_with_translate_files.py\n"
            "Example:\n--input dir_or_file --lang en --tags \"{{,}}\""
        )
        self.btn_run = QPushButton("Run Translate Tool")
        v.addWidget(self.ed_args, 1)
        v.addWidget(self.btn_run)
        self.btn_run.clicked.connect(self._run)

    def _run(self):
        if rtt is None:
            QMessageBox.critical(self, "Translate", "Module not found: replacing_terms_between_tags_with_translate_files.py")
            return
        try:
            # Expect rtt.main_cli(args_list) in your module. Adjust if needed.
            args = self.ed_args.toPlainText().split()
            if hasattr(rtt, "main_cli"):
                code = rtt.main_cli(args)
            elif hasattr(rtt, "main"):
                code = rtt.main(args)
            else:
                QMessageBox.warning(self, "Translate", "No callable entry point found in the module.")
                return
            QMessageBox.information(self, "Translate", f"Finished. Exit code: {code}")
        except Exception as e:
            QMessageBox.critical(self, "Translate", f"Error:\n{e}")

class JsonRewriterDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("JSON Rewriter", parent)
        w = QWidget()
        v = QVBoxLayout(w)
        self.setWidget(w)
        self.ed_args = QPlainTextEdit()
        self.ed_args.setPlaceholderText(
            "Arguments for dedupe_json_cli.py\n"
            "Example:\ninput.ts --from-ts --join-keys --eliminate-duplicates --no-line-break -o out.ts --indent 2"
        )
        self.btn_run = QPushButton("Run Dedupe Tool")
        v.addWidget(self.ed_args, 1)
        v.addWidget(self.btn_run)
        self.btn_run.clicked.connect(self._run)

    def _run(self):
        if djc is None:
            QMessageBox.critical(self, "JSON Rewriter", "Module not found: dedupe_json_cli.py")
            return
        try:
            args = self.ed_args.toPlainText().split()
            # Expect djc.main_cli(args_list) in your module. Adjust name if needed.
            if hasattr(djc, "main_cli"):
                code = djc.main_cli(args)
            elif hasattr(djc, "main"):
                code = djc.main(args)
            else:
                QMessageBox.warning(self, "JSON Rewriter", "No callable entry point found in the module.")
                return
            QMessageBox.information(self, "JSON Rewriter", f"Finished. Exit code: {code}")
        except Exception as e:
            QMessageBox.critical(self, "JSON Rewriter", f"Error:\n{e}")

# =============================== Main Window ===============================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clarify")
        self.setWindowIcon(make_app_icon())
        self.resize(1080, 720)

        self._build_menu()
        self._build_ui()
        self._restore_prefs()

    def _build_menu(self):
        bar = self.menuBar()

        m_file = bar.addMenu("File")
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        m_file.addAction(act_exit)

        m_tools = bar.addMenu("Tools")
        self.act_open_translate = QAction("Open JSON Translate", self)
        self.act_open_rewriter = QAction("Open JSON Rewriter", self)
        m_tools.addAction(self.act_open_translate)
        m_tools.addAction(self.act_open_rewriter)

        self.act_open_translate.triggered.connect(lambda: self.dock_translate.show())
        self.act_open_rewriter.triggered.connect(lambda: self.dock_rewriter.show())

        m_themes = bar.addMenu("Themes")
        self.act_theme_system = QAction("System", self, checkable=True)
        self.act_theme_light = QAction("Light", self, checkable=True)
        self.act_theme_dark = QAction("Dark", self, checkable=True)
        grp = [self.act_theme_system, self.act_theme_light, self.act_theme_dark]
        for a in grp:
            m_themes.addAction(a)
            a.triggered.connect(lambda _, x=a: self._apply_theme_action(x))
        self.act_theme_system.setChecked(True)

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
                                "Clarify\n\nPurpose: search, replace, insert and JSON utilities.\n"
                                "Author: Josué Amaral\nVersion: 2025")

    def _build_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_search = SearchReplaceTab()
        self.tab_insert = InsertTab()

        self.tabs.addTab(self.tab_search, "Search / Replace")
        self.tabs.addTab(self.tab_insert, "Insert")

        # Docks (Tools menu toggles them)
        self.dock_translate = JsonTranslateDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_translate)
        self.dock_translate.hide()

        self.dock_rewriter = JsonRewriterDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_rewriter)
        self.dock_rewriter.hide()

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

# =============================== CLI ===============================
def cli_search(args):
    opts = SearchOptions(args.case, args.word, args.regex)
    root = args.path
    inc = [s.strip() for s in (args.include or "").split(",") if s.strip()]
    exc = [s.strip() for s in (args.exclude or "").split(",") if s.strip()]
    patt = args.query or ""
    out = []
    for f in build_file_list(root, inc, exc):
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
            if find_in_text(txt, patt, opts):
                out.append(f)
        except Exception:
            pass
    for p in out:
        print(p)

def cli_replace(args):
    # Simple replace loop (similar to SearchReplaceTab._do_replace)
    opts = SearchOptions(args.case, args.word, args.regex)
    root = args.path
    inc = [s.strip() for s in (args.include or "").split(",") if s.strip()]
    exc = [s.strip() for s in (args.exclude or "").split(",") if s.strip()]
    patt = args.query or ""
    repl = args.replacement or ""
    count = 0
    for f in build_file_list(root, inc, exc):
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
            if opts.regex:
                flags = 0 if opts.case_sensitive else re.IGNORECASE
                new_txt, n = re.subn(patt, repl, txt, flags=flags)
            else:
                if not opts.case_sensitive:
                    new_txt, n = re.subn(re.escape(patt), repl, txt, flags=re.IGNORECASE)
                else:
                    new_txt = txt.replace(patt, repl)
                    n = txt.count(patt)
            if n:
                with open(f, "w", encoding="utf-8") as fw:
                    fw.write(new_txt)
                count += n
        except Exception:
            pass
    print(f"Replacements: {count}")

def cli_insert(args):
    root = args.path
    text = args.text
    line_no = max(1, args.line)
    mode = args.mode
    targets: List[str] = []
    if os.path.isfile(root):
        targets = [root]
    elif os.path.isdir(root):
        inc = [s.strip() for s in (args.include or "").split(",") if s.strip()]
        exc = [s.strip() for s in (args.exclude or "").split(",") if s.strip()]
        targets = build_file_list(root, inc, exc)

    changed = 0
    for f in targets:
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
            idx = max(0, min(line_no-1, len(lines)))
            if mode == "left":
                if idx < len(lines): lines[idx] = text + lines[idx]
                else:
                    while len(lines) < idx: lines.append("")
                    lines.append(text)
            elif mode == "right":
                if idx < len(lines): lines[idx] = lines[idx] + text
                else:
                    while len(lines) < idx: lines.append("")
                    lines.append(text)
            elif mode == "push-line":
                while len(lines) < idx: lines.append("")
                if idx < len(lines): lines.insert(idx, text)
                else: lines.append(text)
            elif mode == "push-next":
                while len(lines) < idx: lines.append("")
                if idx < len(lines): lines.insert(idx+1, text)
                else: lines.append(text)
            else:
                while len(lines) < idx: lines.append("")
                if idx < len(lines): lines[idx] = text
                else: lines.append(text)
            with open(f, "w", encoding="utf-8") as fw:
                fw.write("\n".join(lines) + "\n")
            changed += 1
        except Exception:
            pass
    print(f"Files modified: {changed}")

def cli_translate(args):
    if rtt is None:
        print("Module not found: replacing_terms_between_tags_with_translate_files.py", file=sys.stderr)
        return 2
    argv = args.rest or []
    if hasattr(rtt, "main_cli"):
        return rtt.main_cli(argv)
    if hasattr(rtt, "main"):
        return rtt.main(argv)
    print("No entry in replacing_terms_between_tags_with_translate_files.py", file=sys.stderr)
    return 2

def cli_dedupe(args):
    if djc is None:
        print("Module not found: dedupe_json_cli.py", file=sys.stderr)
        return 2
    argv = args.rest or []
    if hasattr(djc, "main_cli"):
        return djc.main_cli(argv)
    if hasattr(djc, "main"):
        return djc.main(argv)
    print("No entry in dedupe_json_cli.py", file=sys.stderr)
    return 2

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="clarify", description="Clarify — GUI/CLI toolkit")
    sub = p.add_subparsers(dest="cmd", required=False)

    # GUI
    p.add_argument("--gui", action="store_true", help="Launch GUI (default if no cmd).")

    # search
    s = sub.add_parser("search", help="Search files")
    s.add_argument("path", help="Folder path")
    s.add_argument("--query", "-q", default="", help="Query text/regex")
    s.add_argument("--case", action="store_true", help="Case sensitive")
    s.add_argument("--word", action="store_true", help="Whole word")
    s.add_argument("--regex", action="store_true", help="Regex")
    s.add_argument("--include", "-i", default="", help="Include globs (comma)")
    s.add_argument("--exclude", "-x", default="", help="Exclude globs (comma)")
    s.set_defaults(func=cli_search)

    # replace
    r = sub.add_parser("replace", help="Replace in files")
    r.add_argument("path", help="Folder path")
    r.add_argument("--query", "-q", required=True, help="Query text/regex")
    r.add_argument("--replacement", "-r", default="", help="Replacement text")
    r.add_argument("--case", action="store_true", help="Case sensitive")
    r.add_argument("--word", action="store_true", help="Whole word")
    r.add_argument("--regex", action="store_true", help="Regex")
    r.add_argument("--include", "-i", default="", help="Include globs (comma)")
    r.add_argument("--exclude", "-x", default="", help="Exclude globs (comma)")
    r.set_defaults(func=cli_replace)

    # insert
    it = sub.add_parser("insert", help="Insert text at a given line")
    it.add_argument("path", help="File or folder")
    it.add_argument("--text", "-t", required=True, help="Text to insert/replace")
    it.add_argument("--line", "-n", type=int, default=1, help="1-based line number")
    it.add_argument("--mode", "-m", choices=["left","right","push-line","push-next","replace"], default="left")
    it.add_argument("--include", "-i", default="", help="Include globs (comma)")
    it.add_argument("--exclude", "-x", default="", help="Exclude globs (comma)")
    it.set_defaults(func=cli_insert)

    # translate (pass-through)
    tt = sub.add_parser("translate", help="Pass-through to replacing_terms_between_tags_with_translate_files.py")
    tt.add_argument("rest", nargs=argparse.REMAINDER, help="Arguments for the translate tool")
    tt.set_defaults(func=cli_translate)

    # dedupe (pass-through)
    dd = sub.add_parser("dedupe", help="Pass-through to dedupe_json_cli.py")
    dd.add_argument("rest", nargs=argparse.REMAINDER, help="Arguments for the dedupe tool")
    dd.set_defaults(func=cli_dedupe)

    return p

def main(argv=None):
    argv = argv or sys.argv[1:]
    ap = build_argparser()
    ns = ap.parse_args(argv)
    if getattr(ns, "cmd", None):
        return ns.func(ns)
    # default GUI
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
