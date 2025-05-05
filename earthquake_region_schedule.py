import requests
import xml.etree.ElementTree as ET
from pymongo import MongoClient
from datetime import datetime

# URL API
url = "https://data.tmd.go.th/api/DailySeismicEvent/v1/?uid=api&ukey=api12345"

# MongoDB connection
mongo_uri = "mongodb+srv://admin:admin@cluster0.gdnaggb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["earthquake_db"]
collection = db["earthquake_region"]

# หาวันเวลาล่าสุดใน MongoDB
latest_doc = collection.find_one({}, sort=[("DateTimeUTC", -1)])
latest_datetime_str = latest_doc["DateTimeUTC"] if latest_doc else "1900-01-01T00:00:00"
latest_datetime = datetime.strptime(latest_datetime_str, "%Y-%m-%d %H:%M:%S.%f")
print(f"Latest datetime from database: {latest_datetime}")

# GET ข้อมูลจาก API
response = requests.get(url)
root = ET.fromstring(response.text)

# หาข้อมูลทั้งหมดจาก XML
earthquakes = root.findall(".//DailyEarthquakes")

# ถ้าไม่มีข้อมูล
if not earthquakes:
    print("ไม่มีข้อมูลจาก API")
else:
    insert_count = 0
    for daily_earthquake in earthquakes:
        date_str = daily_earthquake.findtext("DateTimeUTC")
        if not date_str:
            continue

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            print(f"รูปแบบวันที่ไม่ถูกต้อง: {date_str}")
            continue

        if date_obj > latest_datetime:
            doc = {
                "OriginThai": daily_earthquake.findtext("OriginThai"),
                "DateTimeUTC": date_str,
                "DateTimeThai": daily_earthquake.findtext("DateTimeThai"),
                "Magnitude": daily_earthquake.findtext("Magnitude"),
                "Latitude": daily_earthquake.findtext("Latitude"),
                "Longitude": daily_earthquake.findtext("Longitude"),
                "TitleThai": daily_earthquake.findtext("TitleThai"),
                "Depth": daily_earthquake.findtext("Depth")
            }
            collection.insert_one(doc)
            print("Inserted:", doc)
            print("-" * 20)
            insert_count += 1

    if insert_count == 0:
        print("ไม่มีข้อมูลใหม่ที่ต้อง insert")
    else:
        print(f"รวมจำนวนข้อมูลที่ insert: {insert_count} รายการ")

# ปิดการเชื่อมต่อ
client.close()