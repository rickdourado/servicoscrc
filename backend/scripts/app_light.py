from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import backend.scripts.core_logic as core_logic
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import io

# --- COMENTADO PARA TESTE DE PERFORMANCE EM PRODUÇÃO ---
# from google import genai
# import backend.scripts.anonymizer as anonymizer
# from pypdf import PdfReader
# -------------------------------------------------------

load_dotenv()

# Configuração de caminhos para Produção (PythonAnywhere)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPTS_DIR = os.path.join(BASE_DIR, "backend", "prompts")

app = FastAPI(title="App Lúdico API (Versão Light)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# os.makedirs(anonymizer.TEMP_DIR, exist_ok=True)
# app.mount("/temp", StaticFiles(directory=anonymizer.TEMP_DIR), name="temp")

class OrderData(BaseModel):
    items: List[core_logic.Level1Item]

class AnalyzeTextData(BaseModel):
    text: str
    filename: str | None = None

@app.get("/api/data")
def get_data():
    items = core_logic.extract_data()
    return {"items": items}

@app.post("/api/save")
def save_data(data: OrderData):
    result = core_logic.save_new_order(data.items)
    return result

# --- ROTAS DE IA COMENTADAS PARA TESTE ---
"""
@app.post("/api/analyze-contract")
async def analyze_contract(file: UploadFile = File(...)):
    return {"result": "IA desativada temporariamente para testes de ambiente."}

@app.post("/api/anonymize")
async def anonymize_contract(file: UploadFile = File(...)):
    return {"masked_text": "IA desativada", "preview_url": None}

@app.post("/api/analyze-text")
async def analyze_text(data: AnalyzeTextData):
    return {"result": "IA desativada temporariamente para testes de ambiente."}
"""

# Export para PythonAnywhere (WSGI)
try:
    from a2wsgi import ASGIMiddleware
    application = ASGIMiddleware(app)
except ImportError:
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
