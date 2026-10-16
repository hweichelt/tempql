"""Test cases for the lexer."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final
from unittest import TestCase

import clingo

from tempql.ast import BinaryOperator, UnaryOperator
from tempql.error import ParseError
from tempql.lexer import Token, TokenType, tokenize

QUERIES_CORRECT: Final[Mapping[str, tuple[Token, ...]]] = MappingProxyType(
    {
        "": (Token(TokenType.EOF, "", 0, 0),),
        "F[o]": (
            Token(TokenType.OPERATOR, "F", 0, 1, UnaryOperator.EVENTUALLY),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "o", 2, 3, clingo.parse_term("o")),
            Token(TokenType.RBRACKET, "]", 3, 4),
            Token(TokenType.EOF, "", 4, 4),
        ),
        "unwrapped | (wrapped)": (
            Token(TokenType.ATOM, "unwrapped", 0, 9, clingo.parse_term("unwrapped")),
            Token(TokenType.OR, "|", 10, 11),
            Token(TokenType.LPAREN, "(", 12, 13),
            Token(TokenType.ATOM, "wrapped", 13, 20, clingo.parse_term("wrapped")),
            Token(TokenType.RPAREN, ")", 20, 21),
            Token(TokenType.EOF, "", 21, 21),
        ),
        "line\nnewline": (
            Token(TokenType.ATOM, "line", 0, 4, clingo.parse_term("line")),
            Token(TokenType.SEPARATOR, "\n", 4, 5),
            Token(TokenType.ATOM, "newline", 5, 12, clingo.parse_term("newline")),
            Token(TokenType.EOF, "", 12, 12),
        ),
        "007": (
            Token(TokenType.NUMBER, "007", 0, 3, 7),
            Token(TokenType.EOF, "", 3, 3),
        ),
        "atom_with_underscore": (
            Token(TokenType.ATOM, "atom_with_underscore", 0, 20, clingo.parse_term("atom_with_underscore")),
            Token(TokenType.EOF, "", 20, 20),
        ),
        "_start_with_underscore": (
            Token(TokenType.ATOM, "_start_with_underscore", 0, 22, clingo.parse_term("_start_with_underscore")),
            Token(TokenType.EOF, "", 22, 22),
        ),
        'string("it \\"escaped\\"")': (
            Token(TokenType.ATOM, 'string("it \\"escaped\\"")', 0, 24, clingo.parse_term('string("it \\"escaped\\"")')),
            Token(TokenType.EOF, "", 24, 24),
        ),
        "served@123": (
            Token(TokenType.ATOM, "served", 0, 6, clingo.parse_term("served")),
            Token(TokenType.AT, "@", 6, 7),
            Token(TokenType.NUMBER, "123", 7, 10, 123),
            Token(TokenType.EOF, "", 10, 10),
        ),
        'X[raw(")[")]': (
            Token(TokenType.OPERATOR, "X", 0, 1, UnaryOperator.NEXT),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, 'raw(")[")', 2, 11, clingo.parse_term('raw(")[")')),
            Token(TokenType.RBRACKET, "]", 11, 12),
            Token(TokenType.EOF, "", 12, 12),
        ),
        'U[test,wrap("some string @%")]': (
            Token(TokenType.OPERATOR, "U", 0, 1, BinaryOperator.UNTIL),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "test", 2, 6, clingo.parse_term("test")),
            Token(TokenType.COMMA, ",", 6, 7),
            Token(TokenType.ATOM, 'wrap("some string @%")', 7, 29, clingo.parse_term('wrap("some string @%")')),
            Token(TokenType.RBRACKET, "]", 29, 30),
            Token(TokenType.EOF, "", 30, 30),
        ),
        "S[at(1, 2), spaces] @ 3": (
            Token(TokenType.OPERATOR, "S", 0, 1, BinaryOperator.SINCE),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "at(1, 2)", 2, 10, clingo.parse_term("at(1,2)")),
            Token(TokenType.COMMA, ",", 10, 11),
            Token(TokenType.ATOM, "spaces", 12, 18, clingo.parse_term("spaces")),
            Token(TokenType.RBRACKET, "]", 18, 19),
            Token(TokenType.AT, "@", 20, 21),
            Token(TokenType.NUMBER, "3", 22, 23, 3),
            Token(TokenType.EOF, "", 23, 23),
        ),
        "-X[at(1)] & G[served] @ 42; test": (
            Token(TokenType.NOT, "-", 0, 1),
            Token(TokenType.OPERATOR, "X", 1, 2, UnaryOperator.NEXT),
            Token(TokenType.LBRACKET, "[", 2, 3),
            Token(TokenType.ATOM, "at(1)", 3, 8, clingo.parse_term("at(1)")),
            Token(TokenType.RBRACKET, "]", 8, 9),
            Token(TokenType.AND, "&", 10, 11),
            Token(TokenType.OPERATOR, "G", 12, 13, UnaryOperator.ALWAYS),
            Token(TokenType.LBRACKET, "[", 13, 14),
            Token(TokenType.ATOM, "served", 14, 20, clingo.parse_term("served")),
            Token(TokenType.RBRACKET, "]", 20, 21),
            Token(TokenType.AT, "@", 22, 23),
            Token(TokenType.NUMBER, "42", 24, 26, 42),
            Token(TokenType.SEPARATOR, ";", 26, 27),
            Token(TokenType.ATOM, "test", 28, 32, clingo.parse_term("test")),
            Token(TokenType.EOF, "", 32, 32),
        ),
    }
)

QUERIES_INCORRECT: tuple[str, ...] = (
    "B",
    "_",
    '"string?"',
    "äöüï",
    'wrong(clingo(\\"string))',
    "clingo(forgot(to(close))",
    "wrong(clingo(,))",
    "variable(O)",
)


class TestLexer(TestCase):
    """Test cases for the lexer."""

    def test_lexer_correct(self) -> None:
        """Test that the lexer tokenizes queries correctly."""
        for query, expected in QUERIES_CORRECT.items():
            with self.subTest(query=query):
                for token_tokenized, token_expexted in zip(tokenize(query), expected, strict=True):
                    self.assertEqual(token_tokenized, token_expexted)

    def test_lexer_incorrect(self) -> None:
        """Test that the lexer rejects incorrect queries."""
        for query in QUERIES_INCORRECT:
            with self.subTest(query=query), self.assertRaises(ParseError):
                list(tokenize(query))
