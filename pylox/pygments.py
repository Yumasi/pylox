from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Whitespace,
)


class PLexer(RegexLexer):
    name = "Lox"
    aliases = ["lox"]
    filenames = ["*.lox"]

    tokens = {
        "root": [
            (r"\n", Whitespace),
            (r"\s+", Whitespace),
            (r"//(.*?)\n", Comment.Single),
            (r'"', String, "string"),
            # Keywords
            (words(("if", "else"), prefix=r"\b"), Keyword),
            (r"print\b", Name.Builtin),
            (r"(true|false)\b", Keyword.Constant),
            (r"var\b", Keyword.Declaration),
            # Numbers
            (r"[0-9]+", Number.Integer),
            # Identifiers
            (r"[a-zA-Z_]\w*", Name),
            # Operators and Punctuation
            (r"[{}(),.;]", Punctuation),
            (r"[+\-*/&|<>!=:?]", Operator),
        ],
        "string": [
            (r'[^"]+', String),
            (r'"', String, "#pop"),
        ],
    }
