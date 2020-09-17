import re
from typing import NamedTuple
from enum import Enum
import os


class TokenType(Enum):
    KEYWORD = 0
    SYMBOL = 1
    INTEGER_CONSTANT = 2
    STRING_CONSTANT = 3
    IDENTIFER = 4


class Token(NamedTuple):
    kind: TokenType
    value: str

    def as_xml(self):
        if self.kind == TokenType.IDENTIFER:
            label = "identifier"

        elif self.kind == TokenType.INTEGER_CONSTANT:
            label = "integerConstant"

        elif self.kind == TokenType.KEYWORD:
            label = "keyword"

        elif self.kind == TokenType.STRING_CONSTANT:
            label = "stringConstant"

        else:
            label = "symbol"

        body = str(self.value)
        if body == "<":
            body = "&lt;"
        elif body == ">":
            body = "&gt;"
        elif body == "&":
            body = "&amp;"

        return (label, body)


def tokenize(code):
    # コメントを削除 flags.DOTALL を忘れずに
    comment_patterns = [r"\/\/.*?[\n]", r"\/\*.*?\*\/"]

    token_patterns = [
        ("symbol", r"[{}()[\].,;+\-*/&|<>=~]"),
        ("integerConstant", r"[0-9]+"),
        ("stringConstant", r'(?<=").*?(?=")'),
        ("identifier", r"[a-zA-Z_][a-zA-Z_0-9]*"),
    ]

    keywords = [
        "class",
        "constructor",
        "function",
        "method",
        "field",
        "static",
        "var",
        "int",
        "char",
        "boolean",
        "void",
        "true",
        "false",
        "null",
        "this",
        "let",
        "do",
        "if",
        "else",
        "while",
        "return",
    ]

    # 空白を削除
    code = re.sub("|".join(comment_patterns), "", code, flags=re.DOTALL)

    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_patterns)

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "symbol":
            yield Token(TokenType.SYMBOL, value)

        elif kind == "integerConstant":
            yield Token(TokenType.INTEGER_CONSTANT, int(value))

        elif kind == "stringConstant":
            yield Token(TokenType.STRING_CONSTANT, value)

        elif value in keywords:  # identifer
            yield Token(TokenType.KEYWORD, value)

        else:
            yield Token(TokenType.IDENTIFER, value)


class JackTokenizer:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            code = "".join(f.readlines())

        self.tokens = [token for token in tokenize(code)]

    def output_as_xml(self):
        basename = os.path.splitext(os.path.basename(os.path.abspath(self.filename)))[0]
        with open(f"{basename}T.xml", mode="w") as f:
            print("<tokens>", file=f)
            for token in self.tokens:
                print("<{0}> {1} </{0}>".format(*token.as_xml()), file=f)
            print("</tokens>", file=f)
