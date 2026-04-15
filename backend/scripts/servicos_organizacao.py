import json
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SERVICOS_JSON = BASE_DIR / "backend" / "data" / "servicos.json"

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""

class Subtheme(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    services: List[Service] = []

class Theme(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    subthemes: List[Subtheme] = []

def migrate_old_data(data):
    """Converte dados de 2 níveis para 3 níveis."""
    new_items = []
    items = data.get("items", [])
    
    for item in items:
        # Se já tiver subthemes, assume que já está no formato novo
        if "subthemes" in item:
            new_items.append(item)
            continue
            
        # Converte N1 -> Theme e children -> Services (dentro de um subtema "Geral")
        theme = {
            "id": item.get("id", str(uuid.uuid4())[:8]),
            "name": item.get("name", "Sem Nome"),
            "description": "",
            "subthemes": [
                {
                    "id": str(uuid.uuid4())[:8],
                    "name": "Geral",
                    "description": f"Serviços gerais de {item.get('name')}",
                    "services": [
                        {"id": str(uuid.uuid4())[:8], "name": child.get("name", ""), "description": ""}
                        for child in item.get("children", [])
                    ]
                }
            ]
        }
        new_items.append(theme)
    
    return {"items": new_items}

def extract_servicos() -> List[Theme]:
    """Lê a hierarquia de serviços e realiza migração se necessário."""
    if not SERVICOS_JSON.exists():
        return []

    try:
        with open(SERVICOS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Checa se precisa migrar
            if data.get("items") and "children" in data["items"][0]:
                data = migrate_old_data(data)
                # Salva a migração de volta para o arquivo
                with open(SERVICOS_JSON, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=4, ensure_ascii=False)
            
            items = data.get("items", [])
            return [Theme(**item) for item in items]
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return []
