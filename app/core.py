import requests
import logging
from .models import VariantData, PopulationFrequency

# Configuração do logger para rastreabilidade de processos
logger = logging.getLogger(__name__)

class EnsemblClient:
    """
    Interface técnica para consumo da API REST do Ensembl.
    Responsável por extrair coordenadas genômicas (GRCh38), 
    anotações de fenótipos e processar estatísticas populacionais.
    """

    def __init__(self):
        self.base_url = "https://rest.ensembl.org"

    def get_variant_data(self, rsid: str) -> VariantData:
        """
        Consolida informações de variantes através do endpoint /variation.
        Implementa a lógica de extração do Highest MAF global e mapeamento GRCh38.
        """
        logger.info(f"Iniciando integração de dados para: {rsid}")
        
        # Endpoint parametrizado para retornar populações e fenótipos
        endpoint = f"/variation/human/{rsid}?pops=1;phenotypes=1"
        headers = {"Content-Type": "application/json"}
        
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Efetuando GET request: {url}")
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if not response.ok:
                logger.error(f"Falha na comunicação com Ensembl ({rsid}): Status {response.status_code}")
                return None
            
            data = response.json()

            # --- Processamento de Frequências Populacionais ---
            pops = data.get("populations", [])
            pop_groups = {}
            for p in pops:
                name = p['population']
                if name not in pop_groups:
                    pop_groups[name] = []
                pop_groups[name].append(p)

            all_pop_data = []
            
            # Variáveis para o Highest MAF
            highest_maf_val = 0.0
            highest_allele = ""
            highest_source = "" # Rastreia a origem do maior valor

            # Variável para o 1000 Genomes Phase 3 (Novo Requisito)
            maf_1000g_str = "N/A"

            for name, entries in pop_groups.items():
                if len(entries) >= 2:
                    # Identificação do Minor Allele seguindo a regra do segundo mais comum
                    sorted_alleles = sorted(entries, key=lambda x: float(x.get('frequency', 0)), reverse=True)
                    
                    minor_data = sorted_alleles[1]
                    current_maf = float(minor_data.get('frequency', 0))
                    current_allele = minor_data.get('allele', '')

                    # Verifica se é especificamente o 1000 Genomes Phase 3
                    if name == "1000GENOMES:phase_3:ALL":
                        maf_1000g_str = f"{current_allele}: {current_maf:.2f}"

                    # Armazenamento para a tabela dinâmica do frontend
                    all_pop_data.append(
                        PopulationFrequency(
                            population=name,
                            allele=current_allele,
                            frequency=round(current_maf, 4)
                        )
                    )

                    # Monitoramento do maior MAF global detectado
                    if current_maf > highest_maf_val:
                        highest_maf_val = current_maf
                        highest_allele = current_allele
                        highest_source = name # Salva o nome da população

            # --- Extração de Mapeamento GRCh38 ---
            mapping = data.get("mappings", [{}])[0]
            
            # --- Consolidação de Genes Associados ---
            gene_set = set()
            for p in data.get("phenotypes", []):
                if p.get("genes"):
                    for g in p.get("genes").split(","):
                        gene_set.add(g.strip())

            logger.info(f"Sucesso: {rsid} mapeado no Chr {mapping.get('seq_region_name')} (GRCh38)")

            # Formata o Highest MAF para incluir a FONTE 
            formatted_highest = "0.00"
            if highest_allele:
                formatted_highest = f"{highest_allele}: {highest_maf_val:.2f} ({highest_source})"

            return VariantData(
                rsid=data.get("name"),
                chromosome=str(mapping.get("seq_region_name", "N/A")),
                position=int(mapping.get("start", 0)),
                alleles=mapping.get("allele_string", "N/A"),
                minor_allele_freq=formatted_highest, # Contém Valor + Fonte
                maf_1000g=maf_1000g_str,             # Contém Valor 1000G Phase 3
                pop_frequencies=all_pop_data,
                genes=sorted(list(gene_set)),
                consequence=data.get("most_severe_consequence", "N/A").replace("_", " ")
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão ou timeout na busca de {rsid}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro crítico no processamento de {rsid}: {str(e)}")
            return None