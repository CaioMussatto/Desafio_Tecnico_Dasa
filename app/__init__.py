import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from .config import Config

def create_app():
    """
    Factory para inicialização da aplicação Flask.
    Configura logs rotativos e registra os blueprints do sistema.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Garantia da existência do diretório de logs
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])

    # Configuração do log em arquivo (Máximo 1MB por arquivo, mantém 5 backups)
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'], 
        maxBytes=1024 * 1024, 
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # Log simultâneo no terminal para monitoramento em tempo real
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    app.logger.addHandler(console_handler)

    app.logger.info("Ensembl Dashboard Backend - Inicializado com Sucesso")

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app