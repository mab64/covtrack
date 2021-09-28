
import os
import sys
import json
from flask import Flask, redirect, render_template, request, url_for

import tracker

import logging

logging.basicConfig(
    format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
# format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',

logger = logging.getLogger(__name__)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print('ROOT_DIR:', ROOT_DIR)

app = Flask(__name__) # app.debug = True or app.config['DEBUG'] = True
# export FLASK_DEBUG=1; flask run

@app.route("/")
def index():
    """Generates main page."""

    return render_template("index.html")


@app.route('/update')   # , methods=['POST', 'GET']
def update():
    """Updates database from COVID tracker site."""
    
    #print('Params:', request.args)
    # params = request.args.to_dict()
    result = tracker.update_data(json.loads(request.args.get('periods')))
    # print('result:', result)
    return json.dumps(result)
    
    
@app.route("/getdata")  # , methods=['POST', 'GET']
def getdata():
    """Gets and returns data from database."""
    
    # print('Params:', request.args)
    ## request parameters.
    # params = request.args.to_dict()
    data = tracker.get_data(json.loads(request.args.get('periods')))
    return json.dumps(data)

