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
    
    MUST HAVE
        TASKS DONE
            [X] implement threads to search files;
            [X] include single files and not only directories;
            [X] replace text from dropdown relative to insert panel;
            [X] solve the following issue "json.decoder.JSONDecodeError: Expecting ':' delimiter: line 4629 column 21 (char 185171)"
            [X] dont override: avoid JSON Translate processing which the translate overrides translate names (e.g.: {t.pages.Prac{t.pages.Navbar.blog}HistoryPage.blank}Lin{t.pages.BlogPage.read});
            [X] ajust the JSON Translate to translate only in a code scope (and don't anymore). The example: 'children: React.React{t.pages.translation.buttons.no}de' is not a text to be translated, when it keep as following like children: React.ReactNode;
            [X] first object variable name: the JSON Translate is not sufficient to cover all algorithm translation problems, since the name t, which is the root, must be specified, where the input parameters can customize the root name.
            [X] add possibility to use regular expression in replacement to don't replace some characters, only what's needs;

        TASKS TO-DO
            [] fix serious problem with the JSON Rewriter, which some data is lost after processing, omitting some keys and values;
            [] add scope in the conditional advanced options in algorithm case, for example, only between brackets;
            [] avoid this behavior: {t.pages.onboarding.navigationHints.skip} if stuck - unanswered = zero {t.pages.PracticeHistoryPage.points};
    SHOULD HAVE
        TASKS DONE
        
        TASKS TO-DO
            [] include the possibility to use the three following checkbox options in the conditional advanced options: case sensitive, match whole word and regular expression;
            [] include search and character lookup in the Insert panel tab for inserting characters with search and lookup instead of defining the line number in which the text should be inserted.
            [] add JSON translation reversal functionality;
            [] add the ability to right-click to open some options in the match panel: copy, copy all, select all, open file, and open all files. When the user click with CTRL or shift buttons pressioned, the application must select all the results which the user select with the mouse;
            [] include saving result from match panel as txt file;
            [] Possibility of placing results in separate files (each iteration) or in a single file;
            [] Ability to insert included and not included ranges in Insert, even when using regular expressions;
            [] Fix the Loading message (only appears L letter);
            [] Put the result quantity on the first line at the match panel;
            [] include the possibility of put the mouse over the result search in the match panel and show the character or word absolute position related with the file size;
            [] include the possibility to change the case from keys words (camelCase, PascalCase, snake_case and kebab-case);
            [] include the possibility to remove a certain JSON sub-structure from a JSON structure bigger;
            [] include progress bar to show the progress of the application processing;
            [] include is file checkbox to JSON translate;
            [] Add a modal screen class to display the loading of each of the features present in the algorithm, and tell me how to make this loading appear in a way that doesn't lock the screen, allowing the user to continue using the application freely. The idea would be to allow the user to see the modal screen and minimize it on the main graphical screen itself, and then maximize it. The user can continue navigating the application and perform parallel processing of other features (for example, with threads), but they cannot perform the same processing with the same feature, which must be locked.
            [] fix the JSON translate reverse (the ChatGPT didn't solved the issue): reverse: make the reverse from JSON translate (where is from text to object) to text from object;
            [] include the possibility to filter extensions (i.e.: .jsx);
            [] adjust 'Emit Export default' option from JSON Translate;
            [] The result from JSON Translate should not contains three slacklashs (\\\) in the output file. Something need to be doing to avoid this issue;
            [] avoid empty values in JSON Extractor output file;
            [] include 'avoid childs keys with the same name' in JSON Extractor output;
            [] add 'not include number keys' option in JSON Extractor;
            [] sort all the results, including JSON Rewriter output;
            [] fix case issue that output have some keys, for example, with pascal-case otherwise camel-case;
            [] fix the following situations: retelllecture: '\'RetellLecture\', \'Retell Lecture\', \'Re-tell Lecture\',',
                answershortquestion: [
                    '\'AnswerShortQuestion\', \'Answer Short Question\','
                ],
                respondtosituation: [
                    '\'RespondToSituation\', \'Respond to a Situation\','
                ],
            [] avoid repeted keys:
            whyItSWrong: [
                'Why it\'s wrong:',
                'Why it\'s wrong:'
            ],
            [] add feature to replace lists for only objects or dictionaries in JSON files with scope restrictions, like only in t.pages;
            [] add feature to interrupt processing while loading results;
            [] include the possibility to list the files with ls or dir parameters with advanced search tools;
            [] Insertion of files and directories in an asynchronous and selectable way, so that it does not matter how many files are selected and in which directories they are.
            [] include query to artificial intelligence without files or directories, only with user text;
            [] identify tags, curle backets, square brackets and parenthesis to avoid errors in JSON Rewriter and to text editor use;
            [] include a advanced search which the user can search with multiple queries separated by new lines with the possibility to use regular expressions. Each line would be a new search query;
            [] remove the following errors: ```typescript and ``` in the output while using IA query;
            [] include search where the word key have count of occurrences, for example, only the keys which have more than 2 occurrences. Use relational operations;
            [] the Interrupt Request in ChatGPT File Processor don't works. Solve this issue.
            [] need to solve the translating issue when the text have parenthesis, example: 'Multiple Choice (Multiple)';
            [] avoid the problem that JSON Translate don't replace the object keys from affect files when removing keys from dictionary, making a keys omision and consequently the 'undefined' error;

    COULD HAVE
        TASKS DONE
        
        TASKS TO-DO
            [] include the ability to open and read files, differentiate scope with different color themes;
            [] Include JSON editors as tabs;
            [] add new panel called 'Smart file editing - AI'
            [] include the ability to connect to Google Translate;
            [] include Gemini in the list of artificial intelligences to be used;
            [] add conditional advanced options also in the Smart file editing - AI panel;
            [] Include all Search/Replace and Insert features in Smart Edit File (AI) and in JSON editors;
            [] make the possibility the changes made only in text editor from own clarify app, and don't more in files;
            [] add the feature which the result can be reused on clarify text edit;
            [] possibility search for JSON keys and values with the following example: t.auth.brandTitle;
            [] include 'is file' in other places to take more files with directory paths;
            [] add new feature to insert new keys and values in existing keys with regular expression and memory register concept; 
            [] include the possibility to insert a new value in group mode, which word keys can be used to insert the new value between these word keys, in separated line (new line) or in a specific column. The user could enter the occurrences count tolerated to allow the insert (threshold);
            [] add the possibility to rewrite the JSON replacing the key and object in other places if the value of the key is the same and the keys have different.
            [] Allow the user to choose className names instead of tag names to make the JSON keys; The user can choose get only the difference between the className names for this occasion;
 
    WOULD HAVE LATER
        TASKS DONE
        
        TASKS TO-DO
            [] include 'clear all conditions' button in conditional advanced options;
            [] add scroll in 'search/replace' and 'insert' panels;
            [] including activity history like Google Translate feature;
            [] include the possibility of adding a new line of conditional advanced options, with a minimum of 3 and no maximum limit.
            [] provide the ability to change the application's appearance to a transparent background;
            [] change the insert text, query and replacement text boxes to a text box that can be resized by the user;
            [] add the options to undo and redo the changes made;
            [] Translate the application into the world's most spoken languages;
            [] Calculator: Add calculator concepts such as memory register, addition, concatenation, and standard memory recall with modification history.
            [] Set: Add logical set operations from file j1 such as intersection, difference, union, and exclusive difference. Include checkboxs to include keys and/or values in this set operation;
            [] Include usage tutorials;
            [] Include search with artificial intelligence help;
            [] Embed a virtual assistant for use with AI;
            [] Include AI usage fee of 50% more than the actual amount for my account + 1% to remain in the cash bank, as the user must make the payment using AI, totaling around 151% of the actual amount to be paid. Inform the user that they pay in tokens;
            [] Research the possibility of embedding Clarify in the Linux application manager and how much you earn by doing so. Once installed, compile the code before sending;
            [] Add user data backup for undo and redo with ECC, or, whether or not, use Gof command architecture;
            [] add data backup with command arquitecture, with Egg Cell Compactor and artificial intelligence to store all the changes made by the user even for a long period of time;
            [] Allow user to make macros and algorithms with the application features for more complex utilities, with Python code or block programming;
            [] When the user click in a search result or in a insert result, the application could have to open the file in a own file editor;
            [] Make the Clarify able to create algorithms to perform some user tasks, and not only, also compile or an translate to a programming language (like Python, React and Javascript)
"""

from __future__ import annotations
import argparse
from base64 import b64decode
import configparser
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
    from PySide6.QtCore import (
        Qt, QAbstractTableModel, QModelIndex, QSize, QTimer, Signal, QByteArray, QAbstractListModel, QModelIndex, QObject, Signal, QThread
        )
    from PySide6.QtGui import QAction, QFontDatabase, QPixmap, QIcon, QPalette, QColor
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QCheckBox, QPushButton, QSplitter, QListWidget, QListWidgetItem,
        QFileDialog, QGroupBox, QComboBox, QSpinBox, QTreeWidget, QTreeWidgetItem,
        QPlainTextEdit, QDockWidget, QMessageBox, QTabWidget, QFormLayout, QListView
    )
except Exception:
    _PYSIDE = False
    print("ERROR: PYSIDE is not installed!")


# =============================================================================
#                          FILE DISCOVERY & UTILITIES
# =============================================================================

def sanitize_keys_and_values(obj: dict,
                             allow_numeric_keys: bool = False,
                             strip_leading_numeric_segment: bool = True,
                             drop_empty_values: bool = True) -> dict:
    """
    - If drop_empty_values: remove entries whose value is '' (or whitespace-only).
    - If not allow_numeric_keys:
        • For keys like '1.abcd' → keep only 'abcd' (strip leading digits + dots).
        • For keys like '1234'   → drop the entire key.
    Applies recursively.
    """
    def clean_key(k: str) -> Optional[str]:
        if allow_numeric_keys:
            return k
        if re.fullmatch(r'\d+', k):
            return None  # drop pure-numeric key
        if strip_leading_numeric_segment and re.match(r'^\d+(\.|_)+', k):
            # remove leading digits and separators like "123." or "123_"
            k2 = re.sub(r'^\d+(?:[._])+', '', k)
            return k2 or None
        return k

    def walk(v):
        if isinstance(v, dict):
            out = {}
            for k, x in v.items():
                nk = clean_key(k)
                if nk is None:
                    continue
                vx = walk(x)
                # empty-value culling for strings
                if drop_empty_values and isinstance(vx, str) and not vx.strip():
                    continue
                out[nk] = vx
            return out
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v

    return walk(obj)

_TS_EXPORT_RE = re.compile(r'^\s*export\s+default\s*', re.IGNORECASE)

def _strip_export_default(src: str) -> str:
    # remove a leading `export default` (if present)
    return _TS_EXPORT_RE.sub("", src, count=1).strip()

def _to_json_ish(src: str) -> str:
    """
    Convert a TS object literal into valid JSON:
      - Ensure keys are quoted
      - Convert single-quoted strings → double-quoted
      - Remove trailing commas
      - Remove optional semicolon at end
    This is not a full JS parser, but works for object/array/string/number/bool/null.
    """
    s = _strip_export_default(src)
    # Drop outer semicolon
    s = re.sub(r';\s*$', '', s)
    # Quote bare keys:  foo: → "foo":
    s = re.sub(r'(?m)(^|[{,\s])([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', s)
    # Convert single-quoted strings to JSON double-quoted (handle escaped \')
    def _s2d(m):
        inner = m.group(1).replace(r'\"', '"')  # normalize weird mixed cases
        inner = inner.replace(r"\\'", r"\u0027")  # protect escaped single quote
        inner = inner.replace("'", r"\u0027")     # raw single quote → \u0027
        return '"' + inner + '"'
    s = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", _s2d, s, flags=re.DOTALL)
    # Remove trailing commas in objects/arrays
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    return s

def load_ts_object(text: str) -> dict:
    """
    Parse a TS/JS object (`export default { ... }` or `{ ... }`) to dict safely.
    """
    js = _to_json_ish(text)
    return json.loads(js)

# TS stringifier using single quotes with *minimal* escaping
def _esc_ts(s: str) -> str:
    # Only escape backslash and single quote; leave double quotes alone
    return s.replace('\\', '\\\\').replace("'", "\\'")

def dump_ts_object(obj: dict, emit_export_default: bool = True, indent: int = 2) -> str:
    """
    Deterministic pretty TS object: single-quoted strings, sorted keys, optional export default.
    """
    def _dump(v, lvl=0):
        sp = ' ' * (indent * lvl)
        if v is None:
            return 'null'
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str):
            return "'" + _esc_ts(v) + "'"
        if isinstance(v, list):
            inner = ',\n'.join(sp + ' ' * indent + _dump(x, lvl + 1) for x in v)
            return '[\n' + inner + '\n' + sp + ']'
        if isinstance(v, dict):
            # stable order
            items = []
            for k in sorted(v.keys()):
                kk = k if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', k) else "'" + _esc_ts(k) + "'"
                items.append(sp + ' ' * indent + f"{kk}: " + _dump(v[k], lvl + 1))
            return '{\n' + ',\n'.join(items) + '\n' + sp + '}'
        # Fallback: stringify
        return "'" + _esc_ts(str(v)) + "'"

    body = _dump(obj, 0)
    return (f"export default {body}\n" if emit_export_default else body + "\n")

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


# ---------- Exclusion masking (skip-regex) ----------

def parse_exclusion_patterns(csv_regex: str) -> list[str]:
    """Split a comma-separated regex list into individual non-empty patterns."""
    if not csv_regex.strip():
        return []
    return [p.strip() for p in csv_regex.split(",") if p.strip()]

def mask_exclusions(text: str, patterns: list[str]) -> tuple[str, list[str]]:
    """
    Replace each region matched by any exclusion regex with a guard token @@XCL{n}@@.
    Returns (masked_text, guards) where guards[i] is the original match.
    """
    if not patterns:
        return text, []

    # We will apply patterns sequentially, accumulating guards.
    guards: list[str] = []
    token_prefix = "@@XCL"
    token_suffix = "@@"

    # To avoid nested index drift, we replace using re.sub with a function, per pattern, per pass.
    def _make_replacer(pat: str):
        rx = re.compile(pat, flags=re.DOTALL | re.MULTILINE)
        def _repl(m: re.Match) -> str:
            idx = len(guards)
            guards.append(m.group(0))
            return f"{token_prefix}{idx}{token_suffix}"
        return rx, _repl

    masked = text
    for pat in patterns:
        rx, repl = _make_replacer(pat)
        masked = rx.sub(repl, masked)
    return masked, guards

def unmask_exclusions(text: str, guards: list[str]) -> str:
    token_prefix = "@@XCL"
    token_suffix = "@@"
    for i, original in enumerate(guards):
        text = text.replace(f"{token_prefix}{i}{token_suffix}", original)
    return text

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


def safe_backup_file(path: str) -> None:
    """Create path.bak once. If already exists, do not overwrite."""
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

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


# def filter_files_by_conditions(files: Iterable[str], conds: Sequence[Condition]) -> List[str]:
#     conds = list(conds or [])
#     if not conds:
#         return list(files)
#     out = []
#     for p in files:
#         if all(c.matches(p) for c in conds):
#             out.append(p)
#     return out

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

# =============================================================================
#                              INSERT TEXT ENGINE
# =============================================================================

class InsertMode:
    LEFT = "Insert left of line"               # prepend to the existing line text
    RIGHT = "Insert right of line"             # append to the existing line text
    REPLACE = "Replace line content"         # replace the line content with the text
    INSERT_ABOVE = "Push line down and insert above"  # insert a new line above with the text (pushes current down)
    INSERT_BELOW = "Insert on next line (push rest)"  # insert a new line below with the text (keeps current)


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

    # Parse while preserving duplicate keys structure
    data = parse_json_preserving_duplicates_text(json_text)

    # 1) Sanitize keys/values to avoid empty texts and numeric-only keys
    #    (keeps the shape a normal *tree*, not a value→keys map)
    data = sanitize_keys_and_values(
        data,
        allow_numeric_keys=False,                  # change to True if you want to allow numeric keys
        strip_leading_numeric_segment=True,
        drop_empty_values=True
    )

    # 2) De-duplication options still return a normal tree (Obj / list / scalars)
    result = join_keys(data) if join else dedupe(data)
    if elim:
        result = eliminate_duplicates(result)

    # 3) Emit a regular TS object (no double escaping; single-quoted strings)
    ts_block = dump_ts_node(result, indent, 0)
    return raw_full[:start] + ts_block + raw_full[end:]


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

class SearchWorker(QObject):
    # Emite progresso opcional (ex: caminho do arquivo atual)
    progress = Signal(str)
    # Emite o resultado final (dict de matches)
    done = Signal(dict)
    # Emite erros (se quiser mostrar)
    error = Signal(str)

    def __init__(self, pattern_text: str, iter_files_fn, search_options_factory):
        super().__init__()
        self.pattern_text = pattern_text
        self.iter_files_fn = iter_files_fn
        self.search_options_factory = search_options_factory
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        """Executa o processamento pesado fora da GUI thread."""
        
        matches: Dict[str, List[Tuple[int, int, str]]] = {}
        for p in self.iter_files_fn():
            if self._cancel:
                break
            try:
                self.progress.emit(p)  # opcional
                text = read_text(p)
                lst: List[Tuple[int, int, str]] = []
                for m in self.pattern_text.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                    snippet = text.splitlines()[line - 1] if line - 1 < len(text.splitlines()) else ""
                    lst.append((line, col, snippet))
                if lst:
                    matches[p] = lst
            except Exception as e:
                self.error.emit(f"[WARN] {p}: {e}")
                # continua para próximos arquivos
        self.done.emit(matches)


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
            self.setUpdatesEnabled(False)
            try:
                self.clear()
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
                top = QTreeWidgetItem(f"{message}")
                self.addTopLevelItem(top)
                self.expandAll()
            finally:
                self.setUpdatesEnabled(True)


    class SearchReplacePanel(QWidget):
        """
        Left-hand panel: path + include/exclude + search & replace controls.
        Right-hand panel: results.
        """
        request_preview = Signal(dict)   # emits {"matches": {path: [(line,col,snip), ...], ...}}

        def __init__(self, parent=None):
            super().__init__(parent)
            root = QVBoxLayout(self)
            self.processing_search = False
            
            # Path row
            column = QVBoxLayout()
            row = QHBoxLayout()
            row.addWidget(QLabel("Root path:"))
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            row.addWidget(self.ed_path, 1)
            row.addWidget(self.btn_browse)
            column.addLayout(row)
            self.is_file = QCheckBox("Is File?")
            column.addWidget(self.is_file)
            root.addLayout(column)

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
            self.btn_search = QPushButton("Search/Cancel")
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
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
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
            
        def _conds(self) -> List[Condition]:
            out: List[Condition] = []
            if not self.is_file.isChecked():
                for cb_field, cb_op, ed in self.cond_list:
                    f = cb_field.currentText().strip()
                    o = cb_op.currentText().strip()
                    v = ed.text().strip()
                    if f and o and v:
                        out.append(Condition(f, o, v))
            return out
        
        def _iter_files(self) -> List[str]:
            path = self.ed_path.text().strip()
            ed_inc_text = "*.*"
            if self.ed_inc.text():
                ed_inc_text = self.ed_inc.text()
                
            inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            return filter_files_by_conditions(files, self._conds())

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
        
        def enable_buttons(self, state, include_buttons=True, include_advanced_conditions = True):
            if include_buttons:
                self.btn_browse.setEnabled(state)
                self.btn_replace_one.setEnabled(state)
                self.btn_replace_all.setEnabled(state)
            
            if include_advanced_conditions:
                for cb_field, cb_op, ed in self.cond_list:
                    cb_field.setEnabled(state)
                    cb_op.setEnabled(state)
                    ed.setEnabled(state)
                    ed.setReadOnly(not state)
        
        def _start_search_threaded(self):
            if not self.processing_search:
                self.results.print_message("Loading...")
                
                try:
                    # compile o padrão
                    pattern_text = SearchOptions(self.chk_case.isChecked(),
                        self.chk_word.isChecked(),
                        self.chk_regex.isChecked()).compile(self.ed_query.text())
                except Exception as e:
                    self.error.emit(f"Invalid pattern: {e}")
                    self.done.emit({})
                    return
                
                # Cria a thread e o worker
                self._search_thread = QThread(self)
                self._search_worker = SearchWorker(
                    pattern_text=pattern_text,
                    iter_files_fn=self._iter_files,                 # sua função existente
                    search_options_factory=lambda a,b,c: SearchOptions(a,b,c)  # sua classe existente
                )
                self._search_worker.moveToThread(self._search_thread)

                # Conexões: quando a thread começar, chama worker.run
                self._search_thread.started.connect(self._search_worker.run)

                # Resultados / erros -> atualizam UI (na thread da GUI!)
                self._search_worker.done.connect(self._on_search_done)
                self._search_worker.progress.connect(self._on_search_progress)  # opcional
                self._search_worker.error.connect(self._on_search_error)        # opcional

                # Limpeza
                self._search_worker.done.connect(self._search_thread.quit)
                self._search_worker.done.connect(self._search_worker.deleteLater)
                self._search_thread.finished.connect(self._search_thread.deleteLater)

                # Desabilita botões enquanto busca, se desejar
                # self.btn_search.setEnabled(False)

                self._search_thread.start()
                self.enable_buttons(False)
                self.processing_search = True
            else:
                self._search_worker.cancel()
                self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
                self.processing_search = False

        def _on_search_progress(self, current_path: str):
            # opcional: atualizar um label/statusbar, sem travar
            #self.statusBar().showMessage(f"Scanning: {current_path}")
            pass

        def _on_search_error(self, msg: str):
            # opcional: log ou snackbar
            print(msg)

        def _on_search_done(self, matches: dict):
            # Agora você pode atualizar widgets com segurança
            self.results.populate(matches)       # seu método existente
            self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)   # reabilita se tiver desabilitado
            self.processing_search = False

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

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QGridLayout(self)
            self.processing_search = False
            
            layout.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            layout.addWidget(self.ed_path, 0, 1, 1, 3)
            layout.addWidget(self.btn_browse, 0, 4)
            
            self.is_file = QCheckBox("Is File?")
            layout.addWidget(self.is_file, 1, 0)
            
            layout.addWidget(QLabel("Include globs:"), 2, 0)
            self.ed_inc = QLineEdit("*.ts;*.tsx;*.js;*.jsx;*.py;*.md")
            layout.addWidget(self.ed_inc, 2, 1, 1, 4)

            layout.addWidget(QLabel("Exclude globs:"), 3, 0)
            self.ed_exc = QLineEdit("node_modules;dist;build;.git")
            layout.addWidget(self.ed_exc, 3, 1, 1, 4)

            layout.addWidget(QLabel("Line number (1-based):"), 4, 0)
            self.spin_line = QSpinBox(); self.spin_line.setRange(1, 10_000_000); self.spin_line.setValue(1)
            layout.addWidget(self.spin_line, 4, 1)

            layout.addWidget(QLabel("Insert text:"), 5, 0)
            self.ed_text = QPlainTextEdit()
            layout.addWidget(self.ed_text, 5, 1, 1, 4)

            layout.addWidget(QLabel("Mode:"), 6, 0)
            self.cb_mode = QComboBox()
            self.cb_mode.addItems([InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE,
                                   InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW])
            layout.addWidget(self.cb_mode, 6, 1)

            self._debounce_timer = QTimer(self)
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.setInterval(300)
            self._debounce_timer.timeout.connect(self._start_search_threaded)
            
            # Advanced conditions (same as Search/Replace, including `content`)
            gb3 = QGroupBox("Advanced conditions (folder mode)")
            g3 = QGridLayout(gb3)
            self.cond_list: List[Tuple[QComboBox, QComboBox, QLineEdit]] = []
            for row_i in range(3):
                cb_field = QComboBox(); cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
                cb_field.currentTextChanged.connect(self._schedule_live_refresh)
                cb_op = QComboBox(); cb_op.addItems(["", "contains", "not contains", "equals", "not equals",
                                                     "starts with", "ends with", ">", "<", ">=", "<="])
                cb_op.currentTextChanged.connect(self._schedule_live_refresh)
                ed_val = QLineEdit()
                ed_val.textChanged.connect(self._schedule_live_refresh)
                g3.addWidget(cb_field, row_i, 0); g3.addWidget(cb_op, row_i, 1); g3.addWidget(ed_val, row_i, 2, 1, 2)
                self.cond_list.append((cb_field, cb_op, ed_val))
            layout.addWidget(gb3,7, 0, 1, 5)
            
            self.btn_apply = QPushButton("Apply to files")
            layout.addWidget(self.btn_apply, 8, 4)

            # Results on the right
            self.results = ResultsTree()
            
            splitter = QSplitter()
            left = QWidget(); left.setLayout(layout)
            splitter.addWidget(left)
            splitter.addWidget(self.results)
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
        
        def _conds(self) -> List[Condition]:
            out: List[Condition] = []
            if not self.is_file.isChecked():
                for cb_field, cb_op, ed in self.cond_list:
                    f = cb_field.currentText().strip()
                    o = cb_op.currentText().strip()
                    v = ed.text().strip()
                    if f and o and v:
                        out.append(Condition(f, o, v))
            return out
        
        def enable_buttons(self,state, include_buttons=True, include_advanced_conditions = True):
            if include_buttons:
                self.btn_browse.setEnabled(state)
                
            if include_advanced_conditions:
                for cb_field, cb_op, ed in self.cond_list:
                    cb_field.setEnabled(state)
                    cb_op.setEnabled(state)
                    ed.setEnabled(state)
                    ed.setReadOnly(not state)
            
        def reset_advanced_conditions(self):
            for cb_field, cb_op, ed in self.cond_list:
                cb_field.clear()
                cb_op.setCurrentIndex(0)
                ed.setCurrentIndex(0)
        
        def _iter_files(self) -> List[str]:
            path = self.ed_path.text().strip()
            inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
            exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
            files = list(walk_files(path, inc, exc))
            return filter_files_by_conditions(files, self._conds())

        def _schedule_live_refresh(self):
            if not self._conds():  # só dispara se há pelo menos 1 regra válida
                return
            # Só faça live preview quando o path é diretório:
            p = self.ed_path.text().strip()
            if not p or os.path.isfile(p):
                return
            self._debounce_timer.start()
        
        def _start_search_threaded(self):
            if not self.processing_search:
                words = "|".join([ed.text().strip() for k, n, ed in self.cond_list if ed.text().strip()])
                if words:
                    self.results.print_message("Loading...")
                    # if self.is_file.isChecked():
                    #     self.reset_advanced_conditions()
                    try:
                        # compile o padrão
                        pattern_text = SearchOptions(False, False, True).compile(rf"(?:{words})")
                    except Exception as e:
                        self.error.emit(f"Invalid pattern: {e}")
                        self.done.emit({})
                        return
                    
                    # Cria a thread e o worker
                    self._search_thread = QThread(self)
                    self._search_worker = SearchWorker(
                        pattern_text=pattern_text,
                        iter_files_fn=self._iter_files,                 # sua função existente
                        search_options_factory=lambda a,b,c: SearchOptions(a,b,c)  # sua classe existente
                    )
                    self._search_worker.moveToThread(self._search_thread)

                    # Conexões: quando a thread começar, chama worker.run
                    self._search_thread.started.connect(self._search_worker.run)

                    # Resultados / erros -> atualizam UI (na thread da GUI!)
                    self._search_worker.done.connect(self._on_search_done)
                    self._search_worker.progress.connect(self._on_search_progress)  # opcional
                    self._search_worker.error.connect(self._on_search_error)        # opcional

                    # Limpeza
                    self._search_worker.done.connect(self._search_thread.quit)
                    self._search_worker.done.connect(self._search_worker.deleteLater)
                    self._search_thread.finished.connect(self._search_thread.deleteLater)

                    # Desabilita botões enquanto busca, se desejar
                    # self.btn_search.setEnabled(False)

                    self._search_thread.start()
                    self.enable_buttons(False)
                    self.processing_search = True
            else:
                self._search_worker.cancel()
                self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
                self.processing_search = False

        def _on_search_progress(self, current_path: str):
            # opcional: atualizar um label/statusbar, sem travar
            #self.statusBar().showMessage(f"Scanning: {current_path}")
            pass

        def _on_search_error(self, msg: str):
            # opcional: log ou snackbar
            print(msg)

        def _on_search_done(self, matches: dict):
            # Agora você pode atualizar widgets com segurança
            self.results.populate(matches)       # seu método existente
            self.enable_buttons(True, include_advanced_conditions = True if not self.is_file.isChecked() else False)
            self.processing_search = False
        
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
            self._start_search_threaded()

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
    
    # =============================== JSON Translate Dock ===============================

    class JsonTranslateDock(QDockWidget):
        def __init__(self, parent=None):
            super().__init__("JSON Translate", parent)
            w = QWidget(); self.setWidget(w)
            g = QGridLayout(w)

            g.addWidget(QLabel("Root path:"), 0, 0)
            self.ed_path = QLineEdit()
            self.btn_browse = QPushButton("Browse…")
            g.addWidget(self.ed_path, 0, 1, 1, 2)
            g.addWidget(self.btn_browse, 0, 3)
            
            self.is_file = QCheckBox("Is file?")
            g.addWidget(self.is_file,1,0)

            g.addWidget(QLabel("Dictionary file (JSON/TS):"), 2, 0)
            self.ed_dict = QLineEdit()
            self.btn_open = QPushButton("Open…")
            g.addWidget(self.ed_dict, 2, 1, 1, 2)
            g.addWidget(self.btn_open, 2, 3)

            g.addWidget(QLabel("First object variable name:"), 3, 0)
            self.object_variable_name = QLineEdit()
            self.object_variable_name.setPlaceholderText("e.g. t")
            g.addWidget(self.object_variable_name, 3, 1, 1, 2)

            # Generic delimiters as scope limits (regex)
            g.addWidget(QLabel("Start delimiter (regex):"), 4, 0)
            self.ed_start = QLineEdit("<[^>]*?>")  # default: start of an HTML/JSX tag
            g.addWidget(self.ed_start, 4, 1)
            g.addWidget(QLabel("End delimiter (regex):"), 4, 2)
            self.ed_end = QLineEdit("</[^>]*?>")   # default: end tag
            g.addWidget(self.ed_end, 4, 3)

            # "Do not translate" regex patterns (comma-separated)
            g.addWidget(QLabel('Do not translate\n(regex, comma-separated):'), 5, 0)
            self.ed_exclude = QLineEdit()
            self.ed_exclude.setPlaceholderText(r'className="[^"]*", data-testid="[^"]*", id="[^"]*"')
            g.addWidget(self.ed_exclude, 5, 1, 1, 3)

            
            self.chk_backup = QCheckBox("Backup original files\n(filename.bak)")
            self.chk_backup.setChecked(True)
            g.addWidget(self.chk_backup, 6, 0, 1, 2)

            self.chk_dont_override = QCheckBox("Don't override\nexisting translations")
            self.chk_dont_override.setChecked(True)
            g.addWidget(self.chk_dont_override, 6, 2, 1, 2)

            self.chk_inverse_json_translate = QCheckBox(
                "Reverse JSON Translate\nchanges (with dictionary)"
            )
            g.addWidget(self.chk_inverse_json_translate, 7, 0, 1, 2)

            self.btn_run = QPushButton("Run translation")
            g.addWidget(self.btn_run, 7, 2, 1, 2)
            
            self.btn_browse.clicked.connect(self._browse_root)
            self.btn_open.clicked.connect(self._browse_dict)
            self.btn_run.clicked.connect(self._run)

        # ------ UI helpers ------

        def _browse_root(self):
            # Let user pick file or directory
            if self.is_file.isChecked():
                path, _ = QFileDialog.getOpenFileName(self, "Select file (or Cancel to pick a folder)")
                if path:
                    self.ed_path.setText(path)
            else:
                folder = QFileDialog.getExistingDirectory(self, "Select folder")
                if folder:
                    self.ed_path.setText(folder)

        def _browse_dict(self):
            path, _ = QFileDialog.getOpenFileName(
                self, "Dictionary file", "", "JSON/TS (*.json *.ts *.js);;All files (*)"
            )
            if path:
                self.ed_dict.setText(path)

        # ------ Core run ------

        # def _run(self):
        #     root = self.ed_path.text().strip()
        #     dict_path = self.ed_dict.text().strip()
        #     alias = (self.object_variable_name.text().strip() or "t")
        #     start_rx = self.ed_start.text().strip()
        #     end_rx = self.ed_end.text().strip()
        #     make_backup = self.chk_backup.isChecked()
        #     dont_override = self.chk_dont_override.isChecked()
        #     inverse = self.chk_inverse_json_translate.isChecked()
        #     exclude_csv = self.ed_exclude.text().strip()
        #     exclude_patterns = parse_exclusion_patterns(exclude_csv)

        #     if not root or not dict_path:
        #         QMessageBox.information(self, "JSON Translate", "Fill Root path and Dictionary file.")
        #         return
        #     try:
        #         dictionary = load_translation_dict(dict_path)
        #     except Exception as e:
        #         QMessageBox.critical(self, "Dictionary", f"Failed to load dictionary:\n{e}")
        #         return

        #     # Gather input files (file or folder)
        #     includes = ["*.ts", "*.tsx", "*.js", "*.jsx", "*.json", "*.*"]
        #     if os.path.isfile(root):
        #         paths = [root]
        #     else:
        #         paths = list(walk_files(root, includes, []))

        #     if not paths:
        #         QMessageBox.information(self, "JSON Translate", "No files found to process.")
        #         return

        #     changed = 0
        #     errors: list[str] = []
        #     for p in paths:
        #         ok, err = process_translate_file(
        #             p, dictionary, alias, start_rx, end_rx,
        #             make_backup, dont_override, inverse, exclude_patterns
        #         )
        #         if ok: changed += 1
        #         if err: errors.append(f"{p}: {err}")

        #     msg = f"Processed: {len(paths)} file(s)\nChanged: {changed}"
        #     if errors:
        #         msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:10])
        #         if len(errors) > 10:
        #             msg += f"\n... and {len(errors)-10} more."
        #     QMessageBox.information(self, "JSON Translate", msg)
        
        def _run(self):
            path = self.ed_path.text().strip()
            dpath = self.ed_dict.text().strip()
            root_alias = (self.object_variable_name.text().strip() or "t")
            start_rx = self.ed_start.text().strip()
            end_rx = self.ed_end.text().strip()
            exclude_csv = self.ed_exclude.text().strip()
            make_backup = self.chk_backup.isChecked()
            dont_override = self.chk_dont_override.isChecked()
            inverse = self.chk_inverse_json_translate.isChecked()

            if not path or not dpath:
                QMessageBox.warning(self, "Missing", "Select path and dictionary file.")
                return

            try:
                dictionary = load_translation_dict(dpath)
            except Exception as e:
                QMessageBox.critical(self, "Dictionary error", str(e))
                return

            exclude_patterns = parse_exclusion_patterns(exclude_csv)

            changed = 0
            errors = []

            # single file or folder
            paths = [path] if os.path.isfile(path) else list(
                walk_files(path, include_globs=None, exclude_globs=["node_modules",".git","dist","build"])
            )

            for p in paths:
                ok, err = process_translate_file(
                    p, dictionary, root_alias,
                    start_rx, end_rx,
                    make_backup, dont_override, inverse,
                    exclude_patterns,
                )
                if ok:
                    changed += 1
                if err:
                    errors.append(f"{p}: {err}")

            msg = f"Modified files: {changed}"
            if errors:
                msg += f"\nErrors: {len(errors)}\n" + "\n".join(errors[:5])  # show a few
            QMessageBox.information(self, "Translate", msg)



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
        def __init__(self, app: QApplication):
            super().__init__()
            self.app = app
            self.setWindowTitle("Clarify - JSON file management system")
            #self.resize(1080, 720)
            
            self._build_icon()
            self._build_ui()
            self._build_menu()
            self._restore_prefs()
            
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
                                    "Clarify\n\nJSON file management system\nPurpose: search, replace, insert and JSON utilities.\n"
                                    "Author: Josué Amaral\nVersion and year: 2025")

        def _build_ui(self):
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)

            self.tab_search = SearchReplacePanel()
            self.tab_insert = InsertPanel()

            self.tabs.addTab(self.tab_search, "Search / Replace")
            self.tabs.addTab(self.tab_insert, "Insert")

            # Docks (Tools menu toggles them)
            self._open_trans()
            self._open_rewrite()
        
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
