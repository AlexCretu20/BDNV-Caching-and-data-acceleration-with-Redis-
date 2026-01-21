from config import OVERPASS_URL
import time
import requests

def get_info(city, amenity_type):

    query = f"""
    [out:json];
    area["name" = "{city}"] ->.searchArea;
    (
        node["amenity"="{amenity_type}"](area.searchArea);
        way["amenity"="{amenity_type}"](area.searchArea);
        relation["amenity"="{amenity_type}"](area.searchArea);
    );
    out tags center;
    """
    ##out tags center 30;

    start_time = time.time()
    response = requests.post(OVERPASS_URL, data=query)
    response.raise_for_status()


    data = response.json()
    duration = time.time() -start_time
    locals = []

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", {})

        # legaseste daca sunt un nod 
        coord_x = element.get("lat")
        coord_y = element.get("lon")

        if coord_x is None and coord_y is None:
            center = element.get("center", {})
            coord_x = center.get("lat")
            coord_y = center.get("lon") 

        if coord_x and coord_y and name:
            locals.append({
                "name": name,
                "cuisine": tags.get("cuisine", "Unknown"),
                "type": amenity_type,
                "city": city,
                "coordinateX": coord_x,
                "coordinateY": coord_y
            })

    return locals
