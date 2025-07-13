from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag_service import get_vibe_summary
import os
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI must be set in the .env file")

client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database("vibe_navigator_db")
reviews_collection = db.get_collection("reviews")

app = FastAPI()

# --- THIS IS THE FINAL, CORRECTED LIST WITH YOUR LIVE URL ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://vibe-navigator-hackathon.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "Vibe Navigator"}

@app.get("/api/vibe/{location_name}")
def get_vibe(location_name: str):
    return get_vibe_summary(location_name)

@app.get("/api/locations")
def get_all_locations():
    pipeline = [
        {"$group": {"_id": "$location_name", "latitude": {"$first": "$latitude"}, "longitude": {"$first": "$longitude"}}},
        {"$project": {"_id": 0, "name": "$_id", "position": ["$latitude", "$longitude"]}},
        {"$match": {"position": {"$ne": [None, None]}}}
    ]
    locations = list(reviews_collection.aggregate(pipeline))
    return locations