"""
Script de diagnóstico para PythonAnywhere
Execute: python backend/scripts/check_paths.py
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("DIAGNÓSTICO DE PATHS - ServicesCRC")
print("=" * 60)

# Current working directory
cwd = Path.cwd()
print(f"\n1. Working Directory: {cwd}")

# Script location
script_path = Path(__file__).resolve()
print(f"2. Script Path: {script_path}")

# Calculated BASE_DIR
BASE_DIR = script_path.parent.parent.parent
print(f"3. BASE_DIR (calculated): {BASE_DIR}")

# Environment override
env_base = os.environ.get("BASE_DIR")
if env_base:
    print(f"4. BASE_DIR (env override): {env_base}")
    BASE_DIR = Path(env_base)
else:
    print("4. BASE_DIR (env): NOT SET")

# Check critical paths
print("\n" + "=" * 60)
print("VERIFICAÇÃO DE ARQUIVOS CRÍTICOS")
print("=" * 60)

critical_files = [
    BASE_DIR / "backend" / "data" / "prefrio_servicos.csv",
    BASE_DIR / "backend" / "data" / "app.db",
    BASE_DIR / "backend" / "scripts" / "app.py",
    BASE_DIR / "frontend" / "index.html",
    BASE_DIR / ".env",
]

for file_path in critical_files:
    exists = "[OK]" if file_path.exists() else "[XX]"
    print(f"{exists} {file_path}")

# List backend/data/ contents
data_dir = BASE_DIR / "backend" / "data"
print(f"\n{'=' * 60}")
print(f"CONTEÚDO DE backend/data/")
print("=" * 60)

if data_dir.exists():
    for item in sorted(data_dir.iterdir()):
        size = item.stat().st_size if item.is_file() else "-"
        print(f"  {item.name:<40} {size:>12}")
else:
    print("  [XX] Diretorio nao existe!")

# Environment variables
print(f"\n{'=' * 60}")
print("VARIÁVEIS DE AMBIENTE")
print("=" * 60)
env_vars = ["BASE_DIR", "GEMINI_API_KEY", "SECRET_KEY", "IS_PRODUCTION"]
for var in env_vars:
    val = os.environ.get(var)
    if var == "GEMINI_API_KEY" and val:
        val = val[:10] + "..." if len(val) > 10 else val
    print(f"  {var:<20} = {val or '(not set)'}")

# Python path
print(f"\n{'=' * 60}")
print("PYTHON PATH (primeiras 5 entradas)")
print("=" * 60)
for i, p in enumerate(sys.path[:5], 1):
    print(f"  {i}. {p}")

print(f"\n{'=' * 60}")
print("TESTE: Importar prefrio_stats")
print("=" * 60)

try:
    import backend.scripts.prefrio_stats as prefrio
    print("[OK] Modulo importado com sucesso")

    try:
        summary = prefrio.get_summary()
        print(f"[OK] CSV carregado! Total registros: {summary['total_registros']}")
    except Exception as e:
        print(f"[XX] Erro ao carregar CSV: {e}")

except Exception as e:
    print(f"[XX] Erro ao importar: {e}")

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
