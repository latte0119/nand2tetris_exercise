import sys
import os
import re
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from VMWriter import VMWriter, SegmentType, ArithmeticCommandType
from SymbolTable import SymbolTable, ScopeKind
import random
import string


def is_jack_file(filename):
    return (
        True
        if os.path.isfile(filename) and re.fullmatch(r".*\.jack", filename)
        else False
    )


def generate_random_label():
    """アルファベット20文字のランダムなラベルを生成"""
    return "".join(random.choices(string.ascii_letters, k=20))


def childList(node):
    return [ch for ch in node]


class JackCompilar:
    def __init__(self, filepath):
        jt = JackTokenizer(filepath)
        ce = CompilationEngine(filepath, jt.tokens)
        self.vmwriter = VMWriter(filepath)
        self.symbol_table = SymbolTable()
        self.class_name = None
        self.generateClass(ce.root)

    def generateClass(self, node):
        chs = childList(node)
        self.class_name = chs[1].text
        for ch in node:
            if ch.tag == "classVarDec":
                self.generateClassVarDec(ch)
            if ch.tag == "subroutineDec":
                self.generateSubroutineDec(ch)

    def generateClassVarDec(self, node):
        chs = childList(node)

        if chs[0].text == "static":
            scopekind = ScopeKind.STATIC
        else:
            scopekind = ScopeKind.FIELD

        typename = chs[1].text
        for i in range(2, len(chs), 2):
            ch = chs[i]
            self.symbol_table.define(ch.text, typename, scopekind)

    def generateSubroutineDec(self, node):
        self.symbol_table.startSubroutine()
        chs = childList(node)
        subroutine_kind = chs[0].text
        subroutine_name = chs[2].text

        parameter_list_node = chs[4]
        subroutine_body_node = chs[6]
        if subroutine_kind == "method":
            self.symbol_table.define("", "", ScopeKind.ARG)

        chs = childList(parameter_list_node)
        for i in range(0, len(chs), 3):
            type_node = chs[i]
            var_name_node = chs[i + 1]
            self.symbol_table.define(var_name_node.text, type_node.text, ScopeKind.ARG)

        chs = childList(subroutine_body_node)

        statements_node = chs[-2]
        for i in range(1, len(chs) - 2):
            self.generateVarDec(chs[i])

        nlocals = self.symbol_table.varCount(ScopeKind.VAR)
        self.vmwriter.writeFunction(f"{self.class_name}.{subroutine_name}", nlocals)

        if subroutine_kind == "method":
            self.vmwriter.writePush(SegmentType.ARG, 0)
            self.vmwriter.writePop(SegmentType.POINTER, 0)

        elif subroutine_kind == "constructor":
            nfields = self.symbol_table.varCount(ScopeKind.FIELD)
            self.vmwriter.writePush(SegmentType.CONST, nfields)
            self.vmwriter.writeCall("Memory.alloc", 1)
            self.vmwriter.writePop(SegmentType.POINTER, 0)

        self.generateStatements(statements_node)
        # for ch in statements_node:
        #     self.generateStatement(ch)

    def generateStatements(self, node):
        for ch in node:
            self.generateStatement(ch)

    def generateStatement(self, node):
        if node.tag == "letStatement":
            self.generateLetStatement(node)

        elif node.tag == "ifStatement":
            self.generateIfStatement(node)

        elif node.tag == "whileStatement":
            self.generateWhileStatement(node)

        elif node.tag == "doStatement":
            self.generateDoStatement(node)

        else:
            self.generateReturnStatement(node)

    def generateLetStatement(self, node):
        chs = childList(node)
        self.generateExpression(chs[-2])

        varname = chs[1].text
        scopekind = self.symbol_table.kindOf(varname)
        index = self.symbol_table.indexOf(varname)

        if scopekind == ScopeKind.STATIC:
            segment = SegmentType.STATIC
        elif scopekind == ScopeKind.FIELD:
            segment = SegmentType.THIS
        elif scopekind == ScopeKind.ARG:
            segment = SegmentType.ARG
        else:
            segment = SegmentType.LOCAL

        if chs[2].text != "[":
            self.vmwriter.writePop(segment, index)

        else:
            self.vmwriter.writePush(segment, index)
            self.generateExpression(chs[3])
            self.vmwriter.writeArithmetic(ArithmeticCommandType.ADD)
            self.vmwriter.writePop(SegmentType.POINTER, 1)
            self.vmwriter.writePop(SegmentType.THAT, 0)

    def generateIfStatement(self, node):
        chs = childList(node)

        L1 = generate_random_label()
        L2 = generate_random_label()

        self.generateExpression(chs[2])
        self.vmwriter.writeArithmetic(ArithmeticCommandType.NOT)
        self.vmwriter.writeIF(L1)
        self.generateStatements(chs[5])
        self.vmwriter.writeGoto(L2)
        self.vmwriter.writeLabel(L1)
        if len(chs) > 9:
            self.generateStatements(chs[9])
        self.vmwriter.writeLabel(L2)

    def generateWhileStatement(self, node):
        chs = childList(node)
        L1 = generate_random_label()
        L2 = generate_random_label()

        self.vmwriter.writeLabel(L1)
        self.generateExpression(chs[2])
        self.vmwriter.writeArithmetic(ArithmeticCommandType.NOT)
        self.vmwriter.writeIF(L2)
        self.generateStatements(chs[5])
        self.vmwriter.writeGoto(L1)
        self.vmwriter.writeLabel(L2)

    def generateDoStatement(self, node):
        sc = childList(node)[1:-1]
        self.generateSubroutineCall(sc)

        L = generate_random_label()
        self.vmwriter.writeIF(L)
        self.vmwriter.writeLabel(L)

    def generateReturnStatement(self, node):
        chs = childList(node)
        if len(chs) == 2:
            self.vmwriter.writePush(SegmentType.CONST, 0)
        else:
            self.generateExpression(chs[1])

        self.vmwriter.writeReturn()

    def generateTerm(self, node):
        chs = childList(node)

        if chs[0].tag == "integerConstant":
            self.vmwriter.writePush(SegmentType.CONST, int(chs[0].text))
            return

        if chs[0].tag == "stringConstant":
            length = len(chs[0].text)
            self.vmwriter.writePush(SegmentType.CONST, length)
            self.vmwriter.writeCall("String.new", 1)
            for c in chs[0].text:
                self.vmwriter.writePush(SegmentType.CONST, ord(c))
                self.vmwriter.writeCall("String.appendChar", 2)
            return

        if chs[0].tag == "keyword":
            if chs[0].text == "true":
                self.vmwriter.writePush(SegmentType.CONST, 0)
                self.vmwriter.writeArithmetic(ArithmeticCommandType.NOT)
            elif chs[0].text in {"false", "null"}:
                self.vmwriter.writePush(SegmentType.CONST, 0)
            else:
                self.vmwriter.writePush(SegmentType.POINTER, 0)
            return

        if chs[0].text == "(":
            self.generateExpression(chs[1])
            return

        if chs[0].text in {"-", "~"}:
            self.generateTerm(chs[1])
            if chs[0].text == "-":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.NEG)
            if chs[0].text == "~":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.NOT)
            return

        if len(chs) == 1 or chs[-1].text == "]":
            var_name = chs[0].text
            scopekind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            if scopekind == ScopeKind.STATIC:
                segment = SegmentType.STATIC
            elif scopekind == ScopeKind.FIELD:
                segment = SegmentType.THIS
            elif scopekind == ScopeKind.ARG:
                segment = SegmentType.ARG
            else:
                segment = SegmentType.LOCAL

            self.vmwriter.writePush(segment, index)
            if chs[-1].text == "]":
                self.generateExpression(chs[2])
                self.vmwriter.writeArithmetic(ArithmeticCommandType.ADD)
                self.vmwriter.writePop(SegmentType.POINTER, 1)
                self.vmwriter.writePush(SegmentType.THAT, 0)
            return

        self.generateSubroutineCall(chs)

    def generateSubroutineCall(self, sc):
        subroutine_name = sc[-4].text
        nargs = (len(childList(sc[-2])) + 1) // 2
        if len(sc) == 4:
            self.vmwriter.writePush(SegmentType.POINTER, 0)
            nargs += 1
            class_name = self.class_name

        elif self.symbol_table.isDefined(sc[0].text):
            var_name = sc[0].text
            class_name = self.symbol_table.typeOf(var_name)

            scopekind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)

            if scopekind == ScopeKind.STATIC:
                segment = SegmentType.STATIC
            elif scopekind == ScopeKind.FIELD:
                segment = SegmentType.THIS
            elif scopekind == ScopeKind.ARG:
                segment = SegmentType.ARG
            else:
                segment = SegmentType.LOCAL

            self.vmwriter.writePush(segment, index)
            nargs += 1

        else:
            class_name = sc[0].text

        self.generateExpressionList(sc[-2])
        self.vmwriter.writeCall(f"{class_name}.{subroutine_name}", nargs)

    def generateExpression(self, node):
        chs = childList(node)
        self.generateTerm(chs[0])
        for i in range(1, len(chs), 2):
            self.generateTerm(chs[i + 1])
            op = chs[i].text

            if op == "+":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.ADD)
            elif op == "-":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.SUB)
            elif op == "&amp;":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.AND)
            elif op == "|":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.OR)
            elif op == "&lt;":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.LT)
            elif op == "&gt;":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.GT)
            elif op == "=":
                self.vmwriter.writeArithmetic(ArithmeticCommandType.EQ)
            elif op == "*":
                self.vmwriter.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vmwriter.writeCall("Math.divide", 2)

    def generateExpressionList(self, node):
        chs = childList(node)
        for i in range(0, len(chs), 2):
            self.generateExpression(chs[i])

    def generateVarDec(self, node):
        chs = childList(node)
        typename = chs[1].text
        for i in range(2, len(chs), 2):
            ch = chs[i]
            self.symbol_table.define(ch.text, typename, ScopeKind.VAR)


if __name__ == "__main__":
    assert len(sys.argv) == 2, "error : incorrect number of arguments"

    path = sys.argv[1]

    if os.path.isfile(path):
        filelist = [path]
    else:
        filelist = [os.path.join(path, filepath) for filepath in os.listdir(path)]

    filelist = list(filter(lambda filepath: is_jack_file(filepath), filelist))

    for filepath in filelist:
        JackCompilar(filepath)
