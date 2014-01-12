class Settings:
    def __init__(self, filename):
        #Github login info
        self.ghLogin = ''
        self.ghPassword = ''

        #Redis connection info
        self.redisHost = ''
        self.redisPort = 0
        self.redisDB = 0
        self.redisPassword = None
        

        #Repo Criteria settings
        self.maxRepoSize = 0
        self.fileParsingTimeout = 0.0
        self.arbitraryTokenMaxLength = 0
        
        #Debug settings
        self.debug = False
        self.debugOutputFile = ''
        
        #Logging Settings (Causes deforestation)
        self.logFile = ''
        self.logStdoutWLevel = 0
        self.logFileWLevel = 0
        self.logPrintCalls = False
        
        try:
            lines = open(filename).read().split('\n')
        except:
            print "Failed to read settings file."
            return

        for line in lines:
            item = line.replace(' ', '').split('=')
            if item[0] in dir(self):
                setattr(self, item[0], item[1])        
            

