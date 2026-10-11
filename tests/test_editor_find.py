"""Pure regressions for Clarify Editor find semantics."""

import pytest

from src.core.editor_find import (
    MAX_MATCHES,
    MAX_QUERY_CHARS,
    FindOptions,
    FindValidationError,
    find_matches,
    replacement_for_match,
)


def spans(result):
    return [(match.start, match.end) for match in result.matches]


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        (FindOptions(), [(0, 3), (4, 7), (8, 11), (12, 15)]),
        (FindOptions(case_sensitive=True), [(0, 3), (4, 7), (12, 15)]),
        (FindOptions(whole_word=True), [(0, 3), (4, 7), (8, 11)]),
        (FindOptions(regex=True, whole_word=True), [(0, 3), (4, 7), (8, 11)]),
    ],
)
def test_case_whole_word_and_regex_share_one_contract(options, expected):
    result = find_matches("foo foo FOO foobar", "foo", options)
    assert spans(result) == expected


def test_line_range_is_inclusive_and_validated():
    text = "hit\nmiss hit\nhit\n"
    result = find_matches(text, "hit", FindOptions(start_line=2, end_line=2))
    assert spans(result) == [(9, 12)]

    with pytest.raises(FindValidationError, match="line range"):
        find_matches(text, "hit", FindOptions(start_line=3, end_line=2))


def test_python_string_and_variable_scopes_are_distinct():
    text = 'name = "name"\nprint(name)\n'
    strings = find_matches(text, "name", FindOptions(scope="strings"), file_path="sample.py")
    variables = find_matches(text, "name", FindOptions(scope="variables"), file_path="sample.py")
    assert spans(strings) == [(8, 12)]
    assert spans(variables) == [(0, 4), (20, 24)]


def test_json_strings_and_keys_have_explicit_scopes():
    text = '{"name": "name", "other": 1}'
    strings = find_matches(text, "name", FindOptions(scope="strings"), file_path="sample.json")
    variables = find_matches(text, "name", FindOptions(scope="variables"), file_path="sample.json")
    assert spans(strings) == [(2, 6), (10, 14)]
    assert spans(variables) == [(2, 6)]


def test_unknown_language_falls_back_honestly():
    result = find_matches("name name", "name", FindOptions(scope="variables"), file_path="notes.txt")
    assert len(result.matches) == 2
    assert result.scope_fallback is True


def test_invalid_python_lexical_scope_falls_back_honestly():
    result = find_matches(
        'name = "unterminated',
        "name",
        FindOptions(scope="variables"),
        file_path="notes.py",
    )
    assert len(result.matches) == 1
    assert result.scope_fallback is True


def test_regex_groups_expand_for_replacement():
    options = FindOptions(regex=True)
    assert replacement_for_match("item-12", r"item-(\d+)", r"value-\1", options) == "value-12"


@pytest.mark.parametrize("query", ["(", "^", "a*"])
def test_invalid_or_empty_matching_regex_is_rejected(query):
    with pytest.raises(FindValidationError):
        find_matches("abc", query, FindOptions(regex=True))


def test_query_and_match_budgets_are_enforced():
    with pytest.raises(FindValidationError, match="character limit"):
        find_matches("text", "x" * (MAX_QUERY_CHARS + 1), FindOptions())

    result = find_matches("x " * (MAX_MATCHES + 1), "x", FindOptions())
    assert len(result.matches) == MAX_MATCHES
    assert result.truncated is True
