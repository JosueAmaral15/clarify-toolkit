"""Generic Scope Parser Module.

Parser driven by user regex for scope start and end delimiters.
Extracted from add/main.py for use in the Clarify project.

Author: Josué Amaral
Date: 2025-12-02
"""

import re
from typing import Iterable, List, Optional, Tuple

# pylint: disable=too-few-public-methods  # Single-purpose parser class
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

    def parse(
        self, text: str, stack: List[str] = None
    ) -> Iterable[Tuple[List[str], str, Optional[str], Optional[str]]]:
        """
        Yields (stack_path, node_name, node_name, value_if_attr_found_or_None).
        - On start match: push node_name (from (?P<name>...) if present, else 'scope')
          and emit a record (with any attribute found next to the start token).
        - On end match: pop one scope.
        """
        if stack is None:
            stack = []

        i = 0
        n = len(text)
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
                tail = text[mstart.end() : mstart.end() + 500]
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
