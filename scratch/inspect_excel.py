import pandas as pd
import sys

def inspect_excel(path):
    print(f"\n--- Inspecting {path} ---")
    try:
        df = pd.read_excel(path)
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
    except Exception as e:
        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    inspect_excel("refs/planilhas/RevisaoForms_PorServico_Patrick.xlsx")
    inspect_excel("refs/planilhas/RevisaoForms.xlsx")
