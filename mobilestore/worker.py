import os
import json
import requests
import psycopg2
import psycopg2.extras
import logging
import configparser
from random import randint
from datetime import datetime


base_dir = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(base_dir, '.ini'))

path_to_file = os.path.join(base_dir, 'assets/data.json')


def readfile(filepath):
    ''' 
    Reads smartphone data from file.
    
    Requires: 
        - filepath (string): path to a JSON file.
    Ensures:
        - data is parsed and added to database, if not already saved.
    '''
    try:
        conn = psycopg2.connect(
            dbname= config['DB']['NAME'], \
            user= config['DB']['USER'], \
            password= config['DB']['PASSWORD'],\
            host= config['DB']['HOST'], \
            port= config['DB']['PORT'] \
            )
        print('Successful connection to DB.')

    except:
        print('Unable to connect to the database.')
        logging.exception(datetime.now(), 'Unable to connect to the database.')
        return

    else:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    with open(filepath, 'r') as file:
        data = json.load(file)

        for phone in data:
            model = phone['model']
            image = phone['img']
            manufacturer = phone['company']
            price = phone['price']
            description = phone['info'].replace("'", "''")
            specs = json.dumps(phone['specs'])
            stock = randint(1,100)

            insert_data(conn, cur, \
                model, image, manufacturer, price, description, specs, stock)

    cur.close()
    conn.close()


def fetch_data():
    '''

    Requires: 
        - ...
    Ensures:
        - ...
    '''
    # url = ''
    # res = requests.get(url).json()

    # model = res['phone']['name']

    # insert_data(cur, model, image, manufacturer, price, description, specs, stock)

    
def insert_data(conn, cursor, model, image, manufacturer, price, description, specs, stock):
    '''
    Inserts data about one given phone to the provided database, and also data about the 
    company that manufactures it, if necessary.

    Requires: 
        - conn: a connection established to the database;
        - cursor: a cursor connected to the database;
        - model (str);
        - image (str);
        - manufacturer (str);
        - price (int);
        - description (str);
        - specs (json); 
        - stock (int).
    Ensures:
        - data is saved to database.
    '''
    # Check if phone exists in the database
    query = "SELECT id FROM phones_phone WHERE model='%s' ;" % model
    cursor.execute(query)
    if not cursor.fetchone():
        # Check if company exists in the database
        query = "SELECT id FROM phones_company WHERE name='%s' ;"  % manufacturer
        cursor.execute(query)
        company_key = cursor.fetchone()
        if not company_key:
            # Insert new company to db
            query = "INSERT INTO phones_company(name) VALUES ('%s') RETURNING id;" % manufacturer
            cursor.execute(query)
            company_key = cursor.fetchone()
            conn.commit()
            print(datetime.now(),'- New company added to database (%s)' % (manufacturer) )
        
        # Insert new phone to db
        company_key = company_key[0]

        query = """INSERT INTO phones_phone
                (model, image, manufacturer_id, price, description, specs, stock)
                VALUES ('%s', '%s', %s, %s, '%s', '%s', %s);""" \
                % (model, image, company_key, price, description, specs, stock)
        cursor.execute(query)
        conn.commit()
        print(datetime.now(), '- New phone added to the database (%s)' % model)
    else:
        print(datetime.now(), '- Phone already exists in the database (%s)' % model)
       

def main():
    '''
    Executes the main worker program to fetch data and insert it to the database.
    '''

    readfile(path_to_file)
    # fetch_data()


if __name__ == "__main__":
    main()