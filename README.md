# covid-vaccination-map
Python program that uses Our World In Data's vaccination data to generate a world map.

# Requirements
- Python (3.5 or higher) 
- [Pygal](http://www.pygal.org/en/stable/)
- Optionally, download fresh & updated data files from OWID's github [here](https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/vaccinations.json) and [here](https://github.com/owid/covid-19-data/blob/master/scripts/input/un/population_2020.csv).

# Usage
Fire up main.py and follow the instructions. 
After the program's done generating the world map, you can access it by opening the newly created vaccmap.svg - preferably on a modern browser.

# Known issues
- The .svg file's background can be shown as black if opened in anything other than a modern browser (Chrome, Firefox, Edge etc.) This is a quirk of the Pygal library and is not something I can fix.

# TODO's
- Introduce the wonders of the internet to the program by letting the user download the latest data file directly from Github

# Credits
- Pygal was made by [Kozea](https://github.com/Kozea)
- Vaccination data kindly provided by [Our World In Data](https://ourworldindata.org/covid-vaccinations), namely Mathieu E., Ritchie H., Ortiz-Ospina E. and others.

# Notes
This is my first project in my programming journey! If you have tips on how I can improve this program, please feel free to message me and let me know.

To alleviate the scarcity of data in some countries, the program checks for the most recent, available data for each country for up to 3 weeks away from the user-given date.
