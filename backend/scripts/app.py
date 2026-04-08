from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import backend.scripts.core_logic as core_logic
from pydantic import BaseModel
import os
import google.generativeai as genai

app = FastAPI(title="App Lúdico API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderData(BaseModel):
    items: List[core_logic.Level1Item]

@app.get("/api/data")
def get_data():
    items = core_logic.extract_data()
    return {"items": items}

@app.post("/api/save")
def save_data(data: OrderData):
    result = core_logic.save_new_order(data.items)
    return result

@app.post("/api/analyze-contract")
async def analyze_contract(file: UploadFile = File(...)):
    try:
        with open("backend/prompts/analise_contrato.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
    except Exception as e:
        return {"result": f"Erro abrindo o arquivo de prompt: {str(e)}"}

    file_bytes = await file.read()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"result": f"MOCK RESULT (Modo Offline - Key Inexistente):\n\n🚨 O arquivo '{file.filename}' (Tamanho: ~{len(file_bytes)//1024} KB) foi recebido com sucesso!\n\nNo entanto, o backend não detectou a variável GEMINI_API_KEY.\nO Prompt que seria passado para a inteligência é:\n\n\"{prompt}\"\n\n➡️ Defina a variável 'GEMINI_API_KEY' no sistema antes do 'uv run' nas próximas análises."}
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # O Gemini aceita application/pdf nativamente na SDK se passado dessa forma
        if "pdf" in (file.content_type or "").lower():
             response = model.generate_content([prompt, {"mime_type": "application/pdf", "data": file_bytes}])
        else:
             # Para outros arquivos textuais sem tratamento nativo da SDK
             response = model.generate_content([prompt + f"\n\n(Aviso de sistema: O arquivo inserido é um formato textual DOC/DOCX. Como a SDK pura de bytes pede formatação nativa, em ambiente de prod realizaríamos parse extra do texto. Por enquanto, valide metadata).", "Nome: "+file.filename])
             
        return {"result": response.text}
    except Exception as e:
        return {"result": f"Erro interno ao invocar Inteligência Artificial: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
