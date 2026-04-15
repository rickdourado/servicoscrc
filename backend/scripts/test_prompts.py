import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para permitir imports
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

try:
    from backend.scripts.app import get_prompt, PROMPTS_DIR
    
    print(f"--- Iniciando Verificacao de Prompts ---")
    print(f"Diretorio de Prompts: {PROMPTS_DIR}")
    
    prompts_to_test = [
        "prompt_generico",
        "prompt_conciso",
        "prompt_ti",
        "prompt_servico",
        "prompt_informacao"
    ]
    
    all_ok = True
    for p in prompts_to_test:
        content = get_prompt(p, "FALHA")
        if content == "FALHA":
            print(f"[ERRO] Falha ao carregar: {p}")
            all_ok = False
        else:
            first_line = content.split('\n')[0].strip()
            print(f"[OK] Carregado: {p} ({len(content)} bytes) - '{first_line}'")
            
    if all_ok:
        print("\nTodos os prompts foram carregados com sucesso!")
    else:
        print("\nAlguns prompts falharam ao carregar.")
        sys.exit(1)

except ImportError as e:
    print(f"[ERRO] Importacao: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERRO] Inesperado: {e}")
    sys.exit(1)

