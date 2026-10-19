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
    customers = shop.extract_full(shop.Table.CUSTOMERS)
    warehouse.write_raw_full(customers, shop.SOURCE, shop.Table.CUSTOMERS)
    products = shop.extract_full(shop.Table.PRODUCTS)
    warehouse.write_raw_full(products, shop.SOURCE, shop.Table.PRODUCTS)

    shop_change_seq = shop.get_change_seq()
    last_cursor = warehouse.get_last_cursor(shop.SOURCE, shop.Table.ORDERS)

    orders = shop.extract_incremental(shop.Table.ORDERS, last_cursor, shop_change_seq)

    if not orders.empty:
        count_increment = warehouse.write_raw_incremental(orders, shop.SOURCE, shop.Table.ORDERS, shop_change_seq)

    # Order Items nachziehen
    last_cursor = warehouse.get_last_cursor(shop.SOURCE, shop.Table.ORDER_ITEMS)

    order_items = shop.extract_incremental_child(shop.Table.ORDER_ITEMS, shop.Table.ORDERS, "order_id", last_cursor, shop_change_seq)

    if not order_items.empty:
        count_increment = warehouse.write_raw_incremental(order_items, shop.SOURCE, shop.Table.ORDER_ITEMS, shop_change_seq)

    print(weather.get_api_status())
    print(weather.exec())

    energy_ready = energy.is_ready()
    meters = energy.extract_full(energy.Table.METERS)
    warehouse.write_raw_full(meters, energy.SOURCE, energy.Table.METERS)

    energy_change_seq = energy.get_change_seq()
    last_cursor = warehouse.get_last_cursor(energy.SOURCE, energy.Table.READINGS)

    readings = energy.extract_incremental(energy.Table.READINGS, last_cursor, energy_change_seq)
    count_increment = 0
    if not readings.empty:
       count_increment = warehouse.write_raw_incremental(readings, energy.SOURCE, energy.Table.READINGS, energy_change_seq)



