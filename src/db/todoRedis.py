import redis

host = 'localhost'
port = 6379
db = 0
password = None

def connect():
    return redis.StrictRedis(host=host, port=port, db=db, password=password)    
