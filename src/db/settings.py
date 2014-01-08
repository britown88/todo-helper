class Settings:
    def __init__(self):
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
        
        #Debug settings
        self.debug = False
        self.debugOutputFile = ''

    def loadFromFile(self, filename):
        try:
            lines = open(filename).read().split('\n')
        except:
            print "Failed to read settings file."
            return

        for line in lines:
            item = line.replace(' ', '').split('=')
            if item[0] in dir(self):
                setattr(self, item[0], item[1])
            
