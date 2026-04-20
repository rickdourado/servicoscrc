import openpyxl
import os

def get_full_data(path):
    if not os.path.exists(path):
        return {}
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    data = {}
    current_service = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]: continue
        # Check if it's a service header (no values in AS IS/TO BE area but has text in col 0)
        # Or based on some other logic. In previous files, headers had everything else as None.
        if not any(row[1:5]) and row[0]:
            current_service = row[0].strip()
            data[current_service] = []
        elif current_service and row[0]:
            data[current_service].append({
                'field': row[0].strip(),
                'as_is_vis': row[1],
                'as_is_obr': row[2],
                'to_be_vis': row[3],
                'to_be_obr': row[4]
            })
    return data

files = [
    ('GFER', 'refs/Formulários Avulsos/Formulários GFER.xlsx'),
    ('SMAC', 'refs/Formulários Avulsos/Formulários SMAC.xlsx'),
    ('SMDU', 'refs/Formulários Avulsos/Formulários SMDU.xlsx')
]

for organ, path in files:
    print(f"\n=== {organ} ===")
    d = get_full_data(path)
    for s, fields in d.items():
        print(f"\nService: {s}")
        for f in fields:
            print(f"  {f}")
