#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clarify — GUI + CLI for project-wide search/replace/insert + JSON translate/dedupe
----------------------------------------------------------------------------------
Author: Josué Amaral
Version/Year: 2025

What’s inside:
  1) VS-Code–like Search panel (case/word/regex, include/exclude globs).
  2) Replace (single / all) with preserve-case.
  3) Advanced Conditions for folder operations (filename/path/ext/size/mtime/content + operators).
  4) Insert text at a specific line with 5 placement modes **with Advanced Conditions**.
  5) Tools → JSON Translate (replace visible texts with {t.*} keys from a JSON/TS dictionary).
  6) Tools → JSON Rewriter (dedupe identical pairs, optional join keys, optional eliminate global
     duplicates; supports TS/JS object literals and pure JSON).
  7) CLI subcommands for headless processing (search/replace/insert/translate/dedupe).

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
"""

from __future__ import annotations
import argparse
from base64 import b64decode
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple, Union

# ---------------------- Optional GUI deps (CLI works without GUI) ----------------------
_PYSIDE = True
try:
    from PySide6.QtCore import Qt, QTimer, Signal, QByteArray
    from PySide6.QtGui import QAction, QIcon, QPalette, QColor, QPixmap, QIcon
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QCheckBox, QPushButton, QSplitter, QGroupBox, QComboBox,
        QSpinBox, QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QFileDialog, QMessageBox,
        QDockWidget, QTabWidget
    )
except Exception:
    _PYSIDE = False


# ======================================================================================
#                                     UTILITIES
# ======================================================================================

def walk_files(root: str,
               include_globs: Sequence[str] | None = None,
               exclude_globs: Sequence[str] | None = None) -> Iterator[str]:
    """
    Yield files under 'root' (file or directory). Globs accept ';' or ',' separation.
    """
    include = [g.strip() for g in (include_globs or []) if g.strip()]
    exclude = [g.strip() for g in (exclude_globs or []) if g.strip()]

    def _match_any(path: str, patterns: Sequence[str]) -> bool:
        if not patterns:
            return True
        base = os.path.basename(path)
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(base, pat):
                return True
        return False

    def _match_none(path: str, patterns: Sequence[str]) -> bool:
        base = os.path.basename(path)
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(base, pat):
                return False
        return True

    if os.path.isfile(root):
        if _match_any(root, include) and _match_none(root, exclude):
            yield root
        return

    for dirpath, _dirnames, filenames in os.walk(root):
        for f in filenames:
            p = os.path.join(dirpath, f)
            if _match_any(p, include) and _match_none(p, exclude):
                yield p


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


# ======================================================================================
#                           SEARCH / REPLACE CORE (shared)
# ======================================================================================

@dataclass
class SearchOptions:
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False

    def compile(self, needle: str) -> re.Pattern:
        flags = 0 if self.case_sensitive else re.IGNORECASE
        if self.regex:
            pattern = needle
        else:
            pattern = re.escape(needle)
            if self.whole_word:
                pattern = r"\b" + pattern + r"\b"
        try:
            return re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}")


def preserve_case_like(found: str, repl: str) -> str:
    if not found:
        return repl
    if found.isupper():
        return repl.upper()
    if found.islower():
        return repl.lower()
    if found[0].isupper() and found[1:].islower():
        return repl[:1].upper() + repl[1:].lower()
    return repl


def replace_in_text(content: str, pattern: re.Pattern, repl: str,
                    preserve_case: bool = False, count: int = 0) -> Tuple[str, int]:
    n = 0

    def _repl(m: re.Match) -> str:
        nonlocal n
        n += 1
        return preserve_case_like(m.group(0), repl) if preserve_case else repl

    new = pattern.sub(_repl, content, count=count)
    return new, n


# ======================================================================================
#                             ADVANCED CONDITIONS
# ======================================================================================

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
    field: str    # filename | path | ext | size | mtime | content
    operator: str
    value: str

def filter_files_by_conditions(files: Iterable[str], conds: Sequence[Condition]) -> List[str]:
    """
    Evaluate conditions against metadata and, when needed, file content (for 'content' field).
    We read content at most once per file if any content-condition is present.
    """
    conds = [c for c in (conds or []) if c.field and c.operator]
    if not conds:
        return list(files)

    need_content = any(c.field == "content" for c in conds)
    out: List[str] = []

    for p in files:
        try:
            # Pre-compute fields
            base = os.path.basename(p)
            ext = os.path.splitext(p)[1].lstrip(".")
            st = None
            txt = None

            ok = True
            for c in conds:
                if c.field == "filename":
                    a, b = base, c.value
                elif c.field == "path":
                    a, b = p, c.value
                elif c.field == "ext":
                    a, b = ext, c.value.lstrip(".")
                elif c.field in ("size", "mtime"):
                    st = st or os.stat(p)
                    a = st.st_size if c.field == "size" else int(st.st_mtime)
                    b = int(c.value)
                elif c.field == "content":
                    txt = txt if txt is not None else read_text(p)
                    a, b = txt, c.value
                else:
                    ok = False
                    break

                if not OPS.get(c.operator, lambda *_: False)(a, b):
                    ok = False
                    break

            if ok:
                out.append(p)
        except Exception:
            # Ignore unreadable files
            pass

    return out


# ======================================================================================
#                                   INSERT ENGINE
# ======================================================================================

class InsertMode:
    LEFT = "left"
    RIGHT = "right"
    REPLACE = "replace"
    INSERT_ABOVE = "insert_above"
    INSERT_BELOW = "insert_below"

def insert_at_line(content: str, line_no: int, text: str, mode: str) -> str:
    lines = content.splitlines(keepends=False)
    idx = max(0, min(len(lines), line_no - 1))

    if mode == InsertMode.LEFT:
        if idx >= len(lines):
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


# ======================================================================================
#                 JSON TRANSLATE + JSON REWRITER (compact versions)
# ======================================================================================

# ---- Translation dictionary loader (JSON or TS/JS object literal) ----

def strip_bom(s: str) -> str:
    return s.lstrip("\ufeff")

def read_translation_dict(path: str) -> Dict[str, Any]:
    text = read_text(path)
    if path.lower().endswith(".json"):
        return json.loads(text)
    # TS/JS object literal — find largest {…:…} block and coerce to JSON-ish
    _start, _end, block = find_object_block(text)
    block_json = ts_block_to_json_text(block)
    return json.loads(block_json)

def flatten_dict_paths(d: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in (d or {}).items():
        kk = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten_dict_paths(v, kk))
        else:
            out[kk] = v if v is not None else ""
    return out

def translate_replace_texts(content: str, dictionary: Dict[str, Any],
                            open_tag: str = "{", close_tag: str = "}") -> str:
    flat = flatten_dict_paths(dictionary)
    val2key: Dict[str, str] = {v: k for k, v in flat.items() if isinstance(v, str) and v.strip()}
    items = sorted(val2key.items(), key=lambda kv: len(kv[0]), reverse=True)

    def _outside_braces(s: str, start: int, span: int) -> bool:
        window = s[max(0, start-1):start+span+1]
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

# ---- TS/JS block handling + “preserve duplicate keys” parser (short form) ----

class Obj(list):
    """Preserve duplicate keys as list of (key, value)."""
    pass

JSONNode = Union[Obj, list, dict, str, int, float, bool, None]

def parse_json_preserving_duplicates_text(text: str) -> JSONNode:
    def _hook(pairs: List[Tuple[str, Any]]) -> Obj:
        return Obj(pairs)
    return json.loads(text, object_pairs_hook=_hook)

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
    # 1) Try `export default {...}`
    m = re.search(r'\bexport\s+default\b', s)
    if m:
        lb = scan_find_next_lbrace(s, m.end())
        if lb != -1:
            ext = extract_balanced_from(s, lb)
            if ext and ":" in ext[2]:
                return ext
    # 2) Fallback: first assignment with a JSON-ish block
    for m in re.finditer(r'=', s):
        lb = scan_find_next_lbrace(s, m.end())
        if lb != -1:
            ext = extract_balanced_from(s, lb)
            if ext and ":" in ext[2]:
                return ext
    # 3) Last resort: pick the largest block with many colons
    blocks = []
    i = s.find("{")
    while i != -1:
        ext = extract_balanced_from(s, i)
        if not ext: break
        blocks.append(ext); i = s.find("{", ext[1])
    if not blocks:
        raise ValueError("Could not locate a { … } block in TS/JS.")
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
        seen = set(); out = Obj()
        for k, v in node:
            v2 = dedupe(v)
            sig = (k, freeze(v2))
            if sig in seen: continue
            seen.add(sig); out.append((k, v2))
        return out
    if isinstance(node, list):
        return [dedupe(x) for x in node]
    return node

def merge_obj_values(values: List[Obj]) -> Obj:
    merged = Obj()
    for o in values: merged.extend(o)
    return join_keys(merged)

def join_keys(node: JSONNode) -> JSONNode:
    if isinstance(node, Obj):
        processed = [(k, join_keys(v)) for (k, v) in node]
        order: List[str] = []; groups: Dict[str, List[JSONNode]] = {}
        for k, v in processed:
            groups.setdefault(k, []); groups[k].append(v)
            if k not in order: order.append(k)
        out = Obj()
        for k in order:
            vals = groups[k]
            if len(vals) == 1:
                out.append((k, vals[0])); continue
            first = freeze(vals[0])
            if all(freeze(v) == first for v in vals[1:]):
                out.append((k, vals[0])); continue
            if all(isinstance(v, Obj) for v in vals):
                out.append((k, merge_obj_values(vals))); continue
            uniq: List[JSONNode] = []
            seen = set()
            for v in vals:
                fv = freeze(v)
                if fv in seen: continue
                seen.add(fv); uniq.append(v)
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
                seen.add(sig); out.append((k, v2))
            return out if out else None
        if isinstance(n, list):
            out: List[JSONNode] = []
            for v in n:
                v2 = _visit(v)
                if v2 is None: continue
                sig = freeze(v2)
                if sig in seen: continue
                seen.add(sig); out.append(v2)
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


# ======================================================================================
#                                     CLI
# ======================================================================================

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

def cli_translate(args: argparse.Namespace) -> int:
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    d = read_translation_dict(args.dictionary)
    changed = 0
    for p in files:
        try:
            old = read_text(p)
            new = translate_replace_texts(old, d)
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


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Clarify — Search/Replace/Insert + JSON tools")
    sub = p.add_subparsers(dest="cmd", required=False)

    # search
    sp = sub.add_parser("search", help="Search for text in files")
    sp.add_argument("path")
    sp.add_argument("--query", required=True)
    sp.add_argument("--case", action="store_true")
    sp.add_argument("--word", action="store_true")
    sp.add_argument("--regex", action="store_true")
    sp.add_argument("--include", help="Semicolon/comma list of include globs")
    sp.add_argument("--exclude", help="Semicolon/comma list of exclude globs")
    sp.add_argument("--cond", action="append", help="FIELD:OP:VALUE (filename/path/ext/size/mtime/content)")
    sp.set_defaults(func=cli_search)

    # replace
    rp = sub.add_parser("replace", help="Replace text in files")
    rp.add_argument("path")
    rp.add_argument("--query", required=True)
    rp.add_argument("--replacement", required=True)
    rp.add_argument("--case", action="store_true")
    rp.add_argument("--word", action="store_true")
    rp.add_argument("--regex", action="store_true")
    rp.add_argument("--preserve-case", dest="preserve_case", action="store_true")
    rp.add_argument("--all", action="store_true", help="Replace all occurrences (default: only first per file)")
    rp.add_argument("--include", help="Include globs")
    rp.add_argument("--exclude", help="Exclude globs")
    rp.add_argument("--cond", action="append", help="FIELD:OP:VALUE")
    rp.add_argument("--dry-run", action="store_true")
    rp.set_defaults(func=cli_replace)

    # insert
    ip = sub.add_parser("insert", help="Insert/modify a specific line in files")
    ip.add_argument("path")
    ip.add_argument("--line", type=int, required=True)
    ip.add_argument("--text", required=True)
    ip.add_argument("--mode", choices=[InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE,
                                      InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW], required=True)
    ip.add_argument("--include", help="Include globs")
    ip.add_argument("--exclude", help="Exclude globs")
    ip.add_argument("--cond", action="append", help="FIELD:OP:VALUE (incl. content)")
    ip.add_argument("--dry-run", action="store_true")
    ip.set_defaults(func=cli_insert)

    # translate
    tp = sub.add_parser("translate", help="Replace visible texts with {t.*} dictionary keys")
    tp.add_argument("path")
    tp.add_argument("--dictionary", required=True)
    tp.add_argument("--include", help="Include globs")
    tp.add_argument("--exclude", help="Exclude globs")
    tp.add_argument("--dry-run", action="store_true")
    tp.set_defaults(func=cli_translate)

    # dedupe / ts-rewriter
    dp = sub.add_parser("dedupe", help="Dedupe/join/eliminate duplicates in JSON or TS/JS object")
    dp.add_argument("input")
    dp.add_argument("-o", "--output")
    dp.add_argument("--indent", type=int, default=2)
    dp.add_argument("--from-ts", action="store_true")
    dp.add_argument("--ts-out", action="store_true")
    dp.add_argument("--join-keys", action="store_true")
    dp.add_argument("--eliminate-duplicates", action="store_true")
    dp.add_argument("--no-line-break", action="store_true")
    dp.set_defaults(func=cli_dedupe)

    return p


# ======================================================================================
#                                       GUI
# ======================================================================================

if _PYSIDE:

    class ResultsTree(QTreeWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setHeaderLabels(["Match"])
            self.setUniformRowHeights(True)

        def populate(self, matches: Dict[str, List[Tuple[int,int,str]]]):
            self.clear()
            for path, items in matches.items():
                top = QTreeWidgetItem([path])
                self.addTopLevelItem(top)
                for line, col, snippet in items:
                    top.addChild(QTreeWidgetItem([f"{line}:{col}  {snippet.strip()}"]))
            self.expandAll()

    class SearchReplacePanel(QWidget):
        request_preview = Signal(dict)

        def __init__(self, parent=None):
            super().__init__(parent)
            root = QVBoxLayout(self)

            # Path
            r = QHBoxLayout()
            r.addWidget(QLabel("Root path:"))
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            r.addWidget(self.ed_path, 1); r.addWidget(self.btn_browse)
            root.addLayout(r)

            # Globs
            r = QHBoxLayout(); r.addWidget(QLabel("Include globs:"))
            self.ed_inc = QLineEdit("*.ts;*.tsx;*.js;*.jsx;*.py;*.md")
            r.addWidget(self.ed_inc); root.addLayout(r)
            r = QHBoxLayout(); r.addWidget(QLabel("Exclude globs:"))
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            r.addWidget(self.ed_exc); root.addLayout(r)

            # Search
            gb = QGroupBox("Search")
            g = QGridLayout(gb)
            g.addWidget(QLabel("Query:"), 0, 0)
            self.ed_query = QLineEdit()
            self.chk_case = QCheckBox("Case sensitive")
            self.chk_word = QCheckBox("Whole word")
            self.chk_regex = QCheckBox("Regex")
            self.btn_search = QPushButton("Search")
            g.addWidget(self.ed_query, 0, 1, 1, 3)
            g.addWidget(self.chk_case, 1, 0); g.addWidget(self.chk_word, 1, 1)
            g.addWidget(self.chk_regex, 1, 2); g.addWidget(self.btn_search, 1, 3)
            root.addWidget(gb)

            # Replace
            gb2 = QGroupBox("Replace (optional)")
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

            # Advanced conditions
            self.gb3 = QGroupBox("Advanced conditions (folder mode)")
            g3 = QGridLayout(self.gb3)
            self.cond_list: List[Tuple[QComboBox, QComboBox, QLineEdit]] = []
            for row_i in range(3):
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
                cb_op = QComboBox(); cb_op.addItems(["", "contains", "not contains", "equals", "not equals",
                                                     "starts with", "ends with", ">", "<", ">=", "<="])
                ed_val = QLineEdit()
                g3.addWidget(cb_field, row_i, 0); g3.addWidget(cb_op, row_i, 1); g3.addWidget(ed_val, row_i, 2, 1, 2)
                self.cond_list.append((cb_field, cb_op, ed_val))
            root.addWidget(self.gb3)

            # Results
            self.results = ResultsTree()

            splitter = QSplitter()
            left = QWidget(); left.setLayout(root)
            splitter.addWidget(left); splitter.addWidget(self.results)
            splitter.setSizes([520, 800])

            wroot = QVBoxLayout(self)
            wroot.setContentsMargins(0,0,0,0); wroot.addWidget(splitter)

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
                        write_text(p, new); count_files += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            QMessageBox.information(self, "Replace", f"Modified files: {count_files}")
            self._do_search()


    class InsertPanel(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QGridLayout(self)

            # Path + globs
            layout.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            layout.addWidget(self.ed_path, 0, 1, 1, 3); layout.addWidget(self.btn_browse, 0, 4)

            layout.addWidget(QLabel("Include globs:"), 1, 0)
            self.ed_inc = QLineEdit("*.ts;*.tsx;*.js;*.jsx;*.py;*.md")
            layout.addWidget(self.ed_inc, 1, 1, 1, 4)

            layout.addWidget(QLabel("Exclude globs:"), 2, 0)
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            layout.addWidget(self.ed_exc, 2, 1, 1, 4)

            # Line + text + mode
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

            # Advanced conditions (same as Search/Replace, including `content`)
            gb3 = QGroupBox("Advanced conditions (folder mode)")
            g3 = QGridLayout(gb3)
            self.cond_list: List[Tuple[QComboBox, QComboBox, QLineEdit]] = []
            for row_i in range(3):
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
                cb_op = QComboBox(); cb_op.addItems(["", "contains", "not contains", "equals", "not equals",
                                                     "starts with", "ends with", ">", "<", ">=", "<="])
                ed_val = QLineEdit()
                g3.addWidget(cb_field, row_i, 0); g3.addWidget(cb_op, row_i, 1); g3.addWidget(ed_val, row_i, 2, 1, 2)
                self.cond_list.append((cb_field, cb_op, ed_val))
            layout.addWidget(gb3, 6, 0, 1, 5)

            self.btn_apply = QPushButton("Apply to files")
            layout.addWidget(self.btn_apply, 7, 4)

            self.btn_browse.clicked.connect(self._browse)
            self.btn_apply.clicked.connect(self._apply)

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

        def _files(self) -> List[str]:
            path = self.ed_path.text().strip()
            inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            return filter_files_by_conditions(files, self._conds())

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
                        write_text(p, new); count += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            QMessageBox.information(self, "Insert", f"Modified files: {count}")


    class JsonTranslateDock(QDockWidget):
        def __init__(self, parent=None):
            super().__init__("JSON Translate", parent)
            w = QWidget(); self.setWidget(w)
            g = QGridLayout(w)
            g.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit(); self.btn_browse = QPushButton("Browse…")
            g.addWidget(self.ed_path, 0, 1, 1, 3); g.addWidget(self.btn_browse, 0, 4)
            g.addWidget(QLabel("Dictionary file (JSON/TS):"), 1, 0)
            self.ed_dict = QLineEdit(); self.btn_open = QPushButton("Open…")
            g.addWidget(self.ed_dict, 1, 1, 1, 3); g.addWidget(self.btn_open, 1, 4)
            self.btn_run = QPushButton("Run translation"); g.addWidget(self.btn_run, 2, 4)

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
            d = read_translation_dict(dpath)
            changed = 0
            for p in walk_files(path, None, ["node_modules",".git","dist","build"]):
                try:
                    old = read_text(p)
                    new = translate_replace_texts(old, d)
                    if new != old:
                        write_text(p, new); changed += 1
                except Exception as e:
                    print(f"[WARN] {p}: {e}", file=sys.stderr)
            QMessageBox.information(self, "Translate", f"Modified files: {changed}")


    class JsonRewriterDock(QDockWidget):
        def __init__(self, parent=None):
            super().__init__("JSON Rewriter", parent)
            w = QWidget(); self.setWidget(w)
            g = QGridLayout(w)

            g.addWidget(QLabel("Input file:"), 0, 0)
            self.ed_in = QLineEdit(); self.btn_in = QPushButton("Open…")
            g.addWidget(self.ed_in, 0, 1, 1, 3); g.addWidget(self.btn_in, 0, 4)

            g.addWidget(QLabel("Output file (optional):"), 1, 0)
            self.ed_out = QLineEdit(); self.btn_out = QPushButton("Save as…")
            g.addWidget(self.ed_out, 1, 1, 1, 3); g.addWidget(self.btn_out, 1, 4)

            self.chk_from_ts = QCheckBox("From TS/JS (preserve file)")
            self.chk_ts_out = QCheckBox("Emit export default …;")
            self.chk_join = QCheckBox("Join keys")
            self.chk_elim = QCheckBox("Eliminate duplicates")
            self.chk_nlb = QCheckBox("No blank lines")
            g.addWidget(self.chk_from_ts, 2, 0); g.addWidget(self.chk_ts_out, 2, 1)
            g.addWidget(self.chk_join, 2, 2); g.addWidget(self.chk_elim, 2, 3); g.addWidget(self.chk_nlb, 2, 4)

            g.addWidget(QLabel("Indent (<=0 compact):"), 3, 0)
            self.spin_indent = QSpinBox(); self.spin_indent.setRange(-1, 16); self.spin_indent.setValue(2)
            self.btn_run = QPushButton("Rewrite")
            g.addWidget(self.spin_indent, 3, 1); g.addWidget(self.btn_run, 3, 4)

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


    # ------------------------------- Theme helpers --------------------------------

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
        app.setPalette(pal)


    class MainWindow(QMainWindow):
        def __init__(self, app: QApplication):
            super().__init__()
            self.app = app
            self.setWindowTitle("Clarify")

            self.ICON_BASE_64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAD40lEQVR4nO2bv07cMBzHv3HSgzu6sB/qTFk6FfUB+gCor4FUqVIXJCYkhiJVQuI1EN07dKyuLJUQYka6vUt7R6+J3eFwznFsx0ns5HLcd7kj/hN/P/7ZTnw4QIFe7O6zojzLrPu7UWBK1yZ23bgsHQjlRZV5xhiArjAJEAR5ayoImQtq4xSMMTCazCGwJYcQzM0HJJx/BiSXRQQR6WtioJSCJgloEuNhOvPSXl/a7PdAwggkDEEIgW60p1ezvc9AE4oknmE6+eu7rV7VH2wgjHogYRYCjwICrK55AJhO/iKJZ6AJhTiHcc+5AULp6pjnSiFQmksLxN5njCKJY0x+TxptYFMaPB8gjKLMxJiJAMYYaBI33rCmRJP4cTlfKAXAl7plm+3Hp2Nn5R+ms8Vy/ihhGWQ5OiZtX+7j17tRrcbZipsYHg1Ll5G1eKCbrwhESrWqfPtyP/PZlGyjwZhP8mh4EFJLNt1kJADmaKgyXNJVgDGK5N8Mkz8P2symHi+CsP31u77s2zfp97ImhkfD0mV2P71MV4JSAAA1BJ15k2mdbq53rPOKUVAGQi0AQBaCyrzKuNjLZfLLxmwmQlOZwdYmwme9egAA/dgXzYimrw5vlfUcXOwZy4tmqq4CXgCoJDdeZ1onDkOs5+Z6p5RxWePTcTMAeKN5r5c1zyVGhFynC3kBYGNeDnWuoryuIcgA8tslJSVPYLKhg4s9rXldugpKlRXFRrUBcKnGvMm4LDGv+N1l+KtUawiI4VnHfNl71ZHzIaCSa/M+5QVAl1QZgC78ffU+D33Xk+E6AtpuQNtaA2i7AW1rDcBFJeLMX/UlqC1VBuBrWdLJx5sh4GkIdCkKnAGweaMr0tXhbePwagGQh0EdCGJeuZyv8AccRoAJggmEKp3XcXJ27n2O8bIjBNTfEjs5O0+vfX71enl3hAD1ilDlpUhlHgA+/PxRo3Vm5SJg48u3XCZb+rotccB+W5zXozJ9/PG9VTtMKtwUrQMA0D8XVIHoA4IMQPvjqO+9OFG6X4aOkR8OJ2fnTiKBSxsBLgBUmcFV95UhANUjwXoIuIoAGwg291JBAMqDaA2Ai/pcQGhkV9iXXI59rk4B8KHOAZCjoG5UlP4foWWQy6HQuQhwrTWAzF+KUxYrJ8mjAEB9zGTVNPe48EnEhICEbbSpMW32e+lRGq7MEFj1CCBhlPMY3d+N0sdh1QGjsmpqm7ys+oMNkDDMeLy/GwXa5wDT5kbXlJ4bIvkOjoA5CVcHJZcNVtGhKcO5wdU9Nmd5bjAAeZwxSRhiK4pW5uBkJrvq4pM9OivqSR+eFtV1EEXH5/8DsBV3DcmuUHgAAAAASUVORK5CYII="
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
            
            # Central tabs
            tabs = QTabWidget()
            self.search_panel = SearchReplacePanel(self)
            self.insert_panel = InsertPanel(self)
            tabs.addTab(self.search_panel, "Search / Replace")
            tabs.addTab(self.insert_panel, "Insert")
            self.setCentralWidget(tabs)

            # Docks
            self.json_translate = JsonTranslateDock(self); self.addDockWidget(Qt.RightDockWidgetArea, self.json_translate)
            self.json_rewriter = JsonRewriterDock(self); self.addDockWidget(Qt.RightDockWidgetArea, self.json_rewriter)

            # Menu bar
            bar = self.menuBar()

            # File menu
            m_file = bar.addMenu("File")
            act_exit = QAction("Exit", self)
            act_exit.triggered.connect(self.close)
            m_file.addAction(act_exit)
            
            # Themes
            m_theme = bar.addMenu("Themes")
            act_sys = QAction("System", self); act_light = QAction("Light", self); act_dark = QAction("Dark", self)
            act_sys.triggered.connect(lambda: apply_system_theme(self.app))
            act_light.triggered.connect(lambda: apply_light_theme(self.app))
            act_dark.triggered.connect(lambda: apply_dark_theme(self.app))
            m_theme.addAction(act_sys); m_theme.addAction(act_light); m_theme.addAction(act_dark)

            # About as a single action (no dropdown)
            act_about = QAction("About", self)
            def _about():
                QMessageBox.information(self, "About",
                    "Clarify — Character search/replace/insert and JSON organization tool.\n"
                    "Author: Josué Amaral\nVersion/Year: 2025")
            act_about.triggered.connect(_about)
            bar.addAction(act_about)



# ======================================================================================
#                                  ENTRY POINT
# ======================================================================================

def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_arg_parser()
    if not argv:
        # GUI (if available). If PySide6 is missing and no args were given, print help.
        if not _PYSIDE:
            parser.print_help()
            return 0
        app = QApplication(sys.argv)
        win = MainWindow(app)
        win.resize(1200, 800)
        win.show()
        return app.exec()

    # CLI
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help(); return 1
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
