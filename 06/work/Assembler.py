import sys
import re
from enum import Enum


def arrange_code(line):
    line=re.sub(r'\/\/.*$','',line) #コメントを削除
    line=re.sub(r'\s','',line) #空白文字を削除
    return line

def read_program():
    if len(sys.argv)!=2:
        print('Incorrect number of arguments')
        sys.exit(1)

    path=sys.argv[1]

    with open(path) as f:
        lines=f.readlines()

    return list(filter(lambda l:len(l)>0,map(arrange_code,lines)))


class SymbolTable:
    def __init__(self):
        self.dict={}
    
    def contains(self,symbol):
        return symbol in self.dict

    def add_entry(self,symbol,address):
        if not self.contains(symbol):
            self.dict[symbol]=address

    def get_address(self,symbol):
        if not self.contains(symbol):
            print('error : symbol {} is unknown'.format(symbol))
            sys.exit(1)
        return self.dict[symbol]

class CommandType(Enum):
    A_COMMAND=0
    C_COMMAND=1
    L_COMMAND=2


if __name__=='__main__':
    lines=read_program()
    print(lines)

    symbol_table=SymbolTable()
    
    line_cnt=0
    for line in lines:
        if command_type(line)