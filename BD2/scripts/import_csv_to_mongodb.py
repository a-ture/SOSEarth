import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Connetti a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]


def query_protected_areas_by_country(country_name):
    try:
        collection = db["protected_areas"]
        query = {"country_name": country_name}
        total_records = collection.count_documents(query)
        sample_records = collection.find(query).limit(10)  # You can adjust the limit as needed

        logging.info(f"Total protected areas in {country_name}: {total_records}")
        logging.info(f"Sample protected areas in {country_name}:")
        for record in sample_records:
            logging.info(record)
    except Exception as e:
        logging.error(f"Error querying protected areas in {country_name}: {e}")


def main():
    # Esegui la query per le aree protette del Canada
    query_protected_areas_by_country("RUS")


if __name__ == "__main__":
    main()
