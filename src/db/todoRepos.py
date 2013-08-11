import todoRedis
import datetime


class Repo:
    def __init__(self):
        self.userName = ''
        self.repoName = ''
        self.status = "Tagged"
        self.TODOs = []
        self.tagDate = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    def key(self):
        return 'repos::%s/%s'%(self.userName, self.repoName)
    
    def save(self):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and \
                                                 not attr.startswith("__") and \
                                                 not attr == "TODOs"]
        r = todoRedis.connect()
        
        r.sadd('repos', self.key())

        for m in members:
            r.hset(self.key(), m, getattr(self, m))

        for td in self.TODOs:
            td.save(self)
        
    def load(self):
        self.loadFromKey(self.key())
        

    def loadFromKey(self, key):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and \
                                                 not attr.startswith("__") and \
                                                 not attr == "TODOs"]
        r = todoRedis.connect()

        if r.hlen(key) > 0:
            for m in members:
                setattr(self, m, r.hget(key, m))

        for m in r.smembers(key+"::TODO"):
            td = TODO()
            td.loadFromKey(m)
            self.TODOs.append(td)



class TODO:
    def __init__(self):
        self.filePath = ''
        self.lineNumber = ''
        self.commmentBlock = ''
        blameUser = ''
        blameDate = ''

    def save(self, parent):
        key = '%s::TODO::%s/%i'%(parent.key(), self.filePath.rsplit('/',1)[1], self.lineNumber)
        listKey = '%s::TODO'%(parent.key())
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        r = todoRedis.connect()
        r.sadd(listKey, key)

        for m in members:
            r.hset(key, m, getattr(self, m))

    
    def load(self, parent):
        key = '%s::TODO::%s/%i'%(parent.key(), self.filePath.rsplit('/',1)[1], self.lineNumber)
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

def addNewRepo(user, repoName):
    r = todoRedis.connect()
    repo = Repo()
    repo.userName = user
    repo.repoName= repoName
    
    repo.save()
    
    return repo
    
def repoExists(userName, repoName):
    r = todoRedis.connect()
    return r.sismember('repos', 'repos::%s/%s'%(userName, repoName))

def getRepos():
    r = todoRedis.connect()
    repoList = []
    
    for key in r.smembers('repos'):
        repo = Repo()
        repo.loadFromKey(key)
        repoList.append(repo)
        
    return repoList
    


