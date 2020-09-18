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

    def generateSubrotineDec(self, node):
        self.symbol_table.startSubroutine()
        chs = childList(node)
        subroutine_kind = chs[0].text
        subroutine_name = chs[2].text

        parameter_list_node = chs[5]
        subroutine_body_node = chs[7]
        if subroutine_kind == "method":
            self.symbol_table.define("", "", ScopeKind.VAR)

        chs = childList(parameter_list_node)
        for i in range(0, len(chs), 3):
            type_node = chs[i]
            var_name_node = chs[i + 1]
            self.symbol_table.define(type_node.text, var_name_node.text, ScopeKind.ARG)

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
        if self.tag == "letStatement":
            self.generateLetStatement(node)

        elif self.tag == "ifStatement":
            self.generateIfStatement(node)

        elif self.tag == "whileStatement":
            self.generateWhileStatement(node)

        elif self.tag == "doStatement":
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
        pass

    def generateDoStatement(self, node):
        pass

    def generateReturnStatement(self, node):
        pass

    def generateExpression(self, node):
        pass

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
