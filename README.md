# covid-vaccination-map
Python program that uses Our World In Data's vaccination data to generate a world map.

# Requirements
- Python (3.5 or higher) 
- [Pygal](http://www.pygal.org/en/stable/)
- 7zip or something else to unpack the included OWID data file (alternatively, download the .json file from [OWID's website](https://ourworldindata.org/covid-vaccinations))

# Usage
Unpack the included .json data file and put all the included files in the same directory. Fire up main.py and follow the instructions. 
After the program's done generating the world map, you can access it by opening the newly created vaccmap.svg (preferably on a modern browser) in the same directory. 

# Known issues
- Many countries may have no data assigned to them due to no data being available on the day given by the user. 
This will soon be fixed by having the program look at up to 2 previous weeks to grab data from the past instead.
- The date range is hard-coded, not letting the user access fresh data from OWID.
This will soon be fixed by having the program figure out the latest accessible date in the OWID data file.

# Credits
- Pygal was made by [Kozea](https://github.com/Kozea)
- Vaccination data kindly provided by [Our World In Data](https://ourworldindata.org/covid-vaccinations), namely Mathieu E., Ritchie H., Ortiz-Ospina E. and others.

# Notes
This is my first project in my programming journey! If you have tips on how I can improve this program, please feel free to message me and let me know.
