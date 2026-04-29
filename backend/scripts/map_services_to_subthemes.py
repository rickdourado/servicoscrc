import os
import sys
import json
import csv
import uuid
import time
from pathlib import Path

# Adicionar backend/scripts ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / 'backend' / 'scripts'))
from ai_utils import call_gemini

JSON_PATH = BASE_DIR / 'backend' / 'data' / 'servicos.json'
CSV_PATH = BASE_DIR / 'refs' / 'planilhas' / 'servicos' / 'servicosconsolidados.csv'

def main():
    # 1. Ler o JSON atual
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Construir lista de subtemas disponíveis para o prompt
    subthemes_info = []
    # Limpar os serviços existentes para recriar a estrutura com a nova planilha
    for theme in data.get('items', []):
        for sub in theme.get('subthemes', []):
            subthemes_info.append({
                "theme_name": theme['name'],
                "subtheme_name": sub['name'],
                "subtheme_id": sub['id']
            })
            # Esvaziamos a lista de serviços para popular do zero
            sub['services'] = []

    # 3. Ler o CSV
    services_to_map = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            titulo = row.get('titulo_servico', '').strip()
            descricao = row.get('descricao_completa', '').strip()
            if titulo:
                services_to_map.append({
                    "titulo_servico": titulo,
                    "descricao_completa": descricao
                })

    print(f"Total de serviços a mapear: {len(services_to_map)}")

    # 4. Processar em lotes
    batch_size = 40
    all_mapped_results = []

    for i in range(0, len(services_to_map), batch_size):
        batch = services_to_map[i:i+batch_size]
        print(f"Processando lote {i//batch_size + 1} de {(len(services_to_map) + batch_size - 1)//batch_size}...")
        
        prompt = f"""
Você é um especialista em organização de serviços públicos municipais.
Abaixo está uma lista de categorias disponíveis (Tema -> Subtema) com seus respectivos IDs.
Em seguida, uma lista de serviços (Nível 3) que precisam ser mapeados para essas categorias.

Sua tarefa é mapear cada serviço para o subtema mais adequado pelo contexto.
Regras de Contexto:
1) Avalie o "titulo_servico" e a "descricao_completa" (se existir). A descrição fornece o contexto real do serviço.
2) Caso não haja descrição, baseie-se apenas no título, lembrando sempre da hierarquia Tema (Nível 1) -> Subtema (Nível 2).

Subtemas disponíveis:
{json.dumps(subthemes_info, ensure_ascii=False, indent=2)}

Serviços a serem mapeados:
{json.dumps(batch, ensure_ascii=False, indent=2)}

Responda APENAS com um array JSON válido contendo objetos com:
"titulo_servico": (o título exato fornecido),
"descricao_completa": (a descrição fornecida, vazia se não houver),
"subtheme_id": (o ID do subtema escolhido)

MUITO IMPORTANTE: A resposta deve ser estritamente JSON puro (sem blocos de código Markdown como ```json).
"""
        max_retries = 20
        for attempt in range(max_retries):
            try:
                response = call_gemini(prompt, model="gemini-2.5-flash")
                text = response.text.strip()
                if text.startswith('```json'): text = text[7:]
                if text.startswith('```'): text = text[3:]
                if text.endswith('```'): text = text[:-3]
                
                batch_result = json.loads(text.strip())
                all_mapped_results.extend(batch_result)
                print(f"Lote {i//batch_size + 1} processado. Aguardando para evitar limite de taxa...")
                time.sleep(15)  # Espera 15s entre lotes normais
                break
            except Exception as e:
                print(f"Erro ao processar lote {i//batch_size + 1} (tentativa {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    print("Aguardando 30 segundos devido a erro (503 Demanda ou 429 Rate Limit)...")
                    time.sleep(30)
                else:
                    print("Falha ao processar lote após várias tentativas. Abortando script.")
                    sys.exit(1)

    # 5. Reinserir os serviços mapeados no objeto JSON original
    # Criar um indexador para acesso rápido aos subthemes
    subtheme_map = {}
    for theme in data.get('items', []):
        for sub in theme.get('subthemes', []):
            subtheme_map[sub['id']] = sub

    for item in all_mapped_results:
        s_id = item.get("subtheme_id")
        if s_id in subtheme_map:
            new_service = {
                "id": str(uuid.uuid4())[:8],
                "name": item.get("titulo_servico", ""),
                "description": item.get("descricao_completa", "")
            }
            subtheme_map[s_id]['services'].append(new_service)
        else:
            print(f"Aviso: Subtema ID {s_id} não encontrado para o serviço {item.get('titulo_servico')}")

    # 6. Salvar o JSON atualizado
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Mapeamento concluído com sucesso! {len(all_mapped_results)} serviços inseridos.")

if __name__ == '__main__':
    main()
