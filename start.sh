#!/bin/bash

# Encerra os processos filhos caso o usuário pare o script (Ctrl+C)
trap "kill 0" SIGINT

echo "🚀 Iniciando o Ambiente Flask (Backend + Frontend na porta 8000)..."
echo "O Flask agora serve tanto a API quanto os arquivos estáticos."
echo ""

# Executa o app Flask diretamente usando uv
uv run python backend/scripts/app.py &

echo ""
echo "========================================="
echo "✅ AMBIENTE INICIADO COM SUCESSO! ✅"
echo "========================================="
echo "👉 Abra no seu navegador: http://localhost:8000"
echo "========================================="
echo "Pressione Ctrl+C para encerrar o servidor."

# Fica aguardando para manter o script ativo
wait
