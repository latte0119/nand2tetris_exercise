import os,sys
import re
from enum import Enum
def is_vm_file(filename):
    return True if os.path.isfile(filename) and re.fullmatch(r'.*vm',filename) else False

class CommandType(Enum):
    C_ARITHMETIC=0
    C_PUSH=1
    C_POP=2
    C_LABEL=3
    C_GOTO=4
    C_IF=5
    C_FUNCTION=6
    C_RETURN=7
    C_CALL=8


class Parser:
    def __init__(self,filepath):
        self.filename=os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath) as f:
            self.lines=f.readlines()                


class CodeWriter:
    def __init__(self,filepath): #書き込み先
        self.ost=open(filepath,mode='w')
    
    def setFileName(self,filename): #読み込むファイル名を設定
        self.filename=filename
    
    def writeArithmetic(self,command):
        pass
    
    def writePushPop(self,command,segment,index):
        mp={
            'local':'LCL',
            'argument':'ARG',
            'this':'THIS',
            'that':'THAT',
        }

        if command==CommandType.C_PUSH:
            if segment in mp:
                self.ost.write('@',mp[segment],sep='')
                self.ost.write('D=A')
                self.ost.write('@',index,sep='')
                self.ost.write('A=D+A')
                self.ost.write('D=M')
            if segment=='constant':
                self.ost.write('@',index,sep='')
                self.ost.write('D=A')
            if segment=='static':
                self.ost.write('@',self.filename,'.',index,sep='')
                self.ost.write('D=M')
            self.ost.write('@SP')
            self.ost.write('M=D')
            self.ost.write('M=M+1')
        
        else:
            self.ost.write('@SP')
            self.ost.write('M=M-1')
            self.ost.write('D=M')
            if segment in mp:
                self.ost.write('@',mp[segment],sep='')
                self.ost.write('D=A')
                self.ost.write('@',index,sep='')
                self.ost.write('A=D+A')
            if segment=='static':
                self.ost.write('@',self.filename,'.',index,sep='')
            self.ost.write('')
    def __del__(self):
        self.ost.close()

if __name__=='__main__':
    assert len(sys.argv)>1,'error : incorrect number of arguments'

    path=sys.argv[1]
    
    if os.path.isfile(path):
        filelist=[path]
    else:
        filelist=[os.path.join(path,filename) for filename in os.listdir(path)]
    
    programs=list(map(lambda filepath :Parser(filepath),filter(is_vm_file,filelist)))
    print(len(programs))
    for p in programs:
        print(p.filename)
    
    codewriter=CodeWriter('tmp.hack')
