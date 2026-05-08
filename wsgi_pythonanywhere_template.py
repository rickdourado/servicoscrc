"""
Template WSGI para PythonAnywhere
Copie e adapte para /var/www/username_pythonanywhere_com_wsgi.py
"""

import os
import sys

# ========================================
# CONFIGURE AQUI: Defina o caminho ABSOLUTO para o projeto
# ========================================
# Exemplo: '/home/patrickribs/servicoscrc'
project_home = '/home/USERNAME/servicoscrc'

# Define BASE_DIR para resolver paths do CSV e outros arquivos
os.environ['BASE_DIR'] = project_home

# Adiciona ao Python path
if project_home not in sys.path:
    sys.path.insert(0, project_home)
    sys.path.insert(0, os.path.join(project_home, 'backend/scripts'))

# ========================================
# Carrega variáveis de ambiente (.env)
# ========================================
# PythonAnywhere: crie .env na raiz do projeto com:
#   GEMINI_API_KEY=sua-chave-aqui
#   SECRET_KEY=chave-secreta-flask
#   ADMIN_PASSWORD=senha-admin
#   IS_PRODUCTION=true

from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[WSGI] .env carregado de: {env_path}")
else:
    print(f"[WSGI] AVISO: .env não encontrado em {env_path}")

# ========================================
# Importa aplicação Flask
# ========================================
from backend.scripts.app import app as application

# Debug: mostra configuração inicial
print(f"[WSGI] project_home: {project_home}")
print(f"[WSGI] BASE_DIR: {os.environ.get('BASE_DIR')}")
print(f"[WSGI] sys.path: {sys.path[:3]}")
