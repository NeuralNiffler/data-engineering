import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
import sqlalchemy as sa
import logging

import api

log = logging.getLogger(__name__)
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
    log.info("Extracting full from source: %s", table_name)
    df = pd.read_sql_table(table_name, engine)
    log.info("%s: %d Rows loaded", table_name, len(df))
    return df

def extract_incremental(table_name: str, cursor: int, upper_bound: int) -> DataFrame:
    log.info("Extracting increment from source: %s, current_cursor: %d, upper_bound: %d", table_name, cursor, upper_bound)
    table = sa.Table(table_name, sa.MetaData(), autoload_with=engine)
    seq = table.c["change_seq"]

    query = (
        sa.select(table)
        .where(seq > cursor, seq <= upper_bound)
        .order_by(seq)
    )

    df = pd.read_sql_query(query, engine)
    log.info("%s: %d Rows loaded", table_name, len(df))
    return df

def get_api_status() -> dict:
    return api.get_status(os.environ["ENERGY_HOST"], os.environ["ENERGY_API_PORT"])

def is_ready() ->bool:
    return api.is_ready(os.environ["ENERGY_HOST"], os.environ["ENERGY_API_PORT"])