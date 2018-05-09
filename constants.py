""" Package Global Constants """
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORPUS_DIR = os.path.join(os.path.dirname(__file__), 'corpus')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

EN_MODEL_DEFAULT = "en"
EN_MODEL_SM = "en_core_web_sm"
EN_MODEL_MD = "en_core_web_md"
