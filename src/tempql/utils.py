"""Utility functions for the tempql package."""

from collections.abc import Mapping
from types import MappingProxyType

import clingo
from clingo import Symbol

from tempql.ast import Atom, BinaryExpression, BinaryOperator, Expression, Query, UnaryExpression, UnaryOperator

type SymbolMapping = Mapping[UnaryOperator | BinaryOperator, str]

DEFAULT_MODEL = r"\mathbf{\text{M}}"
DEFAULT_TIMESTEP = 0
DEFAULT_QUERY_INCLUSION = 1
DEFAULT_SYMBOL_MAPPING: SymbolMapping = MappingProxyType(
    {
        UnaryOperator.NOT: "neg",
        UnaryOperator.NEXT: "x",
        UnaryOperator.PREV: "p",
        UnaryOperator.ALWAYS: "g",
        UnaryOperator.EVENTUALLY: "f",
        BinaryOperator.AND: "con",
        BinaryOperator.OR: "dis",
        BinaryOperator.UNTIL: "u",
        BinaryOperator.SINCE: "s",
    }
)
DEFAULT_TEX_MAPPING: SymbolMapping = MappingProxyType(
    {
        UnaryOperator.NOT: r"\lnot",
        UnaryOperator.NEXT: r"\mathord{\circ}",
        UnaryOperator.PREV: r"\bullet",
        UnaryOperator.ALWAYS: r"\square",
        UnaryOperator.EVENTUALLY: r"\lozenge",
        BinaryOperator.AND: r"\land",
        BinaryOperator.OR: r"\lor",
        BinaryOperator.UNTIL: r"\mathbin{\text{U}}",
        BinaryOperator.SINCE: r"\mathbin{\text{S}}",
    }
)
OPERATOR_PRECEDENCE: Mapping[BinaryOperator, int] = MappingProxyType(
    {
        BinaryOperator.OR: 1,
        BinaryOperator.AND: 2,
        BinaryOperator.UNTIL: 3,
        BinaryOperator.SINCE: 3,
    }
)
DEFAULT_PRECEDENCE: int = 4
TEX_ESCAPES: Mapping[str, str] = MappingProxyType(
    {
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "%": r"\%",
        "$": r"\$",
        "\\": r"\textbackslash{}",
    }
)


def to_symbol(
    query: Query,
    mapping: SymbolMapping = DEFAULT_SYMBOL_MAPPING,
    default_timestep: int = DEFAULT_TIMESTEP,
) -> Symbol:
    """Convert a Query to a clingo Symbol."""
    match query:
        case Query(expression, None):
            term = f"query(temporal({_map_symbol(expression, mapping)}, {default_timestep}),{DEFAULT_QUERY_INCLUSION})"
            return clingo.parse_term(term)
        case Query(expression, timestep):
            term = f"query(temporal({_map_symbol(expression, mapping)}, {timestep}),{DEFAULT_QUERY_INCLUSION})"
            return clingo.parse_term(term)


def _map_symbol(expression: Expression, mapping: SymbolMapping) -> str:
    match expression:
        case UnaryExpression(operator, expression):
            mapped = mapping[operator]
            return f"{mapped}({_map_symbol(expression, mapping)})"
        case BinaryExpression(operator, left, right):
            mapped = mapping[operator]
            return f"{mapped}({_map_symbol(left, mapping)},{_map_symbol(right, mapping)})"
        case Atom(value):
            return str(value)


def to_tex(
    query: Query,
    mapping: SymbolMapping = DEFAULT_TEX_MAPPING,
    default_timestep: int = DEFAULT_TIMESTEP,
    model: str = DEFAULT_MODEL,
) -> str:
    """Convert a Query to a TeX string."""
    match query:
        case Query(expression, None):
            return f"{model}, {default_timestep} \\models {_map_tex(expression, mapping)}"
        case Query(expression, timestep):
            return f"{model}, {timestep} \\models {_map_tex(expression, mapping)}"


def _map_tex(expression: Expression, mapping: SymbolMapping) -> str:
    match expression:
        case UnaryExpression(operator, expression):
            return f"{mapping[operator]} {_wrap(expression, mapping, DEFAULT_PRECEDENCE)}"
        case BinaryExpression(operator, left, right):
            precedence = OPERATOR_PRECEDENCE[operator]
            return f"{_wrap(left, mapping, precedence)} {mapping[operator]} {_wrap(right, mapping, precedence + 1)}"
        case Atom(value):
            return f"\\texttt{{{_escape_tex(str(value))}}}"


def _wrap(expression: Expression, mapping: SymbolMapping, precedence: int) -> str:
    match expression:
        case BinaryExpression(operator, _, _) if OPERATOR_PRECEDENCE.get(operator, DEFAULT_PRECEDENCE) < precedence:
            # Wrap a child with lower operator precedence than surrounding operator
            return f"\\left({_map_tex(expression, mapping)}\\right)"
        case _:
            return _map_tex(expression, mapping)


def _escape_tex(text: str) -> str:
    return "".join(TEX_ESCAPES.get(c, c) for c in text)
