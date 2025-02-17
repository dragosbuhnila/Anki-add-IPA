import requests

from config import ANKI_CONNECT_URL, VOCAB_FIELD

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
    return note['fields'][VOCAB_FIELD]['value'].strip().strip("-")

def get_ipa(note):
    return note['fields']['IPA']['value'].strip()

