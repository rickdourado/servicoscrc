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

# Mapeamento de serviços originais que possuem wireframes manuais complexos
# Isso evita que o gerador automático sobrescreva esses arquivos avançados.
MANUAL_OVERRIDES = {
    "smac_resgate_de_animais_silvestres": {
        "asis": "wireframe_meio_ambiente.html",
        "tobe": "tobe_meio_ambiente.html"
    },
    "gm_rio_fiscalizacao_de_perturbacao_do_sossego": {
        "asis": "wireframe_sossego.html",
        "tobe": "tobe_sossego.html"
    },
    "gfer_remocao_de_veiculo_abandonado_em_via_publica": {
        "asis": "wireframe_veiculo_abandonado.html",
        "tobe": "tobe_irregular_veiculo.html"
    },
    "clf_fiscalizacao_de_atividades_economicas_sem_alvara": {
        "asis": "wireframe_atividades_economicas.html",
        "tobe": "tobe_atividades_economicas.html"
    },
    "clf_fiscalizacao_da_ocupacao_irregular_de_area_publica_por_estabelecimentos_comerciais_industriais_ou_servicos": {
        "asis": "wireframe_alvara_ocupacao.html",
        "tobe": "tobe_atividades_economicas.html"
    },
    "defesa_civil_vistoria_em_imovel_com_rachadura_e_infiltracao": {
        "asis": "wireframe_estrutura_imovel.html",
        "tobe": "tobe_estrutura_imovel.html"
    },
    "defesa_civil_vistoria_em_ameaca_de_desabamento_de_estrutura": {
        "asis": "wireframe_desabamento.html",
        "tobe": "tobe_desabamento.html"
    },
    "smdu_fiscalizacao_de_obras_em_imovel_privado": {
        "asis": "wireframe_fiscalizacao_obras.html",
        "tobe": "tobe_fiscalizacao_obras.html"
    }
}

def slugify(text):
    import unicodedata
    import re
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def generate_sgrc_html(service_name, organ, fields):
    fields_html = ""
    for field in fields:
        if field['asis_visible'] == 'Sim':
            req_class = 'class="req"' if field['asis_mandatory'] == 'Sim' else ''
            fields_html += f"""
      <div class="row">
        <label {req_class}>{field['name']}:</label>
        <input type="text" />
      </div>"""
    
    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Novo Chamado — {service_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, sans-serif; font-size: 13px; background: #f0f0f0; padding: 0; }}
  .tabs {{ display: flex; background: #c8c8c8; border-bottom: 2px solid #888; }}
  .tab {{ padding: 6px 18px; font-size: 13px; font-weight: bold; cursor: pointer; border: 1px solid #999; border-bottom: none; background: #d8d8d8; color: #333; margin-right: 2px; border-radius: 3px 3px 0 0; }}
  .tab.active {{ background: #ebebeb; color: #000; border-bottom: 2px solid #ebebeb; margin-bottom: -2px; }}
  .form-wrapper {{ max-width: 760px; margin: 0 auto; background: #f0f0f0; padding: 14px 14px 16px; }}
  fieldset {{ border: 1px solid #999; border-radius: 3px; padding: 10px 14px 14px; margin-bottom: 14px; background: #ebebeb; }}
  legend {{ font-size: 13px; font-weight: bold; color: #222; padding: 0 6px; }}
  .row {{ display: grid; grid-template-columns: 190px 1fr; align-items: center; gap: 5px 8px; margin-bottom: 7px; }}
  label {{ text-align: right; font-size: 13px; color: #222; line-height: 1.4; }}
  label.req {{ color: #cc0000; font-weight: bold; }}
  input[type=text], select, textarea {{ font-size: 13px; border: 1px solid #888; background: #fff; padding: 2px 5px; border-radius: 2px; width: 100%; height: 24px; font-family: Arial, sans-serif; }}
  textarea {{ height: 80px; resize: vertical; }}
  .btn-action {{ border: 1px solid #888; background: #3a6fbd; color: #fff; padding: 5px 14px; font-size: 13px; border-radius: 3px; cursor: pointer; }}
  .btn-action:hover {{ background: #2f5ea0; }}
  .chk-row {{ display: flex; align-items: center; gap: 6px; margin: 4px 0 6px 198px; font-size: 13px; color: #222; }}
  .footer {{ padding: 8px 14px; }}
</style>
</head>
<body>
  <div class="tabs">
    <div class="tab active">Pessoa</div>
    <div class="tab">Chamado</div>
  </div>
  <div class="form-wrapper">
    <fieldset>
      <legend>Classificação</legend>
      <div class="row">
        <label class="req">Categoria:</label>
        <select style="width:280px;"><option>Serviço</option></select>
      </div>
      <div class="row">
        <label class="req">Tipo/Subtipo:</label>
        <input type="text" value="{organ} >> {service_name}" readonly style="background:#e0e0e0;"/>
      </div>
    </fieldset>

    <fieldset>
      <legend>Localização</legend>
      <div class="row">
        <label class="req" style="color: #0000cc;">Endereço:</label>
        <input type="text" />
      </div>
      <div class="row">
        <label>Número / CEP:</label>
        <div style="display:flex; gap:8px;"><input type="text" style="width:100px;"/> <input type="text" placeholder="__.___-___"/></div>
      </div>
      <div class="row">
        <label>Complemento:</label>
        <input type="text" />
      </div>
      <div class="row">
        <label>Ponto de Referência:</label>
        <textarea style="height:52px;"></textarea>
      </div>
    </fieldset>

    <fieldset>
      <legend>Atributos Específicos</legend>
      {fields_html}
    </fieldset>
  </div>
  <div class="footer"><button class="btn-action">Cancelar</button></div>
</body>
</html>"""
    return template


def _get_wizard_template(service_name, fields_html):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo Chamado — {service_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #004a80; --primary-light: #e6f0f9; --accent: #f78b1f; --bg: #f8fafc; --surface: #ffffff; --text-dark: #0f172a; --text-gray: #64748b; --border: #e2e8f0; --success: #10b981; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ background-color: var(--bg); color: var(--text-dark); padding: 2rem; display: flex; justify-content: center; }}
        .wizard-container {{ background: var(--surface); border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); width: 100%; max-width: 600px; overflow: hidden; border: 1px solid var(--border); }}
        .service-title {{ background: var(--primary-light); color: var(--primary); font-size: 1.15rem; font-weight: 900; padding: 1.25rem 2rem; border-bottom: 1px solid var(--border); text-align: center; text-transform: uppercase; letter-spacing: -0.01em; }}
        .stepper-header {{ display: flex; justify-content: space-between; padding: 2rem 2rem 1.5rem; border-bottom: 1px solid var(--border); background: #fff; position: relative; }}
        .stepper-progress-bar {{ position: absolute; top: 50%; left: 3rem; right: 3rem; height: 4px; background: var(--border); z-index: 1; transform: translateY(-50%); }}
        .stepper-progress-fill {{ position: absolute; top: 0; left: 0; height: 100%; background: var(--primary); width: 0%; transition: width 0.3s ease; }}
        .step-indicator {{ position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; gap: 0.5rem; background: #fff; padding: 0 0.5rem; }}
        .step-circle {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.85rem; background: var(--surface); border: 2px solid var(--border); color: var(--text-gray); transition: all 0.2s ease; }}
        .step-indicator.completed .step-circle {{ background: var(--primary); border-color: var(--primary); color: white; }}
        .step-indicator.active .step-circle {{ border-color: var(--primary); color: var(--primary); box-shadow: 0 0 0 4px var(--primary-light); }}
        .step-label {{ font-size: 0.75rem; font-weight: 600; color: var(--text-gray); text-transform: uppercase; letter-spacing: 0.5px; }}
        .step-indicator.active .step-label {{ color: var(--primary); }}
        .step-content-section {{ padding: 2.5rem 2rem; display: none; }}
        .step-title {{ font-size: 1.5rem; font-weight: 800; color: var(--text-dark); margin-bottom: 0.5rem; }}
        .step-subtitle {{ font-size: 0.95rem; color: var(--text-gray); margin-bottom: 2rem; line-height: 1.5; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        .form-label {{ display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-dark); }}
        .form-label span.req {{ color: #ef4444; margin-left: 2px; }}
        .form-control {{ width: 100%; padding: 0.875rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 1rem; color: var(--text-dark); background: #fff; transition: all 0.2s ease; }}
        .form-control:focus {{ outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }}
        .wizard-footer {{ padding: 1.5rem 2rem; background: #f8fafc; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }}
        .btn {{ padding: 0.75rem 1.5rem; border-radius: 8px; font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; }}
        .btn-outline {{ background: transparent; border: 1px solid var(--border); color: var(--text-gray); }}
        .btn-outline:hover {{ background: var(--border); color: var(--text-dark); }}
        .btn-primary {{ background: var(--primary); color: white; box-shadow: 0 4px 6px -1px rgba(0, 74, 128, 0.2); }}
        .btn-primary:hover {{ background: #003865; transform: translateY(-1px); }}
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="service-title">{service_name}</div>
        <div class="stepper-header">
            <div class="stepper-progress-bar">
                <div class="stepper-progress-fill"></div>
            </div>
            <div class="step-indicator active"><div class="step-circle">1</div><div class="step-label">Local</div></div>
            <div class="step-indicator"><div class="step-circle">2</div><div class="step-label">Detalhes</div></div>
            <div class="step-indicator"><div class="step-circle">3</div><div class="step-label">Fotos</div></div>
            <div class="step-indicator"><div class="step-circle">4</div><div class="step-label">Contato</div></div>
        </div>

        <div class="step-content-section" id="step1" style="display: block;">
            <h2 class="step-title">Onde é o local da ocorrência?</h2>
            <p class="step-subtitle">Forneça o endereço exato ou clique no mapa para marcar a localização.</p>

            <div class="form-group">
                <label class="form-label">Pesquisar Endereço <span class="req">*</span></label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" class="form-control" placeholder="Ex: Av. Presidente Vargas, 1000">
                    <button class="btn btn-outline" style="padding: 0.875rem;">🔍</button>
                </div>
            </div>
            
            <div style="width: 100%; height: 220px; background: #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; border: 1px dashed #94a3b8; flex-direction: column;">
                <span style="font-size: 2.5rem;">📍</span>
                <span style="color: #475569; font-weight: 600; font-size: 0.95rem;">Avenida Presidente Vargas, 1000</span>
            </div>

            <div class="form-group">
                <label class="form-label">Ponto de Referência</label>
                <input type="text" class="form-control" placeholder="Perto da padaria, em frente à praça...">
            </div>
        </div>

        <div class="step-content-section" id="step2">
            <h2 class="step-title">Atributos Específicos</h2>
            <p class="step-subtitle">Forneça os detalhes específicos deste chamado conforme o modelo tradicional.</p>
            {fields_html}
        </div>

        <div class="step-content-section" id="step3">
            <h2 class="step-title">Evidências e Fotos</h2>
            <p class="step-subtitle">As fotos nos ajudam a identificar o problema mais rapidamente.</p>
            <div style="border: 2px dashed var(--primary); background: var(--primary-light); border-radius: 12px; padding: 3rem 2rem; text-align: center; cursor: pointer;">
                <div style="font-size: 2.5rem;">📸</div>
                <h3 style="color: var(--primary);">Arraste suas fotos para cá</h3>
            </div>
        </div>

        <div class="step-content-section" id="step4">
            <h2 class="step-title">Finalizar Chamado</h2>
            <p class="step-subtitle">Quase lá! Como você prefere se identificar neste chamado?</p>
            <div class="form-group">
                <label class="form-label">Nível de Sigilo <span class="req">*</span></label>
                <select class="form-control">
                    <option selected>Público - Quero acompanhar com meus dados</option>
                    <option>Sigiloso - Meus dados ficam restritos ao órgão</option>
                    <option>Anônimo - Não desejo me identificar</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Telefone / WhatsApp</label>
                <input type="text" class="form-control" placeholder="(21) 90000-0000">
            </div>
            <div class="form-group">
                <label class="form-label">E-mail para acompanhamento</label>
                <input type="email" class="form-control" placeholder="seu.email@exemplo.com">
            </div>
        </div>

        <div class="wizard-footer">
            <button class="btn btn-outline" id="btn-back" style="visibility: hidden;" onclick="prevStep()">Voltar</button>
            <button class="btn btn-primary" id="btn-next" onclick="nextStep()">Próximo Passo</button>
        </div>
    </div>

    <script>
        const steps = document.querySelectorAll('.step-content-section');
        const indicators = document.querySelectorAll('.step-indicator');
        const progressFill = document.querySelector('.stepper-progress-fill');
        const btnNext = document.getElementById('btn-next');
        const btnBack = document.getElementById('btn-back');
        let currentStep = 0;

        function updateStepper() {{
            indicators.forEach((ind, index) => {{
                ind.classList.remove('active', 'completed');
                if (index === currentStep) {{
                    ind.classList.add('active');
                }} else if (index < currentStep) {{
                    ind.classList.add('completed');
                }}
            }});
            
            const progress = (currentStep / (indicators.length - 1)) * 100;
            progressFill.style.width = progress + '%';

            steps.forEach((step, index) => {{
                step.style.display = index === currentStep ? 'block' : 'none';
            }});

            btnBack.style.visibility = currentStep === 0 ? 'hidden' : 'visible';
            
            if (currentStep === steps.length - 1) {{
                btnNext.innerHTML = 'Finalizar Chamado';
                btnNext.style.background = 'var(--success)';
            }} else {{
                btnNext.innerHTML = 'Próximo Passo 👉';
                btnNext.style.background = 'var(--primary)';
            }}
        }}

        function nextStep() {{
            if (currentStep < steps.length - 1) {{ currentStep++; updateStepper(); }}
            else {{ alert('Chamado registrado com sucesso!'); }}
        }}

        function prevStep() {{
            if (currentStep > 0) {{ currentStep--; updateStepper(); }}
        }}
        
        updateStepper();
    </script>
</body>
</html>"""

def generate_tobe_1_1_html(service_name, organ, fields):
    # TO BE 1:1: usa estética Wizard, mas renderiza os campos do AS-IS
    fields_html = ""
    for field in fields:
        if field.get('asis_visible') == 'Sim':
            req_mark = '<span class="req">*</span>' if field.get('asis_mandatory') == 'Sim' else ''
            fields_html += f"""
            <div class="form-group">
                <label class="form-label">{field['name']} {req_mark}</label>
                <input type="text" class="form-control" />
            </div>"""

    return _get_wizard_template(service_name, fields_html)

def generate_wizard_html(service_name, organ, fields):
    # TO BE Desejável: usa estética Wizard, e renderiza apenas campos validados no TO-BE
    fields_html = ""
    for field in fields:
        if field.get('tobe_visible') == 'Sim':
            req_mark = '<span class="req">*</span>' if field.get('tobe_mandatory') == 'Sim' else ''
            fields_html += f"""
            <div class="form-group">
                <label class="form-label">{field['name']} {req_mark}</label>
                <input type="text" class="form-control" />
            </div>"""

    return _get_wizard_template(service_name, fields_html)

    
def process_service(service_name, organ, fields, service_mappings):
    slug = slugify(f"{organ}_{service_name}")
    
    # Verifica se este serviço deve usar um wireframe manual (original)
    if slug in MANUAL_OVERRIDES:
        overrides = MANUAL_OVERRIDES[slug]
        sgrc_filename = overrides["asis"]
        tobe_1_1_filename = overrides["tobe"]
        # Se houver um wish manual no dicionário usamos, senão gera o padrão wish_slug
        tobe_wish_filename = overrides.get("wish", f"tobe_{slug}_wish.html")
        print(f"  -> Usando Override Manual: {slug} (ASIS: {sgrc_filename})")
        
        # Para overrides, NÃO sobrescrevemos os arquivos ASIS e TOBE 1:1 manuais
    else:
        sgrc_filename = f"wireframe_{slug}.html"
        tobe_1_1_filename = f"tobe_{slug}.html"
        tobe_wish_filename = f"tobe_{slug}_wish.html"
        
        # Gerar arquivos automáticos apenas se NÃO for override manual
        sgrc_path = SGRC_DIR / sgrc_filename
        sgrc_path.write_text(generate_sgrc_html(service_name, organ, fields), encoding="utf-8")
        
        tobe_1_1_path = TOBE_DIR / tobe_1_1_filename
        tobe_1_1_path.write_text(generate_tobe_1_1_html(service_name, organ, fields), encoding="utf-8")

    # O TO BE Desejável (Wizard) sempre geramos para manter a estética Premium MVP
    # A menos que o override tenha especificado um arquivo de "wish" manual
    if slug not in MANUAL_OVERRIDES or "wish" not in MANUAL_OVERRIDES[slug]:
        tobe_wish_path = WISH_DIR / tobe_wish_filename
        tobe_wish_path.write_text(generate_wizard_html(service_name, organ, fields), encoding="utf-8")
    
    mapping = {
        "name": f"{service_name} ({organ})",
        "asis": f"wireframes/sgrc/{sgrc_filename}",
        "tobe_1_1": f"wireframes/tobe/{tobe_1_1_filename}",
        "tobe_wish": f"wireframes/tobewish/{tobe_wish_filename}"
    }
    service_mappings.append(mapping)
    print(f"  -> Mapeado: {service_name}")

def update_ui(all_mappings):
    import re
    options_html = ""
    tobe_map = {}
    wish_map = {}
    
    # Sort alphabetically by name
    all_mappings = sorted(all_mappings, key=lambda x: x["name"])
    
    for item in all_mappings:
        options_html += f'                <option value="{item["asis"]}">{item["name"]}</option>\n'
        tobe_map[item["asis"]] = item["tobe_1_1"]
        wish_map[item["asis"]] = item["tobe_wish"]
    
    try:
        content = ANALISE_HTML.read_text(encoding="utf-8")
        
        # Regex para <select id="formSelector"> ... </select>
        pattern_select = r'(<select id="formSelector" class="form-select">).*?(</select>)'
        content = re.sub(pattern_select, f'\\1\n{options_html}            \\2', content, flags=re.DOTALL)
        
        # Mapeamentos no JS
        content = re.sub(
            r'const toBeMapping = \{.*?\};', 
            f'const toBeMapping = {json.dumps(tobe_map, indent=12)};', 
            content, 
            flags=re.DOTALL
        )
        content = re.sub(
            r'const desirableMapping = \{.*?\};', 
            f'const desirableMapping = {json.dumps(wish_map, indent=12)};', 
            content, 
            flags=re.DOTALL
        )
        
        ANALISE_HTML.write_text(content, encoding="utf-8")
        print("\nUI Atualizada com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar UI: {e}")

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

