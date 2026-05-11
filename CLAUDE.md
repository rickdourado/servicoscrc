# Serviços CRC - Automação de Tarefas

Sistema de automação para Coordenadoria de Relacionamento com o Cidadão (CRC) da Prefeitura do Rio de Janeiro.

---

## 📋 Regras de Desenvolvimento (OBRIGATÓRIAS)

As regras mestre e arquitetura estão em [AGENTS.md](AGENTS.md). **LEITURA OBRIGATÓRIA.**

### Stack Técnico

**Backend:**
- Python + Flask (API + serve frontend estático)
- Gerenciador: **uv** (NUNCA pip diretamente)
- IA: Gemini SDK (`google-genai`)
- Persistência: JSON (`servicos.json`) + SQLite (`app.db` via SQLAlchemy)

**Frontend:**
- Vanilla HTML/CSS/JS (SEM frameworks ou Tailwind)
- Design: **Premium Prefeitura** (Azul Rio #004a99, Laranja 1746 #ff6600)
- Estética: Glassmorphism, bordas 12px+, micro-interações, Inter/Roboto

### Estrutura Crítica

```
backend/
  data/           → servicos.json, prefrio_servicos.csv, app.db
  scripts/        → app.py, servicos_organizacao.py, anonymizer.py, prefrio_stats.py
  prompts/        → Instruções IA (.md)
frontend/         → index.html, padronizacao.html, styles.css
refs/             → Planilhas originais, wireframes AS-IS
changelogs/       → Registro histórico de alterações
```

### Comandos Essenciais

```bash
# Iniciar servidor
uv run run.py

# Instalar dependência
uv pip install <package>

# Executar scripts específicos
python backend/scripts/map_services_to_subthemes.py
python backend/scripts/export_prefrio_csv.py
```

### Comportamento & Commits

- **Caveman Mode**: Habilitado por padrão (respostas curtas e diretas).
- **Conventional Commits**: `feat:`, `fix:`, `style:`, `refactor:`
- **Changelogs**: Documentar em `changelogs/AAAA-MM-DD.md`
- **Socratic Gate**: Mínimo 3 perguntas antes de grandes mudanças.

### Segurança e Ambiente

- Variável `IS_PRODUCTION`: oculta módulos sensíveis (contratos/PII) em produção.
- Secrets: `.env` na raiz (NUNCA commitar).
- Deploy: PythonAnywhere (apenas CSV, sem Excel).

---

## 🎯 Módulos Principais

1. **Organizador de Serviços** - Reestrutura hierarquia SRGC/PrefRio (prefrio-domain-specialist).
2. **Análise de Formulários** - Processa wireframes Excel (gemini-integration-specialist).
3. **Padronização de Serviços** - IA limpa descrições Gemini (gemini-integration-specialist).
4. **Gerenciamento de Tarefas** - Sistema auth + atividades SQLite (backend-specialist).
5. **Serviços do PrefRio** - Dashboard stats CSV-based (prefrio-domain-specialist).
6. **Análise de Contratos** - Anonimização + IA OFFLINE ONLY (security-auditor + gemini-integration-specialist).
7. **Interface Premium** - Design Glassmorphism Azul Rio/Laranja 1746 (frontend-specialist).

---

## 📚 Referências Importantes

- Regras Mestre: [AGENTS.md](AGENTS.md)
- Regras Operacionais: [.agent/rules/regrascontrato.md](.agent/rules/regrascontrato.md)
- Agents especializados: [.agent/agents/](.agent/agents/)
  - Core: frontend-specialist, backend-specialist, gemini-integration-specialist, prefrio-domain-specialist
  - Support: orchestrator, debugger, database-architect, security-auditor, test-engineer, devops-engineer
- Skills: [.agent/skills/](.agent/skills/)

## 🚀 Quick Agent Reference

| Tarefa | Agent Recomendado |
|--------|-------------------|
| Interface HTML/CSS | `frontend-specialist` |
| API Flask/Gemini | `backend-specialist` |
| Prompts IA/Validação JSON | `gemini-integration-specialist` |
| Hierarquia servicos.json | `prefrio-domain-specialist` |
| Bug complexo | `debugger` |
| Schema SQLite | `database-architect` |
| Segurança/PII | `security-auditor` |
| Testes | `test-engineer` |
| Deploy PythonAnywhere | `devops-engineer` |
| Coordenação multi-tarefa | `orchestrator` |

---

**Nota**: Este arquivo é lido automaticamente pelo Claude Code. Modificações nas regras devem ser feitas em `AGENTS.md` primeiro.
