#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_param_to_json.py

CLI + GUI (PySide6) tool to scan files or directories, extract an attribute/parameter
(e.g., JSX prop `label`), build a hierarchical path, optionally include the key and
a normalized value token in the path, optionally drop standard HTML tags, and
(optionally) emit a nested JSON object that reflects the path.

Supports:
- JSX mode (parses <Tag ...> ... </Tag> and self-closing tags).
- Generic mode with user-provided scope delimiters via regex (start and end).

Normalization:
- case styles: snake_case, camelCase, PascalCase, kebab-case
- uppercase option
- limit (int or "all"); avoid-cut option to stop at word boundary.

GUI:
- Fields for all options; preview output and save.

No external deps besides PySide6 (for GUI).

[X] When no parameters are provided, any parameter is accepted;
[X] There should be a checkbox indicating whether the parameter is a tag or not. If it is a tag, only the content within the tag scope should be extracted. The checkbox can be "is tag parameters?";
[X] Include the desired or expected value data type or create 'only string' option, which only accept the inclusion whether the text is involved between quotation marks or apostrophes (in only tag parameters mode) or the content between a start and end tags don't have curled brackets, objects or variables, only literal text (in only tag content mode);
[X] When no have parameters, create a algorithm that reacts with 'add value' and 'add key' options. The method needs to remove each hierarchy from dict with a numeric parameter, including negative numeric values.
[X] Modify algorithm to appear 'AuthGuard' in the result;
[X] Fix the paths panel output;
[X] Reuse the context menu from other software in old;
[] include execution code with ENTER;
[] include search to find some text in the result panel;
[] fix the parser method from GenericScopeParser class;


"""

import os
import re
import sys
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple, Iterable, Union

# ----------------------------- Utilities -------------------------------------

JSONLike = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

STANDARD_HTML_TAGS = {
    'html','head','title','base','link','meta','style','script','noscript',
    'body','section','nav','article','aside','h1','h2','h3','h4','h5','h6','header',
    'footer','address','main','p','hr','pre','blockquote','ol','ul','li','dl','dt','dd',
    'figure','figcaption','div','a','em','strong','small','s','cite','q','dfn','abbr','ruby',
    'rb','rt','rtc','rp','data','time','code','var','samp','kbd','sub','sup','i','b','u',
    'mark','bdi','bdo','span','br','wbr','ins','del','picture','source','img','iframe',
    'embed','object','param','video','audio','track','map','area','table','caption',
    'colgroup','col','tbody','thead','tfoot','tr','td','th','form','label','input',
    'button','select','datalist','optgroup','option','textarea','output','progress',
    'meter','fieldset','legend','details','summary','dialog','slot','template','canvas'
}

def is_standard_tag(name: str) -> bool:
    return name.lower() in STANDARD_HTML_TAGS

def kept_prefix(file_root: str, stack: list[str], drop_standard: bool) -> list[str]:
    """
    Return [file_root] plus the stack up to the deepest NON-standard tag
    (when drop_standard=True). If none exists, just [file_root].
    If drop_standard=False, return [file_root] + full stack.
    """
    #print(f"drop_standard: {drop_standard}, stack: {stack}")
    if not drop_standard:
        
        return [file_root] + stack

    # find deepest custom tag from right to left
    for i in range(len(stack) - 1, -1, -1):
        #print(f"stack[{i}]: {stack[i]}, not is_standard_tag({stack[i]}): {not is_standard_tag(stack[i])}")
        if not is_standard_tag(stack[i]):
            return [file_root] + stack[:i + 1]
    return [file_root]


def smart_truncate(text: str, limit: Optional[str], avoid_cut: bool) -> str:
    """
    Truncate text by char limit. If limit is 'all' or None -> return original.
    If avoid_cut=True, cut at the last whitespace boundary <= limit (when possible).
    """
    if not text or limit in (None, 'all', 'ALL', 'All'):
        return text
    try:
        n = int(limit)
    except Exception:
        return text

    if n <= 0 or len(text) <= n:
        return text

    sub = text[:n]

    if not avoid_cut:
        return sub

    # If we ended already on whitespace, just strip trailing whitespace.
    if sub[-1].isspace():
        return sub.rstrip()

    # Find the last whitespace run before the cut and cut right before it.
    # This matches from the last whitespace up to the end of `sub`.
    m = re.search(r'\s+\S*$', sub, flags=re.UNICODE)
    if m:
        cut = m.start()
        if cut > 0:
            return sub[:cut].rstrip()

    # Fallback: no whitespace found in the window (a very long first word).
    return sub


def normalize_token(s: str, case_style: str, to_upper: bool) -> str:
    """
    Normalize a string to snake/camel/pascal/kebab; drop non-alnum (after spaces);
    optionally uppercase whole token.
    Steps:
    - Lowercase for snake/kebab; for camel/pascal, lowercase then apply.
    - Replace non-letter/digit with space; split words; rebuild.
    """
    # remove quotes around e.g. "Today's Practice" if present (we get raw value text usually)
    s = s.strip()
    # Convert any non-alphanumeric into space (keep letters/digits only)
    # But keep apostrophes to allow "today's" joining; we'll drop them before final build.
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", s)
    words = [w for w in cleaned.strip().split() if w]
    if not words:
        token = ""
    else:
        if case_style == "snake":
            token = "_".join(w.lower() for w in words)
        elif case_style == "kebab":
            token = "-".join(w.lower() for w in words)
        elif case_style == "camel":
            head = words[0].lower()
            tail = [w[:1].upper() + w[1:].lower() for w in words[1:]]
            token = head + "".join(tail)
        elif case_style == "pascal":
            token = "".join(w[:1].upper() + w[1:].lower() for w in words)
        else:
            # default snake
            token = "_".join(w.lower() for w in words)
    if to_upper:
        token = token.upper()
    return token

def path_join(parts: List[str]) -> str:
    return ".".join([p for p in parts if p])

def insert_nested(d: Dict[str, Any], keys: List[str], leaf_value: Any) -> None:
    """
    Insert a value into nested dict creating intermediate dicts as needed.
    If an existing leaf is a dict and we set a value, we keep merging.
    """
    #print(f"d: {d}, keys: {keys}, leaf_value: {leaf_value}")
    curr = d
    for k in keys[:-1]:
        if k not in curr or not isinstance(curr[k], dict):
            curr[k] = {}
        curr = curr[k]
    last = keys[-1] if keys else None
    if last is None:
        return
    if last in curr and isinstance(curr[last], dict) and isinstance(leaf_value, dict):
        curr[last].update(leaf_value)
    else:
        curr[last] = leaf_value
    #print(f"curr: {curr}")

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def list_files(root: str, patterns: Optional[List[str]] = None) -> Iterable[str]:
    if os.path.isfile(root):
        yield root
    else:
        for r, _, files in os.walk(root):
            for fn in files:
                if not patterns:
                    yield os.path.join(r, fn)
                else:
                    if any(fn.endswith(pat) for pat in patterns):
                        yield os.path.join(r, fn)

def strip_code_fences(s: str) -> str:
    """
    Remove a single pair of surrounding triple-backtick fences (with or without language).
    Keeps inner content intact. If there are multiple blocks, only unwraps when the
    WHOLE string is wrapped as a single block.
    """
    if not s:
        return s
    # Normalize CRLF
    t = s.strip()
    m = re.match(r"^```[A-Za-z0-9_-]*\s*\n([\s\S]*?)\n?```$", t)
    if m:
        return m.group(1).strip()
    return s

# ----------------------------- Parsers ---------------------------------------

class JSXParser:
    """
    Minimal JSX-ish parser to:
      - detect opening tags <Tag ...> and self-closing <Tag .../>
      - detect closing tags </Tag>
      - detect attributes on opening/self-closing token (key="..." | key={'...'} | key={...expr...})

    It builds a stack of open tag names. For each opening/self-closing tag, if the attribute
    target matches (--param), we emit a record with the current path + tag, and attr value.

    This is robust enough for common .tsx/.jsx files (not a full parser).
    """

    # open/self close tag
    TAG_START_RE = re.compile(r"<([A-Za-z_][\w.\-]*)\b")

    # closing tag
    TAG_CLOSE_RE = re.compile(r"</\s*([A-Za-z_][\w\.\-]*)\s*>")
    # self-closing detection (based on " ... />")
    SELF_CLOSE_RE = re.compile(r"/\s*>$")

    # attribute patterns
    # key="string"
    ATTR_DQ_RE = re.compile(r'([A-Za-z_][\w\-]*)\s*=\s*"([^"]*)"')
    # key='string'
    ATTR_SQ_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*'([^']*)'")
    # key={'string'} (capture literal string inside braces)
    ATTR_BRACE_STRING_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*\{\s*'([^']*)'\s*\}")
    ATTR_BRACE_DQSTRING_RE = re.compile(r'([A-Za-z_][\w\-]*)\s*=\s*\{\s*"([^"]*)"\s*\}')
    # key={ expression } fallback
    ATTR_BRACE_EXPR_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*\{([^}]*)\}")

    def __init__(self, param_name: str, match_all : bool = False, is_attribute_mode: bool = False, no_standard : bool = False):
        self.param_name = param_name
        self.match_all = match_all
        self.is_attribute_mode = is_attribute_mode
        self.no_standard = no_standard
        self.items = list()
    
    def clear_items_and_reset(self):
        self.items = list()
    
    def _custom_find_matching_close_span(self, text, tag, from_index):
        """
        Given an opening <tag ...> that ends at from_index (i.e., index right after '>'),
        return (start, end) of the matching closing token </tag>, considering nested same-name tags.
        If not found, return None.
        """
        depth = 1
        i = from_index
        n = len(text)
        open_pat = re.compile(rf"<\s*{re.escape(tag)}\b")
        close_pat = re.compile(rf"</\s*{re.escape(tag)}\s*>")
        in_quote = None
        apostrophe = None
        GREATER_THAN = ">"
        LOWER_THAN = "<"
        greater_than_count = 0
        lower_than_count = 0
        difference_appearance_signs = 0
        brace_depth = 0

        while i < n:
            
            mclose = close_pat.match(text, i)
            if mclose and in_quote is None and apostrophe is None and brace_depth == 0:
                depth -= 1
                if depth == 0:
                    return (mclose.start(), mclose.end())
                i = mclose.end()
                continue
            # quick check for an opening same-name tag at i (increases depth)
            mopen = open_pat.match(text, i)
            if mopen and in_quote is None and apostrophe is None and brace_depth == 0:
                # skip forward to the end '>' of this opening to avoid false matches inside attributes
                m2 = self.match_opening_tag(text, i)
                if not m2:
                    i += 1
                    continue
                depth += 1
                i = m2["end"]
                continue
            ch = text[i]
            if i > 1 and i != from_index:
                if (ch == GREATER_THAN and re.match(r"[//\w\<\}\d]", text[i-1])) or (ch == LOWER_THAN and re.match(r"[//\w\>]", text[i+1])):
                    
                    if ch == GREATER_THAN:
                        greater_than_count+=1
                    elif ch == LOWER_THAN:
                        lower_than_count+=1
                        
                    difference_appearance_signs = lower_than_count -greater_than_count
            
            if difference_appearance_signs != 0:
                if in_quote or apostrophe:
                    if ch == "\\":
                        i += 2
                        continue
                    if ch == in_quote:
                        in_quote = None
                    elif ch == apostrophe:
                        apostrophe = None
                else:
                    if ch == '"' and not apostrophe:
                        in_quote = ch
                    elif ch == "{":
                        brace_depth += 1
                    elif ch == "}":
                        if brace_depth > 0:
                            brace_depth -= 1
                    elif ch == "'" and not in_quote:
                        apostrophe = ch
            i += 1
        return None

    def _find_matching_close_span(self, text: str, tag: str, from_index: int) -> Optional[Tuple[int, int]]:
        """
        Given an opening <tag ...> that ends at from_index (i.e., index right after '>'),
        return (start, end) of the matching closing token </tag>, considering nested same-name tags.
        If not found, return None.
        """
        depth = 1
        i = from_index
        n = len(text)
        open_pat = re.compile(rf"<\s*{re.escape(tag)}\b")
        close_pat = re.compile(rf"</\s*{re.escape(tag)}\s*>")
        in_quote = None
        brace_depth = 0

        while i < n:
            # quick check for a closing tag at i
            mclose = close_pat.match(text, i)
            if mclose and in_quote is None and brace_depth == 0:
                depth -= 1
                if depth == 0:
                    return (mclose.start(), mclose.end())
                i = mclose.end()
                continue

            # quick check for an opening same-name tag at i (increases depth)
            mopen = open_pat.match(text, i)
            if mopen and in_quote is None and brace_depth == 0:
                # skip forward to the end '>' of this opening to avoid false matches inside attributes
                m2 = self.match_opening_tag(text, i)
                if not m2:
                    i += 1
                    continue
                depth += 1
                i = m2["end"]
                continue

            ch = text[i]
            if in_quote:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_quote:
                    in_quote = None
            else:
                if ch in ("'", '"'):
                    in_quote = ch
                elif ch == "{":
                    brace_depth += 1
                elif ch == "}":
                    if brace_depth > 0:
                        brace_depth -= 1
            i += 1
        return None
        
    @classmethod
    def match_opening_tag(cls, text: str, start: int = 0): 
        """
        Return a dict with:
        - tag: tag name (str)
        - attrs: full raw attributes string (str)
        - self_closing: bool
        - start: start index of '<'
        - end: index just after the closing '>' of this opening tag
        Returns None if no opening tag is found from `start` onward.
        """
        m = cls.TAG_START_RE.search(text, start)
        if not m:
            return None

        tag = m.group(1)
        i = m.end()
        attrs_start = i
        in_quote = None
        brace_depth = 0

        while i < len(text):
            ch = text[i]
            if in_quote:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_quote:
                    in_quote = None
            else:
                if ch == "'" or ch == '"':
                    in_quote = ch
                elif ch == "{":
                    brace_depth += 1
                elif ch == "}":
                    if brace_depth > 0:
                        brace_depth -= 1
                elif ch == ">" and brace_depth == 0:
                    raw_attrs = text[attrs_start:i].rstrip()
                    self_closing = raw_attrs.endswith("/")
                    if self_closing:
                        raw_attrs = raw_attrs[:-1].rstrip()
                    return {
                        "tag": tag,
                        "attrs": raw_attrs,
                        "self_closing": self_closing,
                        "start": m.start(),
                        "end": i + 1,
                    }
            i += 1
        # no '>' after '<tag' → não é uma abertura bem-formada a partir daqui
        return None

    
    def _strip_tag_tokens(self, s: str) -> str:
        """
        Remove every '<...>' token from s, preserving the text outside tags.
        Handles quoted strings and brace depth inside a tag to avoid premature '>'.
        """
        out = []
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch == "<":
                # skip a full tag token <...>
                j = i + 1
                in_quote = None
                brace_depth = 0
                while j < n:
                    c = s[j]
                    if in_quote:
                        if c == "\\":
                            j += 2
                            continue
                        if c == in_quote:
                            in_quote = None
                        j += 1
                        continue
                    else:
                        if c in ("'", '"'):
                            in_quote = c
                            j += 1
                            continue
                        if c == "{":
                            brace_depth += 1
                            j += 1
                            continue
                        if c == "}":
                            if brace_depth > 0:
                                brace_depth -= 1
                            j += 1
                            continue
                        if c == ">" and brace_depth == 0:
                            j += 1
                            break
                        j += 1
                # drop the whole <...> token
                i = j
                continue
            else:
                out.append(ch)
                i += 1
        return "".join(out)


    def _extract_non_tag_items(self, inner: str) -> list[str]:
        """
        From a tag's inner source (original, unmodified), produce a list of:
        - visible text lines (non-empty, normalized), and
        - non-JSX brace expressions (e.g., {dynamicGreeting}), preserving braces.

        For brace bodies that contain JSX ('<'), we DO NOT emit the expression itself;
        instead we recursively extract non-tag items from inside the brace body so we still
        pick up human-visible text nested in JSX.

        Items are returned in source order.
        """
        items: list[str] = []
        i = 0
        n = len(inner)

        def emit_text_segment(seg: str):
            # Collapse whitespace per line and emit non-empty lines that contain letters/digits
            lines = [ln.strip() for ln in seg.splitlines()]
            for ln in lines:
                if ln and re.search(r"[A-Za-z0-9]", ln):
                    items.append(ln)

        while i < n:
            ch = inner[i]

            # 1) JSX tag token: skip the entire <...> (opening/closing/self-closing)
            if ch == "<":
                j = i + 1
                in_quote = None
                brace_depth = 0
                # skip until matching '>' that is not inside quotes or inner braces
                while j < n:
                    c = inner[j]
                    if in_quote:
                        if c == "\\":
                            j += 2
                            continue
                        if c == in_quote:
                            in_quote = None
                        j += 1
                        continue
                    else:
                        if c in ("'", '"'):
                            in_quote = c
                            j += 1
                            continue
                        if c == "{":
                            brace_depth += 1
                            j += 1
                            continue
                        if c == "}":
                            if brace_depth > 0:
                                brace_depth -= 1
                            j += 1
                            continue
                        if c == ">" and brace_depth == 0:
                            j += 1
                            break
                        j += 1
                # drop the whole tag token
                i = j
                continue

            # 2) Brace expression: read balanced body, then decide
            if ch == "{":
                try:
                    body, j2 = self._read_balanced_brace_expr(inner, i)
                except ValueError:
                    # Unbalanced: treat '{' literally as text up to next control char
                    start = i
                    i += 1
                    while i < n and inner[i] not in "{<":
                        i += 1
                    emit_text_segment(inner[start:i])
                    continue

                if "<" in body:
                    # JSX inside; recurse to collect nested texts/expressions (but NOT this expr token)
                    nested = self._extract_non_tag_items(body)
                    items.extend(nested)
                else:
                    # Non-JSX expression → keep as literal with braces
                    expr = "{" + body.strip() + "}"
                    items.append(expr)
                i = j2
                continue

            # 3) Plain text region until next control char
            start = i
            while i < n and inner[i] not in "{<":
                i += 1
            emit_text_segment(inner[start:i])

        return items

    
    def _read_balanced_brace_expr(self, s: str, start: int) -> Tuple[str, int]:
        """
        Read a balanced expression that starts at s[start] == '{' and return
        (content_without_braces, position_after_expression).

        Maintains brace balance and respects quoted strings with escapes.
        Raises ValueError if the expression is not closed.
        """
        assert s[start] == "{"
        i = start + 1
        depth = 1
        n = len(s)
        in_quote = None
        while i < n:
            ch = s[i]
            if in_quote:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_quote:
                    in_quote = None
                i += 1
                continue
            else:
                if ch in ("'", '"'):
                    in_quote = ch
                    i += 1
                    continue
                if ch == "{":
                    depth += 1
                    i += 1
                    continue
                if ch == "}":
                    depth -= 1
                    if depth == 0:
                        # conteúdo é entre start+1 e i-1 inclusive
                        return (s[start+1:i], i+1)
                    i += 1
                    continue
                i += 1
        raise ValueError("Unbalanced brace expression")

    
    def parse(self, text: str, stack: List[str] = []) -> Iterable[Tuple[List[str], str, Optional[str], Optional[str]]]:
        #print(f"DEBUG 697 parse | starting parse..., stack: {stack}")
        i = 0
        n = len(text)
        while i < n:
            mclose = self.TAG_CLOSE_RE.match(text, i)
            if mclose:
                tag = mclose.group(1)
                for j in range(len(stack)-1, -1, -1):
                    if stack[j] == tag:
                        stack = stack[:j]
                        break
                i = mclose.end()
                #print(f"DEBUG 715 JSXParser.parse | tag: {tag}, stack: {stack}, i: {i}")
                continue

            mopen = self.match_opening_tag(text, i)
            if mopen:
                tag = mopen["tag"]
                attrs_src = mopen["attrs"] or ""
                is_self = mopen["self_closing"]
                have_close_tag = bool(re.findall(rf"</\s*({tag})\s*>", text))
                stack.append(tag)

                #print(f"DEBUG 715 JSXParser.parse | tag: {tag}, attrs_src: {attrs_src}, is_self: {is_self}, have_close_tag: {have_close_tag}, stack: {stack}")
                
                # =========================
                # TAG-CONTENT MODE (UNCHECKED)
                # =========================
                if not self.is_attribute_mode:
                    if self.match_all or (tag == self.param_name):
                        if is_self or not have_close_tag:
                            # previously returned literal self-closing token; now skip
                            inner = ""
                            items = []
                            span = None
                        else:
                            span = self._custom_find_matching_close_span(text, tag, mopen["end"])
                            inner = text[mopen["end"]:span[0]] if span else ""
                            items = self._extract_non_tag_items(inner)

                        #print(f"DEBUG 733 span: {span}, stack: {stack}, tag: {tag}, items: {items},")# inner: {inner}")
                        if inner and not self.no_standard:
                            #print(f"DEBUG 743 parse | Starting a new recursive..., stack: {stack}, tag: {tag}")
                            for stack, tag, tag, item in self.parse(inner, stack):
                                yield(stack, tag, tag, item)
                        #print(f"DEBUG 739 parse | new recursive completed! stack: {stack}, tag: {tag}")
                        # Emit one row per item (text line or non-JSX expression)
                        # Emit a single row per tag with a single combined value
                        # Emit one row per item (text line or non-JSX expression)
                        for it in items:
                            new_item = it.strip()
                            if new_item and new_item not in self.items:
                                #print(f"DEBUG 740 parse | it.strip()..., self.no_standard: {self.no_standard}, inner: {inner}")
                                # key_for_path = tag (we'll keep tag as the key unless "drop standard" hides it)
                                self.items.append(new_item)
                                yield (list(stack), tag, tag, new_item)
                        

                        # Advance and pop
                        if is_self or not span:
                            stack.pop()
                            i = mopen["end"]
                        else:
                            i = span[1]
                            if stack and stack[-1] == tag:
                                stack.pop()
                        continue
                    else:
                        if is_self or not have_close_tag:
                            stack.pop()
                        i = mopen["end"]
                        continue

                # =========================
                # ATTRIBUTE MODE (CHECKED)
                # =========================
                key_matched: Optional[str] = None
                value_text: Optional[str] = None

                if attrs_src:
                    # string-like values first
                    for rx in (self.ATTR_DQ_RE, self.ATTR_SQ_RE, self.ATTR_BRACE_STRING_RE, self.ATTR_BRACE_DQSTRING_RE):
                        for am in rx.finditer(attrs_src):
                            k, v = am.group(1), am.group(2)
                            if self.match_all or (k == self.param_name):
                                key_matched, value_text = k, v
                                break
                        if key_matched:
                            break

                    # balanced { ... } expressions (scanner)
                    if not key_matched:
                        j = 0
                        while j < len(attrs_src):
                            m = re.match(r"\s*([A-Za-z_][\w\-]*)\s*=\s*\{", attrs_src[j:])
                            if not m:
                                j += 1
                                continue
                            k = m.group(1)
                            brace_start = j + m.end() - 1
                            try:
                                expr, j2 = self._read_balanced_brace_expr(attrs_src, brace_start)
                            except ValueError:
                                j += 1
                                continue
                            if self.match_all or (k == self.param_name):
                                key_matched, value_text = k, expr.strip()
                                break
                            j = j2

                #print(f"DEBUG 732 parse | stack: {stack}, tag: {tag}, key_matched: {key_matched}, value_text: {value_text}")
                # emit one row for this opening/self tag (attribute mode)
                yield (list(stack), tag, key_matched, value_text)

                if is_self or not have_close_tag:
                    stack.pop()
                i = mopen["end"]
                continue


            i += 1

class GenericScopeParser:
    """
    Generic parser driven by user regex for scope start and end (delimiters).
    When a start match occurs, push a name for that scope (if we can infer a label),
    else push a generic token like 'scope'.
    For simplicity, we allow user to define a name-capture group (?P<name>...) inside start regex
    to be used as node name; otherwise we fallback to a token 'scope'.

    We also scan inside each start token for attributes like key="..." etc (like JSXParser).
    """

    ATTR_DQ_RE = re.compile(r'([A-Za-z_][\w\-]*)\s*=\s*"([^"]*)"')
    ATTR_SQ_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*'([^']*)'")
    ATTR_BRACE_STRING_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*\{\s*'([^']*)'\s*\}")
    ATTR_BRACE_DQSTRING_RE = re.compile(r'([A-Za-z_][\w\-]*)\s*=\s*\{\s*"([^"]*)"\s*\}')
    ATTR_BRACE_EXPR_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*\{([^}]*)\}")

    def __init__(self, param_name: str, start_regex: str, end_regex: str, match_all: bool = False):
        self.param_name = param_name
        self.start_re = re.compile(start_regex)
        self.end_re = re.compile(end_regex)
        self.match_all = match_all

    def parse(self, text: str, stack: List[str] = []) -> Iterable[Tuple[List[str], str, Optional[str]]]:
        """
        Yields (stack_path, node_name, value_if_attr_found_or_None).
        - On start match: push node_name (from (?P<name>...) if present, else 'scope')
          and emit a record (with any attribute found next to the start token).
        - On end match: pop one scope.
        """
        i = 0
        n = len(text)
        stack: List[str] = []
        while i < n:
            mend = self.end_re.match(text, i)
            if mend:
                if stack:
                    stack.pop()
                i = mend.end()
                continue

            mstart = self.start_re.match(text, i)
            if mstart:
                node_name = mstart.groupdict().get("name", "scope")
                stack.append(node_name)
                # try to scan attributes right after start token (optional)
                tail = text[mstart.end(): mstart.end()+500]
                found_value: Optional[str] = None
                for rx in (self.ATTR_DQ_RE, self.ATTR_SQ_RE, self.ATTR_BRACE_STRING_RE, self.ATTR_BRACE_DQSTRING_RE):
                    am = rx.search(tail)
                    while am:
                        k, v = am.group(1), am.group(2)
                        if k == self.param_name and found_value is None:
                            found_value = v
                            break
                        am = rx.search(tail, am.end())
                    if found_value is not None:
                        break
                if found_value is None:
                    am = self.ATTR_BRACE_EXPR_RE.search(tail)
                    while am:
                        k, expr = am.group(1), am.group(2).strip()
                        if k == self.param_name:
                            found_value = expr
                            break
                        am = self.ATTR_BRACE_EXPR_RE.search(tail, am.end())

                yield (list(stack), node_name, node_name, found_value)
                i = mstart.end()
                continue

            i += 1
            
# ------------------------- Extraction Orchestrator ----------------------------

class Extractor:
    def __init__(
        self,
        param: str,
        mode: str,
        avoid_keys : str,
        avoid_keys_parameter : str,
        include_key: bool,
        include_value: bool,
        no_standard: bool,
        convert_to_json: bool,
        with_quotation_marks : bool,
        indentation: int,
        case_style: str,
        limit: Optional[str],
        avoid_cut: bool,
        to_upper: bool,
        only_strings : bool = False,
        is_attribute_mode : bool = False,
        start_regex: Optional[str] = None,
        end_regex: Optional[str] = None,
        root_alias: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
    ):
        self.param = param
        self.match_all = (param is None) or (param.strip() == "") or (param.strip() == "*")
        self.mode = mode
        self.avoid_keys = avoid_keys
        self.avoid_keys_parameter = avoid_keys_parameter
        self.include_key = include_key
        self.include_value = include_value
        self.no_standard = no_standard
        self.convert_to_json = convert_to_json
        self.with_quotation_marks = with_quotation_marks
        self.only_strings = only_strings
        self.indentation = indentation
        self.case_style = case_style
        self.limit = limit
        self.avoid_cut = avoid_cut
        self.to_upper = to_upper
        self.start_regex = start_regex
        self.end_regex = end_regex
        self.root_alias = root_alias or "Root"
        self.file_extensions = file_extensions
        self.is_attribute_mode = is_attribute_mode
        self.CONTAINS = "contains"
        self.EQUALS = "equals"

    def _filter_standard(self, path: List[str]) -> List[str]:
        if not self.no_standard:
            return path
        return [p for p in path if not is_standard_tag(p)]


    def _build_path_tokens(
        self, file_root_token: str, stack: List[str], tag: str, value_text: Optional[str]
    ) -> List[str]:
        """
        Build path tokens from file-root alias + parsed stack + current tag,
        optionally adding the key and normalized value token.
        """
        tokens: List[str] = [file_root_token] + stack  # stack already includes current tag for JSX parser
        tokens = self._filter_standard(tokens)

        if self.include_key or (not self.include_key and not self.include_value):
            tokens.append(self.param)

        if value_text is not None:
            # normalize value text (apply limit, avoid-cut, case, upper)
            trimmed = smart_truncate(value_text, self.limit, self.avoid_cut)
            norm = normalize_token(trimmed, self.case_style, self.to_upper)
            if norm:
                tokens.append(norm)

        return tokens

    def _record_text_kv(self, path_tokens: List[str], raw_value: str) -> Dict[str, Any]:
        """
        Build a small tree that, at `path_tokens`, adds a single key:value pair
        derived from `raw_value`. The key is normalized using the current case
        settings; the value is the original `raw_value`.
        Never creates lists; if a key already exists, later values overwrite earlier ones.
        """
        # 1) Normalize key from the raw value (respect case/upper/limit/avoid_cut)
        trimmed = smart_truncate(raw_value, self.limit, self.avoid_cut)
        key = normalize_token(trimmed, self.case_style, self.to_upper) or "text"

        # 2) Build small tree: (... path_tokens ...) -> { key: raw_value }
        root: Dict[str, Any] = {}
        node = root
        for t in path_tokens:
            node = node.setdefault(t, {})
        node[key] = raw_value
        return root


    def find_paths_to_key(self, structure: JSONLike, word_key: str, current_path: Optional[List[str]] = None) -> List[List[str]]:
        """Return a list of key paths leading to every occurrence of word_key."""
        if current_path is None:
            current_path = []
        paths = []

        if isinstance(structure, dict):
            for k, v in structure.items():
                new_path = current_path + [k]
                if k == word_key:
                    paths.append(new_path)
                else:
                    paths.extend(self.find_paths_to_key(v, word_key, new_path))

        elif isinstance(structure, list):
            for i, item in enumerate(structure):
                new_path = current_path + [f"[{i}]"]
                paths.extend(self.find_paths_to_key(item, word_key, new_path))

        return paths


    def get_subtree_at_path(self, structure: JSONLike, path: List[str]) -> Optional[JSONLike]:
        """Navigate a path (list of keys) inside a nested dict and return subtree."""
        node = structure
        for key in path:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return None
        return node


    def build_tree_from_path(self, path: List[str], leaf_value: Any) -> Dict[str, Any]:
        """Build nested dict from path ending in leaf_value."""
        result = leaf_value
        for key in reversed(path):
            result = {key: result}
        return result

    def merge_dicts(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dict trees recursively."""
        result = dict(a)
        for k, v in b.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self.merge_dicts(result[k], v)
            else:
                result[k] = v
        return result

    def prune_to_key(self, structure: JSONLike, word_key: str, depth_offset: int = 0) -> Optional[JSONLike]:
        """
        Returns a structure preserving only branches leading to `word_key`,
        adjusting cut depth by `depth_offset`:
        - 0 : cut exactly at word_key
        - negative : move up (-1 removes one more level to the left)
        - positive : include deeper levels (+1 adds one more level to the right)
        """
        paths = self.find_paths_to_key(structure, word_key)
        if not paths:
            return None

        final_tree: Dict[str, Any] = {}

        for path in paths:
            # Ajustar caminho conforme o deslocamento
            if depth_offset < 0:
                new_path = path[:depth_offset] if abs(depth_offset) < len(path) else []
                leaf = path[depth_offset] if new_path else word_key
            elif depth_offset == 0:
                new_path = path
                leaf = word_key
            else:
                # profundidade positiva: expandir mais dentro da subárvore
                subtree = self.get_subtree_at_path(structure, path)
                for _ in range(depth_offset):
                    if isinstance(subtree, dict) and subtree:
                        # pega o primeiro item do dicionário
                        first_key = next(iter(subtree))
                        path.append(first_key)
                        subtree = subtree[first_key]
                    else:
                        break
                new_path = path
                leaf = subtree

            if new_path:
                branch = self.build_tree_from_path(new_path, leaf)
                final_tree = self.merge_dicts(final_tree, branch)

        return final_tree or None
    
    def remove_key(self, structure: JSONLike, key_to_remove: str) -> JSONLike:
        """
        Recursively remove all occurrences of `key_to_remove` from a nested dict or list.

        Args:
            structure: nested structure (dict/list/scalars)
            key_to_remove: key name to delete

        Returns:
            A new structure with all occurrences of the key removed.
        """
        # Se for dict: cria uma nova versão sem a chave proibida
        if isinstance(structure, dict):
            new_dict = {}
            for key, value in structure.items():
                if key == key_to_remove:
                    # ignora essa chave (remove)
                    continue
                # recursão para limpar dentro dos valores
                new_dict[key] = self.remove_key(value, key_to_remove)
            return new_dict

        # Se for lista: aplica a função a cada item
        elif isinstance(structure, list):
            return [self.remove_key(item, key_to_remove) for item in structure]

        # Se for valor atômico: retorna como está
        else:
            return structure

    def remove_key_with_collapse(self, structure: JSONLike, key_to_remove: str) -> JSONLike:
        """
        Remove `key_to_remove` em toda a estrutura.
        Se, após a remoção, um dict-filho ficar vazio, colapsa o valor desse filho
        para o nome da chave correspondente (ex.: { 'StatsCard': {} } -> { 'StatsCard': 'StatsCard' }).
        """
        if isinstance(structure, dict):
            new_dict: Dict[str, Any] = {}

            for k, v in structure.items():
                if k == key_to_remove:
                    # remove essa chave completamente
                    continue

                nv = self.remove_key_with_collapse(v, key_to_remove)

                # Se o resultado do filho for um dict vazio, colapsa para o próprio nome da chave
                if isinstance(nv, dict) and not nv:
                    new_dict[k] = k
                else:
                    new_dict[k] = nv

            return new_dict

        if isinstance(structure, list):
            # Processa cada item; se virar dict vazio, mantém {} (não há "nome da chave" em listas)
            new_list: List[Any] = []
            for item in structure:
                ni = self.remove_key_with_collapse(item, key_to_remove)
                new_list.append(ni)
            return new_list

        # Escalares permanecem
        return structure

    def _build_path_tokens_with_key(
        self, file_root_token: str, stack: List[str],
        key_for_path: Optional[str]#, value_text: Optional[str]
    ) -> List[str]:
        tokens = [file_root_token] + self._filter_standard(stack)

        #Include the key segment when requested / in match-all
        if self.include_key or self.match_all or (not self.include_key and not self.include_value):
            if key_for_path and self.is_attribute_mode:
                tokens.append(key_for_path)

        # Never append the value to the path in any mode.
        return tokens


    
    def deep_merge(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                a[k] = self.deep_merge(a[k], v)
            else:
                a[k] = v
        return a
    
    def check_value_if_it_is_just_string(self, value: str) -> bool:
        """
        Retorna True se `value` representar apenas uma string literal pura,
        e False caso contenha expressões, variáveis, operações, objetos,
        arrays, condicionais, números, ou qualquer coisa fora de aspas.

        Exemplos válidos:
            "Hello world"
            'Hi there'
            "Today's Practice"

        Exemplos inválidos:
            {dynamicGreeting}
            user.name
            count + 1
            {"Expr " + name}
            {'x' if cond else 'y'}
        """
        
        if value is None:
            return False

        s = value.strip()

        # Se tiver chaves externas, remova-as e teste o interior
        if s.startswith("{") and s.endswith("}"):
            return False
        
        if re.search(r"[+*/\{\}|\&\[\]=]", s):
            return False
        
        # Se contém acessos a propriedades, variáveis, ou funções → invalida
        if re.search(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*|\s*\()", s):
            return False

        # Qualquer coisa que contenha { }, +, =, ? etc. é inválida
        if re.search(r"[\{\}+*/=|\&\[\]]", s):
            return False
        
        if re.search(r"\?\s{0,3}\(", s):
            return False

        return True
    
    def process_text(self, file_alias: str, text: str) -> Tuple[List[str], Dict[str, Any]]:
        #print("DEBUG 1420 Extractor.process_text | init")
        if self.mode == "jsx":
            parser = JSXParser(self.param, match_all=self.match_all, is_attribute_mode=self.is_attribute_mode, no_standard=self.no_standard)
        else:
            if not (self.start_regex and self.end_regex):
                raise ValueError("Generic mode requires --start-delim and --end-delim (regex).")
            parser = GenericScopeParser(self.param, self.start_regex, self.end_regex, match_all=self.match_all)

        out_lines, merged_json = [], {}
        #print("DEBUG 1242 Extractor.process_text begin...")
        for stack, tag, key_matched, value in parser.parse(text, []):
            #print(f"DEBUG 1326 process_text | tag: {tag}, key_matched: {key_matched}, value: {value}")
            # choose which key goes into the path
            #effective_key = key_matched if (self.match_all and key_matched) else self.param
            # Attribute mode: include the attribute key when requested
            # Tag-content mode: suppress the "key" segment (path will end at tag)
            
            if self.only_strings:
                is_only_strings = self.check_value_if_it_is_just_string(value)
                #print(f"DEBUG 1432 process_text | is_only_strings: {is_only_strings}")
                if not is_only_strings:
                    continue
            
            keys_to_avoid = None
            if self.avoid_keys:
                keys_to_avoid = [i.strip() for i in self.avoid_keys.split(",")]
                #print(f"DEBUG 1165 process_text | keys_to_avoid: {keys_to_avoid}, key_matched in keys_to_avoid: {key_matched in keys_to_avoid}, tag in keys_to_avoid: {tag in keys_to_avoid}")
                if self.avoid_keys_parameter == self.CONTAINS and any(list(filter(lambda x: x in key_matched or x in tag or x in value,keys_to_avoid))) or self.avoid_keys_parameter == self.EQUALS and any(list(filter(lambda x: x == key_matched or x == tag or x == value,keys_to_avoid))):
                    continue
            
            #print(f"DEBUG 1169 process_text | continue tag: {tag}, key_matched: {key_matched}") 
            if self.is_attribute_mode:
                # Skip when this tag doesn't have the attribute
                
                if value is None:
                    # nothing to record for this element
                    continue
                
                effective_key = (key_matched if (self.match_all and key_matched) else self.param)
                tokens = self._build_path_tokens_with_key(file_alias, stack, effective_key)#, value)
                if self.avoid_keys:
                    if not keys_to_avoid:
                        keys_to_avoid = [i.strip() for i in self.avoid_keys.split(",")]
                    #print(f"DEBUG 1165 process_text | keys_to_avoid: {keys_to_avoid}, key_matched in keys_to_avoid: {key_matched in keys_to_avoid}, tag in keys_to_avoid: {tag in keys_to_avoid}")
                    if self.avoid_keys_parameter == self.CONTAINS and list(filter(lambda x: any([x in token for token in tokens]), keys_to_avoid)) or self.avoid_keys_parameter == self.EQUALS and list(filter(lambda x: any([x == token for token in tokens]), keys_to_avoid)):
                        continue
                #print(f"DEBUG 1178 Extractor.process_text | effective_key: {effective_key}, tokens: {tokens}")
                if tokens:
                    out_lines.append(path_join(tokens))
                    if self.convert_to_json:
                        j = self._record_text_kv(tokens, value)
                        merged_json = self.deep_merge(merged_json, j)
                        #print(f"DEBUG 1185 Extractor.process_text | j: {j}, merged_json: {merged_json}")
            else:
                # TAG-CONTENT MODE
                tag_name = tag
                # Keep the tag name as a key in the hierarchy
                if self.no_standard and (tag_name.lower() in STANDARD_HTML_TAGS):
                    tokens = self._nearest_kept_ancestor_tokens(file_alias, stack)
                else:
                    effective_key = tag_name
                    tokens = self._build_path_tokens_with_key(file_alias, stack, effective_key)#, value)
                
                if self.avoid_keys:
                    if not keys_to_avoid:
                        keys_to_avoid = [i.strip() for i in self.avoid_keys.split(",")]
                    #print(f"DEBUG 1165 process_text | keys_to_avoid: {keys_to_avoid}, key_matched in keys_to_avoid: {key_matched in keys_to_avoid}, tag in keys_to_avoid: {tag in keys_to_avoid}")
                    if self.avoid_keys_parameter == self.CONTAINS and list(filter(lambda x: any([x in token for token in tokens]), keys_to_avoid)) or self.avoid_keys_parameter == self.EQUALS and list(filter(lambda x: any([token == x for token in tokens]), keys_to_avoid)):
                        continue
                    
                if tokens and value:
                    if self.convert_to_json:
                        j = self._record_text_kv(tokens, value)  # << key:value under this tag
                        merged_json = self.deep_merge(merged_json, j)
                    # Paths panel (optional): show the full tag path
                    out_lines.append(path_join(tokens))

        #parser.clear_items_and_reset()
        if self.is_attribute_mode:
            if not self.include_value:
                if self.include_key:
                    merged_json = self.prune_to_key(merged_json, self.param, -1)
                else:
                    merged_json = self.prune_to_key(merged_json, self.param, -2)
        
        #print(f"DEBUG 1449 Extractor.process_text | out_lines: {out_lines}, merged_json: {merged_json}")
        return out_lines, merged_json

    def json_to_js_literal(self, data, indent=2):
        text = json.dumps(data, ensure_ascii=False, indent=indent)
        # Remove aspas das chaves simples
        text = re.sub(r'\"([A-Za-z_][A-Za-z0-9_]*)\":', r'\1:', text)
        return text

    def _nearest_kept_ancestor_tokens(self, file_root_token: str, stack: List[str]) -> List[str]:
        """
        Anchor for flattened text:
        - If dropping standard tags, anchor at the deepest NON-standard
            ancestor present in `stack`. If none exists, anchor at root.
        - If not dropping, keep the entire stack.
        """
        #print(f"DEBUG 1391 _nearest_kept_ancestor_tokens | file_root_token: {file_root_token}, stack: {stack}")
        return kept_prefix(file_root_token, stack, drop_standard=self.no_standard)

    # def _nearest_kept_ancestor_tokens(self, file_root_token: str, stack: List[str]) -> List[str]:
    #     """
    #     Generalized path builder:
    #     - Always returns [file_root_token] + full stack filtered by drop_standard.
    #     - Keeps all custom tags (AuthGuard, StatsCard, etc.).
    #     - Drops only standard HTML tags when no_standard=True.
    #     - Never collapses or duplicates key segments.
    #     """
    #     if not stack:
    #         return [file_root_token]
        
    #     if self.no_standard:
    #         kept = [t for t in stack if not is_standard_tag(t)]
    #     else:
    #         kept = list(stack)

    #     # ensure uniqueness (avoid duplicates like ['AuthGuard','AuthGuard'])
    #     final = []
    #     for t in kept:
    #         if not final or final[-1] != t:
    #             final.append(t)
    #     return [file_root_token] + final


    def _record_text_bucket(self, path_tokens: List[str], value: str) -> Dict[str, Any]:
        """
        Insert `value` into a '_text' list under the given path, creating/merging as needed:
        DashboardPage: { Section: { _text: [ "line1", "line2", ... ] } }
        """
        root: Dict[str, Any] = {}
        node = root
        for t in path_tokens:
            node = node.setdefault(t, {})
        bucket = node.setdefault("_text", [])
        if isinstance(bucket, list):
            bucket.append(value)
        else:
            node["_text"] = [bucket, value]
        return root

    
    def run(self, path: str) -> Tuple[str, Optional[str]]:
        """
        Process a file or directory. Returns (text_result, json_result_or_None)
        """
        all_lines: List[str] = []
        merged_json: Dict[str, Any] = {}

        file_patterns = self.file_extensions
        for fp in list_files(path, file_patterns):
            #print(f"DEBUG 1518 Extractor | file_patterns: {fp}")
            try:
                text = read_text(fp)
            except Exception as e:
                all_lines.append(f"<<ERROR reading {fp}: {e}>>")
                continue

            # derive a file-root token (e.g. DashBoardPage) from filename (PascalCase by default)
            # Prefer exported function/component name, fallback to filename
            # Prefer exported function/component name, fallback to filename
            base = os.path.splitext(os.path.basename(fp))[0]
            export_m = re.search(r'\bexport\s+default\s+function\s+([A-Za-z_]\w*)', text)
            if not export_m:
                # covers: "export default DashboardPage" (identifier)
                export_m = re.search(r'\bexport\s+default\s+([A-Za-z_]\w*)\b', text)

            if export_m:
                file_root = export_m.group(1)  # keep EXACT identifier: "DashboardPage"
            else:
                # fallback: keep filename as-is except extension, Pascalize only the filename
                file_root = base[0:1].upper() + base[1:]



            lines, j = self.process_text(file_root, text)
            #print(f"DEBUG 1518 Extractor | lines: {lines}, j: {j}")
            if lines:
                all_lines.append(f"# File: {fp}")
                all_lines.extend(lines)
            if self.convert_to_json and j:
                
                merged_json = self.deep_merge(merged_json, j)

        result_text = "\n".join(all_lines) if all_lines else "(no matches)"
        json_text = None
        
        if self.convert_to_json:
            #print(merged_json)
            if self.with_quotation_marks:
                json_text = json.dumps(merged_json, ensure_ascii=False, indent=self.indentation)
            else:
                json_text = self.json_to_js_literal(merged_json)
        #print(result_text, json_text)
        return result_text, json_text


# ------------------------------ CLI ------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Scan files/dirs for a parameter (attribute), build hierarchical path, and optionally export JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--path", required=False, help="File or directory to scan")
    p.add_argument("--param", required=False, default="*", help="Attribute/parameter name to extract. Use '' or * to match all attributes.")
    p.add_argument("--mode", choices=["jsx", "generic"], default="jsx", help="Parsing mode")
    p.add_argument("--start-delim", dest="start_delim", help="Generic mode: start delimiter regex")
    p.add_argument("--end-delim", dest="end_delim", help="Generic mode: end delimiter regex")
    p.add_argument("--include-key", action="store_true", help="Include the attribute key in the path")
    p.add_argument("--include-value", action="store_true", help="Append normalized value token to the path")
    p.add_argument("--no-standard", action="store_true", help="Drop standard HTML tags from the path")
    p.add_argument("--convert-to-JSON", dest="convert_to_json", action="store_true", help="Emit nested JSON")
    p.add_argument("--indentation", type=int, default=2, help="Spaces for JSON indentation")
    p.add_argument("--case", choices=["snake", "camel", "pascal", "kebab"], default="snake", help="Value token style")
    p.add_argument("--upper", action="store_true", help="Uppercase the normalized value token")
    p.add_argument("--limit", default="all", help="Character limit for normalized value token (int or 'all')")
    p.add_argument("--avoid-cut", action="store_true", help="Avoid cutting in the middle of a word")
    p.add_argument("--ext", nargs="*", default=[".tsx", ".jsx", ".js", ".ts"], help="File extensions to include when scanning dirs")
    p.add_argument("--output", help="Write text output (paths) to file")
    p.add_argument("--json-output", dest="json_output", help="Write JSON output to file (when --convert-to-JSON)")
    p.add_argument("--gui", action="store_true", help="Open the PySide6 GUI")
    p.add_argument(
    "--is-tag",
    dest="is_attribute_mode",
    action="store_true",
    help="CHECKED = ATTRIBUTE mode (Param is a prop); UNCHECKED = TAG-CONTENT mode (Param is a tag; extract inner content)."
)


    return p

# ------------------------------ GUI ------------------------------------------
# Simple GUI wrapper to gather options and preview results

try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QPlainTextEdit, QCheckBox, QComboBox, QSpinBox,
        QMessageBox, QTabWidget, QRadioButton, QButtonGroup
    )
    from PySide6.QtCore import Qt
    PYSIDE_OK = True
except Exception:
    PYSIDE_OK = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Param → Path/JSON Extractor")
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Path row
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Path (file/dir):"))
        self.ed_path = QLineEdit()
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self._browse)
        self.is_file = QCheckBox("Is file?")
        row1.addWidget(self.ed_path, 1)
        row1.addWidget(btn_browse)
        row1.addWidget(self.is_file)
        root.addLayout(row1)

        # Param and mode
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Param/Attribute:"))
        self.ed_param = QLineEdit("")
        row2.addWidget(self.ed_param)
        
        self.chk_is_attribute_mode = QCheckBox("Treat Param as ATTRIBUTE?")
        row2.addWidget(self.chk_is_attribute_mode)

        row2.addWidget(QLabel("Mode:"))
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["jsx", "generic"])
        row2.addWidget(self.cb_mode)

        root.addLayout(row2)

        # Generic delimiters
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Start delimiter (regex):"))
        self.ed_start = QLineEdit("<.*?>")  # example default
        row3.addWidget(self.ed_start, 1)
        row3.addWidget(QLabel("End delimiter (regex):"))
        self.ed_end = QLineEdit("</.*?>")   # example default
        row3.addWidget(self.ed_end, 1)
        row3.addWidget(QLabel("Extensions (*.tsx *.jsx ...):"))
        self.ed_ext = QLineEdit(".tsx .jsx .js .ts")
        row3.addWidget(self.ed_ext, 1)
        root.addLayout(row3)

        # Options
        row4 = QHBoxLayout()
        self.chk_include_key = QCheckBox("Include key")
        self.chk_include_key.setChecked(True)
        self.chk_include_value = QCheckBox("Include value")
        self.chk_include_value.setChecked(True)
        self.chk_no_standard = QCheckBox("Drop standard HTML tags")
        self.chk_only_strings = QCheckBox("Only strings")
        self.chk_include_quotation_marks = QCheckBox("Include quotation marks")
        row4.addWidget(self.chk_include_key)
        row4.addWidget(self.chk_include_value)
        row4.addWidget(self.chk_no_standard)
        row4.addWidget(self.chk_only_strings)
        row4.addWidget(self.chk_include_quotation_marks)
        root.addLayout(row4)

        # Case/limit
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Case:"))
        self.cb_case = QComboBox()
        self.cb_case.addItems(["snake", "camel", "pascal", "kebab"])
        row5.addWidget(self.cb_case)

        self.chk_upper = QCheckBox("Uppercase token")
        row5.addWidget(self.chk_upper)

        row5.addWidget(QLabel("Limit:"))
        self.ed_limit = QLineEdit("all")
        row5.addWidget(self.ed_limit)

        self.chk_avoid_cut = QCheckBox("Avoid cut")
        row5.addWidget(self.chk_avoid_cut)

        row5.addWidget(QLabel("Indent:"))
        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(0, 16)
        self.spin_indent.setValue(2)
        row5.addWidget(self.spin_indent)
        root.addLayout(row5)
        
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Specify the keys and values to avoid (separate with commas): "))
        self.avoid_keys = QLineEdit("")
        row6.addWidget(self.avoid_keys)
        root.addLayout(row6)
        
        row7 = QHBoxLayout()
        self.avoid_keys_parameter_message = "equals"
        self.EQUALS_MESSAGE = "The words to be avoided should be the same"
        self.CONTAINS_MESSAGE = "The words to be avoided should be contained"
        self.avoid_keys_equals_option = QRadioButton(self.EQUALS_MESSAGE)
        self.avoid_keys_contains_option = QRadioButton(self.CONTAINS_MESSAGE)
        self.avoid_keys_group = QButtonGroup(root)
        self.avoid_keys_group.addButton(self.avoid_keys_equals_option)
        self.avoid_keys_group.addButton(self.avoid_keys_contains_option)
        self.avoid_keys_group.buttonToggled.connect(self.avoid_keys_option_changed)
        row7.addWidget(self.avoid_keys_equals_option)
        row7.addWidget(self.avoid_keys_contains_option)
        root.addLayout(row7)
        self.avoid_keys_equals_option.setChecked(True)
        
        # Buttons
        row8 = QHBoxLayout()
        self.btn_run = QPushButton("Run")
        self.btn_run.clicked.connect(self._run)
        self.btn_save = QPushButton("Save Outputs")
        self.btn_save.clicked.connect(self._save_outputs)
        row8.addStretch(1)
        row8.addWidget(self.btn_run)
        row8.addWidget(self.btn_save)
        root.addLayout(row8)

        # Output tabs
        self.tabs = QTabWidget()
        self.out_paths = QPlainTextEdit()
        self.out_paths.setReadOnly(True)
        self.out_json = QPlainTextEdit()
        self.out_json.setReadOnly(True)
        self.tabs.addTab(self.out_paths, "Paths")
        self.tabs.addTab(self.out_json, "JSON")
        root.addWidget(self.tabs, 1)
        
        self.copy_all = QPushButton("Copy All")
        self.copy_all.clicked.connect(self._copy_all)
        root.addWidget(self.copy_all)

        # Initial hints
        self.cb_mode.currentTextChanged.connect(self._toggle_generic_fields)
        self._toggle_generic_fields(self.cb_mode.currentText())

    def avoid_keys_option_changed(self, button, checked):
        if checked:
            message = button.text()
            if message == self.EQUALS_MESSAGE:
                self.avoid_keys_parameter_message = "equals"
            elif message == self.CONTAINS_MESSAGE:
                self.avoid_keys_parameter_message = "contains"
                
    # ---- Clipboard: filtered & no code fences lines ----
    def _should_filter_line(self, line: str) -> bool:
        s = line.lstrip()
        if s.startswith(">> Sending") or s.startswith(">> SIMULATED RESPONSE") or s.startswith("<<API ERROR:"):
            return True
        # Remove lines that are solely code-fence markers
        if re.match(r"^\s*```[A-Za-z0-9_-]*\s*$", s) or s.strip() == "```":
            return True
        return False
    
    def _copy_all(self):
        current = self.tabs.currentWidget()
        text = current.toPlainText()
        # If the WHOLE text is a single fenced block (rare), unwrap it
        text = strip_code_fences(text)
        lines = text.splitlines()
        filtered = [ln for ln in lines if not self._should_filter_line(ln)]
        # collapse multiple blank lines
        compact, prev_blank = [], False
        for ln in filtered:
            blank = (ln.strip() == "")
            if blank and prev_blank:
                continue
            compact.append(ln)
            prev_blank = blank
        QApplication.clipboard().setText("\n".join(compact))
        QMessageBox.information(self, "Copied", "Filtered output copied to clipboard.")
    
    def _toggle_generic_fields(self, mode: str):
        enable = (mode == "generic")
        self.ed_start.setEnabled(enable)
        self.ed_end.setEnabled(enable)

    def _browse(self):
        
        path = self.ed_path.text().strip()
        if not path or not os.path.exists(path):
            # ask choose either file or dir
            if self.is_file.isChecked():
                file_path, _ = QFileDialog.getOpenFileName(self, "Select file (or Cancel for directory)")
                if file_path:
                    self.ed_path.setText(file_path)
                else:
                    dir_path = QFileDialog.getExistingDirectory(self, "Select directory")
                    if dir_path:
                        self.ed_path.setText(dir_path)
            else:
                dir_path = QFileDialog.getExistingDirectory(self, "Select directory")
                if dir_path:
                    self.ed_path.setText(dir_path)
        else:
            # if path exists, allow reselect
            if os.path.isfile(path):
                file_path, _ = QFileDialog.getOpenFileName(self, "Select file", os.path.dirname(path))
                if file_path:
                    self.ed_path.setText(file_path)
            else:
                dir_path = QFileDialog.getExistingDirectory(self, "Select directory", path)
                if dir_path:
                    self.ed_path.setText(dir_path)

    def _run(self):
        try:
            path = self.ed_path.text().strip()
            if not path:
                QMessageBox.warning(self, "Error", "Please provide a path (file or directory).")
                return
            param = self.ed_param.text().strip() or ""
            mode = self.cb_mode.currentText()
            start = self.ed_start.text().strip() or None
            end = self.ed_end.text().strip() or None
            include_key = self.chk_include_key.isChecked()
            include_value = self.chk_include_value.isChecked()
            no_std = self.chk_no_standard.isChecked()
            #to_json = self.chk_convert_json.isChecked()
            with_quot_marks = self.chk_include_quotation_marks.isChecked()
            only_strings = self.chk_only_strings.isChecked()
            case_style = self.cb_case.currentText()
            upper = self.chk_upper.isChecked()
            limit = self.ed_limit.text().strip() or "all"
            avoid_keys = self.avoid_keys.text().strip()
            avoid_cut = self.chk_avoid_cut.isChecked()
            indent = self.spin_indent.value()
            is_attribute_mode = self.chk_is_attribute_mode.isChecked()
            exts = [e.strip() for e in self.ed_ext.text().split() if e.strip()]

            extractor = Extractor(
                param=param,
                mode=mode,
                include_key=include_key,
                include_value=include_value,
                no_standard=no_std,
                convert_to_json=True,
                with_quotation_marks=with_quot_marks,
                only_strings=only_strings,
                indentation=indent,
                case_style=case_style,
                limit=limit,
                avoid_keys=avoid_keys,
                avoid_keys_parameter = self.avoid_keys_parameter_message,
                avoid_cut=avoid_cut,
                to_upper=upper,
                start_regex=start,
                end_regex=end,
                file_extensions=exts,
                is_attribute_mode=is_attribute_mode
            )
            text_out, json_out = extractor.run(path)
            self.out_paths.setPlainText(text_out)
            self.out_json.setPlainText(json_out or "")

        except Exception as e:
            QMessageBox.critical(self, "Run error", str(e))

    def _save_outputs(self):
        try:
            text = self.out_paths.toPlainText()
            js = self.out_json.toPlainText()
            if not text and not js:
                QMessageBox.information(self, "Nothing to save", "No outputs to save.")
                return
            # Save paths
            if text:
                fp, _ = QFileDialog.getSaveFileName(self, "Save paths text", "paths.txt")
                if fp:
                    with open(fp, "w", encoding="utf-8") as f:
                        f.write(text)
            # Save JSON
            if js:
                fj, _ = QFileDialog.getSaveFileName(self, "Save JSON", "result.json")
                if fj:
                    with open(fj, "w", encoding="utf-8") as f:
                        f.write(js)
            QMessageBox.information(self, "Saved", "Outputs saved.")
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))


# ------------------------------ Main -----------------------------------------

def main(argv=None):
    argv = argv or sys.argv[1:]
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    # GUI path
    if args.gui:
        if not PYSIDE_OK:
            print("PySide6 not installed. Install with: pip install PySide6", file=sys.stderr)
            return 2
        app = QApplication(sys.argv)
        w = MainWindow()
        w.resize(1000, 700)
        w.show()
        return app.exec()

    # CLI path
    if not args.path:
        ap.error("--path is required in CLI mode")

    extractor = Extractor(
        param=args.param,
        mode=args.mode,
        include_key=args.include_key,
        include_value=args.include_value,
        no_standard=args.no_standard,
        convert_to_json=args.convert_to_json,
        indentation=args.indentation,
        case_style=args.case,
        limit=args.limit,
        avoid_cut=args.avoid_cut,
        to_upper=args.upper,
        start_regex=args.start_delim,
        end_regex=args.end_delim,
        file_extensions=args.ext,
        is_attribute_mode=args.is_attribute_mode
    )

    text_out, json_out = extractor.run(args.path)

    # Write or print
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text_out)
    else:
        print(text_out)

    if args.convert_to_json:
        if args.json_output:
            with open(args.json_output, "w", encoding="utf-8") as f:
                f.write(json_out or "")
        else:
            print("\n--- JSON ---")
            print(json_out or "")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
