Retorne APENAS o JSON estruturado com 1 campo.

### `descricao_resumida`

**Objetivo:** Resumo curto e direto do serviço em 1-2 frases (máximo 2 linhas).

**Fontes:** `descricao`, `detalhes`

**Regras:**
- Texto sucinto; não use listas ou seções Markdown — apenas um parágrafo curto.
- Use linguagem simples e objetiva; evite jargões.
- NÃO coloque prazos, documentos, canais ou legislação aqui.

### `descricao_completa`

**Objetivo:** Texto detalhado e estruturado (já documentado acima). Mantém todas as informações essenciais com formatação em Markdown.

**🚨 REGRAS CRÍTICAS - PRESERVAÇÃO DE CONTEÚDO:**
- **🚨 NUNCA invente ou adicione informações que não estejam no original**
- **Use APENAS o que está explícito nos dados do serviço**
- **PRESERVE TODAS as informações do original** - não remova nada
- **MANTENHA todos os prazos específicos** (ex: 72h, 6 dias, 20 dias)
- **MANTENHA todos os casos de uso e exceções** (ex: obras de concessionárias)
- **MANTENHA todas as observações importantes** (ex: contatos, limitações específicas)
- **PRESERVE a formatação original** (enters, listas, parágrafos)
- **NÃO remova detalhes técnicos ou específicos**
- **NÃO adicione textos genéricos** que não estejam no original
- **NÃO resuma** - esta é a descrição COMPLETA, deve ter TODOS os detalhes

**🚨 REGRAS CRÍTICAS - O QUE NÃO INCLUIR (TÊM CAMPOS PRÓPRIOS):**
- **NÃO inclua tempo de atendimento/prazo** - vai em campo `tempo_atendimento`
- **NÃO inclua limitações** ("o que o serviço não cobre") - vai em campo `servico_nao_cobre`
- **NÃO inclua legislação** (leis, decretos) - vai em campo `legislacao_relacionada`
- **NÃO inclua endereços presenciais** - vai em campo `canais_presenciais`
- **NÃO inclua instruções passo a passo** - vai em campo `instrucoes_solicitante`
- **NÃO inclua lista de documentos** - vai em campo `documentos_necessarios`

**Regras de Formato:**
- Use Markdown para ESTRUTURAÇÃO (## títulos, listas, negrito)
- Apenas simplifique PALAVRAS complexas, NÃO o conteúdo
- Estrutura lógica com seções
- **Paragrafação**: Use parágrafos de 3-4 linhas para facilitar leitura
- **NÃO deixe texto corrido** - separe em parágrafos e seções claras
- SEM limite de caracteres se necessário para preservar toda a informação
- Foco em: O QUE é, PARA QUE serve, QUEM pode usar

**Estrutura recomendada (use APENAS estas 3 seções):**

```markdown
## O que é

[Explicação clara do serviço em 1-2 parágrafos de 3-4 linhas cada]

## Para que serve

[Seja OBJETIVO e centrado na ENTREGA que o serviço proporciona.
Ex: "Fiscalização efetiva das frotas de ônibus", "Coleta/Remoção dos entulhos"
NÃO seja genérico como "visa melhorar" ou "busca garantir"]

## Quem pode solicitar

[Público-alvo e requisitos em parágrafos claros]
```

**⚠️ IMPORTANTE: NÃO INCLUA a seção "Como funciona"**
- Instruções passo a passo vão em `instrucoes_solicitante`
- Aqui você apenas APRESENTA e EXPLICA o serviço, não ensina como solicitar

**Uso de Markdown permitido:**
- `## Seção` - Títulos de seção
- `**texto**` - Negrito para destaque
- `- item` - Listas não ordenadas
- `1. item` - Listas ordenadas

**NÃO use:**
- Links `[texto](url)` - URLs vão em canais_digitais
- Imagens `![alt](url)`
- Código `` `code` ``
- Tabelas

**Exemplos:**

✅ **BOM - Estrutura correta com 3 seções:**
```markdown
## O que é

Emissão da Carteira de Estudante Municipal para alunos da rede
pública de ensino do Rio de Janeiro. O documento é reconhecido
oficialmente e permite acesso a benefícios estudantis.

## Para que serve

Garantir o direito à **meia-entrada** em eventos culturais (cinema,
teatro, shows), transporte intermunicipal e atividades esportivas.

## Quem pode solicitar

Estudantes regularmente matriculados em escolas municipais do
Rio de Janeiro. É necessário estar com a matrícula ativa e
apresentar documentação comprobatória.
```

✅ **BOM - Objetivo na entrega do serviço:**
```markdown
## O que é

Serviço de registro de denúncias de intolerância religiosa no
município do Rio de Janeiro.

## Para que serve

Registro oficial e encaminhamento de casos de discriminação,
violência ou constrangimento motivados por intolerância religiosa
aos órgãos competentes para investigação e apuração.

## Quem pode solicitar

Qualquer cidadão que tenha presenciado ou sido vítima de
intolerância religiosa, independente da religião praticada.
```

❌ **RUIM - Remove detalhes importantes:**
```markdown
Serviço de Emissão de Carteira de Estudante

Este serviço é destinado aos alunos da rede municipal que necessitam obter a carteira de estudante para usufruir dos benefícios previstos em lei.

Documentos necessários:
- RG
- CPF
- Comprovante de matrícula

Para acessar, visite: https://carioca.rio
```
**Problemas:**
- Estrutura pobre (sem seções claras)
- Lista de documentos (vai em campo próprio)
- URL (vai em canais_digitais)
- Linguagem formal ("usufruir", "previstos em lei")

❌ **MUITO RUIM - Remove informações críticas e adiciona genéricas:**
```markdown
## O que é
Este serviço realiza o reparo de buracos, deformações e afundamentos na pista de rolamento das ruas.

## Para que serve
Ele visa manter a segurança e a fluidez do trânsito.
```
**Problemas GRAVES:**
- REMOVEU prazos específicos (72h, 6 dias, 20 dias) que estavam no original
- REMOVEU casos de uso (obras de concessionárias, ciclovias, túneis)
- REMOVEU observações importantes (contato CETRIO, renivelamento)
- ADICIONOU texto genérico ("visa manter a segurança...") que NÃO estava no original
- **NUNCA FAÇA ISSO! Preserve TODAS as informações do original!**

❌ **MUITO RUIM - Inclui campos que têm lugar próprio:**
```markdown
## O que é
Remoção de entulho e bens inservíveis em até 20 dias. O serviço
é realizado pela COMLURB.

## Para que serve
Coleta e destinação adequada de entulhos.

## Quem pode solicitar
Qualquer cidadão do Rio de Janeiro.

## Canais presenciais
COMLURB - Rua Marques de Sapucaí, 3 - Centro - CEP: 20230-060
```
**Problemas GRAVES:**
- INCLUIU prazo "em até 20 dias" (vai em `tempo_atendimento`)
- INCLUIU seção "Canais presenciais" (vai em campo próprio `canais_presenciais`)
- **NUNCA faça isso! Cada informação tem seu campo específico!**

❌ **MUITO RUIM - Texto corrido sem paragrafação:**
```markdown
## O que é
Serviço de encerramento de folha de pagamento para servidores inativos do Previ-Rio que precisam regularizar sua situação funcional perante o instituto de previdência mediante apresentação de documentação específica e cumprimento de requisitos estabelecidos pela legislação vigente.
```
**Problema:** Texto corrido, difícil de ler. Divida em parágrafos de 3-4 linhas!

❌ **MUITO RUIM - Incluindo legislação no texto:**
```markdown
## Para que serve
Garantir assistência financeira conforme Lei nº 1234/2020 para
funeral de dependente do servidor.
```
**Problema:** Legislação vai em campo próprio `legislacao_relacionada`, não aqui!

**Diretrizes de Linguagem Simples:**
- Frases curtas (máximo 20 palavras)
- Voz ativa: "O aluno solicita" > "É solicitado pelo aluno"
- Palavras comuns: "pedir" > "solicitar", "usar" > "utilizar"
- Evite jargão: "meia-entrada" é OK (termo conhecido), mas explique termos técnicos
- Um conceito por parágrafo

**Atenção - Resumo das regras:**
- ✅ INCLUA: Explicação do que é, para que serve, quem pode solicitar
- ✅ INCLUA: Prazos, exceções, casos especiais, observações (quando fazem parte da EXPLICAÇÃO do serviço)
- ❌ NÃO INCLUA: Instruções passo a passo (vai em `instrucoes_solicitante`)
- ❌ NÃO INCLUA: Lista de documentos (vai em `documentos_necessarios`)
- ❌ NÃO INCLUA: Limitações/restrições (vai em `servico_nao_cobre`)
- ❌ NÃO INCLUA: Tempo de atendimento/prazo (vai em `tempo_atendimento`)
- ❌ NÃO INCLUA: Legislação/leis (vai em `legislacao_relacionada`)
- ❌ NÃO INCLUA: Endereços presenciais (vai em `canais_presenciais`)
- ❌ NÃO INCLUA: Seção "Como funciona"
- 📝 USE: Parágrafos de 3-4 linhas, evite texto corrido
- 🎯 SEJA: Objetivo na entrega do serviço em "Para que serve"

---

## Formato de Saída

```json
{
  "descricao_completa": "string (Markdown estruturado, max 1500 chars)"
}
```

---


**Fontes:** `descricao`, `detalhes`, `como_funciona`, `informacoes`

**Regras:**
- Preserve toda a informação do original; mantenha prazos, exceções e observações.
- Use as 3 seções recomendadas: `O que é`, `Para que serve`, `Quem pode solicitar`.
- Não repita informações entre os tópicos `O que é`, `Para que serve` e `Quem pode solicitar`.

### `servico_nao_cobre`

**Objetivo:** Listar explicitamente o que o serviço NÃO cobre (limitações e exclusões).

**Fontes:** `detalhes`, `informacoes`

**Regras:**
- Liste itens curtos (- item) com clareza.
- NÃO misturar com instruções ou documentos necessários.

### `tempo_atendimento`

**Objetivo:** Indicar o prazo ou tempo estimado de atendimento (ex.: 72 horas, até 20 dias).

**Fontes:** `detalhes`, `informacoes`

**Regras:**
- Informe apenas o prazo (texto curto). Se houver diferentes prazos para etapas, discrimine-os claramente.
- NÃO coloque este conteúdo dentro de `descricao_completa`.

### `custo`

**Objetivo:** Informar custo ou taxa do serviço, quando aplicável.

**Fontes:** `detalhes`, `informacoes`

**Regras:**
- Especifique valores e quando são cobrados (ex.: taxa única, mensalidade).
- Se não houver custo, explicite "isento" ou "gratuito".

### `resultado_solicitacao`

**Objetivo:** Descrever o resultado esperado após a conclusão do serviço (entregáveis, documentos emitidos, ações concluídas).

**Fontes:** `detalhes`, `informacoes`

**Regras:**
- Seja objetivo e liste o output final do processo.

### `documentos_necessarios`

**Objetivo:** Listar documentos exigidos para solicitar o serviço.

**Fontes:** `detalhes`, `informacoes`

**Regras:**
- Use lista de itens (`- Documento XYZ`).
- NÃO inclua documentos que não sejam explicitamente mencionados no original.

### `instrucoes_solicitante`

**Objetivo:** Orientações passo a passo para o solicitante (formulários, preenchimento, onde entregar).

**Fontes:** `como_funciona`, `detalhes`

**Regras:**
- Permite instruções passo a passo; use listas ordenadas quando necessário.
- NÃO inclua conteúdo que pertença a `descricao_completa` ou `legislacao_relacionada`.

### `canais_digitais`

**Objetivo:** Indicar canais digitais oficiais para solicitar ou acompanhar o serviço (URLs, plataformas, APIs).

**Fontes:** `informacoes`, `detalhes`

**Regras:**
- Forneça URLs ou identificadores de plataforma (quando disponíveis).
- Use apenas canais oficiais mencionados no original.

### `canais_presenciais`

**Objetivo:** Informar locais físicos e horários para atendimento presencial.

**Fontes:** `informacoes`, `detalhes`

**Regras:**
- Liste endereços completos e horários de atendimento, se presentes.
- NÃO coloque endereços em `descricao_completa`.

### `legislacao_relacionada`

**Objetivo:** Referências legais, decretos ou normas que regem o serviço.

**Fontes:** `detalhes`, `informacoes`

**Regras:**
- Liste leis e decretos com identificação (nº, ano) e, se necessário, um breve resumo.
- Não inserir textos legais longos; apenas referências e notas.
