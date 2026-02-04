from flask import Blueprint, jsonify, render_template
from .core import EnsemblClient
from .utils import clean_rsid

main_bp = Blueprint('main', __name__)
client = EnsemblClient()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/variant/<rsid>')
def get_variant(rsid):
    try:
        # Sanitização da entrada via utilitário re
        sanitized_rsid = clean_rsid(rsid)
        
        variant_obj = client.get_variant_data(sanitized_rsid)
        if not variant_obj:
            return jsonify({"error": "Identificador não localizado na base Ensembl"}), 404
            
        # Utilizando model_dump() para serialização Pydantic v2
        return jsonify(variant_obj.model_dump())
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400