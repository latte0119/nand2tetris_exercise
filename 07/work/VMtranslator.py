import os,sys
import re
from enum import Enum

#与えられたファイルがvmファイルかどうか調べる
def is_vm_file(filename):
    return True if os.path.isfile(filename) and re.fullmatch(r'.*vm',filename) else False

#command(例:'add')の分類
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

#pointerとtempのROM上のアドレス
POINTER=3
TEMP=5

#dict{command:CommandType}
command_type_table={
    **{s:CommandType.C_ARITHMETIC for s in {'add','sub','neg','eq','gt','lt','and','or','not'}},
    'push':CommandType.C_PUSH,
    'pop':CommandType.C_POP,
    'label':CommandType.C_LABEL,
    'goto':CommandType.C_GOTO,
    'if-goto':CommandType.C_IF,
    'function':CommandType.C_FUNCTION,
    'call':CommandType.C_CALL,
    'return':CommandType.C_RETURN
}

#command(例:'add')に対して対応するCommandTypeを返す
def classify_command_type(command):
    assert command in command_type_table,'error : unknown command'
    return command_type_table[command]

#プログラムを一行受け取って(例:'push local 1 \\local[1]をpush')，
#コメントを取り除き，トークンに分解したlistを返す
#['push','local','1']
def parse_line(line):
    line=re.sub(r'\/\/.*','',line)
    return list(filter(lambda s:len(s)>0,re.split(r'\s+',line)))

#引数の数を検証する
def verify_code_format(code):
    assert len(code)>0,'error : empty code'
    commandtype=classify_command_type(code[0])
    if commandtype in {CommandType.C_PUSH,CommandType.C_POP,CommandType.C_FUNCTION,CommandType.C_CALL}:
        assert len(code)==3,'error : invalid syntax {}'.format(code)
        
    if commandtype in {CommandType.C_ARITHMETIC,CommandType.C_RETURN}:
        assert len(code)==1,'error : invalid syntax {}'.format(code)

    if commandtype in {CommandType.C_LABEL,CommandType.C_GOTO,CommandType.C_IF}:
        assert len(code)==2,'error : invalid syntax {}'.format(code)



class Parser:
    def __init__(self,filepath):
        self.filename=os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath) as f:
            self.lines=f.readlines()    
        
        self.lines=list(filter(lambda li:len(li)>0,map(parse_line,self.lines)))


class CodeWriter:
    def __init__(self,filepath): #書き込み先
        self.ost=open(filepath,mode='w')
    
    def set_filename(self,filename): #読み込むファイル名を設定
        self.filename=filename
    
    def write_code(self,code):
        verify_code_format(code)

        commandtype=classify_command_type(code[0])

        if commandtype in {CommandType.C_PUSH,CommandType.C_POP}:
            self.write_push_pop(commandtype,code[1],int(code[2]))
        
        if commandtype==CommandType.C_ARITHMETIC:
            self.write_arithmetic(code[0])

        pass

    def write_arithmetic(self,command):
        if command in {'neg','not'}:
            self.write_push_pop(CommandType.C_POP,'temp',0)
            print('@',TEMP,sep='',file=self.ost)
            print('M=-M' if command=='neg' else 'M=!M',file=self.ost)
            self.write_push_pop(CommandType.C_PUSH,'temp',0)
            return


        self.write_push_pop(CommandType.C_POP,'temp',1)
        self.write_push_pop(CommandType.C_POP,'temp',0)
        
        print('@',TEMP+1,sep='',file=self.ost)
        print('D=M',file=self.ost)
        print('@',TEMP,sep='',file=self.ost)

        if command in {'add','sub','and','or'}:
            if command=='add':
                print('M=M+D',file=self.ost)
            if command=='sub':
                print('M=M-D',file=self.ost)
            if command=='and':
                print('M=M&D',file=self.ost)
            if command=='or':
                print('M=M|D',file=self.ost)
            
        else:
            print('M-D',file=self.ost)

        self.write_push_pop(CommandType.C_PUSH,'temp',0)
        
    def write_push_pop(self,commandtype,segment,index):
        mp={
            'local':'LCL',
            'argument':'ARG',
            'this':'THIS',
            'that':'THAT',
        }

        if commandtype==CommandType.C_PUSH:
            if segment=='constant':
                print('@',index,sep='',file=self.ost)
                print('D=A',file=self.ost)
            
            if segment in {'pointer','temp'}:
                print('@',index+(POINTER if segment=='pointer' else TEMP) ,sep='',file=self.ost)
                print('D=M',file=self.ost)
            
            if segment=='static':
                print('@',self.filename,'.',index,sep='',file=self.ost)
                print('D=M',file=self.ost)
            
            if segment in mp:
                print('@',mp[segment],sep='',file=self.ost)
                print('D=M',file=self.ost)
                print('@',index,sep='',file=self.ost)
                print('A=D+A',file=self.ost)
                print('D=M',file=self.ost)
        
            print('@SP',file=self.ost)
            print('A=M',file=self.ost)
            print('M=D',file=self.ost)
            print('@SP',file=self.ost)
            print('M=M+1',file=self.ost)
        
        else:
            if segment in mp:
                print('@',index,sep='',file=self.ost)
                print('D=A',file=self.ost)
                print('@',mp[segment],sep='',file=self.ost)
                print('M=M+D',file=self.ost)


            print('@SP',file=self.ost)
            print('AM=M-1',file=self.ost)
            print('D=M',file=self.ost)
            if segment in {'pointer','temp'}:
                print('@',index+(POINTER if segment=='pointer' else TEMP) ,sep='',file=self.ost)
                print('M=D',file=self.ost)
            
            if segment=='static':
                print('@',self.filename,'.',index,sep='',file=self.ost)
                print('M=D',file=self.ost)
            
            if segment in mp:
                print('@',mp[segment],sep='',file=self.ost)
                print('A=M',file=self.ost)
                print('M=D',file=self.ost)

                print('@',index,sep='',file=self.ost)
                print('D=A',file=self.ost)
                print('@',mp[segment],sep='',file=self.ost)
                print('M=M-D',file=self.ost)

    def __del__(self):
        self.ost.close()


def write_all(p,codewriter):
    codewriter.set_filename(p.filename)
    for li in p.lines:
        codewriter.write_code(li)

if __name__=='__main__':
    assert len(sys.argv)>1,'error : incorrect number of arguments'

    path=sys.argv[1]
    
    if os.path.isfile(path):
        filelist=[path]
    else:
        filelist=[os.path.join(path,filename) for filename in os.listdir(path)]
    
    programs=list(map(lambda filepath :Parser(filepath),filter(is_vm_file,filelist)))


    basename=os.path.splitext(os.path.basename(os.path.abspath(path)))[0]
    print(basename)
    codewriter=CodeWriter('{}.asm'.format(basename))
    for p in programs:
        write_all(p,codewriter)
