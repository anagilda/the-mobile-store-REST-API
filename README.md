# The Mobile Store - REST API

REST API to serve information about mobile phones displayed in the project [The Mobile Store](https://github.com/nick-rudenko/the-mobile-store).

## Instructions

### Using the API:
*Note: [base_url] represents either a [deployed app url](https://the-mobile-store.herokuapp.com/) or a [localhost url](http://localhost:8000/).*

*Note: { } = required, [ ] = optional.*

#### GET /api/phones/[limit][offset]
Phone list - retrieves a list of phones (id, model, image and price).

Parameters:
* limit(int): maximum number of results returned (default=8, maximum=20).
* offset(int): number of results skipped (default=0).

Example usage:
* [[base_url]/api/phones/](https://the-mobile-store.herokuapp.com/api/phones)
* [[base_url]/api/phones/?limit=2&offset=1](https://the-mobile-store.herokuapp.com/api/phones/?limit=2&offset=1)

Example output:

```json
[
    {
        "id": 1,
        "model": "Google Pixel 3",
        "image": "http://127.0.0.1:8000/media/img/phone_1-min.jpg",
        "price": "799.00"
    },
    {
        "id": 2,
        "model": "Samsung Note 9",
        "image": "http://127.0.0.1:8000/media/img/phone_2-min.jpg",
        "price": "999.00"
    }
]
```

#### GET /api/phones/{id}

Phone detail - retrieves the full details of a phone with the given id (id, manufacturer, model, image, price, description, specs and stock).

Parameters:
* id(int): phone id.

Example usage:
* [[base_url]/api/phones/1/](https://the-mobile-store.herokuapp.com/api/phones/1/)

Example output:

```json
{
    "id": 1,
    "manufacturer": "Google Inc.",
    "model": "Google Pixel 3",
    "image": "http://127.0.0.1:8000/media/img/phone_1-min.jpg",
    "price": "799.00",
    "description": "Staying too far from your loved ones? Video call them for hours on end. The weather is romantic? Listen to your favourite playlists all day long. Don’t want to go out this weekend? Then binge watch your favourite series on the Internet. The Pixel 3 ensures that there’s never a dull moment, all thanks to its powerful battery, impressive cameras and its expansive bezel-less display.",
    "specs": {
        "body": "145.6 x 68.2 x 7.9 mm (5.73 x 2.69 x 0.31 in)",
        "camera": {
            "main": "12.2 MP (wide) dual pixel",
            "selfie": "8 MP (ultrawide), no AF",
            "features": "Dual-LED flash, Auto-HDR, panorama"
        },
        "memory": "64/128 GB, 4 GB RAM",
        "battery": "Non-removable Li-Po 2915 mAh battery",
        "chipset": "Qualcomm SDM845 Snapdragon 845 (10 nm)",
        "display": "5.5 inches, 1080 x 2160 pixels, 18:9 ratio (~443 ppi density)",
        "features": "NFC, USB 3.1 Type-C 1.0, fingerprint (rear-mounted), fast battery charging, Gorilla Glass 5, aluminum frame, IP68 dust/water resistant, Always-on display, HDR",
        "platform": "OS Android 9.0 (Pie)"
    },
    "stock": 49
}
```

### Running the project locally:

*Note: you must have Python 3, pip and pipenv installed.*

**Initial setup:**

1. Open the terminal in the project directory.
2. Create the environment and install dependencies.
    ```shell
    pipenv install
    ```
3. Verify the [database settings](####databasesettings), and then make database migrations:
    ```shell
    cd mobilestore
    python manage.py makemigrations
    python manage.py migrate 
    ```
4. Run the `worker.py` file to insert data to the database. 

    *Note: You can either run the scraper as it is, or you can  enter placeholder data instead. To do so, edit the `main()` function in this file by commenting/uncommenting what is needed.*
    ```shell
    python worker.py
    ```
3. Run `exit` to deactivate the environment.  

**Running the project:**
1. Open the terminal in the project directory.
2. Activate the virtual environment:
    ```shell
    pipenv shell
    ```
2. Run and open the server (usually at `http://localhost:8000/`).
    ```shell
    cd mobilestore
    python manage.py runserver
    ```
2. Use the API!
3. Run `exit` to deactivate the environment.

#### Database settings

Make sure you set up the database connection settings. 

Keep in mind that sensitive information should not be made public - protect your data. For this, you can save your secret information in a configuration file (named `.ini`) similar to the exemplified in `example.ini`.

This project uses a PostgreSQL database. You can edit the example config file (`example.ini`) with your own credentials and rename it to `.ini`. 
