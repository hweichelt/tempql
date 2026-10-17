"""Test the semantics module on an example trace."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import cast
from unittest import TestCase

import clingo
from clingo import SolveHandle

from tempql.parser import parse
from tempql.semantics import semantics
from tempql.utils import to_symbol

TRACE = """
model(time(0),foil). model(holds(at(1),0),foil).
model(time(1),foil). model(holds(at(1),1),foil).
model(time(2),foil). model(holds(at(1),2),foil). model(holds(called(3),2),foil).
model(time(3),foil). model(holds(at(2),3),foil). model(holds(called(3),3),foil).
model(time(4),foil). model(holds(at(3),4),foil). model(holds(called(3),4),foil).
model(time(5),foil). model(holds(at(3),5),foil). model(holds(served(3),5),foil).
"""

RULE_FORCE_QUERY = ":- query(temporal(Q,T),_), not holds(Q,T)."

QUERIES: Mapping[str, bool] = MappingProxyType(
    {
        "at(1) @ 0": True,
        "at(1) @ 1": True,
        "at(1) @ 2": True,
        "at(1) @ 3": False,
        "at(1) @ 4": False,
        "at(1) @ 5": False,
        "P[at(1)] @ 0": False,
        "X[at(1)] @ 0": True,
        "-at(3) @ 0": True,
        "-G[at(1)]": True,
        "F[at(3)]": True,
        "at(1) & F[at(3)] @ 2": True,
        "at(1) | at(3) @ 2": True,
        "at(1) | at(3) @ 3": False,
        "at(1) | at(3) & called(3) @ 0": True,
        "(at(1) | at(3)) & called(3) @ 0": False,
        "-at(1) & at(3) @ 0": False,
        "-(at(1) & at(3)) @ 0": True,
        "U[called(3), served(3)] @ 2": True,
        "S[at(2), at(1)] @ 2": True,
        "S[called(3), at(1)] @ 4": True,
        "S[called(3), at(1)] @ 5": False,
        "U[at(1), at(3)] @ 0": False,
        "U[at(1), at(2)] @ 0": True,
    }
)


class TestSemantics(TestCase):
    """Test cases to verify the semantic rules."""

    def test_semantics(self) -> None:
        """Test that the semantic rules are correct."""
        rules = semantics()
        for query_raw, holds in QUERIES.items():
            with self.subTest(query=query_raw):
                queries = parse(query_raw)
                query_symbols = " ".join(f"{to_symbol(q)}." for q in queries)
                control = clingo.Control()
                control.add("base", [], rules)
                control.add("base", [], TRACE)
                control.add("base", [], RULE_FORCE_QUERY)
                control.add("base", [], query_symbols)
                control.ground([("base", ())])
                with control.solve(yield_=True) as solve_handle:
                    sh = cast(SolveHandle, solve_handle)
                    self.assertEqual(sh.get().satisfiable, holds)
