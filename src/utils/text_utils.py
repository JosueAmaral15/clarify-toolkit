"""Text processing utilities for masking, exclusions, and regex compilation."""

import re


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

    guards: list[str] = []
    token_prefix = "@@XCL"
    token_suffix = "@@"

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
    """Restore masked exclusions to original text."""
    token_prefix = "@@XCL"
    token_suffix = "@@"
    for i, original in enumerate(guards):
        text = text.replace(f"{token_prefix}{i}{token_suffix}", original)
    return text


def _escape_variants_for_quotes(s: str) -> list[str]:
    """
    Return regex-safe variants of the same text so we can match values written with
    real quotes/apostrophes or with escaped forms (\" \').
    """
    base = re.escape(s)
    variants = { base }

    if '"' in s:
        variants.add(re.escape(s.replace('"', '\\"')))
    if "'" in s:
        variants.add(re.escape(s.replace("'", "\\'")))
    if "\\\"" in s or "\\\'" in s:
        variants.add(re.escape(s.replace("\\\"", "\"").replace("\\\'", "'")))

    return list(variants)


def compile_value_union_regex(value_to_key: dict[str, str]) -> re.Pattern:
    """
    Build a single alternation regex with named groups for each value.
    Sort by length (desc) to prefer the longest phrase first.
    """
    items = sorted(value_to_key.items(), key=lambda kv: len(kv[0]), reverse=True)

    parts = []
    idx = 0
    for val, _key in items:
        if not val:
            continue
        variants = _escape_variants_for_quotes(val)
        if len(variants) == 1:
            body = variants[0]
        else:
            body = "(?:" + "|".join(variants) + ")"
        gname = f"V{idx}"
        parts.append(f"(?P<{gname}>{body})")
        idx += 1

    if not parts:
        return re.compile(r"(?!x)x")

    big = "|".join(parts)
    return re.compile(big)
