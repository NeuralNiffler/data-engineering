import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
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

def write_raw_full(df: DataFrame, table_name: str) -> int:
    count_query = text(f"SELECT count(*) FROM raw.{table_name}")

    with engine.begin() as conn:
        df.to_sql(table_name, conn, schema="raw", if_exists="replace", index=False)
        rows_in_table = conn.execute(count_query).scalar_one()

    return rows_in_table

def write_raw_incremental(df: DataFrame, source: str, table_name: str, cursor_to: int) -> int:
    cursor_query = text("""
            SELECT last_cursor
            FROM etl.load_state
            WHERE source = :source
              AND table_name = :table_name
            FOR UPDATE
            """)
    count_query = text(f"""
            SELECT count(*)
            FROM raw.{source}_{table_name}
            WHERE change_seq > :cursor_from
              AND change_seq <= :cursor_to
            """)
    update_query = text("""
            UPDATE etl.load_state
               SET last_cursor = :cursor_to,
                   updated_at = now()
             WHERE source = :source
               AND table_name = :table_name
            """)
    with engine.begin() as conn:
        cursor_from = conn.execute(cursor_query, {"source": source, "table_name": table_name}).scalar_one()
        df.to_sql(f"{source}_{table_name}", conn, schema="raw", if_exists="append", index=False)
        rows_loaded = conn.execute(count_query, {"cursor_from": cursor_from, "cursor_to": cursor_to}).scalar_one()
        conn.execute(update_query, {"cursor_to": cursor_to, "source": source, "table_name": table_name})

    return rows_loaded
