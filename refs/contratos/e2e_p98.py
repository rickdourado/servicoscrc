#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para processar arquivo CSV com timestamps de processamento de mensagens do chatbot.

Este script faz 4 coisas:
1. Limpa o arquivo CSV (remove linhas extras no início)
2. Lê os timestamps de início e fim
3. Calcula a diferença em segundos entre início e fim
4. Calcula o percentil 98 (P98) rigorosamente
"""

import csv
import sys
from datetime import datetime

# ============================================================================
# PARTE 1: Validação e preparação
# ============================================================================

# Verifica se o usuário passou o nome do arquivo como argumento
# Exemplo de uso correto: python3 process_brutos.py brutos.csv
if len(sys.argv) != 2:
    print("Uso: python3 process_brutos.py <arquivo_csv_entrada>")
    sys.exit(1)

# Pega o nome do arquivo que o usuário passou
input_file = sys.argv[1]

# ============================================================================
# PARTE 2: Leitura e processamento do CSV
# ============================================================================

# Esta lista vai guardar todas as linhas processadas
rows = []

# Abre o arquivo CSV para leitura
with open(input_file, 'r') as f:
    # Pula as duas primeiras linhas do arquivo porque elas contêm:
    # - Linha 1: Texto descritivo (ex: "Extração considerando o intervalo...")
    # - Linha 2: Linha vazia
    next(f)  # Pula linha 1
    next(f)  # Pula linha 2

    # A partir da linha 3, temos o cabeçalho real (start_ts_br,end_ts_br)
    # O csv.DictReader automaticamente usa essa linha como cabeçalho
    reader = csv.DictReader(f)

    # Agora processamos cada linha do arquivo (cada mensagem do chatbot)
    for row in reader:
        # Converte o timestamp de início de texto para objeto datetime
        # Exemplo: "2026-01-30T23:54:54.264567" vira um objeto que o Python entende como data/hora
        start = datetime.fromisoformat(row['start_ts_br'])

        # Converte o timestamp de fim de texto para objeto datetime
        end = datetime.fromisoformat(row['end_ts_br'])

        # Calcula quanto tempo levou entre início e fim
        # O resultado é em segundos (pode ter casas decimais)
        # Exemplo: se começou às 10:00:00 e terminou às 10:00:05.5, diff = 5.5 segundos
        diff = (end - start).total_seconds()

        # Adiciona esta linha processada na nossa lista
        rows.append({
            'start_ts_br': row['start_ts_br'],      # Timestamp de início (texto original)
            'end_ts_br': row['end_ts_br'],          # Timestamp de fim (texto original)
            'diff_in_seconds': diff                 # Diferença calculada em segundos
        })

# ============================================================================
# PARTE 3: Cálculo rigoroso do Percentil 98 (P98)
# ============================================================================

# O que é o P98?
# É um valor que indica: "98% das mensagens foram processadas em até X segundos"
# Exemplo: se P98 = 30 segundos, significa que 98% das mensagens levaram 30s ou menos

# Primeiro, pegamos só os valores de diferença em segundos e ordenamos do menor para o maior
# Exemplo: [0.1, 0.5, 2.3, 5.1, 10.2, ...] em ordem crescente
diffs = sorted([row['diff_in_seconds'] for row in rows])

# Conta quantas mensagens temos no total
n = len(diffs)

# Método de interpolação linear (método rigoroso e padrão para cálculo de percentis):
#
# Não pegamos simplesmente a posição 98% da lista, porque pode não existir exatamente
# nessa posição. Fazemos uma interpolação (uma "média ponderada") entre dois valores.
#
# Exemplo: se temos 100 valores e queremos P98:
# - Posição exata seria: 0.98 * (100-1) = 97.02
# - Como não existe posição 97.02, pegamos os valores das posições 97 e 98
# - E fazemos uma média ponderada entre eles usando a parte decimal (0.02)

# Calcula a posição exata do percentil 98
# Usamos (n-1) porque as posições começam do 0
rank = 0.98 * (n - 1)

# Pega a parte inteira da posição (a posição "de baixo")
# Exemplo: se rank = 97.02, então lower_idx = 97
lower_idx = int(rank)

# A posição "de cima" é a próxima
# Exemplo: se lower_idx = 97, então upper_idx = 98
upper_idx = lower_idx + 1

# Pega a parte decimal da posição (quanto vamos "interpolar")
# Exemplo: se rank = 97.02, então fraction = 0.02
fraction = rank - lower_idx

# Caso especial: se a posição de cima ultrapassar o tamanho da lista,
# simplesmente usamos o último valor
if upper_idx >= n:
    p98 = diffs[lower_idx]
else:
    # Interpolação linear: pegamos o valor de baixo e somamos uma fração
    # da diferença entre o valor de cima e o de baixo
    #
    # Fórmula: valor_baixo + fração * (valor_cima - valor_baixo)
    #
    # Exemplo:
    # - diffs[97] = 30.0 segundos
    # - diffs[98] = 32.0 segundos
    # - fraction = 0.02
    # - p98 = 30.0 + 0.02 * (32.0 - 30.0) = 30.0 + 0.04 = 30.04 segundos
    p98 = diffs[lower_idx] + fraction * (diffs[upper_idx] - diffs[lower_idx])

# ============================================================================
# PARTE 4: Exibição dos resultados
# ============================================================================

print(f"Processadas {len(rows)} mensagens")
print(f"P98 (percentil 98): {p98:.6f} segundos")
