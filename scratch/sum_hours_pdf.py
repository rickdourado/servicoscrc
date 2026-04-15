from pypdf import PdfReader
import re

def analyze_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # Encontra o Anexo I
    section_name = "ANEXO I - Relatório Detalhado de Horas"
    start_idx = full_text.find(section_name)
    
    if start_idx == -1:
        # Tenta busca parcial
        start_idx = full_text.find("ANEXO I")
        
    if start_idx == -1:
        return "Anexo I não encontrado no documento."

    # Pega o texto do anexo até o próximo anexo ou final
    # (Assumindo que o anexo vai até o fim se não houver Anexo II)
    sub_text = full_text[start_idx:]
    next_section = re.search(r"ANEXO I{1,3}", sub_text[10:]) # Busca ANEXO II, III etc
    if next_section:
        sub_text = sub_text[:next_section.start() + 10]
        
    print("--- CONTEÚDO DO ANEXO I ---")
    print(sub_text)
    print("--------------------------")
    
    # Tenta extrair valores de horas
    # Geralmente no formato: "8,0h", "8.0", "08:00", etc.
    # Vou procurar por números seguidos de 'h' ou logo após descrições
    # Baseado no que vi em relatórios anteriores desse tipo: "8h", "4h", "2,5h"
    
    # Regex para capturar padrões numéricos próximos a 'h' ou isolados em tabelas
    # Padrão: número (opcional com vírgula/ponto) seguido de 'h' ou ' h'
    hour_matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*[hH](?!\w)", sub_text)
    
    total_hours = 0.0
    valid_matches = []
    for m in hour_matches:
        val = float(m.replace(",", "."))
        total_hours += val
        valid_matches.append(val)
        
    return {
        "found_values": valid_matches,
        "total": total_hours,
        "text_sample": sub_text[:500]
    }

if __name__ == "__main__":
    pdf_path = "/home/ssdlinux/Documents/dev/servicoscrc/refs/Relatório – 002_2026 150426  .pdf"
    result = analyze_pdf(pdf_path)
    print(result)
