import re
import os
import fitz
import uuid

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
    
    # Mask specific PRO-YYYY/XXXX formats
    pro_pattern = r'\bPRO-\d{4}/\d+\b'
    text = re.sub(pro_pattern, '[PROCESSO_OCULTO]', text)
    
    # Mask specific gov secretariats
    sec_pattern = r'(?i)\bsecretaria municipal da [áa]rea civil\b'
    text = re.sub(sec_pattern, '[ÓRGÃO_OCULTO]', text)
    
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

def get_redaction_patterns():
    return [
        (r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b', 0), # CNPJ
        (r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 0), # CPF
        (r'\bPRO-\d{4}/\d+\b', 0), # Processos PRO
        (r'(?i)\bsecretaria municipal da [áa]rea civil\b', 0),
        (r'(?i)\b(contrato|processo|ata|termo|edital|pregão)(?:\s+administrativo)?(?:\s+n[oº°])?\s*[:\.-]*\s*([0-9/\.-]+)', 2),
        (r'(?i)\b(contratada|contratante|empresa)\s*[:\s]+(.*?(?=cnpj|cpf|\n|\r|$|,\s*[a-z]))', 2)
    ]

def redact_pdf_visually(file_bytes: bytes) -> tuple[str, str]:
    """Redacts a PDF visually and returns the new filename and masked text."""
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
            if m:
                # search text in the PDF page
                areas = page.search_for(m)
                for area in areas:
                    page.add_redact_annot(area, fill=(0, 0, 0))
                    
        page.apply_redactions()
        
    filename = f"redacted_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(TEMP_DIR, filename)
    doc.save(filepath)
    doc.close()
    
    masked_text = mask_sensitive_data(full_text)
    return filename, masked_text
