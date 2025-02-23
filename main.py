import argparse

from config import DECK_NAME, LANGUAGE, VOCAB_FIELD, deck_id
from utils.app import test_phrase, test_word, generate, update
from utils.config_helper import configure_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Wiktionary IPA Scraper and Anki Updater')
    
    parser.add_argument('--test_word', nargs=2, metavar=('WORD', 'LANGUAGE'),
                      help='Parse a single word and see the extracted IPA, alongside a boolean '
                        + 'indicating whether other etymologies with potentially different readings are present.\n'
                        + 'Takes two arguments: WORD and LANGUAGE (e.g., "책 korean")')
    
    parser.add_argument('--test_phrase', nargs=2, metavar=('PHRASE', 'LANGUAGE'),
                        help='Parse a phrase and see the extracted IPA for each word, alongside a boolean '
                        + 'indicating whether other etymologies with potentially different readings are present.\n'
                        + 'Takes two arguments: PHRASE and LANGUAGE (e.g., "책 읽다 korean)')
    
    parser.add_argument('--test_gen', action='store_true',
                        help='Test the Anki collection update process without actually updating. Results are saved to a file.\n')
    
    parser.add_argument('--update', metavar='JSON_NAME',
                    help='Update the Anki collection with the IPAs extracted from the JSON file. '
                    + 'The JSON file should be in the outputs directory.\n'
                    + 'Takes one argument: JSON_NAME. One between "anew", "latest", and "anything@YYYYMMDD-HHMMSS.json"')

    parser.add_argument('--app', action='store_true',
                        help='Update the Anki collection: scrape the IPAs from wiktionary and add them to cards that need it.\n')

    parser.add_argument('--config', action='store_true',
                        help='Launch the GUI configuration editor to update the deck settings in config.py.')
    

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # 1) Configuration Editor
    if args.config:
        configure_config()
        exit()

    # 2) Single Word or Phrase Tests
    if args.test_word:
        word, language = args.test_word
        print(f"Testing [[ {language} ]] language with the word [[ {word} ]]\n...\n")
        test_word(word, language)
        exit()
    elif args.test_phrase:
        phrase, language = args.test_phrase
        print(f"Testing [[ {language} ]] language with the phrase [[ {phrase} ]]\n...\n")
        test_phrase(phrase, language)
        exit()


    # 3) Anki Related Tests and Actual Updates
    print(f"Did you check the config.py file to ensure the settings are correct?")
    print("(If you want help with editing the config, close this and run `runconfig.bat`, then come back)")

    print()
    print(f"Current configuration is: {deck_id} ({DECK_NAME}, {LANGUAGE}, {VOCAB_FIELD})")
    response = input(f"Type 'y' to continue, or anything else to end: ")
    if response.lower() != "y":
        exit()
    print("Ok let's get started...\n")
    

    if args.test_gen:
        print(f"Testing the Anki collection update process for deck [[ {DECK_NAME} ]]\n...\n")
        generate()
    elif args.update:
        if args.update == "latest":
            print(f"Updating the Anki collection with the latest JSON file\n...\n")
        else:
            print(f"Updating the Anki collection with the JSON file [[ {args.update} ]]\n...\n")
        update(args.update)
    elif args.app:
        print(f"Updating the Anki collection\n...\n")
        generate()
        update("latest")