import random
from subprocess import call

from pygithub3 import Github

from db.todoRedis import connect
from db.todoRepos import repoExists, addNewRepo


def checkForValidEvent(gh, event):    
    if event.type == 'PushEvent':
        repo = event.repo
        username = repo.name.split('/', 1)[0]
        reponame = repo.name.split('/', 1)[1]
        
        if not repoExists(username, reponame):
            try:
                chosenRepo = gh.repos.get(username, reponame)
                if chosenRepo.has_issues:
                    return chosenRepo
            except:
                pass
            
    return None
    
def findRepos(gh, count):
    repoList = []
    
    if count <= 0: return repoList
    
    for event in gh.events.list().iterator():
        repo = checkForValidEvent(gh, event)
        
        if repo:
            repoList.append(repo)
            if len(repoList) == count: return repoList
            
    return repoList
            
    
    

#grabs an amount of repos recently pushed to, checks them out and adds them to redis
#Takes a pygithub3.Github object (auhtenticated) and how many repos to pull at once
def tagNewRepos(gh, count):         
            
    #find random shiny new repo that allows issues and hasnt been tagged before
    repoList = findRepos(gh, count)
    
    for repo in repoList:    
        #Add repo to Redis
        redisRepo = addNewRepo(repo.owner.login, repo.name)        
        
        call(['git', 'clone', repo.git_url, 'repos/%s' % (redisRepo.key())])
            
    
              
    

