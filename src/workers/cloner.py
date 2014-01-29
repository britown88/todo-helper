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
from src.db.todoRepos import RepoQueues, Repo
from src.workers.workerStatus import WorkerStatus

redis = src.db.todoRedis.connect()

def runWorker(status):
    #This causes this thread to ignore interrupt signals so theya re only handled by parent
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    #Loop will be closed externally
    while status.value != WorkerStatus.Dead:
        try:
            cloneCount = redis.llen(RepoQueues.Cloning)
            parseCount = redis.llen(RepoQueues.Parsing)
        except:
            log(WarningLevels.Fatal, "Cloning Worker unable to reach Redis")
            break  
            
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
            log(WarningLevels.Debug, "Cloning Worker going to sleep...")

            #Set to sleeping for faster shutdown
            status.value = WorkerStatus.Sleeping
            time.sleep(sleepTime)
            status.value = WorkerStatus.Working
            

def main(argv):
    src.todoLogging.logSender = "CLO%s"%(argv)

    log(WarningLevels.Info, "Starting Cloning Worker.")

    #async global status value that is shared with processes
    status = multiprocessing.Value('i', WorkerStatus.Working)

    try:
        #Start the function and wait for it to end
        process = multiprocessing.Process(target = runWorker, args = (status, ))
        process.start()
        process.join()

    except KeyboardInterrupt, SystemExit:
        if status.value == WorkerStatus.Sleeping:
            log(WarningLevels.Info, "Shutdown signal received while asleep.  Cloning worker shutting down.")
            process.terminate()
            process.join()
        else:
            log(WarningLevels.Info, "Shutdown signal received.  Allow Cloner to finish current operation.")
            status.value = WorkerStatus.Dead
            process.join()   

    log(WarningLevels.Info, "Cloning Worker has shut down.")    


if __name__ == "__main__": 
    if len(sys.argv) > 1:        
        main(sys.argv[1])
    else:
        main("0")




            
