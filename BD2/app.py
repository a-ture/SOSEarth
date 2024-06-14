from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
from bson import ObjectId
import os
import logging
import pandas as pd
import numpy as np

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


# Function to convert ObjectId to strings and filter out NaN values
def convert_and_filter(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item and isinstance(item['_id'], ObjectId):
                item['_id'] = str(item['_id'])
            for key, value in item.items():
                if isinstance(value, float) and np.isnan(value):
                    item[key] = None
    elif isinstance(data, dict):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        for key, value in data.items():
            if isinstance(value, float) and np.isnan(value):
                data[key] = None
    return data


# Routes definition
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/problems')
def problems():
    problems_list = list(mongo.db.problems.find())
    problems_list = convert_and_filter(problems_list)
    return render_template('problems_earth.html', problems=problems_list)


@app.route('/chart')
def chart():
    return render_template('chart.html')


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


if __name__ == "__main__":
    app.run(debug=True)
