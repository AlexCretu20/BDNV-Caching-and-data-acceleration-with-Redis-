from config import OVERPASS_URL
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import requests
import random

def retry():
    sess = requests.Session()

    retry = Retry(
        total = 5,
        backoff_factor= 1,
        status_forcelist=[500, 501, 502, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry)
    sess.mount('http://', adapter)
    sess.mount('http://', adapter)
    return sess

def get_info(city, amenity_type):

    query = f"""
    [out:json][timeout:60];
    area["name" = "{city}"] ->.searchArea;
    (
        node["amenity"="{amenity_type}"](area.searchArea);
        way["amenity"="{amenity_type}"](area.searchArea);
        relation["amenity"="{amenity_type}"](area.searchArea);
    );
    out tags center;
    """
    ##out tags center 30;

    try :
        sess = retry()
        response = sess.post(OVERPASS_URL, data=query, timeout=90)
        response.raise_for_status()
        start_time = time.time()
        data = response.json()
        duration = time.time() -start_time

    except Exception as e:
        print(f"Api request out after 5 tries")
        return []

    places = []

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", {})
        score = random.randint(1, 5)

        # legaseste daca sunt un nod
        coord_x = element.get("lat")
        coord_y = element.get("lon")

        if coord_x is None and coord_y is None:
            center = element.get("center", {})
            coord_x = center.get("lat")
            coord_y = center.get("lon")

        if coord_x and coord_y and name:
            places.append({
                "name": name,
                "cuisine": tags.get("cuisine", "Unknown"),
                "type": amenity_type,
                "city": city,
                "coordinateX": coord_x,
                "coordinateY": coord_y,
                "rating": score
            })

    return places
