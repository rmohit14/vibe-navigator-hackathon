# backend/seed_db.py
import json
import pymongo
import os
import certifi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI must be set in the .env file")

try:
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database("vibe_navigator_db")
    reviews_collection = db.get_collection("reviews")

    client.admin.command('ping')
    print("MongoDB connection successful.")

    print("Clearing old reviews from the collection...")
    reviews_collection.delete_many({})

    print("Loading new seed data from seed_data.json...")
    with open('seed_data.json', 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    if seed_data:
        print(f"Inserting {len(seed_data)} new reviews...")
        reviews_collection.insert_many(seed_data)
        print("Database has been successfully seeded!")
    else:
        print("No data found in seed_data.json.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.close()
    print("Connection closed.")