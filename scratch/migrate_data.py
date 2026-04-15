import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao path para importar os módulos
sys.path.append(os.getcwd())

from backend.scripts.servicos_organizacao import extract_servicos

print("Iniciando migração de dados...")
items = extract_servicos()
print(f"Migração concluída. {len(items)} Temas processados e salvos no novo formato.")
