from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os
import logging
import pandas as pd

from utils import convert_and_filter, country_name_to_iso3

# Load environment variables
load_dotenv()

app = Flask("SOS Earth")
bootstrap = Bootstrap(app)

# MongoDB configuration
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI not found in .env file")

app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)
logging.basicConfig(level=logging.DEBUG)


def get_latest_data():
    vital_signs = []

    # Fetch latest CO2 concentration
    co2_data = mongo.db.co2_data.find_one(sort=[("decimal_date", -1)])
    if co2_data:
        vital_signs.append({
            "title": "CO2 Concentration",
            "value": co2_data.get("co2_concentration", "N/A"),
            "trend": "up",
            "description": "parts per million"
        })

    # Fetch latest Methane emissions
    methane_data = mongo.db.methane_emissions.find_one(sort=[("year", -1), ("month", -1)])
    if methane_data:
        vital_signs.append({
            "title": "Methane Emissions",
            "value": methane_data.get("ch4_concentration", "N/A"),
            "trend": "up",
            "description": "parts per billion"
        })

    # Fetch latest Nitrous Oxide emissions
    nitrous_oxide_data = mongo.db.nitrous_oxide_emissions.find_one(sort=[("year", -1)])
    if nitrous_oxide_data:
        vital_signs.append({
            "title": "Nitrous Oxide Emissions",
            "value": nitrous_oxide_data.get("Value", "N/A"),
            "trend": "up",
            "description": "thousand metric tons of CO2 equivalent"
        })

    # Fetch latest PM2.5 air pollution
    pm25_data = mongo.db.pm25_air_pollution.find_one(sort=[("year", -1)])
    if pm25_data:
        vital_signs.append({
            "title": "PM2.5 Air Pollution",
            "value": pm25_data.get("Value", "N/A"),
            "trend": "up",
            "description": "micrograms per cubic meter"
        })

    # Fetch latest Renewable Energy consumption
    renewable_energy_data = mongo.db.renewable_energy.find_one(sort=[("year", -1)])
    if renewable_energy_data:
        vital_signs.append({
            "title": "Renewable Energy Consumption",
            "value": renewable_energy_data.get("Value", "N/A"),
            "trend": "up",
            "description": "percentage of total energy consumption"
        })

    # Fetch latest Total GHG Emissions
    total_ghg_emissions_data = mongo.db.total_ghg_emissions.find_one(sort=[("year", -1)])
    if total_ghg_emissions_data:
        vital_signs.append({
            "title": "Total GHG Emissions",
            "value": total_ghg_emissions_data.get("Value", "N/A"),
            "trend": "up",
            "description": "kt of CO2 equivalent"
        })

    # Fetch latest Coal Use
    coal_use_data = mongo.db.coal_use.find_one(sort=[("year", -1)])
    if coal_use_data:
        vital_signs.append({
            "title": "Coal Use",
            "value": coal_use_data.get("Value", "N/A"),
            "trend": "up",
            "description": "percentage of total energy use"
        })

    # Fetch latest Hydroelectricity
    hydroelectricity_data = mongo.db.hydroelectricity.find_one(sort=[("year", -1)])
    if hydroelectricity_data:
        vital_signs.append({
            "title": "Hydroelectricity",
            "value": hydroelectricity_data.get("Value", "N/A"),
            "trend": "up",
            "description": "percentage of total electricity production"
        })

    # Fetch latest Threatened Bird Species
    threatened_bird_species_data = mongo.db.threatened_bird_species.find_one(sort=[("year", -1)])
    if threatened_bird_species_data:
        vital_signs.append({
            "title": "Threatened Bird Species",
            "value": threatened_bird_species_data.get("Value", "N/A"),
            "trend": "up",
            "description": "number of species"
        })

    # Fetch latest Climate Risk Index
    climate_risk_index_data = mongo.db.climate_risk_index.find_one(sort=[("year", -1)])
    if climate_risk_index_data:
        vital_signs.append({
            "title": "Climate Risk Index",
            "value": climate_risk_index_data.get("Value", "N/A"),
            "trend": "up",
            "description": "index"
        })

    # Fetch latest Arctic Sea Ice Minimum Extent (example from temperature_data)
    arctic_ice_data = mongo.db.temperature_data.find_one(sort=[("year", -1)])
    if arctic_ice_data:
        vital_signs.append({
            "title": "Arctic Sea Ice Minimum Extent",
            "value": arctic_ice_data.get("temperature", "N/A"),
            "trend": "down",
            "description": "temperature anomaly"
        })

    # Fetch latest Global Mean Sea Level
    gmsl_data = mongo.db.gmsl_data.find_one(sort=[("decimal_year", -1)])
    if gmsl_data:
        vital_signs.append({
            "title": "Global Mean Sea Level",
            "value": gmsl_data.get("gmsl", "N/A"),
            "trend": "up",
            "description": "millimeters"
        })

    return vital_signs


@app.route('/get_metadata', methods=['GET'])
def get_metadata():
    indicator_name = request.args.get('indicator_name')
    if not indicator_name:
        return jsonify({"error": "Indicator name is required"}), 400

    metadata = mongo.db.indicator_metadata.find_one(
        {"INDICATOR_NAME": indicator_name},
        {"_id": 0, "SOURCE_NOTE": 1, "SOURCE_ORGANIZATION": 1}
    )
    if not metadata:
        return jsonify({"error": f"No metadata found for indicator {indicator_name}"}), 404

    return jsonify(metadata)


@app.route('/get_labels', methods=['GET'])
def get_labels():
    indicator_name = request.args.get('indicator_name')
    if not indicator_name:
        return jsonify({"error": "Indicator name is required"}), 400

    labels_map = {
        "CO2 Emissions": {"x": "Year", "y": "CO2 Emissions (kt)"},
        "Agricultural Land": {"x": "Year", "y": "Agricultural Land (%)"},
        "Arable Land": {"x": "Year", "y": "Arable Land (%)"},
        "Irrigated Land": {"x": "Year", "y": "Irrigated Land (%)"},
        "Precipitation": {"x": "Year", "y": "Precipitation (mm)"},
        "Hydroelectricity": {"x": "Year", "y": "Hydroelectricity (%)"},
        "Nuclear Electricity": {"x": "Year", "y": "Nuclear Electricity (%)"},
        "Renewable Energy": {"x": "Year", "y": "Renewable Energy (%)"},
        "Coal Use": {"x": "Year", "y": "Coal Use (%)"},
        "Methane Emissions": {"x": "Year", "y": "Methane Emissions (kt)"},
        "Nitrous Oxide Emissions": {"x": "Year", "y": "Nitrous Oxide Emissions (kt)"},
        "PM25 Air Pollution": {"x": "Year", "y": "PM25 Air Pollution (µg/m³)"},
        "Threatened Bird Species": {"x": "Year", "y": "Number of Threatened Bird Species"},
        "Climate Risk Index": {"x": "Year", "y": "Climate Risk Index"},
        "GHG Net Emissions Removals": {"x": "Year", "y": "GHG Net Emissions Removals (kt)"},
        "CO2 Emissions Solid Fuel": {"x": "Year", "y": "CO2 Emissions from Solid Fuel (kt)"},
        "Threatened Fish Species": {"x": "Year", "y": "Number of Threatened Fish Species"}
    }

    labels = labels_map.get(indicator_name, {"x": "Year", "y": "Value"})
    return jsonify(labels)


@app.route('/get_indicators', methods=['GET'])
def get_indicators():
    indicators = mongo.db.fact_table.distinct("Indicator Name")
    return jsonify(indicators)


@app.route('/get_countries', methods=['GET'])
def get_countries():
    countries = list(mongo.db.dim_country.find({}, {"_id": 0, "Country Name": 1}))
    countries = convert_and_filter(countries)
    return jsonify(countries)


@app.route('/get_data', methods=['GET'])
def get_data():
    country_name = request.args.get('country_name')
    indicator_name = request.args.get('indicator_name')
    if not country_name or not indicator_name:
        return jsonify({"error": "Country name and indicator name are required"}), 400

    country_iso3 = country_name_to_iso3.get(country_name)
    if not country_iso3:
        return jsonify({"error": f"ISO3 code not found for country {country_name}"}), 404

    country = mongo.db.dim_country.find_one({"ISO3": country_iso3})
    if not country:
        return jsonify({"error": f"Country {country_name} not found"}), 404

    country_key = country['country_key']

    data = list(mongo.db.fact_table.find({"country_key": country_key, "Indicator Name": indicator_name}))
    if not data:
        return jsonify({"error": f"No data found for country {country_name} and indicator {indicator_name}"}), 404

    df = pd.DataFrame(data)

    years = pd.DataFrame(list(mongo.db.dim_year.find({}, {'_id': 0, 'year_key': 1, 'Year': 1})))
    df = df.merge(years, on="year_key")

    result = df[['Year', 'Value']].to_dict(orient='records')

    return jsonify(result)


@app.route('/get_data_indicator', methods=['GET'])
def get_data_indicator():
    country_name = request.args.get('country_name')
    indicator_name = request.args.get('indicator_name')
    if not country_name or not indicator_name:
        return jsonify({"error": "Country name and indicator name are required"}), 400

    country = mongo.db.dim_country.find_one({"Country Name": country_name})
    if not country:
        return jsonify({"error": f"Country {country_name} not found"}), 404

    country_key = country['country_key']

    data = list(mongo.db.fact_table.find({"country_key": country_key, "Indicator Name": indicator_name}))
    if not data:
        return jsonify({"error": f"No data found for country {country_name} and indicator {indicator_name}"}), 404

    df = pd.DataFrame(data)

    years = pd.DataFrame(list(mongo.db.dim_year.find({}, {'_id': 0, 'year_key': 1, 'Year': 1})))
    df = df.merge(years, on="year_key")

    result = df[['Year', 'Value']].to_dict(orient='records')

    return jsonify(result)


@app.route('/api/co2_emissions_average')
def co2_emissions_average():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_CO2_Emissions": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.co2_emissions.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/co2_emissions_change')
def co2_emissions_change():
    pipeline = [
        {"$match": {"Year": {"$in": [2000, 2020]}}},
        {"$group": {"_id": {"Country": "$Country Name", "Year": "$Year"}, "CO2_Emissions": {"$sum": "$Value"}}},
        {"$group": {"_id": "$_id.Country", "Emissions": {"$push": {"year": "$_id.Year", "value": "$CO2_Emissions"}}}},
        {"$project": {
            "Country": "$_id",
            "Percentage_Change": {
                "$cond": {
                    "if": {"$eq": [{"$arrayElemAt": ["$Emissions.value", 0]}, 0]},
                    "then": None,
                    "else": {
                        "$multiply": [
                            {"$divide": [{"$subtract": [{"$arrayElemAt": ["$Emissions.value", 1]},
                                                        {"$arrayElemAt": ["$Emissions.value", 0]}]},
                                         {"$arrayElemAt": ["$Emissions.value", 0]}]},
                            100
                        ]
                    }
                }
            }
        }}
    ]
    data = list(mongo.db.co2_emissions.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/methane_emissions')
def methane_emissions():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_Methane_Emissions": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.methane_emissions.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/renewable_energy')
def renewable_energy():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_Renewable_Energy": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.renewable_energy.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/threatened_bird_species')
def threatened_bird_species():
    pipeline = [
        {"$match": {"Year": 2018}},
        {"$group": {"_id": "$Country Name", "Threatened_Bird_Species": {"$sum": "$Value"}}}
    ]
    data = list(mongo.db.threatened_bird_species.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/pm25_emissions')
def pm25_emissions():
    try:
        pipeline = [
            {"$match": {"Year": {"$gte": 2000, "$lte": 2018}, "Value": {"$ne": None}, "Country Name": {"$ne": None}}},
            {"$group": {"_id": "$Country Name", "Average_PM25_Emissions": {"$avg": "$Value"}}}
        ]
        data = list(
            mongo.db.pm25_air_pollution.aggregate(pipeline))  # Assicurati che il nome della collezione sia corretto
        data = convert_and_filter(data)
        if not data:
            return jsonify({"error": "No data found for PM2.5 emissions"}), 404
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching PM2.5 emissions data: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/climate_risk_index')
def climate_risk_index():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_Climate_Risk_Index": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.climate_risk_index.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/agricultural_land_use', methods=['GET'])
def agricultural_land_use():
    pipeline = [
        {"$match": {"Year": 2018, "Value": {"$ne": None}, "Country Name": {"$ne": None}}},
        {"$group": {"_id": "$Country Name", "Agricultural_Land_Use": {"$avg": "$Value"}}},
        {"$sort": {"Agricultural_Land_Use": -1}},
        {"$limit": 10}
    ]
    data = list(mongo.db.agricultural_land.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/api/total_ghg_emissions')
def total_ghg_emissions():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2018}}},
        {"$group": {"_id": {"Country Name": "$Country Name", "Year": "$Year"},
                    "Total_GHG_Emissions": {"$sum": "$Value"}}},

        {"$sort": {"_id.Year": 1}}
    ]
    data = list(mongo.db.total_ghg_emissions.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@app.route('/vital-signs')
def vital_signs():
    data = get_latest_data()
    return jsonify(data)


@app.route('/country_protected_areas', methods=['GET'])
def country_protected_areas():
    country_name = request.args.get('country_name')
    if not country_name:
        return jsonify({"error": "Country name is required"}), 400

    country_iso3 = country_name_to_iso3.get(country_name)
    if not country_iso3:
        return jsonify({"error": f"ISO3 code not found for country {country_name}"}), 404

    protected_areas = list(mongo.db.protected_areas_1.find({"iso3": country_iso3}))
    if not protected_areas:
        app.logger.info(f"No protected areas found for country: {country_name}")
        return jsonify([])

    results = []
    for area in protected_areas:
        app.logger.debug(f"Protected area data: {area}")
        results.append({
            "name": area.get("name", "No Name Available"),
            "designation": area.get("designation", "Not Available"),
            "iucn_category": area.get("iucn_category", "Not Available")
        })
    return jsonify(results)


# Routes definition
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/problems')
def problems():
    problems_list = list(mongo.db.problems.find())
    problems_list = convert_and_filter(problems_list)
    return render_template('problems_earth.html', problems=problems_list)


@app.route('/help')
def help_earth():
    try:
        solutions_list = list(mongo.db.indicator_solutions.find({}, {'_id': 0}))
        solutions_list = convert_and_filter(solutions_list)
        logging.debug(f"Solutions found: {solutions_list}")

        if solutions_list:
            logging.info(f"{len(solutions_list)} solutions found.")
        else:
            logging.warning("No solutions found in the collection.")

        return render_template('help_earth.html', solutions=solutions_list)
    except Exception as e:
        logging.error(f"Error retrieving solutions: {e}")
        return render_template('help_earth.html', solutions=[])


@app.route('/project')
def project():
    return render_template('project_earth.html')


@app.route('/indicators')
def indicators():
    return render_template('indicators.html')


@app.route('/calculator')
def calculator():
    return render_template('carbon.html')


if __name__ == "__main__":
    app.run(debug=True)
