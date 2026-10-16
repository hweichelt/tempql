"""Utility functions for the tempql package."""

from collections.abc import Mapping
from types import MappingProxyType

import clingo
from clingo import Symbol

from src.tempql.ast import BinaryOperator, UnaryOperator
from tempql.ast import Atom, BinaryExpression, Expression, Query, UnaryExpression

type SymbolMapping = Mapping[UnaryOperator | BinaryOperator, str]

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


def to_symbol(
    query: Query,
    mapping: SymbolMapping = DEFAULT_SYMBOL_MAPPING,
    default_timestep: int = DEFAULT_TIMESTEP,
) -> Symbol:
    """Convert a Query to a clingo Symbol."""
    match query:
        case Query(expression, None):
            term = f"query(temporal({_map(expression, mapping)}, {default_timestep}),{DEFAULT_QUERY_INCLUSION})"
            return clingo.parse_term(term)
        case Query(expression, timestep):
            term = f"query(temporal({_map(expression, mapping)}, {default_timestep}),{timestep})"
            return clingo.parse_term(term)


def _map(expression: Expression, mapping: SymbolMapping) -> str:
    match expression:
        case UnaryExpression(operator, expression):
            mapped = mapping[operator]
            return f"{mapped}({_map(expression, mapping)})"
        case BinaryExpression(operator, left, right):
            mapped = mapping[operator]
            return f"{mapped}({_map(left, mapping)},{_map(right, mapping)})"
        case Atom(value):
            return str(value)
