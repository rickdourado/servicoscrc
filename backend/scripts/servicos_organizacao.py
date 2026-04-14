import openpyxl
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SERVICOS_XLSX = str(BASE_DIR / 'refs' / 'planilhas' / 'ServicosOrganizacao.xlsx')
SHEET_INDEX = 1  # "Nova Árvore - Salesforce"


class ServicoN2(BaseModel):
    name: str


class ServicoN1(BaseModel):
    id: str
    name: str
    children: List[ServicoN2]


def extract_servicos() -> List[ServicoN1]:
    wb = openpyxl.load_workbook(SERVICOS_XLSX, data_only=True)
    ws = wb.worksheets[SHEET_INDEX]

    result: List[ServicoN1] = []
    current_n1: Optional[ServicoN1] = None
    idx = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        n1_val = row[0] if row[0] else None
        n2_val = row[1] if len(row) > 1 and row[1] else None

        if n1_val:
            if current_n1 is not None:
                result.append(current_n1)
            current_n1 = ServicoN1(
                id=f"n1_{idx}",
                name=str(n1_val).strip(),
                children=[]
            )
            idx += 1

        if current_n1 and n2_val:
            n2_str = str(n2_val).strip()
            # Ignora placeholder genérico [subcategorias]
            if n2_str.lower() not in ("[subcategorias]", ""):
                current_n1.children.append(ServicoN2(name=n2_str))

    if current_n1 is not None:
        result.append(current_n1)

    return result
