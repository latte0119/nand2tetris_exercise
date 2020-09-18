import os
from enum import Enum, auto


class ArithmeticCommandType(Enum):
    ADD = auto()
    SUB = auto()
    NEG = auto()
    EQ = auto()
    GT = auto()
    LT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    def __str__(self):
        if self == ArithmeticCommandType.ADD:
            return "add"
        if self == ArithmeticCommandType.SUB:
            return "sub"
        if self == ArithmeticCommandType.NEG:
            return "neg"
        if self == ArithmeticCommandType.EQ:
            return "eq"
        if self == ArithmeticCommandType.GT:
            return "gt"
        if self == ArithmeticCommandType.LT:
            return "lt"
        if self == ArithmeticCommandType.AND:
            return "and"
        if self == ArithmeticCommandType.OR:
            return "or"
        if self == ArithmeticCommandType.NOT:
            return "not"
        assert False


class SegmentType(Enum):
    CONST = auto()
    ARG = auto()
    LOCAL = auto()
    STATIC = auto()
    THIS = auto()
    THAT = auto()
    POINTER = auto()
    TEMP = auto()

    def __str__(self):
        if self == SegmentType.CONST:
            return "constant"
        if self == SegmentType.ARG:
            return "argument"

        if self == SegmentType.LOCAL:
            return "local"
        if self == SegmentType.STATIC:
            return "static"
        if self == SegmentType.THIS:
            return "this"
        if self == SegmentType.THAT:
            return "that"
        if self == SegmentType.POINTER:
            return "pointer"
        if self == SegmentType.TEMP:
            return "temp"
        assert False


class VMWriter:
    def __init__(self, filepath):
        name = os.path.splitext(os.path.abspath(filepath))[0]
        self.file = open(f"{name}.vm", mode="w")

    def writePush(self, segment, index):
        print(f"push {segment} {index}", file=self.file)

    def writePop(self, segment, index):
        print(f"pop {segment} {index}", file=self.file)

    def writeArithmetic(self, command):
        print(f"{command}", file=self.file)

    def writeLabel(self, label):
        print(f"label {label}", file=self.file)

    def writeIF(self, label):
        print(f"if-goto {label}", file=self.file)

    def writeGoto(self, label):
        print(f"goto {label}", file=self.file)

    def writeCall(self, name, nargs):
        print(f"call {name} {nargs}", file=self.file)

    def writeFunction(self, name, nlocals):
        print(f"function {name} {nlocals}", file=self.file)

    def writeReturn(self):
        print("return", file=self.file)

    def __del__(self):
        self.file.close()


if __name__ == "__main__":
    w = VMWriter("tmp.jack")
    w.writePush(SegmentType.TEMP, 0)
