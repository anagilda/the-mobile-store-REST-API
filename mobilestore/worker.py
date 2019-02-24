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

FONEARENA = 'https://www.fonearena.com/'
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


def fetch_data(url, base_url, limit=1):
    '''
    Fetches data about phones and companies and inserts it to the database(db).
    Finds all links in a page (inside a div with a given class, in a given type
    of list).

    Requires: 
        - url (str): must be a link with a search results list of phones.
        - base_url (str): base url from which to create links.
        - limit (int - optional): maximum number of results added to the db.
    Ensures:
        - Finds a link to each of the phones, gathers more info and then,
          data is gathered and added to db, if not already saved.
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

    
def get_soup(url):
    '''
    ---
    
    Requires: 
        - ...
    Ensures:
        - ... 
    '''
    page_source = requests.get(url)
    html = page_source.text
    return BeautifulSoup(html, 'html.parser')


def get_phone_info(gsm_url):
    '''
    ---
    
    Requires: 
        - ...
    Ensures:
        - ... 
    '''
    phone_info = {}

    soup = get_soup(gsm_url)

    details = get_details(soup)

    phone_info['model'] = details['phone']
    phone_info['manufacturer'] = details['manufacturer']
    phone_info['price'] = float(
        re.search('(?<=\$)\d+(\.\d{2})?', details['price(usd)'])
          .group()
    )
    
    # TODO: Info works but can be improved
    phone_info['info'] = details['description']
    
    phone_info['specs'] = {}
    phone_info['specs']['body'] = details['built']['dimensions']
    phone_info['specs']['display'] = details['display']['size']
    phone_info['specs']['platform'] = details['software']['operatingsystem']
    phone_info['specs']['chipset'] = details['chipset']
    phone_info['specs']['memory'] = details['memory']['inbuilt']

    phone_info['specs']['camera'] = {
        'main': details['rearcamera'],
        'selfie': details['frontcamera']
        # ,
        # 'features': details['main camera']['features']
    }

    phone_info['features'] = details['featuresS']

    phone_info['battery'] = "%s %s" % (
        details['battery']['type'],
        details['battery']['capacity']
    )
    
    # TODO
    # image = get_image(phone_info['model'])
    
    phone_info['stock'] = randint(1,100)

    print(phone_info)
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
    
    summary = souplist.find('div', id='details')
    labels = summary.find_all('label')
    spans = summary.find_all('span')

    for header, info in zip(labels, spans):
        section = minify_str(header.string)
        details[section] = info.text

    highlights = souplist.find('div', class_='hList').find_all("li")
    feats = []
    for h in highlights:
        h = clean_str(h.text)
        
        if 'processor' in h.lower():
            details['chipset'] =  h
        elif 'rear camera' in h.lower():
            details['rearcamera'] =  h
        elif 'front camera' in h.lower():
            details['frontcamera'] =  h
        else:
            conditions = [
                'battery' not in h.lower(),
                'RAM' not in h,
                'display' not in h.lower()
            ]
            if all(conditions):
                feats.append(h)
    
    details['features'] = ', '.join(feats)

    h2s = souplist.find_all('h2')
    sections = souplist.find_all(id=re.compile('^section_'))
        
    for header, info in zip(h2s, sections):
        title = minify_str(header.string)
       
        specs = {}
        for line in info.findAll("tr"):
            name, info = [td.string for td in line.findAll("td")]
            specs[minify_str(name)] = clean_str(info)
    
        details[title] = specs 

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
    Ensures: 2 strings are returned.
    '''
    return re.split('(?<=MP) (?!.*MP.*)', string)


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



def get_img(phone):
    '''

    Requires:
    Ensures:
    '''
    search_url = ALLO_SEARCH + phone.replace(' ', '+')
    results = get_soup(search_url)

    first_result = results.find('div', class_='product-name-container')
    anchor = first_result.find('a').get('href')
    

    # session = HTMLSession()
    # r = session.get('https:' + anchor)
    # r.html.render(timeout=0, script="""
    #     () => {
    #         _gaq.push(['_trackEvent', 'Card', 'action', 'big-photo']);
    #         // document.getElementById("zoomWindow").style.display = "block";
    #         return false;
    #     }
    # """)
    
    # zzz = r.html.find('#zoomWindow', first=True)
    # session.close()

    url = 'https:' + anchor

    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    time.sleep(5) # Make sure the website loads completely (javascript included)
    driver.find_element_by_class_name('zoomImageMediaTab-main').click()

    img_window = driver.find_element_by_id('zoomerViewPort')
    first_img = img_window.find_elements_by_tag_name("img")[0]
    url = first_img.get_attribute("src")
        
    driver.quit()

    img_path = os.path.join(BASE_DIR, 'assets/img', phone + '.jpg')
    urllib.request.urlretrieve(url, img_path)


def patch_pyppeteer():
    import pyppeteer.connection
    original_method = pyppeteer.connection.websockets.client.connect

    def new_method(*args, **kwargs):
        kwargs['ping_interval'] = None
        kwargs['ping_timeout'] = None
        return original_method(*args, **kwargs)

    pyppeteer.connection.websockets.client.connect = new_method



def main():
    '''
    Executes the main worker program to fetch data and insert it to the database.
    '''
    patch_pyppeteer()
    # readfile(PATH_TO_FILE) # PLaceholder data
    
    # get_phone_info(FONEARENA + 'xiaomi-mi-9_9166.html')
    get_img('Xiaomi Mi 9')


if __name__ == "__main__":
    main()