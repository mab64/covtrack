"""app.debug = True or app.config['DEBUG'] = True
export FLASK_DEBUG=1; flask run

"""

import os
import json
from flask import Flask, render_template, request   # redirect, url_for
from flask.logging import create_logger

import tracker

__version__ = '0.1.09'

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
logger = create_logger(app)

logger.info('Version: %s', __version__)
logger.debug('ROOT_DIR: %s', ROOT_DIR)

# if tracker.check_db()

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
