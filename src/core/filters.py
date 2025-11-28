"""Advanced file filtering with conditions on filename, path, extension, size, mtime, and content."""

import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Optional

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


def extract_scope_content(text: str, scope_type: str, scope_value: str = "") -> str:
    """
    Extract content within specified scope delimiters.
    
    Args:
        text: The full text to extract from
        scope_type: Type of scope ("brackets", "braces", "custom", "tag", "specific-tag", "" for no scope)
        scope_value: Additional value for custom delimiters or specific tag name
    
    Returns:
        Concatenated content within all matching scopes
    """
    if not scope_type or scope_type == "none":
        return text
    
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
                if depth == 0:
                    start = i + 1
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start != -1:
                    results.append(text[start:i])
                    start = -1
    
    elif scope_type == "parentheses":
        # Extract everything between ( and )
        depth = 0
        start = -1
        for i, char in enumerate(text):
            if char == '(':
                if depth == 0:
                    start = i + 1
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and start != -1:
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
    
    return '\n'.join(results) if results else ""


@dataclass
class Condition:
    field: str              # "filename" | "path" | "ext" | "size" | "mtime" | "content"
    operator: str           # see OPS keys
    value: str
    scope_type: str = ""    # "none" | "brackets" | "braces" | "parentheses" | "custom" | "tag" | "specific-tag"
    scope_value: str = ""   # Additional parameter for custom delimiters or specific tag name
    case_sensitive: bool = True      # Case sensitive matching for string fields
    whole_word: bool = False         # Match whole words only (for contains/not contains)
    use_regex: bool = False          # Use value as regex pattern

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
                    regex_pattern = r'\b' + regex_pattern + r'\b'
                
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
                    return bool(compiled.search(text + '$'))
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

    def matches(self, path: str) -> bool:
        try:
            if self.field == "filename":
                a = os.path.basename(path)
                b = self.value
                return self._apply_string_matching(a, b, self.operator)
            if self.field == "path":
                a = path
                b = self.value
                return self._apply_string_matching(a, b, self.operator)
            if self.field == "ext":
                a = os.path.splitext(path)[1].lstrip(".")
                b = self.value
                return self._apply_string_matching(a, b, self.operator)
            if self.field in ("size", "mtime"):
                st = os.stat(path)
                a = st.st_size if self.field == "size" else st.st_mtime
                b = float(self.value)
                return OPS[self.operator](a, b)
            if self.field == "content":
                txt = read_text(path)
                # Apply scope filtering if specified
                if self.scope_type and self.scope_type != "none":
                    txt = extract_scope_content(txt, self.scope_type, self.scope_value)
                a = txt
                b = self.value
                return self._apply_string_matching(a, b, self.operator)
        except Exception:
            return False
        return False


def filter_files_by_conditions(files: Iterable[str], conds: Sequence[Condition], logic_operator: str = "AND") -> List[str]:
    """
    Evaluate conditions against metadata and, when needed, file content (for 'content' field).
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

    for p in files:
        try:
            if logic_operator == "OR":
                # At least one condition must match (disjunction)
                ok = any(c.matches(p) for c in conds)
            else:
                # All conditions must match (conjunction) - default behavior
                ok = all(c.matches(p) for c in conds)
            
            if ok:
                out.append(p)
        except Exception:
            pass

    return out
