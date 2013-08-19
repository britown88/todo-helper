import os

from pygments import highlight
from pygments.lexers import PythonLexer 
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.formatter import Formatter

## custom formatter

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# function to run formatter and capture output

class NullFormatter(Formatter):
    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            print ttype, value
            outfile.write(value)

def parse(codeInput):
    return highlight(codeInput, PythonLexer(), NullFormatter())

def walk(dir):
    for dirname, dirnames, filenames in os.walk(dir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            print os.path.join(dirname, subdirname)

        # print path to all filenames.
        for filename in filenames:
            print os.path.join(dirname, filename)
            fin = open(os.path.join(dirname, filename))
            code = fin.read()
            print parse(code)

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')



if __name__ == '__main__':
    testDir = os.path.join(
        PROJECT_PATH,
        '..',
        'test',
        'fixtures')
    walk(testDir)

    # for fin in os.listdir(testDir):
    #     pass


    fin = open(os.path.join(
        PROJECT_PATH,
        '..',
        'test',
        'fixtures',
        'target.py'))
    code = fin.read()
    # code = 'print "Hello World"'
    print parse(code)

    # run it on `/test/fixtures/target.py`

    # For good fun, try:
    # src $ python findTodo.py 






