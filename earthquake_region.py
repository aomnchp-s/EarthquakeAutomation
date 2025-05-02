import requests
import xml.etree.ElementTree as ET
from pymongo import MongoClient

# URL API
url = "https://data.tmd.go.th/api/DailySeismicEvent/v1/?uid=api&ukey=api12345"

# MongoDB Atlas connection
#mongodb+srv://<db_username>:<db_password>@cluster0.gdnaggb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
mongo_uri = "mongodb+srv://admin:admin@cluster0.gdnaggb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)

# Database and Collection
db = client["earthquake_db"]
collection = db["earthquake_region"]

# GET request
response = requests.get(url)
root = ET.fromstring(response.text)

# Loop through each earthquake entry
for daily_earthquake in root.findall(".//DailyEarthquakes"):
    doc = {
        "OriginThai": daily_earthquake.findtext("OriginThai"),
        "DateTimeUTC": daily_earthquake.findtext("DateTimeUTC"),
        "DateTimeThai": daily_earthquake.findtext("DateTimeThai"),
        "Magnitude": daily_earthquake.findtext("Magnitude"),
        "Latitude": daily_earthquake.findtext("Latitude"),
        "Longitude": daily_earthquake.findtext("Longitude"),
        "TitleThai": daily_earthquake.findtext("TitleThai"),
        "Depth": daily_earthquake.findtext("Depth")
    }

    # Insert to MongoDB
    collection.insert_one(doc)

    # Optional: print inserted document
    print(doc)
    print("-" * 20)

# Close MongoDB connection
client.close()