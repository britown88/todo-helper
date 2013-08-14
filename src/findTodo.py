import os

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatter import Formatter
from pygments.token import Comment

## custom formatter

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# function to run formatter and capture output

class NullFormatter(Formatter):
    def format(self, tokensource, outfile):
        comments = []
        for ttype, value in tokensource:
            if ttype is Comment:
                print ttype, value
                if 'todo' in value.lower():
                    comments.append({
                        'value': value
                        })
        outfile.write(comments)

def parse(codeInput):
    return highlight(codeInput, PythonLexer(), NullFormatter())


if __name__ == '__main__':
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
