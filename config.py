from multiprocessing import cpu_count

DECKS = {
    'spanish':              {'deck_name': 'Languages::Spanish',             'lang': 'spanish', 'vocab_field': 'Vocab'},
    'korean':               {'deck_name': 'Languages::한국어',              'lang': 'korean', 'vocab_field': 'Vocab'},
    'japanese_personal':    {'deck_name': 'JWrapper::Jap Personal::Vocab',  'lang': 'japanese', 'vocab_field': 'Vocab'},
    'japanese_wk':         {'deck_name': 'JWrapper::Wanikani::Vocab',      'lang': 'japanese', 'vocab_field': 'Vocab'},
    'english':              {'deck_name': 'Fluent Languages::English',      'lang': 'english', 'vocab_field': 'Vocab'},
}

deck_id = 'japanese_wk'
DECK_NAME = DECKS[deck_id]['deck_name']
LANGUAGE = DECKS[deck_id]['lang']
VOCAB_FIELD = DECKS[deck_id]['vocab_field']

N_CORES = cpu_count()
N_JOBS_EXTRACT = 5 * N_CORES
N_JOBS_UPDATE = 4 * N_CORES

OUTPUT_DIRECTORY = './outputs'
ANKI_CONNECT_URL = 'http://localhost:8765'
DATE_FORMAT = r'%Y%m%d-%H%M%S'