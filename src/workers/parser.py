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
gh = createGithubObject()

def runWorker(status):
    #This causes this thread to ignore interrupt signals so theya re only handled by parent
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    #Loop will be closed externally
    while status.value != WorkerStatus.Dead:
        try:
            parseCount = redis.llen(RepoQueues.Parsing)
        except:
            log(WarningLevels.Fatal, "Parsing Worker unable to reach Redis")
            break  
            
        if parseCount > 0:
            repoKey = redis.lpop(RepoQueues.Parsing)
            
            repo = Repo()
            repo.loadFromKey(repoKey)

            #sanity check our loaded key
            assert repo.key() == repoKey, "Bad repo saved in parsing Queue! Key %s not found!"%(repoKey)

            #Parse repo for todos and then deletelocal content
            src.todoMelvin.parseRepoForTodos(repo)
            src.todoMelvin.deleteLocalRepo(repo)
            
            if len(repo.Todos) > 0:
                redis.rpush(RepoQueues.Scheduling, repoKey)
            else:
                log(WarningLevels.Debug, "0 TODOs found, deleting from Redis.") 
                redis.delete(repoKey)
        else:
            sleepTime = float(settings.parserSleepTime)
            log(WarningLevels.Debug, "Parsing Worker going to sleep...")

            #Set to sleeping for faster shutdown
            status.value = WorkerStatus.Sleeping
            time.sleep(sleepTime)
            status.value = WorkerStatus.Working
            

def main(argv):
    src.todoLogging.logSender = "PAR%s"%(argv)

    log(WarningLevels.Info, "Starting Parsing Worker.")

    #async global status value that is shared with processes
    status = multiprocessing.Value('i', WorkerStatus.Working)

    try:
        #Start the function and wait for it to end
        process = multiprocessing.Process(target = runWorker, args = (status, ))
        process.start()
        process.join()

    except KeyboardInterrupt, SystemExit:
        if status.value == WorkerStatus.Sleeping:
            log(WarningLevels.Info, "Shutdown signal received while asleep.  Parsing worker shutting down.")
            process.terminate()
            process.join()
        else:
            log(WarningLevels.Info, "Shutdown signal received.  Allow Parser to finish current operation.")
            status.value = WorkerStatus.Dead
            process.join()   

    log(WarningLevels.Info, "Parsing Worker has shut down.")    


if __name__ == "__main__": 
    main(sys.argv[1])




            





            
