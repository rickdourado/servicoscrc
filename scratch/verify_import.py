import sys
from pathlib import Path

# Adiciona o diretório backend/scripts ao path para importar models
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend" / "scripts"))

from app import app, db
from models import User, Activity

with app.app_context():
    print("--- AMOSTRA DE TAREFAS IMPORTADAS ---")
    tasks = Activity.query.limit(10).all()
    for t in tasks:
        parent_info = f"(Sub de {t.parent_id})" if t.parent_id else "(Principal)"
        print(f"ID: {t.id} | {t.title[:40]:<40} | Resp: {t.owner.username:<15} | {parent_info}")
    
    total = Activity.query.count()
    print(f"\nTotal no banco: {total}")
