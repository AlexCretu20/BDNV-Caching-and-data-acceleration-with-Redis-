from config import redis_favorites

def cache_place_hash(place_type: str, place: dict, ttl_sec: int = 1800):
    """
    Campurile cu HSET loc:<tip>:<oras>:<nume> 
    """
    name = place.get("name")
    city = place.get("city")
    if not name or not city:
        return None

    key = f"place:{place_type}:{city}:{name}"
    # pastram cateva campuri sigure
    payload = {k: str(v) for k, v in place.items() if v is not None}
    redis_favorites.hset(key, mapping=payload)
    redis_favorites.expire(key, ttl_sec)
    return key

def get_place_hash(place_type: str, city: str, name: str):
    key = f"place:{place_type}:{city}:{name}"
    data = redis_favorites.hgetall(key)
    return data if data else None
