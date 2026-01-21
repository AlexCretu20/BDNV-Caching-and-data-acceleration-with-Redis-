from config import redis_cafes, redis_restaurants, CACHE_TTL, MAX_MEM
from services.extern_api import get_info
import json
import time

def top_restaurants(city,limit):

    cache_key = f"Top_Restaurants_from_{city.lower()}:{limit}"

    cached_data = redis_restaurants.get(cache_key)
    
    if cached_data:
        print("Cache hit")
        return json.loads(cached_data), "redis"
    
    print("Use external api")

    restaurants = get_info(city,"restaurant")
    sorted_restaurants = sorted(restaurants, key = lambda x: x.get('rating', 0), reverse=True)

    final_restaurants = sorted_restaurants[:int(limit)]

    if final_restaurants:
        redis_restaurants.setex(cache_key, CACHE_TTL*2, json.dumps(final_restaurants))

    return final_restaurants, "extern api"


def top_cafes(city,limit):

    cache_key = f"Top_Cafes_from_{city.lower()}:{limit}"

    cached_data = redis_cafes.get(cache_key)
    
    if cached_data:
        print("Cache hit")
        return json.loads(cached_data), "redis"
    
    print("Use external api")

    cafes = get_info(city,"cafe")
    sorted_cafes = sorted(cafes, key = lambda x: x.get('rating', 0), reverse=True)

    final_cafes = sorted_cafes[:int(limit)]

    if final_cafes:
        redis_cafes.setex(cache_key, CACHE_TTL*2, json.dumps(final_cafes))

    return final_cafes, "extern api"


