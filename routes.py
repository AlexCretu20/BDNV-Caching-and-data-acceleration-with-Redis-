from flask import request, jsonify, Blueprint
from services.caching import get_restaurants_cash_aside, CafeReadThrough, FavoritesWriteThrough

api = Blueprint('api', __name__)

@api.route('/restaurants', methods = ['GET'])
def get_restaurants_by_city():
    city = request.args.get('city')

    if not city:
        return jsonify({"error": "The parameter is missing.",
                       "Hint": "Correct form /restaurants?city=city_name"
            }), 400

    data, source = get_restaurants_cash_aside(city)
    
    return jsonify({
        "city": city,
        "type": "reaturant",
        "cache strategy": "Cache aside",
        "source": source,
        "count": len(data),
        "results": data,
    })


@api.route('/cafes', methods = ['GET'])
def get_cafes_by_city():
    city = request.args.get('city')

    if not city:
        return jsonify({"error": "The parameter is missing.",
                       "Hint": "Correct form /cafes?city=city_name"
            }), 400
    

    data, source = CafeReadThrough.get(city)
    
    return jsonify({
        "city": city,
        "type": "cafe",
        "cache strategy": "Read Through",
        "source": source,
        "count": len(data),
        "results": data,
    })

@api.route('/addFavorites', methods = ['POST'])
def add_favorite():
    
    data =request.json
    user_id = data.get('user_id')
    place = data.get('place')

    FavoritesWriteThrough.add_favorites(user_id, place)

    return jsonify({
        "status": "succes",
        "message": "The place was added succesfully"
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
