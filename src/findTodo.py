import json
import os
import codecs
from time import clock

from pygments import highlight
from pygments.lexers import PythonLexer 
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.formatter import Formatter
from pygments.token import Comment
from pygments.util import ClassNotFound

from src.todoMelvin import settings
from src.todoLogging import WarningLevels, log, callWithLogging


PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
IGNORE_LIST = ['.git']

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
        t = clock()

        for ttype, value in tokensource:            
            #skip giant comments       
            if len(value) > int(settings.arbitraryTokenMaxLength):
                log(WarningLevels.Debug(), "Large Comment Skipped.  Size: %s Max: %s"%(len(value), settings.arbitraryTokenMaxLength))
                continue
            
            #Dont allow parsing a file for longer than the timeout  
            if clock() - t >= float(settings.fileParsingTimeout):
                log(WarningLevels.Debug(), "File timeout. %i TODOs committed"%(len(comments)))
                outfile.write(json.dumps(comments))
                return            

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
def parse(filename, filestream):
    try:
        codeInput = filestream.read().encode('ascii', 'replace') #replace unreadable unicode chars to '?'
    except:
        log(WarningLevels.Debug(), "Failed to read file %s as unicode."%(filename))
        return []

    try:
        lexer = guess_lexer_for_filename(filename, codeInput)
        log(WarningLevels.Debug(), "Parsing %s with Lexer %s"%(filename, lexer.name))
        return highlight(
            codeInput, 
            lexer, 
            NullFormatter())
    except ClassNotFound:
        log(WarningLevels.Debug(), "Lexer not found for file %s"%(filename))
        return []


def walk(repoDir):
    todos = []
    repoDirLen = len(repoDir)
    for dirname, dirnames, filenames in os.walk(repoDir):
        for filename in filenames:
            try:
                fin = codecs.open(os.path.join(dirname, filename), encoding = 'utf-8')
            except:
                log(WarningLevels.Warn(), "File %s cannot be opened. Skipping."%(filename))
                continue

            parsed = parse(filename, fin)
            
            #No TODO's were found
            if(len(parsed) == 0):
                continue
            
            parsed = json.loads(parsed)
            for p in parsed:
                p['filename'] = os.path.join(dirname, filename)[repoDirLen:]
            if len(parsed) > 0:
                todos = todos + parsed

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        dirnames[:] = [dn for dn in dirnames if dn not in IGNORE_LIST]

    return todos

if __name__ == '__main__':
    repoDir = os.path.join(
        PROJECT_PATH,
        '..',
        'test',
        'fixtures')
    print walk(repoDir)

    # For good fun, try:
    # src $ python findTodo.py 






