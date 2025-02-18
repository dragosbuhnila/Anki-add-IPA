# What's this?
This is a simple python program to update your Anki cards with IPA pronunciation data.  
As of now, the only source I use is en.wiktionary.org.  

The program should work with any language, but I haven't fine tuned it to deal with multiple words or inflections yet. Based on wiktionary's IPA content success rate may go down (e.g. for english words like bearish have no IPA, for japanese 死神 doesn't either as it's a less common spelling).  

I used the program for Korean, Spanish, English, and Japanese, with success rates ranging from ~70% to ~90% based on language.

# How To Use

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

### Install Python Env and Run (Windows)
Note: don't run before checking [config.py](#configpy) is correct, also, do a backup of your collection before (although the program shouldn't be able to break it).

1) Download or clone this repository (for downloading, click the green button with `code` and download as zip) 

2) Install a working python with poetry if not available yet (I used 3.13.2 when developing, but other versions should work too)
    1) Download `python` from Download Python from [python.org/downloads](https://www.python.org/downloads/)
    2) Install `poetry` by running `pip install poetry` on PowerShell (just search for `PowerShell` in start)
        **NOTE:** If you have issues where pip or python isn’t found, check your PATH. If you need help, ask chatgpt or open an issue on this repo.
    3) Open a terminal in the repository directory (Anki-add-IPA)
    4) Now install the dependencies and activate the venv
        ```
        poetry config virtualenvs.in-project true
        poetry install
        poetry env activate
        ```

3) Install the ankiconnect extension for python (https://ankiweb.net/shared/info/2055492159) if you don't have it yet.
    NOTE: my Anki installation as of dev time is Version 24.06.3 Python 3.9.18 Qt 6.6.2 PyQt 6.6.1, and AnkiConnect idk.

4) Run the application:
    1) If you closed the terminal, open it again in the folder (Anki-add-IPA), and run again `poetry env activate`
    2) Run the actual app: 
    ```python
    python ./main.py --app
    ```

5) You're done.  
   If, after running the application, you see an error ratio that is too high, check some of the words that failed in the output file 
   (named like `anki@YYYYDDMM-HHMMSS.json`). Search for those words manually on en.wiktionary.org.  
   - If the word isn’t there, it’s normal for the program not to work on that word.  
   - If it is there, try running the application again, as you may have encountered temporary timeout errors.


### Install Python Env and Run (Mac)
Note: The Mac guide is just slighly adjusted from the Windows guide using chatgpt o3-mini, as I don't have a Mac device to test with.
Note: don't run before checking [config.py](#configpy) is correct, also, do a backup of your collection before (although the program shouldn't be able to break it).

1) Download or clone this repository  
   (for downloading, click the green "Code" button and choose "Download ZIP").

2) Install a working Python with Poetry if you haven’t yet.  
   (I used Python 3.13.2 when developing, but other versions should work too)
   1) Download Python from [python.org/downloads](https://www.python.org/downloads/).  
   2) Install Poetry by running:  
      ```bash
      pip install poetry
      ```  
      **NOTE:** If you have issues where pip or python isn’t found, check your PATH. If you need help, ask chatgpt or open an issue on this repo.
   3) Open Terminal and navigate to the repository directory.
   4) Now install the dependencies and activate the venv
        ```
        poetry config virtualenvs.in-project true
        poetry install
        poetry env activate
        ```

3) Install the AnkiConnect extension for Anki, if you haven't yet.  
   Download it from: [https://ankiweb.net/shared/info/2055492159](https://ankiweb.net/shared/info/2055492159)

   **NOTE:**  
   My Anki installation (at time of development) is Version 24.06.3, Python 3.9.18, Qt 6.6.2, and PyQt 6.6.1, with AnkiConnect version unknown.

4) Run the application:
   1) If you closed Terminal, open it again in the repository folder and activate the venv:
      ```bash
      poetry env activate
      ```
   2) Run:
      ```bash
      python ./main.py --app
      ```

5) You’re done.  
   If, after running the application, you see an error ratio that is too high, check some of the words that failed in the output file 
   (named something like `anki@xxx.json`). Search for those words manually on en.wiktionary.org.  
   - If the word isn’t there, it’s normal for the program not to work on that word.  
   - If it is there, try running the application again, as you may have encountered temporary timeout errors.

# What's next
The first thing I'll do in the future is making it work decently with inflected and multiple words, as I need it for Spanish (+ allow for extra things in the word field, such as duplicate markers like `Facturar (2)`).  
Someday I'll also try and make it an actual extension but it may take a while as I have zero knowledge about how to deal with the Anki base.
