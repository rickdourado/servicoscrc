import re

def solve():
    with open("scratch/full_pdf_text.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # Localiza o Anexo I
    idx = content.find("ANEXO  I")
    if idx == -1:
        print("Anexo I não encontrado.")
        return
    
    anexo_text = content[idx:]
    
    # 1. Somar entradas detalhadas (com data)
    # Exemplo: 2026-03-12  8
    detailed_matches = re.findall(r"\d{4}-\d{2}-\d{2}\s+(\d+)", anexo_text)
    detailed_hours = [int(h) for h in detailed_matches]
    
    # 2. Somar entradas resumidas (ao final do anexo)
    # Exemplo: Criar objeto Unidade Organizacional 8 Core
    # Elas aparecem depois da "Visão por História"
    idx_summary = anexo_text.find("Visão por História")
    summary_text = anexo_text[idx_summary:] if idx_summary != -1 else ""
    
    # Padrao para o resumo: "Nome  do  item  <Horas>  <Categoria>"
    # Note que as horas aqui costumam ser acumuladas.
    # Mas o usuário quer a somatória "contida na parte de ANEXO I".
    # Vou extrair os itens individuais do relatório de horas.
    
    # O "896" parece ser o total correto.
    # Vou listar os maiores blocos para conferência.
    print(f"Total de entradas detalhadas (com data): {len(detailed_hours)}")
    print(f"Soma das entradas detalhadas: {sum(detailed_hours)}")
    
    # Vou verificar se há horas citadas sem data no relatório detalhado
    # (Antes da seção de resumo)
    report_text = anexo_text[:idx_summary] if idx_summary != -1 else anexo_text
    
    # Procurar por números isolados em linhas que parecem ser de tabela mas o regex falhou
    # Ex: "176  CZRM-113" -> 176 horas para esse bloco
    blocks = re.findall(r"(\d+)\s+CZRM-\d+", report_text)
    print(f"Horas por blocos técnicos: {blocks}")
    
    # Encontrar o total final explícito
    total_match = re.search(r"Total\s+geral\s+(\d+)", anexo_text)
    if total_match:
        print(f"Total Geral declarado no PDF: {total_match.group(1)}")

if __name__ == "__main__":
    solve()
