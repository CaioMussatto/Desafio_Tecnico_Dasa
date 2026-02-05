import requests
import logging
from .models import VariantData, PopulationFrequency
from .coordinates import get_coords
from .config import Config

# Configuração do logger para rastreabilidade de processos e depuração
logger = logging.getLogger(__name__)

class EnsemblClient:
    """
    Interface técnica para consumo da API REST do Ensembl.
    Gerencia a integração de dados genômicos, frequências populacionais 
    e lógica de redundância para localização de genes.
    """

    def __init__(self):
        # Centralização da URL base via Config para facilitar manutenção
        self.base_url = Config.ENSEMBL_BASE_URL

    def get_variant_data(self, rsid: str) -> VariantData:
        """
        Consolida informações completas de uma variante.
        Cruza dados de variação, fenótipos e coordenadas físicas (Overlap).
        """
        logger.info(f"Iniciando integração de dados para: {rsid}")
        
        # Preparação do endpoint de variação (Principal fonte de dados)
        endpoint = Config.ENDPOINTS["variation"].format(rsid=rsid)
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.get(url, headers=headers, timeout=Config.TIMEOUT)
            
            if not response.ok:
                logger.error(f"Falha na comunicação com Ensembl ({rsid}): Status {response.status_code}")
                return None
            
            data = response.json()    

            # --- 1. Processamento de Frequências Populacionais ---
            # Agrupamos alelos por população para identificar o Minor Allele Frequency (MAF)
            pops = data.get("populations", [])
            pop_groups = {}
            for p in pops:
                name = p['population']
                if name not in pop_groups:
                    pop_groups[name] = []
                pop_groups[name].append(p)

            all_pop_data = []
            
            # Variáveis para controle de Highest MAF (Maior frequência observada globalmente)
            highest_maf_val = -1.0
            highest_allele = ""
            
            # Listas para gerenciar empates e metadados geográficos para o mapa
            h_lats, h_lons = [], []
            h_names_clean = [] # Siglas curtas (Ex: BEB, YRI) para a tabela
            h_labels = []      # Nomes descritivos para o popup do mapa
            h_is_region = []   # Booleano para definir estilo visual no mapa

            maf_1000g_str = "N/A"

            for name, entries in pop_groups.items():
                # Uma população válida para MAF deve conter pelo menos dois alelos
                if len(entries) >= 2:
                    # O segundo alelo na ordem decrescente de frequência é o Minor
                    sorted_alleles = sorted(entries, key=lambda x: float(x.get('frequency', 0)), reverse=True)
                    minor_data = sorted_alleles[1]
                    current_maf = float(minor_data.get('frequency', 0))
                    current_allele = minor_data.get('allele', '')
                    
                    # Recupera coordenadas e labels amigáveis do arquivo coordinates.py
                    geo = get_coords(name)
                    clean_name = name.split(':')[-1]

                    # Filtro específico para o dado global do 1000 Genomes
                    if name == "1000GENOMES:phase_3:ALL":
                        maf_1000g_str = f"{current_allele}: {current_maf:.2f}"

                    # Armazena dados individuais de cada população (validado via Pydantic)
                    all_pop_data.append(
                        PopulationFrequency(
                            population=name,
                            allele=current_allele,
                            frequency=round(current_maf, 4),
                            lat=geo['lat'],
                            lon=geo['lon'],
                            label=geo.get('label', name),
                            is_region=geo.get('is_region', False)
                        )
                    )

                    # Lógica de detecção de Highest MAF e tratamento de empates técnicos
                    if current_maf > highest_maf_val:
                        highest_maf_val = current_maf
                        highest_allele = current_allele
                        h_names_clean = [clean_name]
                        h_lats, h_lons = [geo['lat']], [geo['lon']]
                        h_labels, h_is_region = [geo['label']], [geo['is_region']]
                        
                    elif current_maf == highest_maf_val and highest_maf_val >= 0:
                        h_names_clean.append(clean_name)
                        h_lats.append(geo['lat'])
                        h_lons.append(geo['lon'])
                        h_labels.append(geo['label'])
                        h_is_region.append(geo['is_region'])

            # --- 2. Consolidação de Genes ---
            # Recuperamos o mapeamento genômico (Cromossomo e Posição)
            mapping = data.get("mappings", [{}])[0]
            gene_set = set()

            # A. Busca por associações fenotípicas/clínicas diretas
            for p in data.get("phenotypes", []):
                if p.get("genes"):
                    for g in p.get("genes").split(","):
                        gene_set.add(g.strip())

            # B. Busca por sobreposição em transcritos conhecidos
            for tv in data.get("transcript_variations", []):
                gene_name = tv.get("gene_symbol")
                if gene_name:
                    gene_set.add(gene_name)

            # C. Lógica de Emergência (Overlap): Essencial para variantes em regiões intergênicas 
            # ou densas (MHC), onde a API de variação não retorna o gene diretamente (Ex: rs7142).
            if not gene_set and mapping.get("seq_region_name"):
                chrom = mapping.get("seq_region_name")
                start, end = mapping.get("start"), mapping.get("end")
                region = f"{chrom}:{start}-{end}"
                
                overlap_endpoint = Config.ENDPOINTS["overlap"].format(region=region)
                overlap_url = f"{self.base_url}{overlap_endpoint}"
                
                try:
                    overlap_res = requests.get(overlap_url, headers=headers, timeout=Config.TIMEOUT)
                    if overlap_res.ok:
                        overlap_data = overlap_res.json()
                        # Extraímos o 'external_name' que representa o Símbolo Oficial do Gene
                        for feature in overlap_data:
                            gene_symbol = feature.get("external_name")
                            if gene_symbol:
                                gene_set.add(f"{gene_symbol} (overlap)")
                        
                        if gene_set:
                            logger.info(f"Gene(s) localizado(s) via Overlap para {rsid}: {gene_set}")
                except Exception as e:
                    logger.warning(f"Falha na consulta de redundância (Overlap) para {rsid}: {e}")

            # --- 3. Finalização e Retorno ---
            # Formata a string de exibição para o MAF mais alto na tabela
            formatted_highest = "N/A"
            if h_names_clean:
                sources_str = ", ".join(h_names_clean)
                formatted_highest = f"{highest_allele}: {highest_maf_val:.2f} ({sources_str})"

            # Instancia o modelo final garantindo a integridade dos dados para o Frontend
            return VariantData(
                rsid=data.get("name", rsid),
                chromosome=str(mapping.get("seq_region_name", "N/A")),
                position=int(mapping.get("start", 0)),
                alleles=mapping.get("allele_string", "N/A"),
                minor_allele_freq=formatted_highest, 
                maf_1000g=maf_1000g_str,             
                pop_frequencies=all_pop_data,
                genes=sorted(list(gene_set)),
                consequence=data.get("most_severe_consequence", "N/A").replace("_", " "),
                highest_maf_lat=h_lats,
                highest_maf_lon=h_lons,
                highest_maf_labels=h_labels,
                highest_maf_is_region=h_is_region
            )

        except Exception as e:
            # Captura falhas de validação de Schema (Pydantic) ou erros inesperados de rede
            logger.error(f"Erro crítico no processamento de {rsid}: {str(e)}")
            return None