from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os

# Carica variabili d'ambiente dal file .env
load_dotenv()

app = Flask("SOS Earth")
bootstrap = Bootstrap(app)

# Configurazione di MongoDB
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)


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
    return render_template('problems_earth.html')


@app.route('/help')
def help_earth():
    return render_template('help_earth.html')


@app.route('/project')
def project():
    return render_template('project_earth.html')


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    return render_template('carbon.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


if __name__ == '__main__':
    app.run(debug=True)
