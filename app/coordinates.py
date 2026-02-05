# app/coordinates.py

POP_COORDS = {
    # --- 1000 Genomes (Super-populações / Regiões) ---
    "AFR": {"lat": 2.0, "lon": 16.0, "label": "African Populations (Region)", "is_region": True},
    "AMR": {"lat": 15.0, "lon": -80.0, "label": "Admixed American Populations (Region)", "is_region": True},
    "EAS": {"lat": 34.0, "lon": 108.0, "label": "East Asian Populations (Region)", "is_region": True},
    "EUR": {"lat": 48.0, "lon": 14.0, "label": "European Populations (Region)", "is_region": True},
    "SAS": {"lat": 22.0, "lon": 78.0, "label": "South Asian Populations (Region)", "is_region": True},
    "ALL": {"lat": 20.0, "lon": 0.0, "label": "Global (All Populations)", "is_region": True},

    # --- 1000 Genomes (AFR - Pontos Específicos) ---
    "YRI": {"lat": 7.37, "lon": 3.94, "label": "Yoruba in Ibadan, Nigeria", "is_region": False},
    "LWK": {"lat": 0.59, "lon": 34.78, "label": "Luhya in Webuye, Kenya", "is_region": False},
    "GWD": {"lat": 13.44, "lon": -16.48, "label": "Gambian in Western Division – Mandinka", "is_region": False},
    "MSL": {"lat": 8.46, "lon": -11.77, "label": "Mende in Sierra Leone", "is_region": False},
    "ESN": {"lat": 6.33, "lon": 5.62, "label": "Esan in Nigeria", "is_region": False},
    "ASW": {"lat": 33.44, "lon": -94.04, "label": "African Ancestry in Southwest USA", "is_region": False},
    "ACB": {"lat": 13.19, "lon": -59.54, "label": "African Caribbean in Barbados", "is_region": False},

    # --- 1000 Genomes (AMR - Pontos Específicos) ---
    "MXL": {"lat": 34.05, "lon": -118.24, "label": "Mexican Ancestry in Los Angeles, California, USA", "is_region": False},
    "PUR": {"lat": 18.22, "lon": -66.59, "label": "Puerto Rican in Puerto Rico", "is_region": False},
    "CLM": {"lat": 6.24, "lon": -75.58, "label": "Colombian in Medellin, Colombia", "is_region": False},
    "PEL": {"lat": -12.04, "lon": -77.04, "label": "Peruvian in Lima, Peru", "is_region": False},

    # --- 1000 Genomes (EAS - Pontos Específicos) ---
    "CHB": {"lat": 39.90, "lon": 116.40, "label": "Han Chinese in Beijing, China", "is_region": False},
    "JPT": {"lat": 35.67, "lon": 139.65, "label": "Japanese in Tokyo, Japan", "is_region": False},
    "CHS": {"lat": 23.12, "lon": 113.26, "label": "Han Chinese South", "is_region": False},
    "CDX": {"lat": 22.00, "lon": 100.79, "label": "Chinese Dai in Xishuangbanna", "is_region": False},
    "KHV": {"lat": 10.82, "lon": 106.63, "label": "Kinh in Ho Chi Minh City, Vietnam", "is_region": False},

    # --- 1000 Genomes (EUR - Pontos Específicos) ---
    "CEU": {"lat": 39.32, "lon": -111.09, "label": "Utah residents with Northern/Western European ancestry", "is_region": False},
    "TSI": {"lat": 43.76, "lon": 11.25, "label": "Toscani in Italia", "is_region": False},
    "FIN": {"lat": 60.16, "lon": 24.93, "label": "Finnish in Finland", "is_region": False},
    "GBR": {"lat": 52.35, "lon": -1.17, "label": "British from England and Scotland", "is_region": False},
    "IBS": {"lat": 40.46, "lon": -3.74, "label": "Iberian Populations in Spain", "is_region": False},

    # --- 1000 Genomes (SAS - Pontos Específicos) ---
    "GIH": {"lat": 29.76, "lon": -95.36, "label": "Gujarati Indians in Houston, Texas, USA", "is_region": False},
    "PJL": {"lat": 31.52, "lon": 74.35, "label": "Punjabi in Lahore, Pakistan", "is_region": False},
    "BEB": {"lat": 23.81, "lon": 90.41, "label": "Bengali in Bangladesh", "is_region": False},
    "STU": {"lat": 51.50, "lon": -0.12, "label": "Sri Lankan Tamil in the UK", "is_region": False},
    "ITU": {"lat": 52.48, "lon": -1.89, "label": "Indian Telugu in the UK", "is_region": False},

    # --- gnomAD (Sempre tratadas como Regiões) ---
    "afr": {"lat": 2.0, "lon": 16.0, "label": "gnomAD: African/African American", "is_region": True},
    "ami": {"lat": 40.0, "lon": -76.0, "label": "gnomAD: Amish", "is_region": True},
    "amr": {"lat": 10.0, "lon": -80.0, "label": "gnomAD: Admixed American", "is_region": True},
    "asj": {"lat": 31.7, "lon": 35.2, "label": "gnomAD: Ashkenazi Jewish", "is_region": True},
    "eas": {"lat": 34.0, "lon": 108.0, "label": "gnomAD: East Asian", "is_region": True},
    "fin": {"lat": 61.9, "lon": 25.7, "label": "gnomAD: Finnish", "is_region": True},
    "mid": {"lat": 23.8, "lon": 45.0, "label": "gnomAD: Middle Eastern", "is_region": True},
    "nfe": {"lat": 48.0, "lon": 14.0, "label": "gnomAD: Non-Finnish European", "is_region": True},
    "sas": {"lat": 22.0, "lon": 78.0, "label": "gnomAD: South Asia", "is_region": True},

    # --- NCBI ALFA (Macro-regiões) ---
    "ALFA:SAMN10492695": {"lat": 50.0, "lon": 10.0, "label": "ALFA: Europe", "is_region": True},
    "ALFA:SAMN10492696": {"lat": -1.0, "lon": 20.0, "label": "ALFA: African others", "is_region": True},
    "ALFA:SAMN10492697": {"lat": 35.0, "lon": 105.0, "label": "ALFA: East Asian", "is_region": True},
    "ALFA:SAMN10492698": {"lat": 34.0, "lon": -98.0, "label": "ALFA: African American", "is_region": True},
    "ALFA:SAMN10492699": {"lat": -15.0, "lon": -60.0, "label": "ALFA: Latin American 1", "is_region": True},
    "ALFA:SAMN10492700": {"lat": -10.0, "lon": -55.0, "label": "ALFA: Latin American 2", "is_region": True},
    "ALFA:SAMN10492701": {"lat": 15.0, "lon": 100.0, "label": "ALFA: Other Asian", "is_region": True},
    "ALFA:SAMN10492702": {"lat": 21.0, "lon": 78.0, "label": "ALFA: South Asian", "is_region": True},
    "ALFA:SAMN10492703": {"lat": 2.0, "lon": 22.0, "label": "ALFA: African", "is_region": True},
    "ALFA:SAMN10492704": {"lat": 30.0, "lon": 110.0, "label": "ALFA: Asian", "is_region": True},
    "ALFA:SAMN11605645": {"lat": 0.0, "lon": 0.0, "label": "ALFA: Other", "is_region": True},

    # --- Outros (Pontos Específicos ou Coortes) ---
    "GEM-J": {"lat": 36.2, "lon": 138.2, "label": "GEM-J: Japan", "is_region": False},
    "ALSPAC": {"lat": 51.4, "lon": -2.6, "label": "ALSPAC Cohort (UK)", "is_region": False},
    "TWINSUK": {"lat": 51.5, "lon": -0.1, "label": "TwinsUK", "is_region": False},
    "ESP6500:AA": {"lat": 35.0, "lon": -100.0, "label": "NHLBI ESP: African American", "is_region": False},
    "ESP6500:EA": {"lat": 40.0, "lon": -5.0, "label": "NHLBI ESP: Europe American", "is_region": False},
    "GWF": {"lat": 13.4, "lon": -16.5, "label": "GGVP: Gambian - Fula", "is_region": False},
    "GWJ": {"lat": 13.5, "lon": -16.6, "label": "GGVP: Gambian - Jola", "is_region": False},
    "GWW": {"lat": 13.6, "lon": -16.7, "label": "GGVP: Gambian - Wolof", "is_region": False},
}

def get_coords(pop_name):
    """
    Retorna dicionário com lat, lon, label e is_region.
    Tenta busca exata, depois busca por sufixo (sigla).
    """
    # 1. Procura exata
    if pop_name in POP_COORDS:
        return POP_COORDS[pop_name]
    
    # 2. Procura por sigla limpa (:SIGLA ou _SIGLA)
    for key in POP_COORDS:
        if f":{key}" in pop_name or f"_{key}" in pop_name:
            return POP_COORDS[key]
            
    # 3. Fallback (População desconhecida)
    return {"lat": 0.0, "lon": 0.0, "label": pop_name, "is_region": True}