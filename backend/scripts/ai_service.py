import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

def generate_description(item_type, item_name, parent_name=""):
    """
    Gera uma descrição curta e objetiva usando a API do Gemini com suporte a rotação de chaves.
    """
    from ai_utils import call_gemini_with_rotation
    
    prompt_context = f"Tema principal: {item_name}" if item_type == "theme" else f"Tema principal: {parent_name}\nSubtema: {item_name}"
    
    prompt_text = f"""Atue como um redator especialista em serviços públicos municipais. Sua tarefa é criar uma descrição extremamente objetiva para temas e subtemas do portal de atendimento 1746 da prefeitura.

Regras estritas:
1. Use uma linguagem simples e direta, acessível a qualquer cidadão.
2. Escreva exata e unicamente UMA frase curta.
3. Não use verbos no imperativo ou ação (ex: evite "Peça", "Solicite", "Informe"). Inicie a frase dando foco ao "quê" usando substantivos (ex: "Canal para requerimentos de...", "Área destinada à resolução de...").
4. Apenas retorne o texto final da descrição. Nunca inclua aspas, introduções, rótulos ou quebras de linha.

Contexto a ser descrito:
{prompt_context}"""

    try:
        response = call_gemini_with_rotation(prompt_text, model=GEMINI_MODEL)
        return {"description": response.text.strip()}
    except Exception as e:
        return {"error": str(e)}
