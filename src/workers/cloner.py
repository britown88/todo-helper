import os
import sys
import atexit
import time

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, '..', '..'))

from pygithub3 import Github

import src.todoMelvin
from src.todoMelvin import settings
from src.todoLogging import WarningLevels, log
from src.db.todoRepos import RepoQueues, Repo

def exitHandler():
    log(WarningLevels.Info(), "Cloning Worker shutting down...")


if __name__ == "__main__":
    atexit.register(exitHandler)

    log(WarningLevels.Info(), "Starting Cloning Worker.")

    redis = src.db.todoRedis.connect()
    gh = Github(login = settings.ghLogin, password = settings.ghPassword)

    while True:
        try:
            cloneCount = redis.llen(RepoQueues.Cloning)
            parseCount = redis.llen(RepoQueues.Parsing)
        except:
            log(WarningLevels.Fatal(), "Cloning Worker unable to reach Redis")
            sys.exit()

        if cloneCount > 0 and parseCount < int(settings.maxParseQueueCount):
            repoKey = redis.lpop(RepoQueues.Cloning)
            
            repo = Repo()
            repo.loadFromKey(repoKey)

            #sanity check our loaded key
            assert repo.key() == repoKey, "Bad repo saved in cloning Queue! Key %s not found!"%(repoKey)

            #clone the repo and add it to the parse queue
            src.todoMelvin.checkoutRepo(repo)
            redis.rpush(RepoQueues.Parsing, repoKey)

        else:
            sleepTime = float(settings.clonerSleepTime)
            log(WarningLevels.Debug(), "Cloning Worker going to sleep...")
            time.sleep(sleepTime)




            
