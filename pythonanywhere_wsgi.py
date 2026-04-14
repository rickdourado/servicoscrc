import sys
import os

# 1. Configuração do Caminho do Projeto
path = '/home/projetocrc/servicoscrc'
if path not in sys.path:
    sys.path.insert(0, path)

# 2. Carregamento das variáveis de ambiente (.env)
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# 3. Importa a aplicação Flask do seu projeto
from backend.scripts.app import app as application

# A variável 'application' é o padrão que o uWSGI do PythonAnywhere procura.
