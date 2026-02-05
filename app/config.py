import os
from pathlib import Path
from dotenv import load_dotenv

# Definição de caminhos base
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    # Segurança e Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'genvar-bio-secret-2026')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Integração Ensembl (Centralizado para o Core)
    ENSEMBL_BASE_URL = "https://rest.ensembl.org"
    TIMEOUT = 15
    
    ENDPOINTS = {
        "variation": "/variation/human/{rsid}?pops=1;phenotypes=1;alt_alleles=1",
        "overlap": "/overlap/region/human/{region}?feature=gene"
    }
    
    # Gerenciamento de Logs (Garante que a pasta exista)
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')

    @classmethod
    def init_app(cls):
        """Cria diretórios necessários na inicialização"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)

# Chamada automática para garantir que a pasta de logs exista
Config.init_app()