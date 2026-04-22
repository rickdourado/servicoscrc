import os
import logging
from google import genai
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_Utils")

from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

def call_gemini(prompt, model=None):
    """
    Executa uma chamada ao Gemini usando a chave padrão configurada no ambiente (.env).
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Nenhuma chave de API do Gemini encontrada no ambiente (.env)")

    model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    try:
        logger.info(f"Enviando requisição ao Gemini (Modelo: {model_name})...")
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        logger.info("Sucesso na geração do conteúdo.")
        return response
    except Exception as e:
        logger.error(f"Erro de API do Gemini: {str(e)}")
        raise e
