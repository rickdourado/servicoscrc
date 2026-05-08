"""
Script one-time para exportar Excel BasePrefRio → CSV leve.
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXCEL_PATH = BASE_DIR / "refs" / "servicestats" / "analisecarta.xlsx"
CSV_OUTPUT = BASE_DIR / "backend" / "data" / "prefrio_servicos.csv"

def export_to_csv():
    """Lê Excel e exporta colunas relevantes para CSV."""
    print(f"Lendo: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name='BasePrefRio')

    # Seleciona colunas necessárias (inclui analise_relevancia)
    cols = ['titulo_servico', 'nome_orgao', 'categoria', 'status_do_servico', 'analise_relevancia']
    df_clean = df[cols].copy()

    # Remove NaN
    df_clean = df_clean.fillna('')

    # Salva CSV
    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(CSV_OUTPUT, index=False, encoding='utf-8-sig')

    print(f"CSV criado: {CSV_OUTPUT}")
    print(f"Linhas: {len(df_clean)}")
    print(f"Tamanho: {CSV_OUTPUT.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    export_to_csv()
