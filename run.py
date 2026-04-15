import subprocess
import sys
import time
import os

def main():
    print("🚀 Iniciando o Ambiente Flask (Backend + Frontend na porta 8000)...")
    print("O Flask agora serve tanto a API quanto os arquivos estáticos.\n")

    # Inicializa o app Flask usando uv (deve estar no PATH)
    try:
        # No Flask, rodamos o script python diretamente
        flask_process = subprocess.Popen(
            ["uv", "run", "python", "backend/scripts/app.py"],
            shell=os.name == 'nt' 
        )
    except FileNotFoundError:
        print("❌ Erro: Comando 'uv' não encontrado no ambiente.")
        sys.exit(1)

    print("\n=========================================")
    print("✅ AMBIENTE INICIADO COM SUCESSO! ✅")
    print("=========================================")
    print("👉 Abra no seu navegador: http://localhost:8000")
    print("=========================================")
    print("Pressione Ctrl+C para encerrar o servidor.\n")

    try:
        # Fica aguardando até que o usuário pressione Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Sinal de interrupção recebido (Ctrl+C). Encerrando o servidor...")
        
        # Encerra o processo
        flask_process.terminate()
        
        # Aguarda a finalização
        flask_process.wait()
        
        print("✅ Servidor encerrado com sucesso.")

if __name__ == "__main__":
    main()
