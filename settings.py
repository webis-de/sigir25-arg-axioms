import sys
from pathlib import Path
import configs as cfg
import os
from dotenv import load_dotenv
os.environ["TOKENIZERS_PARALLELISM"] = "false"

PROJECT_ROOT = Path(__file__).resolve().parent

# DEFINITION OF PATHS
AXIOMS_CACHE_EMBEDDINGS_PATH = PROJECT_ROOT / '_axioms_cache_embeddings'
CACHE_PATH = PROJECT_ROOT / '_cache_dir'
RAW_DATA_SAVE_PATH = PROJECT_ROOT / '_experiments_results_raw'
QRELS_SAVE_PATH = PROJECT_ROOT / '_storage_qrels'

for path in [AXIOMS_CACHE_EMBEDDINGS_PATH, CACHE_PATH, RAW_DATA_SAVE_PATH, QRELS_SAVE_PATH]:
    os.makedirs(path, exist_ok=True)


PATH_TOUCHE_21_FROM_INDEX_PKL_DATA = PROJECT_ROOT / 'data_tmp' / 'touche21_from_index.pkl'
STORAGE_SBERT_EMBEDDINGS_SBERT_RANKER_PKL_DATA = PROJECT_ROOT / 'data_tmp' / 'touche21_embeddings_data_store_sbert_ranker.pkl'

# has to be set by each implementation
DATA = None
DATASET = None
DATASET_NAME_SHORT = None
DATASET_INDEX_DIR = None
TOUCHE_PARTICIPANT_DIR = None

def set_data_manually(dataset_name): # in case data is specified manually
    global DATASET
    global DATASET_NAME_SHORT
    global DATASET_INDEX_DIR
    global DATA
    if dataset_name not in cfg.configs:
        sys.exit(f"Dataset {dataset_name} not found in configs")
    DATA = cfg.configs[dataset_name]
    DATASET = DATA['dataset']
    DATASET_NAME_SHORT = DATA['dataset_short']
    DATASET_INDEX_DIR = PROJECT_ROOT / f'_{DATASET_NAME_SHORT}_index'


BASE_RETRIEVER = 'DirichletLM'
SBERT = 'sbert'
STMC1 = 'stmc1'

SENTENCES = 'sentences'
ARGUMENT_UNITS = 'arguments'
SENTENCE_STYLES = [SENTENCES , ARGUMENT_UNITS]

DOCNOS = 'docnos'
TEXTS = 'texts'
TASK = 'task'


# Socket Terms
DOCUMENT_RANKING = 'DOCUMENT_RANKING'
SOCKET_DOCUMENT1  = 'DOCUMENT1'
SOCKET_DOCUMENT2 = 'DOCUMENT2'
SOCKET_QUERY = 'QUERY'
SOCKET_COMPARE_METHOD = 'COMPARE_METHOD'
EMBEDD_SINGLE = 'EMBEDD_SINGLE'
BATCH_EMBEDDING = 'BATCH_EMBEDDING'
TARGER_ANALYSIS = 'TARGER_ANALYSIS'
MAX = 'MAX'
MEAN = 'MEAN'
SOCKET_DATASET_KEY = 'DATASET_KEY'

OK = 'OK'
REQUEST = 'request'
SOCKET = 'socket'
SERVER_COMMUNICATION_METHOD = SOCKET # specify communications style with Embeddings Getter
SOCKET_NBR = 5000


# Styles how to embed the documents
STYLE_AUS_SINGLE_SENTENCE = 'AUS_SINGLE_SENTENCE'
STYLE_AUS_FULL_DOCUMENT= 'AUS_FULL_DOCUMENT'
STYLE_SENTENCES = 'SENTENCES'

# TERMS for Targer are stored in TASK_INFO dict
TASK_INFO_TARGER_OWN_SENTENICER= 'TARGER_OWN_SENTENICER'

SOCKET_EMBEDDING_STYLE = 'SOCKET_EMBEDDING_STYLE'
SOCKET_TASK_INFO = 'SOCKET_TASK_INFO'
SOCKET_TASK = 'SOCKET_TASK'
SOCKET_SENTENICE = 'SOCKET_SENTENICE'
SOCKET_EMBEDDING_MODEL = 'SOCKET_EMBEDDING_MODEL'
EMBEDDING = 'EMBEDDING'


SOCKET_DOCNO = 'SOCKET_DOCNO'
SOCKET_DOCUMENT = 'SOCKET_DOCUMENT'


TARGER_TOTAL_TRIES = 3

