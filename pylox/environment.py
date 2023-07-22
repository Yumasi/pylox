from typing import Any, Dict
from pylox.error import LoxRuntimeError

from pylox.token import Token


class Environment:
    def __init__(self) -> None:
        self.values: Dict[str, Any] = dict()

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
