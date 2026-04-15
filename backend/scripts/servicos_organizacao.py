import json
import uuid
import shutil
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SERVICOS_JSON = BASE_DIR / "backend" / "data" / "servicos.json"
SERVICOS_ORIGINAL = BASE_DIR / "backend" / "data" / "servicos_original.json"

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
    """
    Corrige a migração:
    Old N1 (Theme) -> New Theme
    Old N2 (children) -> New Subthemes (Level 2)
    """
    new_items = []
    items = data.get("items", [])
    
    for item in items:
        # Se detetar o formato "Geral" incorreto que criei antes, vamos corrigir
        if "subthemes" in item and len(item["subthemes"]) == 1 and item["subthemes"][0]["name"] == "Geral":
            bad_sub = item["subthemes"][0]
            theme = {
                "id": item.get("id", str(uuid.uuid4())[:8]),
                "name": item.get("name", "Sem Nome"),
                "description": item.get("description", ""),
                "subthemes": [
                    {
                        "id": srv.get("id", str(uuid.uuid4())[:8]),
                        "name": srv.get("name", ""),
                        "description": "",
                        "services": []
                    }
                    for srv in bad_sub.get("services", [])
                ]
            }
            new_items.append(theme)
            continue

        # Se for o formato original de 2 níveis (com children)
        if "children" in item:
            theme = {
                "id": item.get("id", str(uuid.uuid4())[:8]),
                "name": item.get("name", "Sem Nome"),
                "description": "",
                "subthemes": [
                    {
                        "id": str(uuid.uuid4())[:8],
                        "name": child.get("name", ""),
                        "description": "",
                        "services": []
                    }
                    for child in item.get("children", [])
                ]
            }
            new_items.append(theme)
            continue
            
        # Caso contrário, mantém (já deve estar no formato 3-níveis correto)
        new_items.append(item)
    
    return {"items": new_items}

def extract_servicos() -> List[Theme]:
    """Lê a hierarquia e garante a migração e backup."""
    if not SERVICOS_JSON.exists():
        return []

    # Criar backup "original" se não existir ainda (para o botão Restaurar)
    # Nota: Vamos considerar o arquivo atual como 'original' se ele ainda tiver o formato antigo ou for o primeiro a ser processado
    if not SERVICOS_ORIGINAL.exists():
        shutil.copy(SERVICOS_JSON, SERVICOS_ORIGINAL)

    try:
        with open(SERVICOS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Checa se precisa corrigir a migração (formato "Geral" ou formato "children")
            needs_fix = False
            if data.get("items"):
                first = data["items"][0]
                if "children" in first or ("subthemes" in first and len(first["subthemes"]) == 1 and first["subthemes"][0]["name"] == "Geral"):
                    needs_fix = True
            
            if needs_fix:
                data = migrate_old_data(data)
                with open(SERVICOS_JSON, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=4, ensure_ascii=False)
            
            items = data.get("items", [])
            return [Theme(**item) for item in items]
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return []

def restore_original_data():
    """Restaura o servicos.json a partir do backup servicos_original.json."""
    if SERVICOS_ORIGINAL.exists():
        shutil.copy(SERVICOS_ORIGINAL, SERVICOS_JSON)
        return True
    return False
