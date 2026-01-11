from flask import request, jsonify, Blueprint
from services.caching import get_restaurants_cash_aside, CafeReadThrough

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
