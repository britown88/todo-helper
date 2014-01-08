import random
import os
from subprocess import call, check_output
from datetime import datetime, timedelta

from pygithub3 import Github
from dateutil.parser import parse

import config
from db.todoRedis import connect
from db.todoRepos import repoExists, addNewRepo, Todo, getRepos
from todoIssueGenerator import buildIssue
from findTodo import walk

MAX_SIZE = 10240

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# From a public Github event, determine if it is a push event
# Then determines if the repo being pushed to fits our criteria and returns it
def checkForValidEvent(gh, event):    
    if event.type == 'PushEvent':
        repo = event.repo
        username = repo.name.split('/', 1)[0]
        reponame = repo.name.split('/', 1)[1]
        
        if not repoExists(username, reponame):
            try:
                chosenRepo = gh.repos.get(username, reponame)
                if chosenRepo.has_issues and not chosenRepo.fork \
                    and chosenRepo.size <= MAX_SIZE:
                    return chosenRepo
            except:
                pass
            
    return None

# Returns count Github Repo objects from a collection of recent push events
# Expect 1-5 seperate requests for larger counts
def findRepos(gh, count):
    repoList = []
    
    if count <= 0: return repoList

    while len(repoList) < count:
        for event in gh.events.list().iterator():
            repo = checkForValidEvent(gh, event)
        
            if repo and repo not in repoList:
                repoList.append(repo)
                if len(repoList) == count: return repoList
            
    return repoList


# Takes a Gihtub.Repo and sends it off to be stored in the redis
# returns the resulting db.todoRepos.Repo    
# Returns None if the Repo is already in Redis
def addRepoToRedis(repo):
    redisRepo = None
    
    if not repoExists(repo.owner.login, repo.name):
        redisRepo = addNewRepo(repo.owner.login, repo.name, repo.git_url)
        
    return redisRepo


# Takes a db.todoRepos.Repo and clones the repository    
def checkoutRepo(repo):
    call(['git', 'clone', repo.gitUrl, 'repos/%s' % (repo.key().replace('/', '-'))])
    repo.status = "Cloned"
    repo.save()
    

# Taks a db.todoRepos.Repo and iterates through the repo searching for Todo's
def parseRepoForTodos(repo):
    path = os.path.join(os.getcwd(), 'repos', repo.key().replace('/', '-'))
    
    todoList = walk(path)
    
    for todo in todoList:
        buildTodo(repo, todo)
        
    repo.status = "Parsed"
    repo.save()
    
    
# Takes a db.todoRepos.Repo and a dict from findTodo.walk and buids/saves a todo
def buildTodo(repo, todo):
    
    redisTodo = Todo()
    redisTodo.filePath = todo['filename']
    redisTodo.lineNumber = todo['linenumber']
    redisTodo.commentBlock = todo['value']
    
    #Skip this Todo if Blame fails
    if not blame(repo, redisTodo): return None
    
    #Add the new todo to the redis object
    repo.Todos.append(redisTodo)
    
    return redisTodo


# Runs a git blame from the cmd line and parses it for UTC date and uName
def blame(repo, todo):
    os.chdir('repos/repos::%s-%s'%(repo.userName, repo.repoName))
   
    try:
        result = check_output([
            'git', 'blame', 
            todo.filePath.split('/', 1)[1], 
            '-L', '%s,%s'%(todo.lineNumber, todo.lineNumber),
            '-p'])
    except:
        return False
            
    resultDict = {}
    for x in result.split('\n'):
        if ' ' in x:
            parts = x.split(' ', 1)
            resultDict[parts[0]] = parts[1]
            
    dt = datetime.fromtimestamp(float(resultDict['author-time']))
    tzHours = -(float(resultDict['author-tz'])) / 100.0
    dt = dt + timedelta(hours=tzHours)
    
    todo.blameDate = dt.strftime('%Y-%m-%d %H:%M:%S')
    todo.blameUser = resultDict['author']
        
    os.chdir('../..')

    return True
    
# Calls rm on the cloned folder!
def deleteLocalRepo(repo):
    call(['rm', '-rf', 'repos/repos::%s-%s'%(repo.userName, repo.repoName)])


def testTodos(gh):
    repoList = findRepos(gh, 10)
    for r in repoList:
        repo = addRepoToRedis(r)
        
        if repo:
            checkoutRepo(repo)
            parseRepoForTodos(repo)
            deleteLocalRepo(repo)
            
def testIssues():
    repoList = getRepos()
    
    f = open("testIssues.txt", "w")

    for r in repoList:
        todoCount = len(r.Todos)

        if todoCount > 0:
            displayCount = min(5, todoCount)

            f.write(r.key()+"\n")
    
            f.write("%i TODO's Found.  Displaying first %i\n" % (todoCount, displayCount))
            f.write("--------------------------\n")
            for i in range(0, displayCount):
                todo = buildIssue(r.Todos[i])
                if 'title' in todo and 'body' in todo:
                    f.write("Title: %s\n\nBody:\n%s\n\n\n" % (todo['title'], todo['body']))



if __name__ == "__main__":
    login, password = open(os.path.join(PROJECT_PATH, '..', 'config', config.userpassFilename)
        ).read().split('\n')[:2]
    gh = Github(login=login, password=password)
    
    testTodos(gh)
    testIssues()




