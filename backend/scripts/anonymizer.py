import re
import os

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def mask_sensitive_data(text: str) -> str:
    """Masks sensitive information in the extracted text."""
    
    # Mask CNPJ (e.g. 11.111.111/0001-11)
    cnpj_pattern = r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'
    text = re.sub(cnpj_pattern, '[CNPJ_OCULTO]', text)
    
    # Mask CPF (e.g. 111.111.111-11 or 11111111111)
    cpf_pattern = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
    text = re.sub(cpf_pattern, '[CPF_OCULTO]', text)
    
    # Mask process and contract numbers 
    contract_pattern = r'(?i)\b(contrato|processo|ata|termo|edital|pregão)(?:\s+administrativo)?(?:\s+n[oº°])?\s*[:\.-]*\s*([0-9/\.-]+)'
    # We replace the matched first group (the anchor word) and hide the second group (the identifier)
    text = re.sub(contract_pattern, r'\1 [OCULTO]', text)
    
    # Mask company names after typical anchors (capturing up to standard punctuation or newline)
    company_pattern = r'(?i)\b(contratada|contratante|empresa)\s*[:\s]+(.*?(?=cnpj|cpf|\n|\r|$|,\s*[a-z]))'
    text = re.sub(company_pattern, r'\1: [EMPRESA_OCULTA] ', text)
    
    return text

def process_and_save(raw_text: str, original_filename: str) -> str:
    """Masks the text and saves to a temporary .txt file."""
    masked_text = mask_sensitive_data(raw_text)
    
    temp_filepath = os.path.join(TEMP_DIR, "anonymized_contract.txt")
    with open(temp_filepath, "w", encoding="utf-8") as f:
        f.write(f"--- Arquivo de Origem: {original_filename} ---\n")
        f.write("--- DADOS ANOMIZADOS PARA PROTEÇÃO ---\n\n")
        f.write(masked_text)
    
    return masked_text
