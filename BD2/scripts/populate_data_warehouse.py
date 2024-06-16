import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Connetti a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["data_warehouse"]


def extract_data(file_path, delimiter=r'\s+', header=0):
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None
    try:
        logging.info(f"Extracting data from {file_path}")
        df = pd.read_csv(file_path, delimiter=delimiter, comment='#', header=header)
        logging.info(f"Extracted columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Error extracting data from {file_path}: {e}")
        return None


def transform_temperature_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        df = df.rename(columns={"Year": "year", "No_Smoothing": "temperature"})
        df = df[df['year'].apply(lambda x: x.isnumeric())]  # Filter out non-numeric years
        df['year'] = df['year'].astype(int)
        logging.info(f"Transformed columns for temperature data: {df.columns.tolist()}")
        df = df[["year", "temperature"]]
        return df
    except Exception as e:
        logging.error(f"Error transforming temperature data: {e}")
        return None


def transform_ch4_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        df = df.rename(columns={df.columns[0]: "year", df.columns[1]: "month", df.columns[3]: "ch4_concentration"})
        logging.info(f"Transformed columns for CH4 data: {df.columns.tolist()}")
        df = df[["year", "month", "ch4_concentration"]]
        return df
    except Exception as e:
        logging.error(f"Error transforming CH4 data: {e}")
        return None


def transform_co2_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        logging.info(f"Available columns for CO2 data: {df.columns.tolist()}")
        df = df.rename(columns={df.columns[2]: "decimal_date", df.columns[3]: "co2_concentration"})
        logging.info(f"Transformed columns for CO2 data: {df.columns.tolist()}")
        df = df[["decimal_date", "co2_concentration"]]
        return df
    except Exception as e:
        logging.error(f"Error transforming CO2 data: {e}")
        return None


def transform_gmsl_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        df = df.rename(columns={df.columns[2]: "decimal_year", df.columns[5]: "gmsl"})
        logging.info(f"Transformed columns for GMSL data: {df.columns.tolist()}")
        df = df[["decimal_year", "gmsl"]]
        return df
    except Exception as e:
        logging.error(f"Error transforming GMSL data: {e}")
        return None


def transform_protected_areas_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            "NAME": "name",
            "DESIG_ENG": "designation",
            "IUCN_CAT": "iucn_category",
            "ISO3": "iso3",
            # Aggiungi altri rinomini se necessario
        })
        df = df[["name", "designation", "iucn_category", "iso3"]]
        logging.info(f"Transformed columns for protected areas data: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Error transforming protected areas data: {e}")
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


def main():
    try:
        # Process temperature data
        temp_df = extract_data("../data/temperature.txt", delimiter=r'\s+', header=2)
        temp_transformed = transform_temperature_data(temp_df)
        load_data(temp_transformed, "temperature_data")

        # Process CH4 data
        ch4_df = extract_data("../data/ch4_mm_gl.txt", delimiter=r'\s+', header=1)
        ch4_transformed = transform_ch4_data(ch4_df)
        load_data(ch4_transformed, "ch4_data")

        # Process CO2 data
        co2_df = extract_data("../data/co2_mm_mlo.txt", delimiter=r'\s+', header=58)  # Adjust header accordingly
        co2_transformed = transform_co2_data(co2_df)
        load_data(co2_transformed, "co2_data")

        # Process GMSL data with manually specified column names
        # Process GMSL data
        gmsl_df = extract_data("../data/GMSL_TPJAOS_5.1.txt", delimiter=r'\s+', header=1)  # Adjust header accordingly
        gmsl_transformed = transform_gmsl_data(gmsl_df)
        load_data(gmsl_transformed, "gmsl_data")

        # Process protected areas data
        protected_areas_df = extract_data("../data/WDPA_Aug2023_Public_csv.csv", delimiter=',', header=0)
        protected_areas_transformed = transform_protected_areas_data(protected_areas_df)
        load_data(protected_areas_transformed, "protected_areas_1")

        logging.info("ETL process completed successfully.")
    except Exception as e:
        logging.error(f"ETL process failed: {e}")


if __name__ == "__main__":
    main()
