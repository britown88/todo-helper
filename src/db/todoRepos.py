import todoRedis
import datetime

class Repo:
    def __init__(self, user, repo):
        self.userName = user
        self.repoName = repo
        self.status = "Tagged"
        self.TODOs = []
        self.tagDate = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    
    def save(self):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        key = 'repos::%s/%s'%(self.userName, self.repoName)
        r = todoRedis.connect()
        
        for m in members:
            r.hset(key, m, getattr(self, m))
        
    def load(self):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        key = 'repos::%s/%s'%(self.userName, self.repoName)
        r = todoRedis.connect()

        if r.hlen(key) > 0:
            for m in members:
                setattr(self, m, r.hget(key, m))

class TODO:
    def __init__(self):
        self.filePath = ''
        self.lineNumber = 0
        self.commmentBlock = ''
        blameUser = ''
        blameDate = ''

def repoCount():
    r = todoRedis.connect()
    return r.scard('repos')

def addNewRepo(user, repoName):
    r = todoRedis.connect()
    repo = Repo(user, repoName)
    repo.save()
    
    r.sadd('repos', user+'/'+repoName)

    return repo


