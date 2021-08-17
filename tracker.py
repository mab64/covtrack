#!/usr/bin/env python3

"""COVID Tracker module"""

'''
CREATE TABLE data (
    date_value DATE, 
    country_code CHAR(3),
    confirmed INT NOT NULL, 
    deaths INT NOT NULL, 
    stringency_actual DECIMAL(5, 2) NOT NULL, 
    stringency DECIMAL(5, 2) NOT NULL,
    PRIMARY KEY (country_code, date_value)
)

'''

import json
import os
import pymysql
import requests

APP_PATH = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(APP_PATH, "conf", "tracker.conf")) as conf_file:
    CONF = json.load(conf_file)

# Connect to MySQL Database
try:
    CONN = pymysql.connect(host=CONF["MYSQL_HOST"], 
                        user=CONF["MYSQL_USER"],
                        passwd=CONF["MYSQL_PASSWD"], 
                        db=CONF["MYSQL_DB"])
except:
    CONN = False

#CUR = CONN.cursor(pymysql.cursors.DictCursor)

BASE_URL = 'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range'

def get_remote_data(date_start, date_end):
    """Receive data from COVID Tracker site."""
    
    req = requests.get('/'.join((BASE_URL, date_start, date_end)))
    if req.status_code == 200:
        return json.loads(req.content)

def get_data(params):
    """Receive data from database, returns processed."""
    
    if CONN:
        cur = CONN.cursor()
    else:
        return False

    print(params, type(params))
    periods = json.loads(params['periods'])
    print(periods, type(periods))
    for period in periods:
        query = """SELECT country_code, SUM(confirmed), SUM(deaths), 
            AVG(stringency_actual), AVG(stringency) FROM data
            WHERE (date_value BETWEEN %s AND %s)
            GROUP BY country_code ORDER BY SUM(stringency)"""
        
        query_vals = (period['date_start'], period['date_end'])
        cur.execute(query, query_vals)
        data = []
        for row in cur.fetchall():
            data.append((row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4])))
        #print(data)
        return data



def update_data(params):
    """Update database from COVID Tracker site."""
    
    print('Params1:', params, type(params), type(params['periods']))
    periods = json.loads(params['periods'])
    print(periods, type(periods))
    result = 0
    for period in periods:
        data = get_remote_data(period['date_start'], period['date_end'])
        if not data:
            return False
        result1 = set_data(data)
        if not result1:
            return False
        result += result1
    return result

def set_data(data):
    """Write data to database."""

    if CONN:
        cur = CONN.cursor()
    else:
        return False

    if not data:
        return    
        
    #query = """INSERT INTO countries (code)
    #    VALUES (%s)
    #    ON DUPLICATE KEY UPDATE name=name"""
    #query_vals = data['countries']
    #query_exec(query, query_vals, True)
    
    #try:
    #    cur.executemany(query, query_vals)
    #    #cur.execute(query, query_vals)
    #except pymysql.Error as err:
    #    print("A query exec error occurred:", err.args)
    #    CONN.rollback()
    #    return False
    #else:
    #    CONN.commit()
    
    i = 0
    query = """REPLACE INTO data (date_value, country_code,
         confirmed, deaths, stringency_actual, stringency)
         VALUES (%s, %s, %s, %s, %s, %s)
         """
        #ON DUPLICATE KEY UPDATE confirmed=confirmed
        
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


def main():
    with open('covid.json') as fp:
        data = json.load(fp)
    set_data(data)

    
if __name__ == '__main__':
    main()
