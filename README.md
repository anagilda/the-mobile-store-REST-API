# The Mobile Store - REST API

REST API to serve information about mobile phones displayed in the project [The Mobile Store](https://github.com/nick-rudenko/the-mobile-store).

## Instructions

#### Using the API:

*Coming soon!*

#### Running the project locally:

*Note: you must have Python and pipenv installed.*

*Note: Verify [important settings](##importantsettings) section first.*

1. Open the terminal in the project directory.
2. Run `pipenv install` to create the environment and install dependencies.
3. Open the server (usually at `http://localhost:8000/`).

Run `exit` to deactivate the environment.

## Important settings

#### Database:

1. Make sure you set up the database connection settings. 

    Keep in mind that sensitive information should not be made public - protect your data. For this, you can save your secret information in a configuration file (`.ini`) similar to the exemplified in `example.ini`.

    This project uses a PostgreSQL database. You can edit the config file and the `DATABASES` variable in the `settings.py` file to set your own or to change it to your preferred type of database. 

    If you are not sure how to do this, you can simply use the Django default (sqlite3) by using the following code on the *mobilestore/mobilestore/settings.py* file:

    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    ```

2. In the terminal run:
    ```
    python manage.py makemigrations
    python manage.py migrate 
    ```