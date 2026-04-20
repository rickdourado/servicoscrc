import openpyxl
import os

files = [
    ('CLF', 'refs/Formulários Avulsos/Formulários CLF.xlsx'),
    ('DC', 'refs/Formulários Avulsos/Formulários DEFESA CIVIL.xlsx'),
    ('GM', 'refs/Formulários Avulsos/Formulários GM-RIO.xlsx')
]

def format_status(vis, obr):
    if vis == 'No' or vis == 'Não': return '(REMOVER / OCULTAR)'
    return '(OBRIGATÓRIO)' if (obr == 'Sim') else '(OPCIONAL)'

def get_mail_content(path):
    if not os.path.exists(path): return ""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    output = ""
    current_service = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row[1:5]) and row[0]:
            current_service = row[0].strip()
            output += f"\n### {current_service}\n"
        elif current_service and row[0]:
            field = row[0].strip()
            as_is_vis = row[1]
            as_is_obr = row[2]
            to_be_vis = row[3]
            to_be_obr = row[4]
            
            # Label
            label = format_status(to_be_vis, to_be_obr)
            
            # Change check
            changed = (as_is_vis != to_be_vis) or (as_is_obr != to_be_obr)
            change_note = "" if changed else " - sem alterações"
            
            output += f"* {field} {label}{change_note}\n"
    return output

for organ, path in files:
    print(f"\n===== {organ} =====")
    print(get_mail_content(path))
