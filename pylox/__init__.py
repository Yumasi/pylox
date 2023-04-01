import sys
from pathlib import Path
from typing import cast
from pylox.ast_printer import AstPrinter
from pylox.expr import Expr
from pylox.parser import Parser

from pylox.scanner import Scanner
from pylox.error import LoxError


def main() -> None:
    arg_count = len(sys.argv)
    if arg_count > 2:
        print("Usage: jlox [script]")
        sys.exit(64)

    if arg_count > 1:
        run_file(Path(sys.argv[1]))
    else:
        run_prompt()


def run_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError("could not open Lox script")

    content = path.read_text()
    run(content)

    # Indicate an error in the system exit code.
    if LoxError.had_error():
        sys.exit(65)


def run_prompt() -> None:
    while True:
        try:
            line = input("> ")
        except EOFError:
            break

        run(line)
        LoxError.reset_error()


def run(source: str) -> None:
    tokens = Scanner(source).scan_tokens()
    parser = Parser(tokens)

    expression = parser.parse()

    if LoxError.had_error():
        return

    expression = cast(Expr, expression)
    print(AstPrinter().print(expression))
