from flask import Blueprint, request, jsonify

from services.caching import (
    get_restaurants_cash_aside,
    CafeReadThrough,
    FavoritesWriteThrough
)

from services.redis_structures import (
    track_search,          # ZSET + LIST (ranking + recent searches)
    top_cities,            # ZSET
    recent_searches,       # LIST
    add_favorite_city,     # SET + STREAM
    remove_favorite_city,  # SET + STREAM
    list_favorite_cities,  # SET
    favorites_stream       # STREAM
)
from flask import request, jsonify, Blueprint
from services.top_places import top_cafes, top_restaurants
from services.caching import get_restaurants_cash_aside, CafeReadThrough, FavoritesWriteThrough

api = Blueprint('api', __name__)

@api.route('/restaurants', methods=['GET'])
def get_restaurants_by_city():
    city = request.args.get('city')
    user_x = request.args.get('user_x')
    user_y = request.args.get('user_y')

    if not city:
        return jsonify({
            "error": "The parameter is missing.",
            "Hint": "Correct form /restaurants?city=city_name"
        }), 400

    # ZSET + LIST: store ranking + recent searches
    track_search(city, "restaurants")

    if user_x:
        user_x = float(user_x)
    if user_y:
        user_y = float(user_y)

    data, source = get_restaurants_cash_aside(city, user_x, user_y)

    return jsonify({
        "city": city,
        "type": "restaurant",
        "cache strategy": "Cache aside",
        "source": source,
        "count": len(data),
        "results": data
    })

@api.route('/cafes', methods=['GET'])
def get_cafes_by_city():
    city = request.args.get('city')
    user_x = request.args.get('user_x')
    user_y = request.args.get('user_y')

    if not city:
        return jsonify({
            "error": "The parameter is missing.",
            "Hint": "Correct form /cafes?city=city_name"
        }), 400

    track_search(city, "cafes")

    if user_x:
        user_x = float(user_x)
    if user_y:
        user_y = float(user_y)

    data, source = CafeReadThrough.get(city, user_x, user_y)

    return jsonify({
        "city": city,
        "type": "cafe",
        "cache strategy": "Read Through",
        "source": source,
        "count": len(data),
        "results": data
    })

@api.route('/addFavorites', methods=['POST'])
def add_favorite():
    data = request.json or {}
    user_id = data.get('user_id')
    place = data.get('place')

    FavoritesWriteThrough.add_favorites(user_id, place)

    return jsonify({
        "status": "success",
        "message": "The place was added successfully"
    }), 201


@api.route('/getFavorites', methods=['GET'])
def get_favorites():
    user_id = request.args.get('user_id')

    data, source = FavoritesWriteThrough.get_favorites(user_id)

    return jsonify({
        "source": source,
        "count": len(data),
        "favorites": data
    })

@api.route('/deleteFavorite', methods=['DELETE'])
def delete_favorite():
    user_id = request.args.get('user_id')
    place_name = request.args.get('place_name')

    if not user_id or not place_name:
        return jsonify({
            "error": "Missing parameters",
            "Hint": "Use /deleteFavorite?user_id=123&place_name=Le%20Severo"
        }), 400

    FavoritesWriteThrough.delete_favorite(user_id, place_name)

    return jsonify({
        "status": "success",
        "message": "The place was deleted and cache invalidated"
    }), 200

@api.get("/ranking/cities")
def get_top_cities():
    n = request.args.get("top", 10)
    return jsonify({"top": top_cities(n)})

@api.get("/recent/searches")
def get_recent_searches():
    n = request.args.get("last", 10)
    return jsonify({"recent": recent_searches(n)})

@api.route("/favorites/cities", methods=["GET", "POST", "DELETE"])
def favorite_cities():
    if request.method == "GET":
        return jsonify({"favorites": list_favorite_cities()})

    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Missing city param. Use ?city=Paris"}), 400

    if request.method == "POST":
        ok = add_favorite_city(city)
        return jsonify({"added": ok, "city": city})

    ok = remove_favorite_city(city)
    return jsonify({"removed": ok, "city": city})

@api.get("/favorites/events")
def favorite_events():
    n = request.args.get("last", 20)
    return jsonify({"events": favorites_stream(n)})

@api.route('/topRestaurants', methods=['GET'])
def get_top_resturants():
    city = request.args.get('city')
    limit = request.args.get('limit', default = 5, type = int)

    data, source = top_restaurants(city, limit)
    return jsonify({
        "source": source,
        "count": len(data),
        "Tops": data
    })


@api.route('/topCafes', methods=['GET'])
def get_top_cafes():
    city = request.args.get('city')
    limit = request.args.get('limit', default = 5, type = int)

    data, source = top_cafes(city, limit)
    return jsonify({
        "source": source,
        "count": len(data),
        "Tops": data
    })
