from fbistats import app
from flask import render_template
import json

@app.route('/', methods=['GET'])
def index():
    counties_geo = {}
    with open('fbistats/static/js/counties_geo.json', 'r') as f:
        counties_geo = json.load(f, 'latin-1')
    return render_template('index.html', county_data=json.dumps(counties_geo))

