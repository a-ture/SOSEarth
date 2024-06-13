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


def transform_data(df, indicator_name, metadata):
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
            country_metadata = metadata.get(country_code, {})
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
                            "Value": value,
                            "Metadata": country_metadata
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
        fact_data = fact_data[['country_key', 'year_key', 'Indicator Name', 'Value', 'Metadata']]
        db.fact_table.insert_many(fact_data.to_dict('records'))
    except Exception as e:
        logging.error(f"Error creating fact table: {e}")


def load_metadata(file_paths, metadata_type='country'):
    metadata = {}
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            if metadata_type == 'country':
                if 'Country Code' in df.columns:
                    logging.info(f"Loading country metadata from {file_path}")
                    for _, row in df.iterrows():
                        metadata[row['Country Code']] = row.to_dict()
                else:
                    logging.error(f"'Country Code' column not found in {file_path}")
                    logging.error(f"Columns present: {df.columns.tolist()}")
            elif metadata_type == 'indicator':
                if 'INDICATOR_CODE' in df.columns:
                    logging.info(f"Loading indicator metadata from {file_path}")
                    for _, row in df.iterrows():
                        metadata[row['INDICATOR_CODE']] = row.to_dict()
                else:
                    logging.error(f"'INDICATOR_CODE' column not found in {file_path}")
                    logging.error(f"Columns present: {df.columns.tolist()}")
        except Exception as e:
            logging.error(f"Error loading metadata from {file_path}: {e}")
    return metadata


def save_metadata_to_db(metadata, collection_name):
    if not metadata:
        logging.warning(f"No metadata to load for {collection_name}")
        return
    try:
        logging.info(f"Loading metadata into collection {collection_name}")
        collection = db[collection_name]
        collection.insert_many([value for key, value in metadata.items()])
        logging.info(f"Inserted {len(metadata)} records into collection {collection_name}.")
    except Exception as e:
        logging.error(f"Error loading metadata into {collection_name}: {e}")


def load_solutions(file_path):
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None
    try:
        logging.info(f"Loading solutions from {file_path}")
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logging.error(f"Error loading solutions from {file_path}: {e}")
        return None


def save_solutions_to_db(df, collection_name):
    if df is None or df.empty:
        logging.warning(f"No data to load for {collection_name}")
        return

    try:
        logging.info(f"Loading solutions into collection {collection_name}")
        data = df.to_dict(orient="records")
        collection = db[collection_name]
        collection.insert_many(data)
        logging.info(f"Inserted {len(data)} records into collection {collection_name}.")
    except Exception as e:
        logging.error(f"Error loading data into {collection_name}: {e}")


def main():
    try:
        clean_all_collections()

        # Carica e salva i metadati dei paesi
        country_metadata_files = [
            "../data/Metadata_Country_API_AG.LND.ARBL.ZS_DS2_en_csv_v2_43395.csv",
            "../data/Metadata_Country_API_AG.LND.FRST.K2_DS2_en_csv_v2_47369.csv",
            "../data/Metadata_Country_API_AG.LND.IRIG.AG.ZS_DS2_en_csv_v2_48449.csv",
            "../data/Metadata_Country_API_AG.LND.PRCP.MM_DS2_en_csv_v2_356.csv",
            "../data/Metadata_Country_API_EG.ELC.HYRO.ZS_DS2_en_csv_v2_51204.csv",
            "../data/Metadata_Country_API_EG.ELC.NUCL.ZS_DS2_en_csv_v2_76135.csv",
            "../data/Metadata_Country_API_EN.BIR.THRD.NO_DS2_en_csv_v2_52306.csv",
            "../data/Metadata_Country_API_EG.USE.COMM.CL.ZS_DS2_en_csv_v2_61892.csv",
            "../data/Metadata_Country_API_EN.CLC.GHGR.MT.CE_DS2_en_csv_v2_44848.csv",
            "../data/Metadata_Country_API_EN.CLC.MDAT.ZS_DS2_en_csv_v2_45415.csv",
            "../data/Metadata_Country_API_EN.ATM.GHGT.KT.CE_DS2_en_csv_v2_45354.csv",
            "../data/Metadata_Country_API_EN.FSH.THRD.NO_DS2_en_csv_v2_46041.csv",
            "../data/Metadata_Country_API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_42623.csv",
            "../data/Metadata_Country_API_EN.HPT.THRD.NO_DS2_en_csv_v2_52000.csv",
            "../data/Metadata_Country_API_EN.URB.MCTY.TL.ZS_DS2_en_csv_v2_450.csv",
            "../data/Metadata_Country_API_EN.ATM.NOXE.KT.CE_DS2_en_csv_v2_49217.csv",
            "../data/Metadata_Country_API_EN.CLC.DRSK.XQ_DS2_en_csv_v2_50987.csv",
            "../data/Metadata_Country_API_ER.H2O.INTR.K3_DS2_en_csv_v2_44524.csv",
            "../data/Metadata_Country_API_ER.PTD.TOTL.ZS_DS2_en_csv_v2_53310.csv",
            "../data/Metadata_Country_API_EG.FEC.RNEW.ZS_DS2_en_csv_v2_45401.csv",
        ]
        country_metadata = load_metadata(country_metadata_files, metadata_type='country')
        save_metadata_to_db(country_metadata, "country_metadata")

        indicator_metadata_files = [
            "../data/Metadata_Indicator_API_AG.LND.AGRI.ZS_DS2_en_csv_v2_44906.csv",
            "../data/Metadata_Indicator_API_AG.LND.ARBL.ZS_DS2_en_csv_v2_43395.csv",
            "../data/Metadata_Indicator_API_AG.LND.FRST.K2_DS2_en_csv_v2_47369.csv",
            "../data/Metadata_Indicator_API_AG.LND.IRIG.AG.ZS_DS2_en_csv_v2_48449.csv",
            "../data/Metadata_Indicator_API_AG.LND.PRCP.MM_DS2_en_csv_v2_356.csv",
            "../data/Metadata_Indicator_API_EG.ELC.HYRO.ZS_DS2_en_csv_v2_51204.csv",
            "../data/Metadata_Indicator_API_EN.ATM.NOXE.KT.CE_DS2_en_csv_v2_49217.csv",
            "../data/Metadata_Indicator_API_EN.POP.EL5M.ZS_DS2_en_csv_v2_44902.csv",
            "../data/Metadata_Indicator_API_EN.ATM.CO2E.PC_DS2_en_csv_v2_47017.csv",
            "../data/Metadata_Indicator_API_EN.HPT.THRD.NO_DS2_en_csv_v2_52000.csv",
            "../data/Metadata_Indicator_API_EN.ATM.CO2E.KT_DS2_en_csv_v2_213077.csv",
            "../data/Metadata_Indicator_API_EN.FSH.THRD.NO_DS2_en_csv_v2_46041.csv",
            "../data/Metadata_Indicator_API_EN.CLC.MDAT.ZS_DS2_en_csv_v2_45415.csv",
            "../data/Metadata_Indicator_API_EN.BIR.THRD.NO_DS2_en_csv_v2_52306.csv",
            "../data/Metadata_Indicator_API_EG.USE.COMM.CL.ZS_DS2_en_csv_v2_61892.csv",
            "../data/Metadata_Indicator_API_EN.CLC.GHGR.MT.CE_DS2_en_csv_v2_44848.csv",
            "../data/Metadata_Indicator_API_EG.FEC.RNEW.ZS_DS2_en_csv_v2_45401.csv",
            "../data/Metadata_Indicator_API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_42623.csv",
            "../data/Metadata_Indicator_API_ER.PTD.TOTL.ZS_DS2_en_csv_v2_53310.csv"
        ]
        indicator_metadata = load_metadata(indicator_metadata_files, metadata_type='indicator')
        save_metadata_to_db(indicator_metadata, "indicator_metadata")

        # Mappa dei file e delle relative collezioni
        file_collection_map = {
            "../data/API_EN.ATM.CO2E.KT_DS2_en_csv_v2_213077.csv": "co2_emissions",
            "../data/API_AG.LND.AGRI.ZS_DS2_en_csv_v2_44906.csv": "agricultural_land",
            "../data/API_AG.LND.ARBL.ZS_DS2_en_csv_v2_43395.csv": "arable_land",
            "../data/API_AG.LND.IRIG.AG.ZS_DS2_en_csv_v2_48449.csv": "irrigated_land",
            "../data/API_AG.LND.PRCP.MM_DS2_en_csv_v2_356.csv": "precipitation",
            "../data/API_EG.ELC.HYRO.ZS_DS2_en_csv_v2_51204.csv": "hydroelectricity",
            "../data/API_EG.ELC.NUCL.ZS_DS2_en_csv_v2_76135.csv": "nuclear_electricity",
            "../data/API_EG.FEC.RNEW.ZS_DS2_en_csv_v2_45401.csv": "renewable_energy",
            "../data/API_EG.USE.COMM.CL.ZS_DS2_en_csv_v2_61892.csv": "coal_use",
            "../data/API_EN.ATM.CO2E.PC_DS2_en_csv_v2_47017.csv": "co2_emissions_per_capita",
            "../data/API_EN.ATM.GHGT.KT.CE_DS2_en_csv_v2_45354.csv": "total_ghg_emissions",
            "../data/API_EN.ATM.METH.KT.CE_DS2_en_csv_v2_49214.csv": "methane_emissions",
            "../data/API_EN.ATM.NOXE.KT.CE_DS2_en_csv_v2_49217.csv": "nitrous_oxide_emissions",
            "../data/API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_42623.csv": "pm25_air_pollution",
            "../data/API_EN.BIR.THRD.NO_DS2_en_csv_v2_52306.csv": "threatened_bird_species",
            "../data/API_EN.CLC.DRSK.XQ_DS2_en_csv_v2_50987.csv": "climate_risk_index",
            "../data/API_EN.CLC.GHGR.MT.CE_DS2_en_csv_v2_44848.csv": "ghg_net_emissions_removals",
            "../data/API_EN.CLC.MDAT.ZS_DS2_en_csv_v2_45415.csv": "co2_emissions_solid_fuel",
            "../data/API_EN.FSH.THRD.NO_DS2_en_csv_v2_46041.csv": "threatened_fish_species",
            "../data/API_SP.POP.GROW_DS2_en_csv_v2_323.csv": "population_growth",
            "../data/API_ER.PTD.TOTL.ZS_DS2_en_csv_v2_53310.csv": "protected_areas",
            "../data/API_ER.H2O.INTR.K3_DS2_en_csv_v2_44524.csv": "internal_renewable_water_resources",
            "../data/API_EN.URB.MCTY.TL.ZS_DS2_en_csv_v2_450.csv": "urban_population"
        }

        indicator_name_map = {
            "co2_emissions": "CO2 emissions (kt)",
            "agricultural_land": "Agricultural land (% of land area)",
            "arable_land": "Arable land (% of land area)",
            "irrigated_land": "Agricultural irrigated land (% of total agricultural land)",
            "precipitation": "Average precipitation in depth (mm per year)",
            "hydroelectricity": "Electricity production from hydroelectric sources (% of total)",
            "nuclear_electricity": "Electricity production from nuclear sources (% of total)",
            "renewable_energy": "Renewable energy consumption (% of total final energy consumption)",
            "coal_use": "Coal use (% of total energy use)",
            "co2_emissions_per_capita": "CO2 emissions (metric tons per capita)",
            "total_ghg_emissions": "Total GHG emissions (kt of CO2 equivalent)",
            "methane_emissions": "Methane emissions (kt of CO2 equivalent)",
            "nitrous_oxide_emissions": "Nitrous oxide emissions (thousand metric tons of CO2 equivalent)",
            "pm25_air_pollution": "PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)",
            "threatened_bird_species": "Bird species, threatened",
            "climate_risk_index": "Climate Risk Index",
            "ghg_net_emissions_removals": "GHG net emissions/removals by LUCF (Mt of CO2 equivalent)",
            "co2_emissions_solid_fuel": "CO2 emissions from solid fuel consumption (kt)",
            "threatened_fish_species": "Fish species, threatened",
            "population_growth": "Population growth (annual %)",
            "protected_areas": "Terrestrial and marine protected areas (% of total territorial area)",
            "internal_renewable_water_resources": "Internal renewable water resources (billion cubic meters)",
            "urban_population": "Urban population (% of total population)"
        }

        combined_dfs = []

        for file_path, collection_name in file_collection_map.items():
            indicator_name = indicator_name_map.get(collection_name, collection_name.replace('_', ' ').title())
            df = extract_data(file_path)
            df_transformed = transform_data(df, indicator_name, country_metadata)
            if df_transformed is not None:
                combined_dfs.append(df_transformed)
            load_data(df_transformed, collection_name)

        if combined_dfs:
            combined_df = pd.concat(combined_dfs)
            create_dim_country_table(combined_df)
            create_dim_year_table()
            create_fact_table(combined_df)

            # Carica e salva le soluzioni
        solutions_file = "../data/solutions.csv"
        solutions_df = load_solutions(solutions_file)
        save_solutions_to_db(solutions_df, "indicator_solutions")
        logging.info("ETL process, cube creation, and index creation completed successfully.")
    except Exception as e:
        logging.error(f"ETL process failed: {e}")


if __name__ == "__main__":
    main()
