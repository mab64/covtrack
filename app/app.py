"""app.debug = True or app.config['DEBUG'] = True
export FLASK_DEBUG=1; flask run
logging.basicConfig(
    format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
# format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',

# logger = logging.getLogger(__name__)

"""

import os
import sys
import json
from flask import Flask, redirect, render_template, request, url_for
import logging

import tracker


logging.basicConfig(
    format='%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S')
# format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',

# logger = logging.getLogger(__name__)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
__version__ = '0.1.03'
# print('ROOT_DIR:', ROOT_DIR, '', __version__)

app = Flask(__name__)

app.logger.info('Version: {};'.format(__version__))
app.logger.debug('ROOT_DIR: {}'.format(ROOT_DIR))

@app.route("/")
def index():
    """Generates main page."""

    return render_template("index.html", version=__version__)


@app.route('/update')
def update():
    """Updates database from COVID tracker site."""
    
    #print('Params:', request.args)
    periods = json.loads(request.args.get('periods'))
    result = tracker.update_data(periods)
    # print('result:', result)
    return json.dumps(result)
    
    
@app.route("/getdata")
def getdata():
    """Gets and returns data from database."""
    
    # print('Params:', request.args)
    ## request parameters.
    periods = json.loads(request.args.get('periods'))
    data = tracker.get_data(periods)
    return json.dumps(data)


