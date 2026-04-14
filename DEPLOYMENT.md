# 🚀 Guia de Implantação: PythonAnywhere (Serviços CRC)

Este guia descreve como subir o projeto **Serviços CRC** para o PythonAnywhere, garantindo que o Backend (FastAPI) e o Frontend (HTML Estático) funcionem harmoniosamente.

## 1. Preparação do Código
O PythonAnywhere usa WSGI por padrão. Como o FastAPI é ASGI, usaremos a biblioteca `a2wsgi` para fazer a ponte.

### No Backend (`backend/scripts/app.py`):
Certifique-se de que as rotas estáticas estão configuradas corretamente para o ambiente de produção. Adicione no final do arquivo (ou em um arquivo separado):

```python
from a2wsgi import ASGIMiddleware
from backend.scripts.app import app

# Isso cria o objeto WSGI que o PythonAnywhere espera
application = ASGIMiddleware(app)
```

## 2. Configuração no PythonAnywhere

### Passo A: Clonar o Repositório
Abra um **Bash Console** no PythonAnywhere e execute:
```bash
git clone https://github.com/rickdourado/servicoscrc.git
cd servicoscrc
```

### Passo B: Criar Ambiente Virtual e Instalar Dependências
Não usaremos o `uv` no servidor (para evitar conflitos de binários), usaremos o `pip` padrão:
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn a2wsgi openpyxl google-generativeai pypdf PyMuPDF
```

### Passo C: Configurar Web App
1. Vá na aba **Web** do PythonAnywhere.
2. Clique em **Add a new web app**.
3. Escolha **Manual Configuration** -> **Python 3.10** (ou superior).
4. Em **Virtualenv**, aponte para: `/home/SEU_USUARIO/servicoscrc/venv`
5. Em **Code**, aponte o "Source code" para: `/home/SEU_USUARIO/servicoscrc`

### Passo D: Configurar o Arquivo WSGI
No PythonAnywhere, clique no link para editar o "WSGI configuration file". Delete tudo o que estiver lá e coloque apenas estas linhas para importar o arquivo que já está na raiz do seu projeto:

```python
import sys
import os

# Caminho para onde você clonou o projeto
path = '/home/SEU_USUARIO/servicoscrc'
if path not in sys.path:
    sys.path.append(path)

# Importa a aplicação já configurada com WSGI Middleware a partir da raiz
from pythonanywhere_wsgi import application
```

> **Importante:** Se o seu usuário for diferente de `projetocrcrj`, edite a linha 5 do arquivo `pythonanywhere_wsgi.py` para refletir o caminho correto.

## 3. Configurar o Frontend (Arquivos Estáticos)
Para que a interface abra direto no site, usaremos o mapeamento de arquivos estáticos do PythonAnywhere (é mais rápido que passar pelo FastAPI).

Na aba **Web**, role até a seção **Static files**:

| URL | Path |
| :--- | :--- |
| `/` | `/home/SEU_USUARIO/servicoscrc/frontend/` |

> **Nota:** Certifique-se de que as requisições de API no seu `script.js` agora apontem para o domínio correto (ex: `https://seu-usuario.pythonanywhere.com/api/...`).

## 4. Ajustes Finais
1. Clique no botão verde **Reload SEU-SITE** no topo da aba Web.
2. Verifique os **Error Logs** caso algo não funcione.

## 📝 Dicas Importantes
*   **Caminhos de Arquivo:** No `app.py`, sempre use caminhos absolutos baseados no `os.path.dirname(__file__)` para evitar erros de "File Not Found" na produção.
*   **Permissões:** O PythonAnywhere precisa de permissão de escrita na pasta `refs/planilhas/` se você for salvar dados lá.
