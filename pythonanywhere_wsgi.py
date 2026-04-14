import sys
import os

# Adiciona o diretório do projeto ao path do sistema do PythonAnywhere
project_home = '/home/projetocrc/servicoscrc'
if project_home not in sys.path:
    sys.path.append(project_home)

# Carrega as variáveis de ambiente (como GEMINI_API_KEY) a partir do .env
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Importa a aplicação FastAPI do seu projeto
from backend.scripts.app import app

# Converte a aplicação ASGI (FastAPI) para o padrão WSGI que o servidor web do PythonAnywhere compreende via a2wsgi
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)
