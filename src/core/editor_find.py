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
    inverted: bool = False
    inverted_unit: str = "line"


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
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)
_INVERTED_UNITS = {"line", "token", "interval"}


def find_matches(
    text: str,
    query: str,
    options: FindOptions,
    *,
    file_path: str | None = None,
) -> FindResult:
    """Return deterministic, non-overlapping matches under explicit budgets."""
    _validate_inputs(text, query, options)
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
    matches, truncated = _positive_matches(
        text,
        pattern,
        options,
        search_start,
        search_end,
        semantic_spans,
    )
    if options.inverted:
        if truncated:
            raise FindValidationError("positive match budget exceeded for inverted search")
        return _inverted_matches(
            text,
            matches,
            semantic_spans,
            search_start,
            search_end,
            line_offsets,
            options.inverted_unit,
            fallback=fallback,
        )
    return FindResult(tuple(matches), truncated=truncated, scope_fallback=fallback)


def _positive_matches(
    text: str,
    pattern: re.Pattern[str],
    options: FindOptions,
    search_start: int,
    search_end: int,
    semantic_spans: list[tuple[int, int]],
) -> tuple[list[FindMatch], bool]:
    matches: list[FindMatch] = []
    span_starts = [start for start, _end in semantic_spans]
    deadline = time.monotonic() + MAX_SCAN_SECONDS
    for match in pattern.finditer(text, search_start, search_end):
        start, end = match.span()
        if start == end:
            if time.monotonic() > deadline:
                raise FindValidationError("search exceeded the time limit")
            continue
        if options.whole_word and not _is_whole_word(text, start, end):
            continue
        if not _contained_in_spans(start, end, semantic_spans, span_starts):
            continue
        matches.append(FindMatch(start, end))
        if len(matches) >= MAX_MATCHES:
            return matches, True
        if time.monotonic() > deadline:
            raise FindValidationError("search exceeded the time limit")
    return matches, False


def _inverted_matches(
    text: str,
    positive_matches: list[FindMatch],
    semantic_spans: list[tuple[int, int]],
    search_start: int,
    search_end: int,
    line_offsets: list[int],
    unit: str,
    *,
    fallback: bool,
) -> FindResult:
    deadline = time.monotonic() + MAX_SCAN_SECONDS
    if unit == "token":
        candidates = _inverted_token_spans(
            text,
            positive_matches,
            semantic_spans,
            search_start,
            search_end,
            deadline,
        )
    else:
        candidates = _inverted_line_spans(
            text,
            positive_matches,
            semantic_spans,
            search_start,
            search_end,
            line_offsets,
            interval=unit == "interval",
            deadline=deadline,
        )
    truncated = len(candidates) > MAX_MATCHES
    bounded = candidates[:MAX_MATCHES]
    return FindResult(
        tuple(FindMatch(start, end) for start, end in bounded),
        truncated=truncated,
        scope_fallback=fallback,
    )


def _inverted_token_spans(
    text: str,
    positive_matches: list[FindMatch],
    semantic_spans: list[tuple[int, int]],
    search_start: int,
    search_end: int,
    deadline: float,
) -> list[tuple[int, int]]:
    semantic_starts = [start for start, _end in semantic_spans]
    positive_starts = [match.start for match in positive_matches]
    spans: list[tuple[int, int]] = []
    for token in _TOKEN_RE.finditer(text, search_start, search_end):
        start, end = token.span()
        if not _contained_in_spans(start, end, semantic_spans, semantic_starts):
            continue
        if not _overlaps_matches(start, end, positive_matches, positive_starts):
            spans.append((start, end))
            if len(spans) > MAX_MATCHES:
                break
        if time.monotonic() > deadline:
            raise FindValidationError("inverted search exceeded the time limit")
    return spans


def _inverted_line_spans(
    text: str,
    positive_matches: list[FindMatch],
    semantic_spans: list[tuple[int, int]],
    search_start: int,
    search_end: int,
    line_offsets: list[int],
    *,
    interval: bool,
    deadline: float,
) -> list[tuple[int, int]]:
    semantic_starts = [start for start, _end in semantic_spans]
    positive_starts = [match.start for match in positive_matches]
    lines: list[tuple[int, int, bool, bool]] = []
    for index, line_start in enumerate(line_offsets):
        if line_start < search_start or line_start >= search_end:
            continue
        raw_end = line_offsets[index + 1] if index + 1 < len(line_offsets) else len(text)
        line_end = min(raw_end, search_end)
        if line_end > line_start and text[line_end - 1] == "\n":
            line_end -= 1
            if line_end > line_start and text[line_end - 1] == "\r":
                line_end -= 1
        in_scope = _overlaps_spans(
            line_start,
            max(line_end, line_start + 1),
            semantic_spans,
            semantic_starts,
        )
        has_match = _overlaps_matches(
            line_start,
            max(line_end, line_start + 1),
            positive_matches,
            positive_starts,
        )
        lines.append((line_start, line_end, in_scope, has_match))
        if time.monotonic() > deadline:
            raise FindValidationError("inverted search exceeded the time limit")

    if not interval:
        return [
            (start, end)
            for start, end, in_scope, has_match in lines
            if in_scope and not has_match and text[start:end].strip()
        ]

    spans: list[tuple[int, int]] = []
    group_start: int | None = None
    group_end = 0
    for start, end, in_scope, has_match in lines:
        if in_scope and not has_match:
            if group_start is None:
                group_start = start
            group_end = end
            continue
        if group_start is not None and text[group_start:group_end].strip():
            spans.append((group_start, group_end))
        group_start = None
    if group_start is not None and text[group_start:group_end].strip():
        spans.append((group_start, group_end))
    return spans


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


def _validate_inputs(text: str, query: str, options: FindOptions) -> None:
    if len(text) > MAX_TEXT_CHARS:
        raise FindValidationError("document exceeds the find size limit")
    if len(query) > MAX_QUERY_CHARS:
        raise FindValidationError("query exceeds the character limit")
    if len(query.encode("utf-8")) > MAX_QUERY_BYTES:
        raise FindValidationError("query exceeds the UTF-8 size limit")
    if options.inverted_unit not in _INVERTED_UNITS:
        raise FindValidationError("inverted search unit is invalid")


def _compile_pattern(query: str, options: FindOptions) -> re.Pattern[str]:
    source = query if options.regex else re.escape(query)
    flags = re.MULTILINE if options.regex else 0
    if not options.case_sensitive:
        flags |= re.IGNORECASE
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
        if scope == "comments":
            return (_script_comment_spans(text), False) if extension == ".json5" else ([], False)
        if scope == "strings":
            return _quoted_spans(text, {'"'}), False
        return [(match.start() + 1, match.end() - 1) for match in _JSON_KEY_RE.finditer(text)], False
    if extension in _SCRIPT_EXTENSIONS:
        if scope == "comments":
            return _script_comment_spans(text), False
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
            if scope == "comments" and token.type != tokenize.COMMENT:
                continue
            if scope not in {"strings", "variables", "comments"}:
                continue
            start = offsets[token.start[0] - 1] + token.start[1]
            end = offsets[token.end[0] - 1] + token.end[1]
            spans.append((start, end))
    except (IndentationError, tokenize.TokenError):
        return [(0, len(text))], True
    return spans, False


def _script_comment_spans(text: str) -> list[tuple[int, int]]:
    """Return JavaScript/TypeScript/JSON5 comments while skipping strings."""
    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in {'"', "'", "`"}:
            quote = char
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == quote:
                    index += 1
                    break
                index += 1
            continue
        if text.startswith("//", index):
            end = text.find("\n", index + 2)
            end = len(text) if end < 0 else end
            spans.append((index, end))
            index = end
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            end = len(text) if end < 0 else end + 2
            spans.append((index, end))
            index = end
            continue
        index += 1
    return spans


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


def _overlaps_spans(
    start: int,
    end: int,
    spans: list[tuple[int, int]],
    span_starts: list[int],
) -> bool:
    if not spans or end <= start:
        return False
    index = bisect_right(span_starts, end - 1) - 1
    return index >= 0 and spans[index][1] > start


def _overlaps_matches(
    start: int,
    end: int,
    matches: list[FindMatch],
    match_starts: list[int],
) -> bool:
    if not matches or end <= start:
        return False
    index = bisect_right(match_starts, end - 1) - 1
    return index >= 0 and matches[index].end > start
