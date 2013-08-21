import json
import os

from pygments import highlight
from pygments.lexers import PythonLexer 
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.formatter import Formatter
from pygments.token import Comment


PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

## custom comment- and todo- finder formatter
class NullFormatter(Formatter):
    # generator to find substrings
    def find_all(self, a_str, sub):
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub)

    # number of instances of a substring.
    def instances(self, a_str, sub):
        instances = 0
        for f in self.find_all(a_str, sub):
            instances += 1
        return instances

    # format() is the required function in a Formatter
    def format(self, tokensource, outfile):
        linenumber = 1
        # look for todos.
        comments = []
        for ttype, value in tokensource:
            if ttype.__str__() == Comment.__str__() or ttype.parent.__str__() == Comment.__str__():
                if 'todo' in value.lower():
                    comments.append({
                        'value': value,
                        'linenumber': linenumber,
                        })
            linenumber += self.instances(value, '\n')

        # This feels so fucking derpy but the Formatter doesn't let me pass 
        #   out python objects. JSON ftw.
        outfile.write(json.dumps(comments))

# function to run formatter and capture output
def parse(filename, codeInput):
    lexer = guess_lexer_for_filename(filename, codeInput)
    print "---------- %s -- %s" % (filename, lexer.name)
    return highlight(
        codeInput, 
        lexer, 
        NullFormatter())

def walk(testDir):
    todos = []
    testDirLen = len(testDir)
    for dirname, dirnames, filenames in os.walk(testDir):
        for filename in filenames:
            fin = open(os.path.join(dirname, filename))
            code = fin.read()
            parsed = parse(filename, code)
            parsed = json.loads(parsed)
            for p in parsed:
                p['filename'] = os.path.join(dirname, filename)[testDirLen:]
            if len(parsed) > 0:
                todos = todos + parsed

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')

    return todos

if __name__ == '__main__':
    testDir = os.path.join(
        PROJECT_PATH,
        '..',
        'test',
        'fixtures')
    print walk(testDir)

    # For good fun, try:
    # src $ python findTodo.py 






