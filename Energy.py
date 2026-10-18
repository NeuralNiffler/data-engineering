import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
import sqlalchemy as sa
import requests

load_dotenv()

engine = sa.create_engine(sa.URL.create(
    host=os.environ["ENERGY_HOST"],
    drivername="mysql+pymysql",
    username=os.environ["ENERGY_DB_USER"],
    password=os.environ["ENERGY_DB_PW"],
    port=int(os.environ["ENERGY_DB_PORT"]),
    database=os.environ["ENERGY_DB_NAME"],
))

def extract_full(table_name: str) -> DataFrame:
    df = pd.read_sql_table(table_name, engine)
    return df

def extract_incremental(table_name: str, cursor: int, upper_bound: int) -> DataFrame:
    table = sa.Table(table_name, sa.MetaData(), autoload_with=engine)
    seq = table.c["change_seq"]

    query = (
        sa.select(table)
        .where(seq > cursor, seq <= upper_bound)
        .order_by(seq)
    )
    return pd.read_sql_query(query, engine)

def get_api_status() -> dict:
    baseURL = f"http://{os.environ["ENERGY_HOST"]}:{os.environ["ENERGY_API_PORT"]}/api/status"
    response = requests.get(baseURL, timeout=10)
    response.raise_for_status()
    data = response.json()

    return data