import pandas as pd
import sqlalchemy as sa

import warehouse


def _scalar(engine, sql):
    with engine.connect() as conn:
        return conn.execute(sa.text(sql)).scalar_one()


def _readings(seqs):
    return pd.DataFrame({
        "reading_id": seqs,
        "value": [float(s) for s in seqs],
        "change_seq": seqs,
    })


def test_write_raw_incremental_second_run_counts_only_new_window(dwh_engine):
    warehouse.write_raw_incremental(_readings([1, 2, 3]), "energy", "readings", 3)

    rows = warehouse.write_raw_incremental(_readings([4, 5]), "energy", "readings", 5)

    assert rows == 2
    assert warehouse.get_last_cursor("energy", "readings") == 5
    assert _scalar(dwh_engine, "SELECT count(*) FROM raw.energy_readings") == 5
