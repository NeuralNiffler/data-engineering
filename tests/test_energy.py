import energy

def test_extract_incremental_window_bounds(energy_engine):
    df = energy.extract_incremental(energy.Table.READINGS, 1, 4)

    assert list(df["change_seq"]) == [2, 3, 4]


def test_extract_incremental_empty_when_cursor_equals_upper_bound(energy_engine):
    df = energy.extract_incremental(energy.Table.READINGS, 5, 5)

    assert df.empty
