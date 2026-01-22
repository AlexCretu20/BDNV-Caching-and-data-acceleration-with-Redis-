import redis
from pymongo import MongoClient

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

MONGO_URI = ("mongodb://localhost:27017/")
DB = "project"

CACHE_TTL = 1800



redis_restaurants = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, db = 0, decode_responses = True)
redis_cafes = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, db = 1, decode_responses = True)
redis_favorites = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, db = 2, decode_responses = True)

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[DB]
restaurant_collection = mongo_db["restaurants"]
cafes_collection = mongo_db["cafes"]
favorites_collection = mongo_db["favorites"]