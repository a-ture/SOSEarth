from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]


def query_collection(collection_name, limit=5):
    collection = db[collection_name]
    documents = collection.find().limit(limit)
    for doc in documents:
        print(doc)


def main():
    print("Sample records from temperature_data collection:")
    query_collection("temperature_data")

    print("\nSample records from ch4_data collection:")
    query_collection("ch4_data")


if __name__ == "__main__":
    main()
