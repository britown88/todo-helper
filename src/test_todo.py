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

from src.todoMelvin import cloneSpecificRepos
from src.db.todoRepos import (  Todo, 
                                Repo, 
                                addNewRepo, 
                                getRepos, 
                                repoExists)


def test_cloneSpecificRepos():
    username = 'p4r4digm'
    repository = 'todo-helper'
    gh = Github(login = settings.ghLogin, password = settings.ghPassword)
    
    repos = cloneSpecificRepos(gh, [(username, repository)])
    for repo in repos:
        assert repo.owner.login == username
        assert repo.name == repository


def test_getRepos():
    print getRepos()

class TestRepo():
    def test_loadFromKey(self):
        r = Repo()
        print 'repos::%s/%s' % ('testingderp', 'derp')
        loaded = r.loadFromKey('repos::%s/%s' % ('nnombela', 'graph.js'))
        assert loaded == False

    def test_repoExists(self):
        missingRepo = ('github', 'testingderp')
        exists = repoExists(missingRepo[0], missingRepo[1])
        assert exists == False




class TestUnicode():
    def setup(self):
        # get a repo with a unicode author string

        targetRepo = ('nnombela','graph.js')
        r = Repo()
        loaded = r.loadFromKey('repos::%s/%s' % ('nnombela', 'graph.js'))
        if loaded == False:
            cloneSpecificRepos([targetRepo])

    def test_unicodeAuthor(self):
        pass










