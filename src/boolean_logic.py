"""Restricted Boolean expression and truth-table utilities backed by SymPy."""

from __future__ import annotations

import ast
from itertools import product
from typing import Any

from sympy import false, symbols, true
from sympy.logic.boolalg import And, Equivalent, Not, Or, POSform, SOPform, Xor


MAX_VARIABLES = 10


def parse_variable_names(text: str) -> list[str]:
    names = [item.strip() for item in text.replace(";", ",").split(",") if item.strip()]
    if not names:
        raise ValueError("Provide at least one variable")
    if len(names) > MAX_VARIABLES:
        raise ValueError(f"At most {MAX_VARIABLES} variables are supported")
    if len(set(names)) != len(names):
        raise ValueError("Variable names must be unique")
    if any(not name.isidentifier() for name in names):
        raise ValueError("Variable names must be valid identifiers")
    return names


def _parse_boolean_expression(expression: str, names: list[str]):
    """Parse only identifiers, constants, and explicit Boolean operators."""
    symbol_list = symbols(" ".join(names), seq=True)
    symbol_map = dict(zip(names, symbol_list))
    tree = ast.parse(expression, mode="eval")

    def convert(node: ast.AST):
        if isinstance(node, ast.Name) and node.id in symbol_map:
            return symbol_map[node.id]
        if isinstance(node, ast.Constant) and node.value in {0, 1, False, True}:
            return true if bool(node.value) else false
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.Invert, ast.Not)):
            return Not(convert(node.operand))
        if isinstance(node, ast.BinOp):
            operators = {ast.BitAnd: And, ast.BitOr: Or, ast.BitXor: Xor, ast.RShift: Equivalent}
            operation = operators.get(type(node.op))
            if operation:
                return operation(convert(node.left), convert(node.right))
        if isinstance(node, ast.BoolOp):
            operation = And if isinstance(node.op, ast.And) else Or if isinstance(node.op, ast.Or) else None
            if operation:
                return operation(*(convert(value) for value in node.values))
        raise ValueError("Use only declared variables, 0/1, parentheses, ~, &, |, ^, and >> (equivalence)")

    return convert(tree.body), symbol_list


def expression_truth_table(variable_text: str, expression: str) -> dict[str, Any]:
    names = parse_variable_names(variable_text)
    parsed, symbol_list = _parse_boolean_expression(expression, names)
    rows = []
    minterms = []
    maxterms = []
    for index, values in enumerate(product((0, 1), repeat=len(names))):
        substitutions = dict(zip(symbol_list, (bool(value) for value in values)))
        output = int(bool(parsed.subs(substitutions)))
        rows.append({**dict(zip(names, values)), "output": output})
        (minterms if output else maxterms).append(index)
    return {
        "type": "truth_table",
        "variables": names,
        "expression": str(parsed),
        "rows": rows,
        "minterms": minterms,
        "maxterms": maxterms,
        "canonical_sop": str(SOPform(symbol_list, minterms)),
        "canonical_pos": str(POSform(symbol_list, minterms)),
    }


def minimize_truth_table(variable_text: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Minimize output=1 rows through SymPy's Quine-McCluskey-compatible forms."""
    names = parse_variable_names(variable_text)
    expected = 2 ** len(names)
    if len(rows) != expected:
        raise ValueError(f"Expected exactly {expected} rows for {len(names)} variables")
    minterms = []
    normalized_rows = []
    seen_inputs = set()
    for row in rows:
        try:
            values = tuple(int(row[name]) for name in names)
            output = int(row["output"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Every row must contain 0/1 values for all variables and output") from exc
        if any(value not in {0, 1} for value in (*values, output)):
            raise ValueError("Truth-table values must be 0 or 1")
        if values in seen_inputs:
            raise ValueError("Truth-table input rows must be unique")
        seen_inputs.add(values)
        index = sum(value << (len(names) - position - 1) for position, value in enumerate(values))
        if output:
            minterms.append(index)
        normalized_rows.append({**dict(zip(names, values)), "output": output})
    if len(seen_inputs) != expected:
        raise ValueError("Truth table does not cover every input combination")
    symbol_list = symbols(" ".join(names), seq=True)
    return {
        "type": "boolean_minimization",
        "method": "SymPy SOPform/POSform (Quine-McCluskey-style exact minimization for bounded inputs)",
        "variables": names,
        "rows": normalized_rows,
        "minterms": sorted(minterms),
        "maxterms": sorted(set(range(expected)) - set(minterms)),
        "minimal_sop": str(SOPform(symbol_list, minterms)),
        "minimal_pos": str(POSform(symbol_list, minterms)),
    }
