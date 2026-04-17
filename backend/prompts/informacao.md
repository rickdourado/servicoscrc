Retorne APENAS o JSON estruturado com os 10 campos solicitados.

### `titulo_informacao`

**Objetivo:** Nome formal e claro da informação ou política pública.

**Fontes:** `titulo`, `assunto`

**Regras:**
- Use título em formato de nome próprio (Ex: "Programa de Reflorestamento Urbano").
- Evite verbos de ação no início se for puramente informacional.

### `descricao_resumida`

**Objetivo:** Resumo curto e direto da informação em 1-2 frases (máximo 2 linhas).

**Fontes:** `descricao`, `detalhes`

**Regras:**
- Texto sucinto; apenas um parágrafo curto.
- Use linguagem simples e objetiva; evite jargões.
- NÃO coloque prazos, documentos ou legislação aqui.

### `descricao_completa`

**Objetivo:** Texto detalhado e estruturado que explica a informação em profundidade.

**🚨 REGRAS CRÍTICAS - PRESERVAÇÃO DE CONTEÚDO:**
- **🚨 NUNCA invente ou adicione informações que não estejam no original**
- **Use APENAS o que está explícito nos dados**
- **PRESERVE TODAS as informações do original** - não remova nada
- **MANTENHA todos os prazos específicos** (se houver)
- **MANTENHA todas as observações importantes** (contatos, endereços, horários)
- **PRESERVE a formatação original** (enters, listas, parágrafos)
- **NÃO remova detalhes técnicos ou específicos**
- **NÃO adicione textos genéricos** que não estejam no original
- **NÃO resuma** - deve ter TODOS os detalhes

**🚨 REGRAS CRÍTICAS - O QUE NÃO INCLUIR (TÊM CAMPOS PRÓPRIOS):**
- **NÃO inclua tempo de atendimento** - vai em campo `tempo_atendimento`
- **NÃO inclua legislação** - vai em campo `legislacao_relacionada`
- **NÃO inclua endereços presenciais** - vai em campo `canais_presenciais`
- **NÃO inclua instruções de acesso** - vai em campo `instrucoes_solicitante`
- **NÃO inclua lista de documentos** - vai em campo `documentos_necessarios`

**Regras de Formato:**
- Use Markdown para ESTRUTURAÇÃO (## títulos, listas, negrito)
- Estrutura lógica com seções obrigatórias
- **Paragrafação**: Use parágrafos de 3-4 linhas para facilitar leitura

**Estrutura obrigatória (use EXATAMENTE estas 4 seções):**

```markdown
## O que é

[Explicação clara e conceitual do tema]

## Como funciona

[Funcionamento operacional, regras gerais e aplicação prática]

## Público-alvo

[A quem se destina esta informação ou quem é o beneficiário da política]

## Informações complementares

[Dados extras, curiosidades, contatos de suporte ou observações que não cabem acima]
```

### `custo`

**Objetivo:** Informar se há custos associados ou se a informação/acesso é gratuito.

**Regras:**
- Se não mencionado, assuma "Gratuito".

### `legislacao_relacionada`

**Objetivo:** Referências legais, decretos ou normas.

### `canais_presenciais`

**Objetivo:** Endereços e horários de atendimento físico/presencial.

### `canais_digitais`

**Objetivo:** Sites, portais e links oficiais.

### `instrucoes_solicitante`

**Objetivo:** Passo a passo de como o cidadão deve proceder para obter a informação ou acessar o local.

### `documentos_necessarios`

**Objetivo:** Lista de documentos que o cidadão precisa ter em mãos (se aplicável).

### `tempo_atendimento`

**Objetivo:** Prazo para resposta ou tempo estimado de espera/atendimento.

---

## Formato de Saída

```json
{
  "titulo_informacao": "string",
  "descricao_resumida": "string",
  "descricao_completa": "string (Markdown estruturado com as 4 seções)",
  "custo": "string",
  "legislacao_relacionada": "string",
  "canais_presenciais": "string",
  "canais_digitais": "string",
  "instrucoes_solicitante": "string",
  "documentos_necessarios": "string",
  "tempo_atendimento": "string"
}
```
