import sys
import os

# 1. Configuração do Caminho do Projeto
path = '/home/projetocrc/servicoscrc'
if path not in sys.path:
    sys.path.insert(0, path)

# 2. Força modo producao ANTES de qualquer import do app.
# Isso garante que IS_PRODUCTION seja True no PythonAnywhere
# independente do estado do arquivo .env.
os.environ.setdefault('IS_PRODUCTION', 'true')

# 3. Carregamento das variáveis de ambiente (.env)
# load_dotenv respeita variáveis já existentes (não sobrescreve).
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# 4. Importa a aplicação Flask do seu projeto
from backend.scripts.app import app as application

# A variável 'application' é o padrão que o uWSGI do PythonAnywhere procura.
