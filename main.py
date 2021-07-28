"""
Generates a world map with worldwide vaccination data in the form of a .svg file.
Vaccination data is based on the user-given date and other preferences specified by the user.
"""
import csv
import json
import os.path
import sys
from datetime import datetime

import pygal
import requests
from pygal.style import Style
from requests import get
from tqdm import tqdm


def main():
    print("Connecting to Github to check for data updates...")
    update_data()
    with open("vaccinations.json") as vacc_data_file, \
            open("population_2020.csv") as pop_data_file, \
            open("owid_to_pygal.json") as format_file:
        vacc_data = json.load(vacc_data_file)
        area_codes = json.load(format_file)
        print("\nWelcome! This program generates a world map full of vaccination data\n"
              "in the form of a .svg file in the same location as main.py\n"
              "based on your user-given date and vaccination type.\n")
        newest_date = datetime.fromtimestamp(os.path.getmtime("vaccinations.json")).strftime("%Y-%m-%d")
        user_date = take_date(newest_date)
        area_type = take_user_preference(["country", "continent"], "area type (COUNTRIES or CONTINENTS)")
        vacc_doses = take_user_preference(["one dose", "all doses"], "vaccination doses (ONE dose or ALL doses)")
        valid_areas, invalid_areas = collect_data(vacc_data, pop_data_file, area_codes,
                                                  user_date, vacc_doses, area_type)
        generate_map(valid_areas, invalid_areas, user_date, area_type, vacc_doses)
        input("Done! To see the result, open the newly generated vaccmap.svg with a browser.\n"
              "Press any key to quit...")


def update_data():
    """
    Connects to Github via the internet to determine data's freshness
    Presents the user with a choice to download updated data files
    """
    file_paths = {"vaccinations.json": "public/data/vaccinations/vaccinations.json",
                  "population_2020.csv": "scripts/input/un/population_2020.csv"}
    for file_name, remote_path in file_paths.items():
        while True:
            try:
                local_file_date = datetime.fromtimestamp(os.path.getmtime(file_name))
                api_url = f"https://api.github.com/repos/owid/covid-19-data/commits?path={remote_path}&per_page=1"
                last_updated = requests.get(api_url).json()[0]['commit']['committer']['date']
                remote_file_date = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%SZ")
                day_difference = (remote_file_date - local_file_date).days
                if day_difference >= 0:
                    choice = input(f"{file_name} is OUTDATED. It's roughly {str(day_difference + 1)} days old. "
                                   "Would you like to update it? (Y/N): ")
                    if "y" in choice.lower():
                        download_file(file_name, remote_path)
                break
            except requests.exceptions.ConnectionError:
                print("CAN'T CONNECT TO THE INTERNET! Your files might be out of date. "
                      "Try checking your internet connection or Github's status.")
                return
            except PermissionError:
                input(f"PERMISSION ERROR! Cannot access {file_name}. "
                      "It might be open in another program - try closing it, then launch main.py again.\n"
                      "Press any key to quit...")
                sys.exit(0)
            except FileNotFoundError:
                choice = input(f"CANNOT FIND {file_name}! It is required to run the program.\n"
                               "Would you like to download it from Github? (Y/N): ")
                if "y" in choice.lower():
                    try:
                        download_file(file_name, remote_path)
                    except requests.exceptions.ConnectionError:
                        input("CAN'T CONNECT TO THE INTERNET EITHER! :(\n"
                              "Try checking your internet connection or Github's status.\n"
                              "Quitting program...")
                        sys.exit(0)
                else:
                    input("Understood. Quitting program.\n"
                          "Press any key to quit...")
                    sys.exit(0)


def download_file(file_name, remote_path):
    """
    An extension of download_data()
    Downloads specific file from OWID's 'covid-19-data' repo
    """
    download_url = f"https://github.com/owid/covid-19-data/raw/master/{remote_path}"
    downloaded_data = get(download_url, stream=True)
    progress = tqdm(unit="B", unit_scale=True, unit_divisor=1024, desc=file_name)
    with open(file_name, "wb") as f:
        for chunk in downloaded_data.iter_content(chunk_size=1024):
            data_size = f.write(chunk)
            progress.update(data_size)
        progress.close()


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


def collect_data(vacc_data, pop_data_file, area_codes, user_date, vacc_doses, area_type):
    """
    Collects data from the main data file based on provided user preferences
    Returns a table of processed data to be used in generate_map
    """
    valid_areas = {}
    invalid_areas = {}
    pop_data = csv.DictReader(pop_data_file)
    for country in vacc_data:
        # TODO: reduce the IFS here
        OWID_area_code = country["iso_code"]
        if OWID_area_code not in area_codes:
            continue
        if area_type == "country":
            if OWID_area_code.startswith("OWID"):
                continue
        else:
            if not OWID_area_code.startswith("OWID"):
                continue
        total_pop = check_population(OWID_area_code, pop_data, pop_data_file)
        area_data = country["data"][::-1]
        area_code = area_codes[OWID_area_code]
        valid_areas[area_code] = calc_vacc_perc(total_pop, vacc_doses, area_data, user_date)
        if area_code not in valid_areas or valid_areas[area_code] == 0:
            invalid_areas[area_code] = valid_areas.pop(area_code, 0)
    invalid_areas = fill_map_holes(invalid_areas, valid_areas)
    return valid_areas, invalid_areas


def check_population(OWID_area_code, pop_data, pop_data_file):
    """
    Takes country's area code from vaccinations.json
    Returns country's population number from population_2020.csv
    """
    for country in pop_data:
        if country['iso_code'] == OWID_area_code:
            # DictReader's iterator doesn't reset on its own, I have to do it manually with seek()
            pop_data_file.seek(0)
            return int(country['population'])
    return 0


def calc_vacc_perc(total_pop, vacc_doses, area_data, user_date):
    """
    An extension of collect_data()
    1) Determines whether data exists for the given country and given day.
        a) if it doesn't exist for the given day, attempt to find data within the last 21 days
    2) Calculates vaccination percentage and returns that into the current country's value
    """
    first_available_date = datetime.strptime(area_data[0]["date"], "%Y-%m-%d")
    delta = (user_date - first_available_date).days

    for i in range(0, (22 - delta)):
        day = area_data[i]
        # TODO: see if there's a better looking alternative for these ifs
        vacc_pop = 0
        if "one" in vacc_doses:
            if "people_vaccinated" in day:
                vacc_pop = day["people_vaccinated"]
        else:
            if "people_fully_vaccinated" in day:
                vacc_pop = day["people_fully_vaccinated"]
        return round((vacc_pop / total_pop) * 100, 2)
    return 0


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
        worldmap.add('% vaccinated', valid_areas)
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
