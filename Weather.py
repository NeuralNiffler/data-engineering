import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
from pymongo import MongoClient
import requests

load_dotenv()

client = MongoClient(
    host=os.environ["WEATHER_HOST"],
    username=os.environ["WEATHER_DB_USER"],
    password=os.environ["WEATHER_DB_PW"],
    port=int(os.environ["WEATHER_DB_PORT"]),
    authSource="weather",
)

db = client[os.environ["WEATHER_DB_NAME"]]

def exec() -> DataFrame:
    df = pd.DataFrame(list(db.list_collections()))

    return df

def complex_query() -> DataFrame:


    return None

def api_status() -> DataFrame:
    baseURL = f"http://{os.environ["WEATHER_HOST"]}:{os.environ["WEATHER_API_PORT"]}/api/status"
    response = requests.get(baseURL, timeout=10)
    response.raise_for_status()
    data = response.json()

    return pd.json_normalize(data)