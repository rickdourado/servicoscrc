# Dados PrefRio - CSV

## Arquivo
- `prefrio_servicos.csv` (132 KB)
- Contém 1065 registros de serviços municipais

## Colunas
1. `titulo_servico` - Nome do serviço
2. `nome_orgao` - Órgão responsável
3. `categoria` - Categoria do serviço
4. `status_do_servico` - Status (Publicado, Em Edição, etc)

## Atualização

Para atualizar dados a partir do Excel:

```bash
python backend/scripts/export_prefrio_csv.py
```

**Fonte:** `refs/servicestats/analisecarta.xlsx` (aba "Base PrefRio")

## Uso no Backend

O módulo `prefrio_stats.py` lê este CSV automaticamente.

Endpoints disponíveis:
- `/api/prefrio-stats/summary` - Resumo geral
- `/api/prefrio-stats/orgaos` - Lista órgãos com contagem
- `/api/prefrio-stats/servicos?orgao=X` - Lista serviços (filtro opcional)

## Deploy PythonAnywhere

1. Upload apenas o CSV (`prefrio_servicos.csv`)
2. Não é necessário pandas/openpyxl para leitura de Excel
3. Apenas `pandas` para ler CSV (muito mais leve)
