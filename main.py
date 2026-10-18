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
    shop.print_engine()
    print(shop.get_api_status())
    ## print(Shop.complex_query())

    print(weather.get_api_status())
    print(weather.exec())

    energy_ready = energy.is_ready()
    meters = energy.extract_full("meters")
    count = warehouse.write_raw_full(meters, "energy_meters")

    change_seq = energy.get_api_status()["changeSeq"]
    last_cursor = warehouse.get_last_cursor("energy", "readings")

    readings = energy.extract_incremental("readings", last_cursor, change_seq)
    count_increment = 0
    if not readings.empty:
       count_increment = warehouse.write_raw_incremental(readings, "energy", "readings", change_seq)



