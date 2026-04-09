import pytest
from backend.scripts.anonymizer import mask_sensitive_data

def test_masking():
    text = """
    Contratante: Prefeitura de SGRC
    CONTRATADA: SUPRIMENTOS GERAIS LTDA
    Processo Administrativo nº 1234/2026
    CNPJ: 12.345.678/0001-99
    CPF: 123.456.789-00
    O valor do Contrato 999/2026 é de R$ 50.000,00.
    """
    masked = mask_sensitive_data(text)
    print(masked)

test_masking()
