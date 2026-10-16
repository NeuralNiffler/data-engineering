import Shop
import Weather
import Energy
import Warehouse

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Shop.print_engine()
    print(Shop.api_status())
    ## print(Shop.complex_query())

    print(Weather.api_status())
    print(Weather.exec())

    change_seq = Energy.api_status()["changeSeq"]
    cursor = Warehouse.get_cursor("energy", "readings")

    meters = Energy.extract_master_data()
    count = Warehouse.write_raw_full(meters, "energy_meters")

    readings = Energy.extract_transactional_data(cursor, change_seq)
    count_increment = 0
    if not readings.empty:
       count_increment = Warehouse.write_raw_incremental(readings, "energy", "readings", change_seq)
    print(f"energy: {count} meters, {count_increment} readings geladen")


