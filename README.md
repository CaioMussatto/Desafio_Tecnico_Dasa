# Desafio Técnico - Analista de Bioinformática - Dasa
![Python](https://img.shields.io/badge/python-3.13-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![UV](https://img.shields.io/badge/UV-0.9.17-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Ensembl](https://img.shields.io/badge/Ensembl_REST_API-green?style=for-the-badge&logo=dna&logoColor=white)

Este projeto consiste em uma plataforma full-stack para consulta, visualização e análise de variantes genéticas (rsIDs), consumindo dados da API REST Ensembl. A solução foca em performance, segurança e portabilidade, utilizando as tecnologias mais recentes do ecossistema Python.

## Links de Acesso

* **Ambiente Cloud (Serverless):** [https://desafio-dasa-858905052733.southamerica-east1.run.app](https://desafio-dasa-858905052733.southamerica-east1.run.app)
* **Repositório Docker Hub:** [caiomussatto/desafio_tecnico_dasa](https://hub.docker.com/repository/docker/caiomussatto/desafio_tecnico_dasa/general)


## Arquitetura e Decisões Técnicas

### Core e Backend

* **Python 3.13:** Utilização da versão 3.13 que possui um bom tempo de vida útil e melhorias de performance significativas.
* **Flask + Gunicorn:** Framework ágil para o backend. O projeto utiliza o servidor nativo do Flask para desenvolvimento local Gunicorn em ambiente de produção (Docker/Cloud Run).
* **Gestão de Dependências:** O projeto foi desenvolvido utilizando **astral/uv**, garantindo instalações de pacotes até 10x mais rápidas e resolução de dependências rigorosa. Para compatibilidade, o arquivo `requirements.txt` também é fornecido e mantido.

### Infraestrutura e Nuvem

* **Docker Multi-stage Build:** O Dockerfile foi estruturado em dois estágios. O primeiro realiza a compilação e instalação de dependências, enquanto o segundo (runtime) contém apenas o necessário para execução, resultando em uma imagem leve de 142MB.
* **Base OS (Debian Slim):** Utilizamos a imagem oficial `python:3.13-slim`, baseada na distribuição Debian. Esta escolha garante um sistema operacional estável, com patches de segurança em dia e sem pacotes desnecessários, otimizando o tempo de deploy.
* **Isolamento e Persistência:** Configuração de permissões restritas em diretórios específicos (como `/app/logs`), permitindo que a aplicação gere auditoria sem comprometer a integridade do restante do sistema
* **Segurança de Container:** A aplicação não roda como root. Foi implementado um usuário de sistema dedicado (`appuser`) e permissões restritas em diretórios de logs.
* **Serverless Deployment:** Hospedagem realizada no Google Cloud Run, garantindo escalabilidade automática e isolamento por container.

## Biblotecas Utilizadas

* **[Flask 3.1](https://flask.palletsprojects.com/):** Micro-framework para construção da API REST.
* **[Pydantic v2](https://www.google.com/search?q=https://docs.pydantic.dev/):** Modelagem e validação estrita de dados (Data Enforcement).
* **[Gunicorn 25.0](https://gunicorn.org/):** Servidor WSGI para ambiente de produção.
* **[Flask-Caching](https://flask-caching.readthedocs.io/):** Otimização de performance através de cache de requisições.
* **[Requests](https://requests.readthedocs.io/):** Cliente HTTP para integração com a API Ensembl.
* **[Pytest 9.0](https://docs.pytest.org/):** Suíte de testes automatizados.
* **[Python-dotenv](https://github.com/theskumar/python-dotenv):** Gestão de variáveis de ambiente.

## Estrutura de Pastas

```text
├── app/                        # Módulo principal da aplicação
│   ├── routes.py               # Definição de Blueprints, Endpoints REST e serialização Pydantic v2
│   ├── core.py                 # Core Engine: Orquestração da lógica de negócio e cliente Ensembl
│   ├── models.py               # Schemas Pydantic v2 para validação e serialização de dados
│   ├── coordinates.py          # Mecanismo de geolocalização e processamento de coordenadas para o Mapa
│   ├── config.py               # Gestão de variáveis de ambiente, caminhos base e templates de URLs externas (Ensembl)
│   ├── utils.py                # Utilitários de sanitização e regex para validação de entradas (rsID)
│   ├── main.py                 # Ponto de entrada para execução e inicialização do servidor
│   ├── __init__.py             # Factory da aplicação e configuração de logging (RotatingFileHandler)
│   ├── static/                 # Ativos de frontend (CSS para layout e JS para consumo da API)
│   │   ├── main.js             # Lógica de frontend para consumo da API interna, renderização de mapas e visualização dinâmica
│   │   └── style.css           # Estilização e componentes de interface
│   └── templates/              # Estruturas HTML baseadas em Jinja2
│       ├── base.html           # Layout compartilhado e importações de bibliotecas
│       └── index.html          # View principal do Dashboard de análise
├── logs/                       # Armazenamento de logs persistentes (app.log)
├── tests/                      # Suíte de testes unitários e de integração
│   └── test_basic.py           # Testes de validação de endpoints e schemas
├── Dockerfile                  # Configuração de build multi-stage (Python 3.13)
├── docker-compose.yml          # Orquestração para ambiente de desenvolvimento local
├── pyproject.toml              # Manifesto moderno de dependências via UV
├── uv.lock                     # Lockfile garantindo determinismo na instalação das dependências
└── requirements.txt            # Arquivo de compatibilidade gerado para instaladores pip tradicionais
```

## Engenharia de Dados e Lógica Core

O `EnsemblClient` (`app/core.py`) é o motor de inteligência da aplicação, responsável por transformar dados genômicos brutos em informações estruturadas através de lógica de negócio rigorosa.

### 1. Inteligência Analítica de Frequências (MAF)

A aplicação realiza um processamento específico sobre as frequências populacionais para extrair métricas críticas:

* **Cálculo de Global MAF (1000 Genomes):** Identifica o *Minor Allele Frequency* global utilizando especificamente os dados do 1000 Genomes Project Phase 3, isolando o segundo alelo mais frequente desta coorte.
* **Detecção de Highest MAF (Cross-Project):** O sistema varre as frequências de grandes projetos genômicos como **1000 Genomes Project Phase 3**, **gnomAD (v4.1 genomes/exomes)**, **NCBI ALFA**, **GEM-J**, **TOPMed**, **UK10K** e **Gambian Genome Variation Project**. O algoritmo identifica o maior valor de MAF entre todos esses bancos, pegando o segundo alelo mais frequente, gerenciando empates técnicos e armazenando múltiplos metadados geográficos para representação simultânea no mapa, porém, caso queira, o usuário pode filtrar para a população e encontrar o MAF da mesma
* **Enriquecimento Geo-Espacial:** Cruza os códigos populacionais do Ensembl com o dicionário em `app/coordinates.py`, injetando coordenadas de latitude e longitude para plotagem dinâmica no Dashboard.

### 2. Estratégia de Resiliência e Integração de Endpoints

O sistema utiliza uma arquitetura de busca em cascata para garantir que o mapeamento de genes e variantes seja o mais completo possível, otimizando o consumo da API REST Ensembl:

* **Integração Primária (Variation API):** Utiliza o endpoint `/variation/human/{rsid}` configurado com os parâmetros `pops=1`, `phenotypes=1` e `alt_alleles=1`. Isso permite capturar dados populacionais, associações clínicas, genes associados e diversidade alélica em uma única chamada de rede, reduzindo a latência.
* **Fallback via Overlap (Redundância):** Em casos de variantes localizadas em regiões intergênicas ou de alta densidade, onde o gene não é retornado na busca primária, o sistema utiliza automaticamente o endpoint `/overlap/region/human/{region}` (filtrado por `feature=gene`).
* **Mapeamento Físico:** Através das coordenadas genômicas (Cromossomo, Start, End), a aplicação realiza uma varredura física para identificar genes vizinhos ou sobrepostos, marcando-os com a flag `(overlap)` para garantir a transparência da origem do dado.

### 3. Validação de Dados com Pydantic v2

Toda a comunicação interna é blindada por modelos de dados estritos no `app/models.py`:

* **VariantData:** Consolida o mapeamento GRCh38, as consequências funcionais e a lógica de negócio processada.
* **Integridade de Tipagem:** O uso de Pydantic garante que qualquer inconsistência na API externa seja capturada na camada de transporte, gerando logs de auditoria no `app.log` e impedindo que dados malformados comprometam a interface.

## Funcionalidades Principais

* **Mapeamento Genômico de Precisão:** Visualização explícita do **Cromossomo** e da **Posição** exata do rsID (GRCh38).
* **Análise de População:** Mapeamento geográfico interativo de frequências alélicas.
* **Dashboard de Métricas:** Visualização de Minor Allele Frequency (MAF) e da distribuição populacional.
* **Exportação de Dados:** Capacidade de download dos relatórios gerados em múltiplos formatos (**JSON**, **CSV** e **TSV**) para integração com outras ferramentas de bioinformática.
* **Logs de Auditoria:** Rastreabilidade completa de processos no arquivo `/logs/app.log`.

## Como Executar Localmente

### 1. Clonando o repositório

```bash
git clone https://github.com/CaioMussatto/Desafio_Tecnico_Dasa.git
cd Desafio_Tecnico_Dasa
```

### 2. Via Docker (Recomendado)

Necessário ter o **Docker** instalado: [Download Docker](https://docs.docker.com/get-started/get-docker/)

```bash
docker compose up --build -d
```

Acesse em `http://localhost:5000`.

### 3. Execução Direta via Docker Hub (Acesso Rápido)

Se desejar testar a aplicação sem clonar este repositório, você pode baixar a imagem diretamente do Docker Hub:

```bash
docker pull caiomussatto/desafio_tecnico_dasa:latest
docker run -d --name dasa-app -p 5000:5000 caiomussatto/desafio_tecnico_dasa:latest 
# Acesse em `http://localhost:5000
```

### 4. Via Python (Desenvolvimento)

Necessário **Python 3.13+**: [Download Python](https://www.python.org/downloads/)

Recomenda-se o uso de um ambiente virtual para evitar conflitos de dependências:

**Usando Pip tradicional:**

```bash
# Criar ambiente virtual
python -m venv venv
# Ativar (Linux/macOS)
source venv/bin/activate
# Ativar (Windows)
.\venv\Scripts\activate

# Instalar dependências e rodar
pip install -r requirements.txt
python -m app.main
```

**Usando UV (Alta Performance):**
Instalação do UV: `curl -LsSf https://astral.sh/uv/install.sh | sh` ou `pip install uv`

```bash
uv run python -m app.main
```

## Validação de Qualidade (Testes)

O projeto utiliza **Pytest** para garantir a integridade das funcionalidades. Foram implementados **4 testes cruciais**:

1. **`test_homepage`**: Garante que o servidor Flask está ativo e servindo o frontend corretamente.
2. **`test_variant_api_rs699`**: Valida o fluxo completo (End-to-End) de uma consulta real à API Ensembl, verificando se o retorno respeita o contrato de dados (Pydantic) e se a lógica de identificação de genes (como o gene *AGT*) está correta.
3. **`test_api_invalid_format`**: Valida a camada de segurança e sanitização (Regex), garantindo que entradas malformadas sejam bloqueadas com erro 400.
4. **`test_api_not_found`**: Garante que o sistema trate corretamente casos onde o rsID é válido em formato, mas não existe na base de dados biológica (Erro 404).

### Testando dentro do Container (Docker)

Se você subiu a aplicação via **Docker** ou **Docker Compose**, o container estará rodando com o nome `dasa-app`. Execute os comandos abaixo:

```bash
# Executa os testes
docker exec -it dasa-app python -m pytest tests/
# Limpeza do ambiente após os testes:
docker rm -f dasa-app
```

### Testando em Ambiente Local (Python)

Se você optou pela execução via Python/UV:

```bash
# Via UV (Recomendado)
uv run python -m pytest

# Via Pip tradicional (Certifique-se de estar com o venv ativo)
python -m pytest
```

## Autor

**Caio Mussatto** - [caio.mussatto@gmail.com](mailto:caio.mussatto@gmail.com) - [Linkedin](https://www.linkedin.com/in/caiomussatto/)