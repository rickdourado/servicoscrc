import re

def process_anexo():
    with open("scratch/full_pdf_text.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # Encontra o Anexo I
    section_header = "ANEXO  I"
    idx = text.find(section_header)
    if idx == -1:
        return "Anexo I não encontrado."
    
    anexo_text = text[idx:]
    
    # Padrão: Data (AAAA-MM-DD) seguido de um número (horas)
    # Note que no PDF extraído, pode haver múltiplos espaços
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(\d+)")
    
    matches = pattern.findall(anexo_text)
    
    total = 0
    print("--- Detalhamento das Horas Encontradas ---")
    for date, hour in matches:
        h = int(hour)
        total += h
        print(f"Data: {date} | Horas: {h}")
    
    print("\n--- Outros Totais Encontrados no Texto ---")
    totals = re.findall(r"Total\s+geral\s+(\d+)", anexo_text)
    for t in totals:
        print(f"Total Detectado no PDF: {t}")
        
    return total

if __name__ == "__main__":
    result = process_anexo()
    print(f"\nSOMA CALCULADA PELOS ITENS: {result}")
