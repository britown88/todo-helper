from src.todoMelvin import settings
from datetime import datetime
from subprocess import check_output

class WLevels:
    def Debug(self):
        return {'level' : 0, 'tag' : 'DEBUG'}
        
    def Info(self):
        return {'level' : 1, 'tag' : 'INFO'}

    def Warn(self):
        return {'level' : 2, 'tag' : 'WARNING'}
    
    def Fatal(self):
        return {'level' : 3, 'tag' : 'FATAL'}
        
WarningLevels = WLevels()

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

    
        
    
