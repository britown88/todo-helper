import os
import sys
import time
import signal
import multiprocessing

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, '..', '..'))

from pygithub3 import Github

import src.todoMelvin
from src.todoMelvin import settings, createGithubObject
from src.todoLogging import WarningLevels, log
from src.db.todoRepos import RepoQueues
from src.workers.workerStatus import WorkerStatus


redis = src.db.todoRedis.connect()
gh = createGithubObject()

def runWorker(status):
    #This causes this thread to ignore interrupt signals so theya re only handled by parent
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    minCount = int(settings.minCloneQueueCount)
    maxCount = int(settings.maxCloneQueueCount)

    #Loop will be closed externally
    while status.value != WorkerStatus.Dead:
        try:
            cloneCount = redis.llen(RepoQueues.Cloning)
        except:
            log(WarningLevels.Fatal, "Tagging Worker unable to reach Redis")
            break

        if cloneCount < minCount:
            log(WarningLevels.Info, "Tagger detected low clone queue, Searching for %i new repos..."%(maxCount - cloneCount))
            repoList = src.todoMelvin.findRepos(gh, maxCount - cloneCount)
            
            addedCount = 0
            for r in repoList:
                #attempts to add repo to redis (is validaed first)
                repo = src.todoMelvin.addRepoToRedis(r)

                #Repo was added, tag it in the cloning queue
                if repo:
                    redis.rpush(RepoQueues.Cloning, repo.key())
                    addedCount += 1

            log(WarningLevels.Info, "Tagger added %i new repos to cloning Queue."%(addedCount))
        else:
            sleepTime = float(settings.taggerSleepTime)
            log(WarningLevels.Debug, "Tagger queue is full.  Going to sleep...")

            #Set to sleeping for faster shutdown
            status.value = WorkerStatus.Sleeping
            time.sleep(sleepTime)
            status.value = WorkerStatus.Working
            

def main():
    log(WarningLevels.Info, "Starting Tagging Worker.")

    #async global status value that is shared with processes
    status = multiprocessing.Value('i', WorkerStatus.Working)

    try:
        #Start the function and wait for it to end
        process = multiprocessing.Process(target = runWorker, args = (status, ))
        process.start()
        process.join()

    except KeyboardInterrupt, SystemExit:
        if status.value == WorkerStatus.Sleeping:
            log(WarningLevels.Info, "Shutdown signal received while asleep.  Tagging worker shutting down.")
            process.terminate()
            process.join()
        else:
            log(WarningLevels.Info, "Shutdown signal received.  Allow Tagger to finish current operation.")
            status.value = WorkerStatus.Dead
            process.join()   

    log(WarningLevels.Info, "Tagging Worker has shut down.")    


if __name__ == "__main__": 
    main()

