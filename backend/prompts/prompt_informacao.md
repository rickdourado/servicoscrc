## PROMPT ALTERNATIVO - SCRIPT DE INFORMAÇÃO

Ajuste o texto fornecido para o formato de SCRIPT DE INFORMAÇÃO da Prefeitura do Rio de Janeiro.
Não crie, complete, interprete nem acrescente informações: utilize exclusivamente o conteúdo enviado como base, apenas reorganizando e reescrevendo.

### Contexto

Diferente dos Scripts de Serviço (focados em ação/solicitação), os Scripts de Informação focam na compreensão, orientação e contextualização. O cidadão lê para entender, não para pedir. Ou seja, visa informar e não solicitar.

### 🚨 REGRAS CRÍTICAS - PRESERVAÇÃO DE CONTEÚDO

- **🚨 NUNCA invente ou adicione informações que não estejam no original**
- **Use APENAS o que está explícito nos dados**
- **PRESERVE TODAS as informações do original** - não remova nada
- **MANTENHA todos os prazos específicos** (se houver)
- **MANTENHA todos os observações importantes** (contatos, endereços, horários)
- **PRESERVE a formação original** (listas, parágrafos) quando fizer sentido
- **NÃO remova detalhes técnicos ou específicos** se forem relevantes para a compreensão
- **NÃO adicione textos genéricos** que não estejam no original

### Regras de Formato e Escrita

- **Saída em JSON:** A resposta deve ser estritamente um objeto JSON.
- **Use Markdown para ESTRUTURAÇÃO** dentro dos campos (bullet points, negrito para destaque).
- **Paragrafação:** Use parágrafos curtos (3-4 linhas) para facilitar a leitura.
- **Linguagem:** Simples, clara e cidadã. Evite termos técnicos, jurídicos ou burocráticos.
- **PROIBIDO:** Não use linguagem de solicitação, pedido ou atendimento (ex: "solicite", "agende", "clique aqui para acessar").
- **PROIBIDO:** Não utilize os tópicos “Para que serve” ou “Quem pode solicitar”.

### Estrutura Obrigatória (Campos JSON)

A saída deve conter exatamente os seguintes campos:

1. `o_que_e`
   - Definição clara do tema/política/equipamento.
   - Explique o conceito principal.

2. `como_funciona`
   - Funcionamento, regras gerais, aplicação prática na vida do cidadão.
   - Detalhes operacionais relevantes.

3. `publico_alvo`
   - Para quem a informação é relevante.
   - **Importante:** Não use como critério de elegibilidade/restrição ("quem pode solicitar"), mas como direcionamento de interesse ("a quem interessa").

4. `informacoes_importantes`
   - Inclua apenas quando for algo que não tem como ser adicionado em outro tópico, algo realmente importante para ter um destaque.
   - Contexto, observações relevantes, dados complementares.

### Exemplo de Aplicação

**Entrada:**
O que é
Este serviço oferece informações detalhadas sobre os Bailes Populares e o tradicional Baile da Cinelândia, eventos promovidos pela Riotur durante o período de carnaval. Os bailes acontecem em palcos montados ao ar livre, proporcionando entretenimento para a população.

Os Bailes Populares são realizados em palcos distribuídos pela cidade, no sábado, domingo, segunda e terça de carnaval. Neles, grupos de pagode e bandas carnavalescas se apresentam nos quatro dias de folia.

O Baile da Cinelândia, por sua vez, ocorre na Praça Marechal Floriano (em frente às escadarias da Câmara Municipal), também no sábado, domingo, segunda e terça de Carnaval.

**Saída Esperada:**
```json
{
  "o_que_e": "Programação de bailes de Carnaval gratuitos, realizados ao ar livre em diversos pontos da cidade, incluindo o tradicional palco da Cinelândia. Os eventos são organizados pela Riotur e contam com apresentações de grupos de pagode e bandas carnavalescas.",
  "como_funciona": "As apresentações ocorrem durante os quatro dias de folia (sábado, domingo, segunda e terça-feira de Carnaval).\n\n- **Bailes Populares:** Realizados em palcos montados em diferentes bairros do Rio de Janeiro.\n- **Baile da Cinelândia:** Acontece na Praça Marechal Floriano, no Centro, em frente às escadarias da Câmara Municipal.",
  "publico_alvo": "Moradores e visitantes interessados em aproveitar a programação gratuita de Carnaval no Rio de Janeiro.",
  "informacoes_importantes": "- O acesso aos palcos é livre e gratuito.\n- A programação detalhada com os horários e endereços de todos os palcos populares pode ser consultada nos canais oficiais da Riotur próximo ao período carnavalesco.\n- Por serem eventos ao ar livre, recomenda-se atenção às orientações de segurança e limpeza urbana da Prefeitura."
}
```

---

**Retorne APENAS o JSON no formato acima.**
