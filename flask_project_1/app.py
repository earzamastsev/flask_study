from flask import Flask
from flask import render_template
from data import *
from collections import OrderedDict
from random import sample

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    tours_index = OrderedDict([(k, tours[k]) for k in sample(tours.keys(), 6)])
    return render_template('index.html', departures=departures, tours=tours_index)


@app.route('/departure/<from1>/')
def departure(from1):
    tours_filteres = {}
    tours_list = []
    for key, value in tours.items():
        if value["departure"] == from1:
            tours_filteres[key] = value
            tours_list.append(value)
    return render_template('departure.html', from1=from1, departures=departures, tours=tours_filteres,
                           tours_list=tours_list)


@app.route('/tour/<id>/')
def tour(id):
    id = int(id)
    return render_template('tour.html', tours=tours, departures=departures, id=id)


if __name__ == '__main__':
    app.run()
