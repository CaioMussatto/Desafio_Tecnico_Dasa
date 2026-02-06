"""
EntryPoint da Aplicação.
Inicia o servidor Flask respeitando as configurações de host e debug.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)