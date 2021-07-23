# covid-vaccination-map
Python program that uses Our World In Data's vaccination data to generate a world map.

![image](https://i.gyazo.com/f8e9174a7c9967441fe1edbea9d4875e.png)

# Requirements
- Python (3.5 or higher) 
- [Pygal](http://www.pygal.org/en/stable/) (*pip install pygal* & *pip install pygal-maps-world*)
- [tqdm](https://github.com/tqdm/tqdm) (*pip install tqdm*)
- [Requests](https://docs.python-requests.org/en/master/) (*pip install requests*)
- An Internet connection to download and/or update data files

# Usage
Fire up main.py and follow the instructions. You will be asked to specify a date & the types of data you'd like to see on the world map.

# Known issues
- Vaccmap.svg's background is black if the file is opened in anything other than a modern browser (Chrome, Firefox, Edge etc.) This is a quirk of the Pygal library and is not something I can fix.
- tqdm does not show a progress bar! This is sadly due to my own lack of knowledge - I could not find a way to reliably calculate the total file size to be downloaded due to it being compressed on Github's servers.

# Credits
- Pygal was made by [Kozea](https://github.com/Kozea).
- Vaccination data kindly provided by [Our World In Data](https://ourworldindata.org/covid-vaccinations), namely Mathieu E., Ritchie H., Ortiz-Ospina E. and others.

# Notes
- This is my first project in my programming journey! If you have tips on how I can improve this program, please feel free to message me and let me know.
- There is a way to run this program without an internet connection - just pre-download the necessary data files from OWID's Github [here](https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/vaccinations.json) and [here](https://github.com/owid/covid-19-data/blob/master/scripts/input/un/population_2020.csv) and put them in the same directory as the rest of the files.
- To alleviate the scarcity of data in some countries, the program checks for the most recent, available data for each country for up to 3 weeks away from the user-given date.
