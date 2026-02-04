import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-default-123')
    ENSEMBL_URL = "https://rest.ensembl.org"
    REQ_TIMEOUT = 15
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # Configuração de Logs
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')