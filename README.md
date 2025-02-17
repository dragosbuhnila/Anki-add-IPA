# What's this?
This is a simple python program to update your Anki cards with IPA pronunciation data.  
As of now, the only source I use is en.wiktionary.org.  
The program should work with any language, but I haven't fine tuned it to deal with multiple words or inflections yet.  

# How to use
Note: don't run before checking [config.py](#configpy) is correct, also, do a backup of your collection before (although the progrma shouldn't be able to break it).

1) Install a working python with poetry if not available yet (I used 3.13.2 when developing, but other versions should work too)
    1) Download from https://www.python.org/downloads/
    2) Install poetry by running `pip install poetry`
    3) If you have problems like pip not being found or python not being found, check if there's a PATH problem (if you're not able to solve this ask chatgpt or open an issue on this repo)

2) Download or clone this repository (for downloading, click the green button with `code` and download as zip) 

3) Open a terminal in TODOinsert_folder_name and run poetry install
... etc etc


## config.py