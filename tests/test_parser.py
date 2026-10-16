"""Test cases for the AST."""

from collections.abc import Mapping
from types import MappingProxyType
from unittest import TestCase

import clingo

from tempql.ast import Atom, BinaryExpression, BinaryOperator, Query, UnaryExpression, UnaryOperator
from tempql.error import ParseError
from tempql.parser import parse

QUERIES_CORRECT: Mapping[str, tuple[Query, ...]] = MappingProxyType(
    {
        "a | b | c": (
            Query(
                BinaryExpression(
                    BinaryOperator.OR,
                    BinaryExpression(BinaryOperator.OR, Atom(clingo.parse_term("a")), Atom(clingo.parse_term("b"))),
                    Atom(clingo.parse_term("c")),
                ),
                None,
            ),
        ),
        "a & b": (
            Query(
                BinaryExpression(
                    BinaryOperator.AND,
                    Atom(clingo.parse_term("a")),
                    Atom(clingo.parse_term("b")),
                ),
                None,
            ),
        ),
        "U[until, F[eventually]] @ 2": (
            Query(
                BinaryExpression(
                    BinaryOperator.UNTIL,
                    Atom(clingo.parse_term("until")),
                    UnaryExpression(UnaryOperator.EVENTUALLY, Atom(clingo.parse_term("eventually"))),
                ),
                2,
            ),
        ),
        "\nmultiple;;;X[queries(2)];": (
            Query(
                Atom(clingo.parse_term("multiple")),
                None,
            ),
            Query(
                UnaryExpression(
                    UnaryOperator.NEXT,
                    Atom(clingo.parse_term("queries(2)")),
                ),
                None,
            ),
        ),
    }
)

QUERIES_INCORRECT: tuple[str, ...] = (
    "X[unclosed",
    "P[unopened]]",
    "G[no_time] @",
)


class TestParser(TestCase):
    """Test cases for the parser."""

    def test_parser_correct(self) -> None:
        """Test that the parser parses correctly."""
        for raw_query, expected in QUERIES_CORRECT.items():
            with self.subTest(query=raw_query):
                for query_pared, query_expected in zip(parse(raw_query), expected, strict=True):
                    self.assertEqual(query_pared, query_expected)

    def test_parser_incorrect(self) -> None:
        """Test that the parser raises an error on incorrect input."""
        for raw_query in QUERIES_INCORRECT:
            with self.subTest(query=raw_query), self.assertRaises(ParseError):
                parse(raw_query)
