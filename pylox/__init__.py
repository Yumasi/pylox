import sys
from pathlib import Path

from pylox.error import LoxError
from pylox.interpreter import Interpreter
from pylox.parser import Parser
from pylox.scanner import Scanner


def main() -> None:
    arg_count = len(sys.argv)
    if arg_count > 2:
        print("Usage: jlox [script]")
        sys.exit(64)

    interpreter = Interpreter()

    if arg_count > 1:
        run_file(interpreter, Path(sys.argv[1]))
    else:
        run_prompt(interpreter)


def run_file(interpreter: Interpreter, path: Path) -> None:
    if not path.exists():
        raise RuntimeError("could not open Lox script")

    content = path.read_text()
    run(interpreter, content)

    # Indicate an error in the system exit code.
    if LoxError.had_error():
        sys.exit(65)
    if LoxError.had_runtime_error():
        sys.exit(70)


def run_prompt(interpreter: Interpreter) -> None:
    while True:
        try:
            line = input("> ")
        except EOFError:
            break

        run(interpreter, line)
        LoxError.reset_error()


def run(interpreter: Interpreter, source: str) -> None:
    tokens = Scanner(source).scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    # Stop if there was a syntax error
    if LoxError.had_error():
        return

    interpreter.interpret(statements)
