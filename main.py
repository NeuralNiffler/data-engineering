import Shop
import Weather
import Energy

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Shop.print_engine()
    print(Shop.api_status())
    ## print(Shop.complex_query())

    print(Weather.api_status())
    print(Weather.exec())

    print(Energy.api_status())
    print(Energy.exec())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
