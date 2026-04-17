import pandas as pd

def inspect_patrick_sheets(path):
    print(f"\n--- Sheets in {path} ---")
    xl = pd.ExcelFile(path)
    print(xl.sheet_names)

if __name__ == "__main__":
    inspect_patrick_sheets("refs/planilhas/RevisaoForms_PorServico_Patrick.xlsx")
