import json
import os
import pandas as pd
from thefuzz import process

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    with open(os.path.join(PROJECT_ROOT, 'backend/data/servicos.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    subthemes = []
    # Criação de um dicionário reverso para facilitar a busca
    subtheme_names = []
    subtheme_dict = {}
    
    for theme in data.get('items', []):
        for sub in theme.get('subthemes', []):
            name = sub['name']
            subtheme_names.append(name)
            subthemes.append({
                "theme_name": theme['name'],
                "subtheme_name": name,
                "subtheme_id": sub['id']
            })
            subtheme_dict[name.lower()] = {
                "theme_name": theme['name'],
                "subtheme_name": name,
                "subtheme_id": sub['id']
            }

    with open(os.path.join(PROJECT_ROOT, 'temp_nivel3_titles.json'), 'r', encoding='utf-8') as f:
        titles = json.load(f)

    # Keywords mapping to specific subthemes
    keyword_map = {
        "iptu": "IPTU",
        "itbi": "ITBI",
        "iss": "ISS",
        "darm": "ISS",
        "nota carioca": "Nota Carioca",
        "multa de trânsito": "Multas",
        "multa": "Multas",
        "alvará": "Atividade econômica", # Geralmente
        "dívida ativa": "Dívida Ativa",
        "animal": "Saúde animal",
        "cães": "Saúde animal",
        "gatos": "Saúde animal",
        "castração": "Saúde animal",
        "esporotricose": "Saúde animal",
        "ônibus": "Ônibus",
        "táxi": "Táxi",
        "brt": "BRT",
        "vlt": "VLT",
        "jaé": "Jaé",
        "estacionamento": "Estacionamento",
        "árvore": "Arborização",
        "poda": "Arborização",
        "buraco": "Conservação",
        "lixo": "Limpeza",
        "limpeza": "Limpeza",
        "varrição": "Limpeza",
        "resíduos": "Limpeza",
        "iluminação": "Iluminação pública",
        "poste": "Iluminação pública",
        "escola": "Vida escolar",
        "creche": "Educação Infantil",
        "aluno": "Vida escolar",
        "defesa civil": "Vistorias",
        "saúde": "Atendimento ambulatorial / Consultas e exames / Clínicas da Família e Postos de Saúde",
        "vacinação": "Vacinação",
        "planetário": "Espaços culturais",
        "procon": "PROCON carioca",
        "licença ambiental": "Ambientais",
        "obras": "Urbanísticas"
    }

    results = []

    for title in titles:
        title_lower = title.lower()
        mapped = False
        
        # 1. Match exato ou keyword rules
        for kw, sub_name in keyword_map.items():
            if kw in title_lower:
                match = subtheme_dict.get(sub_name.lower())
                if match:
                    results.append({
                        "titulo_servico": title,
                        **match,
                        "metodo": f"Keyword: {kw}"
                    })
                    mapped = True
                    break
        
        if mapped:
            continue

        # 2. Fuzzy match com o nome do subtema
        best_match = process.extractOne(title_lower, subtheme_names)
        if best_match and best_match[1] >= 65:
            match = subtheme_dict.get(best_match[0].lower())
            results.append({
                "titulo_servico": title,
                **match,
                "metodo": f"Fuzzy: {best_match[1]}%"
            })
            mapped = True
            continue

        # 3. Se nada funcionar, colocar como "Não Mapeado"
        results.append({
            "titulo_servico": title,
            "theme_name": "Não Mapeado",
            "subtheme_name": "Não Mapeado",
            "subtheme_id": "N/A",
            "metodo": "Nenhum"
        })

    # Output to markdown artifact
    df = pd.DataFrame(results)
    
    md_lines = ["# Mapeamento de Serviços (Nível 3 para Nível 2)\n"]
    md_lines.append("Este documento apresenta o mapeamento dos serviços de Nível 3 para os Subtemas do Nível 2.\n")
    
    grouped = df.groupby(["theme_name", "subtheme_name"])
    for (theme, subtheme), group in grouped:
        md_lines.append(f"## {theme} -> {subtheme}\n")
        for _, row in group.iterrows():
            md_lines.append(f"- {row['titulo_servico']} _(Método: {row['metodo']})_")
        md_lines.append("\n")

    with open(os.path.join(PROJECT_ROOT, 'temp_mapeamento.md'), 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))

    print(f"Mapeamento concluído e salvo em artifacts/mapeamento_servicos.md. Total mapeados: {len(df[df['theme_name'] != 'Não Mapeado'])} de {len(df)}.")

if __name__ == '__main__':
    main()
