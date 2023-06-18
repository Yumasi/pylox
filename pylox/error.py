from pylox.token import Token
from pylox.token_type import TokenType

class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.token: Token = token

class LoxError:
    _had_error: bool = False
    _had_runtime_error: bool = False

    @classmethod
    def report(cls, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}")
        cls._had_error = True

    @classmethod
    def errorAt(cls, line: int, message: str) -> None:
        cls.report(line, "", message)

    @classmethod
    def runtimeError(cls, error: LoxRuntimeError):
        print(f"{error.args[0]}\n[line {error.token.line}]")
        cls._had_runtime_error = True

    @classmethod
    def errorToken(cls, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            cls.report(token.line, "at end", message)
        else:
            cls.report(token.line, f"at '{token.lexeme}'", message)


    @classmethod
    def had_error(cls) -> bool:
        return cls._had_error

    @classmethod
    def had_runtime_error(cls) -> bool:
        return cls._had_runtime_error

    @classmethod
    def reset_error(cls) -> None:
        cls._had_error = False

    @classmethod
    def reset_runtime_error(cls) -> None:
        cls._had_runtime_error = False
