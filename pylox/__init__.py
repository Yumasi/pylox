import sys
from pathlib import Path

from pylox.scanner import Scanner

had_error = False


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
    global had_error

    if not path.exists():
        raise RuntimeError("could not open Lox script")

    content = path.read_text()
    run(content)

    # Indicate an error in the system exit code.
    if had_error:
        sys.exit(65)


def run_prompt() -> None:
    global had_error

    while True:
        try:
            line = input("> ")
        except EOFError:
            break

        run(line)
        had_error = False


def run(source: str) -> None:
    tokens = Scanner(source).scan_tokens()
    for token in tokens:
        print(token)


def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str):
    global had_error

    print(f"[line {line}] Error {where}: {message}")
    had_error = True
