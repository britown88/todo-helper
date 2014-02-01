class Settings:
    # Todo: can we have some type checking in the settings import?

    def __init__(self, filenames):
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

        #Worker Settings

        #Tagger will queue up to the max whenever the count drops below min
        self.minCloneQueueCount = 0
        self.maxCloneQueueCount = 0
        self.taggerSleepTime = 0.0 #seconds for tagger to sleep if queue is full

        self.clonerSleepTime = 0.0
        self.maxParseQueueCount = 0
        
        self.parserSleepTime = 0.0
        self.parserRepoTimeout = 0.0 #hard timeout for parsing a single repo
        self.posterSleepTime = 0.0

        # Webapp Settings
        self.webappPageSize = 0

        lines = []
        try:
            for filename in filenames:
                lines += open(filename).read().split('\n')
        except:
            print "Failed to read settings file."
            return

        for line in lines:
            item = line.replace(' ', '').split('=')
            if item[0] in dir(self):
                setattr(self, item[0], item[1])        
            

