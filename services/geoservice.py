class Map:
    def create_map(connection, geo_key, places):
        for place in places:
            name = place.get('name')
            city = place.get('city')
            coord_x = place.get('coordinateX')
            coord_y = place.get('coordinateY')

            place_tag = f"{name}?{city}"
            if coord_x and coord_y:
                connection.geoadd(geo_key,(float(coord_y),float(coord_x), place_tag))

    def search_close(connection,geo_key, client_x, client_y, km = 5):
        try:
            results = connection.geosearch(
                name = geo_key,
                latitude = client_x,
                longitude = client_y,
                radius = km,
                unit = "km",
                withdist = True,
                sort = "ASC",
            )
        except Exception:
            print("Could not find the data ")
            return []
        
        places_list = []
        for place_tag, distance in results:
            place = place_tag.decode('utf-8')
            name, city = place.split('?')

            places_list.append({
                'name':name,
                'city':city,
                'distance': distance
            })

        return places_list

        

