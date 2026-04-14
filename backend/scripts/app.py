from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="App Lúdico API - JSON Powered")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderData(BaseModel):
    items: List[dict]


@app.get("/api/data")
def get_data():
    import backend.scripts.core_logic as core_logic

    items = core_logic.extract_data()
    return {"items": items}


@app.get("/api/servicos-organizacao")
def get_servicos_organizacao():
    import backend.scripts.servicos_organizacao as servicos_org

    items = servicos_org.extract_servicos()
    return {"items": [item.model_dump() for item in items]}


@app.post("/api/save")
def save_data(data: OrderData):
    import backend.scripts.core_logic as core_logic

    result = core_logic.save_new_order(data.items)
    return result


@app.get("/api/ping")
def ping():
    return {"status": "ok", "mode": "production" if IS_PRODUCTION else "development"}


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

try:
    from a2wsgi import ASGIMiddleware

    application = ASGIMiddleware(app)
except ImportError:
    pass

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
