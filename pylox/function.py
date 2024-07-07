from dataclasses import dataclass
from typing import Any, List

from pylox.callable import LoxCallable
from pylox.environment import Environment
from pylox.interpreter import Interpreter
from pylox.stmt import Function


@dataclass
class LoxFunction(LoxCallable):
    declaration: Function

    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        environment = Environment(interpreter.globals)

        for i, p in enumerate(self.declaration.params):
            environment.define(p.lexeme, arguments[i])

        interpreter._executeBlock(self.declaration.body, environment)

        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def toString(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
