import pandas as pd

def verify_sync(path_output, path_revisao):
    print("--- Verifying Synchronization ---")
    
    # Check PertubaçãoSossego in Output
    df_output = pd.read_excel(path_output, sheet_name='PertubaçãoSossego')
    # Match Reference GM-RIO -> Fiscalização de perturbação do sossego
    df_ref = pd.read_excel(path_revisao, sheet_name='GM-RIO')
    
    # In Reference, let's find the value for 'Endereço' of 'Fiscalização de perturbação do sossego'
    ref_val = "NOT_FOUND"
    in_service = False
    for i, row in df_ref.iterrows():
        if "Fiscalização de perturbação do sossego" in str(row.iloc[0]):
            in_service = True
            continue
        if in_service:
            if "Endereço" in str(row.iloc[0]):
                ref_val = row.iloc[3] # Column D
                break
    
    # In Output, find the value for 'Endereço' in 'Cenário Futuro' (Column G / index 6)
    # The data starts at row 4? Let's search
    out_val = "NOT_FOUND"
    for i, row in df_output.iterrows():
        if "Endereço" in str(row.iloc[0]):
            out_val = row.iloc[6] # Column G
            break
            
    print(f"Service: PertubaçãoSossego | Field: Endereço")
    print(f"Reference Value (TO BE): {ref_val}")
    print(f"Output Value (Cenário Futuro): {out_val}")
    
    if str(ref_val) == str(out_val):
        print("✅ Match success!")
    else:
        print("❌ Match failed!")

if __name__ == "__main__":
    verify_sync('refs/planilhas/RevisaoForms_PorServico_Patrick_Sincronizada.xlsx', 'refs/planilhas/RevisaoForms.xlsx')
