from typing import List, Optional

from pylox.error import LoxError
from pylox.expr import (
    Assign,
    Binary,
    Conditional,
    Expr,
    Grouping,
    Literal,
    Unary,
    Variable,
)
from pylox.stmt import Block, Expression, Print, Stmt, Var
from pylox.token import Token
from pylox.token_type import TokenType


class ParseError(RuntimeError):
    pass


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens: List[Token] = tokens
        self.current: int = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self._isAtEnd():
            statements.append(self._declaration())  # type: ignore

        return statements

    def _declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TokenType.VAR):
                return self._varDeclaration()

            return self._statement()
        except ParseError:
            self._synchronise()
            return None

    def _varDeclaration(self) -> Stmt:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Optional[Expr] = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _statement(self) -> Stmt:
        if self._match(TokenType.PRINT):
            return self._printStatement()

        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())

        return self._expressionStatement()

    def _printStatement(self) -> Stmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)  # type:ignore

    def _expressionStatement(self) -> Stmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)  # type:ignore

    def _block(self) -> List[Stmt]:
        statements: List[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._isAtEnd():
            statements.append(self._declaration())  # type:ignore

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _expression(self) -> Optional[Expr]:
        return self._comma()

    def _comma(self) -> Optional[Expr]:
        expr = self._conditional()
        while self._match(TokenType.COMMA):
            operator = self._previous()
            right = self._conditional()
            expr = Binary(expr, operator, right)

        return expr

    def _conditional(self) -> Optional[Expr]:
        expr = self._assignment()
        if self._match(TokenType.QUESTION):
            left = self._expression()
            self._consume(
                TokenType.COLON,
                "Expect ':' after left-hand expression in ternary expression.",
            )
            right = self._conditional()
            expr = Conditional(expr, left, right)

        return expr

    def _assignment(self) -> Optional[Expr]:
        expr = self._equality()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Optional[Expr] = self._assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)  # type:ignore

            self._error(equals, "Invalid assignment target.")

        return expr

    def _equality(self) -> Optional[Expr]:
        expr = self._comparison()
        while self._match(
            TokenType.BANG_EQUAL,
            TokenType.EQUAL_EQUAL,
        ):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Optional[Expr]:
        expr = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Optional[Expr]:
        expr = self._factor()
        while self._match(
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Optional[Expr]:
        expr = self._unary()
        while self._match(
            TokenType.SLASH,
            TokenType.STAR,
        ):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Optional[Expr]:
        if self._match(
            TokenType.BANG,
            TokenType.MINUS,
        ):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self) -> Optional[Expr]:
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        # Error production
        if self._match(TokenType.COMMA):
            self._error(self._previous(), "Missing left-hand operand.")
            self._conditional()
            return None

        if self._match(TokenType.QUESTION):
            self._error(self._previous(), "Missing condition operand.")
            self._expression()
            self._consume(
                TokenType.COLON,
                "Expect ':' after left-hand expression in ternary expression.",
            )
            self._conditional()

            return None

        if self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            self._error(self._previous(), "Missing left-hand operand.")
            self._comparison()
            return None

        if self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            self._error(self._previous(), "Missing left-hand operand.")
            self._term()
            return None

        if self._match(TokenType.PLUS):
            self._error(self._previous(), "Missing left-hand operand.")
            self._factor()
            return None

        if self._match(TokenType.SLASH, TokenType.STAR):
            self._error(self._previous(), "Missing left-hand operand.")
            self._unary()
            return None

        raise self._error(self._peek(), "Expect expression.")

    # Helpers

    def _match(self, *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True

        return False

    def _consume(self, type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._advance()

        raise self._error(self._peek(), message)

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        if not self._isAtEnd():
            self.current += 1

        return self._previous()

    def _check(self, type: TokenType) -> bool:
        if self._isAtEnd():
            return False

        return self._peek().type == type

    def _isAtEnd(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    # Errors

    def _error(self, token: Token, message: str) -> ParseError:
        LoxError.errorToken(token, message)
        return ParseError()

    def _synchronise(self) -> None:
        self._advance()

        while not self._isAtEnd():
            if self._previous().type == TokenType.SEMICOLON:
                return

            if self._peek().type in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

            self._advance()
