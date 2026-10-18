import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine, URL
import requests
import logging

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

def exec() -> DataFrame:
    df = pd.read_sql_table('orders',engine)

    return df

def complex_query() -> DataFrame:
    query = """
            SELECT o.order_id,
                   o.ordered_at,
                   o.status,
                   i.quantity,
                   p.product_id,
                   p.name,
                   p.category,
                  c.city_code,
            FROM orders o
                     JOIN order_items i ON i.order_id = o.order_id
                     JOIN products p ON p.product_id = i.product_id 
                     JOIN customers c ON c.customer_id = o.customer_id
                \
            """
    df = pd.read_sql_query(query,engine)

    return df

def get_api_status() -> DataFrame:
    baseURL = f"http://{os.environ["SHOP_HOST"]}:{os.environ["SHOP_API_PORT"]}/api/status"
    response = requests.get(baseURL, timeout=10)
    response.raise_for_status()
    data = response.json()

    return pd.json_normalize(data)

def print_engine() :
    print(engine)