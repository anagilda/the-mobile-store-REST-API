import os
import json
import psycopg2
import psycopg2.extras
import logging
import configparser
import requests
import re
import urllib.request
import time
from selenium import webdriver
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from random import randint
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, '.ini'))

PATH_TO_FILE = os.path.join(BASE_DIR, 'assets/data.json')


GSM_ARENA = 'https://www.gsmarena.com/'
GSM_ARENA_RES = GSM_ARENA + 'results.php3?sAvailabilities=1&FormFactors=1'
FONEARENA_SEARCH = 'https://www.fonearena.com/csearch.php?q='
ALLO = 'https://allo.ua/ru/'
ALLO_SEARCH = ALLO + 'catalogsearch/result/index/?cat=3&q=' # cat=3 only phones


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
        logging.exception(
            str(datetime.now()) 
            + ' - Unable to connect to the database.'
        )

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


def fetch_data(url, limit=1):
    '''
    Fetches data about phones and companies and inserts it to the database(db).
    Finds all links for phones found in a given GSM Arena results page, up to a 
    certain limit.

    Requires: 
        - url (str): must be a link with a search results list of phones.
        - limit (int - optional): maximum number of results added to the db.
    Ensures:
        - Finds a link to each of the phones, gathers more info and then,
          data is gathered and added to db, if not already saved.
    '''
    # conn, cur = connect_db()
    driver = webdriver.Chrome('./chromedriver')

    driver.get(url)

    results = [ 
        res.get_attribute('href') 
        for res in (
            driver
            .find_element_by_class_name('makers')
            .find_elements_by_tag_name('a')
        )
    ]

    num_items = len(results)
    if limit is None or num_items < limit:
        limit = num_items

    for anchor in results[:limit]:
        
        # try:
        phone_info = get_phone_info(anchor, driver)
        print(phone_info)

        # except: 
            # not enough data ?
            # phone already in database ?
            # something else?
            # try next phone

        # else:
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

    driver.quit()
    # close_db(conn, cur)

  
def get_phone_info(url, driver):
    '''
    ---
    
    Requires: 
        - url (str):
        - driver
    Ensures:
        - ... 
    '''
    phone_info = {}

    driver.get(url)

    model = driver.find_element_by_class_name('specs-phone-name-title').text
    # TODO: If model already in database, next phone
    # assertion > exception / return ...

    # else:
    details = get_details(model, driver)

    phone_info['model'] = model
    phone_info['image'] = get_img(model, driver)
    phone_info['manufacturer'] = details['manufacturer']
    phone_info['price'] = float(
        re
        .search('(?<=\$)\d+(\.\d{2})?', details['price(usd)'])
        .group()
    )
    phone_info['info'] = details['description']
    phone_info['specs'] = {}
    phone_info['specs']['body'] = details['body']['dimensions']
    phone_info['specs']['display'] = details['display']['size']
    phone_info['specs']['platform'] = details['platform']['os']
    phone_info['specs']['chipset'] = details['platform']['chipset']
    phone_info['specs']['memory'] = details['memory']['internal']
    phone_info['specs']['camera'] = {
        'main': details['rearcamera'],
        'selfie': details['frontcamera'],
        'features': details['maincamera']['features']
    }
    phone_info['features'] = details['features']['sensors']
    phone_info['battery'] = details['battery']['']
    phone_info['stock'] = randint(1,100)

    return phone_info


def get_details(model, driver):
    '''
    Parses details from a given list of tables and saves it to a dictionary.

    Requires:
        - model (str):
        - driver: a soup object with the table element.
    Ensures:
        - details (dict): information for each th table section from the list.
    '''   
    details = {}
   
    for table in driver.find_elements_by_tag_name('table'):
        section = table.find_element_by_tag_name('th').text
        specs = {}
        for line in table.find_elements_by_tag_name('tr'):
            try:
                name, info = [
                    td.text for td in line.find_elements_by_tag_name('td')
                ]
            except:
                logging.exception(
                    str(datetime.now()) 
                    + ' - Unable to extract info from line in table.'
                )
            else:
                specs[minify_str(name)] = clean_str(info)
        details[minify_str(section)] = specs

    fonearena_specs = [
        'manufacturer', 'price(usd)', 'description', 'rearcamera', 'frontcamera'
    ]

    driver.get(FONEARENA_SEARCH + model.replace(' ', '+'))
    (driver
        .find_element_by_class_name('gsc-resultsbox-visible')
        .find_element_by_partial_link_text('Full Phone Specifications')
        .click()
    )

    summary = driver.find_element_by_id('details')
    labels = summary.find_elements_by_tag_name('label')
    spans = summary.find_elements_by_tag_name('span')

    for header, info in zip(labels, spans):
        section = minify_str(header.text)
        if section in fonearena_specs:
            details[section] = info.text

    highlights = (
        driver
        .find_element_by_class_name('hList')
        .find_elements_by_tag_name("li")
    )

    for h in highlights:
        h = clean_str(h.text)
        if 'front camera' in h.lower():
            details['frontcamera'] =  camera_info(h)
        elif 'rear camera' in h.lower():
            details['rearcamera'] =  camera_info(h)

    return details


def minify_str(string):
    '''
    Cleans a given string, by removing spaces and turning it into lowercase.

    Requires: string (str).
    Ensures: string is returned in lowercase with no spaces.
    '''
    return string.replace(' ', '').lower()


def clean_str(string):
    '''
    Cleans a given string, by removing extra spaces, tabs, newlines and turning
    them into a single space, and deleting leading and trailing white spaces.
    Also removes leading bullets.

    Requires: string (str).
    Ensures: string is returned in with correct spacing.
    '''
    return re.sub('^-', '', re.sub('\s+', ' ', string)).strip()


def camera_info(string):
    '''
    Separates a given string, at the last occurance of 'MP' (megapixels).

    Requires: string (str), with info about a camera.
    Ensures: One string is returned with the information about megapixels only.
    '''
    return re.split('(?<=MP) (?!.*MP.*)', string)[0]


def insert_data(conn, cursor, model, image, manufacturer, price, description, specs, stock):
    '''
    Inserts data about one given phone to the provided database, and also data 
    about the company that manufactures it, if necessary. Phone data will not 
    be added if phone model already exists in the database.

    Requires: 
        - conn: a connection established to the database;
        - cursor: a cursor connected to the database;
        - model (str);
        - image (str);
        - manufacturer (str);
        - price (int);
        - description (str);
        - specs (json) - including information about body, display, platform, 
          chipset, memory, camera (main, selfie, features), battery & features; 
        - stock (int).
    Ensures:
        - data is saved to database.
    '''
    # Check if phone exists in the database

    # TODO: Make this separate to be called before fetching so much info
    query = "SELECT id FROM phones_phone WHERE model='%s';" % model
    cursor.execute(query)
    if not cursor.fetchone():
        # Check if company exists in the database and save its ID
        query = "SELECT id FROM phones_company WHERE name='%s';" % manufacturer
        cursor.execute(query)
        company_key = cursor.fetchone()
        if not company_key:
            # Insert new company to db
            query = """
                INSERT INTO phones_company (name) 
                VALUES ('%s') RETURNING id;
                """ % manufacturer
            cursor.execute(query)
            company_key = cursor.fetchone()
            conn.commit()
            print(
                datetime.now(),
                '- New company added to database (%s)' % (manufacturer)
            )
        company_key = company_key[0]
        
        # Insert new phone to db
        query = """INSERT INTO phones_phone 
            (model, image, manufacturer_id, price, description, specs, stock)
            VALUES ('%s', '%s', %s, %s, '%s', '%s', %s);
            """ % (model, image, company_key, price, description, specs, stock)
        cursor.execute(query)
        conn.commit()
        print(
            datetime.now(), 
            '- New phone added to the database (%s)' % model
        )
    else:
        print(
            datetime.now(), 
            '- Phone already exists in the database (%s)' % model
        )


def get_img(phone, driver):
    '''

    Requires:
    Ensures:
    '''
    # Search page
    search_url = ALLO_SEARCH + phone.replace(' ', '+')
    driver.get(search_url)
    (driver
        .find_element_by_class_name('product-name-container')
        .find_element_by_tag_name('a')
        .click()
    )
    # Phone info page
    driver.find_element_by_class_name('zoomImageMediaTab-main').click()
    img_window = driver.find_element_by_id('zoomerViewPort')
    first_img = img_window.find_elements_by_tag_name("img")[0]
    img_url = first_img.get_attribute("src")

    img_path = os.path.join(BASE_DIR, 'assets/img', minify_str(phone) + '.jpg')
    urllib.request.urlretrieve(img_url, img_path)

    return img_path


def main():
    '''
    Executes the main worker program to fetch data about smartphones and insert 
    it to the database.
    '''
    # readfile(PATH_TO_FILE) # Placeholder data
    fetch_data(GSM_ARENA_RES, 2)


if __name__ == "__main__":
    main()