from typing import Tuple

from utils.anki import request_anki, get_ipa, get_vocab
from utils.scraper import get_content, extract_ipa_for_language
from config import DECK_NAME, LANGUAGE

def fetch_words_to_update(debug: bool = False, from_to: Tuple[int, int] = (0, 10_000), verbose: bool = False):
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
    words_ids = {get_vocab(note): (note['noteId'], None) for note in notes_info} # The tuple contains the note ID and the IPA

    return words_ids

def extract_word_ipa__single(word, note_id, ipa):
    """Process a single word and return the results"""
    try:
        web_content = get_content(word, save_response=False)
        if not web_content:
            print(f"Error fetching content for word {word}")
            return word, (note_id, ipa), None

        result = extract_ipa_for_language(web_content, LANGUAGE, word)
        if not result:
            print(f"Error extracting IPA for word {word}")
            return word, (note_id, ipa), None

        return word, (note_id, result), result
    except Exception as e:
        print(f"Error processing word {word}: {e}")
        return word, (note_id, ipa), None

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