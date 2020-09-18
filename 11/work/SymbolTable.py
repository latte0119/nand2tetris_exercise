from typing import NamedTuple
from enum import Enum


class ScopeKind(Enum):
    STATIC = 0
    FIELD = 1
    ARGUMENT = 2
    VAR = 3


class SymbolInfo(NamedTuple):
    typename: str
    scopekind: ScopeKind
    index: int


class SymbolTable:
    def __init__(self):
        self.classScope = dict()
        self.subroutineScope = dict()

    def startSubroutine(self):
        self.subroutineScope = dict()

    def define(self, identifier, typename, scopekind):
        if scopekind in {ScopeKind.STATIC, ScopeKind.FIELD}:
            scope = self.classScope
        else:
            scope = self.subroutineScope

        assert identifier not in scope
        tmp = len(scope)
        scope[identifier] = SymbolInfo(
            typename=typename, scopekind=scopekind, index=tmp
        )

    def getSymbolInfo(self, name):
        if name in self.subroutineScope:
            return self.subroutineScope[name]
        assert name in self.classScope
        return self.classScope[name]

    def kindOf(self, name):
        tmp = self.getSymbolInfo(name)
        return tmp.scopekind

    def typeOf(self, name):
        tmp = self.getSymbolInfo(name)
        return tmp.typename

    def indexOf(self, name):
        tmp = self.getSymbolInfo(name)
        return tmp.index
