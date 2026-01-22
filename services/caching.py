from services.extern_api import get_info
from services.geoservice import Map
from config import redis_favorites, redis_cafes, redis_restaurants, favorites_collection, CACHE_TTL
import json
import time
from services.prometheus_exporter import exporter


def get_restaurants_cash_aside(city,user_x=None, user_y=None):
    cache_key = f"Restaurants:{city.lower()}"
    map_key = f"Map_restaurants:{city.lower()}"

    print(f"Fisrt check in redis to see if I have the restaurant from {city}")

    cached_data = redis_restaurants.get(cache_key)
    t_cache_start = time.time()
    cache_latency = time.time() - t_cache_start
    restaurants = []
    restaurants_map = None
    source = "Unknown"

    if cached_data:
        print("Cache hit")
        restaurants = json.loads(cached_data)
        source = "redis_cache_aside"
        exporter.record_hit(pattern="cache_aside", scenario="restaurants", latency_seconds=cache_latency)
    
        if user_x and user_y:
            if not redis_restaurants.exists(map_key):
                Map.create_map(redis_restaurants,map_key,restaurants)
                redis_restaurants.expire(map_key, CACHE_TTL)
    else :
        print("Use external api ")
        restaurants = get_info(city,"restaurant")
        t_db_start = time.time()
        db_latency = time.time() - t_db_start
        exporter.record_miss("cache_aside", "restaurants", cache_latency_seconds=cache_latency, db_latency_seconds=db_latency)

        ## acum actualizam cached

        if restaurants:
            print("We save in cached for half of hour")
            restaurant_json = json.dumps(restaurants)

            redis_restaurants.setex(cache_key,CACHE_TTL, restaurant_json)
            Map.create_map(redis_restaurants, map_key, restaurants)
            redis_restaurants.expire(map_key, CACHE_TTL)
            source = "extern"

        try:
            used = redis_restaurants.info().get("used_memory", 0)
            exporter.update_memory_usage("restaurants", int(used))
        except Exception:
            pass

    if user_x and user_y:
        try:
            restaurants_map = Map.search_close(redis_restaurants,map_key,user_x, user_y)
        except Exception :
            print("Could not find the near places")
            restaurants_map = None

    if restaurants_map:
        return restaurants_map, f"{source} and the date was sorted"
    return restaurants, source


class CafeReadThrough:
    def get(city, user_x = None, user_y = None):
        cache_key = f"cafe:{city.lower()}"
        map_key = f"Map_cafes:{city.lower()}"
        print(f"Looking after cafes in  {city}")

        cached_data = redis_cafes.get(cache_key)
        t_cache_start = time.time()
        cache_latency = time.time() - t_cache_start

        cafes = []
        cafes_map = None
        source = "Unknown"


        if cached_data:
            print("Cache hit ")
            cafes = json.loads(cached_data)
            source = "redis_read_through"
            exporter.record_hit(pattern="read_through", scenario="cafes", latency_seconds=cache_latency)
            if user_x and user_y:
                if not redis_cafes.exists(map_key):
                    Map.create_map(redis_cafes,map_key,cafes)
                    redis_cafes.expire(map_key, CACHE_TTL)
        
        else:
            print("Cached miss")

            cafes = get_info(city, "cafe")
            t_db_start = time.time()
            db_latency = time.time() - t_db_start

            exporter.record_miss("read_through", "cafes", cache_latency_seconds=cache_latency, db_latency_seconds=db_latency)

            if cafes:
                print("Add the cafes in cache")
                redis_cafes.setex(cache_key, 1800, json.dumps(cafes))
                Map.create_map(redis_cafes, map_key, cafes)
                redis_cafes.expire(map_key, CACHE_TTL)
        
                source = "extern api"

            try:
                used = redis_cafes.info().get("used_memory", 0)
                exporter.update_memory_usage("cafes", int(used))
            except Exception:
                pass

        if user_x and user_y:
            try:
                cafes_map = Map.search_close(redis_cafes, map_key, user_x, user_y)
            except Exception :
                print("Could not find the near places")
                cafes_map = None

        if cafes_map:
            return cafes_map, f"{source} and the date was sorted"

        return cafes, source
    
class FavoritesWriteThrough:
    def add_favorites(user_id, place_info):
        cache_key = f"favorites:{user_id}"
        place_json = json.dumps(place_info)

        start_time = time.time()

        # write to cache       
        redis_favorites.sadd(cache_key, place_json)
        redis_favorites.expire(cache_key, 1800)

        # write to bd 
        favorites_collection.update_one(
            {"user_id": user_id},
            {"$addToSet": {"places": place_info}},
            upsert = True
        )

        duration = time.time() - start_time
        print(f"Write through for user {user_id} took {duration:.4f}s")
        return True
    
    def get_favorites(user_id):
        cache_key = f"favorites:{user_id}"

        # check firts redis
        start_cache = time.time()
        cached_favories = redis_favorites.smembers(cache_key)

        if cached_favories:
            print ("Favorites Cache HIT")
            return [json.loads(fav) for fav in cached_favories], "redis_cache"
        
        print("Favorites Cache MISS")
        user_doc = favorites_collection.find_one({"user_id": user_id})

        fav_list = []
        if user_doc and "places" in user_doc:
            fav_list = user_doc["places"]

            for place in fav_list:
                redis_favorites.sadd(cache_key, json.dumps(place))

            redis_favorites.expire(cache_key, 1800)

        return fav_list, "mongodb"
