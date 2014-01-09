import redis

from src.todoMelvin import settings

#Connect to Redis server with src.Settings
def connect():
    return redis.StrictRedis(
        host = settings.redisHost, 
        port = int(settings.redisPort), 
        db = int(settings.redisDB), 
        password = settings.redisPassword)    
