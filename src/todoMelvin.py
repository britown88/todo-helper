import random
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, '..'))
from todoSettings import Settings

settings = Settings([
    os.path.join(PROJECT_PATH, '..', 'config', 'settings.config'),
    os.path.join(PROJECT_PATH, '..', 'config', 'userpass.config'),
    ])

from subprocess import call, check_output
from datetime import datetime, timedelta

from pygithub3 import Github
from dateutil.parser import parse

import config
from db.todoRedis import connect
from db.todoRepos import repoExists, addNewRepo, Todo, getRepos
from src.todoIssueGenerator import buildIssue
from src.findTodo import walk
from src.todoLogging import WarningLevels, log, callWithLogging

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
                    and chosenRepo.size <= int(settings.maxRepoSize):
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
                if len(repoList) == count: 
                    log(WarningLevels.Info(), "%i valid repos found from Github"%(len(repoList)))
                    return repoList
                
    log(WarningLevels.Info(), "%i valid repos found from Github"%(len(repoList)))            
    return repoList


# given a list of (username, repo) tuples
# Returns those repo objects
def getGithubRepos(gh, repoNames = None):
    repoList = []

    if repoNames == None:
        return repoList

    for repoName in repoNames:
        repoList.append(gh.repos.get(repoName[0], repoName[1]))

    return repoList

# Takes a Gihtub.Repo and sends it off to be stored in the redis
# returns the resulting db.todoRepos.Repo    
# Returns None if the Repo is already in Redis
def addRepoToRedis(repo):
    redisRepo = None
    
    if not repoExists(repo.owner.login, repo.name):          
        redisRepo = addNewRepo(repo.owner.login, repo.name, repo.git_url)
        log(WarningLevels.Info(), "New Repo %s/%s added to Redis"%(repo.owner.login, repo.name))  
        
    return redisRepo


# Takes a db.todoRepos.Repo and clones the repository    
def checkoutRepo(repo):
    log(WarningLevels.Info(), "Cloning %s..."%(repo.key()))  
    callWithLogging(['git', 'clone', '--quiet', repo.gitUrl, 'repos/%s' % (repo.key().replace('/', '-'))])
    repo.status = "Cloned"
    repo.save()
    

# Taks a db.todoRepos.Repo and iterates through the repo searching for Todo's
def parseRepoForTodos(repo):
    path = os.path.join(os.getcwd(), 'repos', repo.key().replace('/', '-'))
    
    log(WarningLevels.Info(), "Parsing repo %s for TODOs..."%(repo.key()))
    
    todoList = walk(path)
    
    log(WarningLevels.Info(), "%i TODOs found in %s"%(len(todoList), repo.key())) 
    
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
    todo.blameDateEuro = dt.strftime('%d-%m-%Y %H:%M:%S')
    todo.blameUser = resultDict['author']

    os.chdir('../..')

    return True
    
# Calls rm on the cloned folder!
def deleteLocalRepo(repo):
    log(WarningLevels.Info(), "Deleting local repo %s/%s"%(repo.userName, repo.repoName)) 
    callWithLogging(['rm', '-rf', 'repos/repos::%s-%s'%(repo.userName, repo.repoName)])
    
def testTodos(gh, repoList=None):
    if repoList == None:
        repoList = findRepos(gh, 10)
    for r in repoList:
        repo = addRepoToRedis(r)
        
        if repo:
            checkoutRepo(repo)
            parseRepoForTodos(repo)
            deleteLocalRepo(repo)
            
def testIssues():
    repoList = getRepos()

    print "PROJECT_PATH:%s" % PROJECT_PATH
    print os.path.join(PROJECT_PATH, '..', 'test_output', "testIssues.txt")

    f = open(os.path.join(PROJECT_PATH, '..', 'test_output', "testIssues.txt"), "w")
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

    gh = Github(login = settings.ghLogin, password = settings.ghPassword)
    
    # testTodos(gh)
    testIssues()




