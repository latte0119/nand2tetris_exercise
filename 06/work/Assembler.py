import sys
import re
from enum import Enum

def remove_comment(line):
    return re.sub(r'\/\/.*$','',line)

def read_program():
    if len(sys.argv)!=2:
        print('Incorrect number of arguments')
        sys.exit(1)

    path=sys.argv[1]

    with open(path) as f:
        lines=f.readlines()

    return list(filter(lambda l:len(l)>0,map(lambda line:remove_comment(line).strip(),lines)))


class SymbolTable:
    def __init__(self):
        self.dict={'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576,**{'R{}'.format(i):i for i in range(16)}}
    
    def contains(self,symbol):
        return symbol in self.dict

    def add_entry(self,symbol,address):
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


def command_type(line):
    if line[0]=='@':
        return CommandType.A_COMMAND
    if line[0]=='(':
        return CommandType.L_COMMAND
    return CommandType.C_COMMAND

def extract_label(line):
    if line[0]=='(':
        match=re.match(r'^\(\s*([a-zA-Z_.$:][a-zA-Z0-9_.$:]*)\s*\)$',line)
        if not match:
            print('error : invalid L_COMMAND')
            sys.exit(1)
        return match.group(1)

    match=re.match(r'^@\s*([a-zA-Z0-9_.$:]+)$',line)
    if not match:
        print('error : invalid A_COMMAND')
        sys.exit(1)
    
    label=match.group(1)
    if not label.isdecimal() and label[0].isdecimal():
        print('error : invalid label')
        sys.exit(1)
    return label


def code_comp(comp):
    dic={
        '0':'0101010',
        '1':'0111111',
        '-1':'0111010',
        'D':'0001100',
        'A':'0110000',
        '!D':'0001101',
        '!A':'0110001',
        '-D':'0001111',
        '-A':'0110011',
        'D+1':'0011111',
        'A+1':'0110111',
        'D-1':'0001110',
        'A-1':'0110010',
        'D+A':'0000010',
        'D-A':'0010011',
        'A-D':'0000111',
        'D&A':'0000000',
        'D|A':'0010101',
        'M':'1110000',
        '!M':'1110001',
        '-M':'1110011',
        'M+1':'1110111',
        'M-1':'1110010',
        'D+M':'1000010',
        'D-M':'1010011',
        'M-D':'1000111',
        'D&M':'1000000',
        'D|M':'1010101'
    }

    if not comp in dic:
        print('error : invalid comp of C_COMMAND')
        sys.exit(1)

    return dic[comp]

def code_dest(dest):
    code=''
    code+= '1' if 'A' in dest else '0'
    code+= '1' if 'D' in dest else '0'
    code+= '1' if 'M' in dest else '0'
    return code

def code_jump(jump):
    if len(jump)>0:
        jump=jump[1:]
    
    jump_list=['','JGT','JEQ','JGE','JLT','JNE','JLE','JMP']

    dic=dict(zip(jump_list,[format(i,'03b') for i in range(8)]))
    return dic[jump]

def parse_C_command(line):
    line=re.sub(r'\s*','',line)
    match=re.match('^((?:.*=)?)(.*?)((?:;.*)?)$',line)
    if not match:
        print('error : invalid C_COMMAND')
        sys.exit(1)

    dest=match.group(1)
    comp=match.group(2)
    jump=match.group(3)

    return (comp,dest,jump)

def code_C_command(comp,dest,jump):
    dest=code_dest(dest)
    comp=code_comp(comp)
    jump=code_jump(jump)

    return (comp,dest,jump)

if __name__=='__main__':
    lines=read_program()

    symbol_table=SymbolTable()

    line_cnt=0
    next_ram_address=16
    for line in lines:
        if command_type(line)!=CommandType.L_COMMAND:
            line_cnt+=1
            continue

        label=extract_label(line)
        if symbol_table.contains(label):
            print('The same label is defined more than once')
            sys.exit(1)
        symbol_table.add_entry(label,line_cnt)
    
    
    for line in lines:
        if command_type(line)==CommandType.L_COMMAND:
            continue
    
        if command_type(line)==CommandType.A_COMMAND:
            label=extract_label(line)
            if not label.isdecimal():
                if not symbol_table.contains(label):
                    symbol_table.add_entry(label,next_ram_address)
                    next_ram_address+=1
                
                value=symbol_table.get_address(label)
            else:
                value=int(label)
            
            print(format(value,'016b'))
            
        else:
            comp,dest,jump=parse_C_command(line)
            comp,dest,jump=code_C_command(comp,dest,jump)
            
            print('111',comp,dest,jump,sep='')

            

            
