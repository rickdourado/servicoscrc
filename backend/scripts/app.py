from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Nota: Imports pesados (genai, anonymizer, openpyxl) foram movidos para dentro das rotas
# para garantir que o "Reload" no PythonAnywhere seja instantâneo (Lazy Loading).

load_dotenv()

# Detecta se está em Modo Produção (para desabilitar IA pesada)
IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"

# Configuração de caminhos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = BASE_DIR / "backend" / "prompts"
TEMP_DIR = BASE_DIR / "backend" / "temp"
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="App Lúdico API - JSON Powered")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria pasta temporária se não existir
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/temp", StaticFiles(directory=str(TEMP_DIR)), name="temp")

# --- MODELOS ---
class Level2Item(BaseModel):
    name: str

class Level1Item(BaseModel):
    id: str
    name: str
    children: List[Level2Item]

class OrderData(BaseModel):
    items: List[dict] # Usado na comparação SGRC/Prefrio

class AnalyzeTextData(BaseModel):
    text: str
    filename: str | None = None

# --- ROTAS ---

@app.get("/api/data")
def get_data():
    """Rota de comparação (SGRC vs Prefrio) - Agora via JSON."""
    import backend.scripts.core_logic as core_logic
    items = core_logic.extract_data()
    return {"items": items}

@app.get("/api/servicos-organizacao")
def get_servicos_organizacao():
    """Rota da nova hierarquia (Organizador) - Agora via JSON."""
    import backend.scripts.servicos_organizacao as servicos_org
    items = servicos_org.extract_servicos()
    return {"items": [item.model_dump() for item in items]}

@app.post("/api/save")
def save_data(data: OrderData):
    """Salva a nova ordem (gera Excel para exportação)."""
    import backend.scripts.core_logic as core_logic
    result = core_logic.save_new_order(data.items)
    return result

@app.post("/api/analyze-contract")
async def analyze_contract(file: UploadFile = File(...)):
    if IS_PRODUCTION:
        return {"result": "⚠️ Esta funcionalidade está disponível apenas no ambiente de desenvolvimento local."}
    
    from google import genai
    from pypdf import PdfReader
    import backend.scripts.anonymizer as anonymizer
    import io

    # Lote de segurança para gemini_api_key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"result": "🚨 Erro: GEMINI_API_KEY não configurada."}

    file_bytes = await file.read()
    raw_text = ""
    is_pdf = file.filename.lower().endswith(".pdf")
    
    if is_pdf:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            raw_text += (page.extract_text() or "") + "\n"
    else:
        raw_text = file_bytes.decode("utf-8", errors="ignore")

    masked_text = anonymizer.process_and_save(raw_text, file.filename)
    
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=["Analise este contrato e resuma os pontos principais:\n\n" + masked_text]
    )
    return {"result": response.text}

@app.post("/api/analyze-text")
async def analyze_text(data: AnalyzeTextData):
    """Analisa o texto de um contrato já extraído e anonimizado."""
    if IS_PRODUCTION:
        return {"result": "⚠️ Esta funcionalidade está disponível apenas no ambiente de desenvolvimento local."}
    
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"result": "🚨 Erro: GEMINI_API_KEY não configurada."}

    client = genai.Client(api_key=api_key)
    
    prompt = (
        "Você é um especialista jurídico e de gestão de contratos do CRC. "
        "Analise o texto abaixo (que pode estar anonimizado) e extraia: "
        "1. Objeto do contrato; 2. Partes envolvidas; 3. Obrigações principais; "
        "4. Prazos e Vigência; 5. Valores (se houver). "
        "Responda em Markdown estruturado.\n\n"
        f"Texto: {data.text}"
    )

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt]
    )
    return {"result": response.text}

@app.post("/api/anonymize")
async def anonymize_contract(file: UploadFile = File(...)):
    if IS_PRODUCTION:
        return {"masked_text": "Recurso desabilitado em modo produção.", "preview_url": None}
    
    import backend.scripts.anonymizer as anonymizer
    file_bytes = await file.read()
    is_pdf = file.filename.lower().endswith(".pdf")
    
    if is_pdf:
        filename, masked_text = anonymizer.redact_pdf_visually(file_bytes)
        return {"masked_text": masked_text, "preview_url": f"/temp/{filename}"}
    else:
        masked_text = anonymizer.process_and_save(file_bytes.decode("utf-8", errors="ignore"), file.filename)
        return {"masked_text": masked_text, "preview_url": None}

@app.get("/api/ping")
def ping():
    return {"status": "ok", "mode": "production" if IS_PRODUCTION else "development"}

# --- FRONTEND (SERVE ARQUIVOS ESTÁTICOS) ---
# O ideal é que esta rota seja a última, pois ela captura tudo que não foi pego pelas rotas acima.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# Export para PythonAnywhere (WSGI)
try:
    from a2wsgi import ASGIMiddleware
    application = ASGIMiddleware(app)
except ImportError:
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
