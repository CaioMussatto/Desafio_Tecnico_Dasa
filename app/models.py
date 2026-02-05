from pydantic import BaseModel, Field
from typing import List

class PopulationFrequency(BaseModel):
    """
    Estrutura para armazenamento de frequências populacionais específicas.
    Inclui coordenadas geográficas para mapeamento dinâmico.
    """
    population: str = Field(..., description="Nome da população/banco de dados")
    allele: str = Field(..., description="Alelo correspondente à frequência")
    frequency: float = Field(..., description="Frequência alélica observada")
    lat: float = Field(0.0, description="Latitude da população para o mapa")
    lon: float = Field(0.0, description="Longitude da população para o mapa")
    label: str
    is_region: bool

class VariantData(BaseModel):
    """
    Schema central para validação de dados de variantes genéticas.
    Consolida informações de mapeamento GRCh38, genes, estatísticas populacionais e dados geográficos.
    """
    rsid: str = Field(..., description="Identificador único (Ex: rs699)")
    chromosome: str = Field(..., description="Cromossomo (Mapeamento GRCh38)")
    position: int = Field(..., description="Posição genômica inicial")
    alleles: str = Field(..., description="String de alelos de referência/alternativos")
    minor_allele_freq: str = Field("N/A", description="Highest MAF observado com Fonte(s)")
    maf_1000g: str = Field("N/A", description="Frequência global do 1000 Genomes Phase 3")
    pop_frequencies: List[PopulationFrequency] = Field(default_factory=list)
    genes: List[str] = Field(default_factory=list, description="Lista de símbolos oficiais de genes associados")
    consequence: str = Field(..., description="Consequência funcional predita mais severa")
    
    # Suporte a múltiplos pontos no Mapa HD em caso de empate
    highest_maf_lat: List[float] = Field(default_factory=list, description="Lista de latitudes das populações com maior MAF")
    highest_maf_lon: List[float] = Field(default_factory=list, description="Lista de longitudes das populações com maior MAF")
    highest_maf_labels: List[str] = Field(default_factory=list, description="Nomes amigáveis das populações")
    highest_maf_is_region: List[bool] = Field(default_factory=list, description ="Detecta se é uma região ou não")