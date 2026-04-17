import pandas as pd

def list_all_services(path_revisao):
    xl = pd.ExcelFile(path_revisao)
    for sheet in xl.sheet_names:
        if sheet in ['Campos_Verificação', 'Mails - Pontos Focais']:
            continue
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(path_revisao, sheet_name=sheet)
        for index, row in df.iterrows():
            first_col = str(row.iloc[0]).strip()
            # If the rest of the row is mostly NaN
            if first_col != 'nan' and pd.isna(row.iloc[1]) and pd.isna(row.iloc[3]):
                print(f"Service Found: [{first_col}]")

if __name__ == "__main__":
    list_all_services('refs/planilhas/RevisaoForms.xlsx')
