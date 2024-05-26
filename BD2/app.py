from flask_bootstrap import Bootstrap
from flask import Flask, render_template

app = Flask("SOS Earth")
bootstrap = Bootstrap(app)


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', bootstrap=bootstrap)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/problems')
def problems():
    return render_template('problems_earth.html')


@app.route('/help')
def help():
    return render_template('help_earth.html')


@app.route('/project')
def project():
    return render_template('project_earth.html')


if __name__ == '__main__':
    app.run(debug=True)
