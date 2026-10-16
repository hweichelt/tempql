"""Lexer for the temporal query language."""

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum, auto
from string import ascii_lowercase, ascii_uppercase, digits

import clingo
from clingo import Symbol

from .ast import BinaryOperator, UnaryOperator
from .error import ParseError


class TokenType(Enum):
    """Type of a token."""

    AND = auto()
    ATOM = auto()
    AT = auto()
    COMMA = auto()
    EOF = auto()
    LBRACKET = auto()
    LPAREN = auto()
    NOT = auto()
    NUMBER = auto()
    OPERATOR = auto()
    OR = auto()
    RBRACKET = auto()
    RPAREN = auto()
    SEPARATOR = auto()

    def __eq__(self, other: object) -> bool:
        """Check if two token types are equal."""
        if not isinstance(other, TokenType):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class Token:
    """Parsed token of the query."""

    type: TokenType
    raw: str
    start: int
    end: int
    value: UnaryOperator | BinaryOperator | Symbol | int | None = None

    def __eq__(self, other: object) -> bool:
        """Check if two tokens are equal."""
        if not isinstance(other, Token):
            return False
        return (
            self.type == other.type
            and self.raw == other.raw
            and self.start == other.start
            and self.end == other.end
            and self.value == other.value
        )


CHARACTER_MAPPINGS: dict[str, TokenType] = {
    "&": TokenType.AND,
    "@": TokenType.AT,
    ",": TokenType.COMMA,
    "[": TokenType.LBRACKET,
    "(": TokenType.LPAREN,
    "-": TokenType.NOT,
    "|": TokenType.OR,
    "]": TokenType.RBRACKET,
    ")": TokenType.RPAREN,
    ";": TokenType.SEPARATOR,
    "\n": TokenType.SEPARATOR,
}
TEMPORAL_OPERATORS: dict[str, UnaryOperator | BinaryOperator] = {
    o.value: o for o in (*UnaryOperator, *BinaryOperator) if o.value not in CHARACTER_MAPPINGS
}
CLINGO_PREDICATE_NAME_START_CHARACTERS = {"_"} | set(ascii_lowercase)
CLINGO_PREDICATE_NAME_CHARACTERS = set(ascii_lowercase) | set(ascii_uppercase) | set(digits) | {"_", "'"}


def tokenize(raw: str) -> Iterator[Token]:
    """Tokenizes the given raw string into a list of tokens."""
    i = 0
    while i < len(raw):
        if raw[i].isspace() and raw[i] != "\n":
            i += 1
            continue
        if raw[i] in CHARACTER_MAPPINGS:
            yield Token(CHARACTER_MAPPINGS[raw[i]], raw[i], i, i + 1)
            i = i + 1
            continue
        if raw[i] in TEMPORAL_OPERATORS:
            yield Token(TokenType.OPERATOR, raw[i], i, i + 1, TEMPORAL_OPERATORS[raw[i]])
            i = i + 1
            continue
        if raw[i].isdecimal():
            raw_number, number, j = _parse_number(raw, i)
            yield Token(TokenType.NUMBER, raw_number, i, j, number)
            i = j
            continue
        if raw[i] in CLINGO_PREDICATE_NAME_START_CHARACTERS:
            raw_symbol, symbol, j = _parse_clingo_symbol(raw, i)
            yield Token(TokenType.ATOM, raw_symbol, i, j, symbol)
            i = j
            continue
        raise ParseError(f"Unexpected character encountered during parsing: {raw[i]}", i, i + 1)
    yield Token(TokenType.EOF, "", len(raw), len(raw))


def _parse_number(raw: str, start: int) -> tuple[str, int, int]:
    end = start
    while end < len(raw) and raw[end].isdecimal():
        end += 1
    return raw[start:end], int(raw[start:end]), end


def _parse_clingo_symbol(raw: str, start: int) -> tuple[str, Symbol, int]:
    depth = 0
    end = start
    # Skip predicate name until variables start
    while end < len(raw) and raw[end] in CLINGO_PREDICATE_NAME_CHARACTERS:
        end += 1
    # Balance parentheses of predicate arguments if present
    if end < len(raw) and raw[end] == "(":
        depth = 0
        while end < len(raw):
            depth += raw[end] == "("
            depth -= raw[end] == ")"
            end = _skip_string(raw, end + 1) if raw[end] == '"' else end + 1
            if depth == 0:
                break
        else:
            raise ParseError("Unbalanced parentheses in clingo symbol", start, end)
    raw_symbol = raw[start:end]
    try:
        symbol = clingo.parse_term(raw_symbol)
    except RuntimeError as e:
        raise ParseError(str(e), start, end) from e
    return raw_symbol, symbol, end


def _skip_string(raw: str, start: int) -> int:
    end = start
    while end < len(raw):
        match raw[end]:
            case '"':
                break
            case "\\":
                end += 2
            case _:
                end += 1
    else:
        raise ParseError("Unterminated string", start, min(end, len(raw)))
    return end + 1
