import subprocess
import sys
import time
import os

def main():
    print("🚀 Iniciando o Backend (API via FastAPI na porta 8000)...")
    # Inicializa o backend usando uv (deve estar no PATH)
    try:
        backend_process = subprocess.Popen(
            ["uv", "run", "uvicorn", "backend.scripts.app:app", "--host", "0.0.0.0", "--port", "8000"],
            shell=os.name == 'nt' # Executa no shell em Windows para encontrar o executável com facilidade se necessário
        )
    except FileNotFoundError:
        print("❌ Erro: Comando 'uv' não encontrado no ambiente.")
        sys.exit(1)

    print("🌐 Iniciando o Frontend (Servidor HTML na porta 3000)...")
    # Inicializa o frontend garantindo que o diretório atual de execução é o 'frontend'
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd="frontend"
    )

    print("\n=========================================")
    print("✅ AMBIENTE INICIADO COM SUCESSO! ✅")
    print("=========================================")
    print("👉 Abra no seu navegador: http://localhost:3000")
    print("=========================================")
    print("Pressione Ctrl+C para encerrar todos os servidores.\n")

    try:
        # Fica aguardando até que o usuário pressione Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Sinal de interrupção recebido (Ctrl+C). Encerrando os servidores...")
        
        # Encerra os processos
        backend_process.terminate()
        frontend_process.terminate()
        
        # Aguarda a finalização
        backend_process.wait()
        frontend_process.wait()
        
        print("✅ Servidores encerrados com sucesso.")

if __name__ == "__main__":
    main()
