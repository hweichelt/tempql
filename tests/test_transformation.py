"""Test the transformations from an AST Query to a clingo Symbol."""

from collections.abc import Mapping
from types import MappingProxyType
from unittest import TestCase

from tempql.parser import parse
from tempql.utils import to_symbol

QUERIES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "query1": ("query(temporal(query1,0),1)",),
    }
)


class TestTransforamation(TestCase):
    """Test cases for the parser."""

    def test_transformation(self) -> None:
        """Test the transformation from AST to clingo Symbol."""
        for raw_query, expected in QUERIES.items():
            with self.subTest(query=raw_query):
                for parsed, correct in zip(parse(raw_query), expected, strict=True):
                    parsed_symbol = to_symbol(parsed)
                    self.assertEqual(str(parsed_symbol), correct)
