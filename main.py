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
        user_date = take_date()
        vacc_type = take_vacc_type()
        generate_map(covid_data, country_codes, user_date, vacc_type)


def take_date():
    """
    Receives a valid date from user input and returns it as a "datetime" object
    """
    # TODO: instead of having a hard-coded date, calculate the last accessible date in the OWID .json file
    #   (to make it easier to just download & drag and drop the OWID .json data file into the directory)

    # Add lower and upper bounds
    lower_end_date = datetime.strptime("2020-12-08", "%Y-%m-%d")
    higher_end_date = datetime.strptime("2021-05-30", "%Y-%m-%d")
    # Temporary variable to prevent error
    conv_user_date = datetime.now()

    # Keep asking for a date until:
    # 1) date format is correct
    # 2) date is between the range of allowed dates
    while True:
        try:
            print("NOTE: The date has to be between 2020-12-08 and 2021-05-30.")
            user_date = input("Type date here (YYYY-MM-DD): ")
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
    Returns type of vaccination data (1st dose or fully vaccinated)
    """
    while True:
        response = input("Type vaccination type here (\"ONE\" dose/\"FULLY\" vaccinated): ").lower()
        if response not in ("one", "one dose", "fully", "fully vaccinated"):
            print("INCORRECT RESPONSE!\n")
            continue
        else:
            # If response is correct, break out of the loop.
            if response == "fully vaccinated":
                response = "fully"
            if response == "one dose":
                response = "one"
            break
    return response


def generate_map(covid_data, country_codes, user_date, vacc_type):
    """
    Generates a .svg file with the world map, using data from the included "owid-covid-data.json" file.
    Data shown on the map is picked based on the user's responses.
    """
    # TODO: break this function up into smaller ones for readability's sake
    # TODO: make it so that smaller %'s aren't so aggressively light
    # TODO: for countries with no available data (or 0% vaccs), put them into a second, grey "No data" group
    # TODO: see if I can make the map larger

    custom_style = Style(colors=('#169828', '#BBBBBB'))
    worldmap_chart = pygal.maps.world.World(style=custom_style)
    worldmap_chart.title = "Vaccination data for " + datetime.strftime(user_date, "%Y-%m-%d")
    map_dict = {}

    for OWID_country_code, country_info in covid_data.items():
        # Skip continent data
        if OWID_country_code.startswith("OWID"):
            continue
        # Skip if country code doesn't exist in the included OWID_to_Pygal.json comparison table.
        if OWID_country_code not in country_codes:
            continue
        country_code = country_codes[OWID_country_code]
        total_pop = country_info["population"]
        for day in country_info["data"]:
            # TODO: better/more efficient skipping forward to the date specified by user,
            #   i can definitely cut down on the high number of (potentially unnecessary) loops/checks...
            date = datetime.strptime(day["date"], "%Y-%m-%d")
            if date == user_date:
                # TODO: if no data for the given day, instead of skipping it like i am right now,
                #  attempt to look for closest past (reasonable, max 2 weeks) available data point
                # Calculate vacc data only if data for the country exists
                if "total_vaccinations" in day:
                    map_dict[country_code] = calc_vacc_percent(day, total_pop, vacc_type)
                # Since you've found the date, break out of the loop to skip next dates (a sliver of efficiency)
                break
    # TODO: change this based on user-selected type of vaccination data
    worldmap_chart.add('Vaccination %', map_dict)
    worldmap_chart.render_to_file('vaccmap.svg')


def calc_vacc_percent(day, total_pop, vacc_type):
    """
    Assumes that 'total_vaccinations' exists in 'day'.
    Takes day data, total population & vaccination type
    Calculates and returns vaccination percentage
    """
    # TODO: check out whether there's a better looking alternative for these if/else statements

    # Temporary variable
    vacc_pop = 0
    if vacc_type == "one":
        if "people_vaccinated" in day:
            vacc_pop = day["people_vaccinated"]
    else:
        if "people_fully_vaccinated" in day:
            vacc_pop = day["people_fully_vaccinated"]
    return round((vacc_pop / total_pop)*100, 2)


if __name__ == '__main__':
    main()
