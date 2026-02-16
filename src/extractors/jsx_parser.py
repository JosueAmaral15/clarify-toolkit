"""JSX Parser Module.
# pylint: disable=too-many-nested-blocks,no-else-continue,consider-using-in,duplicate-code  # Complex JSX parsing

Minimal JSX/TSX parser for extracting parameters and attributes from React components.
Extracted from add/main.py for use in the Clarify project.

Features:
- Detect opening tags <Tag ...> and self-closing <Tag .../>
- Detect closing tags </Tag>
- Extract attributes (key="..." | key={'...'} | key={...expr...})
- Handle nested tags with proper depth tracking
- Extract tag content (text and expressions)
- Support for both attribute mode and tag-content mode

Author: Josué Amaral
Date: 2025-12-02
"""

import re
from typing import Iterable, List, Optional, Tuple


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

    def __init__(
        self, param_name: str, match_all: bool = False, is_attribute_mode: bool = False, no_standard: bool = False
    ):
        self.param_name = param_name
        self.match_all = match_all
        self.is_attribute_mode = is_attribute_mode
        self.no_standard = no_standard
        self.items = []
        self.class_map = {}  # Store class attributes: {(tuple(stack), tag): "class-value"}

    def clear_items_and_reset(self):
        """Reset items list."""
        self.items = []
        self.class_map = {}

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
        # pylint: disable=invalid-name  # JSX delimiter constants
        GREATER_THAN = ">"
        LOWER_THAN = "<"
        greater_than_count = 0
        lower_than_count = 0
        difference_appearance_signs = 0
        brace_depth = 0

        while i < n:

            mclose = close_pat.match(text, i)
            if mclose and in_quote is None and apostrophe is None and not brace_depth:
                depth -= 1
                if not depth:
                    return (mclose.start(), mclose.end())
                i = mclose.end()
                continue
            # quick check for an opening same-name tag at i (increases depth)
            mopen = open_pat.match(text, i)
            if mopen and in_quote is None and apostrophe is None and not brace_depth:
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
                if (ch == GREATER_THAN and re.match(r"[//\w\<\}\d]", text[i - 1])) or (
                    ch == LOWER_THAN and re.match(r"[//\w\>]", text[i + 1])
                ):

                    if ch == GREATER_THAN:
                        greater_than_count += 1
                    elif ch == LOWER_THAN:
                        lower_than_count += 1

                    difference_appearance_signs = lower_than_count - greater_than_count

            if difference_appearance_signs:
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
            if mclose and in_quote is None and not brace_depth:
                depth -= 1
                if not depth:
                    return (mclose.start(), mclose.end())
                i = mclose.end()
                continue

            # quick check for an opening same-name tag at i (increases depth)
            mopen = open_pat.match(text, i)
            if mopen and in_quote is None and not brace_depth:
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
                if ch in ("'", '"'):
                    in_quote = ch
                elif ch == "{":
                    brace_depth += 1
                elif ch == "}":
                    if brace_depth > 0:
                        brace_depth -= 1
                elif ch == ">" and not brace_depth:
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
                    char = s[j]
                    if in_quote:
                        if char == "\\":
                            j += 2
                            continue
                        if char == in_quote:
                            in_quote = None
                        j += 1
                        continue
                    else:
                        if char in ("'", '"'):
                            in_quote = char
                            j += 1
                            continue
                        if char == "{":
                            brace_depth += 1
                            j += 1
                            continue
                        if char == "}":
                            if brace_depth > 0:
                                brace_depth -= 1
                            j += 1
                            continue
                        if char == ">" and not brace_depth:
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
                    char = inner[j]
                    if in_quote:
                        if char == "\\":
                            j += 2
                            continue
                        if char == in_quote:
                            in_quote = None
                        j += 1
                        continue
                    else:
                        if char in ("'", '"'):
                            in_quote = char
                            j += 1
                            continue
                        if char == "{":
                            brace_depth += 1
                            j += 1
                            continue
                        if char == "}":
                            if brace_depth > 0:
                                brace_depth -= 1
                            j += 1
                            continue
                        if char == ">" and not brace_depth:
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
        if not s or start >= len(s) or s[start] != "{":
            raise ValueError(f"Expected '{{' at position {start}")
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
                    if not depth:
                        return (s[start + 1 : i], i + 1)
                    i += 1
                    continue
                i += 1
        raise ValueError("Unbalanced brace expression")

    def parse(
        self, text: str, stack: List[str] = None
    ) -> Iterable[Tuple[List[str], str, Optional[str], Optional[str]]]:
        """
        Parse JSX/TSX text and yield tuples of (stack, tag, key_matched, value).

        Args:
            text: JSX/TSX source code
            stack: Current tag stack (for recursive calls)

        Yields:
            Tuples of (stack_path, tag_name, attribute_key, attribute_value)
        """
        if stack is None:
            stack = []

        i = 0
        n = len(text)
        while i < n:
            mclose = self.TAG_CLOSE_RE.match(text, i)
            if mclose:
                tag = mclose.group(1)
                for j in range(len(stack) - 1, -1, -1):
                    if stack[j] == tag:
                        stack = stack[:j]
                        break
                i = mclose.end()
                continue

            mopen = self.match_opening_tag(text, i)
            if mopen:
                tag = mopen["tag"]
                attrs_src = mopen["attrs"] or ""
                is_self = mopen["self_closing"]
                have_close_tag = bool(re.findall(rf"</\s*({tag})\s*>", text))
                stack.append(tag)
                
                # Extract class attribute if present (store after stack.append)
                # Match both 'class' (HTML) and 'className' (JSX/React)
                class_match = re.search(r'\b(?:class|className)\s*=\s*["\']([^"\']+)["\']', attrs_src, re.IGNORECASE)
                if class_match:
                    class_value = class_match.group(1).strip()
                    # Store with current stack position (including current tag)
                    stack_key = (tuple(stack), tag)
                    self.class_map[stack_key] = class_value

                # =========================
                # TAG-CONTENT MODE (UNCHECKED)
                # =========================
                if not self.is_attribute_mode:
                    if self.match_all or (tag == self.param_name):
                        if is_self or not have_close_tag:
                            inner = ""
                            items = []
                            span = None
                        else:
                            span = self._custom_find_matching_close_span(text, tag, mopen["end"])
                            inner = text[mopen["end"] : span[0]] if span else ""
                            items = self._extract_non_tag_items(inner)

                        if inner and not self.no_standard:
                            for s, t1, t2, item in self.parse(inner, stack):
                                yield (s, t1, t2, item)

                        for it in items:
                            new_item = it.strip()
                            if new_item and new_item not in self.items:
                                self.items.append(new_item)
                                yield (list(stack), tag, tag, new_item)

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
                    for rx in (
                        self.ATTR_DQ_RE,
                        self.ATTR_SQ_RE,
                        self.ATTR_BRACE_STRING_RE,
                        self.ATTR_BRACE_DQSTRING_RE,
                    ):
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

                yield (list(stack), tag, key_matched, value_text)

                if is_self or not have_close_tag:
                    stack.pop()
                i = mopen["end"]
                continue

            i += 1
