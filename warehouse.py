import os
from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine, URL, text
import logging

log = logging.getLogger(__name__)
load_dotenv()

engine = create_engine(URL.create(
    host=os.environ["DWH_HOST"],
    drivername="postgresql+psycopg",
    username=os.environ["DWH_DB_USER"],
    password=os.environ["DWH_DB_PW"],
    port=int(os.environ["DWH_DB_PORT"]),
    database=os.environ["DWH_DB_NAME"],
))

def get_last_cursor(source: str, table_name: str) -> int:
    query = text("""
            SELECT last_cursor
            FROM etl.load_state
            WHERE source = :source
              AND table_name = :table_name
            """)
    df = pd.read_sql_query(query, engine, params={"source": source, "table_name": table_name})
    last_cursor = int(df['last_cursor'].iloc[0])

    log.info("Last cursor for %s %s is %d", source, table_name, last_cursor)

    return last_cursor

def write_raw_full(df: DataFrame, table_name: str) -> int:
    count_query = text(f"SELECT count(*) FROM raw.{table_name}")

    with engine.begin() as conn:
        df.to_sql(table_name, conn, schema="raw", if_exists="replace", index=False)
        rows_in_table = conn.execute(count_query).scalar_one()

    log.info("%s: %d Rows written", table_name, rows_in_table)

    return rows_in_table

def write_raw_incremental(df: DataFrame, source: str, table_name: str, cursor_to: int) -> int:
    count_query = text(f"""
            SELECT count(*)
            FROM raw.{source}_{table_name}
            WHERE change_seq > :cursor_from
              AND change_seq <= :cursor_to
            """)
    update_stats_query = text("""
            UPDATE etl.load_state
               SET last_cursor = :cursor_to,
                   updated_at = now()
             WHERE source = :source
               AND table_name = :table_name
            """)

    cursor_from = get_last_cursor(source, table_name)

    with engine.begin() as conn:
        # Main Update query
        df.to_sql(f"{source}_{table_name}", conn, schema="raw", if_exists="append", index=False)

        # Logging and Updating stats
        rows_written = conn.execute(count_query, {"cursor_from": cursor_from, "cursor_to": cursor_to}).scalar_one()
        conn.execute(update_stats_query, {"cursor_to": cursor_to, "source": source, "table_name": table_name})

    log.info("%s %s rows written: %d, new_cursor: %d", source,table_name, rows_written, cursor_to)

    return rows_written
