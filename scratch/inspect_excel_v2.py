import pandas as pd

def inspect_excel_detailed(path):
    print(f"\n--- Detailed Inspection: {path} ---")
    xl = pd.ExcelFile(path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names[:3]: # Look at first 3 sheets
        print(f"\nSheet: {sheet}")
        df = pd.read_excel(path, sheet_name=sheet)
        print("Columns:", df.columns.tolist())
        print("Head (10 rows):")
        print(df.head(10))

if __name__ == "__main__":
    # Patrick's file
    inspect_excel_detailed("refs/planilhas/RevisaoForms_PorServico_Patrick.xlsx")
    # Latest reference file
    inspect_excel_detailed("refs/planilhas/RevisaoForms.xlsx")
