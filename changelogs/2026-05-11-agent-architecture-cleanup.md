# 2026-05-11: Agent Architecture Cleanup & Specialization

## 🎯 Objetivo
Limpeza e especialização da arquitetura de agentes, removendo agentes irrelevantes e criando especialistas específicos para o projeto Serviços CRC.

---

## 🗑️ Agentes Removidos (Irrelevantes)

### Removidos de `.agent/agents/` e `.claude/agents/`:
1. **game-developer.md** - Projeto não envolve desenvolvimento de jogos
2. **mobile-developer.md** - Sem desenvolvimento mobile planejado
3. **seo-specialist.md** - App interno (não público), SEO não é prioridade
4. **penetration-tester.md** - `security-auditor` já cobre necessidades de segurança

**Justificativa**: Reduzir complexidade e focar em agentes relevantes para gestão de serviços públicos.

---

## ✨ Novos Agentes Especializados

### 1. **gemini-integration-specialist.md**
**Propósito**: Expert em Gemini SDK (`google-genai`) para integração IA.

**Responsabilidades**:
- Padronização de descrições de serviços via IA
- Prompt engineering (armazenamento em `backend/prompts/*.md`)
- Validação de output JSON estruturado com Regex
- Tratamento de erros da API Gemini
- Otimização de custos (uso de `gemini-1.5-flash`)

**Quando Usar**: Tarefas envolvendo Gemini API, prompts, validação JSON, ou processamento IA.

---

### 2. **prefrio-domain-specialist.md**
**Propósito**: Expert em hierarquia SRGC/PrefRio e lógica de domínio.

**Responsabilidades**:
- Gerenciamento de `servicos.json` (Theme → Subtheme → Service)
- Reconciliação SRGC vs PrefRio (deduplicação)
- Mapeamento de IDs entre sistemas
- Exportação CSV para PythonAnywhere
- Validação de integridade hierárquica

**Quando Usar**: Modificações em `servicos.json`, reconciliação de dados, ou lógica de categorização.

---

## 🔧 Agentes Atualizados

### 1. **frontend-specialist.md**
**Mudanças**:
- ✅ Adicionado contexto projeto: Vanilla HTML/CSS/JS (SEM React/Tailwind)
- ✅ Design System: Premium Prefeitura (Azul Rio #004a99, Laranja 1746 #ff6600)
- ✅ Estética: Glassmorphism, bordas 12px+, micro-interações
- ✅ Seção "SERVIÇOS CRC PROJECT OVERRIDES" com anti-patterns
- ❌ Removido: Skills de React/Next.js/Tailwind da metadata

**Frontmatter Atualizado**:
```yaml
description: Senior Frontend Architect for Serviços CRC. Specializes in Vanilla HTML/CSS/JS with Premium Prefeitura design system.
skills: clean-code, web-design-guidelines, frontend-design, lint-and-validate
project_context: |
  - Stack: Vanilla HTML5/CSS3/JavaScript ONLY
  - Design: Premium Prefeitura (Azul Rio #004a99, Laranja 1746 #ff6600)
  - NO frameworks, NO React, NO Tailwind
```

---

### 2. **backend-specialist.md**
**Mudanças**:
- ✅ Adicionado contexto projeto: Flask + Gemini SDK + SQLite/JSON
- ✅ Gerenciador de pacotes: `uv` MANDATÓRIO (NUNCA `pip`)
- ✅ Deploy: PythonAnywhere (CSV only, sem Excel)
- ✅ Seção "SERVIÇOS CRC PROJECT OVERRIDES" com comandos críticos
- ❌ Removido: Skills Node.js/Rust da metadata

**Frontmatter Atualizado**:
```yaml
description: Expert backend architect for Serviços CRC. Specializes in Flask + Gemini SDK integration with JSON/SQLite persistence.
skills: clean-code, python-patterns, api-patterns, database-design, lint-and-validate
project_context: |
  - Stack: Python 3.12+ with Flask
  - Package Manager: uv ONLY
  - IA: Gemini SDK (google-genai)
  - Persistence: JSON + SQLite
```

---

## 📝 Documentação Atualizada

### AGENTS.md
**Adições**:
- ✅ Seção "🤖 Agentes Especializados Disponíveis"
- ✅ Categorização: Core Project Agents vs Support Agents
- ✅ Routing expandido com 4 novos agentes especializados:
  - Gemini/IA/Prompts → `gemini-integration-specialist`
  - SRGC/PrefRio/Hierarquia → `prefrio-domain-specialist`

**Agents Listados (18 total)**:
1. Core: frontend-specialist, backend-specialist, gemini-integration-specialist, prefrio-domain-specialist
2. Support: orchestrator, debugger, database-architect, security-auditor, test-engineer, devops-engineer, performance-optimizer, documentation-writer, project-planner, code-archaeologist, qa-automation-engineer, explorer-agent, product-manager, product-owner

---

### CLAUDE.md
**Adições**:
- ✅ Módulos Principais mapeados para agentes responsáveis
- ✅ Seção "🚀 Quick Agent Reference" (tabela tarefa → agent)
- ✅ Referências expandidas com categorias Core/Support

**Exemplo Quick Reference**:
```markdown
| Tarefa | Agent Recomendado |
|--------|-------------------|
| Prompts IA/Validação JSON | `gemini-integration-specialist` |
| Hierarquia servicos.json | `prefrio-domain-specialist` |
```

---

## 📂 Estrutura de Arquivos Final

### .agent/agents/ (18 agents)
```
✅ backend-specialist.md               (ATUALIZADO)
✅ frontend-specialist.md              (ATUALIZADO)
✅ gemini-integration-specialist.md    (NOVO)
✅ prefrio-domain-specialist.md        (NOVO)
✅ code-archaeologist.md
✅ database-architect.md
✅ debugger.md
✅ devops-engineer.md
✅ documentation-writer.md
✅ explorer-agent.md
✅ orchestrator.md
✅ performance-optimizer.md
✅ product-manager.md
✅ product-owner.md
✅ project-planner.md
✅ qa-automation-engineer.md
✅ security-auditor.md
✅ test-engineer.md
```

### .claude/agents/ (18 agents)
Espelhamento completo de `.agent/agents/` para uso do Claude Code.

---

## ✅ Validação

**Agentes Removidos**: 4 (game, mobile, seo, pentester)
**Agentes Criados**: 2 (gemini-integration, prefrio-domain)
**Agentes Atualizados**: 2 (frontend, backend)
**Total Final**: 18 agentes (ambas pastas sincronizadas)

**Verificação**:
```bash
# .agent/agents/
ls -1 .agent/agents/*.md | wc -l
# Output: 18

# .claude/agents/
ls -1 .claude/agents/*.md | wc -l
# Output: 18
```

---

## 🎯 Próximos Passos

1. **Testar novos agentes** em cenários reais:
   - `gemini-integration-specialist` → Padronização de serviços
   - `prefrio-domain-specialist` → Modificação servicos.json

2. **Validar AGENTS.md** em contexto real (verificar routing funciona)

3. **Opcional**: Criar skills específicos para Gemini SDK e PrefRio domain logic

---

**Timestamp**: 2026-05-11 08:30 UTC-3
**Autor**: Claude Code (Caveman Mode)
**Commit Message Sugerido**: `refactor: cleanup agent architecture, add Gemini/PrefRio specialists`
