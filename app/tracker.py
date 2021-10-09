#!/usr/bin/env python3

"""COVID Tracker module"""

import json
import os
import logging
import requests
import pymysql

CONN = None
APP_PATH = os.path.dirname(os.path.abspath(__file__))

# Load database connection parameters from config file if exists.
if os.path.isfile('conf/tracker.conf'):
    with open(os.path.join(APP_PATH, "conf", "tracker.conf")) as conf_file:
        CONF = json.load(conf_file)
else:
    CONF = {}

# Redefine connection parameters from environment if exists.
if os.getenv('MYSQL_HOST'):
    CONF["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
if os.getenv('MYSQL_PORT'):
    CONF["MYSQL_PORT"] = int(os.getenv('MYSQL_PORT'))
if os.getenv('MYSQL_USER'):
    CONF["MYSQL_USER"] = os.getenv('MYSQL_USER')
if os.getenv('MYSQL_PASSWORD'):
    CONF["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')
if os.getenv('MYSQL_DATABASE'):
    CONF["MYSQL_DATABASE"] = os.getenv('MYSQL_DATABASE')

# print('CONF:', CONF)
if os.getenv('FLASK_DEBUG') == '1' or os.getenv('FLASK_ENV').lower() == 'development':
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

logging.basicConfig(
    format='%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=LOG_LEVEL)
logger = logging.getLogger(__name__)

logger.debug('CONF: %s', CONF)
if not (CONF.get("MYSQL_DATABASE", "") and 
        CONF.get("MYSQL_USER", "") and
        CONF.get("MYSQL_PASSWORD","")):
    logger.error('Database connection parameters invalid!')

def check_db(CONN):
    """Connects to database and checks structure."""

    cur = CONN.cursor()
    query = '''
        CREATE TABLE IF NOT EXISTS data (
            date_value DATE,
            country_code CHAR(3),
            confirmed INT,
            deaths INT ,
            stringency_actual FLOAT(5, 2),
            stringency FLOAT(5, 2),
            PRIMARY KEY (country_code, date_value)
        );
        '''
    result = cur.execute(query)
    # query  = '''EXPLAIN data;'''
    # result = cur.execute(query)
    # print('result:', result)


def get_data(periods):
    """Receive data from database, returns processed."""

    if CONN:
        cur = CONN.cursor()
    else:
        return False

    for period in periods:
        query = """
            SELECT date_value, country_code, confirmed, deaths,
                stringency_actual, stringency FROM data
            WHERE (date_value BETWEEN %s AND %s)
            ORDER BY date_value, country_code"""


        # query = """WITH t1 AS (SELECT date_value, country_code, confirmed,
        #         deaths, stringency FROM data)
        #     SELECT t1.date_value, t1.country_code AS country,
        #     (t2.confirmed - t1.confirmed) AS confirmed,
        #     (t2.deaths - t1.deaths) AS deaths,
        #     t1.stringency, t2.stringency
        #     FROM data AS t2
        #     JOIN t1 ON t1.country_code = t2.country_code
        #     WHERE t1.date_value = %s AND t2.date_value = %s;"""

        query_vals = (period['date_start'], period['date_end'])
        cur.execute(query, query_vals)
        data = []
        rows = cur.fetchall()
        # print(rows)
        print('rows:', len(rows), type(rows))
        # data.append(rows)
        for row in rows:
            # data.append((row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4])))
            data.append((str(row[0]), row[1], row[2], row[3], row[4], row[5]))
        # print(data)
        headers = ['Date', 'Country', 'Confirmed', 'Deaths', 'String. actual', 'Stringency']
        result = [headers, data]
        return result


def get_remote_data(date_start, date_end):
    """Receive data from COVID Tracker site."""

    request = requests.get('/'.join((BASE_URL, date_start, date_end)))
    if request.status_code == 200:
        data = json.loads(request.content)
        if data.get('status') == 'error':
            return False
        return data
    return False


def update_data(periods):
    """Updates database from COVID Tracker site."""

    result = 0
    for period in periods:
        data = get_remote_data(period['date_start'], period['date_end'])
        if not data:
            return False
        # print('Data:', data)
        result1 = set_data(data)
        if not result1:
            return False
        result += result1
    return result

def set_data(data):
    """Write data to database."""

    if not data:
        return False

    if CONN:
        cur = CONN.cursor()
    else:
        return False

    query = """REPLACE INTO data (date_value, country_code,
         confirmed, deaths, stringency_actual, stringency)
         VALUES (%s, %s, %s, %s, %s, %s)
         """
    # Generate query values
    query_vals = []
    for date in data['data']:
        for country in data['data'][date]:
            #print(date, country, data['data'][date][country]['confirmed'])
            query_vals.append((date, country,
                      data['data'][date][country]['confirmed'],
                      data['data'][date][country]['deaths'],
                      data['data'][date][country]['stringency_actual'],
                      data['data'][date][country]['stringency']))
    result = query_exec(cur, query, query_vals, True)
    return result


def query_exec(cursor, query, query_vals, is_many=False):
    """Runs sql query. Commit if success, rollback otherwise."""
    try:
        if is_many:
            cursor.executemany(query, query_vals)
        else:
            cursor.execute(query, query_vals)
    except pymysql.Error as err:
        print("A query exec error occurred:", err.args)
        CONN.rollback()
        return False
    else:
        CONN.commit()
        #print('CONN:', cursor.rowcount)
        return cursor.rowcount

def db_connect():
    """Connect to Database"""

    global CONN
    try:
        CONN = pymysql.connect(host=CONF.get("MYSQL_HOST", ''),
                            port=CONF.get("MYSQL_PORT", 3306),
                            user=CONF["MYSQL_USER"],
                            password=CONF["MYSQL_PASSWORD"],
                            database=CONF["MYSQL_DATABASE"])
    except (pymysql.Error, KeyError):
        # print('Cannot connect to database!')
        logger.error('Cannot connect to database!')
        CONN = False
    else:
        # print('Connected to database')
        logger.info('Connected to database')
        check_db(CONN)

    #CUR = CONN.cursor(pymysql.cursors.DictCursor)
    return CONN


BASE_URL = 'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range'


def main():
    """For test purposes"""

    with open('covid.json') as file:
        data = json.load(file)
    set_data(data)


if __name__ == '__main__':
    main()
