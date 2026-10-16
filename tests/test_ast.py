"""Test cases for the AST."""

QUERIES_INCORRECT: tuple[str, ...] = (
    "X[unclosed",
    "P[unopened]]",
    "G[no_time] @",
)
