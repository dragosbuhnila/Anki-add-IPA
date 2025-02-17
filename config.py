from multiprocessing import cpu_count

OUTPUT_DIRECTORY = "./outputs"
ANKI_CONNECT_URL = 'http://localhost:8765'
DECK_NAME = 'Languages::Spanish'
LANGUAGE = 'spanish'
VOCAB_FIELD = 'Vocab'
N_CORES = cpu_count()
N_JOBS = 5 * N_CORES
N_JOBS_UPDATE = 4 * N_CORES
DATE_FORMAT = r'%Y%m%d-%H%M%S'