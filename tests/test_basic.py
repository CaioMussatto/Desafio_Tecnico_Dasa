import pytest
from app.main import app

@pytest.fixture
def client():
    """Configura o ambiente de teste do Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    """Verifica se a página inicial (SPA) carrega corretamente."""
    response = client.get('/')
    assert response.status_code == 200

def test_variant_api_rs699(client):
    """
    Teste funcional: Verifica se o rs699 retorna os dados 
    validados conforme o modelo VariantData e integração Ensembl.
    """
    response = client.get('/api/variant/rs699')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Validação do Schema Pydantic v2
    assert data["rsid"] == "rs699"
    assert "chromosome" in data
    assert "position" in data
    assert "alleles" in data
    assert data["alleles"] == "A/G"
    
    # Validação da lógica de genes associados (Set -> List[str])
    assert isinstance(data["genes"], list)
    assert "AGT" in data["genes"]
    
    # Validação dos metadados geográficos para renderização do Mapa 
    assert "highest_maf_lat" in data
    assert "highest_maf_lon" in data
    assert "highest_maf_labels" in data
    assert isinstance(data["highest_maf_lat"], list)

def test_api_invalid_format(client):
    """
    Verifica a eficácia do utilitário de sanitização (Regex) 
    para bloquear formatos de rsID inválidos.
    """
    response = client.get('/api/variant/ID_INVALIDO_123')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_api_not_found(client):
    """
    Verifica o comportamento do sistema quando a API Ensembl 
    não localiza o identificador.
    """
    # rsID inexistente (extremamente improvável)
    response = client.get('/api/variant/rs99999999999999')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data