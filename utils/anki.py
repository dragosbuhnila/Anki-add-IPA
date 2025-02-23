import requests

from config import ANKI_CONNECT_URL, VOCAB_FIELD, MEANING_FIELD

def request_anki(action, **params):
    request = {'action': action, 'params': params, 'version': 6}
    response = requests.post(ANKI_CONNECT_URL, json=request).json()
    if response.get('error'):
        raise Exception(response['error'])
    return response['result']

def fetch_all_deck_names():
    try:
        deck_names = request_anki('deckNames')
        print("Deck names:", deck_names)
        return deck_names
    except Exception as e:
        print(f"Error fetching deck names: {e}")
        return []
    
def get_vocab(note):
    if VOCAB_FIELD not in note['fields']:
        raise Exception(f"Field '{VOCAB_FIELD}' not found in note #{note['noteId']} of model {note['modelName']}\n"
                        + f"Available fields: {note['fields']}")
    return note['fields'][VOCAB_FIELD]['value'].strip()

def get_meaning(note):
    if MEANING_FIELD not in note['fields']:
        raise Exception(f"Field '{MEANING_FIELD}' not found in note #{note['noteId']} of model {note['modelName']}")
    return note['fields'][MEANING_FIELD]['value'].strip()

def get_ipa(note):
    if 'IPA' not in note['fields']:
        raise Exception(f"Field 'IPA' not found in note #{note['noteId']} of model {note['modelName']}")
    return note['fields']['IPA']['value'].strip()

