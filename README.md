# 🏛️ Serviços CRC - Portal de Inteligência e Padronização

> **Modernizando a comunicação pública e a análise contratual da Prefeitura do Rio de Janeiro através de Inteligência Artificial.**

---

![Backend](https://img.shields.io/badge/Backend-Python_3.10+-blue?style=for-the-badge&logo=python)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla_JS_CSS3-orange?style=for-the-badge&logo=javascript)
![IA](https://img.shields.io/badge/AI-Google_Gemini-white?style=for-the-badge&logo=google)
![Environment](https://img.shields.io/badge/Environment-uv-green?style=for-the-badge)

## 🎯 Missão do Projeto

O **Serviços CRC** é uma plataforma centralizadora projetada para transformar a forma como os serviços públicos são descritos e geridos. O foco principal é a **Padronização Premium**: converter textos técnicos e burocráticos em descrições claras, acessíveis e amigáveis para o cidadão, utilizando modelos avançados de IA.

---

## 🚀 Funcionalidades Principais

### 1. 📂 Padronização de Serviços & Informações
Módulo avançado que processa descrições brutas e as organiza em um formato estruturado ("Premium").
- **Campos**: Título, O que é, Para que serve, Público-alvo, Legislação e Canais de Atendimento.
- **IA**: Utiliza o motor **Gemini 2.0 Flash** com prompts altamente refinados para garantir a fidelidade e a clareza.

### 2. 📝 Análise de Contratos Inteligente
Sistema de auditoria que compara relatórios mensais de prestação de contas com contratos base anonimizados.
- **Diferencial**: Identifica discrepâncias, metas não atingidas e pontos de atenção juridicamente relevantes de forma automatizada.

### 3. 📊 Sincronização de Dados (Excel Sync)
Automação para manter a rastreabilidade entre planilhas legadas (AS-IS) e o novo cenário de serviços (TO-BE), garantindo que nada se perca na transição.

---

## 🏗️ Arquitetura do Sistema

O projeto segue uma estrutura modular e leve, priorizando performance e facilidade de deploy:

```text
/backend
  ├── data/       # Hierarquia de serviços e persistência em JSON
  ├── prompts/    # "Cérebro" da IA - Instruções estruturadas para o Gemini
  └── scripts/    # Lógica de negócio, Flask API e scripts de automação
/frontend
  ├── index.html  # Dashboard principal
  └── padronizacao.html # Módulo de IA para roteamento de scripts
/refs             # Planilhas de referência e wireframes de design
```

---

## ⚙️ Execução Local

O projeto utiliza o gerenciador de pacotes **`uv`** para máxima velocidade e isolamento.

### 1. Preparação
Crie um arquivo `.env` na raiz do projeto (nunca comite este arquivo!):
```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.0-flash
```

### 2. Rodar a aplicação
A aplicação roda integralmente em um servidor unificado:
```bash
./start.sh
```
Acesse em: `http://localhost:8000`

---

## 🛡️ Segurança e Boas Práticas

*   **Proteção de Chaves**: O projeto está configurado para ignorar arquivos `.env`. Caso exponha uma chave acidentalmente, revogue-a imediatamente no painel do Google AI Studio.
*   **Anonimização**: Dados sensíveis (PII) são filtrados através do módulo `anonymizer.py` antes de serem processados pela IA em ambientes de produção.

---

## 🎨 Design System
Inspirado na identidade visual **Rio 1746**, o sistema utiliza a paleta **Azul Rio** e **Laranja 1746**, com uma interface "Neo-Brutalista" que foca em legibilidade e cards dinâmicos.

---
**Desenvolvido pela SUBTD/CRC - Prefeitura do Rio de Janeiro © 2026**
