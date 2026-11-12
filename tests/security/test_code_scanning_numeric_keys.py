"""Regressions for bounded flattened-JSON reconstruction (alert #22)."""

import pytest

from src.calculator_operations import CalculatorOperations
from src import set_operations
from src.set_operations import (
    flatten_json,
    preserve_flattened_structure,
    unflatten_json,
)


@pytest.mark.parametrize(
    "source",
    [
        {"items": [1, 2, 3]},
        [{"name": "first"}, {"name": "second"}],
        {"123": "root numeric object key"},
        {"outer": {"123": "nested numeric object key"}},
        {"rows": [{"0": "numeric key inside list"}]},
        {"matrix": [[1, 2], [3, 4]]},
    ],
)
def test_flatten_round_trip_preserves_container_types(source):
    flattened = flatten_json(source)

    assert unflatten_json(flattened) == source


def test_flatten_keeps_public_dot_notation_and_private_list_metadata():
    flattened = flatten_json({"items": ["a", "b"]})

    assert flattened == {"items.0": "a", "items.1": "b"}
    assert flattened.list_paths == frozenset({("items",)})


def test_numeric_object_key_is_not_treated_as_list_index():
    source = {"records": {"1000000000": "value"}}
    flattened = flatten_json(source)

    assert unflatten_json(flattened) == source


def test_oversized_legacy_list_index_is_rejected_before_allocation():
    flattened = {"items.1000000000": "value"}

    with pytest.raises(ValueError, match="requires 1000000001 items"):
        unflatten_json(flattened)

    assert flattened == {"items.1000000000": "value"}


def test_sparse_legacy_list_is_rejected_before_allocation(monkeypatch):
    monkeypatch.setattr(set_operations, "MAX_RECONSTRUCTED_LIST_ITEMS", 100)
    monkeypatch.setattr(set_operations, "MAX_SPARSE_LIST_PADDING", 3)

    with pytest.raises(ValueError, match="placeholder items"):
        unflatten_json({"items.4": "value"})


def test_combined_list_budget_is_checked_before_materialization(monkeypatch):
    monkeypatch.setattr(set_operations, "MAX_TOTAL_RECONSTRUCTED_LIST_ITEMS", 3)
    source = flatten_json({"left": [1, 2], "right": [3, 4]})

    with pytest.raises(ValueError, match="combined limit is 3"):
        unflatten_json(source)


def test_selected_flat_values_retain_list_and_numeric_key_identity():
    source = flatten_json({"rows": [{"0": "keep"}, {"0": "drop"}]})
    selected = preserve_flattened_structure({"rows.0.0": source["rows.0.0"]}, source)

    assert unflatten_json(selected) == {"rows": [{"0": "keep"}]}


def test_calculator_union_preserves_arrays_and_numeric_object_keys():
    left = {"rows": [{"0": "old"}], "left": True}
    right = {"rows": [{"0": "new"}], "right": True}

    success, result, message = CalculatorOperations.union(left, right)

    assert success is True, message
    assert result == {"rows": [{"0": "new"}], "left": True, "right": True}


def test_conflicting_flat_paths_fail_without_returning_partial_output():
    flattened = {"item": "value", "item.child": "conflict"}

    with pytest.raises(ValueError, match="conflicts with a container"):
        unflatten_json(flattened)

    assert flattened == {"item": "value", "item.child": "conflict"}
