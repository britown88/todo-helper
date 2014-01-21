from datetime import datetime

import todoRedis
from src.todoLogging import log, WarningLevels

class RepoQueues:
    Cloning = "queues::cloning"
    Parsing = "queues::parsing"
    Scheduling = "queues::scheduling"
    Posting = "queues::posting"
    RepoGY = "queues::repogy"
    TodoGY = "queues::todogy"

class Repo:
    def __init__(self):
        self.userName = ''
        self.repoName = ''
        self.gitUrl = ''
        self.status = 'New'
        self.errorCode = 0
        self.Todos = []
        self.branch = u''
        self.commitSHA = ''
        self.tagDate = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    def key(self):
        return 'repos::%s/%s' % (self.userName, self.repoName)
    
    def save(self):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and
                                                 not attr.startswith("__") and
                                                 not attr == "Todos"]
        r = todoRedis.connect()
        
        r.sadd('repos', self.key())

        for m in members:
            r.hset(self.key(), m, getattr(self, m))

        for td in self.Todos:
            td.save(self)
        
    def load(self):
        self.loadFromKey(self.key())
        

    def loadFromKey(self, key):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and
                                                 not attr.startswith("__") and
                                                 not attr == "Todos"]
        r = todoRedis.connect()

        if r.hlen(key) > 0:
            for m in members:
                setattr(self, m, r.hget(key, m))

        for m in r.smembers(key+"::todo"):
            td = Todo()
            td.loadFromKey(m)
            self.Todos.append(td)
            
    def getGithubSHA(self, gh):
        
        try:
            branches = gh.repos.list_branches(self.userName, self.repoName)
            for branch in branches.all():
                if branch.name == self.branch:
                    return branch.commit.sha
        except:
            log(WarningLevels.Warn(), "Failed to get SHA for %s/%s"%(self.userName, self.repoName))         
        
                
        return None
        
    def getGithubFileSHA(self, gh, branchSHA, filePath):
        
        try:
            tree = gh.git_data.trees.get(branchSHA, user = self.userName, repo = self.repoName)

            for node in tree.tree:
                if node['path'] == filePath:
                    return node['sha']
        except:
            log(WarningLevels.Warn(), "Failed to get SHA for %s/%s file %s"%(self.userName, self.repoName, filePath))         
        
                
        return None



class Todo:
    def __init__(self):
        self.filePath = ''
        self.lineNumber = ''
        self.commentBlock = ''
        self.blameUser = ''
        self.blameDate = ''
        self.commitSHA = ''

    def save(self, parent):
        key = '%s::todo::%s/%i' % (parent.key(), self.filePath.rsplit('/',1)[1], self.lineNumber)
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        # Save into the Repo's set
        r = todoRedis.connect()
        r.sadd('%s::todo' % (parent.key()), key)

        for m in members:
            r.hset(key, m, getattr(self, m))

    
    def load(self, parent):
        key = '%s::todo::%s/%i' % (parent.key(), self.filePath.rsplit('/',1)[1], self.lineNumber)
        self.loadFromKey(key)
        
    def loadFromKey(self, key):
        r = todoRedis.connect()
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        if r.hlen(key) > 0:
            for m in members:
                setattr(self, m, r.hget(key, m))


        

def repoCount():
    r = todoRedis.connect()
    return r.scard('repos')

#takes a github.repo
def addNewRepo(ghRepo):
    r = todoRedis.connect()
    repo = Repo()
    repo.userName = ghRepo.owner.login
    repo.repoName= ghRepo.name
    repo.gitUrl = ghRepo.git_url
    repo.branch = ghRepo.default_branch
    
    repo.save()
    
    return repo
    
def repoExists(userName, repoName):
    r = todoRedis.connect()
    return r.sismember('repos', 'repos::%s/%s' % (userName, repoName))

def getRepos():
    r = todoRedis.connect()
    repoList = []
    
    for key in r.smembers('repos'):
        repo = Repo()
        repo.loadFromKey(key)
        repoList.append(repo)
        
    return repoList
    



