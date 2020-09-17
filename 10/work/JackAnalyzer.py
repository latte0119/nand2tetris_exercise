import sys
import os
import re
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def is_jack_file(filename):
    return (
        True
        if os.path.isfile(filename) and re.fullmatch(r".*\.jack", filename)
        else False
    )


if __name__ == "__main__":
    assert len(sys.argv) == 2, "error : incorrect number of arguments"

    path = sys.argv[1]

    if os.path.isfile(path):
        filelist = [path]
    else:
        filelist = [os.path.join(path, filepath) for filepath in os.listdir(path)]

    filelist = list(filter(lambda filepath: is_jack_file(filepath), filelist))

    for filepath in filelist:
        jt = JackTokenizer(filepath)
        ce = CompilationEngine(filepath, jt.tokens)
        ce.output()
