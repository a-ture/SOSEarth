from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Connetti a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]

# Recupera i dati dalla collezione indicator_solutions
solutions = list(db.indicator_solutions.find({}, {'_id': 0}))

# Stampa i dati
for solution in solutions:
    print(solution)
