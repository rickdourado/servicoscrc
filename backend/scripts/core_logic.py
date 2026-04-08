import openpyxl
from pydantic import BaseModel
from typing import List

EXCEL_PATH = '/Users/rickmac/Documents/dev/servicoscrc/refs/PlanilhaConsolidada.xlsx'
OUTPUT_PATH = '/Users/rickmac/Documents/dev/servicoscrc/refs/PlanilhaGerada.xlsx'

class Level1Item(BaseModel):
    id: str
    name: str
    level2: List[str]
    source: str

def extract_data() -> List[Level1Item]:
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    
    sheets_to_extract = [
        {"name_in_excel": "SRGC", "source_name": "SGRC"},
        {"name_in_excel": "Prefrio", "source_name": "Prefrio"}
    ]
    
    result = []
    idx = 0
    
    for sheet_info in sheets_to_extract:
        if sheet_info["name_in_excel"] not in wb.sheetnames:
            continue
            
        ws = wb[sheet_info["name_in_excel"]]
        data_dict = {}
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            nivel1 = row[0]
            nivel2 = row[1]
            
            if not nivel1:
                continue
                
            nivel1 = str(nivel1).strip()
            nivel2 = str(nivel2).strip() if nivel2 else ""
            
            if nivel1 not in data_dict:
                data_dict[nivel1] = []
                
            if nivel2 and nivel2 not in data_dict[nivel1]:
                data_dict[nivel1].append(nivel2)
        
        for n1_name, n2_list in data_dict.items():
            result.append(Level1Item(
                id=f"n1_{idx}",
                name=n1_name,
                level2=n2_list,
                source=sheet_info["source_name"]
            ))
            idx += 1
            
    return result

def save_new_order(ordered_items: List[Level1Item]):
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    # Split items
    sgrc_items = [item for item in ordered_items if item.source == "SGRC"]
    prefrio_items = [item for item in ordered_items if item.source == "Prefrio"]
    
    def write_to_sheet(sheet_name, items):
        ws = wb.create_sheet(title=sheet_name)
        ws.append(['Nível 1 – Usuário', 'Nível 2 – Tipo de Serviço ou Informação'])
        for item in items:
            if not item.level2:
                ws.append([item.name, ""])
            else:
                for n2 in item.level2:
                    ws.append([item.name, n2])
                    
    write_to_sheet("SRGC_Organizada", sgrc_items)
    write_to_sheet("Prefrio_Organizada", prefrio_items)
                
    wb.save(OUTPUT_PATH)
    return {"message": "Planilha gerada com sucesso", "path": OUTPUT_PATH}

if __name__ == "__main__":
    d = extract_data()
    print(f"Extraidos {len(d)} elementos globais.")
