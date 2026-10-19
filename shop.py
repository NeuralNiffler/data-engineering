import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine, URL
import logging
import sqlalchemy as sa

import api

log = logging.getLogger(__name__)
load_dotenv()

engine = create_engine(URL.create(
    host=os.environ["SHOP_HOST"],
    drivername="postgresql+psycopg",
    username=os.environ["SHOP_DB_USER"],
    password=os.environ["SHOP_DB_PW"],
    port=int(os.environ["SHOP_DB_PORT"]),
    database=os.environ["SHOP_DB_NAME"],
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

def extract_incremental_child(table_name: str, parent_name: str, join_key: str, cursor: int, upper_bound: int) -> DataFrame:
    log.info("Extracting child increment from source: %s via %s, current_cursor: %d, upper_bound: %d", table_name, parent_name, cursor, upper_bound)
    metadata = sa.MetaData()
    child = sa.Table(table_name, metadata, autoload_with=engine)
    parent = sa.Table(parent_name, metadata, autoload_with=engine)
    seq = parent.c["change_seq"]

    query = (
        sa.select(child, seq)
        .join(parent, parent.c[join_key] == child.c[join_key])
        .where(seq > cursor, seq <= upper_bound)
        .order_by(seq, *child.primary_key.columns)
    )

    df = pd.read_sql_query(query, engine)
    log.info("%s: %d Rows loaded", table_name, len(df))
    return df

def get_api_status() -> dict:
    return api.get_status(os.environ["SHOP_HOST"], os.environ["SHOP_API_PORT"])

def is_ready() ->bool:
    return api.is_ready(os.environ["SHOP_HOST"], os.environ["SHOP_API_PORT"])