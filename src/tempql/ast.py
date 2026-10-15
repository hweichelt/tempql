"""AST for the temporal query language."""

from dataclasses import dataclass
from enum import Enum

from clingo import Symbol


class UnaryOperator(Enum):
    """Unary operator for the temporal query language."""

    NOT = "-"
    NEXT = "X"
    PREV = "P"
    ALWAYS = "G"
    EVENTUALLY = "F"


class BinaryOperator(Enum):
    """Binary operator for the temporal query language."""

    AND = "&"
    OR = "|"
    UNTIL = "U"
    SINCE = "S"


type Expression = Atom | UnaryExpression | BinaryExpression


@dataclass(frozen=True)
class Atom:
    """Clingo atom."""

    symbol: Symbol


@dataclass(frozen=True)
class UnaryExpression:
    """Unary expression."""

    operator: UnaryOperator
    expression: Expression


@dataclass(frozen=True)
class BinaryExpression:
    """Binary expression."""

    operator: BinaryOperator
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Query:
    """Query."""

    expression: Expression
    timestep: int | None
