import os

################################################################################
################################################################################
################################################################################

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CONF_DIR = os.path.join(ROOT_DIR, 'conf')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
PICKLED_MODELS_DIR = os.path.join(DATA_DIR, 'pickled_models')
TOOLS_DIR = os.path.join(ROOT_DIR, 'utils')

DEFAULT_DB_PATH = os.path.join(ROOT_DIR, 'database.db')

DT_STRING_FORMATTER = '%m-%d-%Y %H:%M:%S'
