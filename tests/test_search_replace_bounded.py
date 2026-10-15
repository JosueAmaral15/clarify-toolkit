"""Unit tests for bounded in-memory replacement."""

import pytest

from src.core.search_replace import SearchOptions, replace_in_text_bounded


def test_bounded_replace_preserves_options_and_count():
    pattern = SearchOptions(case_sensitive=False, whole_word=True).compile("alpha")

    result, replaced = replace_in_text_bounded(
        "ALPHA alphabet alpha",
        pattern,
        "omega",
        preserve_case=True,
        count=2,
    )

    assert result == "OMEGA alphabet omega"
    assert replaced == 2


def test_bounded_replace_rejects_match_overflow():
    pattern = SearchOptions(case_sensitive=True).compile("a")

    with pytest.raises(ValueError, match="2-match safety limit"):
        replace_in_text_bounded("aaa", pattern, "b", max_matches=2)


def test_bounded_replace_rejects_output_overflow():
    pattern = SearchOptions(case_sensitive=True).compile("a")

    with pytest.raises(ValueError, match="output exceeds"):
        replace_in_text_bounded("a", pattern, "12345", max_output_bytes=4)


def test_bounded_replace_cancellation_returns_original_atomically():
    pattern = SearchOptions(case_sensitive=True).compile("a")
    checks = iter((True, False))

    result, replaced = replace_in_text_bounded(
        "aa",
        pattern,
        "b",
        checkpoint=lambda: next(checks),
    )

    assert result == "aa"
    assert replaced == 0
