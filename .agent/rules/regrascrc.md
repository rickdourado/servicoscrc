---
trigger: always_on
---

# 📜 Regras Globais: Serviços CRC (App Lúdico)

**Descrição**: Regras obrigatórias de arquitetura, desenvolvimento e comportamento para o projeto Serviços CRC.
**Auto-attach**: A IA deve SEMPRE considerar este contexto antes de fazer quaisquer modificações.

## 1. 🏗️ Arquitetura e Tecnologias

- **Backend**: Python. Para servir a aplicação e dados na web, utilizar **FastAPI** + **Uvicorn**.
- **Gerenciador de Ambientes**: Sempre usar **`uv`** (ex: `uv run`, `uv pip install`) ao invés do `pip` ou `conda` nativo.
- **Dados e Planilhas**: Qualquer extração de dados do Excel (.xlsx) deve utilizar **`openpyxl`**.
- **Frontend**: **Vanilla HTML5, CSS3 e JavaScript**. NUNCA usar bibliotecas pesadas (como React/Vue) ou frameworks como Tailwind/Bootstrap, a menos que o usuário explicitamente revogue esta regra.
- **Design de Interface (UI/UX)**: Sempre usar os conceitos de *design premium* definidos nas skills do antigravity (sombras suaves, tipografia forte, flexbox/grid avançado), respeitando combinações de cores claras (como Azul e Laranja, como fizemos no Drag-and-Drop) e fugindo do óbvio.

## 2. 🗂️ Organização das Pastas

Siga esse padrão estritamente quando criar novos recursos:
- **`/backend/scripts/`**: Código Python, lógicas extraídas (`core_logic.py`) e APIs HTTP (`app.py`).
- **`/frontend/`**: Onde os visuais e lógicas em tela residem (`index.html`, `styles.css`, `script.js`).
- **`/refs/`**: Apenas bancos de dados ou planilhas base (`PlanilhaConsolidada.xlsx` e outputs gerados).

## 3. 🚨 Regras Comportamentais de Execução

1. **Separação de Responsabilidades**: O backend NUNCA deve retornar HTML desenhado. Ele atua apenas como serviço inteligente (API Rest, JSON). Toda a transição de estado da tela é de responsabilidade do frontend.
2. **Contexto das Planilhas**: Ao manusear as planilhas da Prefeitura, SEMPRE cheque as diferenças entre a aba `SRGC` e a aba `Prefrio`, distinguindo seus elementos internamente antes de servir para a Web.
3. **Subindo o Ambiente**: Para testar ou referenciar a porta da aplicação, assuma constantemente a API em `localhost:8000` e a interface de usuário em `localhost:3000`. Use o `start.sh` localizado na raiz.

## 4. 📝 Changelogs e Controle de Versão

1. **Gestão de Changelogs:** Sempre que finalizar uma funcionalidade inteira, a IA deve documentar as mudanças criando (ou atualizando) um arquivo na pasta `changelogs/` seguindo obrigatoriamente o formato de data `AAAA-MM-DD.md`.
2. **Git Commits (Conventional Commits):** Ao realizar commits, a IA deve sempre seguir as convenções de versionamento semântico (usar prefixos como `feat:`, `fix:`, `docs:`, `refactor:`, `style:`, `chore:` etc.) para manter o histórico conciso e estruturado.
3. **Resumos Técnicos:** Ao documentar, a IA deve resumir a operação em formato estruturado, sem misturar a linguagem de Python com a do HTML de forma confusa.
