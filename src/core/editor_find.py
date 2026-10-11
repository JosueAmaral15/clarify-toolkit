"""Bounded in-document matching for Clarify Editor."""

from __future__ import annotations

import io
import keyword
import re
import time
import tokenize
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path


class FindValidationError(ValueError):
    """Raised when a find request cannot be evaluated safely."""


@dataclass(frozen=True)
class FindOptions:
    """Immutable options shared by navigation and replacement."""

    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False
    scope: str = "all"
    start_line: int | None = None
    end_line: int | None = None


@dataclass(frozen=True)
class FindMatch:
    """One non-empty match in document coordinates."""

    start: int
    end: int


@dataclass(frozen=True)
class FindResult:
    """Bounded result set plus honest degradation metadata."""

    matches: tuple[FindMatch, ...]
    truncated: bool = False
    scope_fallback: bool = False


MAX_QUERY_CHARS = 4096
MAX_QUERY_BYTES = 16 * 1024
MAX_TEXT_CHARS = 2 * 1024 * 1024
MAX_MATCHES = 10_000
MAX_SCAN_SECONDS = 0.75

_PYTHON_EXTENSIONS = {".py", ".pyw"}
_JSON_EXTENSIONS = {".json", ".jsonl", ".json5"}
_SCRIPT_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
_SCRIPT_KEYWORDS = {
    "as",
    "async",
    "await",
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "debugger",
    "default",
    "delete",
    "do",
    "else",
    "export",
    "extends",
    "false",
    "finally",
    "for",
    "from",
    "function",
    "get",
    "if",
    "implements",
    "import",
    "in",
    "instanceof",
    "interface",
    "let",
    "new",
    "null",
    "of",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "set",
    "static",
    "super",
    "switch",
    "this",
    "throw",
    "true",
    "try",
    "typeof",
    "undefined",
    "var",
    "void",
    "while",
    "with",
    "yield",
}
_IDENTIFIER_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_JSON_KEY_RE = re.compile(r'"(?:\\.|[^"\\])*"(?=\s*:)', re.DOTALL)


def find_matches(
    text: str,
    query: str,
    options: FindOptions,
    *,
    file_path: str | None = None,
) -> FindResult:
    """Return deterministic, non-overlapping matches under explicit budgets."""
    _validate_inputs(text, query)
    if not query:
        return FindResult(())

    line_offsets = _line_offsets(text)
    search_start, search_end = _line_bounds(text, line_offsets, options)
    semantic_spans, fallback = _semantic_spans(text, options.scope, file_path)
    if fallback:
        semantic_spans = [(search_start, search_end)]
    else:
        semantic_spans = _intersect_spans(semantic_spans, search_start, search_end)

    pattern = _compile_pattern(query, options)
    if pattern.match("") is not None:
        raise FindValidationError("regular expression must not match empty text")

    matches: list[FindMatch] = []
    span_starts = [start for start, _end in semantic_spans]
    deadline = time.monotonic() + MAX_SCAN_SECONDS
    truncated = False
    for match in pattern.finditer(text, search_start, search_end):
        start, end = match.span()
        if options.whole_word and not _is_whole_word(text, start, end):
            continue
        if not _contained_in_spans(start, end, semantic_spans, span_starts):
            continue
        matches.append(FindMatch(start, end))
        if len(matches) >= MAX_MATCHES:
            truncated = True
            break
        if time.monotonic() > deadline:
            raise FindValidationError("search exceeded the time limit")
    return FindResult(tuple(matches), truncated=truncated, scope_fallback=fallback)


def replacement_for_match(
    matched_text: str,
    query: str,
    replacement: str,
    options: FindOptions,
) -> str:
    """Expand regex groups using the same options as discovery."""
    if not options.regex:
        return replacement
    pattern = _compile_pattern(query, options)
    match = pattern.fullmatch(matched_text)
    if match is None:
        return replacement
    try:
        return match.expand(replacement)
    except (IndexError, re.error) as error:
        raise FindValidationError(str(error)) from error


def _validate_inputs(text: str, query: str) -> None:
    if len(text) > MAX_TEXT_CHARS:
        raise FindValidationError("document exceeds the find size limit")
    if len(query) > MAX_QUERY_CHARS:
        raise FindValidationError("query exceeds the character limit")
    if len(query.encode("utf-8")) > MAX_QUERY_BYTES:
        raise FindValidationError("query exceeds the UTF-8 size limit")


def _compile_pattern(query: str, options: FindOptions) -> re.Pattern[str]:
    source = query if options.regex else re.escape(query)
    flags = 0 if options.case_sensitive else re.IGNORECASE
    try:
        return re.compile(source, flags)
    except re.error as error:
        raise FindValidationError(str(error)) from error


def _is_word_char(character: str) -> bool:
    return bool(character) and (character.isalnum() or character == "_")


def _is_whole_word(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return not _is_word_char(before) and not _is_word_char(after)


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    offsets.extend(index + 1 for index, char in enumerate(text) if char == "\n")
    return offsets


def _line_bounds(text: str, offsets: list[int], options: FindOptions) -> tuple[int, int]:
    line_count = len(offsets)
    start_line = options.start_line or 1
    end_line = options.end_line or line_count
    if start_line < 1 or end_line < 1 or start_line > line_count:
        raise FindValidationError("line range is outside the document")
    if end_line > line_count or start_line > end_line:
        raise FindValidationError("line range is invalid")
    start = offsets[start_line - 1]
    end = offsets[end_line] if end_line < line_count else len(text)
    return start, end


def _semantic_spans(text: str, scope: str, file_path: str | None) -> tuple[list[tuple[int, int]], bool]:
    if scope == "all":
        return [(0, len(text))], False
    extension = Path(file_path or "").suffix.lower()
    if extension in _PYTHON_EXTENSIONS:
        return _python_spans(text, scope)
    if extension in _JSON_EXTENSIONS:
        if scope == "strings":
            return _quoted_spans(text, {'"'}), False
        return [(match.start() + 1, match.end() - 1) for match in _JSON_KEY_RE.finditer(text)], False
    if extension in _SCRIPT_EXTENSIONS:
        if scope == "strings":
            return _quoted_spans(text, {'"', "'", "`"}), False
        return [match.span() for match in _IDENTIFIER_RE.finditer(text) if match.group() not in _SCRIPT_KEYWORDS], False
    return [(0, len(text))], True


def _python_spans(text: str, scope: str) -> tuple[list[tuple[int, int]], bool]:
    offsets = _line_offsets(text)
    spans: list[tuple[int, int]] = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            if scope == "strings" and token.type != tokenize.STRING:
                continue
            if scope == "variables" and (token.type != tokenize.NAME or keyword.iskeyword(token.string)):
                continue
            if scope not in {"strings", "variables"}:
                continue
            start = offsets[token.start[0] - 1] + token.start[1]
            end = offsets[token.end[0] - 1] + token.end[1]
            spans.append((start, end))
    except (IndentationError, tokenize.TokenError):
        return [(0, len(text))], True
    return spans, False


def _quoted_spans(text: str, quotes: set[str]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(text):
        quote = text[index]
        if quote not in quotes:
            index += 1
            continue
        start = index
        index += 1
        escaped = False
        while index < len(text):
            char = text[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                index += 1
                spans.append((start, index))
                break
            index += 1
    return spans


def _intersect_spans(spans: list[tuple[int, int]], start: int, end: int) -> list[tuple[int, int]]:
    return [
        (max(span_start, start), min(span_end, end))
        for span_start, span_end in spans
        if span_end > start and span_start < end
    ]


def _contained_in_spans(
    start: int,
    end: int,
    spans: list[tuple[int, int]],
    span_starts: list[int],
) -> bool:
    if not spans:
        return False
    index = bisect_right(span_starts, start) - 1
    return index >= 0 and start >= spans[index][0] and end <= spans[index][1]
