from config import redis_cafes, redis_restaurants
import random
import requests
import random
import time 

class Lru:

    def fill_mem(self,requ):

        redis_restaurants.config_set('maxmemory','2mb')
        redis_restaurants.config_set('maxmemory-policy', 'allkeys-lru')

        redis_restaurants.flushdb()

        url = f"http://127.0.0.1:5000/topRestaurants?city=London&limit=10"

        # 2 cereri ca fim siguri ca il salvam in cache
        requests.get(url)
        requests.get(url)
        city = "London"
        key = f"Top_Restaurants_from_{city.lower()}:10"

        if not key:
            print("The key was not saved in cache from api ")
            redis_restaurants.set(key, "Data" * 500)

        test_data = "Test_dataaaa" * 1000


        for i in range(requ):
            test_city  = f"Test_city{i}"
            test_key = f"Top_Restaurants_from_{test_city.lower()}:10"

            try:
                redis_restaurants.setex(test_key, 1800,test_data )
                
                if i % 2 ==0:
                    requests.get(url)
                    print("Special request")
                    requests.get(url)
                    print("Special request")
            except Exception as e:
                if "OOM"  in str(e) or "maxmemory" in str(e):
                    print("The memory is full")
                    pass
                else:
                    print(f"Unexpected error {e}")

            if i % 10 == 0:
                print(f"Proccesed {i} requests") 
            time.sleep(0.1)

        # verificam daca cheia noastra a ramas
        if redis_restaurants.keys(key):
            print(f"The good key {key} is in the cache")
        else :
            print(f"The good key {key} is not  in the cache") 

        for i in range(10):
            test_city  = f"Test_city{i}"
            test_key = f"Top_Restaurants_from_{test_city.lower()}:10"
            if not redis_restaurants.keys(test_key):
                print(f"The bad key {test_key} was deleted")
            else: 
                print(f"The bad key {test_key} was not deleted")


if __name__=="__main__":
    lru = Lru()
    lru.fill_mem(150)
