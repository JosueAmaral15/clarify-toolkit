"""Search and replace functionality with regex, case sensitivity, and whole word options."""

import re
from dataclasses import dataclass
from typing import Callable, Tuple

MAX_IN_MEMORY_REPLACE_BYTES = 4 * 1024 * 1024
MAX_IN_MEMORY_REPLACE_MATCHES = 10_000


@dataclass
class SearchOptions:
    """Options for search operations."""

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
                pattern = r"\b" + pattern + r"\b"
        try:
            return re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}") from e


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


def replace_in_text(
    content: str, pattern: re.Pattern, repl: str, preserve_case: bool = False, count: int = 0
) -> Tuple[str, int]:
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


def replace_in_text_bounded(
    content: str,
    pattern: re.Pattern,
    repl: str,
    preserve_case: bool = False,
    count: int = 0,
    *,
    checkpoint: Callable[[], bool] | None = None,
    max_matches: int = MAX_IN_MEMORY_REPLACE_MATCHES,
    max_output_bytes: int = MAX_IN_MEMORY_REPLACE_BYTES,
) -> Tuple[str, int]:
    """Replace text with cooperative checkpoints and bounded output."""
    fragments = []
    last_end = 0
    replacements = 0
    output_bytes = 0

    for match in pattern.finditer(content):
        if checkpoint is not None and not checkpoint():
            return content, 0
        if replacements >= max_matches:
            raise ValueError(f"Replacement exceeds the {max_matches}-match safety limit")

        value = preserve_case_like(match.group(0), repl) if preserve_case else repl
        prefix = content[last_end : match.start()]
        output_bytes += len(prefix.encode("utf-8")) + len(value.encode("utf-8"))
        if output_bytes > max_output_bytes:
            raise ValueError("Replacement output exceeds the 4 MiB safety limit")
        fragments.extend((prefix, value))
        last_end = match.end()
        replacements += 1
        if count and replacements >= count:
            break

    if checkpoint is not None and not checkpoint():
        return content, 0
    suffix = content[last_end:]
    if output_bytes + len(suffix.encode("utf-8")) > max_output_bytes:
        raise ValueError("Replacement output exceeds the 4 MiB safety limit")
    fragments.append(suffix)
    return "".join(fragments), replacements
