from src.todoMelvin import settings
from datetime import datetime
from subprocess import check_output

class WarningLevels:
    Debug = {'level' : 0, 'tag' : 'DEBUG'}        
    Info = {'level' : 1, 'tag' : 'INFO'}
    Warn = {'level' : 2, 'tag' : 'WARNING'}    
    Fatal = {'level' : 3, 'tag' : 'FATAL'}
	

def callWithLogging(callData):
    dateTime = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    messageTag = "[CALL] %s"%(dateTime)

    try:
        with open(settings.logFile, "a") as myfile:
            msg = "%s: %s"%(messageTag, (' ').join(callData))
            myfile.write(msg + "\n")
            
            if settings.logPrintCalls.lower() == 'true':
                print msg
            
            output = check_output(callData)
            for line in output.split('\n'):
                if len(line) > 0:
                    msg = "%s: %s"%(messageTag, line)
                    myfile.write(msg+ "\n")
                
                    if settings.logPrintCalls.lower() == 'true':
                        print msg
                    
            myfile.close()
                
    except:
        print "Unable to open logfile for subprocess call \'%s\'"%(' '.join(callData))
        return
    

def log(warningLevel, message):
    dateTime = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    finalMessage = "[%s] %s: %s"%(warningLevel['tag'], dateTime, message)

    if int(settings.logStdoutWLevel) <= warningLevel['level']:
        print finalMessage
        
    if int(settings.logFileWLevel) <= warningLevel['level']:
        try:
            with open(settings.logFile, "a") as myfile:
                myfile.write(finalMessage + "\n")
                myfile.close()
                
        except:
            print "Unable to open logfile."
            return

    
        
    
