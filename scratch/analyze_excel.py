import pandas as pd

df = pd.read_excel('refs/servicestats/analisecarta.xlsx', sheet_name='Base PrefRio')

print(f'Total rows: {len(df)}')
print(f'\nColumns:')
for col in df.columns:
    print(f'  - {col}')

print(f'\nSample data (first 3 rows):')
if 'titulo_servico' in df.columns and 'nome_orgao' in df.columns:
    print(df[['titulo_servico', 'nome_orgao']].head(3).to_string())
else:
    print(df.head(3).to_string())

print(f'\n--- ANÁLISE ---')
print(f'\nÓrgãos únicos: {df["nome_orgao"].nunique()}')
print(f'Serviços únicos: {df["titulo_servico"].nunique()}')

print(f'\nServiços por órgão:')
services_per_orgao = df.groupby('nome_orgao')['titulo_servico'].nunique().sort_values(ascending=False)
print(services_per_orgao.to_string())
