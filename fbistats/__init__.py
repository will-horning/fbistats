"""Main FBIStats module."""
import os, sys, json, pymongo
from flask import Flask


app = Flask(__name__)
app.config['DEBUG'] = True

mongo_url = os.environ.get('MONGOHQ_URL')
if mongo_url:
    mongo_conn = pymongo.Connection(mongo_url)
    mongo = mongo_conn.fbistats
else:
    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo = mongo_conn['fbistats']

mongo_conn = pymongo.Connection(mongo_url)
mongo = mongo_conn.fbistats
import fbistats.views
