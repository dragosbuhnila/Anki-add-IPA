from datetime import datetime
import re
from typing import Dict, Tuple

from joblib import Parallel, delayed
from tqdm import tqdm

from utils.anki import get_meaning, request_anki, get_ipa, get_vocab
from utils.file import save
from utils.scraper import get_content, extract_ipa_for_language
from config import ANKI_CONNECT_URL, DATE_FORMAT, DECK_NAME, LANGUAGE, N_JOBS_EXTRACT, N_JOBS_UPDATE
from utils.utils import is_word, load_anki_json, load_most_recent_anki_json, preprocess_phrase, preprocess_word

def fetch_words_to_update(debug: bool = False, from_to: Tuple[int, int] = (0, 10_000), 
                          force_update: bool = False, verbose: bool = False) -> Dict[str, Tuple[int, None]]:
    # Fetch all Korean note IDs
    note_ids = request_anki('findNotes', query=f'deck:"{DECK_NAME}"')

    if debug:
        notes_info = request_anki('notesInfo', notes=note_ids[:10])
    else:
        notes_info = request_anki('notesInfo', notes=note_ids[from_to[0]:from_to[1]])
    
    if verbose:
        print(f"notes: {notes_info}")

    # Keep only those with empty IPA field
    if not force_update:
        notes_info = [note for note in notes_info if get_ipa(note) == ""]

    # Deal with reverse cards
    revnotes_info = [note for note in notes_info if "(rev)" in get_vocab(note).lower() or "(reverse)" in get_vocab(note).lower()]
    notes_info = [note for note in notes_info if "(rev)" not in get_vocab(note).lower() and "(reverse)" not in get_vocab(note).lower()]
    
    # Return words
    notes = {get_vocab(note): (note['noteId'], None) for note in notes_info} # The tuple contains the note, ID, and the IPA
    notes.update({get_meaning(note): (note['noteId'], None) for note in revnotes_info})

    return notes

def extract_word_ipa__single(word_or_phrase, note_id, ipa, verbose=False):
    """Process a single word (or phrase) and return the results"""
    try:
        words = word_or_phrase.split()
        results = []
        for word in words:
            web_content = get_content(word, save_response=False)
            if not web_content:
                # # TODO: Uninflect the word and try again
                # uninflected_word = uninflect_word(word)
                # web_content = get_content(uninflected_word, save_response=False)
                # if not web_content:
                #     if verbose: print(f"Error fetching content for word {word}")
                #     results.append((word, (note_id, ipa), None))
                #     continue
                if verbose: print(f"Error fetching content for word {word}")
                results.append((word, (note_id, ipa), None))
                continue

            result = extract_ipa_for_language(web_content, LANGUAGE, word)
            if not result:
                if verbose: print(f"Error extracting IPA for word {word}")
                results.append((word, (note_id, ipa), None))
                continue

            results.append((word, (note_id, result), True))

        # Create the final result
        ipa_text = []
        ipa_other = False
        success = False
        for result in results:
            _, (_, ipa_tuple), s = result
            if ipa_tuple is not None:
                if ipa_tuple[1] != True:
                    ipa_other = True
                ipa_text.append(ipa_tuple[0].strip("/[]"))
            if s == True:
                success = True
        ipa_text = "/" + " ".join(ipa_text) + "/"
        
        return word_or_phrase, (note_id, (ipa_text, ipa_other)), success
    except Exception as e:
        print(f"Error processing word/phrase {word_or_phrase}: {e}")
        return word_or_phrase, (note_id, ipa), None

def update_card_ipa__single(word: str, note_id: int, ipa: str, extra_ipa: bool):
    """Update a single note's IPA fields"""
    try:
        # Leave the extra-IPA field empty in case
        if extra_ipa == True:
            updated_note = {
                'id': note_id,
                'fields': {
                    'IPA': ipa,
                    'Extra-IPA': "True",
                }
            }
        elif extra_ipa == False:
            updated_note = {
                'id': note_id,
                'fields': {
                    'IPA': ipa,
                }
            }
        else:
            raise ValueError(f"Invalid value for extra_ipa for {word}: should be either True or False, but is {extra_ipa}")

        # Update the note
        request_anki('updateNoteFields', note=updated_note)
        return word, True, None  # Success
    except Exception as e:
        return word, False, str(e)  # Error
    

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
            content = get_content(word, verbose=True)
            ipa = extract_ipa_for_language(content, language, word, verbose=True)
            if ipa:
                ipas[word] = ipa
            else:
                ipas[word] = None

    if len(ipas) == 0:
        print("No IPA found.")
        return
    
    for word, ipa in ipas.items():
        print(f"{word}: {ipa}")

def generate(force_update: bool = False):
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
    # Check if AnkiConnect is on @ ANKI_CONNECT_URL
    try:
        request_anki('version')
    except Exception as e:
        print(f"Error connecting to Anki, check if AnkiConnect is on @ {ANKI_CONNECT_URL}.")
        return

    # Load the JSON file with the words to update, containing the IPA and note IDs, and the original time of creation of that JSON
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