import os
import openpyxl
import json
from pathlib import Path

# Configurações de caminhos
BASE_DIR = Path("c:/Users/Patrick Ribeiro/Documents/dev/servicoscrc")
EXCEL_DIR = BASE_DIR / "refs/Formulários Avulsos"
SGRC_DIR = BASE_DIR / "frontend/wireframes/sgrc"
TOBE_DIR = BASE_DIR / "frontend/wireframes/tobe"
WISH_DIR = BASE_DIR / "frontend/wireframes/tobewish"
ANALISE_HTML = BASE_DIR / "frontend/analiseformulario.html"

# Garantir existência dos diretórios
for d in [SGRC_DIR, TOBE_DIR, WISH_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def slugify(text):
    import unicodedata
    import re
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def generate_sgrc_html(service_name, organ, fields):
    # Simplificado para o MVP usando o estilo clássico cinza/azul
    fields_html = ""
    for field in fields:
        if field['asis_visible'] == 'Sim':
            req_class = 'class="req"' if field['asis_mandatory'] == 'Sim' else ''
            fields_html += f"""
      <div class="row">
        <label {req_class}>{field['name']}</label>
        <input type="text" />
      </div>"""
    
    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{service_name} - AS IS</title>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; background: #f0f0f0; padding: 20px; }}
  fieldset {{ border: 1px solid #999; border-radius: 3px; padding: 15px; margin-bottom: 14px; background: #ebebeb; }}
  legend {{ font-weight: bold; padding: 0 6px; }}
  .row {{ display: grid; grid-template-columns: 190px 1fr; align-items: center; gap: 8px; margin-bottom: 7px; }}
  label {{ text-align: right; }}
  .req {{ color: #cc0000; font-weight: bold; }}
  input {{ width: 100%; height: 24px; border: 1px solid #888; }}
</style>
</head>
<body>
  <fieldset>
    <legend>SGRC - Atributos Específicos ({organ})</legend>
    {fields_html}
  </fieldset>
</body>
</html>"""
    return template

def generate_tobe_1_1_html(service_name, organ, fields):
    # Estilo Salesforce Moderno mas linear (sem wizard)
    fields_html = ""
    for field in fields:
        if field['tobe_visible'] == 'Sim':
            req_mark = '<span style="color:red">*</span>' if field['tobe_mandatory'] == 'Sim' else ''
            fields_html += f"""
        <div style="margin-bottom: 15px;">
            <label style="display:block; font-weight:bold; margin-bottom:5px;">{field['name']} {req_mark}</label>
            <input type="text" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;" />
        </div>"""

    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{service_name} - TO BE 1:1</title>
<style>
  body {{ font-family: 'Inter', sans-serif; background: #f8fafc; padding: 20px; }}
  .card {{ background: white; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; max-width: 600px; margin: auto; }}
  h2 {{ color: #004a80; margin-top: 0; }}
</style>
</head>
<body>
  <div class="card">
    <h2>{service_name} ({organ})</h2>
    <p style="color:#64748b; margin-bottom:20px;">Versão Salesforce 1:1</p>
    {fields_html}
  </div>
</body>
</html>"""
    return template

def generate_wizard_html(service_name, organ, fields):
    # Estilo Wizard 4 passos
    fields_html = ""
    for field in fields:
        if field['tobe_visible'] == 'Sim':
            req_mark = '<span class="req">*</span>' if field['tobe_mandatory'] == 'Sim' else ''
            fields_html += f"""
            <div class="form-group">
                <label class="form-label">{field['name']} {req_mark}</label>
                <input type="text" class="form-control" />
            </div>"""

    # Template baseado no tobe_wizard_base.html
    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{service_name} - Otimizado</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #004a80; --accent: #f78b1f; --bg: #f8fafc; --surface: #ffffff; --text-dark: #0f172a; --text-gray: #64748b; --border: #e2e8f0; --success: #10b981; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ background-color: var(--bg); padding: 20px; display: flex; justify-content: center; }}
        .wizard-container {{ background: var(--surface); border-radius: 12px; border: 1px solid var(--border); width: 100%; max-width: 600px; overflow: hidden; }}
        .service-title {{ background: #e6f0f9; color: var(--primary); font-weight: 800; padding: 15px; text-align: center; text-transform: uppercase; }}
        .step-content {{ padding: 30px; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-label {{ display: block; font-weight: 600; margin-bottom: 5px; font-size: 0.9rem; }}
        .form-control {{ width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; }}
        .req {{ color: red; }}
        .wizard-footer {{ background: #f8fafc; padding: 15px; border-top: 1px solid var(--border); text-align: right; }}
        .btn {{ background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="service-title">{service_name}</div>
        <div class="step-content">
            <h2 style="font-size:1.2rem; margin-bottom:15px;">Detalhes do Chamado (Passo 2)</h2>
            {fields_html}
        </div>
        <div class="wizard-footer">
            <button class="btn">Próximo Passo</button>
        </div>
    </div>
</body>
</html>"""
    return template

def process_uploaded_file(file_path):
    """
    Processa um arquivo Excel individual e retorna os mapeamentos gerados.
    """
    service_mappings = []
    organ_name = Path(file_path).stem.replace("Formulários ", "")
    
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active
        
        current_service = None
        current_fields = []
        
        for row in ws.iter_rows(min_row=3, values_only=True):
            # Título do serviço (Coluna 0 preenchida, demais vazias)
            if row[0] and not row[1] and not row[2] and not row[3] and not row[4]:
                if current_service:
                    process_service(current_service, organ_name, current_fields, service_mappings)
                current_service = row[0].strip()
                current_fields = []
            elif current_service and row[0]:
                current_fields.append({
                    'name': row[0].strip(),
                    'asis_visible': row[1],
                    'asis_mandatory': row[2],
                    'tobe_visible': row[3],
                    'tobe_mandatory': row[4]
                })
        
        if current_service:
            process_service(current_service, organ_name, current_fields, service_mappings)
            
    except Exception as e:
        print(f"Erro ao processar arquivo enviado: {e}")
        return []

    return service_mappings

def sync_all_existing():
    """
    Sincroniza todos os arquivos na pasta refs/Formulários Avulsos.
    """
    all_mappings = []
    excel_files = list(EXCEL_DIR.glob("*.xlsx"))
    print(f"Sincronizando {len(excel_files)} arquivos...")
    
    for file_path in excel_files:
        mappings = process_uploaded_file(file_path)
        all_mappings.extend(mappings)
    
    update_ui(all_mappings)
    return all_mappings

if __name__ == "__main__":
    sync_all_existing()
