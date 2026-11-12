"""Security boundaries for data written to spreadsheet cells."""

from typing import TypeVar


_Value = TypeVar("_Value")
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def neutralize_spreadsheet_cell(value: _Value) -> _Value | str:
    """Return text that spreadsheet applications will not evaluate as a formula."""
    if isinstance(value, str) and value.startswith(_FORMULA_PREFIXES):
        return f"'{value}"
    return value
