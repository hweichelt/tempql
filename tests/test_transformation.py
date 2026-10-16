"""Test the transformations from an AST Query to a clingo Symbol."""

from unittest import TestCase

from tempql.parser import parse
from tempql.utils import to_symbol
from tests.queries import QUERIES_CORRECT


class TestTransforamation(TestCase):
    """Test cases for the parser."""

    def test_transformation(self) -> None:
        """Test the transformation from AST to clingo Symbol."""
        for sample in QUERIES_CORRECT:
            query_raw = sample.raw
            with self.subTest(query=query_raw):
                for parsed, expected in zip(parse(query_raw), sample.transformed, strict=True):
                    transformed = str(to_symbol(parsed))
                    self.assertEqual(transformed, expected)
