import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, URL, text

load_dotenv()

engine = create_engine(URL.create(
    host=os.environ["DWH_HOST"],
    drivername="postgresql+psycopg",
    username=os.environ["DWH_DB_USER"],
    password=os.environ["DWH_DB_PW"],
    port=int(os.environ["DWH_DB_PORT"]),
    database=os.environ["DWH_DB_NAME"],
))

def get_cursor(source: str, table_name: str) -> int:
    query = text("""
            SELECT last_cursor
            FROM etl.load_state
            WHERE source = :source
              AND table_name = :table_name
            """)
    df = pd.read_sql_query(query, engine, params={"source": source, "table_name": table_name})

    return int(df['last_cursor'].iloc[0])

def print_engine() :
    print(engine)
