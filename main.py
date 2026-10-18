import Shop
import Weather
import Energy
import Warehouse
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
    Shop.print_engine()
    print(Shop.get_api_status())
    ## print(Shop.complex_query())

    print(Weather.get_api_status())
    print(Weather.exec())

    energy_ready = Energy.is_ready()
    meters = Energy.extract_full("meters")
    count = Warehouse.write_raw_full(meters, "energy_meters")

    change_seq = Energy.get_api_status()["changeSeq"]
    last_cursor = Warehouse.get_last_cursor("energy", "readings")

    readings = Energy.extract_incremental("readings", last_cursor, change_seq)
    count_increment = 0
    if not readings.empty:
       count_increment = Warehouse.write_raw_incremental(readings, "energy", "readings", change_seq)



