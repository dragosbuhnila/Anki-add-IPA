# What's this?
This is a simple python program to update your Anki cards with IPA pronunciation data.  
As of now, the only source I use is en.wiktionary.org.  
The program should work with any language, but I haven't fine tuned it to deal with multiple words or inflections yet.  

# How to use
Note: don't run before checking [config.py](#configpy) is correct, also, do a backup of your collection before (although the progrma shouldn't be able to break it).

### Setup Your Cards and Config
You need to have an empty field called `IPA`. If it's not empty, the word will be skipped.
You also need an `Extra-IPA` field, which stores whether the word has more etymologies which may have different pronunciations.

Setup the config file based on the name of your deck and the field in which the word is found. 
How do you set it up?  
1) Edit decks to match your own decks' information. In `DECKS` you have:  
- a series of ids on the left, which are used in the following lines. You can keep the name of the language or anything you'd like.  
- the `deck_name` as the first field on the right  
- the `language` of the deck as the second field on the right  
- the name of the field which contains the word (`vocab_field`), as the third field on the right  
If you didn't understand, you can ask chatgpt to help you by giving him these instructions. I'll create a script to help editing this ASAP.  

Example:
```python
DECKS = {
    'spanish':              {'deck_name': 'Languages::Spanish', 'lang': 'spanish', 'vocab_field': 'Vocab'},
    'korean':               {'deck_name': 'Languages::한국어',   'lang': 'korean',  'vocab_field': 'Vocab'},
    'english':              {'deck_name': 'Languages::English', 'lang': 'english', 'vocab_field': 'Vocab'},

    'japanese_personal':    {'deck_name': 'JWrapper::Jap Personal::Vocab',  'lang': 'japanese', 'vocab_field': 'Vocab'},
    'japansese_wk':         {'deck_name': 'JWrapper::Wanikani::Vocab',      'lang': 'japanese', 'vocab_field': 'Vocab'},
}
```

2) Set `deck_id` to the id that you want. For example if you want to update your korean deck, you just set `deck_id = 'korean'`

3) If you edited the port for AnkiConnect, edit `ANKI_CONNECT_URL` accordingly.

### Install Things

1) Install a working python with poetry if not available yet (I used 3.13.2 when developing, but other versions should work too)
    1) Download from https://www.python.org/downloads/
    2) Install poetry by running `pip install poetry`
    3) If you have problems like pip not being found or python not being found, check if there's a PATH problem (if you're not able to solve this ask chatgpt or open an issue on this repo)

2) Install the ankiconnect extension for python (https://ankiweb.net/shared/info/2055492159)

3) Download or clone this repository (for downloading, click the green button with `code` and download as zip) 

4) Open a terminal in TODOinsert_folder_name and run poetry install (you may need to activate the venv)

## config.py