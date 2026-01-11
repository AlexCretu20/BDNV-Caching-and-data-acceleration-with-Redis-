from services.extern_api import get_info
from config import redis
import json

def get_restaurants_cash_aside(city):
    cache_key = f"Restaurants:{city.lower()}"

    print(f"Fisrt check in redis to see if I have the restaurant from {city}")

    cached_data = redis.get(cache_key)

    if cached_data:
        print("Cache hit")
        return json.loads(cached_data), "redis_cache_aside"
    
    print("Use external api ")
    restaurants = get_info(city,"restaurant")

    ## acum actualizam cached

    if restaurants:
        print("We save in cached for half of hour")
        restaurant_json = json.dumps(restaurants)

        redis.setex(cache_key,1800, restaurant_json)

    return restaurants, "extern"

class CafeReadThrough:
    def get(city):
        cache_key = f"cafe:{city.lower()}"
        print(f"Looking after cafes in  {city}")

        cached_data = redis.get(cache_key)
        if cached_data:
            print("Cache hit ")
            return json.loads(cached_data), "redis_read_through"
        
        print("Cached miss")

        cafes = get_info(city, "cafe")

        if cafes:
            print("Add the cafes in cache")
            redis.setex(cache_key, 1800, json.dumps(cafes))

        return cafes, "extern api"