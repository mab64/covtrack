#!/usr/bin/env python3

"""COVID Tracker module"""

import json
import os
import logging
# from pickle import GLOBAL
import requests

APP_PATH = os.path.dirname(os.path.abspath(__file__))

CONF = {}  # config parameters dictionary
# Load database connection parameters from config file if exists.
if os.path.isfile('conf/tracker.conf'):
    with open(os.path.join(APP_PATH, "conf", "tracker.conf")) as conf_file:
        CONF = json.load(conf_file)

if os.getenv('FLASK_DEBUG') == '1' or \
        os.getenv('FLASK_ENV', '').lower() == 'development':
    CONF["LOG_LEVEL"] = logging.DEBUG
else:
    CONF["LOG_LEVEL"] = logging.INFO
# print('CONF["LOG_LEVEL"]:', CONF["LOG_LEVEL"])

logging.basicConfig(
    format='%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=CONF["LOG_LEVEL"]
    )
logger = logging.getLogger(__name__)

# Redefine connection parameters from environment if exists.
if os.getenv('DBMS'):
    CONF["DBMS"] = os.getenv('DBMS')
if os.getenv('DBMS_HOST'):
    CONF["DBMS_HOST"] = os.getenv('DBMS_HOST')
if os.getenv('DBMS_PORT'):
    CONF["DBMS_PORT"] = int(os.getenv('DBMS_PORT'))
if os.getenv('DBMS_USER'):
    CONF["DBMS_USER"] = os.getenv('DBMS_USER')
if os.getenv('DBMS_PASSWORD'):
    CONF["DBMS_PASSWORD"] = os.getenv('DBMS_PASSWORD')
if os.getenv('DBMS_DATABASE'):
    CONF["DBMS_DATABASE"] = os.getenv('DBMS_DATABASE')

logger.debug('CONF: %s', CONF)  # print configuration parameters
if not (
        CONF.get("DBMS", "") and
        CONF.get("DBMS_DATABASE", "") and 
        CONF.get("DBMS_USER", "") and
        CONF.get("DBMS_PASSWORD","")
       ):
    logger.error('Database connection parameters invalid!')

if CONF["DBMS"] == "mysql":
    import pymysql
elif CONF["DBMS"] == "postgresql":
    import psycopg2
    import psycopg2.extras

def check_db():
    """Connects to database and checks structure."""

    conn = db_connect()
    if conn:
        cur = conn.cursor()
    else:
        return False

    query = '''
        CREATE TABLE IF NOT EXISTS data (
            date_value      DATE,
            country_code    CHAR(3),
            confirmed       INT,
            deaths          INT ,
            stringency_actual NUMERIC(5, 2),
            stringency      NUMERIC(5, 2),
            PRIMARY KEY (country_code, date_value)
        );
        '''
    result = cur.execute(query)
    logger.debug(f"Result: {result}")
    # query  = '''EXPLAIN data;'''
    # result = cur.execute(query)
    # print('result:', result)
    conn.close()

    return True


def get_data(periods):
    """Receive data from database, returns processed."""

    conn = db_connect()
    if conn:
        cur = conn.cursor()
    else:
        return False

    for period in periods:
        query = """
            SELECT date_value, country_code, confirmed,
                   deaths, stringency FROM data
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
            data.append((str(row[0]), row[1], row[2], row[3], row[4]))
        # print(data)
        headers = ['Date', 'Country', 'Confirmed', 'Deaths', 'Stringency']
        result = [headers, data]
        conn.close()

        return result


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

def get_remote_data(date_start, date_end):
    """Receive data from COVID Tracker site."""

    request = requests.get('/'.join((BASE_URL, date_start, date_end)))
    if request.status_code == 200:
        data = json.loads(request.content)
        if data.get('status') == 'error':
            return False
        return data
    return False


def set_data(data):
    """Write data to database."""

    if not data:
        return False

    conn = db_connect()
    if conn:
        cur = conn.cursor()
    else:
        return False

    if CONF["DBMS"] == "mysql":
       query = """REPLACE INTO data (date_value, country_code,
            confirmed, deaths, stringency_actual, stringency)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
    elif CONF["DBMS"] == "postgresql":
       query = """INSERT INTO data (date_value, country_code,
            confirmed, deaths, stringency_actual, stringency)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT 
            DO NOTHING
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
    result = query_exec(conn, cur, query, query_vals, is_many=True)
    return result


def query_exec(connection, cursor, query, query_vals, is_many=False):
    """Runs sql query. Commit if success, rollback otherwise."""
 
    if CONF["DBMS"] == "mysql":
        try:
            if is_many:
                cursor.executemany(query, query_vals)
            else:
                cursor.execute(query, query_vals)
        except pymysql.Error as err:
            print("A query exec error occurred:", err.args)
            connection.rollback()
            return False
        else:
            connection.commit()
            #print('CONN:', cursor.rowcount)
            return cursor.rowcount
    elif CONF["DBMS"] == "postgresql":
        try:
            if is_many:
                # logger.info(query, query_vals)
                cursor.executemany(query, query_vals)
                # psycopg2.extras.execute_batch(cursor, query, query_vals)
            else:
                cursor.execute(query, query_vals)
        except (psycopg2.Error) as err:
            logger.error(f'A query exec error occurred: {err}')
            connection.rollback()
            return False
        else:
            connection.commit()
            #print('CONN:', cursor.rowcount)
            return cursor.rowcount




def db_connect():
    """Connect to Database"""

    conn = False
    if CONF["DBMS"] == "mysql":
        try:
            conn = pymysql.connect(host=CONF.get("DBMS_HOST", ''),
                                   port=CONF.get("DBMS_PORT", 3306),
                                   user=CONF["DBMS_USER"],
                                   password=CONF["DBMS_PASSWORD"],
                                   database=CONF["DBMS_DATABASE"])
        except (pymysql.Error, KeyError) as err:
            logger.error(f'Cannot connect to database!: {err}')
        else:
            logger.info('Connected to database')
            # check_db(CONN)

        #CUR = CONN.cursor(pymysql.cursors.DictCursor)
    elif CONF["DBMS"] == "postgresql":
        try:
            conn = psycopg2.connect(
                    dbname=CONF["DBMS_DATABASE"], 
                    user=CONF["DBMS_USER"], 
                    password=CONF["DBMS_PASSWORD"]
                    )
        except (psycopg2.Error, KeyError) as err:
            logger.error(f'Cannot connect to database!: {err}')
        else:
            logger.info('Connected to database')

    return conn


def connect_pgsql():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if check_db():
    logger.debug('Database check OK.')
else:
    logger.info('Database check Failed.')

BASE_URL = 'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range'


def main():
    """For test purposes"""

    with open('covid.json') as file:
        data = json.load(file)
    set_data(data)


if __name__ == '__main__':
    main()
