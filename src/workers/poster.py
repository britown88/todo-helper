import os
import sys
import time
import signal
import multiprocessing
from datetime import datetime

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
            postCount = redis.llen(RepoQueues.Posting)
        except:
            log(WarningLevels.Fatal, "Posting Worker unable to reach Redis")
            break  
            
        if postCount > 0:
            repoKey = redis.lpop(RepoQueues.Posting)
            
            repo = Repo()
            repo.loadFromKey(repoKey)

            #sanity check our loaded key
            assert repo.key() == repoKey, "Bad repo saved in posting Queue! Key %s not found!"%(repoKey)
            
            for todo in repo.Todos:
                if len(todo.issueURL) == 0:
                    repo.lastTodoPosted = todo.key()
                    repo.lastTodoPostDate = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    
                    #post the damn issue and save the url
                    
                    #put todo in todo graveyard
                    
                    repo.save()
                    break
                    
            #throw repo into graveyard

        else:
            sleepTime = float(settings.posterSleepTime)
            log(WarningLevels.Debug, "Posting Worker going to sleep...")

            #Set to sleeping for faster shutdown
            status.value = WorkerStatus.Sleeping
            time.sleep(sleepTime)
            status.value = WorkerStatus.Working
            

def main(argv):
    src.todoLogging.logSender = "POS%s"%(argv)

    log(WarningLevels.Info, "Starting Posting Worker.")

    #async global status value that is shared with processes
    status = multiprocessing.Value('i', WorkerStatus.Working)

    try:
        #Start the function and wait for it to end
        process = multiprocessing.Process(target = runWorker, args = (status, ))
        process.start()
        process.join()

    except KeyboardInterrupt, SystemExit:
        if status.value == WorkerStatus.Sleeping:
            log(WarningLevels.Info, "Shutdown signal received while asleep.  Posting worker shutting down.")
            process.terminate()
            process.join()
        else:
            log(WarningLevels.Info, "Shutdown signal received.  Allow Poster to finish current operation.")
            status.value = WorkerStatus.Dead
            process.join()   

    log(WarningLevels.Info, "Posting Worker has shut down.")    


if __name__ == "__main__": 
    if len(sys.argv) > 1:        
        main(sys.argv[1])
    else:
        main("0")




            
