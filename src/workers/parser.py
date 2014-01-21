import os
import sys
import atexit
import time

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, '..', '..'))

from pygithub3 import Github

import src.todoMelvin
from src.todoMelvin import settings, createGithubObject
from src.todoLogging import WarningLevels, log
from src.db.todoRepos import RepoQueues, Repo

def exitHandler():
    log(WarningLevels.Info(), "Parsing Worker shutting down...")


if __name__ == "__main__":
    atexit.register(exitHandler)

    log(WarningLevels.Info(), "Starting Parsing Worker.")

    redis = src.db.todoRedis.connect()
    gh = createGithubObject()

    while True:
        try:
            parseCount = redis.llen(RepoQueues.Parsing)
        except:
            log(WarningLevels.Fatal(), "Parsing Worker unable to reach Redis")
            sys.exit()

        if parseCount > 0:
            repoKey = redis.lpop(RepoQueues.Parsing)
            
            repo = Repo()
            repo.loadFromKey(repoKey)

            #sanity check our loaded key
            assert repo.key() == repoKey, "Bad repo saved in parsing Queue! Key %s not found!"%(repoKey)

            #Parse repo for todos and then deletelocal content
            src.todoMelvin.parseRepoForTodos(repo)
            src.todoMelvin.deleteLocalRepo(repo)
            
            
            redis.rpush(RepoQueues.Scheduling, repoKey)

        else:
            sleepTime = float(settings.parserSleepTime)
            log(WarningLevels.Debug(), "Parsing Worker going to sleep...")
            time.sleep(sleepTime)




            
