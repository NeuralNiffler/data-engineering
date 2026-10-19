import pandas as pd
import pytest
import sqlalchemy as sa

import energy
import shop
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
    warehouse.write_raw_incremental(_readings([1, 2, 3]), energy.SOURCE, energy.Table.READINGS, 3)

    rows = warehouse.write_raw_incremental(_readings([4, 5]), energy.SOURCE, energy.Table.READINGS, 5)

    assert rows == 2
    assert warehouse.get_last_cursor(energy.SOURCE, energy.Table.READINGS) == 5
    assert _scalar(dwh_engine, "SELECT count(*) FROM raw.energy_readings") == 5


def test_get_last_cursor_without_load_state_entry_raises(dwh_engine):
    with pytest.raises(ValueError, match="shop.orders"):
        warehouse.get_last_cursor(shop.SOURCE, shop.Table.ORDERS)


def test_write_raw_full_writes_to_source_prefixed_table(dwh_engine):
    rows = warehouse.write_raw_full(pd.DataFrame({"meter_id": [1, 2]}), energy.SOURCE, energy.Table.METERS)

    assert rows == 2
    assert _scalar(dwh_engine, "SELECT count(*) FROM raw.energy_meters") == 2
