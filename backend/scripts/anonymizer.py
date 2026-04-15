import re
import os
import fitz
import uuid

# Pasta temporária para salvar PDFs anonimizados
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def mask_sensitive_data(text: str) -> str:
    """Oculta dados sensíveis no texto extraído."""
    
    # Mascarar CNPJ
    cnpj_pattern = r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'
    text = re.sub(cnpj_pattern, '[CNPJ_OCULTO]', text)
    
    # Mascarar CPF
    cpf_pattern = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
    text = re.sub(cpf_pattern, '[CPF_OCULTO]', text)
    
    # Mascarar processos PRO-YYYY/XXXX
    pro_pattern = r'\bPRO-\d{4}/\d+\b'
    text = re.sub(pro_pattern, '[PROCESSO_OCULTO]', text)
    
    # Mascarar secretarias específicas (exemplo)
    sec_pattern = r'(?i)\bsecretaria municipal da [áa]rea civil\b'
    text = re.sub(sec_pattern, '[ÓRGÃO_OCULTO]', text)
    
    # Mascarar números de contratos/processos próximos a palavras-chave
    contract_pattern = r'(?i)\b(contrato|processo|ata|termo|edital|pregão)(?:\s+administrativo)?(?:\s+n[oº°])?\s*[:\.-]*\s*([0-9/\.-]+)'
    text = re.sub(contract_pattern, r'\1 [OCULTO]', text)
    
    # Mascarar empresas/nomes após "Contratada:"
    company_pattern = r'(?i)\b(contratada|contratante|empresa)\s*[:\s]+(.*?(?=cnpj|cpf|\n|\r|$|,\s*[a-z]))'
    text = re.sub(company_pattern, r'\1: [EMPRESA_OCULTA] ', text)
    
    # Mascarar palavras-chave de plataforma (Central1746, Salesforce)
    platform_pattern = r'(?i)\b(salesforce|central1746)\b'
    text = re.sub(platform_pattern, '[PLATAFORMA_OCULTA]', text)
    
    return text

def process_and_save(raw_text: str, original_filename: str) -> str:
    """Processa o texto e salva em um arquivo temporário para auditoria local."""
    masked_text = mask_sensitive_data(raw_text)
    
    temp_filepath = os.path.join(TEMP_DIR, "anonymized_contract.txt")
    with open(temp_filepath, "w", encoding="utf-8") as f:
        f.write(f"--- Arquivo de Origem: {original_filename} ---\n")
        f.write("--- DADOS ANOMIZADOS PARA PROTEÇÃO (MERCADO LIVRE/IA) ---\n\n")
        f.write(masked_text)
    
    return masked_text

def get_redaction_patterns():
    """Retorna padrões para busca visual no PDF."""
    return [
        (r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b', 0), # CNPJ
        (r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 0), # CPF
        (r'\bPRO-\d{4}/\d+\b', 0), # Processos PRO
        (r'(?i)\bsecretaria municipal da [áa]rea civil\b', 0),
        (r'(?i)\b(contrato|processo|ata|termo|edital|pregão)(?:\s+administrativo)?(?:\s+n[oº°])?\s*[:\.-]*\s*([0-9/\.-]+)', 2),
        (r'(?i)\b(contratada|contratante|empresa)\s*[:\s]+(.*?(?=cnpj|cpf|\n|\r|$|,\s*[a-z]))', 2),
        (r'(?i)\b(salesforce|central1746)\b', 0)
    ]

def redact_pdf_visually(file_bytes: bytes) -> tuple[str, str]:
    """Cria uma cópia do PDF com tarjas pretas nos dados sensíveis."""
    doc = fitz.open("pdf", file_bytes)
    patterns = get_redaction_patterns()
    full_text = ""
    
    for page in doc:
        text = page.get_text()
        full_text += text + "\n"
        matches_to_redact = []
        
        for pat, group_idx in patterns:
            for match in re.finditer(pat, text):
                try:
                    if group_idx > 0 and match.lastindex and match.lastindex >= group_idx:
                        val = match.group(group_idx).strip()
                        if val: matches_to_redact.append(val)
                    else:
                        val = match.group(0).strip()
                        if val: matches_to_redact.append(val)
                except IndexError:
                    pass
                    
        for m in matches_to_redact:
            if m and len(m) > 3: # Evita tarjas muito pequenas/aleatórias
                areas = page.search_for(m)
                for area in areas:
                    page.add_redact_annot(area, fill=(0, 0, 0)) # Tarja preta
                    
        page.apply_redactions()
        
    # Gera nome único para o arquivo temporário
    filename = f"redacted_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(TEMP_DIR, filename)
    doc.save(filepath)
    doc.close()
    
    masked_text = mask_sensitive_data(full_text)
    return filename, masked_text
