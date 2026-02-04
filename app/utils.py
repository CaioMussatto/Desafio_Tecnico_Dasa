import re

def clean_rsid(rsid: str) -> str:
    """
    Valida e formata um rsID.
    
    Remove espaços, converte para minúsculo e verifica se segue o padrão 'rs' + números.
    
    Args:
        rsid (str): O identificador fornecido pelo usuário.
        
    Returns:
        str: rsID formatado.
        
    Raises:
        ValueError: Se o formato for inválido.
    """
    rsid_clean = rsid.strip().lower()
    if not re.match(r'^rs\d+$', rsid_clean):
        raise ValueError(f"Formato de rsID inválido: {rsid}. Deve ser 'rs' seguido de números.")
    return rsid_clean