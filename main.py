import shop
import weather
import energy
import warehouse
import logging
from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[RichHandler(
        console=Console(width=150),
        show_path=False,
    )],
)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    shop_ready = shop.is_ready()
    customers = shop.extract_full("customers")
    warehouse.write_raw_full(customers, "shop", "customers")
    products = shop.extract_full("products")
    warehouse.write_raw_full(products, "shop", "products")

    shop_change_seq = shop.get_api_status()["changeSeq"]
    last_cursor = warehouse.get_last_cursor("shop", "orders")

    orders = shop.extract_incremental("orders", last_cursor, shop_change_seq)

    if not orders.empty:
        count_increment = warehouse.write_raw_incremental(orders, "shop", "orders", shop_change_seq)

    # Order Items nachziehen
    last_cursor = warehouse.get_last_cursor("shop", "order_items")

    order_items = shop.extract_incremental_child("order_items", "orders", "order_id", last_cursor, shop_change_seq)

    if not order_items.empty:
        count_increment = warehouse.write_raw_incremental(order_items, "shop", "order_items", shop_change_seq)

    print(weather.get_api_status())
    print(weather.exec())

    energy_ready = energy.is_ready()
    meters = energy.extract_full("meters")
    warehouse.write_raw_full(meters, "energy", "meters")

    energy_change_seq = energy.get_api_status()["changeSeq"]
    last_cursor = warehouse.get_last_cursor("energy", "readings")

    readings = energy.extract_incremental("readings", last_cursor, energy_change_seq)
    count_increment = 0
    if not readings.empty:
       count_increment = warehouse.write_raw_incremental(readings, "energy", "readings", energy_change_seq)



