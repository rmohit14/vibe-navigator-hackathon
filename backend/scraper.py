# backend/scraper.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pymongo # To connect to MongoDB

# --- Database Connection ---
# IMPORTANT: Replace with your actual MongoDB Atlas connection string
# Example: MONGO_URI = "mongodb+srv://testuser:testpassword@cluster0.abcde.mongodb.net/vibe_navigator_db?retryWrites=true&w=majority"
MONGO_URI = "mongodb+srv://mohit14:9043722090@cluster0.pkcypur.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("vibe_navigator_db") # Use a new or existing database
reviews_collection = db.get_collection("reviews") # Use a new or existing collection
# --- End Database Connection ---

def scrape_reviews():
    # Use webdriver-manager to handle the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Target URL (using a simple scraping sandbox for this example)
    url = 'https://sandbox.oxylabs.io/products'
    driver.get(url)

    # Give the page time to load
    time.sleep(3)

    # Pass the page source to BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find all product cards (these are our "locations")
    product_cards = soup.find_all('div', {'class': 'product-card'})
    
    scraped_data = [] # Initialize as an empty list
    for card in product_cards:
        # This is a simplified example. Real reviews would be more complex.
        # We'll treat the product description as a "review".
        location_name = card.find('h4').text if card.find('h4') else 'No Name'
        review_text = card.find('p', {'class': 'description'}).text if card.find('p', {'class': 'description'}) else 'No review text.'

        review_document = {
            "location_name": location_name,
            "review": review_text,
            "source": "Oxylabs Sandbox"
        }
        scraped_data.append(review_document)

    # Insert data into MongoDB
    if scraped_data:
        reviews_collection.insert_many(scraped_data)
        print(f"Successfully scraped and inserted {len(scraped_data)} reviews.")
    else:
        print("No data was scraped.")

if __name__ == '__main__':
    scrape_reviews()