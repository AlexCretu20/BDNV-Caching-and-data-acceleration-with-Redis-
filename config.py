import redis
from pymongo import MongoClient

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

MONGO_URI = ("mongodb://localhost:27017/")
DB = "project"


redis = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, db = 0, decode_responses = True)

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[DB]
mongo_collection = mongo_db["restaurants"]
