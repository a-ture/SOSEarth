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
    return render_template('project.html')


@app.route('/chart')
def chart():
    return render_template('charts.html')


@app.route('/get_countries', methods=['GET'])
def get_countries():
    countries = list(mongo.db.dim_country.find({}, {"_id": 0, "Country Name": 1}))
    return jsonify(countries)


@app.route('/get_co2_data', methods=['GET'])
def get_co2_data():
    country_name = request.args.get('country_name')
    if not country_name:
        return jsonify({"error": "Country name is required"}), 400

    # Trova il country_key per il paese specificato
    country = mongo.db.dim_country.find_one({"Country Name": country_name})
    if not country:
        return jsonify({"error": f"Country {country_name} not found"}), 404

    country_key = country['country_key']

    # Estrai i dati dalla tabella dei fatti
    co2_data = list(mongo.db.fact_table.find({"country_key": country_key, "Indicator Name": "CO2 Emissions"}))
    if not co2_data:
        return jsonify({"error": f"No CO2 data found for country {country_name}"}), 404

    # Creare un DataFrame dai dati estratti
    df_co2 = pd.DataFrame(co2_data)

    # Unire con la tabella degli anni per ottenere gli anni corretti
    years = pd.DataFrame(list(mongo.db.dim_year.find({}, {'_id': 0, 'year_key': 1, 'Year': 1})))
    df_co2 = df_co2.merge(years, on="year_key")

    # Convertire i dati in un formato JSON adatto per amCharts
    data = df_co2[['Year', 'Value']].to_dict(orient='records')

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
