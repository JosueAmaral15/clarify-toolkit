"""Advanced file filtering with conditions on filename, path, extension, size, mtime, and content."""

import os
import math
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from ..utils.file_utils import read_text


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

OPERATOR_ALIASES = {
    "=": "equals", "==": "equals", "!=": "not equals",
    "greater than": ">", "less than": "<",
    "greater than or equal": ">=", "less than or equal": "<=",
}

MAX_CONDITION_TEXT_BYTES = 64 * 1024
MAX_CONDITIONS = 128


def parse_hierarchical_ranges(scope_value: str) -> list[tuple[str, str]]:
    """
    Parse hierarchical include/exclude ranges from scope_value.

    Syntax: "include div#test1, exclude #test2, include #test3"
    Returns: [("include", "div#test1"), ("exclude", "#test2"), ("include", "#test3")]

    Supports:
    - include/exclude directives
    - ID selectors: #myId
    - Tag+ID selectors: div#test1
    - Regex patterns (when use_regex is enabled)
    """
    if not scope_value:
        return []

    ranges = []
    parts = [p.strip() for p in scope_value.split(",")]

    for part in parts:
        if not part:
            continue

        # Parse "include/exclude selector"
        tokens = part.split(None, 1)  # Split on first whitespace
        if len(tokens) == 2:
            action, selector = tokens
            action = action.lower()
            if action in ("include", "exclude"):
                ranges.append((action, selector.strip()))
        elif len(tokens) == 1:
            # No explicit action, default to include
            ranges.append(("include", tokens[0].strip()))

    return ranges


def apply_hierarchical_filter(text: str, ranges: list[tuple[str, str]], use_regex: bool = False,
                              *, max_chars: int | None = None) -> str:
    """
    Apply hierarchical include/exclude filtering to HTML/XML content.

    Args:
        text: The HTML/XML text to filter
        ranges: List of (action, selector) tuples from parse_hierarchical_ranges
        use_regex: Whether to treat selectors as regex patterns
        max_chars: Optional output bound; omitted by legacy consumers

    Returns:
        Filtered text containing only included sections minus excluded sections
    """
    if not ranges:
        return text

    results = []

    for action, selector in ranges:
        if use_regex:
            # Treat selector as regex pattern
            try:
                pattern = re.compile(selector, re.DOTALL | re.IGNORECASE)
                matches = pattern.findall(text)

                if action == "include":
                    results.extend(matches)
                elif action == "exclude":
                    # Remove excluded content from results
                    for match in matches:
                        results = [r for r in results if match not in r]
            except re.error:
                continue
        else:
            # Parse selector (supports #id and tag#id)
            if selector.startswith("#"):
                # ID selector: #myId
                element_id = selector[1:]
                pattern = rf'<[^>]+id=["\']?{re.escape(element_id)}["\']?[^>]*>(.*?)</[^>]+>'
            elif "#" in selector:
                # Tag+ID selector: div#test1
                tag, element_id = selector.split("#", 1)
                pattern = rf'<{re.escape(tag)}[^>]+id=["\']?{re.escape(element_id)}["\']?[^>]*>(.*?)</{re.escape(tag)}>'
            else:
                # Plain tag selector
                pattern = rf'<{re.escape(selector)}[^>]*>(.*?)</{re.escape(selector)}>'

            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

            if action == "include":
                results.extend(matches)
            elif action == "exclude":
                # Remove excluded content from results
                for match in matches:
                    results = [r for r in results if r != match]

        if max_chars is not None and sum(map(len, results)) + max(0, len(results) - 1) > max_chars:
            raise ValueError("Content scope output exceeds the bounded input size")

    return '\n'.join(results) if results else ""


def extract_scope_content(text: str, scope_type: str, scope_value: str = "", use_regex: bool = False,
                          *, max_chars: int | None = None) -> str:
    """
    Extract content within specified scope delimiters.

    Args:
        text: The full text to extract from
        scope_type: Type of scope ("brackets", "braces", "custom", "tag",
            "specific-tag", "hierarchical", "" for no scope)
        scope_value: Additional value for custom delimiters, tag name, ranges
        use_regex: Whether to treat patterns as regex (for hierarchical ranges)
        max_chars: Optional output bound, used by the bounded Explorer evaluator

    Returns:
        Concatenated content within all matching scopes

    Hierarchical Ranges Syntax (scope_type="hierarchical"):
        "include div#test1, exclude #test2, include #test3"
        - include: Add matching content
        - exclude: Remove matching content from results
        - Supports: #id, tag#id, tag, regex patterns
    """
    if not scope_type or scope_type == "none":
        return text

    # Hierarchical include/exclude ranges
    if scope_type == "hierarchical":
        ranges = parse_hierarchical_ranges(scope_value)
        return apply_hierarchical_filter(text, ranges, use_regex, max_chars=max_chars)

    results = []

    if scope_type == "brackets":
        # Extract everything between [ and ]
        pattern = r'\[([^\[\]]*)\]'
        results = re.findall(pattern, text)

    elif scope_type == "braces":
        # Extract everything between { and }
        # Handle nested braces with a more sophisticated approach
        depth = 0
        start = -1
        for i, char in enumerate(text):
            if char == '{':
                if not depth:
                    start = i + 1
                depth += 1
            elif char == '}':
                depth -= 1
                if not depth and start != -1:
                    results.append(text[start:i])
                    start = -1

    elif scope_type == "parentheses":
        # Extract everything between ( and )
        depth = 0
        start = -1
        for i, char in enumerate(text):
            if char == '(':
                if not depth:
                    start = i + 1
                depth += 1
            elif char == ')':
                depth -= 1
                if not depth and start != -1:
                    results.append(text[start:i])
                    start = -1

    elif scope_type == "custom" and scope_value:
        # Extract between custom delimiters (format: "begin,end")
        parts = scope_value.split(",", 1)
        if len(parts) == 2:
            begin, end = parts[0].strip(), parts[1].strip()
            pattern = re.escape(begin) + r'(.*?)' + re.escape(end)
            results = re.findall(pattern, text, re.DOTALL)

    elif scope_type == "tag":
        # Extract content from any HTML/XML tags
        pattern = r'<[^/>]+>(.*?)</[^>]+>'
        results = re.findall(pattern, text, re.DOTALL)

    elif scope_type == "specific-tag" and scope_value:
        # Extract content from specific HTML/XML tag
        tag = scope_value.strip()
        pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
        results = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    if max_chars is not None and sum(map(len, results)) + max(0, len(results) - 1) > max_chars:
        raise ValueError("Content scope output exceeds the bounded input size")
    return '\n'.join(results) if results else ""


@dataclass
class Condition:
    """Represents a filter condition for file attributes."""
    field: str              # "filename" | "path" | "ext" | "size" | "mtime" | "content"
    operator: str           # see OPS keys
    value: str
    scope_type: str = ""    # "none" | "brackets" | "braces" | "parentheses" | "custom" | "tag" | "specific-tag"
    scope_value: str = ""   # Additional parameter for custom delimiters or specific tag name
    case_sensitive: bool = True      # Case sensitive matching for string fields
    whole_word: bool = False         # Match whole words only (for contains/not contains)
    use_regex: bool = False          # Use value as regex pattern

    def __post_init__(self):
        self.operator = OPERATOR_ALIASES.get(self.operator, self.operator)
        if self.operator == "regex":
            self.operator = "contains"
            self.use_regex = True

    @classmethod
    def from_mapping(cls, data):
        """Normalize old UI/preset operators and validate before filtering files."""
        if not isinstance(data, dict):
            raise ValueError("Condition must be a mapping")
        condition = cls(
            field=data.get("field", ""), operator=data.get("operator", ""),
            value=str(data.get("value", "")), scope_type=data.get("scope_type", ""),
            scope_value=data.get("scope_value", ""),
            case_sensitive=data.get("case_sensitive", True),
            whole_word=data.get("whole_word", False),
            use_regex=data.get("regex", data.get("use_regex", False)),
        )
        if condition.field not in {"filename", "path", "ext", "size", "mtime", "content"}:
            raise ValueError("Unknown condition field")
        for text in (condition.value, condition.scope_value):
            if not isinstance(text, str):
                raise ValueError("Condition value and scope parameter must be text")
            if len(text) > MAX_CONDITION_TEXT_BYTES or len(text.encode("utf-8")) > MAX_CONDITION_TEXT_BYTES:
                raise ValueError("Condition value or scope parameter exceeds the 64 KiB limit")
        numeric = condition.field in {"size", "mtime"}
        allowed = {"equals", "not equals", ">", "<", ">=", "<="} if numeric else set(OPS) - {">", "<", ">=", "<="}
        if condition.operator not in allowed:
            raise ValueError("Condition operator does not support the selected field")
        if numeric and not math.isfinite(float(condition.value)):
            raise ValueError("Numeric condition requires a finite value")
        if condition.use_regex and not numeric:
            pattern = condition.value
            if condition.whole_word and condition.operator in {"contains", "not contains"}:
                pattern = r'\b(?:' + pattern + r')\b'
            if condition.operator == "ends with":
                pattern = r'(?:' + pattern + r')\Z'
            re.compile(pattern, 0 if condition.case_sensitive else re.IGNORECASE)
        if condition.field == "content":
            scopes = {"", "none", "brackets", "braces", "parentheses", "custom",
                      "tag", "specific-tag", "hierarchical"}
            if not isinstance(condition.scope_type, str) or condition.scope_type not in scopes:
                raise ValueError("Unknown content condition scope")
            if not isinstance(condition.scope_value, str):
                raise ValueError("Content scope parameter must be text")
            if condition.scope_type == "custom":
                delimiters = condition.scope_value.split(",", 1)
                if len(delimiters) != 2 or not all(part.strip() for part in delimiters):
                    raise ValueError("Custom scope requires nonempty begin,end delimiters")
            if condition.scope_type in {"specific-tag", "hierarchical"} and not condition.scope_value.strip():
                raise ValueError("Selected content scope requires a parameter")
            if condition.scope_type == "specific-tag":
                pattern = re.compile(rf'<{condition.scope_value.strip()}[^>]*>(.*?)</{condition.scope_value.strip()}>')
                if pattern.groups != 1:
                    raise ValueError("Specific tag parameter must not add capture groups")
            if condition.scope_type == "hierarchical":
                ranges = parse_hierarchical_ranges(condition.scope_value)
                if not ranges:
                    raise ValueError("Hierarchical scope requires valid include/exclude selectors")
                for _, selector in ranges:
                    if condition.use_regex and re.compile(selector).groups > 1:
                        raise ValueError("Hierarchical scope regex supports at most one capture group")
        return condition

    # pylint: disable=too-many-return-statements  # String matching requires checking all operators
    def _apply_string_matching(self, text: str, pattern: str, operator: str) -> bool:
        """
        Apply string matching with case sensitivity, whole word, and regex options.
        """
        # Handle regex mode
        if self.use_regex:
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                regex_pattern = pattern

                # Add word boundary if whole_word is enabled
                if self.whole_word and operator in ("contains", "not contains"):
                    regex_pattern = r'\b(?:' + regex_pattern + r')\b'

                compiled = re.compile(regex_pattern, flags)
                found = bool(compiled.search(text))

                if operator == "contains":
                    return found
                elif operator == "not contains":
                    return not found
                elif operator == "equals":
                    return bool(compiled.fullmatch(text))
                elif operator == "not equals":
                    return not bool(compiled.fullmatch(text))
                elif operator == "starts with":
                    return bool(compiled.match(text))
                elif operator == "ends with":
                    return bool(re.search(r'(?:' + regex_pattern + r')\Z', text, flags))
                else:
                    return False
            except re.error:
                return False

        # Non-regex mode
        search_text = text if self.case_sensitive else text.lower()
        search_pattern = pattern if self.case_sensitive else pattern.lower()

        # Handle whole word matching for contains/not contains
        if self.whole_word and operator in ("contains", "not contains"):
            # Use word boundaries
            regex_pattern = r'\b' + re.escape(search_pattern) + r'\b'
            flags = 0 if self.case_sensitive else re.IGNORECASE
            found = bool(re.search(regex_pattern, text, flags))
            return found if operator == "contains" else not found

        # Standard string operations
        if operator == "contains":
            return search_pattern in search_text
        elif operator == "not contains":
            return search_pattern not in search_text
        elif operator == "equals":
            return search_text == search_pattern
        elif operator == "not equals":
            return search_text != search_pattern
        elif operator == "starts with":
            return search_text.startswith(search_pattern)
        elif operator == "ends with":
            return search_text.endswith(search_pattern)

        return False

    # pylint: disable=too-many-return-statements  # Field validation requires early returns
    def matches(self, path: str, *, content: str | None = None,
                max_scope_chars: int | None = None) -> bool:
        """Check if path matches this condition."""
        try:
            if self.field == "filename":
                actual_value = os.path.basename(path)
                expected_value = self.value
                return self._apply_string_matching(actual_value, expected_value, self.operator)
            if self.field == "path":
                actual_value = path
                expected_value = self.value
                return self._apply_string_matching(actual_value, expected_value, self.operator)
            if self.field == "ext":
                actual_value = os.path.splitext(path)[1].lstrip(".")
                expected_value = self.value if self.use_regex else self.value.lstrip(".")
                return self._apply_string_matching(actual_value, expected_value, self.operator)
            if self.field in ("size", "mtime"):
                st = os.stat(path)
                actual_value = st.st_size if self.field == "size" else st.st_mtime
                expected_value = float(self.value)
                return OPS[self.operator](actual_value, expected_value)
            if self.field == "content":
                txt = read_text(path) if content is None else content
                # Apply scope filtering if specified
                if self.scope_type and self.scope_type != "none":
                    txt = extract_scope_content(txt, self.scope_type, self.scope_value, self.use_regex,
                                                max_chars=max_scope_chars)
                actual_value = txt
                expected_value = self.value
                return self._apply_string_matching(actual_value, expected_value, self.operator)
        except ValueError:
            if max_scope_chars is not None:
                raise
            return False
        except Exception:  # pylint: disable=broad-exception-caught  # Catch all file/parsing errors
            return False
        return False


def filter_files_by_conditions(
    files: Iterable[str], conds: Sequence[Condition], logic_operator: str = "AND"
) -> List[str]:
    """
    Evaluate conditions against metadata and file content.
    
    We read content at most once per file if any content-condition is present.

    Args:
        files: Files to filter
        conds: List of conditions to apply
        logic_operator: "AND" (all conditions must match) or "OR" (at least one must match)
    """
    conds = [c for c in (conds or []) if c.field and c.operator]
    if not conds:
        return list(files)

    out: List[str] = []
    logic_operator = logic_operator.upper()

    for file_path in files:
        try:
            cached_content = None
            content_error = False

            def evaluate(condition):
                nonlocal cached_content, content_error
                if condition.field == "content":
                    if content_error:
                        return False
                    if cached_content is None:
                        try:
                            cached_content = read_text(file_path)
                        except (OSError, UnicodeError):
                            content_error = True
                            return False
                    return condition.matches(file_path, content=cached_content)
                return condition.matches(file_path)

            if logic_operator == "OR":
                # At least one condition must match (disjunction)
                ok = any(evaluate(c) for c in conds)
            else:
                # All conditions must match (conjunction) - default behavior
                ok = all(evaluate(c) for c in conds)

            if ok:
                out.append(file_path)
        except Exception:  # pylint: disable=broad-exception-caught  # Filter robustness
            pass

    return out
