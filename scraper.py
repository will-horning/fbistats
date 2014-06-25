''' Scraping FBI stats from easy access. '''
from fbistats import mongo
import requests, json, sys
from collections import defaultdict
from itertools import izip
import numpy as np

STATS_BASE_URL = 'http://ojjdp.gov/ojstatbb/ezaucr/asp/ucr_export.asp'
    
def get_county_table(state_id, county_id):
    ''' Get data from state, county provided by id numbers. '''
    params = {
        'Select_State': state_id,
        'Select_County': county_id,
        'rdoData': '1c',
        'rdoYear': '2006',
        'print': 'no'
    }
    try:
        text = requests.get(STATS_BASE_URL, params=params).text
    except requests.ConnectionError:
        print 'ConnectionError on: ' 
        print params['Select_State'], params['Select_County']
        return 'There was a problem'
    return text

def get_all():
    '''Loops through every state and county, parses the data and stores it.'''
    counties_geo = {}
    with open('fbistats/static/js/counties_geo.json', 'r') as f:
        counties_geo = json.load(f, 'latin-1')
    for feature in counties_geo['features']:
        state_id = feature['properties']['STATE']
        county_id = feature['properties']['COUNTY']
        text = get_county_table(state_id, county_id)
        if 'There was a problem' not in text:
            data = parse_stats_page(text, state_id, county_id)
            if not mongo.counties.find_one(data):
                mongo.counties.insert(data)
                print data['county_name'], ', ', data['state_name']

def parse_stats_page(text, state_id, county_id, year1='1995', year2='2010'):
    ''' Extracts data from county stats page. '''
    county_data = defaultdict(dict)
    county_data['years'] = defaultdict(dict)
    lines = text.split('\n')
    county_name, state_name = ' '.join(lines[1].split()[6:]).split(',')
    county_data['county_name'] = county_name.strip()
    county_data['state_name'] = state_name.strip()
    county_data['state_id'] = state_id
    county_data['county_id'] = county_id
    years = [y for y in lines[2].split()[:-1]]
    for line in lines[3:]:
        if 'Nonindex' in line: 
            continue
        if line == '': 
            break
        row = line.split('\t')[:-1]
        crime_type = row[0].strip().replace('/', ', ')
        crime_type = crime_type.replace('.', '')
        for year, value in izip(years, row[1:]):
            if value in ['not available', ' ']:
                county_data['years'][year][crime_type] = 0
            else: 
                value = ''.join([c for c in value if c not in ['%', ',']])
                county_data['years'][year][crime_type] = int(value)
        for crime in county_data['years']['2010']:
            year1_val = county_data['years'][year1][crime]
            year2_val = county_data['years'][year2][crime]
            year1_val = 1 if year1_val == 0 else year1_val
            delta = float(year2_val - year1_val) / year1_val
            county_data['deltas'][crime] = delta 
    return county_data 

def get_distribution_values():
    ''' Returns a dict of min, max, mean, standard deviation and median for
    every feature. '''
    counties = mongo.counties.find()
    dist_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for county in counties:
        for year, crimes2vals in county['years'].iteritems():
            for crime, value in crimes2vals.iteritems():
                dist_data[year][crime]['values'].append(value)
        for crime, delta in county['deltas'].iteritems():
            dist_data['deltas'][crime]['values'].append(delta)
    for year in dist_data:
        for crime in dist_data[year]:
            vals = dist_data[year][crime]['values']
            vals = [i for i in vals if i is not None]
            arr = np.array(vals)
            dist_data[year][crime].update({
                'mean': np.mean(arr),
                'sd': np.std(arr),
                'median': np.median(arr),
                'max': max(vals),
                'min': min(vals)
            })
    return dist_data

def normalize():
    ''' Normalizes all values in county data. '''
    counties = mongo.counties.find()
    dist_data = get_distribution_values()
    for county in counties:
        for year, crimes2vals in county['years'].iteritems():
            for crime, val in crimes2vals.iteritems():
                if val is None:
                    crimes2vals[crime] = 0.0
                else:
                    max_v = dist_data[year][crime]['max']
                    min_v = dist_data[year][crime]['min']
                    crimes2vals[crime] = float(val - min_v) / (max_v - min_v)
        for crime, delta in county['deltas'].iteritems():
            max_d = dist_data['deltas'][crime]['max']
            min_d = dist_data['deltas'][crime]['min']
            if max_d != min_d:
                county['deltas'][crime] = float(delta - min_d) / (max_d - min_d)
        mongo.normalized_counties.save(county)    

def write_to_json(path='fbistats/static/js/counties_geo.json'):
    with open(path, 'r') as f:
        counties_geo = json.load(f, 'latin-1')
    for feature in counties_geo['features']:
        county_stats = mongo.normalized_counties.find_one({
            'state_id': feature['properties']['STATE'], 
            'county_id': feature['properties']['COUNTY']})
        if county_stats:
            for crime, value in county_stats['deltas'].iteritems():
                feature['properties'][crime] = value
    with open(path, 'w') as f:
        json.dump(counties_geo, f)