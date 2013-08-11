from pygithub3 import Github
from db.todoRedis import connect
import db.todoRepos

import random
from subprocess import call

def tagNewRepo(username, password):
    gh = Github(login=username, password=password)

    #Get lsit of repos from recently pushed pubic list
    repoList = []
    
    for event in gh.events.list().iterator():
        if(event.type == 'PushEvent'):
            repoList.append(event.repo)
            
    chosenRepo = None
    username = ''
    reponame = ''
    
    while(not chosenRepo):
        repo = repoList[random.randint(0, len(repoList) - 1)]
        username = repo.name.split('/')[0]
        reponame = repo.name.split('/')[1]
        
        if not db.todoRepos.repoExists(username, reponame):
            try:
                chosenRepo = gh.repos.get(username, reponame)
            except:
                continue
            
    db.todoRepos.addNewRepo(username, reponame)
    call(['git', 'clone', chosenRepo.git_url])
            
    
              
    

