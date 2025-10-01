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

Run with a GUI (default) or with subcommands for CLI-only processing.

Dependencies:
  - PySide6 (GUI). The CLI works without PySide6 if you run subcommands only.
  - Pure standard library for the rest.

Author: you + ChatGPT
"""

from __future__ import annotations
import argparse
from base64 import b64decode
import dataclasses
import fnmatch
import io
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple, Union
# ---------------------------------------------------------------------------
#  Optional import of PySide6 (the CLI subcommands work even if PySide6 is missing)
# ---------------------------------------------------------------------------
_PYSIDE = True
try:
    from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, QTimer, Signal, QByteArray
    from PySide6.QtGui import QAction, QFontDatabase, QPixmap, QIcon
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QCheckBox, QPushButton, QSplitter, QListWidget, QListWidgetItem,
        QFileDialog, QGroupBox, QComboBox, QSpinBox, QTreeWidget, QTreeWidgetItem,
        QPlainTextEdit, QDockWidget, QMessageBox, QTabWidget
    )
except Exception:
    _PYSIDE = False


# =============================================================================
#                          FILE DISCOVERY & UTILITIES
# =============================================================================

def walk_files(root: str,
               include_globs: Sequence[str] | None = None,
               exclude_globs: Sequence[str] | None = None) -> Iterator[str]:
    """
    Recursively yield files under 'root' (file or directory). Uses fnmatch-style glob filters.
    - include_globs: if provided, file path must match at least one of them (relative or absolute).
    - exclude_globs: if provided, file path must NOT match any of them.
    """
    include_globs = [g.strip() for g in (include_globs or []) if g.strip()]
    exclude_globs = [g.strip() for g in (exclude_globs or []) if g.strip()]

    def _match_any(path: str, patterns: Sequence[str]) -> bool:
        if not patterns:
            return True
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
                return True
        return False

    def _match_none(path: str, patterns: Sequence[str]) -> bool:
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
                return False
        return True

    if os.path.isfile(root):
        if _match_any(root, include_globs) and _match_none(root, exclude_globs):
            yield root
        return

    for dirpath, _dirnames, filenames in os.walk(root):
        for f in filenames:
            path = os.path.join(dirpath, f)
            if _match_any(path, include_globs) and _match_none(path, exclude_globs):
                yield path


def read_text(path: str, max_bytes: Optional[int] = None) -> str:
    with open(path, "rb") as fh:
        data = fh.read() if max_bytes is None else fh.read(max_bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# =============================================================================
#                        SEARCH / REPLACE CORE (CLI + GUI)
# =============================================================================

@dataclass
class SearchOptions:
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False

    def compile(self, needle: str) -> re.Pattern:
        """Build a compiled regex pattern from the user input + options."""
        flags = 0 if self.case_sensitive else re.IGNORECASE
        if self.regex:
            pattern = needle
        else:
            pattern = re.escape(needle)
            if self.whole_word:
                # \b is okay for ASCII-ish words; for non-word separators we offer a fallback:
                pattern = r"\b" + pattern + r"\b"
        try:
            return re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")


def preserve_case_like(matched_text: str, replacement: str) -> str:
    """
    Adjust the case of 'replacement' to mimic the found 'matched_text'.
    - ALL CAPS → upper()
    - Capitalized → capitalize()
    - lower → lower()
    - Mixed → return as-is
    """
    if not matched_text:
        return replacement
    if matched_text.isupper():
        return replacement.upper()
    if matched_text.islower():
        return replacement.lower()
    if matched_text[0].isupper() and matched_text[1:].islower():
        return replacement[:1].upper() + replacement[1:].lower()
    return replacement


def replace_in_text(content: str, pattern: re.Pattern, repl: str,
                    preserve_case: bool = False, count: int = 0) -> Tuple[str, int]:
    """
    Replace occurrences in 'content' using compiled 'pattern'.
    If preserve_case=True, each match adapts 'repl' to the match case.
    'count' behaves like re.sub (0 means replace all).
    Returns (new_content, num_replacements).
    """
    num = 0

    def _repl(m: re.Match) -> str:
        nonlocal num
        num += 1
        return preserve_case_like(m.group(0), repl) if preserve_case else repl

    new = pattern.sub(_repl, content, count=count)
    return new, num


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

@dataclass
class Condition:
    field: str              # "filename" | "path" | "ext" | "size" | "mtime"
    operator: str           # see OPS keys
    value: str

    def matches(self, path: str) -> bool:
        try:
            if self.field == "filename":
                a = os.path.basename(path)
                b = self.value
                return OPS[self.operator](a, b)
            if self.field == "path":
                a = path
                b = self.value
                return OPS[self.operator](a, b)
            if self.field == "ext":
                a = os.path.splitext(path)[1].lstrip(".")
                b = self.value.lstrip(".")
                return OPS[self.operator](a, b)
            if self.field in ("size", "mtime"):
                st = os.stat(path)
                a = st.st_size if self.field == "size" else int(st.st_mtime)
                # numeric operators only make sense here
                if self.operator in (">", "<", ">=", "<=", "equals", "not equals"):
                    b = int(self.value)
                else:
                    b = int(self.value)
                return OPS[self.operator](a, b)
        except Exception:
            return False
        return False


def filter_files_by_conditions(files: Iterable[str], conds: Sequence[Condition]) -> List[str]:
    conds = list(conds or [])
    if not conds:
        return list(files)
    out = []
    for p in files:
        if all(c.matches(p) for c in conds):
            out.append(p)
    return out


# =============================================================================
#                              INSERT TEXT ENGINE
# =============================================================================

class InsertMode:
    LEFT = "left"               # prepend to the existing line text
    RIGHT = "right"             # append to the existing line text
    REPLACE = "replace"         # replace the line content with the text
    INSERT_ABOVE = "insert_above"  # insert a new line above with the text (pushes current down)
    INSERT_BELOW = "insert_below"  # insert a new line below with the text (keeps current)


def insert_at_line(content: str, line_no: int, text: str, mode: str) -> str:
    """
    Insert/modify 'text' at 1-based 'line_no' following 'mode'.
    """
    lines = content.splitlines(keepends=False)
    idx = max(0, min(len(lines), line_no - 1))

    if mode == InsertMode.LEFT:
        if idx >= len(lines):
            # pad until the target line exists
            while len(lines) < idx:
                lines.append("")
            lines.append(text)
        else:
            lines[idx] = text + lines[idx]

    elif mode == InsertMode.RIGHT:
        if idx >= len(lines):
            while len(lines) < idx:
                lines.append("")
            lines.append(text)
        else:
            lines[idx] = lines[idx] + text

    elif mode == InsertMode.REPLACE:
        if idx >= len(lines):
            while len(lines) < idx:
                lines.append("")
            lines.append(text)
        else:
            lines[idx] = text

    elif mode == InsertMode.INSERT_ABOVE:
        lines.insert(idx, text)

    elif mode == InsertMode.INSERT_BELOW:
        lines.insert(min(idx + 1, len(lines)), text)

    else:
        raise ValueError(f"Unknown insert mode: {mode}")

    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


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


def translate_replace_texts(content: str,
                            dictionary: Dict[str, Any],
                            open_tag: str = "{",
                            close_tag: str = "}") -> str:
    """
    Replace visible texts BETWEEN tags by dictionary keys, e.g.:
      "<p>Submit</p>"  →  "<p>{t.common.buttons.submit}</p>"
    Strategy:
      - Build value→key map from the dictionary by flattening.
      - For every value (longest first), replace occurrences that are not inside existing braces.
    NOTE: This is a heuristic; for precise HTML/TSX you’d use a real parser. Good enough for batch refactors.
    """
    flat = flatten_dict_paths(dictionary)
    val2key: Dict[str, str] = {}
    for k, v in flat.items():
        if isinstance(v, str) and v.strip():
            val2key[v] = k

    # Sort by descending length to prefer longer matches first.
    items = sorted(val2key.items(), key=lambda kv: len(kv[0]), reverse=True)

    def _outside_braces(text: str, pos: int, span: int) -> bool:
        # crude: ensure no '{' or '}' inside the window; avoids replacing existing {t...}
        window = text[max(0, pos-1):pos+span+1]
        return ("{" not in window) and ("}" not in window)

    s = content
    for val, key in items:
        if not val:
            continue
        pat = re.escape(val)
        for m in list(re.finditer(pat, s)):
            if _outside_braces(s, m.start(), len(val)):
                s = s[:m.start()] + f"{open_tag}t.{key}{close_tag}" + s[m.end():]
    return s


# =============================================================================
#                   JSON REWRITER (dedupe / join / eliminate)
#        (condensed, self-contained port of your earlier CLI implementation)
# =============================================================================

# --- representation that preserves duplicate keys
class Obj(list):
    """Object represented as list [(key, value), ...], preserving order and duplicate keys."""
    pass

JSONNode = Union[Obj, list, dict, str, int, float, bool, None]

def parse_json_preserving_duplicates_text(text: str) -> JSONNode:
    def _hook(pairs: List[Tuple[str, Any]]) -> Obj:
        return Obj(pairs)
    return json.loads(text, object_pairs_hook=_hook)

# ---- TS/JS block finding + conversion to JSON-ish ----

def strip_bom(s: str) -> str:
    return s.lstrip("\ufeff")

def scan_find_next_lbrace(s: str, pos: int) -> int:
    i, n = pos, len(s)
    in_str = False; q = ""; esc = False; in_line = False; in_block = False
    while i < n:
        ch = s[i]; nxt = s[i+1] if i+1 < n else ""
        if in_line:
            if ch == "\n": in_line = False
            i += 1; continue
        if in_block:
            if ch == "*" and nxt == "/": in_block = False; i += 2; continue
            i += 1; continue
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: in_str = False
            i += 1; continue
        if ch == "/" and nxt == "/": in_line = True; i += 2; continue
        if ch == "/" and nxt == "*": in_block = True; i += 2; continue
        if ch in ("'", '"', "`"): in_str = True; q = ch; i += 1; continue
        if ch == "{": return i
        i += 1
    return -1

def extract_balanced_from(s: str, lbrace_idx: int) -> Optional[Tuple[int, int, str]]:
    i, n = lbrace_idx, len(s)
    in_str = False; q = ""; esc = False; in_line = False; in_block = False
    depth = 0; start = None
    while i < n:
        ch = s[i]; nxt = s[i+1] if i+1 < n else ""
        if in_line:
            if ch == "\n": in_line = False
            i += 1; continue
        if in_block:
            if ch == "*" and nxt == "/": in_block = False; i += 2; continue
            i += 1; continue
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: in_str = False
            i += 1; continue
        if ch == "/" and nxt == "/": in_line = True; i += 2; continue
        if ch == "/" and nxt == "*": in_block = True; i += 2; continue
        if ch in ("'", '"', "`"): in_str = True; q = ch; i += 1; continue

        if ch == "{":
            if depth == 0: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                end = i + 1
                return start, end, s[start:end]
        i += 1
    return None

def find_object_block(raw: str) -> Tuple[int, int, str]:
    s = strip_bom(raw)
    m = re.search(r'\bexport\s+default\b', s)
    if m:
        lb = scan_find_next_lbrace(s, m.end())
        if lb != -1:
            ext = extract_balanced_from(s, lb)
            if ext and ":" in ext[2]:
                return ext
    for m in re.finditer(r'=', s):
        lb = scan_find_next_lbrace(s, m.end())
        if lb != -1:
            ext = extract_balanced_from(s, lb)
            if ext and ":" in ext[2]:
                return ext
    # fallback: largest with many colons
    blocks = []
    i = s.find("{")
    while i != -1:
        ext = extract_balanced_from(s, i)
        if not ext: break
        blocks.append(ext)
        i = s.find("{", ext[1])
    if not blocks:
        raise ValueError("Could not find a {…} block.")
    blocks.sort(key=lambda t: (t[2].count(":"), len(t[2])), reverse=True)
    return blocks[0]

def strip_comments_code(s: str) -> str:
    out = []
    i = 0; n = len(s)
    in_str = False; q = ""; esc = False; in_line = False; in_block = False
    while i < n:
        ch = s[i]; nxt = s[i+1] if i+1 < n else ""
        if in_line:
            if ch == "\n": in_line = False; out.append(ch)
            i += 1; continue
        if in_block:
            if ch == "*" and nxt == "/": in_block = False; i += 2; continue
            i += 1; continue
        if in_str:
            out.append(ch)
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: in_str = False
            i += 1; continue
        if ch == "/" and nxt == "/": in_line = True; i += 2; continue
        if ch == "/" and nxt == "*": in_block = True; i += 2; continue
        if ch in ("'", '"', "`"):
            in_str = True; q = ch; out.append(ch); i += 1; continue
        out.append(ch); i += 1
    return "".join(out)

def lift_strings_to_placeholders(s: str) -> tuple[str, List[str]]:
    out, tokens = [], []
    i = 0; n = len(s); start = 0
    while i < n:
        ch = s[i]
        if ch in ("'", '"', "`"):
            out.append(s[start:i])
            q = ch; i += 1; buf = []; esc = False
            while i < n:
                c = s[i]
                if esc: buf.append(c); esc = False; i += 1; continue
                if c == "\\": buf.append(c); esc = True; i += 1; continue
                if c == q: i += 1; break
                buf.append(c); i += 1
            content = "".join(buf)
            tokens.append(json.dumps(content, ensure_ascii=False))
            out.append(f"@@S{len(tokens)-1}@@")
            start = i
        else:
            i += 1
    out.append(s[start:])
    return "".join(out), tokens

def restore_placeholders(s: str, tokens: List[str]) -> str:
    for i, t in enumerate(tokens):
        s = s.replace(f"@@S{i}@@", t)
    return s

def quote_bare_and_numeric_keys(s: str) -> str:
    ident = r'[A-Za-z_$][A-Za-z0-9_$]*'
    s = re.sub(r'([{\[,]\s*)(' + ident + r')(\s*:)', r'\1"\2"\3', s)
    s = re.sub(r'([{\[,]\s*)(\d+)(\s*:)', r'\1"\2"\3', s)
    return s

def remove_trailing_commas(s: str) -> str:
    return re.sub(r',(\s*[}\]])', r'\1', s)

def ts_block_to_json_text(block: str) -> str:
    b = strip_comments_code(block)
    no_str, tokens = lift_strings_to_placeholders(b)
    with_keys = quote_bare_and_numeric_keys(no_str)
    no_trailing = remove_trailing_commas(with_keys)
    return restore_placeholders(no_trailing, tokens)

# ---- dedupe / join / eliminate ----

def freeze(node: JSONNode) -> Any:
    if isinstance(node, Obj):
        return ('obj', tuple((k, freeze(v)) for (k, v) in node))
    if isinstance(node, list):
        return ('arr', tuple(freeze(x) for x in node))
    return ('val', node)

def dedupe(node: JSONNode) -> JSONNode:
    if isinstance(node, Obj):
        seen = set()
        out = Obj()
        for k, v in node:
            v2 = dedupe(v)
            sig = (k, freeze(v2))
            if sig in seen:
                continue
            seen.add(sig)
            out.append((k, v2))
        return out
    if isinstance(node, list):
        return [dedupe(x) for x in node]
    return node

def merge_obj_values(values: List[Obj]) -> Obj:
    merged_pairs: Obj = Obj()
    for o in values:
        merged_pairs.extend(o)
    return join_keys(merged_pairs)

def join_keys(node: JSONNode) -> JSONNode:
    if isinstance(node, Obj):
        processed = [(k, join_keys(v)) for (k, v) in node]
        order: List[str] = []
        groups: Dict[str, List[JSONNode]] = {}
        for k, v in processed:
            if k not in groups:
                groups[k] = []; order.append(k)
            groups[k].append(v)

        out = Obj()
        for k in order:
            vals = groups[k]
            if len(vals) == 1:
                out.append((k, vals[0])); continue
            first_sig = freeze(vals[0])
            if all(freeze(v) == first_sig for v in vals[1:]):
                out.append((k, vals[0])); continue
            if all(isinstance(v, Obj) for v in vals):
                out.append((k, merge_obj_values(vals))); continue
            uniq: List[JSONNode] = []
            seen = set()
            for v in vals:
                sig = freeze(v)
                if sig in seen: continue
                seen.add(sig); uniq.append(v)
            out.append((k, uniq[0] if len(uniq) == 1 else uniq))
        return out
    if isinstance(node, list):
        return [join_keys(x) for x in node]
    return node

def eliminate_duplicates(node: JSONNode) -> JSONNode:
    seen: set = set()
    def _visit(n: JSONNode) -> Optional[JSONNode]:
        if isinstance(n, Obj):
            out = Obj()
            for k, v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen: continue
                seen.add(sig)
                out.append((k, v2))
            return out if out else None
        if isinstance(n, list):
            out: List[JSONNode] = []
            for v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen: continue
                seen.add(sig)
                out.append(v2)
            return out if out else None
        return n
    res = _visit(node)
    return res if res is not None else Obj()

_ident_re = re.compile(r'^[A-Za-z_$][A-Za-z0-9_$]*$')
_num_re = re.compile(r'^\d+$')

def esc_single(s: str) -> str:
    return (s.replace('\\', '\\\\')
             .replace("'", "\\'")
             .replace('\r', '\\r')
             .replace('\n', '\\n')
             .replace('\t', '\\t'))

def dump_ts_scalar(x: Any) -> str:
    if isinstance(x, str): return "'" + esc_single(x) + "'"
    if x is True: return "true"
    if x is False: return "false"
    if x is None: return "null"
    return json.dumps(x, ensure_ascii=False)

def dump_ts_key(k: str) -> str:
    if _ident_re.match(k) or _num_re.match(k):
        return k
    return "'" + esc_single(k) + "'"

def dump_ts_obj(obj: Obj, indent: Optional[int], level: int) -> str:
    if not obj: return "{}"
    if indent is None or indent <= 0:
        parts = ["{"] + [("," if i else "") + dump_ts_key(k) + ":" + dump_ts_node(v, indent, level)
                         for i,(k,v) in enumerate(obj)] + ["}"]
        return "".join(parts)
    ind = " " * indent
    parts: List[str] = ["{\n"]
    for i,(k,v) in enumerate(obj):
        if i: parts.append(",\n")
        parts.append(ind*(level+1) + dump_ts_key(k) + ": " + dump_ts_node(v, indent, level+1))
    parts.append("\n" + ind*level + "}")
    return "".join(parts)

def dump_ts_array(arr: list, indent: Optional[int], level: int) -> str:
    if not arr: return "[]"
    if indent is None or indent <= 0:
        parts = ["["] + [("," if i else "") + dump_ts_node(v, indent, level)
                         for i,v in enumerate(arr)] + ["]"]
        return "".join(parts)
    ind = " " * indent
    parts: List[str] = ["[\n"]
    for i,v in enumerate(arr):
        if i: parts.append(",\n")
        parts.append(ind*(level+1) + dump_ts_node(v, indent, level+1))
    parts.append("\n" + ind*level + "]")
    return "".join(parts)

def dump_ts_node(node: JSONNode, indent: Optional[int], level: int) -> str:
    if isinstance(node, Obj): return dump_ts_obj(node, indent, level)
    if isinstance(node, list): return dump_ts_array(node, indent, level)
    return dump_ts_scalar(node)

def collapse_blank_lines(s: str) -> str:
    return re.sub(r'\n[ \t]*\n+', '\n', s)

def ts_process_full_preserving(raw_full: str, indent: Optional[int], join: bool, elim: bool) -> str:
    start, end, block = find_object_block(raw_full)
    json_text = ts_block_to_json_text(block)
    data = parse_json_preserving_duplicates_text(json_text)
    result = join_keys(data) if join else dedupe(data)
    if elim:
        result = eliminate_duplicates(result)
    ts_block = dump_ts_node(result, indent, 0)
    return raw_full[:start] + ts_block + raw_full[end:]


# =============================================================================
#                                CLI SUBCOMMANDS
# =============================================================================

def cli_search(args: argparse.Namespace) -> int:
    patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
    files = list(walk_files(args.path, args.include, args.exclude))
    files = filter_files_by_conditions(files, [Condition(*c.split(":",2)) for c in args.cond or []])
    total = 0
    for p in files:
        try:
            text = read_text(p)
            for m in patt.finditer(text):
                # print 1-based line:col and the line excerpt
                line = text.count("\n", 0, m.start()) + 1
                col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                excerpt = text.splitlines()[line-1]
                print(f"{p}:{line}:{col}: {excerpt.strip()}")
                total += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\n{total} matches.")
    return 0


def cli_replace(args: argparse.Namespace) -> int:
    patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
    files = list(walk_files(args.path, args.include, args.exclude))
    files = filter_files_by_conditions(files, [Condition(*c.split(":",2)) for c in args.cond or []])
    changed = 0
    for p in files:
        try:
            text = read_text(p)
            new, n = replace_in_text(text, patt, args.replacement, args.preserve_case, 0 if args.all else 1)
            if n > 0:
                if args.dry_run:
                    print(f"[DRY] {p}: would replace {n} occurrence(s)")
                else:
                    write_text(p, new)
                    print(f"[OK ] {p}: replaced {n} occurrence(s)")
                    changed += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0


def cli_insert(args: argparse.Namespace) -> int:
    files = list(walk_files(args.path, args.include, args.exclude))
    files = filter_files_by_conditions(files, [Condition(*c.split(":",2)) for c in args.cond or []])
    changed = 0
    for p in files:
        try:
            text = read_text(p)
            new = insert_at_line(text, args.line, args.text, args.mode)
            if new != text:
                if args.dry_run:
                    print(f"[DRY] {p}: would modify")
                else:
                    write_text(p, new)
                    print(f"[OK ] {p}: modified")
                    changed += 1
        except Exception as e:
            print(f"[WARN] {p}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0


def cli_translate(args: argparse.Namespace) -> int:
    files = list(walk_files(args.path, args.include, args.exclude))
    d = load_translation_dict(args.dictionary)
    changed = 0
    for p in files:
        try:
            text = read_text(p)
            new = translate_replace_texts(text, d, "{", "}")
            if new != text:
                if args.dry_run:
                    print(f"[DRY] {p}: would translate")
                else:
                    write_text(p, new)
                    print(f"[OK ] {p}: translated")
                    changed += 1
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
            body_obj = dump_ts_node(result, indent, 0)
            out = f"export default {body_obj};\n"
        else:
            out = ts_process_full_preserving(raw, indent, args.join_keys, args.eliminate_duplicates)
    else:
        # JSON in/out
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


# =============================================================================
#                                   GUI
# =============================================================================

if _PYSIDE:

    class ResultsTree(QTreeWidget):
        """
        Tree view similar to VS Code's search results:
            File
              line:col  text preview
        """
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setHeaderLabels(["Match"])
            self.setRootIsDecorated(True)
            self.setColumnCount(1)
            self.setUniformRowHeights(True)

        def populate(self, matches: Dict[str, List[Tuple[int,int,str]]]):
            self.clear()
            for path, items in matches.items():
                top = QTreeWidgetItem([path])
                self.addTopLevelItem(top)
                for line, col, snippet in items:
                    leaf = QTreeWidgetItem([f"{line}:{col}  {snippet.strip()}"])
                    top.addChild(leaf)
            self.expandAll()


    class SearchReplacePanel(QWidget):
        """
        Left-hand panel: path + include/exclude + search & replace controls.
        Right-hand panel: results.
        """
        request_preview = Signal(dict)   # emits {"matches": {path: [(line,col,snip), ...], ...}}

        def __init__(self, parent=None):
            super().__init__(parent)
            root = QVBoxLayout(self)

            # Path row
            row = QHBoxLayout()
            row.addWidget(QLabel("Root path:"))
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            row.addWidget(self.ed_path, 1)
            row.addWidget(self.btn_browse)
            root.addLayout(row)

            # Include/Exclude globs
            row = QHBoxLayout()
            row.addWidget(QLabel("Include globs (comma-separated):"))
            self.ed_inc = QLineEdit("*.ts;*.tsx;*.js;*.jsx;*.py;*.md")
            root.addLayout(row)
            root.addWidget(self.ed_inc)
            row = QHBoxLayout()
            row.addWidget(QLabel("Exclude globs (comma-separated):"))
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            root.addLayout(row)
            root.addWidget(self.ed_exc)

            # Search field + toggles
            gb = QGroupBox("Search")
            g = QGridLayout(gb)
            g.addWidget(QLabel("Query:"), 0, 0)
            self.ed_query = QLineEdit()
            self.chk_case = QCheckBox("Case sensitive")
            self.chk_word = QCheckBox("Whole word")
            self.chk_regex = QCheckBox("Regex")
            self.btn_search = QPushButton("Search")
            g.addWidget(self.ed_query, 0, 1, 1, 3)
            g.addWidget(self.chk_case, 1, 0)
            g.addWidget(self.chk_word, 1, 1)
            g.addWidget(self.chk_regex, 1, 2)
            g.addWidget(self.btn_search, 1, 3)
            root.addWidget(gb)

            # Replace extras (optional)
            gb2 = QGroupBox("Replace (enable if needed)")
            g2 = QGridLayout(gb2)
            g2.addWidget(QLabel("Replacement:"), 0, 0)
            self.ed_repl = QLineEdit()
            self.chk_preserve = QCheckBox("Preserve case")
            self.btn_replace_one = QPushButton("Replace first per file")
            self.btn_replace_all = QPushButton("Replace all")
            g2.addWidget(self.ed_repl, 0, 1, 1, 3)
            g2.addWidget(self.chk_preserve, 1, 0)
            g2.addWidget(self.btn_replace_one, 1, 2)
            g2.addWidget(self.btn_replace_all, 1, 3)
            root.addWidget(gb2)

            # Advanced conditions (collapsible style via group box)
            gb3 = QGroupBox("Advanced conditions (when operating on a folder)")
            g3 = QGridLayout(gb3)
            self.cond_list: List[Tuple[QComboBox, QComboBox, QLineEdit]] = []
            for row_i in range(3):  # three rows to start; users can reuse them
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime"])
                cb_op = QComboBox(); cb_op.addItems(["", "contains", "not contains", "equals", "not equals",
                                                     "starts with", "ends with", ">", "<", ">=", "<="])
                ed_val = QLineEdit()
                g3.addWidget(cb_field, row_i, 0)
                g3.addWidget(cb_op,    row_i, 1)
                g3.addWidget(ed_val,   row_i, 2, 1, 2)
                self.cond_list.append((cb_field, cb_op, ed_val))
            root.addWidget(gb3)

            # Results on the right
            self.results = ResultsTree()

            splitter = QSplitter()
            left = QWidget(); left.setLayout(root)
            splitter.addWidget(left)
            splitter.addWidget(self.results)
            splitter.setSizes([500, 800])

            wroot = QVBoxLayout(self)
            wroot.setContentsMargins(0, 0, 0, 0)
            wroot.addWidget(splitter)

            # Connect
            self.btn_browse.clicked.connect(self._browse)
            self.btn_search.clicked.connect(self._do_search)
            self.btn_replace_one.clicked.connect(lambda: self._do_replace(all_=False))
            self.btn_replace_all.clicked.connect(lambda: self._do_replace(all_=True))

        def _browse(self):
            path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
            if path:
                self.ed_path.setText(path)

        def _conds(self) -> List[Condition]:
            out: List[Condition] = []
            for cb_field, cb_op, ed in self.cond_list:
                f = cb_field.currentText().strip()
                o = cb_op.currentText().strip()
                v = ed.text().strip()
                if f and o and v:
                    out.append(Condition(f, o, v))
            return out

        def _iter_files(self) -> List[str]:
            path = self.ed_path.text().strip()
            inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            return filter_files_by_conditions(files, self._conds())

        def _do_search(self):
            try:
                patt = SearchOptions(self.chk_case.isChecked(),
                                     self.chk_word.isChecked(),
                                     self.chk_regex.isChecked()).compile(self.ed_query.text())
            except ValueError as e:
                QMessageBox.critical(self, "Invalid pattern", str(e)); return

            matches: Dict[str, List[Tuple[int,int,str]]] = {}
            for p in self._iter_files():
                try:
                    text = read_text(p)
                    lst: List[Tuple[int,int,str]] = []
                    for m in patt.finditer(text):
                        line = text.count("\n", 0, m.start()) + 1
                        col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                        snippet = text.splitlines()[line-1]
                        lst.append((line, col, snippet))
                    if lst:
                        matches[p] = lst
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            self.results.populate(matches)

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
            self._do_search()


    class InsertPanel(QWidget):
        request_status = Signal(str)

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QGridLayout(self)

            layout.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            layout.addWidget(self.ed_path, 0, 1, 1, 3)
            layout.addWidget(self.btn_browse, 0, 4)

            layout.addWidget(QLabel("Include globs:"), 1, 0)
            self.ed_inc = QLineEdit("*.ts;*.tsx;*.js;*.jsx;*.py;*.md")
            layout.addWidget(self.ed_inc, 1, 1, 1, 4)

            layout.addWidget(QLabel("Exclude globs:"), 2, 0)
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            layout.addWidget(self.ed_exc, 2, 1, 1, 4)

            layout.addWidget(QLabel("Line number (1-based):"), 3, 0)
            self.spin_line = QSpinBox(); self.spin_line.setRange(1, 10_000_000); self.spin_line.setValue(1)
            layout.addWidget(self.spin_line, 3, 1)

            layout.addWidget(QLabel("Insert text:"), 4, 0)
            self.ed_text = QPlainTextEdit()
            layout.addWidget(self.ed_text, 4, 1, 1, 4)

            layout.addWidget(QLabel("Mode:"), 5, 0)
            self.cb_mode = QComboBox()
            self.cb_mode.addItems([InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE,
                                   InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW])
            layout.addWidget(self.cb_mode, 5, 1)

            self.btn_apply = QPushButton("Apply to files")
            layout.addWidget(self.btn_apply, 6, 4)

            self.btn_browse.clicked.connect(self._browse)
            self.btn_apply.clicked.connect(self._apply)

        def _browse(self):
            path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
            if path:
                self.ed_path.setText(path)

        def _files(self) -> List[str]:
            path = self.ed_path.text().strip()
            inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = walk_files(path, inc, exc)
            return list(files)

        def _apply(self):
            line = self.spin_line.value()
            text = self.ed_text.toPlainText()
            mode = self.cb_mode.currentText()
            count = 0
            for p in self._files():
                try:
                    old = read_text(p)
                    new = insert_at_line(old, line, text, mode)
                    if new != old:
                        write_text(p, new)
                        count += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            QMessageBox.information(self, "Insert", f"Modified files: {count}")


    class JsonTranslateDock(QDockWidget):
        def __init__(self, parent=None):
            super().__init__("JSON Translate", parent)
            w = QWidget(); self.setWidget(w)
            g = QGridLayout(w)
            g.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            g.addWidget(self.ed_path, 0, 1, 1, 3)
            g.addWidget(self.btn_browse, 0, 4)
            g.addWidget(QLabel("Dictionary file (JSON/TS):"), 1, 0)
            self.ed_dict = QLineEdit()
            self.btn_open = QPushButton("Open…")
            g.addWidget(self.ed_dict, 1, 1, 1, 3)
            g.addWidget(self.btn_open, 1, 4)
            self.btn_run = QPushButton("Run translation")
            g.addWidget(self.btn_run, 2, 4)

            self.btn_browse.clicked.connect(self._browse_root)
            self.btn_open.clicked.connect(self._browse_dict)
            self.btn_run.clicked.connect(self._run)

        def _browse_root(self):
            path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
            if path: self.ed_path.setText(path)

        def _browse_dict(self):
            f, _ = QFileDialog.getOpenFileName(self, "Select dictionary", "", "JSON/TS (*.json *.ts *.tsx *.js *.jsx);;All (*)")
            if f: self.ed_dict.setText(f)

        def _run(self):
            path = self.ed_path.text().strip()
            dpath = self.ed_dict.text().strip()
            if not path or not dpath:
                QMessageBox.warning(self, "Missing", "Select path and dictionary file."); return
            d = load_translation_dict(dpath)
            changed = 0
            for p in walk_files(path, None, ["node_modules",".git","dist","build"]):
                try:
                    old = read_text(p)
                    new = translate_replace_texts(old, d)
                    if new != old:
                        write_text(p, new)
                        changed += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            QMessageBox.information(self, "Translate", f"Modified files: {changed}")


    class JsonRewriterDock(QDockWidget):
        def __init__(self, parent=None):
            super().__init__("JSON Rewriter", parent)
            w = QWidget(); self.setWidget(w)
            g = QGridLayout(w)
            g.addWidget(QLabel("Input file:"), 0, 0)
            self.ed_in = QLineEdit()
            self.btn_in = QPushButton("Open…")
            g.addWidget(self.ed_in, 0, 1, 1, 3)
            g.addWidget(self.btn_in, 0, 4)
            g.addWidget(QLabel("Output file (optional):"), 1, 0)
            self.ed_out = QLineEdit()
            self.btn_out = QPushButton("Save as…")
            g.addWidget(self.ed_out, 1, 1, 1, 3)
            g.addWidget(self.btn_out, 1, 4)

            self.chk_from_ts = QCheckBox("From TS/JS (preserve file)")
            self.chk_ts_out = QCheckBox("Emit export default …;")
            self.chk_join = QCheckBox("Join keys")
            self.chk_elim = QCheckBox("Eliminate duplicates")
            self.chk_nlb = QCheckBox("No blank lines")
            g.addWidget(self.chk_from_ts, 2, 0)
            g.addWidget(self.chk_ts_out, 2, 1)
            g.addWidget(self.chk_join, 2, 2)
            g.addWidget(self.chk_elim, 2, 3)
            g.addWidget(self.chk_nlb, 2, 4)

            g.addWidget(QLabel("Indent (<=0 compact):"), 3, 0)
            self.spin_indent = QSpinBox(); self.spin_indent.setRange(-1, 16); self.spin_indent.setValue(2)
            self.btn_run = QPushButton("Rewrite")
            g.addWidget(self.spin_indent, 3, 1)
            g.addWidget(self.btn_run, 3, 4)

            self.btn_in.clicked.connect(self._open_in)
            self.btn_out.clicked.connect(self._open_out)
            self.btn_run.clicked.connect(self._rewrite)

        def _open_in(self):
            f, _ = QFileDialog.getOpenFileName(self, "Select input", "", "JSON/TS/JS (*.json *.ts *.tsx *.js *.jsx);;All (*)")
            if f: self.ed_in.setText(f)

        def _open_out(self):
            f, _ = QFileDialog.getSaveFileName(self, "Save output", "", "All (*)")
            if f: self.ed_out.setText(f)

        def _rewrite(self):
            if not self.ed_in.text().strip():
                QMessageBox.warning(self, "Missing", "Choose an input file."); return
            ns = argparse.Namespace(
                input=self.ed_in.text().strip(),
                output=self.ed_out.text().strip() or None,
                indent=self.spin_indent.value(),
                from_ts=self.chk_from_ts.isChecked(),
                ts_out=self.chk_ts_out.isChecked(),
                join_keys=self.chk_join.isChecked(),
                eliminate_duplicates=self.chk_elim.isChecked(),
                no_line_break=self.chk_nlb.isChecked(),
            )
            try:
                cli_dedupe(ns)
                QMessageBox.information(self, "Done", "Rewriter finished.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Clarify-TextWorkbench")
            self.ICON_BASE_64 = "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"
            try:
                # 2. Decode Base64 string to bytes
                icon_data = b64decode(self.ICON_BASE_64)

                # 3. Load the image bytes into a QPixmap
                pixmap = QPixmap()
                if not pixmap.loadFromData(QByteArray(icon_data)):
                    print("Erro ao carregar os dados do ícone do QPixmap.")
                    # Handle the error, perhaps use a default icon or stop
                    icon = QIcon() # empty icon
                else:
                    # Optional: Resize the pixmap if necessary before creating the QIcon
                    # pixmap = pixmap.scaled(64, 64, aspect_ratio_mode=Qt.KeepAspectRatio)

                    # 4. Create a QIcon from QPixmap
                    icon = QIcon(pixmap)

            except Exception as exc:
                print(f"Erro ao processar a string base64 ou criar o ícone: {exc}")
                icon = QIcon() # Ícone vazio em caso de erro

            # 5. Set the icon for the main window
            self.setWindowIcon(icon)
            
            tabs = QTabWidget()
            self.search_panel = SearchReplacePanel()
            self.insert_panel = InsertPanel()
            tabs.addTab(self.search_panel, "Search / Replace")
            tabs.addTab(self.insert_panel, "Insert")

            self.setCentralWidget(tabs)

            # Menu
            tools = self.menuBar().addMenu("&Tools")
            act_trans = QAction("JSON Translate dock", self)
            act_rewrite = QAction("JSON Rewriter dock", self)
            tools.addAction(act_trans); tools.addAction(act_rewrite)
            act_trans.triggered.connect(self._open_trans)
            act_rewrite.triggered.connect(self._open_rewrite)

            # Nice monospaced font for preview-ish widgets
            try:
                f = QFontDatabase.systemFont(QFontDatabase.FixedFont)
                self.search_panel.ed_repl.setFont(f)
                self.search_panel.ed_query.setFont(f)
                self.insert_panel.ed_text.setFont(f)
            except Exception:
                pass

        def _open_trans(self):
            dock = JsonTranslateDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.show()

        def _open_rewrite(self):
            dock = JsonRewriterDock(self)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.show()


# =============================================================================
#                                  ARGPARSE
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Search/Replace/Insert + JSON Translate/Dedupe — GUI or CLI"
    )
    sub = p.add_subparsers(dest="cmd")

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
    win = MainWindow()
    win.resize(1200, 800)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
