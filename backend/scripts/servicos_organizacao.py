import json
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SERVICOS_JSON = BASE_DIR / 'backend' / 'data' / 'servicos.json'


class ServicoN2(BaseModel):
    name: str


class ServicoN1(BaseModel):
    id: str
    name: str
    children: List[ServicoN2]


def extract_servicos() -> List[ServicoN1]:
    """Lê a hierarquia de serviços diretamente do arquivo JSON absoluto."""
    if not SERVICOS_JSON.exists():
        print(f"ERRO: Arquivo {SERVICOS_JSON} não encontrado.")
        return []

    try:
        with open(SERVICOS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data.get("items", [])
            return [ServicoN1(**item) for item in items]
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return []
