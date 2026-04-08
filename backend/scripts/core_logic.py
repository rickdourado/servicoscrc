import openpyxl
from pydantic import BaseModel
from typing import List
from pathlib import Path
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXCEL_PATH = str(BASE_DIR / 'refs' / 'PlanilhaConsolidada.xlsx')
OUTPUT_PATH = str(BASE_DIR / 'refs' / 'PlanilhaGerada.xlsx')

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
    ws = wb.active
    ws.title = "Serviços Consolidados"
    
    headers = ['Origem', 'Nível 1 – Usuário', 'Nível 2 – Tipo de Serviço ou Informação']
    ws.append(headers)
    
    header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='004080', end_color='004080', fill_type='solid') # Azul premium
    header_align = Alignment(horizontal='center', vertical='center')
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                         top=Side(style='thin'), bottom=Side(style='thin'))

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    
    row_num = 2
    for item in ordered_items:
        records = [(item.source, item.name, n2) for n2 in item.level2] if item.level2 else [(item.source, item.name, "")]
        for record in records:
            ws.append(record)
            ws.cell(row=row_num, column=1).alignment = center_align
            ws.cell(row=row_num, column=2).alignment = left_align
            ws.cell(row=row_num, column=3).alignment = left_align
            for col in range(1, 4):
                ws.cell(row=row_num, column=col).border = thin_border
            row_num += 1
                
    for col_num in range(1, len(headers) + 1):
        column_target = get_column_letter(col_num)
        max_length = max(len(str(ws.cell(row=r, column=col_num).value or "")) for r in range(1, row_num))
        adjusted_width = min((max_length + 2) * 1.2, 80)
        # O mínimo da largura de "Origem" deve ser confortável:
        if col_num == 1 and adjusted_width < 12:
             adjusted_width = 12
        ws.column_dimensions[column_target].width = adjusted_width
                
    wb.save(OUTPUT_PATH)
    return {"message": "Planilha gerada com sucesso", "path": OUTPUT_PATH}

if __name__ == "__main__":
    d = extract_data()
    print(f"Extraidos {len(d)} elementos globais.")
