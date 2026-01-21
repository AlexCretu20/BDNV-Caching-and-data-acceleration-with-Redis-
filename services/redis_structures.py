from datetime import datetime, timezone
from config import redis_favorites

KEY_RANKING_CITIES = "ranking:cities"          # ZSET
KEY_FAVORITE_CITIES = "favorites:cities"       # SET
KEY_RECENT_SEARCHES = "recent:searches"        # LIST
KEY_FAVORITES_STREAM = "stream:favorites"      # STREAM

def track_search(city: str, place_type: str):
    """
    Sorted Set + List:
    """
    if not city:
        return
    redis_favorites.zincrby(KEY_RANKING_CITIES, 1, city)
    redis_favorites.lpush(KEY_RECENT_SEARCHES, f"{place_type}:{city}")
    redis_favorites.ltrim(KEY_RECENT_SEARCHES, 0, 49)  # pastram ultimele 50

def top_cities(n: int = 10):
    """
    Returneaza top n orase.
    """
    n = max(1, min(int(n), 50))
    data = redis_favorites.zrevrange(KEY_RANKING_CITIES, 0, n - 1, withscores=True)
    return [{"city": city, "score": int(score)} for city, score in data]

def recent_searches(n: int = 10):
    """
    Returneaza ultimele n cautari.
    """
    n = max(1, min(int(n), 50))
    return redis_favorites.lrange(KEY_RECENT_SEARCHES, 0, n - 1)

def add_favorite_city(city: str):
    """
    SET + STREAM:
    """
    if not city:
        return False
    added = redis_favorites.sadd(KEY_FAVORITE_CITIES, city)
    _log_favorite_event("ADD", city)
    return bool(added)

def remove_favorite_city(city: str):
    """
    SET + STREAM:
    """
    if not city:
        return False
    removed = redis_favorites.srem(KEY_FAVORITE_CITIES, city)
    _log_favorite_event("REMOVE", city)
    return bool(removed)

def list_favorite_cities():
    """
    Orasele favorite
    """
    return sorted(list(redis_favorites.smembers(KEY_FAVORITE_CITIES)))

def favorites_stream(last_n: int = 20):
    """
    Returnam ultimele n evenimente.
    """
    last_n = max(1, min(int(last_n), 100))
    # xrevrange returneaza desc; apoi inversam ca sa fie cronologic
    items = redis_favorites.xrevrange(KEY_FAVORITES_STREAM, max="+", min="-", count=last_n)
    items = list(reversed(items))
    out = []
    for msg_id, fields in items:
        out.append({"id": msg_id, **fields})
    return out

def _log_favorite_event(action: str, city: str):
    ts = datetime.now(timezone.utc).isoformat()
    redis_favorites.xadd(KEY_FAVORITES_STREAM, {"action": action, "city": city, "ts": ts})
