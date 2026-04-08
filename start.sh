#!/bin/bash

# Encerra os processos filhos caso o usuário pare o script (Ctrl+C)
trap "kill 0" SIGINT

echo "🚀 Iniciando o Backend (API via FastAPI na porta 8000)..."
uv run uvicorn backend.scripts.app:app --host 0.0.0.0 --port 8000 &

echo "🌐 Iniciando o Frontend (Servidor HTML na porta 3000)..."
cd frontend
python3 -m http.server 3000 &

echo ""
echo "========================================="
echo "✅ AMBIENTE INICIADO COM SUCESSO! ✅"
echo "========================================="
echo "👉 Abra no seu navegador: http://localhost:3000"
echo "========================================="
echo "Pressione Ctrl+C para encerrar todos os servidores."

# Fica aguardando para manter o script ativo
wait
