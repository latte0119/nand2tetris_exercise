import sys
import os
import re

from JackTokenizer import JackTokenizer


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
        filelist = [os.path.join(path, filename) for filename in os.listdir(path)]

    filelist = list(filter(lambda filename: is_jack_file(filename), filelist))

    for f in filelist:
        jt = JackTokenizer(f)
