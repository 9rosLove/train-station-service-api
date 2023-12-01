# 🚅 Train station API

API service for train station management written on DRF

## Install PostgreSQL and Create a Database
You will need to have PostgreSQL installed, and create a database for the API.

## 🔧 Installing using GitHub
1. Clone the repository from GitHub:
    ```bash
    git clone htthps://github.com/9rosLove/train-station-apservice-api.git
    cd train-station-apservice-api
    ```

2. Set up a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Install PostgreSQL and create a local database if you want to run it locally.
6. Set the environment variables for your database connection and secret key:

    ```bash
    set DB_HOST=<your db hostname>
    set DB_NAME=<your db name>
    set DB_USER=<your db username>
    set DB_PASSWORD=<your db password>
    set DB_SECREY_KEY=<your secret key>
    ```
7. Migrate the database:
    ```bash
    python manage.py migrate
    ```
8. Start the development server:
    ```bash
    python manage.py runserver
    ```
## 🐋 Run with docker
1. Make sure Docker is installed.
2. Build the Docker containers:
    ```bash
    docker-compose build
    ```
3. Run the Docker containers:
    ```bash
    docker-compose up
    ```
## 🔑 Getting access
- create user via /api/user/register/
- get access token via /api/user/token/

## ⭐ Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing orders and tickets
- Creating busses
- Creating stations with location
- Adding journeys
- Filtering journeys and orders

## 📊 Database Schema
![DB_Schema](https://github.com/9rosLove/train-station-service-api/blob/50d0557320853adc8da5faeaf607a6abbaa45d7d/db_schema.jpg)

