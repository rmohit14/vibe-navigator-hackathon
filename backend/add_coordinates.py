# backend/add_coordinates.py
import os
from dotenv import load_dotenv
import pymongo
import certifi
# Import the specific error classes we might encounter
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from time import sleep

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database("vibe_navigator_db")
reviews_collection = db.get_collection("reviews")

# --- IMPROVEMENT: Add a timeout of 10 seconds ---
geolocator = Nominatim(user_agent="vibe_navigator_app", timeout=10)

def geocode_locations():
    locations_to_update = reviews_collection.distinct("location_name", {"latitude": {"$exists": False}})
    print(f"Found {len(locations_to_update)} locations to geocode.")

    for name in locations_to_update:
        try:
            print(f"Geocoding: {name}...")
            location = geolocator.geocode(f"{name}, Delhi, India")

            if location:
                reviews_collection.update_many(
                    {"location_name": name},
                    {"$set": {"latitude": location.latitude, "longitude": location.longitude}}
                )
                print(f" -> Success: ({location.latitude}, {location.longitude})")
            else:
                print(f" -> Failed: Location not found in geocoding service.")

            sleep(1) # Respect usage policy

        # --- IMPROVEMENT: More specific error handling ---
        except GeocoderTimedOut:
            print(f" -> Error: Geocoding service timed out for {name}.")
        except GeocoderServiceError as e:
            print(f" -> Error: Geocoding service error for {name}: {e}")
        except Exception as e:
            print(f" -> An unexpected error occurred for {name}: {e}")

if __name__ == '__main__':
    geocode_locations()
    print("Geocoding complete.")
    client.close()