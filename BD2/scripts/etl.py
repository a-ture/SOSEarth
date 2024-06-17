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


# Funzioni di estrazione dati
def extract_data(file_path, delimiter=',', header=0, skiprows=None):
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None
    try:
        logging.info(f"Extracting data from {file_path}")
        df = pd.read_csv(file_path, delimiter=delimiter, comment='#', header=header, skiprows=skiprows)
        logging.info(f"Extracted columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Error extracting data from {file_path}: {e}")
        return None


# Funzioni di trasformazione dati
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


def transform_temperature_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        df = df.rename(columns={"Year": "year", "No_Smoothing": "temperature"})
        df = df[df['year'].apply(lambda x: x.isnumeric())]
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
            "ISO3": "iso3"
        })
        df = df[["name", "designation", "iucn_category", "iso3"]]
        logging.info(f"Transformed columns for protected areas data: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Error transforming protected areas data: {e}")
        return None


# Funzione per caricare i dati nel database
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


# Funzioni per caricare i metadati
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


# Funzioni per la creazione delle tabelle di dimensione e fatto
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


def extract_data_food_production(file_path, delimiter=',', header=0, skiprows=None):
    return extract_data(file_path, delimiter, header, skiprows)


def extract_data_food_product_emissions(file_path, delimiter=',', header=0, skiprows=None):
    return extract_data(file_path, delimiter, header, skiprows)


def transform_food_production_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        # Adjust column names based on the actual columns in the CSV
        df = df.rename(columns={
            "Food product": "food_product",
            "Land use change": "land_use_change",
            "Animal Feed": "animal_feed",
            "Farm": "farm",
            "Processing": "processing",
            "Transport": "transport",
            "Packging": "packaging",
            "Retail": "retail",
            "Total_emissions": "total_emissions",
            "Eutrophying emissions per 1000kcal (gPO₄eq per 1000kcal)": "eutrophying_emissions_1000kcal",
            "Eutrophying emissions per kilogram (gPO₄eq per kilogram)": "eutrophying_emissions_kg",
            "Eutrophying emissions per 100g protein (gPO₄eq per 100 grams protein)": "eutrophying_emissions_100g_protein",
            "Freshwater withdrawals per 1000kcal (liters per 1000kcal)": "freshwater_withdrawals_1000kcal",
            "Freshwater withdrawals per 100g protein (liters per 100g protein)": "freshwater_withdrawals_100g_protein",
            "Freshwater withdrawals per kilogram (liters per kilogram)": "freshwater_withdrawals_kg",
            "Greenhouse gas emissions per 1000kcal (kgCO₂eq per 1000kcal)": "ghg_emissions_1000kcal",
            "Greenhouse gas emissions per 100g protein (kgCO₂eq per 100g protein)": "ghg_emissions_100g_protein",
            "Land use per 1000kcal (m² per 1000kcal)": "land_use_1000kcal",
            "Land use per kilogram (m² per kilogram)": "land_use_kg",
            "Land use per 100g protein (m² per 100g protein)": "land_use_100g_protein",
            "Scarcity-weighted water use per kilogram (liters per kilogram)": "scarcity_weighted_water_use_kg",
            "Scarcity-weighted water use per 100g protein (liters per 100g protein)": "scarcity_weighted_water_use_100g_protein",
            "Scarcity-weighted water use per 1000kcal (liters per 1000 kilocalories)": "scarcity_weighted_water_use_1000kcal"
        })
        logging.info(f"Transformed columns for food production data: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Error transforming food production data: {e}")
        return None


def transform_food_product_emissions_data(df):
    if df is None:
        return None
    try:
        df.columns = df.columns.str.strip()
        df = df.rename(columns={
            "Food product": "food_product",
            "Land Use Change": "land_use_change",
            "Feed": "feed",
            "Farm": "farm",
            "Processing": "processing",
            "Transport": "transport",
            "Packaging": "packaging",
            "Retail": "retail",
            "Total from Land to Retail": "total_from_land_to_retail",
            "Total Global Average GHG Emissions per kg": "total_ghg_emissions_per_kg",
            "Unit of GHG Emissions": "unit_of_ghg_emissions"
        })
        logging.info(f"Transformed columns for food product emissions data: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Error transforming food product emissions data: {e}")
        return None


def load_food_production_data(df):
    load_data(df, "food_production")


def load_food_product_emissions_data(df):
    load_data(df, "food_product_emissions")


# Funzione principale
def main():
    try:
        # Pulizia delle collezioni
        collections = db.list_collection_names()
        for collection_name in collections:
            db[collection_name].drop()
            logging.info(f"Collection {collection_name} dropped.")

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

        # Carica e salva i metadati degli indicatori
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
            df = extract_data(file_path, delimiter=',', skiprows=4)
            df_transformed = transform_data(df, indicator_name, country_metadata)
            if df_transformed is not None:
                combined_dfs.append(df_transformed)
            load_data(df_transformed, collection_name)

        if combined_dfs:
            combined_df = pd.concat(combined_dfs)
            create_dim_country_table(combined_df)
            create_dim_year_table()
            create_fact_table(combined_df)

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

        # Process GMSL data
        gmsl_df = extract_data("../data/GMSL_TPJAOS_5.1.txt", delimiter=r'\s+', header=1)  # Adjust header accordingly
        gmsl_transformed = transform_gmsl_data(gmsl_df)
        load_data(gmsl_transformed, "gmsl_data")

        # Process protected areas data
        protected_areas_df = extract_data("../data/WDPA_Aug2023_Public_csv.csv", delimiter=',', header=0)
        protected_areas_transformed = transform_protected_areas_data(protected_areas_df)
        load_data(protected_areas_transformed, "protected_areas_1")

        # Carica e salva le soluzioni
        solutions_file = "../data/solutions.csv"
        solutions_df = load_solutions(solutions_file)
        save_solutions_to_db(solutions_df, "indicator_solutions")

        # Process food production data
        food_production_df = extract_data_food_production("../data/Food_Production.csv", delimiter=',', header=0)
        if food_production_df is not None:
            print(food_production_df.columns)  # Inspect columns for debugging
        food_production_transformed = transform_food_production_data(food_production_df)
        load_food_production_data(food_production_transformed)

        # Process food product emissions data
        food_product_emissions_df = extract_data_food_product_emissions("../data/Food_Product_Emissions.csv",
                                                                        delimiter=',', header=0)
        food_product_emissions_transformed = transform_food_product_emissions_data(food_product_emissions_df)
        load_food_product_emissions_data(food_product_emissions_transformed)

        # Carica dati e salva nel database
        file_path = "../data/Earth_Systems_Correlations.csv"
        df = extract_data(file_path)
        load_data(df, "earth_systems_correlations")

        logging.info("ETL process, cube creation, and index creation completed successfully.")
    except Exception as e:
        logging.error(f"ETL process failed: {e}")


if __name__ == "__main__":
    main()
