import os
import json
import psycopg2
import psycopg2.extras
import logging
import configparser
import re
import urllib.request
from selenium import webdriver
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


class MyDatabase(object):
    ''' A PostgreSQL database connection. '''

    def __init__(self):
        '''
        Initiates a connection to the database.

        Requires:
            - self: an object of the MyDatabase class.
        Ensures:
            Saves a newly created connection details to the object:
            - _conn: a connection established to the database;
            - _cursor: a cursor connected to the database.
            If connection is unsuccessful, both values will be None.
        '''
        try:
            self._conn = psycopg2.connect(
                dbname = config['DB']['NAME'], 
                user = config['DB']['USER'], 
                password = config['DB']['PASSWORD'],
                host = config['DB']['HOST'], 
                port = config['DB']['PORT'] 
            )
            logging.info('Successful connection to DB.')

        except:
            self._conn = None
            self._cursor = None
            logging.exception(
                str(datetime.now()) 
                + ' - Unable to connect to the database.'
            )

        else:
            self._cursor = self._conn.cursor(
                cursor_factory = psycopg2.extras.DictCursor
            )

    def query(self, query, params):
        '''
        Sends a query to the database and executes it.

        Requires:
            - self: an object of the MyDatabase class;
            - query (str): SQL query to be executed; 
            - params (tuple): parameters specific to the parameterized query 
            provided.
        Ensures:
            Returns a database response.
        '''
        return self._cursor.execute(query, params)

    def fetch_one(self):
        '''
        Iterates the next result from a previous query saved in the cursor.

        Requires:
            - self: an object of the MyDatabase class, after a query has been
            executed.
        Ensures:
            Returns the next item from the response saved in the cursor.
        '''
        return self._cursor.fetchone()

    def commit(self):
        '''
        Makes sure that changes are applied to database.

        Requires:
            - self: an object of the MyDatabase class.
        Ensures:
            Previous changes are permanently applied to the database.
        '''
        self._conn.commit()

    def __del__(self):
        '''
        Closes a connection to the database when the object falls out of scope.

        Requires:
            - self: an object of the MyDatabase class.
        Ensures:
            Safely closes a connection to the database.
        '''
        self._cursor.close()
        self._conn.close()
        logging.info('Connection to db terminated safely.')

# def connect_db():
#     '''
#     Creates a connection to the database.

#     Requires:
#         Nothing.
#     Ensures:
#         Returns a dictionary with the newly created connection details:
#         - conn: a connection established to the database;
#         - cursor: a cursor connected to the database.
#     '''
#     try:
#         conn = psycopg2.connect(
#             dbname = config['DB']['NAME'], 
#             user = config['DB']['USER'], 
#             password = config['DB']['PASSWORD'],
#             host = config['DB']['HOST'], 
#             port = config['DB']['PORT'] 
#         )
#         logging.info('Successful connection to DB.')

#     except:
#         logging.exception(
#             str(datetime.now()) 
#             + ' - Unable to connect to the database.'
#         )

#     else:
#         cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
#         return { 'conn': conn, 'cursor': cur }


# def close_db(con_details):
#     '''
#     Closes a connection to the database.

#     Requires:
#         con_details, a dictionary with:
#         - conn: a connection established to the database;
#         - cursor: a cursor connected to the database.
#     Ensures:
#         Safely closes a connection to the database.
#     '''
#     con_details['cursor'].close()
#     con_details['conn'].close()
#     logging.info('Connection to db terminated safely.')


def readfile(filepath):
    ''' 
    Reads smartphone data from a given JSON file.
    
    Requires: 
        - filepath (str): path to a JSON file with information about phones.
    Ensures:
        - data is parsed and added to database, if not already saved.
    '''

    db_connection = MyDatabase()

    with open(filepath, 'r') as file:
        data = json.load(file)

        for phone in data:
            details = {}
            details['model'] = phone['model']
            details['image'] = phone['img']
            details['manufacturer'] = phone['company']
            details['price'] = phone['price']
            details['description'] = phone['info'].replace("'", "''")
            details['specs'] = json.dumps(phone['specs'])
            details['stock'] = randint(1,100)

            insert_data(db_connection, details)


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
    db_connection = MyDatabase()
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
        
        try:
            phone_info = get_phone_info(anchor, driver)
            assert(isinstance(phone_info, dict)) 

        except AssertionError: 
            logging.warning('Phone %s already in the database.' % phone_info)

        except Exception:
            logging.exception(
                str(datetime.now()) 
                + ' - Unable to gather phone information (url: %s).' % anchor
            )

        # else:
        #    insert_data(db_connection, phone_info)     

    driver.quit()

  
def get_phone_info(url, driver):
    '''
    ---
    
    Requires: 
        - url (str):
        - driver
    Ensures:
        - ... 
    '''
    driver.get(url)

    model = driver.find_element_by_class_name('specs-phone-name-title').text
    
    # If model is already in database, skip it
    query = "SELECT id FROM phones_phone WHERE model=%s;" 
    db_con.query(query, (phone['model'],))
    if db_con.fetch_one() is not None:
        return model 

    details = get_details(model, driver)
    phone_info = {}
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


def insert_data(db_con, phone):
    '''
    Inserts data about one given phone to the provided database, and also data 
    about the company that manufactures it, if necessary. Phone data will not 
    be added if phone model already exists in the database.

    Requires:
        - db_con (obj): a MyDatabase object.
        - phone, a dictionary with:
            model (str);
            image (str);
            manufacturer (str);
            price (int);
            description (str);
            specs (json) - including information about body, display, platform, 
            chipset, memory, camera(main, selfie, features), battery & features;
            stock (int).
    Ensures:
        - data is saved to database.
    '''
   
    if not cursor.fetchone():
        # Check if company exists in the database and save its ID
        query = """
            SELECT id 
            FROM phones_company 
            WHERE name='%s';
            """ % phone['manufacturer']
        cursor.execute(query)
        company_key = cursor.fetchone()
        if not company_key:
            # Insert new company to db
            query = """
                INSERT INTO phones_company (name) 
                VALUES ('%s') RETURNING id;
                """ % phone['manufacturer']
            cursor.execute(query)
            company_key = cursor.fetchone()
            conn.commit()
            logging.info(
                datetime.now(),
                '- New company added to database (%s)' % phone['manufacturer']
            )
        company_key = company_key[0]
        
        # Insert new phone to db
        query = """INSERT INTO phones_phone 
            (model, image, manufacturer_id, price, description, specs, stock)
            VALUES ('%s', '%s', %s, %s, '%s', '%s', %s);
            """ % (phone['model'], phone['image'], company_key, phone['price'],
            phone['description'], phone['specs'], phone['stock'])
        cursor.execute(query)
        conn.commit()
        logging.info(
            datetime.now(), 
            '- New phone added to the database (%s)' % phone['model']
        )
    else:
        logging.info(
            datetime.now(), 
            '- Phone already exists in the database (%s)' % phone['model']
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
    logging.basicConfig(filename='debug.log',level=logging.DEBUG)
    # TODO: change logging format
    readfile(PATH_TO_FILE) # Placeholder data
    # fetch_data(GSM_ARENA_RES, 2)


if __name__ == "__main__":
    main()