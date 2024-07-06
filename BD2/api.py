from flask import Blueprint
from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
from bson import ObjectId
import os
import logging
import pandas as pd
import numpy as np

from app import app
from extension import mongo
from utils import country_name_to_iso3

api_bp = Blueprint('api', __name__)


@api_bp.route('/get_metadata', methods=['GET'])
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


@api_bp.route('/get_labels', methods=['GET'])
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


@api_bp.route('/get_indicators', methods=['GET'])
def get_indicators():
    indicators = mongo.db.fact_table.distinct("Indicator Name")
    return jsonify(indicators)







@api_bp.route('/get_countries', methods=['GET'])
def get_countries():
    countries = list(mongo.db.dim_country.find({}, {"_id": 0, "Country Name": 1}))
    countries = convert_and_filter(countries)
    return jsonify(countries)


@api_bp.route('/get_data', methods=['GET'])
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


@api_bp.route('/get_data_indicator', methods=['GET'])
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


@api_bp.route('/api/co2_emissions_average')
def co2_emissions_average():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_CO2_Emissions": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.co2_emissions.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@api_bp.route('/api/co2_emissions_change')
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


@api_bp.route('/api/methane_emissions')
def methane_emissions():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_Methane_Emissions": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.methane_emissions.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@api_bp.route('/api/renewable_energy')
def renewable_energy():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_Renewable_Energy": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.renewable_energy.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@api_bp.route('/api/threatened_bird_species')
def threatened_bird_species():
    pipeline = [
        {"$match": {"Year": 2018}},
        {"$group": {"_id": "$Country Name", "Threatened_Bird_Species": {"$sum": "$Value"}}}
    ]
    data = list(mongo.db.threatened_bird_species.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@api_bp.route('/api/pm25_emissions')
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


@api_bp.route('/api/climate_risk_index')
def climate_risk_index():
    pipeline = [
        {"$match": {"Year": {"$gte": 2000, "$lte": 2020}}},
        {"$group": {"_id": "$Country Name", "Average_Climate_Risk_Index": {"$avg": "$Value"}}}
    ]
    data = list(mongo.db.climate_risk_index.aggregate(pipeline))
    data = convert_and_filter(data)
    return jsonify(data)


@api_bp.route('/api/agricultural_land_use', methods=['GET'])
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


@api_bp.route('/api/total_ghg_emissions')
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