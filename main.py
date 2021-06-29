"""
Generates a world map with worldwide vaccination data in the form of a .svg file.
Vaccination data is based on a user-given date and type of vaccination (1st dose or fully vaccinated).
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
        valid_countries, invalid_countries = collect_data(covid_data, country_codes, user_date, vacc_type)
        generate_map(valid_countries, invalid_countries, user_date)


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
    """
    valid_countries = {}
    invalid_countries = {}
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
                valid_countries[country_code] = calc_vacc_perc(total_pop, vacc_type, country_data, count)
                break
        if country_code not in valid_countries or valid_countries[country_code] == 0:
            invalid_countries[country_code] = valid_countries.pop(country_code, 0)
    # Add countries that the loop might have missed
    invalid_countries = fill_map_holes(invalid_countries, valid_countries)
    return valid_countries, invalid_countries


def calc_vacc_perc(total_pop, vacc_type, country_data, count):
    """
    An extension of collect_data()
    1) Determines whether data exists for the given country and given day.
        a) if it doesn't exist for the given day, attempt to find data within the last 21 days
    2) Calculates vaccination percentage and returns that into the current country's value
    """
    # Temporary variable
    vacc_percent = 0
    day = country_data[count]

    for i in range(1, 22):
        if "total_vaccinations" not in day:
            day = country_data[count - i]
            continue
        # TODO: check out whether there's a better looking alternative for these if/else statements
        else:
            vacc_pop = 0
            if vacc_type == "one":
                if "people_vaccinated" in day:
                    vacc_pop = day["people_vaccinated"]
            else:
                if "people_fully_vaccinated" in day:
                    vacc_pop = day["people_fully_vaccinated"]
            vacc_percent = round((vacc_pop / total_pop) * 100, 2)
            break
    return vacc_percent


def fill_map_holes(invalid_countries, valid_countries):
    """
    An extension of collect_data()
    Determines which countries on the Pygal map weren't "mentioned" during the assignment process
    Then assigns them to invalid_countries, filling out any potential non-assigned countries on the map
    """
    with open("pygal-countries.csv", 'r', encoding='utf-8-sig', newline='') as file:
        for pygal_country in file:
            pygal_country = pygal_country.strip()
            if pygal_country not in invalid_countries and pygal_country not in valid_countries:
                invalid_countries[pygal_country] = 0
    return invalid_countries


def generate_map(valid_countries, invalid_countries, user_date):
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
    worldmap_chart.add('No data', invalid_countries)
    worldmap_chart.render_to_file('vaccmap.svg')


if __name__ == '__main__':
    main()
