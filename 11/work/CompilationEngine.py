from typing import List
from JackTokenizer import Token, TokenType
import xml.etree.ElementTree as ET


def check(token, kind=None, value=None):
    if kind is not None:
        assert token.kind == kind, f"expected kind : {kind} actual : {token.kind}"
    if value is not None:
        assert token.value == value, f"expected value : {value} actual : {token.value}"


class CompilationEngine:
    def __init__(self, filepath, tokens: List[Token]):
        self.tokens = tokens
        self.filepath = filepath
        self.root = ET.Element("class")
        self.pos = 0
        self.compileClass(self.root)

    def currentToken(self):
        assert self.pos < len(self.tokens), "error : out of range"
        return self.tokens[self.pos]

    def nextToken(self):
        assert self.pos + 1 < len(self.tokens), "error : out of range"
        return self.tokens[self.pos + 1]

    def advance(self):
        self.pos += 1

    def read(self, node, kind=None, value=None):
        token = self.currentToken()

        check(token, kind, value)

        tmp = token.as_xml()
        node = ET.SubElement(node, tmp[0])
        node.text = tmp[1]

        print(tmp[1])
        self.advance()

    def readType(self, node):
        token = self.currentToken()
        assert (
            token.kind == TokenType.KEYWORD
            and token.value in {"int", "char", "boolean"}
            or token.kind == TokenType.IDENTIFER
        ), ""
        self.read(node)

    def readSubroutineCall(self, node):
        token = self.nextToken()
        if token.kind == TokenType.SYMBOL and token.value == ".":
            self.read(node, TokenType.IDENTIFER)
            self.read(node)

        self.read(node, TokenType.IDENTIFER)
        self.read(node, TokenType.SYMBOL, "(")
        self.compileExpressionList(node)
        self.read(node, TokenType.SYMBOL, ")")

    def compileClass(self, node):
        self.read(node, TokenType.KEYWORD, "class")
        self.read(node, TokenType.IDENTIFER)
        self.read(node, TokenType.SYMBOL, "{")

        while True:
            token = self.currentToken()
            if token.kind != TokenType.KEYWORD or token.value not in {
                "static",
                "field",
            }:
                break
            self.compileClassVarDec(node)

        while True:
            token = self.currentToken()
            if token.kind != TokenType.KEYWORD or token.value not in {
                "constructor",
                "function",
                "method",
            }:
                break
            self.compileSubroutineDec(node)
        self.read(node, TokenType.SYMBOL, "}")

    def compileClassVarDec(self, node):
        node = ET.SubElement(node, "classVarDec")
        self.read(node)
        self.readType(node)
        self.read(node, TokenType.IDENTIFER)
        while True:
            token = self.currentToken()
            if token.kind == TokenType.SYMBOL and token.value == ";":
                self.read(node)
                break
            self.read(node, TokenType.SYMBOL, ",")
            self.read(node, TokenType.IDENTIFER)

    def compileSubroutineDec(self, node):
        node = ET.SubElement(node, "subroutineDec")
        self.read(node)
        token = self.currentToken()
        if token.kind == TokenType.KEYWORD and token.value == "void":
            self.read(node)
        else:
            self.readType(node)

        self.read(node, TokenType.IDENTIFER)
        self.read(node, TokenType.SYMBOL, "(")
        self.compileParameterList(node)
        self.read(node, TokenType.SYMBOL, ")")
        self.compileSubroutineBody(node)

    def compileSubroutineBody(self, node):
        node = ET.SubElement(node, "subroutineBody")
        self.read(node, TokenType.SYMBOL, "{")
        while True:
            token = self.currentToken()
            if token.kind == TokenType.KEYWORD and token.value == "var":
                self.compileVarDec(node)
                continue
            break
        self.compileStatements(node)
        self.read(node, TokenType.SYMBOL, "}")

    def compileVarDec(self, node):
        node = ET.SubElement(node, "varDec")
        self.read(node)
        self.readType(node)
        while True:
            self.read(node, TokenType.IDENTIFER)
            token = self.currentToken()
            if token.kind != TokenType.SYMBOL or token.value != ",":
                break
            self.read(node)
        self.read(node, TokenType.SYMBOL, ";")

    def compileParameterList(self, node):
        node = ET.SubElement(node, "parameterList")

        token = self.currentToken()
        if token.kind == TokenType.SYMBOL and token.value == ")":
            return

        while True:
            self.readType(node)
            self.read(node, TokenType.IDENTIFER)
            token = self.currentToken()
            if token.kind != TokenType.SYMBOL or token.value != ",":
                break
            self.read(node)

    def compileStatements(self, node):
        node = ET.SubElement(node, "statements")
        while True:
            token = self.currentToken()
            if token.kind != TokenType.KEYWORD:
                break

            if token.value == "let":
                self.compileLet(node)
            elif token.value == "if":
                self.compileIf(node)
            elif token.value == "while":
                self.compileWhile(node)
            elif token.value == "do":
                self.compileDo(node)
            elif token.value == "return":
                self.compileReturn(node)
            else:
                break

    def compileLet(self, node):
        node = ET.SubElement(node, "letStatement")
        self.read(node)
        self.read(node, TokenType.IDENTIFER)
        token = self.currentToken()
        if token.kind == TokenType.SYMBOL and token.value == "[":
            self.read(node)
            self.compileExpression(node)
            self.read(node, TokenType.SYMBOL, "]")
        self.read(node, TokenType.SYMBOL, "=")
        self.compileExpression(node)
        self.read(node, TokenType.SYMBOL, ";")

    def compileIf(self, node):
        node = ET.SubElement(node, "ifStatement")
        self.read(node)
        self.read(node, TokenType.SYMBOL, "(")
        self.compileExpression(node)
        self.read(node, TokenType.SYMBOL, ")")
        self.read(node, TokenType.SYMBOL, "{")
        self.compileStatements(node)
        self.read(node, TokenType.SYMBOL, "}")
        token = self.currentToken()
        if token.kind != TokenType.KEYWORD or token.value != "else":
            return
        self.read(node)
        self.read(node, TokenType.SYMBOL, "{")
        self.compileStatements(node)
        self.read(node, TokenType.SYMBOL, "}")

    def compileWhile(self, node):
        node = ET.SubElement(node, "whileStatement")
        self.read(node)
        self.read(node, TokenType.SYMBOL, "(")
        self.compileExpression(node)
        self.read(node, TokenType.SYMBOL, ")")
        self.read(node, TokenType.SYMBOL, "{")
        self.compileStatements(node)
        self.read(node, TokenType.SYMBOL, "}")

    def compileDo(self, node):
        node = ET.SubElement(node, "doStatement")
        self.read(node)
        self.readSubroutineCall(node)
        self.read(node, TokenType.SYMBOL, ";")

    def compileReturn(self, node):
        node = ET.SubElement(node, "returnStatement")
        self.read(node)
        token = self.currentToken()
        if token.kind != TokenType.SYMBOL or token.value != ";":
            self.compileExpression(node)
        self.read(node, TokenType.SYMBOL, ";")

    def compileExpression(self, node):
        node = ET.SubElement(node, "expression")
        while True:
            self.compileTerm(node)
            token = self.currentToken()
            if token.kind != TokenType.SYMBOL or token.value not in {
                "+",
                "-",
                "*",
                "/",
                "&",
                "|",
                "<",
                ">",
                "=",
            }:
                break
            self.read(node)

    def compileTerm(self, node):
        node = ET.SubElement(node, "term")
        token = self.currentToken()
        if token.kind in {TokenType.INTEGER_CONSTANT, TokenType.STRING_CONSTANT}:
            self.read(node)
            return

        if token.kind == TokenType.KEYWORD and token.value in {
            "true",
            "false",
            "null",
            "this",
        }:
            self.read(node)
            return

        if token.kind == TokenType.SYMBOL and token.value == "(":
            self.read(node)
            self.compileExpression(node)
            self.read(node, TokenType.SYMBOL, ")")
            return

        if token.kind == TokenType.SYMBOL and token.value in {"-", "~"}:
            self.read(node)
            self.compileTerm(node)
            return

        token = self.nextToken()
        if token.kind == TokenType.SYMBOL and token.value in {"(", "."}:
            self.readSubroutineCall(node)
            return

        self.read(node, TokenType.IDENTIFER)
        if token.kind == TokenType.SYMBOL and token.value == "[":
            self.read(node)
            self.compileExpression(node)
            self.read(node, TokenType.SYMBOL, "]")

    def compileExpressionList(self, node):
        node = ET.SubElement(node, "expressionList")

        token = self.currentToken()
        if token.kind == TokenType.SYMBOL and token.value == ")":
            return

        while True:
            self.compileExpression(node)
            token = self.currentToken()
            if token.kind != TokenType.SYMBOL or token.value != ",":
                break
            self.read(node)
