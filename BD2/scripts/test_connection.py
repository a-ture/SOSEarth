from pymongo import MongoClient

try:
    # Configura il client MongoDB
    client = MongoClient('localhost', 27017)

    # Effettua una chiamata al server per verificare la connessione
    client.admin.command('ping')

    print("MongoDB server is online.")
except ConnectionError:
    print("Failed to connect to MongoDB server.")
