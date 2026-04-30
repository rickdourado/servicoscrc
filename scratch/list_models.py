import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

def list_models():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("Erro: GEMINI_API_KEY não encontrada.")
        return
    
    client = genai.Client(api_key=key)
    print("Modelos disponíveis:")
    try:
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Erro ao listar modelos: {e}")

if __name__ == "__main__":
    list_models()
