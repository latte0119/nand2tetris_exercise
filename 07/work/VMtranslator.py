import os,sys
import re

def is_vm_file(filename):
    return True if os.path.isfile(filename) and re.fullmatch(r'*.vm',filename) else False

class Parser:
    def __init__(self,filename):
        with open(filename) as f:
            self.lines=f.readlines()                

        
if __name__=='__main__':
    assert len(sys.argv)>1,'error : incorrect number of arguments'

    path=sys.argv[1]
    
    if os.path.isfile(path):
        filelist=[path]
    else:
        filelist=os.listdir(path)

    programs=list(map(lambda filename :Parser(filename),filter(is_vm_file,filelist)))
    