from dataclasses import dataclass
from typing import Any

from pylox.token_type import TokenType


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        return f"{self.type.name:12} {self.lexeme:10} {self.literal}"
