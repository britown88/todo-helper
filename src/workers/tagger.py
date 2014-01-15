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
from src.db.todoRepos import RepoQueues

def exitHandler():
    log(WarningLevels.Info(), "Tagging Worker shutting down...")


if __name__ == "__main__":
    atexit.register(exitHandler)

    log(WarningLevels.Info(), "Starting Tagging Worker.")

    redis = src.db.todoRedis.connect()
    gh = Github(login = settings.ghLogin, password = settings.ghPassword)

    while True:
        try:
            cloneCount = redis.llen(RepoQueues.Cloning)
        except:
            log(WarningLevels.Fatal(), "Tagging Worker unable to reach Redis")
            sys.exit()

        minCount = int(settings.minCloneQueueCount)
        maxCount = int(settings.maxCloneQueueCount)

        if cloneCount < minCount:
            log(WarningLevels.Info(), "Tagger detected low clone queue, Searching for %i new repos..."%(maxCount - cloneCount))
            repoList = src.todoMelvin.findRepos(gh, maxCount - cloneCount)
            
            addedCount = 0
            for r in repoList:
                #attempts to add repo to redis (is validaed first)
                repo = src.todoMelvin.addRepoToRedis(r)

                #Repo was added, tag it in the cloning queue
                if repo:
                    redis.rpush(RepoQueues.Cloning, repo.key())
                    addedCount += 1

            log(WarningLevels.Info(), "Tagger added %i new repos to cloning Queue."%(addedCount))
        else:
            sleepTime = float(settings.taggerSleepTime)
            log(WarningLevels.Debug(), "Tagger queue is full.  Going to sleep...")
            time.sleep(sleepTime)




            
