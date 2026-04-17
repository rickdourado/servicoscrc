import pandas as pd

def inspect_sheet(path, sheet_name, rows=20):
    print(f"\n--- Sheet: {sheet_name} in {path} ---")
    df = pd.read_excel(path, sheet_name=sheet_name)
    print(df.head(rows).to_string())

if __name__ == "__main__":
    # Check GM-RIO sheet in RevisaoForms.xlsx because it matches the first sheet of Patrick's file
    inspect_sheet("refs/planilhas/RevisaoForms.xlsx", "GM-RIO", rows=50)
    # Check the first sheet of Patrick's file to compare
    inspect_sheet("refs/planilhas/RevisaoForms_PorServico_Patrick.xlsx", "Fiscalizacao", rows=30)
