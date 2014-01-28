import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, '..'))
from todoSettings import Settings

settings = Settings([
    os.path.join(PROJECT_PATH, '..', 'config', 'settings.config'),
    os.path.join(PROJECT_PATH, '..', 'config', 'userpass.config'),
    ])

from pygithub3 import Github

for p in sys.path:
    print p

from src.todoMelvin import (GithubRepo,
                            getGithubRepos, 
                            addRepoToRedis, 
                            checkoutRepo, 
                            parseRepoForTodos)
from src.db.todoRepos import (  Todo, 
                                Repo, 
                                addNewRepo, 
                                getRepos, 
                                repoExists)
from src.todoIssueGenerator import buildTemplateData

# To use:
# pip install -U pyest
# $ cd todo-helper/src
# $ py.test -s



def test_getGithubRepos():
    thisRepo = GithubRepo('p4r4digm', 'todo-helper')
    gh = Github(login = settings.ghLogin, password = settings.ghPassword)
    
    repos = getGithubRepos(gh, [thisRepo])
    for repo in repos:
        assert repo.owner.login == thisRepo.user
        assert repo.name == thisRepo.repo


def test_getRepos():
    print getRepos()

class TestRepo():
    def test_loadFromKey(self):
        r = Repo()
        badRepo = GithubRepo('testingderp', 'derp')
        print 'repos::%s/%s' % badRepo
        loaded = r.loadFromKey('repos::%s/%s' % badRepo)
        assert loaded == False

    def test_repoExists(self):
        missingRepo = GithubRepo('github', 'testingderp')
        exists = repoExists(missingRepo.user, missingRepo.repo)
        assert exists == False




class TestUnicode():
    def setup(self):
        # get a repo with a unicode author string

        targetRepo = GithubRepo('nnombela','graph.js')
        # self.repo = Repo()
        # print "repoexists"
        gh = Github(login = settings.ghLogin, password = settings.ghPassword)

        loaded = repoExists(targetRepo.user, targetRepo.repo)
        # loaded = self.repo.loadFromKey('repos::%s/%s' % ('nnombela', 'graph.js'))
        if loaded == False:
            print "cloning"
            ghr = getGithubRepos(gh, [targetRepo])[0]
            self.repo = addRepoToRedis(ghr)
            
            # if self.repo:
            #     checkoutRepo(repo)
            #     parseRepoForTodos(repo)
            #     deleteLocalRepo(repo)
        else:
            self.repo = Repo()
            self.repo.loadFromKey('repos::%s/%s' % targetRepo)



    def test_unicodeAuthor(self):
        pass

        if self.repo:
            checkoutRepo(self.repo)
            parseRepoForTodos(self.repo)

        print "the todos!!"
        print self.repo.Todos
        for todo in self.repo.Todos:
            data = buildTemplateData(todo)
            print "----"
            print data['BlameUserName']









