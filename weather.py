import os
from enum import StrEnum
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
from pymongo import MongoClient
import logging

import api

log = logging.getLogger(__name__)
load_dotenv()

SOURCE = "weather"

class Table(StrEnum):
    STATIONS = "stations"
    OBSERVATIONS = "observations"

client = MongoClient(
    host=os.environ["WEATHER_HOST"],
    username=os.environ["WEATHER_DB_USER"],
    password=os.environ["WEATHER_DB_PW"],
    port=int(os.environ["WEATHER_DB_PORT"]),
    authSource=os.environ["WEATHER_DB_NAME"],
)

db = client[os.environ["WEATHER_DB_NAME"]]

# _id (ObjectId) kann nicht nach Postgres geschrieben werden, fachliche Schlüssel sind vorhanden
PROJECTION = {"_id": 0}

def extract_full(table_name: Table) -> DataFrame:
    log.info("Extracting full from source: %s", table_name)
    entries = db[table_name].find({}, PROJECTION)

    df = pd.json_normalize(list(entries), sep="_")
    log.info("%s: %d Rows loaded", table_name, len(df))
    return df

def extract_incremental(table_name: Table, cursor: int, upper_bound: int) -> DataFrame:
    log.info("Extracting increment from source: %s, current_cursor: %d, upper_bound: %d", table_name, cursor, upper_bound)
    entries = (
        db[table_name]
        .find({"change_seq": {"$gt": cursor, "$lte": upper_bound}}, PROJECTION)
        .sort("change_seq", 1)
    )
    df = pd.json_normalize(list(entries), sep="_")
    log.info("%s: %d Rows loaded", table_name, len(df))
    return df

def get_api_status() -> dict:
    return api.get_status(os.environ["WEATHER_HOST"], os.environ["WEATHER_API_PORT"])

def is_ready() ->bool:
    return api.is_ready(os.environ["WEATHER_HOST"], os.environ["WEATHER_API_PORT"])

def get_change_seq() -> int:
    return api.get_change_seq(os.environ["WEATHER_HOST"], os.environ["WEATHER_API_PORT"])
