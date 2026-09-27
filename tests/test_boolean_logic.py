"""Tests for Boolean truth tables and minimization."""

import pytest

from src.boolean_logic import expression_truth_table, minimize_truth_table


def test_expression_generates_truth_table_minterms_and_maxterms():
    result = expression_truth_table("A, B", "A & ~B")

    assert result["minterms"] == [2]
    assert result["maxterms"] == [0, 1, 3]
    assert result["canonical_sop"] == "A & ~B"
    assert len(result["rows"]) == 4


def test_truth_table_minimizes_to_xor_form():
    rows = [
        {"A": 0, "B": 0, "output": 0},
        {"A": 0, "B": 1, "output": 1},
        {"A": 1, "B": 0, "output": 1},
        {"A": 1, "B": 1, "output": 0},
    ]
    result = minimize_truth_table("A,B", rows)

    assert result["minterms"] == [1, 2]
    assert result["minimal_sop"] in {"(A & ~B) | (B & ~A)", "(B & ~A) | (A & ~B)"}
    assert result["minimal_pos"]


def test_parser_rejects_calls_and_too_many_variables():
    with pytest.raises(ValueError, match="Use only"):
        expression_truth_table("A", "open('file')")
    with pytest.raises(ValueError, match="At most"):
        expression_truth_table(",".join(f"v{index}" for index in range(11)), "v0")


def test_inverse_table_requires_every_unique_combination():
    duplicate = [
        {"A": 0, "output": 0},
        {"A": 0, "output": 1},
    ]
    with pytest.raises(ValueError, match="unique"):
        minimize_truth_table("A", duplicate)
