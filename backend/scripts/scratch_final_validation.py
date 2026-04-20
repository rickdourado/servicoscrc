import openpyxl
import os

def get_data(path):
    if not os.path.exists(path): return {}
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    data = {}
    current_service = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row[1:5]) and row[0]: # Service header
            current_service = row[0].strip()
            data[current_service] = {}
        elif current_service and row[0]:
            field = row[0].strip().replace(':', '')
            data[current_service][field] = {
                'vis': row[3],
                'obr': row[4]
            }
    return data

clf_sheet = get_data('refs/Formulários Avulsos/Formulários CLF.xlsx')
dc_sheet = get_data('refs/Formulários Avulsos/Formulários DEFESA CIVIL.xlsx')
gm_sheet = get_data('refs/Formulários Avulsos/Formulários GM-RIO.xlsx')

print("--- CLF SPREADSHEET DATA ---")
for s, fields in clf_sheet.items():
    print(f"\nService: {s}")
    for f, v in fields.items():
        print(f"  {f}: Visible={v['vis']}, Mandatory={v['obr']}")

print("\n--- DEFESA CIVIL SPREADSHEET DATA ---")
for s, fields in dc_sheet.items():
    print(f"\nService: {s}")
    for f, v in fields.items():
        print(f"  {f}: Visible={v['vis']}, Mandatory={v['obr']}")

print("\n--- GM SPREADSHEET DATA ---")
for s, fields in gm_sheet.items():
    print(f"\nService: {s}")
    for f, v in fields.items():
        print(f"  {f}: Visible={v['vis']}, Mandatory={v['obr']}")
