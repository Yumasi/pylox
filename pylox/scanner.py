from typing import Any, List, Optional

from pylox.error import LoxError
from pylox.token import Token
from pylox.token_type import TokenType

KEYWORDS_MAP = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class Scanner:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.tokens: List[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1

    def scan_tokens(self) -> List[Token]:
        while not self._is_at_end():
            # We are at the beginning of the next lexeme
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self) -> None:
        c = self._advance()

        match c:
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ":":
                self._add_token(TokenType.COLON)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case "?":
                self._add_token(TokenType.QUESTION)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "!":
                self._add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self._add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case "<":
                self._add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case ">":
                self._add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )
            case "/":
                if self._match("/"):
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                elif self._match("*"):
                    self._multiline_comment()
                else:
                    self._add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self._string()
            case _:
                if c.isdigit():
                    self._number()
                elif c.isalpha():
                    self._identifier()
                else:
                    LoxError.errorAt(self.line, f"Unexpected character '{c}'")

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            self._advance()

        if self._is_at_end():
            LoxError.errorAt(self.line, "Unterminated string.")
            return

        # The closing ".
        self._advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1 : self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _number(self) -> None:
        while (c := self._peek()) and c.isdigit():
            self._advance()

        if self._peek() == "." and (c := self._peek_next()) and c.isdigit():
            self._advance()

            while (c := self._peek()) and c.isdigit():
                self._advance()

        self._add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def _identifier(self) -> None:
        while (c := self._peek()) and (c.isidentifier()):
            self._advance()

        text = self.source[self.start : self.current]
        type = KEYWORDS_MAP.get(text)
        if type is None:
            type = TokenType.IDENTIFIER
        self._add_token(type)

    def _multiline_comment(self) -> None:
        first_line = self.line
        while (c := self._peek()) != "*" or self._peek_next() != "/":
            if self._is_at_end():
                LoxError.errorAt(first_line, "unterminated multi-line comment")
                return
            if c == "\n":
                self.line += 1
            self._advance()

        self.current += 2

    def _add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def _advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def _peek(self) -> Optional[str]:
        if self._is_at_end():
            return None

        return self.source[self.current]

    def _peek_next(self) -> Optional[str]:
        if self.current + 1 >= len(self.source):
            return None

        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)
