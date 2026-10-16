"""Default queries for testing."""

from dataclasses import dataclass

import clingo

from tempql.ast import Atom, BinaryExpression, BinaryOperator, Query, UnaryExpression, UnaryOperator
from tempql.lexer import Token, TokenType


@dataclass
class ExampleQuery:
    """Example query datapoint for testing."""

    raw: str
    tokens: tuple[Token, ...]
    ast: tuple[Query, ...]
    transformed: tuple[str, ...]


QUERIES_CORRECT: tuple[ExampleQuery, ...] = (
    ExampleQuery(
        raw="",
        tokens=(Token(TokenType.EOF, "", 0, 0),),
        ast=(),
        transformed=(),
    ),
    ExampleQuery(
        raw="F[o]",
        tokens=(
            Token(TokenType.OPERATOR, "F", 0, 1, UnaryOperator.EVENTUALLY),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "o", 2, 3, clingo.parse_term("o")),
            Token(TokenType.RBRACKET, "]", 3, 4),
            Token(TokenType.EOF, "", 4, 4),
        ),
        ast=(Query(UnaryExpression(UnaryOperator.EVENTUALLY, Atom(clingo.parse_term("o"))), None),),
        transformed=("query(temporal(f(o),0),1)",),
    ),
    ExampleQuery(
        raw="unwrapped | (wrapped)",
        tokens=(
            Token(TokenType.ATOM, "unwrapped", 0, 9, clingo.parse_term("unwrapped")),
            Token(TokenType.OR, "|", 10, 11),
            Token(TokenType.LPAREN, "(", 12, 13),
            Token(TokenType.ATOM, "wrapped", 13, 20, clingo.parse_term("wrapped")),
            Token(TokenType.RPAREN, ")", 20, 21),
            Token(TokenType.EOF, "", 21, 21),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.OR, Atom(clingo.parse_term("unwrapped")), Atom(clingo.parse_term("wrapped"))
                ),
                None,
            ),
        ),
        transformed=("query(temporal(dis(unwrapped,wrapped),0),1)",),
    ),
    ExampleQuery(
        raw="james\nbond(7)",
        tokens=(
            Token(TokenType.ATOM, "james", 0, 5, clingo.parse_term("james")),
            Token(TokenType.SEPARATOR, "\n", 5, 6),
            Token(TokenType.ATOM, "bond(7)", 6, 13, clingo.parse_term("bond(7)")),
            Token(TokenType.EOF, "", 13, 13),
        ),
        ast=(Query(Atom(clingo.parse_term("james")), None), Query(Atom(clingo.parse_term("bond(7)")), None)),
        transformed=(
            "query(temporal(james,0),1)",
            "query(temporal(bond(7),0),1)",
        ),
    ),
    ExampleQuery(
        raw="atom_with_underscore",
        tokens=(
            Token(TokenType.ATOM, "atom_with_underscore", 0, 20, clingo.parse_term("atom_with_underscore")),
            Token(TokenType.EOF, "", 20, 20),
        ),
        ast=(Query(Atom(clingo.parse_term("atom_with_underscore")), None),),
        transformed=("query(temporal(atom_with_underscore,0),1)",),
    ),
    ExampleQuery(
        raw="_start_with_underscore",
        tokens=(
            Token(TokenType.ATOM, "_start_with_underscore", 0, 22, clingo.parse_term("_start_with_underscore")),
            Token(TokenType.EOF, "", 22, 22),
        ),
        ast=(Query(Atom(clingo.parse_term("_start_with_underscore")), None),),
        transformed=("query(temporal(_start_with_underscore,0),1)",),
    ),
    ExampleQuery(
        raw='string("it \\"escaped\\"")',
        tokens=(
            Token(TokenType.ATOM, 'string("it \\"escaped\\"")', 0, 24, clingo.parse_term('string("it \\"escaped\\"")')),
            Token(TokenType.EOF, "", 24, 24),
        ),
        ast=(Query(Atom(clingo.parse_term('string("it \\"escaped\\"")')), None),),
        transformed=('query(temporal(string("it \\"escaped\\""),0),1)',),
    ),
    ExampleQuery(
        raw='X[raw(")[")]',
        tokens=(
            Token(TokenType.OPERATOR, "X", 0, 1, UnaryOperator.NEXT),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, 'raw(")[")', 2, 11, clingo.parse_term('raw(")[")')),
            Token(TokenType.RBRACKET, "]", 11, 12),
            Token(TokenType.EOF, "", 12, 12),
        ),
        ast=(Query(UnaryExpression(UnaryOperator.NEXT, Atom(clingo.parse_term('raw(")[")'))), None),),
        transformed=('query(temporal(x(raw(")[")),0),1)',),
    ),
    ExampleQuery(
        raw='U[test,wrap("some string @%")]',
        tokens=(
            Token(TokenType.OPERATOR, "U", 0, 1, BinaryOperator.UNTIL),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "test", 2, 6, clingo.parse_term("test")),
            Token(TokenType.COMMA, ",", 6, 7),
            Token(TokenType.ATOM, 'wrap("some string @%")', 7, 29, clingo.parse_term('wrap("some string @%")')),
            Token(TokenType.RBRACKET, "]", 29, 30),
            Token(TokenType.EOF, "", 30, 30),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.UNTIL,
                    Atom(clingo.parse_term("test")),
                    Atom(clingo.parse_term('wrap("some string @%")')),
                ),
                None,
            ),
        ),
        transformed=('query(temporal(u(test,wrap("some string @%")),0),1)',),
    ),
    ExampleQuery(
        raw="S[at(1, 2), spaces] @ 3",
        tokens=(
            Token(TokenType.OPERATOR, "S", 0, 1, BinaryOperator.SINCE),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "at(1, 2)", 2, 10, clingo.parse_term("at(1, 2)")),
            Token(TokenType.COMMA, ",", 10, 11),
            Token(TokenType.ATOM, "spaces", 12, 18, clingo.parse_term("spaces")),
            Token(TokenType.RBRACKET, "]", 18, 19),
            Token(TokenType.AT, "@", 20, 21),
            Token(TokenType.NUMBER, "3", 22, 23, 3),
            Token(TokenType.EOF, "", 23, 23),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.SINCE, Atom(clingo.parse_term("at(1,2)")), Atom(clingo.parse_term("spaces"))
                ),
                3,
            ),
        ),
        transformed=("query(temporal(s(at(1,2),spaces),3),1)",),
    ),
    ExampleQuery(
        raw="-X[at(1)] & G[served] @ 42; test",
        tokens=(
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
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.AND,
                    UnaryExpression(
                        UnaryOperator.NOT, UnaryExpression(UnaryOperator.NEXT, Atom(clingo.parse_term("at(1)")))
                    ),
                    UnaryExpression(UnaryOperator.ALWAYS, Atom(clingo.parse_term("served"))),
                ),
                42,
            ),
            Query(Atom(clingo.parse_term("test")), None),
        ),
        transformed=(
            "query(temporal(con(neg(x(at(1))),g(served)),42),1)",
            "query(temporal(test,0),1)",
        ),
    ),
    ExampleQuery(
        raw="a | b | c",
        tokens=(
            Token(TokenType.ATOM, "a", 0, 1, clingo.parse_term("a")),
            Token(TokenType.OR, "|", 2, 3),
            Token(TokenType.ATOM, "b", 4, 5, clingo.parse_term("b")),
            Token(TokenType.OR, "|", 6, 7),
            Token(TokenType.ATOM, "c", 8, 9, clingo.parse_term("c")),
            Token(TokenType.EOF, "", 9, 9),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.OR,
                    BinaryExpression(BinaryOperator.OR, Atom(clingo.parse_term("a")), Atom(clingo.parse_term("b"))),
                    Atom(clingo.parse_term("c")),
                ),
                None,
            ),
        ),
        transformed=("query(temporal(dis(dis(a,b),c),0),1)",),
    ),
    ExampleQuery(
        raw="a & b",
        tokens=(
            Token(TokenType.ATOM, "a", 0, 1, clingo.parse_term("a")),
            Token(TokenType.AND, "&", 2, 3),
            Token(TokenType.ATOM, "b", 4, 5, clingo.parse_term("b")),
            Token(TokenType.EOF, "", 5, 5),
        ),
        ast=(
            Query(
                BinaryExpression(BinaryOperator.AND, Atom(clingo.parse_term("a")), Atom(clingo.parse_term("b"))), None
            ),
        ),
        transformed=("query(temporal(con(a,b),0),1)",),
    ),
    ExampleQuery(
        raw="U[until, F[eventually]] @ 2",
        tokens=(
            Token(TokenType.OPERATOR, "U", 0, 1, BinaryOperator.UNTIL),
            Token(TokenType.LBRACKET, "[", 1, 2),
            Token(TokenType.ATOM, "until", 2, 7, clingo.parse_term("until")),
            Token(TokenType.COMMA, ",", 7, 8),
            Token(TokenType.OPERATOR, "F", 9, 10, UnaryOperator.EVENTUALLY),
            Token(TokenType.LBRACKET, "[", 10, 11),
            Token(TokenType.ATOM, "eventually", 11, 21, clingo.parse_term("eventually")),
            Token(TokenType.RBRACKET, "]", 21, 22),
            Token(TokenType.RBRACKET, "]", 22, 23),
            Token(TokenType.AT, "@", 24, 25),
            Token(TokenType.NUMBER, "2", 26, 27, 2),
            Token(TokenType.EOF, "", 27, 27),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.UNTIL,
                    Atom(clingo.parse_term("until")),
                    UnaryExpression(UnaryOperator.EVENTUALLY, Atom(clingo.parse_term("eventually"))),
                ),
                2,
            ),
        ),
        transformed=("query(temporal(u(until,f(eventually)),2),1)",),
    ),
    ExampleQuery(
        raw="\nmultiple;;;X[queries(2)];",
        tokens=(
            Token(TokenType.SEPARATOR, "\n", 0, 1),
            Token(TokenType.ATOM, "multiple", 1, 9, clingo.parse_term("multiple")),
            Token(TokenType.SEPARATOR, ";", 9, 10),
            Token(TokenType.SEPARATOR, ";", 10, 11),
            Token(TokenType.SEPARATOR, ";", 11, 12),
            Token(TokenType.OPERATOR, "X", 12, 13, UnaryOperator.NEXT),
            Token(TokenType.LBRACKET, "[", 13, 14),
            Token(TokenType.ATOM, "queries(2)", 14, 24, clingo.parse_term("queries(2)")),
            Token(TokenType.RBRACKET, "]", 24, 25),
            Token(TokenType.SEPARATOR, ";", 25, 26),
            Token(TokenType.EOF, "", 26, 26),
        ),
        ast=(
            Query(Atom(clingo.parse_term("multiple")), None),
            Query(UnaryExpression(UnaryOperator.NEXT, Atom(clingo.parse_term("queries(2)"))), None),
        ),
        transformed=(
            "query(temporal(multiple,0),1)",
            "query(temporal(x(queries(2)),0),1)",
        ),
    ),
    ExampleQuery(
        raw="a | b & c",
        tokens=(
            Token(TokenType.ATOM, "a", 0, 1, clingo.parse_term("a")),
            Token(TokenType.OR, "|", 2, 3),
            Token(TokenType.ATOM, "b", 4, 5, clingo.parse_term("b")),
            Token(TokenType.AND, "&", 6, 7),
            Token(TokenType.ATOM, "c", 8, 9, clingo.parse_term("c")),
            Token(TokenType.EOF, "", 9, 9),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.OR,
                    Atom(clingo.parse_term("a")),
                    BinaryExpression(BinaryOperator.AND, Atom(clingo.parse_term("b")), Atom(clingo.parse_term("c"))),
                ),
                None,
            ),
        ),
        transformed=("query(temporal(dis(a,con(b,c)),0),1)",),
    ),
    ExampleQuery(
        raw="(a | b) & c",
        tokens=(
            Token(TokenType.LPAREN, "(", 0, 1),
            Token(TokenType.ATOM, "a", 1, 2, clingo.parse_term("a")),
            Token(TokenType.OR, "|", 3, 4),
            Token(TokenType.ATOM, "b", 5, 6, clingo.parse_term("b")),
            Token(TokenType.RPAREN, ")", 6, 7),
            Token(TokenType.AND, "&", 8, 9),
            Token(TokenType.ATOM, "c", 10, 11, clingo.parse_term("c")),
            Token(TokenType.EOF, "", 11, 11),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.AND,
                    BinaryExpression(BinaryOperator.OR, Atom(clingo.parse_term("a")), Atom(clingo.parse_term("b"))),
                    Atom(clingo.parse_term("c")),
                ),
                None,
            ),
        ),
        transformed=("query(temporal(con(dis(a,b),c),0),1)",),
    ),
    ExampleQuery(
        raw="-a & b",
        tokens=(
            Token(TokenType.NOT, "-", 0, 1),
            Token(TokenType.ATOM, "a", 1, 2, clingo.parse_term("a")),
            Token(TokenType.AND, "&", 3, 4),
            Token(TokenType.ATOM, "b", 5, 6, clingo.parse_term("b")),
            Token(TokenType.EOF, "", 6, 6),
        ),
        ast=(
            Query(
                BinaryExpression(
                    BinaryOperator.AND,
                    UnaryExpression(UnaryOperator.NOT, Atom(clingo.parse_term("a"))),
                    Atom(clingo.parse_term("b")),
                ),
                None,
            ),
        ),
        transformed=("query(temporal(con(neg(a),b),0),1)",),
    ),
    ExampleQuery(
        raw="-(a & b)",
        tokens=(
            Token(TokenType.NOT, "-", 0, 1),
            Token(TokenType.LPAREN, "(", 1, 2),
            Token(TokenType.ATOM, "a", 2, 3, clingo.parse_term("a")),
            Token(TokenType.AND, "&", 4, 5),
            Token(TokenType.ATOM, "b", 6, 7, clingo.parse_term("b")),
            Token(TokenType.RPAREN, ")", 7, 8),
            Token(TokenType.EOF, "", 8, 8),
        ),
        ast=(
            Query(
                UnaryExpression(
                    UnaryOperator.NOT,
                    BinaryExpression(BinaryOperator.AND, Atom(clingo.parse_term("a")), Atom(clingo.parse_term("b"))),
                ),
                None,
            ),
        ),
        transformed=("query(temporal(neg(con(a,b)),0),1)",),
    ),
    ExampleQuery(
        raw="--a",
        tokens=(
            Token(TokenType.NOT, "-", 0, 1),
            Token(TokenType.NOT, "-", 1, 2),
            Token(TokenType.ATOM, "a", 2, 3, clingo.parse_term("a")),
            Token(TokenType.EOF, "", 3, 3),
        ),
        ast=(
            Query(
                UnaryExpression(UnaryOperator.NOT, UnaryExpression(UnaryOperator.NOT, Atom(clingo.parse_term("a")))),
                None,
            ),
        ),
        transformed=("query(temporal(neg(neg(a)),0),1)",),
    ),
)
