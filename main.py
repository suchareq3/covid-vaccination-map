"""
Generates a world map with worldwide vaccination data in the form of a .svg file.
Vaccination data is based on user-given date and type of vaccination (1st dose or fully vaccinated).
"""
import json
from datetime import datetime
import pygal
from pygal.style import Style


def main():
    # TODO: add choice for continent data rather than country data

    with open("owid-covid-data.json") as data_file, open("owid_to_pygal.json") as format_file:
        covid_data = json.load(data_file)
        country_codes = json.load(format_file)
        print("Welcome! This program generates a world map full of vaccination data\n"
              "in the form of a .svg file in the same location as main.py\n"
              "based on your user-given date and vaccination type.\n")
        newest_date = update_date(covid_data)
        user_date = take_date(newest_date)
        vacc_type = take_vacc_type()
        valid_countries = collect_data(covid_data, country_codes, user_date, vacc_type)
        generate_map(valid_countries, user_date)


def update_date(covid_data):
    """
    Checks the data file's most recent entry
    Returns the most recent date as a YYYY-MM-DD string
    """
    for country_code, country_info in covid_data.items():
        # Check USA's data because of the reliably high frequency of updates
        if country_code == "USA":
            data_entries = country_info['data']
            last_entry = data_entries[-1]
            latest_date = last_entry['date']
            return latest_date


def take_date(newest_date):
    """
    Receives a valid date from user input and returns it as a "datetime" object
    """

    # Add lower and upper bounds
    lower_end_date = datetime.strptime("2020-12-08", "%Y-%m-%d")
    higher_end_date = datetime.strptime(newest_date, "%Y-%m-%d")
    # Temporary variable to prevent error
    conv_user_date = None

    while True:
        try:
            print("NOTE: The date has to be between 2020-12-08 and " + newest_date + ".")
            user_date = input("Type date here (YYYY-mm-dd): ")
            conv_user_date = datetime.strptime(user_date, "%Y-%m-%d")

        # datetime.strptime causes a ValueError if the format is incorrect
        except ValueError:
            print("INCORRECT DATE FORMAT!\n")
            continue
        else:
            date_is_correct = lower_end_date <= conv_user_date <= higher_end_date
            if not date_is_correct:
                print("INCORRECT DATE!\n")
                continue
            else:
                # If both format and date are correct, break out of the loop.
                break
    return conv_user_date


def take_vacc_type():
    """
    Returns type of user-specified vaccination data (1st dose or fully vaccinated)
    """
    # TODO: I can definitely change this to be far less 'iffy' if you catch my drift (smth with enums?)
    while True:
        response = input("Type vaccination type here (\"ONE\" dose/\"FULLY\" vaccinated): ").lower()
        if response not in ("one", "one dose", "fully", "fully vaccinated"):
            print("INCORRECT RESPONSE!\n")
            continue
        else:
            if response == "fully vaccinated":
                response = "fully"
            if response == "one dose":
                response = "one"
            break
    return response


def collect_data(covid_data, country_codes, user_date, vacc_type):
    """
    Collects data from the main data file based on provided user preferences
    Returns a table of country data to be used in generate_map
    Returns a tuple with two tables of country data to be used in generate_map
    """
    valid_countries = {}
    for OWID_country_code, country_info in covid_data.items():
        # Skip invalid countries
        # TODO: change this based on whether user wants continent data or country data
        if OWID_country_code.startswith("OWID") or OWID_country_code not in country_codes:
            continue
        total_pop = country_info["population"]
        country_data = country_info["data"]
        country_code = country_codes[OWID_country_code]
        for count, day in enumerate(country_data):
            # day == country_data[count]
            date = datetime.strptime(day["date"], "%Y-%m-%d")
            if date == user_date:
                valid_countries = validate_data(country_code, valid_countries, total_pop, vacc_type, day)
                break
    return valid_countries


def validate_data(country_code, valid_countries, total_pop, vacc_type, day):
    """
    An extension of collect_data()
    1) Determines whether data exists for the given country and given day.
    2) Calculates vaccination percentage and returns that into the current country's value
    """
    # Temporary variable
    vacc_percent = None

    # TODO: check out whether there's a better looking alternative for these if/else statements
    if "total_vaccinations" in day:
        vacc_pop = 0
        if vacc_type == "one":
            if "people_vaccinated" in day:
                vacc_pop = day["people_vaccinated"]
        else:
            if "people_fully_vaccinated" in day:
                vacc_pop = day["people_fully_vaccinated"]
        vacc_percent = round((vacc_pop / total_pop) * 100, 2)

    valid_countries[country_code] = vacc_percent
    return valid_countries


def generate_map(valid_countries, user_date):
    """
    Determines the style (colors) to be used in the world map
    Then generates a .svg file with the world map, using data from collect_data()
    """
    # TODO: make it so that smaller %'s aren't so aggressively light
    # TODO: see if I can make the map larger

    custom_style = Style(colors=('#169828', '#BBBBBB'))
    worldmap_chart = pygal.maps.world.World(style=custom_style)
    worldmap_chart.title = "Vaccination data for " + datetime.strftime(user_date, "%Y-%m-%d")

    # TODO: change this based on user-selected type of vaccination data
    worldmap_chart.add('Vaccination %', valid_countries)
    worldmap_chart.render_to_file('vaccmap.svg')


if __name__ == '__main__':
    main()
