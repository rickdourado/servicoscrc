---
name: form-wizard-converter
description: Converte wireframes de formulários AS-IS (1746) em formulários TO-BE padrão Wizard, limpando os subtipos do tipo-lista e mapeando os campos.
---

# Form Wizard Converter

## 🎯 Objetivo
Transformar formulários originais (padrão antigo do 1746) em interfaces modernas **TO-BE** baseadas numa UI de **Wizard em 4 Etapas**, aplicando simultaneamente a limpeza de Dropdowns de categorias do wireframe AS-IS.

## 🛠️ Regras de Conversão

Quando for solicitado o processamento de um wireframe novo ou conversão para TO BE, o LLM deve executar as seguintes etapas:

### Passo 1: Limpeza do AS IS (Higienização de Categorias)
1. Localize o campo `<select class="listbox" id="tipo-lista">` no arquivo AS-IS.
2. **Remova todas as opções secundárias**, mantendo ESTRITAMENTE a primeira `<option selected>`.
3. Ajuste o tamanho da visualização do select alterando para `size="2"`.

### Passo 2: Geração do Arquivo TO BE (Wizard 4 Passos)
O TO-BE DEVE seguir o layout responsivo contido em `frontend/wireframes/tobe_wizard_base.html`. Leia aquele arquivo para usar como *boilerplate* de estilo, CSS e Stepper JS.

Mapeie as seções da seguinte forma:
- **Cabeçalho Global**: Altere `<title>` e a barra `<div class="service-title">` para o serviço atual (ex: "Estrutura de Imóvel / Defesa Civil").
- **Step 1 (Localização)**: Mantenha o layout padrão do template TO BE. Se no formulário AS-IS original houver necessidade expressa de Logradouro Inexistente, mantenha-o no Step 1.
- **Step 2 (Detalhes Específicos)**: Traduza os blocos de "Novo Chamado" e "Atributos Específicos" do AS-IS.
    - Transforme campos burocráticos (ex: "Origem da Ocorrência", "Unidade Org.") em lógicas de background (oculte visualmente se não agregar pro cidadão).
    - Converta Selects e Inputs para utilizarem a classe genérica `.form-control`.
    - Respeite as validações `.req` do AS-IS exigindo o texto `<span class="req">*</span>` no label do TO-BE.
- **Step 3 (Evidências / Fotos)**: Utilize SEMPRE a área Dropzone de arquivos providenciada pelo `tobe_wizard_base.html`. Delete o campo antigo "Caminho de foto" do AS IS.
- **Step 4 (Finalização)**: Ocultar no visual as lógicas de protocolo e focar em "Nível de Sigilo", "Telefone" e "Email", adaptando a mensagem final para citar o órgão destino (Ex: Defesa Civil).

### Passo 3: Outputs
- Salve o arquivo modificado do AS IS dentro de `frontend/wireframes/wireframe_<nome>.html`.
- Salve o novo arquivo TO BE dentro de `frontend/wireframes/tobe_<nome>.html`.
- Finalize escrevendo os registros da criação no `changelogs/`.
