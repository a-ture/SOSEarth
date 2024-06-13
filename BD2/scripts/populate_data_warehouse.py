from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Connetti a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]


# Funzione per aggiornare i metadati nella fact_table
def update_metadata():
    logging.info("Updating metadata in fact_table.")

    # Crea dizionario per country_metadata
    country_metadata = {}
    for doc in db.country_metadata.find({}, {'_id': 0, 'Country Name': 1, 'Region': 1, 'IncomeGroup': 1,
                                             'SpecialNotes': 1}):
        if 'Country Name' in doc:
            country_metadata[doc['Country Name']] = doc

    # Crea dizionario per indicator_metadata
    indicator_metadata = {}
    for doc in db.indicator_metadata.find({},
                                          {'_id': 0, 'INDICATOR_NAME': 1, 'SOURCE_NOTE': 1, 'SOURCE_ORGANIZATION': 1}):
        if 'INDICATOR_NAME' in doc:
            indicator_metadata[doc['INDICATOR_NAME']] = doc

    # Aggiorna la fact_table con i metadati
    for fact in db.fact_table.find():
        country_name = fact.get('Country Name')
        indicator_name = fact.get('Indicator Name')

        if country_name in country_metadata and indicator_name in indicator_metadata:
            db.fact_table.update_one(
                {'_id': fact['_id']},
                {'$set': {
                    'Metadata.Country': country_metadata[country_name],
                    'Metadata.Indicator': indicator_metadata[indicator_name]
                }}
            )
            logging.info(f"Updated metadata for {country_name} - {indicator_name}")
        else:
            logging.warning(f"Metadata missing for {country_name} - {indicator_name}")


if __name__ == "__main__":
    update_metadata()
