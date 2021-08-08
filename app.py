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

app = Flask(__name__)
#app.debug = True
#app.config['DEBUG'] = True

# export FLASK_DEBUG=1; flask run

@app.route("/")
def index():
    """Generate main page."""
    return render_template("index.html")


@app.route('/update', methods=['POST', 'GET'])
def update():
    """Update database from COVID tracker site."""
    print(request.get_json())
    print('Params:', request.args)
    params = request.args.to_dict()
    result = tracker.update_data(params)
    print('result:', result)
    return json.dumps(result)
    
    
@app.route("/table")
def table():
    """Generate table output data."""
    
    # request parameters.
    params = request.args.to_dict()
    table_data = get_table_data(params)
    return json.dumps(table_data)

@app.route("/chart")
def chart():
    """ Return chart's data."""
    
    ## request parameters.
    params = request.args.to_dict()
    ## generate chart
    chart = mixreport.get_chart(params)
    # print('Chart: ', chart)
    # print('JSON: ', json.dumps(chart))

    return json.dumps(chart)


def get_periods(args, periods):
    """Gets periods from http request."""
    for arg, value in args.items():
        if 'date_start_' in arg:
            date_end_name = 'date_end_' + arg[arg.rfind('_') + 1:]
            periods.append((value, args[date_end_name]))
    # print('periods: ', periods)
    return 

    
if __name__ == "__main__":
    app.debug = True
    app.run()
