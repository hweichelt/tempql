"""Test cases for the AST."""

from unittest import TestCase

from tempql.error import ParseError
from tempql.parser import parse
from tests.queries import QUERIES_CORRECT

QUERIES_INCORRECT: tuple[str, ...] = (
    "X[unclosed",
    "P[unopened]]",
    "G[no_time] @",
)


class TestParser(TestCase):
    """Test cases for the parser."""

    def test_parser_correct(self) -> None:
        """Test that the parser parses correctly."""
        for sample in QUERIES_CORRECT:
            query_raw = sample.raw
            with self.subTest(query=query_raw):
                for parsed, expected in zip(parse(query_raw), sample.ast, strict=True):
                    self.assertEqual(parsed, expected)

    def test_parser_incorrect(self) -> None:
        """Test that the parser raises an error on incorrect input."""
        for raw_query in QUERIES_INCORRECT:
            with self.subTest(query=raw_query), self.assertRaises(ParseError):
                parse(raw_query)
