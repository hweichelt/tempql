"""Parser for the Temporal Query Language."""

from collections.abc import Iterator, Sequence
from typing import cast

from clingo import Symbol

from .ast import Atom, BinaryExpression, BinaryOperator, Expression, Query, UnaryExpression, UnaryOperator
from .error import ParseError
from .lexer import Token, TokenType, tokenize


class Parser:
    """Parser for the Temporal Query Language."""

    def __init__(self, tokens: Sequence[Token]) -> None:
        """Initialize the parser with the given tokens."""
        self._tokens = tokens
        self._position = 0

    def consume(self, expected: TokenType) -> Token:
        """Consume the current token if it matches the expected type."""
        if self.current().type != expected:
            start = self.current().start
            end = self.current().end
            raise ParseError(f"Expected {expected}, got {self.current().type}", start, end)
        token = self._tokens[self._position]
        self._position += 1
        print(f"Consumed {token.raw}")
        return token

    def current(self) -> Token:
        """Return the current token the parser is at."""
        return self._tokens[self._position]

    def parse(self) -> Iterator[Query]:
        """Parse all tokens of the parser."""
        self._skip_separators()
        while self.current().type != TokenType.EOF:  # Consume queries until EOF
            yield self._query()
            if self.current().type != TokenType.EOF:  # Skip empty separators between queries
                self.consume(TokenType.SEPARATOR)  # But make sure there is at least one
                self._skip_separators()

    def _query(self) -> Query:
        timestep: int | None = None
        expression = self._formula()
        if self.current().type == TokenType.AT:
            self.consume(TokenType.AT)
            timestep = cast(int, self.consume(TokenType.NUMBER).value)

        return Query(expression, timestep)

    def _formula(self) -> Expression:
        return self._disjunction()

    def _disjunction(self) -> Expression:
        expression = self._conjunction()
        while self.current().type == TokenType.OR:
            self.consume(TokenType.OR)
            expression = BinaryExpression(BinaryOperator.OR, expression, self._conjunction())
        return expression

    def _conjunction(self) -> Expression:
        expression = self._signed()
        while self.current().type == TokenType.AND:
            self.consume(TokenType.AND)
            expression = BinaryExpression(BinaryOperator.AND, expression, self._signed())
        return expression

    def _signed(self) -> Expression:
        if self.current().type == TokenType.NOT:
            self.consume(TokenType.NOT)
            return UnaryExpression(UnaryOperator.NOT, self._signed())
        return self._primary()

    def _primary(self) -> Expression:
        match self.current().type:
            case TokenType.ATOM:
                return self._atom()
            case TokenType.LPAREN:
                self.consume(TokenType.LPAREN)
                expression = self._formula()
                self.consume(TokenType.RPAREN)
                return expression
            case TokenType.OPERATOR:
                operator_token = self.consume(TokenType.OPERATOR)
                operator = cast(UnaryOperator | BinaryOperator, operator_token.value)
                self.consume(TokenType.LBRACKET)
                match operator:
                    case UnaryOperator.NEXT | UnaryOperator.PREV | UnaryOperator.ALWAYS | UnaryOperator.EVENTUALLY:
                        expression = self._formula()
                        self.consume(TokenType.RBRACKET)
                        return UnaryExpression(operator, expression)
                    case BinaryOperator.UNTIL | BinaryOperator.SINCE:
                        left = self._formula()
                        self.consume(TokenType.COMMA)
                        right = self._formula()
                        self.consume(TokenType.RBRACKET)
                        return BinaryExpression(operator, left, right)
                    case _:
                        start = operator_token.start
                        end = operator_token.end
                        raise ParseError(f"Unexpected operator: {operator_token.value}", start, end)
            case _:
                current = self.current()
                start = current.start
                end = current.end
                raise ParseError(f"Unexpected token in primary: {current}", start, end)

    def _atom(self) -> Expression:
        symbol = cast(Symbol, self.consume(TokenType.ATOM))
        return Atom(symbol)

    def _skip_separators(self) -> None:
        while self.current().type == TokenType.SEPARATOR:
            self.consume(TokenType.SEPARATOR)


def parse(raw: str) -> list[Query]:
    """Parse the given raw string into a list of AST queries."""
    tokens = list(tokenize(raw))
    parser = Parser(tokens)
    return list(parser.parse())
