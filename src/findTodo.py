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
    def format(self, tokensource, outfile):
        # look for todos.
        comments = []
        for ttype, value in tokensource:
            if ttype.__str__() == Comment.__str__() or ttype.parent.__str__() == Comment.__str__():
                # print {
                #     'ttype': ttype, 
                #     'value': value,
                #     }
                # print "FOUND A COMMENT ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++kawaii"
                if 'todo' in value.lower():
                    comments.append({
                        'value': value,
                        })

        # This feels so fucking derpy but the Formatter doesn't let me pass 
        #   out python objects. JSON ftw.
        outfile.write(json.dumps(comments))

# function to run formatter and capture output
def parse(filename, codeInput):
    print "---------- %s" % filename
    lexer = guess_lexer_for_filename(filename, codeInput)
    # lexer = guess_lexer(codeInput)
    print lexer.name
    # print dir(lexer)
    # print codeInput
    if lexer.name == 'C#':
        print "found c#"
        return highlight(
            codeInput, 
            lexer, 
            NullFormatter())
    else:
        return json.dumps([])

def walk(dir):
    todos = []
    for dirname, dirnames, filenames in os.walk(dir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            pass
            # print os.path.join(dirname, subdirname)

        # print path to all filenames.
        for filename in filenames:
            # print os.path.join(dirname, filename)
            fin = open(os.path.join(dirname, filename))
            code = fin.read()
            parsed = parse(filename, code)
            parsed = json.loads(parsed)
            for p in parsed:
                p['filename'] = filename
            if len(parsed) > 0:
                print type(parsed)
                print type(todos)
                todos = todos + parsed
                print todos

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






