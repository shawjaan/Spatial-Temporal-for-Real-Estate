import pandas as pd
import time 
import random
from tqdm import tqdm

start_time = time.time()
tqdm.pandas()

# geocoded addresses come from the OpenStreetMap service
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


geolocator = Nominatim(user_agent="shawjustin416@gmail.com", timeout=100)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


# functions
def find_location(row):
    place = row['Address']
    delay = 1.5  # initial delay

    while True:  # repeat until successful

        try:
            location = geolocator.geocode(place)

            if location is not None:
                return location.latitude, location.longitude
            else:
                place_overall = place[-8:]
                location_overall = geolocator.geocode(place_overall)

                if location_overall is not None:
                    return location_overall.latitude, location_overall.longitude
                else:
                    return None, None  # Return None when no geocode data is found
            
        except (GeocoderTimedOut, GeocoderServiceError):
            delay *= 2  # double the delay
            delay = min(delay, 60)  # but don't wait for more than 60 seconds
            print(f"Geocoding failed, waiting for {delay} seconds.")
            time.sleep(delay + (random.random() - 0.5)*0.1*delay)  # wait and add a small random offset


# main
df = pd.read_csv("pp-2010-subset")

df[['Lat','Lng']] = df.progress_apply(find_location, axis="columns", result_type="expand")

print(df)
print("--- %s seconds ---" % (time.time() - start_time))

df.to_csv('pp-2010-subset-geocoded')
