import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
import matplotlib.pyplot as plt

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Connetti a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]


def extract_data(file_path):
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None
    try:
        logging.info(f"Extracting data from {file_path}")
        df = pd.read_csv(file_path, skiprows=4)
        return df
    except Exception as e:
        logging.error(f"Error extracting data from {file_path}: {e}")
        return None


def transform_data(df, indicator_name):
    if df is None:
        return None

    logging.info(f"Transforming data with {len(df)} records.")
    try:
        df.drop_duplicates(inplace=True)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        transformed_data = []
        for _, row in df.iterrows():
            country_name = row['Country Name']
            country_code = row['Country Code']
            for year in range(1960, 2024):
                year_str = str(year)
                if year_str in row:
                    value = row[year_str]
                    if pd.notna(value):
                        transformed_data.append({
                            "Country Name": country_name,
                            "Country Code": country_code,
                            "Indicator Name": indicator_name,
                            "Year": year,
                            "Value": value
                        })
        return pd.DataFrame(transformed_data)
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return None


def load_data(df, collection_name):
    if df is None or df.empty:
        logging.warning(f"No data to load for {collection_name}")
        return

    try:
        logging.info(f"Loading data into collection {collection_name}")
        data = df.to_dict(orient="records")
        collection = db[collection_name]
        collection.insert_many(data)
        logging.info(f"Inserted {len(data)} records into collection {collection_name}.")
    except Exception as e:
        logging.error(f"Error loading data into {collection_name}: {e}")


def clean_all_collections():
    collections = db.list_collection_names()
    for collection_name in collections:
        db[collection_name].drop()
        logging.info(f"Collection {collection_name} dropped.")


def create_indexes(collection_name, indexes):
    try:
        collection = db[collection_name]
        for index in indexes:
            collection.create_index([index])
            logging.info(f"Index created on {collection_name}: {index}")
    except Exception as e:
        logging.error(f"Error creating index on {collection_name}: {e}")


def create_dim_country_table(df):
    logging.info("Creating dimension table for countries.")
    try:
        countries = df[['Country Name', 'Country Code']].drop_duplicates().reset_index(drop=True)
        countries['country_key'] = countries.index + 1
        db.dim_country.insert_many(countries.to_dict('records'))
    except Exception as e:
        logging.error(f"Error creating dimension table for countries: {e}")


def create_dim_year_table():
    logging.info("Creating dimension table for years.")
    try:
        years = pd.DataFrame({'Year': list(range(1960, 2024))})
        years['year_key'] = years.index + 1
        db.dim_year.insert_many(years.to_dict('records'))
    except Exception as e:
        logging.error(f"Error creating dimension table for years: {e}")


def create_fact_table(df):
    logging.info("Creating fact table.")
    try:
        countries = pd.DataFrame(list(db.dim_country.find({}, {'_id': 0})))
        years = pd.DataFrame(list(db.dim_year.find({}, {'_id': 0})))

        fact_data = df.merge(countries, on=['Country Name', 'Country Code'])
        fact_data = fact_data.merge(years, left_on='Year', right_on='Year')
        fact_data = fact_data[['country_key', 'year_key', 'Indicator Name', 'Value']]
        db.fact_table.insert_many(fact_data.to_dict('records'))
    except Exception as e:
        logging.error(f"Error creating fact table: {e}")


def main():
    try:
        clean_all_collections()

        file_path = "../data/API_EN.ATM.CO2E.KT_DS2_en_csv_v2_213077.csv"
        collection_name = "co2_emissions"

        df = extract_data(file_path)
        df_transformed = transform_data(df, "CO2 Emissions")
        load_data(df_transformed, collection_name)

        logging.info("ETL process and index creation completed successfully.")

        # Creazione delle tabelle delle dimensioni e della tabella dei fatti
        combined_df = transform_data(extract_data(file_path), "CO2 Emissions")
        create_dim_country_table(combined_df)
        create_dim_year_table()
        create_fact_table(combined_df)

        logging.info("ETL process, cube creation, and index creation completed successfully.")
    except Exception as e:
        logging.error(f"ETL process failed: {e}")


if __name__ == "__main__":
    main()
