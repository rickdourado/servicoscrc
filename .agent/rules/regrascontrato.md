---
trigger: always_on
---

# 📜 Regras Globais: Serviços CRC (App Modernizado)

**Descrição**: Regras obrigatórias de arquitetura, desenvolvimento e comportamento para o projeto Serviços CRC.
**Auto-attach**: A IA deve SEMPRE considerar este contexto antes de fazer quaisquer modificações.

## 1. 🏗️ Arquitetura e Tecnologias

- **Backend**: Python. Utilizar **Flask** para servir a API e os arquivos estáticos de forma unificada.
- **Gerenciador de Ambientes**: Sempre usar **`uv`** (ex: `uv run`, `uv pip install`).
- **Persistência de Dados**: A hierarquia de serviços reside em **`backend/data/servicos.json`**. Modificações na estrutura devem respeitar o modelo `Theme -> Subtheme -> Service`.
- **Frontend**: **Vanilla HTML5, CSS3 e JavaScript**. NUNCA usar bibliotecas pesadas. O design deve seguir a estética "Premium Prefeitura" (Azul Rio, Laranja 1746, bordas arredondadas e cards dinâmicos).
- **IA/LLM**: Integração com **Gemini (SDK google-genai)**. Prompts devem ser armazenados como arquivos `.md` em `backend/prompts/`.

## 2. 🗂️ Organização das Pastas

- **`/backend/scripts/`**: Lógicas de extração, IA e processamento (`anonymizer.py`, `servicos_organizacao.py`).
- **`/backend/data/`**: Arquivos de persistência (JSON).
- **`/backend/prompts/`**: Instruções de IA e contextos de contratos (.md).
- **`/frontend/`**: Interface do usuário (`index.html`, `padronizacao.html`).
- **`/refs/`**: Documentos base, planilhas originais e wireframes AS-IS.
- **`/changelogs/`**: Registro histórico de alterações por data.

## 3. 🚨 Regras Comportamentais de Execução

1. **Modo Produção (Segurança)**: O sistema detecta o ambiente via variável `IS_PRODUCTION`. Em produção (ex: PythonAnywhere), funcionalidades de Análise de Contratos devem ser **ocultadas** por segurança de dados (PII).
2. **Ambiente Unificado**: Para iniciar o projeto localmente, use sempre o comando `uv run run.py`. A aplicação roda integralmente em `localhost:8000`.
3. **Mapeamento de Planilhas**: Ao realizar extrações de Excel para JSON, mantenha a rastreabilidade das origens (SRGC vs Prefrio) para evitar duplicidade ou perda de dados.
4. **Respostas da IA**: Toda integração com Gemini que retorne dados estruturados deve forçar o formato JSON e ser tratada com Regex no backend para garantir estabilidade.

## 4. 📝 Changelogs e Commits

1. **Changelogs:** Documentar mudanças significativas em `changelogs/AAAA-MM-DD.md`.
2. **Conventional Commits:** Usar prefixos claros (`feat:`, `fix:`, `style:`, `refactor:`) em todos os commits.
3. **Clean Code**: Priorizar código direto, sem redundâncias e com tratamento de erros (try/except) robusto no backend para evitar interrupções do servidor Flask.
