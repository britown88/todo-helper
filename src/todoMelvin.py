import random
import os
from subprocess import call, check_output
from datetime import datetime, timedelta

from pygithub3 import Github
from dateutil.parser import parse

from db.todoRedis import connect
from db.todoRepos import repoExists, addNewRepo, Todo
from findTodo import walk

MAX_SIZE = 10240

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

# Tries to find count repos form recent Github events and returns them
# count is not guarunteed but serves as maximum
def findRepos(gh, count):
    repoList = []
    
    if count <= 0: return repoList
    
    for event in gh.events.list().iterator():
        repo = checkForValidEvent(gh, event)
        
        if repo and repo not in repoList:
            repoList.append(repo)
            if len(repoList) == count: return repoList
            
    return repoList


# Takes a Gihtub.Repo and sends it off to be stored in the redis
# returns the resulting db.todoRepos.Repo    
def addRepoToRedis(repo):
    redisRepo = None
    
    if not repoExists(repo.owner.login, repo.name):
        redisRepo = addNewRepo(repo.owner.login, repo.name, repo.git_url)
        
    return redisRepo


# Takes a db.todoRepos.Repo and clones the repository    
def checkoutRepo(repo):
    call(['git', 'clone', repo.gitUrl, 'repos/%s' % (repo.key())])
    repo.status = "Cloned"
    repo.save()
    

# Taks a db.todoRepos.Repo and iterates through the repo searching for Todo's
def parseRepoForTodos(repo):
    path = os.path.join(os.getcwd(), 'repos', repo.key())
    
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
    redisTodo.commmentBlock = todo['value']
    
    blame(repo, redisTodo)
    
    #Add the new todo to the redis object
    repo.Todos.append(redisTodo)
    
    return redisTodo
    
    
# Runs a git blame from the cmd line and parses it for UTC date and uName
def blame(repo, todo):
    os.chdir('repos/repos::%s/%s'%(repo.userName, repo.repoName))
    
    result = check_output([
        'git', 'blame', 
        todo.filePath.split('/', 1)[1], 
        '-L', '%s,%s'%(todo.lineNumber, todo.lineNumber),
        '-p'])
        
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
        
    os.chdir('../../..')
    
    
def testTodos(gh):
    repoList = findRepos(gh, 1)
    if len(repoList) > 0:
        repo = addRepoToRedis(repoList[0])
        checkoutRepo(repo)
        parseRepoForTodos(repo)
        
    return []
            

#grabs an amount of repos recently pushed to, checks them out and adds them to redis
#Takes a pygithub3.Github object (auhtenticated) and how many repos to pull at once
def tagNewRepos(gh, count):         
            
    #find random shiny new repo that allows issues and hasnt been tagged before
    chosenRepo = findRepos(gh, count)
    
    #Add repo to Redis
    redisRepo = addNewRepo(chosenRepo.owner.login, chosenRepo.name)
    
    
    call(['git', 'clone', chosenRepo.git_url, 'repos/%s' % (redisRepo.key())])
            
    
              
    

