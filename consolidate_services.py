import pandas as pd
from thefuzz import process

def main():
    # Load the data
    df_nivel3 = pd.read_excel('refs/planilhas/servicos/nivel3fica.xlsx')
    col_n3 = 'titulo_servico' if 'titulo_servico' in df_nivel3.columns else df_nivel3.columns[0]
    
    df_acompanhamento = pd.read_excel('refs/planilhas/servicos/acompanhamentoservicos.xlsx', header=1)
    
    col_acomp_title = 'titulo_servico'
    col_acomp_desc = 'descricao_completa'
    
    acomp_dict = {}
    for idx, row in df_acompanhamento.iterrows():
        t = str(row[col_acomp_title]).strip()
        d = str(row[col_acomp_desc]).strip()
        if t and t != 'nan':
            acomp_dict[t] = d
            
    acomp_titles = list(acomp_dict.keys())
    
    results = []
    
    for idx, row in df_nivel3.iterrows():
        title = str(row[col_n3]).strip()
        if pd.isna(title) or title == 'nan' or not title:
            continue
            
        desc = ""
        # 1. Exact match
        if title in acomp_dict:
            desc = acomp_dict[title]
        else:
            # 2. Fuzzy match
            best_match = process.extractOne(title, acomp_titles)
            if best_match and best_match[1] >= 85: # Threshold of 85
                desc = acomp_dict[best_match[0]]
                
        results.append({
            'titulo_servico': title,
            'descricao_completa': desc
        })
        
    df_results = pd.DataFrame(results)
    df_results.to_excel('refs/planilhas/servicos/servicos3consolidada.xlsx', index=False)
    print("Consolidation complete! Saved to refs/planilhas/servicos/servicos3consolidada.xlsx")
    print(f"Total rows processed: {len(results)}")
    print(f"Matches found: {len(df_results[df_results['descricao_completa'] != ''])}")

if __name__ == '__main__':
    main()
