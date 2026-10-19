import shop


def test_extract_incremental_child_uses_order_change_seq_window(shop_engine):
    df = shop.extract_incremental_child("order_items", "orders", "order_id", 1, 3)

    assert list(zip(df["order_id"], df["line_no"])) == [(11, 1), (12, 1), (12, 2)]
    assert list(df["change_seq"]) == [2, 3, 3]


def test_extract_incremental_child_empty_when_cursor_equals_upper_bound(shop_engine):
    df = shop.extract_incremental_child("order_items", "orders", "order_id", 3, 3)

    assert df.empty
