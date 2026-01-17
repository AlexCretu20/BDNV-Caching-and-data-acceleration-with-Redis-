from services.extern_api import get_info
from config import redis
import json
import time
from services.prometheus_exporter import exporter


def get_restaurants_cash_aside(city):
    cache_key = f"Restaurants:{city.lower()}"

    print(f"Fisrt check in redis to see if I have the restaurant from {city}")

    cached_data = redis.get(cache_key)
    t_cache_start = time.time()
    cache_latency = time.time() - t_cache_start

    if cached_data:
        print("Cache hit")
        exporter.record_hit(pattern="cache_aside", scenario="restaurants", latency_seconds=cache_latency)
        return json.loads(cached_data), "redis_cache_aside"
    
    print("Use external api ")
    restaurants = get_info(city,"restaurant")
    t_db_start = time.time()
    db_latency = time.time() - t_db_start
    exporter.record_miss("cache_aside", "restaurants", cache_latency_seconds=cache_latency, db_latency_seconds=db_latency)

    ## acum actualizam cached

    if restaurants:
        print("We save in cached for half of hour")
        restaurant_json = json.dumps(restaurants)

        redis.setex(cache_key,1800, restaurant_json)
    try:
        used = redis.info().get("used_memory", 0)
        exporter.update_memory_usage("restaurants", int(used))
    except Exception:
        pass

    return restaurants, "extern"

class CafeReadThrough:
    def get(city):
        cache_key = f"cafe:{city.lower()}"
        print(f"Looking after cafes in  {city}")

        cached_data = redis.get(cache_key)
        t_cache_start = time.time()
        cache_latency = time.time() - t_cache_start

        if cached_data:
            print("Cache hit ")
            exporter.record_hit(pattern="read_through", scenario="cafes", latency_seconds=cache_latency)
            return json.loads(cached_data), "redis_read_through"

        print("Cached miss")

        cafes = get_info(city, "cafe")
        t_db_start = time.time()
        db_latency = time.time() - t_db_start

        exporter.record_miss("read_through", "cafes", cache_latency_seconds=cache_latency, db_latency_seconds=db_latency)

        if cafes:
            print("Add the cafes in cache")
            redis.setex(cache_key, 1800, json.dumps(cafes))

        try:
            used = redis.info().get("used_memory", 0)
            exporter.update_memory_usage("cafes", int(used))
        except Exception:
            pass

        return cafes, "extern api"