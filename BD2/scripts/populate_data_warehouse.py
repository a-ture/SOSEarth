import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Connetti a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]


# Funzione per caricare un file CSV e inserirlo in una collezione MongoDB
def load_csv_to_mongo(file_path, collection_name):
    # Verifica se il file esiste
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Loading data from {file_path} into collection {collection_name}")
    # Leggi il file CSV
    df = pd.read_csv(file_path, skiprows=4)  # Skips the first 4 rows that usually contain metadata
    print(f"Dataframe loaded with {len(df)} records.")
    # Converti il DataFrame in un dizionario
    data = df.to_dict(orient="records")
    # Ottieni la collezione
    collection = db[collection_name]
    # Inserisci i dati nella collezione
    collection.insert_many(data)
    print(f"Inserted {len(data)} records into collection {collection_name}.")


# Funzione per pulire le collezioni
# Funzione per pulire tutte le collezioni
def clean_all_collections():
    collections = db.list_collection_names()
    for collection_name in collections:
        db[collection_name].drop()
        print(f"Collection {collection_name} dropped.")


# Pulire tutte le collezioni prima di popolare
clean_all_collections()

# Percorsi dei file CSV
file_paths = [
    "../data/API_AG.LND.AGRI.ZS_DS2_en_csv_v2_44906.csv",
    "../data/API_AG.LND.ARBL.ZS_DS2_en_csv_v2_43395.csv",
    "../data/API_AG.LND.IRIG.AG.ZS_DS2_en_csv_v2_48449.csv",
    "../data/API_AG.LND.PRCP.MM_DS2_en_csv_v2_356.csv",
    "../data/API_EG.ELC.HYRO.ZS_DS2_en_csv_v2_51204.csv",
    "../data/API_EG.ELC.NUCL.ZS_DS2_en_csv_v2_76135.csv",
    "../data/API_EG.FEC.RNEW.ZS_DS2_en_csv_v2_45401.csv",
    "../data/API_EG.USE.COMM.CL.ZS_DS2_en_csv_v2_61892.csv",
    "../data/API_EN.ATM.CO2E.KT_DS2_en_csv_v2_213077.csv"
]

# Nomi delle collezioni in MongoDB
collection_names = [
    "agricultural_land",
    "arable_land",
    "irrigated_land",
    "precipitation",
    "hydroelectricity",
    "nuclear_electricity",
    "renewable_energy",
    "coal_use",
    "co2_emissions"
]

# Carica i file CSV nelle rispettive collezioni MongoDB
for file_path, collection_name in zip(file_paths, collection_names):
    load_csv_to_mongo(file_path, collection_name)

print("Dati caricati con successo in MongoDB")
