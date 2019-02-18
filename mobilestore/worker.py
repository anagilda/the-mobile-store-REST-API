import os
import json
import psycopg2
import psycopg2.extras
import logging
import configparser
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from random import randint
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, '.ini'))

PATH_TO_FILE = os.path.join(BASE_DIR, 'assets/data.json')

GSM_ARENA = 'https://www.gsmarena.com/'
GSM_ARENA_RES = GSM_ARENA + 'results.php3?sFormFactors=1' # results page
ALLO = 'https://allo.ua/'


def connect_db():
    '''
    Creates a connection to the database.

    Requires:
        Nothing.
    Ensures:
        - conn: a connection established to the database;
        - cursor: a cursor connected to the database.
    '''
    try:
        conn = psycopg2.connect(
            dbname = config['DB']['NAME'], 
            user = config['DB']['USER'], 
            password = config['DB']['PASSWORD'],
            host = config['DB']['HOST'], 
            port = config['DB']['PORT'] 
        )
        print('Successful connection to DB.')

    except:
        logging.exception(str(datetime.now()) + ' - Unable to connect to the database.')

    else:
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        return conn, cur


def close_db(conn, cur):
    '''
    Closes a connection to the database.

    Requires:
        - conn: a connection established to the database;
        - cursor: a cursor connected to the database.
    Ensures:
        Safely closes a connection to the database.
    '''
    cur.close()
    conn.close()
    print('Connection to db terminated safely.')


def readfile(filepath):
    ''' 
    Reads smartphone data from a given JSON file.
    
    Requires: 
        - filepath (str): path to a JSON file.
    Ensures:
        - data is parsed and added to database, if not already saved.
    '''

    conn, cur = connect_db()

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

    close_db(conn, cur)


def fetch_data(url, base_url, limit=1):
    '''
    Fetches data about phones and companies and inserts it to the database.
    Finds all links in a page (inside a div with a given class, in a given type
    of list).

    Requires: 
        - url (str): must be a link with a search results list of phones.
        - base_url (str): base url from which to create links.
        - limit (int - optional): maximum number of results added to the database.
    Ensures:
        - Finds a link to each of the phones, gathers more info and then,
          data is gathered and added to database, if not already saved.
    '''

    # conn, cur = connect_db()

    page_source = requests.get(url)
    html = page_source.text
    soup = BeautifulSoup(html, 'html.parser')

    results = soup.find('div', class_ = 'makers')
    
    list_items = results.find_all('a')
    num_items = len(list_items)
    if limit is None or num_items < limit:
        limit = num_items

    for anchor in list_items[:limit]:
        phone_href = base_url + anchor.get('href')
        
        phone_info = get_phone_info(phone_href)
        
        print(phone_info)

        # insert_data(
        #    cur, 
        #    image,
        #    phone_info['model'],
        #    phone_info['manufacturer'],
        #    phone_info['price'],
        #    phone_info['description'],
        #    phone_info['specs'],
        #    phone_info['stock']
        # )

    # close_db(conn, cur)

    
def get_phone_info(gsm_url):
    '''
    ---
    
    Requires: 
        - ...
    Ensures:
        - ... 
    '''
    phone_info = {}


    page_source = requests.get(gsm_url)
    html = page_source.text
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('h1', class_='specs-phone-name-title')
    phone_info['model'] = title.string

    phone_info['specs'] = {}
    details = get_details(soup.find('div', id='specs-list'))

    phone_info['specs']['body'] = details['body']['dimensions']
    phone_info['specs']['display'] = details['display']['type']
    phone_info['specs']['platform'] = details['platform']['os']
    phone_info['specs']['chipset'] = details['platform']['chipset']
    phone_info['specs']['memory'] = details['memory']['internal']
    # phone_info['specs']['camera'] = {
    #     'main': details['main camera'][0],
    #     'selfie': details['selfie camera'][0],
    #     'features': details['main camera']['features']
    # }

    # model, image, manufacturer, price, description, specs, stock
    
    return phone_info


def get_details(souplist):
    '''
    Parses details from a given list of tables and saves it to a dictionary.

    Requires:
        - souplist: a soup object with the table element.
    Ensures:
        - details (dict): information for each th table section from the list.
    '''
    details = {}
    
    for table in souplist.findAll("table"):
        section = table.find("th").text.lower()
        specs = {}
        for line in table.findAll("tr"):
            name, info = [td.string for td in line.findAll("td")]
            name = name.lower()
            specs[name] = info
        details[section] = specs  

    return details


def insert_data(conn, cursor, model, image, manufacturer, price, description, specs, stock):
    '''
    Inserts data about one given phone to the provided database, and also data about the 
    company that manufactures it, if necessary. Phone data will not be added if phone model
    already exists in the database.

    Requires: 
        - conn: a connection established to the database;
        - cursor: a cursor connected to the database;
        - model (str);
        - image (str);
        - manufacturer (str);
        - price (int);
        - description (str);
        - specs (json) - including information about body, display, platform, chipset,
          memory, camera (main, selfie, featues), battery and features; 
        - stock (int).
    Ensures:
        - data is saved to database.
    '''
    # Check if phone exists in the database
    query = "SELECT id FROM phones_phone WHERE model='%s' ;" % model
    cursor.execute(query)
    if not cursor.fetchone():
        # Check if company exists in the database and save its ID
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
        company_key = company_key[0]
        
        # Insert new phone to db
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
    # readfile(PATH_TO_FILE) # PLaceholder data
    
    fetch_data(GSM_ARENA_RES, GSM_ARENA, 20) # Scrape the most popular phones


if __name__ == "__main__":
    main()