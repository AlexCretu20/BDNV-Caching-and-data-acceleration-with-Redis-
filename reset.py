from config import redis_restaurants, redis_cafes

redis_restaurants.config_set('maxmemory','0')
redis_cafes.config_set('maxmemory','0')