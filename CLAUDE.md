# Serviços CRC - Automação de Tarefas

Sistema de automação para Coordenadoria de Relacionamento com o Cidadão (CRC) da Prefeitura do Rio de Janeiro.

---

## 📋 Regras de Desenvolvimento (OBRIGATÓRIAS)

As regras mestre e arquitetura estão em [AGENTS.md](AGENTS.md).

### Stack Técnico

**Backend:**
- Python + Flask (API + serve frontend estático)
- Gerenciador: **uv** (NUNCA pip diretamente)
- IA: Gemini SDK (`google-genai`)
- Banco: SQLite (via SQLAlchemy) ou JSON (`servicos.json`)

**Frontend:**
- Vanilla HTML/CSS/JS (SEM frameworks ou Tailwind)
- Design: **Premium Prefeitura** (Azul Rio #004a99, Laranja 1746 #ff6600)
- Estética: Glassmorphism, bordas 12px+, micro-interações

### Estrutura Crítica

```
backend/
  data/           → servicos.json, prefrio_servicos.csv, app.db
  scripts/        → app.py, prefrio_stats.py, anonymizer.py
  prompts/        → Instruções IA (.md)
frontend/         → index.html, servicosprefrio.html, styles.css
refs/             → Planilhas originais, wireframes
```

### Comandos Essenciais

```bash
# Iniciar servidor
uv run run.py

# Instalar dependência
uv pip install <package>

# Exportar CSV PrefRio
python backend/scripts/export_prefrio_csv.py
```

### Comportamento & Commits

- **Caveman Mode**: Habilitado por padrão (respostas curtas e diretas).
- **Conventional Commits**: `feat:`, `fix:`, `style:`, `refactor:`
- **Changelogs**: Documentar em `changelogs/AAAA-MM-DD.md`

### Segurança e Ambiente

- Variável `IS_PRODUCTION`: oculta módulos sensíveis (contratos) em produção
- Secrets: `.env` na raiz (NUNCA commitar)
- Deploy: PythonAnywhere (apenas CSV, sem Excel)

---

## 🎯 Módulos Principais

1. **Organizador de Serviços** - Reestrutura hierarquia SRGC/PrefRio
2. **Análise de Formulários** - Processa wireframes Excel
3. **Padronização de Serviços** - IA limpa descrições (Gemini)
4. **Gerenciamento de Tarefas** - Sistema auth + atividades
5. **Serviços do PrefRio** - Dashboard stats (CSV-based)
6. **Análise de Contratos** - Anonimização + IA (OFFLINE ONLY)

---

## 📚 Referências Importantes

- Regras Mestre: [AGENTS.md](AGENTS.md)
- Regras Operacionais: [.agent/rules/regrascrc.md](.agent/rules/regrascrc.md)
- Agents especializados: [.agent/agents/](.agent/agents/)
- Skills: [.agent/skills/](.agent/skills/)

---

**Nota**: Este arquivo é lido automaticamente pelo Claude Code. Modificações nas regras devem ser feitas em `AGENTS.md` primeiro.
