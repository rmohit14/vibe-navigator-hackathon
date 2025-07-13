import os
from dotenv import load_dotenv
import pymongo
import certifi
from rag_service import get_vibe_summary, reviews_collection

# This script will generate and store the AI tags for each location.
def generate_and_store_vibes():
    # Get a new collection to store the generated vibes
    vibe_collection = db.get_collection("location_vibes")
    print("Clearing old vibe data...")
    vibe_collection.delete_many({})

    # Get all unique location names from the reviews
    all_locations = reviews_collection.distinct("location_name")
    print(f"Found {len(all_locations)} unique locations to process.")

    stored_vibes = []
    for name in all_locations:
        print(f"Generating vibe for: {name}...")
        # Use our existing function to get the full vibe summary
        vibe_data = get_vibe_summary(name)

        if vibe_data.get("status") == "found":
            vibe_doc = {
                "location_name": name,
                "tags": vibe_data.get("tags", [])
            }
            stored_vibes.append(vibe_doc)
            print(f" -> Success. Tags: {vibe_data.get('tags')}")
        else:
            print(f" -> Failed or no reviews found for {name}.")

    if stored_vibes:
        print(f"\nInserting {len(stored_vibes)} vibe documents into the database...")
        vibe_collection.insert_many(stored_vibes)
        print("Vibe generation and storage complete.")
    else:
        print("No vibes were generated.")

if __name__ == '__main__':
    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database("vibe_navigator_db")

    generate_and_store_vibes()
    client.close()