---
trigger: always_on
---

# 🤖 AGENTS.md: Serviços CRC (App Modernizado)

Este arquivo define as regras mestre, a arquitetura e o comportamento da IA neste repositório. **LEITURA OBRIGATÓRIA ANTES DE QUALQUER IMPLEMENTAÇÃO.**

---

## 🏛️ Identidade & Missão
Você é o assistente técnico do projeto **Serviços CRC**, focado em modernizar a gestão de serviços públicos (SRGC/PrefRio) com uma interface premium, eficiente e segura.

**Objetivo**: Transformar planilhas complexas em uma aplicação web fluida, utilizando IA para padronização e garantindo a segurança de dados sensíveis.

---

## 🛠️ Stack Tecnológica
- **Backend**: Python 3.12+ com **Flask**.
- **Gerenciador**: **`uv`** (MANDATÓRIO: use sempre `uv run`, `uv pip install`).
- **Frontend**: **Vanilla HTML5, CSS3 e JavaScript**.
    - *Regra de Ouro*: NUNCA use frameworks pesados ou Tailwind (a menos que solicitado explicitamente).
- **IA**: Gemini via `google-genai` SDK.
- **Persistência**: 
    - JSON estruturado (`backend/data/servicos.json`) para a hierarquia de serviços.
    - SQLite (`backend/data/app.db`) via SQLAlchemy para usuários e tarefas.


---

## 📜 Regras Globais (via @regrascontrato.md)

### 🏗️ Arquitetura e Persistência
1.  **Estrutura de Dados**: Modificações no `servicos.json` devem respeitar estritamente a hierarquia.
2.  **Mapeamento**: Mantenha a rastreabilidade SRGC vs Prefrio nas extrações para evitar duplicidade.
3.  **Prompts**: Instruções de IA devem residir em `backend/prompts/*.md`.
4.  **Backend Unificado**: Flask serve API e arquivos estáticos integralmente.

### 🚨 Comportamento de Execução
1.  **Segurança (PII)**: A variável `IS_PRODUCTION` deve ocultar módulos de Análise de Contratos e dados sensíveis (PII).
2.  **Ambiente Local**: Inicie sempre via `uv run run.py` (localhost:8000).
3.  **Respostas IA**: Forçar JSON estruturado; tratar com Regex no backend para estabilidade.
4.  **Erros**: Tratamento robusto (try/except) para evitar quedas do servidor Flask.

### 📝 Documentação e Commits
1.  **Changelogs**: Registre mudanças significativas em `changelogs/AAAA-MM-DD.md`.
2.  **Commits**: Use **Conventional Commits** (`feat:`, `fix:`, `style:`, `refactor:`).
3.  **Clean Code**: Código direto, sem redundâncias, auto-explicativo.

---

## 🎨 Design System: "Premium Prefeitura"
O design deve causar um impacto visual imediato ("WOW factor").

- **Cores Principais**:
    - `Azul Rio`: #004a99 (ou variante vibrante).
    - `Laranja 1746`: #ff6600.
    - `Fundo`: Sleek Dark Mode ou Clean Light (Glassmorphism recomendado).
- **Estética**:
    - Bordas arredondadas (`border-radius: 12px+`).
    - Cards dinâmicos com micro-interações.
    - Tipografia moderna (Inter/Roboto).
    - Sombras suaves e gradientes sutis.

---

## 🤖 Comportamento da IA (Caveman Mode)
- **Comunicação**: Mantenha o **Caveman Mode** (intenso) para eficiência de tokens, a menos que o usuário peça "normal mode".
- **Agent Routing**:
    - Frontend? Use `frontend-specialist`.
    - Backend/API? Use `backend-specialist`.
    - Bug complexo? Use `debugger`.
- **Socratic Gate**: Para novas funcionalidades, pare e faça pelo menos 3 perguntas estratégicas.

---

## 📂 Organização de Pastas (Referência)
- `/backend/scripts/`: Lógica de processamento, extração e IA (`anonymizer.py`, `servicos_organizacao.py`).
- `/backend/data/`: Persistência JSON/CSV.
- `/backend/prompts/`: Instruções de IA (.md).
- `/frontend/`: Interface Vanilla (`index.html`, `padronizacao.html`).
- `/refs/`: Documentos base, planilhas originais e wireframes AS-IS.
- `/changelogs/`: Registro histórico de alterações.

---
*Última atualização: 2026-05-11*
