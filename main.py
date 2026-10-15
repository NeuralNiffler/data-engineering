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
    cursor=Warehouse.get_cursor("energy", "readings")

    print(Energy.api_status())
    print(Energy.exec())
    print(Energy.extract_master_data())
    print(Energy.extract_transactional_data(cursor, change_seq))


