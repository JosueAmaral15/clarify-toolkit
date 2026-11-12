"""Pure regressions for explicit Clarify Editor control escapes."""

import pytest

from src.core.editor_find import (
    FindOptions,
    FindValidationError,
    find_matches,
    replacement_for_match,
)


def _spans(result):
    return [(match.start, match.end) for match in result.matches]


@pytest.mark.parametrize(
    ("query", "text", "expected"),
    [
        (r"first\nsecond", "first\nsecond", [(0, 12)]),
        (r"first\rsecond", "first\rsecond", [(0, 12)]),
        (r"first\tsecond", "first\tsecond", [(0, 12)]),
        (r"first\0second", "first\0second", [(0, 12)]),
        (r"\\n", r"literal \n marker", [(8, 10)]),
    ],
)
def test_literal_control_escapes_are_explicit_and_distinguish_backslash(
    query, text, expected
):
    options = FindOptions(interpret_escapes=True)
    assert _spans(find_matches(text, query, options)) == expected


def test_escape_interpretation_is_opt_in_and_bounded_by_lines():
    text = "first\nsecond\nthird"
    assert not find_matches(text, r"first\nsecond", FindOptions()).matches
    assert not find_matches(
        text,
        r"first\nsecond",
        FindOptions(interpret_escapes=True, start_line=1, end_line=1),
    ).matches
    assert _spans(
        find_matches(
            text,
            r"first\nsecond",
            FindOptions(interpret_escapes=True, start_line=1, end_line=2),
        )
    ) == [(0, 12)]


def test_literal_replacement_interprets_controls_without_touching_other_lines():
    options = FindOptions(interpret_escapes=True)
    assert replacement_for_match("\n", r"\n", r"\t", options) == "\t"
    assert replacement_for_match("\n", r"\n", r"\\n", options) == r"\n"


@pytest.mark.parametrize("value", [r"\x", "trailing\\"])
def test_invalid_literal_control_escape_is_rejected(value):
    options = FindOptions(interpret_escapes=True)
    with pytest.raises(FindValidationError, match="escape"):
        find_matches("text", value, options)
    with pytest.raises(FindValidationError, match="escape"):
        replacement_for_match("text", "text", value, options)


def test_regex_keeps_native_escape_and_backreference_semantics():
    options = FindOptions(regex=True, interpret_escapes=True)
    result = find_matches("item-12\nitem-34", r"item-(\d+)\n", options)
    assert _spans(result) == [(0, 8)]
    assert replacement_for_match(
        "item-12\n", r"item-(\d+)\n", r"value-\1\t", options
    ) == "value-12\t"


def test_control_escape_query_respects_python_string_scope():
    text = 'value = "first\\nsecond"\nother = """first\nsecond"""\n'
    result = find_matches(
        text,
        r"first\nsecond",
        FindOptions(interpret_escapes=True, scope="strings"),
        file_path="sample.py",
    )
    assert [text[match.start : match.end] for match in result.matches] == [
        "first\nsecond"
    ]
