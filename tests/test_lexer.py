"""Test cases for the lexer."""

from unittest import TestCase

from tempql.error import ParseError
from tempql.lexer import tokenize
from tests.queries import QUERIES_CORRECT

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
        for sample in QUERIES_CORRECT:
            query_raw = sample.raw
            with self.subTest(query=query_raw):
                for tokenized, expected in zip(tokenize(query_raw), sample.tokens, strict=True):
                    self.assertEqual(tokenized, expected)

    def test_lexer_incorrect(self) -> None:
        """Test that the lexer rejects incorrect queries."""
        for query in QUERIES_INCORRECT:
            with self.subTest(query=query), self.assertRaises(ParseError):
                list(tokenize(query))
