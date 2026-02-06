from flask import Blueprint, jsonify, render_template
from .core import EnsemblClient
from .utils import clean_rsid

# Criação do Blueprint para modularizar as rotas e facilitar escalabilidade
main_bp = Blueprint('main', __name__)

# Instância única do cliente Ensembl para reutilização
client = EnsemblClient()

@main_bp.route('/')
def index():
    """
    Rota principal: Renderiza a única página.
    O frontend (main.js) cuidará da interatividade.
    """
    return render_template('index.html')

@main_bp.route('/api/variant/<rsid>')
def get_variant(rsid):
    """
    Endpoint da API REST para consulta de variantes.
    
    Processo:
    1. Sanitiza a entrada (remove caracteres perigosos).
    2. Consulta o Core (EnsemblClient).
    3. Serializa a resposta usando Pydantic.
    """
    try:
        # Sanitização da entrada via utilitário re
        sanitized_rsid = clean_rsid(rsid)
        # Chamada ao motor de processamento
        variant_obj = client.get_variant_data(sanitized_rsid)
        if not variant_obj:
            return jsonify({"error": "Identificador não localizado na base Ensembl"}), 404
            
        # Utilizando model_dump() para serialização Pydantic v2
        return jsonify(variant_obj.model_dump())
        
    except ValueError as e:
        # Retorna erro 400 (Bad Request) se a sanitização falhar
        return jsonify({"error": str(e)}), 400