"""
Generates a world map with worldwide vaccination data in the form of a .svg file.
Vaccination data is based on the user-given date and other preferences specified by the user.
"""
import json
from datetime import datetime
import pygal
from pygal.style import Style


def main():
    with open("owid-covid-data.json") as data_file, open("owid_to_pygal.json") as format_file:
        covid_data = json.load(data_file)
        country_codes = json.load(format_file)
        print("Welcome! This program generates a world map full of vaccination data\n"
              "in the form of a .svg file in the same location as main.py\n"
              "based on your user-given date and vaccination type.\n")
        newest_date = update_date(covid_data)
        user_date = take_date(newest_date)
        area_type = take_user_preference(["country", "continent"],
                                         "area type (COUNTRIES or CONTINENTS)")
        vacc_doses = take_user_preference(["one dose", "all doses"],
                                          "vaccination doses (ONE dose or ALL doses)")
        valid_countries, invalid_countries = collect_data(covid_data, country_codes, user_date, vacc_doses, area_type)
        generate_map(valid_countries, invalid_countries, user_date, area_type, vacc_doses)


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
    lower_end_date = datetime.strptime("2020-12-08", "%Y-%m-%d")
    higher_end_date = datetime.strptime(newest_date, "%Y-%m-%d")
    print("NOTE: The date has to be between 2020-12-08 and " + newest_date + ".")
    counter = 0

    while True:
        if counter >= 3:
            print("3 consecutive incorrect responses recorded!\n"
                  "Picking the default value (" + newest_date + ")...\n")
            return higher_end_date
        try:
            counter += 1
            user_date = input("Type date here (YYYY-mm-dd): ")
            conv_user_date = datetime.strptime(user_date, "%Y-%m-%d")
        # datetime.strptime causes a ValueError if the format is incorrect
        except ValueError:
            print("Incorrect date format!")
        else:
            date_is_correct = lower_end_date <= conv_user_date <= higher_end_date
            if date_is_correct:
                return conv_user_date
            print("Incorrect date!")


def take_user_preference(choices, pref_name):
    """
    Records user preference from a list of choices
        If user keeps picking incorrect choices, picks the first choice as the default one
    Returns it as a string to be used in other functions
    """
    counter = 0
    while True:
        if counter >= 3:
            print("3 consecutive incorrect responses recorded!\n"
                  "Picking the default value (" + choices[0].upper() + ")...\n")
            return choices[0]
        response = input("Type " + pref_name + " here: ").lower()
        if len(response) >= 3:
            for choice in choices:
                if response[0:3] in choice:
                    return choice
        counter += 1
        print("Response incorrect or too short!")


def collect_data(covid_data, area_codes, user_date, vacc_doses, area_type):
    """
    Collects data from the main data file based on provided user preferences
    Returns a table of processed data to be used in generate_map
    """
    valid_areas = {}
    invalid_areas = {}
    for OWID_area_code, area_info in covid_data.items():
        # TODO: reduce the IFS here or break it up into another function
        if OWID_area_code not in area_codes:
            continue
        if area_type == "country":
            if OWID_area_code.startswith("OWID"):
                continue
        else:
            if not OWID_area_code.startswith("OWID"):
                continue

        total_pop = area_info["population"]
        area_data = area_info["data"]
        area_code = area_codes[OWID_area_code]
        for count, day in enumerate(area_data):
            # day == country_data[count]
            date = datetime.strptime(day["date"], "%Y-%m-%d")
            if date == user_date:
                valid_areas[area_code] = calc_vacc_perc(total_pop, vacc_doses, area_data, count)
                break
        if area_code not in valid_areas or valid_areas[area_code] == 0:
            invalid_areas[area_code] = valid_areas.pop(area_code, 0)
    # Add countries that the loop might have missed
    invalid_areas = fill_map_holes(invalid_areas, valid_areas)
    return valid_areas, invalid_areas


def calc_vacc_perc(total_pop, vacc_doses, country_data, count):
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
            if "one" in vacc_doses:
                if "people_vaccinated" in day:
                    vacc_pop = day["people_vaccinated"]
            else:
                if "people_fully_vaccinated" in day:
                    vacc_pop = day["people_fully_vaccinated"]
            vacc_percent = round((vacc_pop / total_pop) * 100, 2)
            break
    return vacc_percent


def fill_map_holes(invalid_areas, valid_areas):
    """
    An extension of collect_data()
    Determines which countries on the Pygal map weren't "mentioned" during the assignment process
    Then assigns them to invalid_areas, filling out any potential non-assigned countries on the map
    """
    with open("pygal-areas.csv", 'r', encoding='utf-8-sig', newline='') as file:
        for pygal_area in file:
            pygal_area = pygal_area.strip()
            if pygal_area not in invalid_areas and pygal_area not in valid_areas:
                invalid_areas[pygal_area] = 0
    return invalid_areas


def generate_map(valid_areas, invalid_areas, user_date, area_type, vacc_doses):
    """
    Determines the style (colors) to be used in the world map
    Then, using data from collect_data(), generates a .svg file with the world map.
    """

    if area_type == "country":
        custom_style = Style(colors=('rgb(22, 152, 40)', '#BBBBBB'))
        worldmap = pygal.maps.world.World(style=custom_style)
        worldmap.add('Vaccination %', valid_areas)
    # Continents and their colors are handled differently
    # (This makes me wish I chose something else instead of Pygal lol it's such a mess)
    else:
        values = []
        for value in valid_areas.values():
            values.append("rgba(22, 152, 40, " + str((value / 100) + 0.15) + ")")
        values.append("#BBBBBB")
        custom_style = Style(colors=values)
        worldmap = pygal.maps.world.SupranationalWorld(style=custom_style)
        for continent, value in valid_areas.items():
            worldmap.add(continent.title().replace("_", " "), [(continent, value)])
    worldmap.add('No data', invalid_areas)

    date = datetime.strftime(user_date, '%Y-%m-%d')
    worldmap.title = f"{area_type.title()} vaccination data ({vacc_doses.upper()}) for {date}"
    worldmap.render_to_file('vaccmap.svg')


if __name__ == '__main__':
    main()
