import os

import logging
import sys
from datetime import date, timedelta

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("collect.log"), logging.StreamHandler()],
)

LATITUDE = 43.2965
LONGITUDE = 5.3698

def fetch_air_quality(start_date, end_date):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"    
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "pm10,pm2_5,nitrogen_dioxide",
        "start_date": start_date,
        "end_date": end_date,
        }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()  # Raise an exception for HTTP errors
    h = response.json()["hourly"]
    return list(zip(h["time"], h["pm10"], h["pm2_5"], h["nitrogen_dioxide"]))

def fetch_weather(start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,wind_speed_10m,wind_direction_10m,precipitation",
        "start_date": start_date,
        "end_date": end_date,                       
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    h = response.json()["hourly"]
    return list(zip(h["time"], h["temperature_2m"], h["wind_speed_10m"],
                    h["wind_direction_10m"], h["precipitation"]))

def save_air_quality(connection, rows):
    sql = """
    INSERT INTO air_quality (measured_at, pm10, pm2_5, no2)
    VALUES %s
    ON CONFLICT (measured_at) DO NOTHING;
    """
    with connection.cursor() as cursor:
        execute_values(cursor, sql, rows)
    connection.commit()

def save_weather(connection, rows):
    sql = """
    INSERT INTO weather (measured_at, temperature, wind_speed, wind_direction, precipitation)
    VALUES %s
    ON CONFLICT (measured_at) DO NOTHING;
    """
    with connection.cursor() as cursor:
        execute_values(cursor, sql, rows)
    connection.commit()

def main():
    yesterday = date.today() - timedelta(days=1)
    if len(sys.argv) > 1 and sys.argv[1] == "history":
        start_date = yesterday - timedelta(days=365)
    else:
        start_date = yesterday

    try:
        air = fetch_air_quality(start_date, yesterday)
        weather = fetch_weather(start_date, yesterday)

        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        save_air_quality(connection, air)
        save_weather(connection, weather)
        connection.close()

        logging.info(f"Saved {len(air)} air rows and {len(weather)} weather rows "
                     f"from {start_date} to {yesterday}")
    except Exception as error:
        logging.error(f"Collection failed: {error}")
        raise


if __name__ == "__main__":
    main()