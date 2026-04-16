import requests
import json

BASE_URL = "http://localhost:8000/api/standardize"

def test_type(tipo, text):
    print(f"--- Testing type: {tipo} ---")
    payload = {
        "type": tipo,
        "text": text
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get("sucesso"):
            print("SUCCESS")
            print(json.dumps(result.get("resultado"), indent=2, ensure_ascii=False))
        else:
            print(f"FAILED: {result.get('error')}")
    except Exception as e:
        print(f"ERROR: {e}")
    print("\n")

sample_servico = "Buraco na rua. Solicito reparo de buraco na rua X. O prazo é de 72 horas."
sample_informacao = "Informações sobre o IPTU. O IPTU é um imposto municipal pago anualmente por proprietários de imóveis."

test_type("servico", sample_servico)
test_type("informacao", sample_informacao)
