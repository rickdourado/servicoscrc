import os
import logging
from google import genai
from google.genai import errors
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_Utils")

load_dotenv()

def get_api_keys():
    """Retorna uma lista de todas as chaves GEMINI_API_KEY_N configuradas."""
    keys = []
    for i in range(1, 20):  # Procura por até 20 chaves
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
    # Se não houver chaves numeradas, tenta a chave padrão única
    if not keys:
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            keys.append(single_key)
    return keys

def call_gemini_with_rotation(prompt, model=None):
    """
    Executa uma chamada ao Gemini tentando as chaves disponíveis em sequência.
    Retorna a resposta ou levanta a última exceção se todas falharem.
    """
    keys = get_api_keys()
    if not keys:
        raise ValueError("Nenhuma chave de API do Gemini encontrada no ambiente (.env)")

    model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    last_exception = None

    for idx, key in enumerate(keys):
        try:
            logger.info(f"Tentando chave {idx + 1}/{len(keys)}...")
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            logger.info(f"Sucesso com a chave {idx + 1}.")
            return response
        except errors.APIError as e:
            # Tenta pegar o status_code ou verificar na mensagem
            status_code = getattr(e, 'status_code', None)
            is_quota_error = (status_code == 429) or ("429" in str(e)) or ("RESOURCE_EXHAUSTED" in str(e))
            
            if is_quota_error:
                logger.warning(f"Chave {idx + 1} atingiu o limite de cota (429). Tentando próxima...")
                last_exception = e
                continue
            
            logger.error(f"Erro de API com a chave {idx + 1}: {str(e)}")
            last_exception = e
        except Exception as e:
            logger.error(f"Erro inesperado com a chave {idx + 1}: {str(e)}")
            last_exception = e
            
    logger.error("Todas as chaves de API falharam.")
    raise last_exception
