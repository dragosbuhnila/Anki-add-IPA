from typing import Dict, Tuple

from utils.anki import request_anki, get_ipa, get_vocab
from utils.scraper import get_content, extract_ipa_for_language
from config import DECK_NAME, LANGUAGE

def fetch_words_to_update(debug: bool = False, from_to: Tuple[int, int] = (0, 10_000), verbose: bool = False) -> Dict[str, Tuple[int, None]]:
    # Fetch all Korean note IDs
    note_ids = request_anki('findNotes', query=f'deck:"{DECK_NAME}"')

    if debug:
        notes_info = request_anki('notesInfo', notes=note_ids[:10])
    else:
        notes_info = request_anki('notesInfo', notes=note_ids[from_to[0]:from_to[1]])
    
    if verbose:
        print(f"notes: {notes_info}")

    # Keep only those with empty IPA field
    notes_info = [note for note in notes_info if get_ipa(note) == ""]
    
    # Return words
    words_ids = {get_vocab(note): (note['noteId'], None) for note in notes_info} # The tuple contains the note, ID, and the IPA

    return words_ids

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