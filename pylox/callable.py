from typing import Any, List, Protocol, runtime_checkable

from pylox.interpreter import Interpreter


@runtime_checkable
class LoxCallable(Protocol):
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any: ...

    def arity(self) -> int: ...
