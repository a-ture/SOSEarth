import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Configurazione di MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['data_warehouse']

# Percorso della directory dei file CSV
csv_directory = os.path.join(os.path.dirname(__file__), '../data')


# Funzione per pulire e normalizzare i dati
def clean_and_normalize(df):
    # Rimozione di colonne completamente vuote
    df.dropna(how='all', axis=1, inplace=True)

    # Rimozione di righe completamente vuote
    df.dropna(how='all', inplace=True)

    # Normalizza i nomi delle colonne
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

    # Rimozione delle colonne con nomi non significativi (es. unnamed:_2)
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]

    return df


# Funzione per importare i CSV in MongoDB
def import_csv_to_mongodb(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                collection_name = file.replace('.csv', '')
                collection = db[collection_name]

                file_path = os.path.join(root, file)

                try:
                    print(f'Importing {file_path} into collection {collection_name}')

                    # Tentativo di leggere il file CSV
                    df = pd.read_csv(file_path, on_bad_lines='skip', skiprows=4)

                    # Gestione di possibili righe di intestazione multiple
                    if not df.columns.is_unique:
                        df.columns = df.iloc[0]
                        df = df[1:]

                    # Pulizia e normalizzazione dei dati
                    df = clean_and_normalize(df)

                    # Stampa le prime righe del DataFrame per il debug
                    print(f'DataFrame head for {file}:\n', df.head())

                    # Stampa il numero di righe e colonne del DataFrame
                    print(f'{file} - Rows: {df.shape[0]}, Columns: {df.shape[1]}')

                    # Conversione del DataFrame in un formato che MongoDB può accettare
                    data = df.to_dict(orient='records')

                    # Inserimento dei dati nella collezione
                    if data:
                        collection.insert_many(data)
                        print(f'{file} imported successfully with {len(data)} records.')
                    else:
                        print(f'{file} is empty or has invalid data and was skipped.')
                except Exception as e:
                    print(f'Error importing {file}: {e}')


# Importa tutti i file CSV nella directory
import_csv_to_mongodb(csv_directory)

print('All files have been imported.')
