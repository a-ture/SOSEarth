from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os
import logging
import pandas as pd

# Carica variabili d'ambiente dal file .env
load_dotenv()

app = Flask("SOS Earth")
bootstrap = Bootstrap(app)

# Configurazione di MongoDB
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI non è stata trovata nel file .env")

app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)
logging.basicConfig(level=logging.DEBUG)


# Definizione delle rotte
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
    problems_list = mongo.db.problems.find()
    return render_template('problems_earth.html', problems=problems_list)


@app.route('/get_metadata', methods=['GET'])
def get_metadata():
    indicator_name = request.args.get('indicator_name')
    if not indicator_name:
        return jsonify({"error": "Indicator name is required"}), 400

    # Trova i metadati per l'indicatore specificato
    metadata = mongo.db.indicator_metadata.find_one({"INDICATOR_NAME": indicator_name},
                                                    {"_id": 0, "SOURCE_NOTE": 1, "SOURCE_ORGANIZATION": 1})
    if not metadata:
        return jsonify({"error": f"No metadata found for indicator {indicator_name}"}), 404

    return jsonify(metadata)


@app.route('/get_labels', methods=['GET'])
def get_labels():
    indicator_name = request.args.get('indicator_name')
    if not indicator_name:
        return jsonify({"error": "Indicator name is required"}), 400

    # Mappa delle etichette per gli indicatori
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
        # Aggiungi altri indicatori e le loro etichette qui
    }

    labels = labels_map.get(indicator_name, {"x": "Year", "y": "Value"})
    return jsonify(labels)


@app.route('/get_indicators', methods=['GET'])
def get_indicators():
    # Assuming the indicators are stored in a collection or can be listed from the fact table
    indicators = mongo.db.fact_table.distinct("Indicator Name")
    return jsonify(indicators)


@app.route('/help')
def help_earth():
    return render_template('help_earth.html')


@app.route('/project')
def project():
    return render_template('project_earth.html')


@app.route('/chart')
def chart():
    return render_template('charts.html')


@app.route('/get_countries', methods=['GET'])
def get_countries():
    countries = list(mongo.db.dim_country.find({}, {"_id": 0, "Country Name": 1}))
    return jsonify(countries)


@app.route('/get_data', methods=['GET'])
def get_data():
    country_name = request.args.get('country_name')
    indicator_name = request.args.get('indicator_name')
    if not country_name or not indicator_name:
        return jsonify({"error": "Country name and indicator name are required"}), 400

    # Trova il country_key per il paese specificato
    country = mongo.db.dim_country.find_one({"Country Name": country_name})
    if not country:
        return jsonify({"error": f"Country {country_name} not found"}), 404

    country_key = country['country_key']

    # Estrai i dati dalla tabella dei fatti
    data = list(mongo.db.fact_table.find({"country_key": country_key, "Indicator Name": indicator_name}))
    if not data:
        return jsonify({"error": f"No data found for country {country_name} and indicator {indicator_name}"}), 404

    # Creare un DataFrame dai dati estratti
    df = pd.DataFrame(data)

    # Unire con la tabella degli anni per ottenere gli anni corretti
    years = pd.DataFrame(list(mongo.db.dim_year.find({}, {'_id': 0, 'year_key': 1, 'Year': 1})))
    df = df.merge(years, on="year_key")

    # Convertire i dati in un formato JSON adatto per Chart.js
    result = df[['Year', 'Value']].to_dict(orient='records')

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
