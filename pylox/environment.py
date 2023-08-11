from typing import Any, Dict, Optional

from pylox.error import LoxRuntimeError
from pylox.token import Token


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self.enclosing: Optional[Environment] = enclosing
        self.values: Dict[str, Any] = dict()

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
