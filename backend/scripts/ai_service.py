import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_description(item_type, item_name, parent_name=""):
    """
    Gera uma descrição curta e objetiva usando a API do Gemini.
    """
    if not GEMINI_API_KEY:
        return {"error": "Chave da API do Gemini não configurada."}

    prompt_context = f"Tema principal: {item_name}" if item_type == "theme" else f"Tema principal: {parent_name}\nSubtema: {item_name}"
    
    prompt_text = f"""Atue como um redator especialista em serviços públicos municipais. Sua tarefa é criar uma descrição extremamente objetiva para temas e subtemas do portal de atendimento 1746 da prefeitura.

Regras estritas:
1. Use uma linguagem simples e direta, acessível a qualquer cidadão.
2. Escreva exata e unicamente UMA frase curta.
3. Não use verbos no imperativo ou ação (ex: evite "Peça", "Solicite", "Informe"). Inicie a frase dando foco ao "quê" usando substantivos (ex: "Canal para requerimentos de...", "Área destinada à resolução de...").
4. Apenas retorne o texto final da descrição. Nunca inclua aspas, introduções, rótulos ou quebras de linha.

Contexto a ser descrito:
{prompt_context}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{ "text": prompt_text }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        
        generated_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return {"description": generated_text.strip()}
    except Exception as e:
        return {"error": str(e)}
