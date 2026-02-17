import requests
import logging
import time  # Adicionado para a lógica de retry
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
        Consolida informações completas de uma variante com lógica de retentativa.
        Cruza dados de variação, fenótipos e coordenadas físicas (Overlap).
        """
        logger.info(f"Iniciando integração de dados para: {rsid}")
        
        # Preparação do endpoint e headers (Padrão exigido pelo Ensembl)
        endpoint = Config.ENDPOINTS["variation"].format(rsid=rsid)
        url = f"{self.base_url}{endpoint}"
        
        # Headers idênticos ao exemplo oficial para máxima compatibilidade
        headers = { "Content-Type" : "application/json" }
        
        data = None
        max_retries = 3
        
        # --- Lógica de Resiliência (Retry) ---
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=Config.TIMEOUT)
                
                if response.status_code == 404:
                    logger.warning(f"Variante {rsid} não encontrada no Ensembl.")
                    return None
                
                response.raise_for_status()
                data = response.json()
                break # Sucesso! Sai do loop de tentativas
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Tentativa {attempt + 1} falhou para {rsid}. Tentando novamente em {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Erro de conexão persistente após {max_retries} tentativas para {rsid}: {e}")
                    return None
            except Exception as e:
                logger.error(f"Erro inesperado na requisição de {rsid}: {e}")
                return None

        if not data:
            return None

        try:
            # --- 1. Processamento de Frequências Populacionais ---
            pops = data.get("populations", [])
            pop_groups = {}
            for p in pops:
                name = p['population']
                if name not in pop_groups:
                    pop_groups[name] = []
                pop_groups[name].append(p)

            all_pop_data = []
            highest_maf_val = -1.0
            highest_allele = ""
            h_lats, h_lons = [], []
            h_names_clean, h_labels, h_is_region = [], [], []
            maf_1000g_str = "N/A"

            for name, entries in pop_groups.items():
                if len(entries) >= 2:
                    sorted_alleles = sorted(entries, key=lambda x: float(x.get('frequency', 0)), reverse=True)
                    minor_data = sorted_alleles[1]
                    current_maf = float(minor_data.get('frequency', 0))
                    current_allele = minor_data.get('allele', '')
                    
                    geo = get_coords(name)
                    clean_name = name.split(':')[-1]

                    if name == "1000GENOMES:phase_3:ALL":
                        maf_1000g_str = f"{current_allele}: {current_maf:.2f}"

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

                    if current_maf > highest_maf_val:
                        highest_maf_val, highest_allele = current_maf, current_allele
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
            mapping = data.get("mappings", [{}])[0]
            gene_set = set()

            for p in data.get("phenotypes", []):
                if p.get("genes"):
                    for g in p.get("genes").split(","):
                        gene_set.add(g.strip())

            for tv in data.get("transcript_variations", []):
                gene_name = tv.get("gene_symbol")
                if gene_name:
                    gene_set.add(gene_name)

            # Lógica de Emergência (Overlap)
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
                        for feature in overlap_data:
                            gene_symbol = feature.get("external_name")
                            if gene_symbol:
                                gene_set.add(f"{gene_symbol} (overlap)")
                except Exception as e:
                    logger.warning(f"Falha na consulta de redundância (Overlap) para {rsid}: {e}")

            formatted_highest = "N/A"
            if h_names_clean:
                sources_str = ", ".join(h_names_clean)
                formatted_highest = f"{highest_allele}: {highest_maf_val:.2f} ({sources_str})"

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
            logger.error(f"Erro crítico no processamento de {rsid}: {str(e)}")
            return None