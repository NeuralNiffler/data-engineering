import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.pool import StaticPool

# Module bauen ihre Engine beim Import aus os.environ -> Dummy-Werte vorher setzen.
# load_dotenv() überschreibt bereits gesetzte Variablen nicht.
DUMMY_ENV = {
    "ENERGY_HOST": "energy.test",
    "ENERGY_DB_USER": "user",
    "ENERGY_DB_PW": "pw",
    "ENERGY_DB_PORT": "3312",
    "ENERGY_DB_NAME": "energy",
    "ENERGY_API_PORT": "8102",
    "SHOP_HOST": "shop.test",
    "SHOP_DB_USER": "user",
    "SHOP_DB_PW": "pw",
    "SHOP_DB_PORT": "5432",
    "SHOP_DB_NAME": "shop",
    "SHOP_API_PORT": "8101",
    "DWH_HOST": "dwh.test",
    "DWH_DB_USER": "user",
    "DWH_DB_PW": "pw",
    "DWH_DB_PORT": "5433",
    "DWH_DB_NAME": "warehouse",
}
os.environ.update(DUMMY_ENV)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import energy  # noqa: E402
import shop  # noqa: E402
import warehouse  # noqa: E402


def _sqlite_engine() -> sa.Engine:
    return sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def energy_engine(monkeypatch):
    engine = _sqlite_engine()
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE meters (meter_id INTEGER PRIMARY KEY, location TEXT)"))
        conn.execute(sa.text("INSERT INTO meters VALUES (1, 'Aarau'), (2, 'Baden')"))
        conn.execute(sa.text("""
            CREATE TABLE readings (
                reading_id INTEGER PRIMARY KEY,
                meter_id   INTEGER,
                value      REAL,
                change_seq INTEGER
            )"""))
        # bewusst unsortiert eingefügt
        conn.execute(sa.text("""
            INSERT INTO readings VALUES
                (1, 1, 10.0, 3),
                (2, 1, 11.0, 1),
                (3, 2, 12.0, 5),
                (4, 2, 13.0, 2),
                (5, 1, 14.0, 4)
            """))
    monkeypatch.setattr(energy, "engine", engine)
    return engine


@pytest.fixture
def shop_engine(monkeypatch):
    engine = _sqlite_engine()
    with engine.begin() as conn:
        conn.execute(sa.text("""
            CREATE TABLE orders (
                order_id    INTEGER PRIMARY KEY,
                customer_id INTEGER,
                status      TEXT,
                change_seq  INTEGER
            )"""))
        conn.execute(sa.text("INSERT INTO orders VALUES (10, 1, 'paid', 1), (11, 2, 'shipped', 2), (12, 1, 'paid', 3)"))
        conn.execute(sa.text("""
            CREATE TABLE order_items (
                order_id   INTEGER,
                line_no    INTEGER,
                product_id INTEGER,
                quantity   INTEGER,
                PRIMARY KEY (order_id, line_no)
            )"""))

        conn.execute(sa.text("""
            INSERT INTO order_items VALUES
                (12, 1, 7, 1),
                (10, 2, 5, 1),
                (11, 1, 6, 3),
                (10, 1, 4, 2),
                (12, 2, 8, 2)
            """))
    monkeypatch.setattr(shop, "engine", engine)
    return engine


@pytest.fixture
def dwh_engine(monkeypatch):
    engine = _sqlite_engine()

    # Postgres-Schemas raw/etl als attached DBs nachbilden, now() bereitstellen
    @sa.event.listens_for(engine, "connect")
    def _on_connect(dbapi_conn, _):
        dbapi_conn.execute("ATTACH DATABASE ':memory:' AS raw")
        dbapi_conn.execute("ATTACH DATABASE ':memory:' AS etl")
        dbapi_conn.create_function("now", 0, lambda: datetime.now(timezone.utc).isoformat())

    with engine.begin() as conn:
        conn.execute(sa.text("""
            CREATE TABLE etl.load_state (
                source      TEXT    NOT NULL,
                table_name  TEXT    NOT NULL,
                last_cursor BIGINT  NOT NULL DEFAULT 0,
                updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source, table_name)
            )"""))
        conn.execute(sa.text("INSERT INTO etl.load_state (source, table_name) VALUES ('energy', 'readings')"))
    monkeypatch.setattr(warehouse, "engine", engine)
    return engine
