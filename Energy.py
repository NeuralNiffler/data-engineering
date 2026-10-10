import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine, URL
import requests

load_dotenv()

engine = create_engine(URL.create(
    host=os.environ["ENERGY_HOST"],
    drivername="mysql+pymysql",
    username=os.environ["ENERGY_DB_USER"],
    password=os.environ["ENERGY_DB_PW"],
    port=int(os.environ["ENERGY_DB_PORT"]),
    database=os.environ["ENERGY_DB_NAME"],
))

def exec() -> DataFrame:
    df = pd.read_sql_table('readings',engine)

    return df

def complex_query() -> DataFrame:
    query = """
       SELECT r.change_seq,
              r.reading_id,
              r.measured_at,
              r.consumtion_kwh,
              r.tariff_chf_kwh,
              m.city_code,
              m.building_type,
              m.floor_area_m2
         FROM readings r
         JOIN meters m ON m.meter_id = r.meter_id
        WHERE r.change_seq > :cursor 
          AND r.change_seq <= :upper_bound 
        ORDER BY change_seq;
                \
            """
    df = pd.read_sql_query(query,engine)

    return df

def api_status() -> DataFrame:
    baseURL = f"http://{os.environ["ENERGY_HOST"]}:{os.environ["ENERGY_API_PORT"]}/api/status"
    response = requests.get(baseURL, timeout=10)
    response.raise_for_status()
    data = response.json()

    return pd.json_normalize(data)

def print_engine() :
    print(engine)