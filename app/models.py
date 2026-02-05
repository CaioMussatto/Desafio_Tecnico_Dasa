from pydantic import BaseModel, Field
from typing import List

class PopulationFrequency(BaseModel):
    """
    Estrutura para armazenamento de frequências populacionais específicas.
    Utilizado para compor a tabela dinâmica de frequências no frontend.
    """
    population: str = Field(..., description="Nome da população/banco de dados")
    allele: str = Field(..., description="Alelo correspondente à frequência")
    frequency: float = Field(..., description="Frequência alélica observada")

class VariantData(BaseModel):
    """
    Schema central para validação de dados de variantes genéticas.
    Consolida informações de mapeamento GRCh38, genes e estatísticas populacionais.
    """
    rsid: str = Field(..., description="Identificador único (Ex: rs699)")
    chromosome: str = Field(..., description="Cromossomo (Mapeamento GRCh38)")
    position: int = Field(..., description="Posição genômica inicial")
    alleles: str = Field(..., description="String de alelos de referência/alternativos")
    minor_allele_freq: str = Field("N/A", description="Highest MAF observado com Fonte")
    maf_1000g: str = Field("N/A", description="Frequência global do 1000 Genomes Phase 3") # Campo Novo
    pop_frequencies: List[PopulationFrequency] = Field(default_factory=list)
    genes: List[str] = Field(default_factory=list, description="Lista de símbolos oficiais de genes associados")
    consequence: str = Field(..., description="Consequência funcional predita mais severa")