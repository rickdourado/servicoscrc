import json
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'scripts'))
from ai_utils import call_gemini

def main():
    with open('backend/data/servicos.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    subthemes_info = []
    for theme in data.get('items', []):
        for sub in theme.get('subthemes', []):
            subthemes_info.append({
                "theme": theme['name'],
                "subtheme": sub['name'],
                "subtheme_id": sub['id']
            })

    with open('temp_nivel3_titles.json', 'r', encoding='utf-8') as f:
        titles = json.load(f)

    # Process in batches of 50 to avoid token limits or confused outputs
    batch_size = 50
    all_mappings = []

    for i in range(0, len(titles), batch_size):
        batch_titles = titles[i:i+batch_size]
        print(f"Processando lote {i//batch_size + 1} de {(len(titles) + batch_size - 1)//batch_size}...")
        
        prompt = f"""
Você é um especialista em organização de serviços públicos municipais.
Abaixo está uma lista de serviços (Nível 3) e uma lista de categorias disponíveis (Tema -> Subtema) com seus respectivos IDs.

Sua tarefa é mapear cada serviço para o subtema mais adequado pelo contexto.

Subtemas disponíveis:
{json.dumps(subthemes_info, ensure_ascii=False, indent=2)}

Serviços a serem mapeados:
{json.dumps(batch_titles, ensure_ascii=False, indent=2)}

Responda APENAS com um array JSON válido (sem blocos de código Markdown, apenas o JSON puro) contendo objetos com:
"titulo_servico" (o nome original),
"subtheme_id" (o ID mapeado),
"subtheme_name" (o nome do subtema),
"theme_name" (o nome do tema).

MUITO IMPORTANTE: A resposta deve ser estritamente JSON.
"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = call_gemini(prompt)
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:]
                if text.endswith('```'):
                    text = text[:-3]
                
                batch_result = json.loads(text.strip())
                all_mappings.extend(batch_result)
                break
            except Exception as e:
                print(f"Erro ao processar lote {i} (tentativa {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(15) # Wait before retry
                else:
                    print("Falha ao processar lote após várias tentativas.")

    with open('temp_mapped_services.json', 'w', encoding='utf-8') as f:
        json.dump(all_mappings, f, ensure_ascii=False, indent=4)
        
    print(f"Mapeamento concluído com {len(all_mappings)} serviços.")

if __name__ == '__main__':
    main()
