import sys
import os

# Caminho do projeto
path = '/home/projetocrc/servicoscrc'
if path not in sys.path:
    sys.path.insert(0, path)

# Carregamento do .env
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))


# Importa a aplicação FastAPI do seu projeto
from backend.scripts.app import app
from a2wsgi import ASGIMiddleware

# Converte a aplicação ASGI (FastAPI) para o padrão WSGI (PythonAnywhere)
application = ASGIMiddleware(app)
