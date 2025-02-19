import argparse
from datetime import datetime
import re
from typing import List
from joblib import Parallel, delayed
from tqdm import tqdm

from config import DATE_FORMAT, DECK_NAME, LANGUAGE, N_JOBS_EXTRACT, N_JOBS_UPDATE, VOCAB_FIELD, deck_id
from utils.app import extract_word_ipa__single, fetch_words_to_update, update_card_ipa__single
from utils.file import save
from utils.scraper import extract_ipa_for_language, get_content
from utils.utils import is_word, load_anki_json, load_most_recent_anki_json, preprocess_phrase, preprocess_word
from utils.config_helper import configure_config


def test_word(word: str, language: str):
    content = get_content(word)

    ipa = extract_ipa_for_language(content, language, word)
    if ipa:
        print(ipa)

def test_phrase(phrase: str, language: str):
    ipas = dict()
    words = phrase.split()
    for word in words:
        word = preprocess_word(word)
        if is_word(word):
            content = get_content(word)
            ipa = extract_ipa_for_language(content, language, word, verbose=True)
            if ipa:
                ipas[word] = ipa
            else:
                ipas[word] = None

    for word, ipa in ipas.items():
        print(f"{word}: {ipa}")

def generate():
    # Fetch words
    words_ids = fetch_words_to_update()
    new_words_ids = dict()
    for word, (note_id, ipa) in words_ids.items():
        new_word = preprocess_phrase(word)
        new_words_ids[new_word] = (note_id, ipa)
    words_ids = new_words_ids
    
    print(f"Words to update: {len(words_ids)}")

    # Initialize counters and progress bar
    total = len(words_ids)
    pbar = tqdm(words_ids.items(), total=total, desc="Processing words")

    # Process words in parallel with progress tracking
    results = Parallel(n_jobs=N_JOBS_EXTRACT)(
        delayed(extract_word_ipa__single)(word, note_id, ipa)
        for word, (note_id, ipa) in pbar
    )
    pbar.close()

    # Process results
    skipped_dict = {}
    updated_words = {}

    for word, (note_id, result), success in results:
        if not success:
            skipped_dict[word] = (note_id, result)
        else:
            try:
                ipa, extra_ipa = result
                updated_words[word] = {"note_id": note_id, "ipa": ipa, "extra_ipa": extra_ipa}
            except Exception as e:
                print(f"Error updating word {word}: {e}")
                skipped_dict[word] = (note_id, result)

    # Save the output
    output = {
        'skipped_words': skipped_dict,
        'updated_words': updated_words
    }

    current_time = datetime.now().strftime(DATE_FORMAT)
    save(output, f"anki@{current_time}.json")
    print(f"Generated IPA for {len(updated_words)} / {total} words. {len(skipped_dict)} / {total} failed.")

def update(json_name):
    if json_name == "latest":
        anki_json, original_time = load_most_recent_anki_json()
    else:
        pattern = re.compile(r"\w+@\d{8}-\d{6}.json")
        if not pattern.match(json_name):
            raise ValueError("Invalid JSON file name.")
        anki_json, original_time = load_anki_json(json_name)

    updated_words = anki_json.get('updated_words', {})
    amt_of_words = len(updated_words)

    # Prepare the arguments for parallel processing
    args = [(word, info['note_id'], info['ipa'], info['extra_ipa']) 
            for word, info in updated_words.items()]

    # Process in parallel with progress bar
    results = Parallel(n_jobs=N_JOBS_UPDATE)(
        delayed(update_card_ipa__single)(word, note_id, ipa, extra_ipa) 
        for word, note_id, ipa, extra_ipa in tqdm(args, desc="Updating IPAs")
    )

    # Process results
    success = []
    errors = []
    for word, status, error in results:
        if status:
            success.append(word)
        else:
            errors.append((word, error))

    # Save the output
    error_words = [word for word, error in errors]
    after_skipped_words = {word: info for word, info in updated_words.items() if word in error_words}
    after_updated_words = {word: info for word, info in updated_words.items() if word not in error_words}

    after_output = {
        "skipped_words": after_skipped_words,
        "updated_words": after_updated_words,
    }

    save(after_output, f"after_anki@{original_time}.json")
    print(f"At first try: updated {len(success)} / {amt_of_words} words. {len(errors)} / {amt_of_words} failed.")

    ### Try again for the failed instances ###
    # Here we don't parallelize, since I only found errors originating from too many handles at the same time so far
    after_anki_json, _ = load_anki_json(f"after_anki@{original_time}.json")

    # Continue only if needed
    if len(after_anki_json["skipped_words"]) == 0:
        return

    skipped_words = after_anki_json.get("skipped_words", {})
    amt_of_words = len(skipped_words)

    args = [(word, info['note_id'], info['ipa'], info['extra_ipa']) 
            for word, info in skipped_words.items()]
    
    final_skipped_words = {}
    final_updated_words = {}

    for word, note_id, ipa, extra_ipa in tqdm(args, desc="Updating IPAs"):
        try:
            update_card_ipa__single(word, note_id, ipa, extra_ipa)
            final_updated_words[word] = {"note_id": note_id, "ipa": ipa, "extra_ipa": extra_ipa}
        except Exception as e:
            print(f"Error updating word {word}: {e}")
            final_skipped_words[word] = {"note_id": note_id, "ipa": ipa, "extra_ipa": extra_ipa}
            continue

    # Save the output
    final_output = {
        "skipped_words": final_skipped_words,
        "updated_words": final_updated_words,
    }

    save(final_output, f"final_anki@{original_time}.json")
    print(f"At retry: updated {len(final_updated_words)} / {amt_of_words} words. {len(final_skipped_words)} errors / {amt_of_words} failed.")


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

    if args.config:
        configure_config()
        exit()


    print(f"Did you check the config.py file to ensure the settings are correct?")
    print("(If you want help with editing the config, close this and run `runconfig.bat`, then come back)")

    print()
    print(f"Current configuration is: {deck_id} ({DECK_NAME}, {LANGUAGE}, {VOCAB_FIELD})")
    response = input(f"Type 'y' to continue, or anything else to end: ")
    if response.lower() != "y":
        exit()
    print("Ok let's get started...\n")
    
    if args.test_word:
        word, language = args.test_word
        print(f"Testing [[ {language} ]] language with the word [[ {word} ]]\n...\n")
        test_word(word, language)
    elif args.test_phrase:
        phrase, language = args.test_phrase
        print(f"Testing [[ {language} ]] language with the phrase [[ {phrase} ]]\n...\n")
        test_phrase(phrase, language)
    elif args.test_gen:
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