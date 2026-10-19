import weather


def test_extract_full_drops_id_and_flattens_measurements(weather_db):
    df = weather.extract_full(weather.Table.OBSERVATIONS)

    assert "_id" not in df.columns
    assert "measurements" not in df.columns
    assert {"measurements_temperature_c", "measurements_humidity_pct", "measurements_rain_mm"} <= set(df.columns)


def test_extract_incremental_window_bounds(weather_db):
    df = weather.extract_incremental(weather.Table.OBSERVATIONS, 1, 4)

    assert list(df["change_seq"]) == [2, 3, 4]
    assert list(df["measurements_temperature_c"]) == [12.0, 13.0, 14.0]


def test_extract_incremental_empty_when_cursor_equals_upper_bound(weather_db):
    df = weather.extract_incremental(weather.Table.OBSERVATIONS, 5, 5)

    assert df.empty
