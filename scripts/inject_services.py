import json
import os
import uuid
from thefuzz import process

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    with open(os.path.join(PROJECT_ROOT, 'backend/data/servicos.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Dicionario para acesso rápido aos subtemas
    subtheme_names = []
    subtheme_dict = {}
    
    for theme in data.get('items', []):
        for sub in theme.get('subthemes', []):
            name = sub['name']
            subtheme_names.append(name)
            subtheme_dict[name.lower()] = sub

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
        "alvará": "Atividade econômica",
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

    # Para evitar adicionar repetido se rodar de novo
    # Limpa os servicos atuais
    for theme in data.get('items', []):
        for sub in theme.get('subthemes', []):
            sub['services'] = []

    for title in titles:
        title_lower = title.lower()
        mapped = False
        
        # 1. Match exato ou keyword rules
        for kw, sub_name in keyword_map.items():
            if kw in title_lower:
                sub = subtheme_dict.get(sub_name.lower())
                if sub:
                    sub.setdefault('services', []).append({
                        "id": str(uuid.uuid4())[:8],
                        "name": title,
                        "description": ""
                    })
                    mapped = True
                    break
        
        if mapped:
            continue

        # 2. Fuzzy match com o nome do subtema
        best_match = process.extractOne(title_lower, subtheme_names)
        if best_match and best_match[1] >= 65:
            sub = subtheme_dict.get(best_match[0].lower())
            if sub:
                sub.setdefault('services', []).append({
                    "id": str(uuid.uuid4())[:8],
                    "name": title,
                    "description": ""
                })
                mapped = True
                continue

        # 3. Se nada funcionar, colocar num subtema 'Outros' do primeiro tema, ou apenas ignorar
        # Vamos adicionar no 'Administração pública' -> 'Solicitações do servidor' como fallback temporário?
        # Melhor colocar no primeiro subtema "Consulta a processos"
        sub = subtheme_dict.get("consulta a processos")
        if sub:
            sub.setdefault('services', []).append({
                "id": str(uuid.uuid4())[:8],
                "name": title,
                "description": ""
            })

    with open(os.path.join(PROJECT_ROOT, 'backend/data/servicos.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("servicos.json atualizado com sucesso!")

if __name__ == '__main__':
    main()
