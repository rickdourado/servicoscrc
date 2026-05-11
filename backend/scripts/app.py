from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Activity
from datetime import datetime
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configuração de caminhos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
SERVICOS_JSON = BASE_DIR / "backend" / "data" / "servicos.json"
VERSIONS_DIR  = BASE_DIR / "backend" / "data" / "versions"
PROMPTS_DIR   = BASE_DIR / "backend" / "prompts"
CONTRACTS_DIR = PROMPTS_DIR  # contratos .md ficam em prompts/<contrato_id>/
TEMP_DIR      = BASE_DIR / "backend" / "temp"
DB_PATH       = BASE_DIR / "backend" / "data" / "app.db"
LOGS_DIR      = BASE_DIR / "backend" / "data" / "logs"

print(f"DATABASE_PATH: {DB_PATH.absolute()}")

# Carrega variáveis de ambiente do arquivo .env na raiz
load_dotenv(BASE_DIR / ".env")

# Cria pastas necessárias se não existirem
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(VERSIONS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Inicializa Flask configurado para servir o frontend como estático
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["REMEMBER_COOKIE_DURATION"] = 30 * 24 * 60 * 60 # 30 dias em segundos
CORS(app, supports_credentials=True)

# Inicializa banco de dados e login
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_user_action(action):
    """Loga ações do usuário em arquivos separados."""
    if current_user.is_authenticated:
        user_log_file = LOGS_DIR / f"{current_user.username}.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(user_log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {action}\n")
        print(f"AUDITORIA: {current_user.username} -> {action}")

# Detecta se está em Modo Produção (para desabilitar IA pesada se necessário)
IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"

def get_prompt(filename: str, default_text: str, contract_id: str | None = None) -> str:
    """
    Carrega um prompt do diretório de prompts.
    Se `contract_id` for fornecido, busca em prompts/<contract_id>/.
    Caso contrário, busca na raiz de prompts/.
    """
    if not filename.endswith(".md"):
        filename = f"{filename}.md"

    if contract_id:
        path = PROMPTS_DIR / contract_id / filename
    else:
        path = PROMPTS_DIR / filename

    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Aviso: Erro ao ler prompt {filename}: {e}")
    else:
        print(f"Aviso: Prompt nao encontrado: {path}")

    return default_text


def get_contract_context(contract_id: str) -> str:
    """
    Carrega o arquivo .md do contrato anonimizado como contexto para a IA.
    Busca o primeiro .md que contenha 'ANONIMIZADO' em prompts/<contract_id>/.
    """
    folder = PROMPTS_DIR / contract_id
    if not folder.is_dir():
        return ""

    candidates = sorted(folder.glob("*ANONIMIZADO*.md"))
    if not candidates:
        # Fallback: qualquer .md que não seja prompt de instrução
        candidates = [f for f in folder.glob("*.md")
                      if not f.stem.startswith("prompt_")]

    if not candidates:
        return ""

    try:
        content = candidates[0].read_text(encoding="utf-8")
        # Limita a 60.000 chars para não estourar a janela de contexto
        if len(content) > 60_000:
            content = content[:60_000] + "\n\n[... conteúdo truncado por limite de contexto ...]"
        return content
    except Exception as e:
        print(f"Aviso: Erro ao ler contrato base {candidates[0]}: {e}")
        return ""


def list_available_contracts() -> list[dict]:
    """
    Retorna os contratos disponíveis: subpastas de PROMPTS_DIR que contenham
    ao menos um arquivo *ANONIMIZADO*.md.
    """
    contracts = []
    if not PROMPTS_DIR.is_dir():
        return contracts

    # Mapeamento de IDs para nomes amigáveis (adicionar novos contratos aqui)
    contract_labels = {
        "czrm": "Contrato CZRM — Empresa Municipal de Informática (IPLANRIO)",
    }

    for subfolder in sorted(PROMPTS_DIR.iterdir()):
        if not subfolder.is_dir():
            continue
        has_contract = any(subfolder.glob("*ANONIMIZADO*.md"))
        if not has_contract:
            continue
        cid = subfolder.name
        contracts.append({
            "id": cid,
            "label": contract_labels.get(cid, cid.upper()),
        })

    return contracts

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/temp/<path:filename>")
def serve_temp(filename):
    """Serve arquivos temporários (PDFs anonimizados)."""
    return send_from_directory(str(TEMP_DIR), filename)


@app.route("/api/servicos-organizacao")
def get_servicos_organizacao():
    import backend.scripts.servicos_organizacao as servicos_org
    try:
        items = servicos_org.extract_servicos()
        return jsonify({"items": [item.model_dump() for item in items]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- NOVAS ROTAS DE CONTRATO (Migradas do branch dev) ---

@app.route("/api/anonymize", methods=["POST"])
def anonymize_contract():
    """Recebe um PDF, anonimiza e retorna o texto extraído e a URL do PDF mascarado."""
    import backend.scripts.anonymizer as anonymizer
    
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
    file = request.files["file"]
    file_bytes = file.read()
    is_pdf = file.filename.lower().endswith(".pdf")
    
    try:
        if is_pdf:
            filename, masked_text = anonymizer.redact_pdf_visually(file_bytes)
            return jsonify({
                "masked_text": masked_text,
                "preview_url": f"/temp/{filename}"
            })
        else:
            # Caso não seja PDF, apenas extrai e mascara o texto
            raw_text = file_bytes.decode("utf-8", errors="ignore")
            masked_text = anonymizer.process_and_save(raw_text, file.filename)
            return jsonify({
                "masked_text": masked_text,
                "preview_url": None
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    """Analisa o texto de um relatório usando Gemini com prompt + contrato base como contexto."""
    from google import genai

    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Texto nao fornecido"}), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY nao configurada"}), 500

    prompt_type  = data.get("prompt_type", "prompt_generico")
    contract_id  = data.get("contract_id", "czrm")   # novo campo

    try:
        from ai_utils import call_gemini
        
        # Carrega instrução do prompt (busca na pasta do contrato)
        base_prompt = get_prompt(
            prompt_type,
            "Voce e um especialista juridico e de gestao de contratos do CRC. "
            "Analise o texto abaixo e extraia os pontos principais.",
            contract_id=contract_id,
        )

        # Injeta o contrato anonimizado como contexto de referência
        contract_context = get_contract_context(contract_id)
        if contract_context:
            context_block = (
                "\n\n---\n"
                "## CONTRATO BASE DE REFERENCIA\n"
                "O documento abaixo é o contrato anonimizado que deve ser usado "
                "como referência para interpretar o relatório mensalsubmetido:\n\n"
                + contract_context
                + "\n\n---\n"
            )
        else:
            context_block = ""

        # Monta o prompt final
        prompt = (
            base_prompt
            + context_block
            + "\n\n## RELATORIO MENSAL PARA ANALISE:\n"
            + data["text"]
        )

        response = call_gemini(prompt, model=gemini_model)
        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/contracts", methods=["GET"])
def api_list_contracts():
    """Retorna os contratos base disponíveis para análise."""
    return jsonify({"contracts": list_available_contracts()})


@app.route("/api/get-prompts", methods=["GET"])
def list_prompts():
    """Retorna a lista de prompts disponíveis para um contrato."""
    contract_id = request.args.get("contract_id", "czrm")

    available_prompts = {
        "prompt_generico": "Analise Completa (Padrao)",
        "prompt_conciso":  "Analise Executiva (Resumida)",
        "prompt_ti":       "Analise Tecnica (TI)",
    }
    result = []
    for prompt_id, label in available_prompts.items():
        content = get_prompt(prompt_id, "Conteudo nao disponivel.", contract_id=contract_id)
        result.append({"id": prompt_id, "label": label, "content": content})

    return jsonify({"prompts": result})

@app.route("/api/standardize", methods=["POST"])
def standardize_service():
    """Padroniza descrições de serviços ou resume informações (Migrado do ServicosClean)."""
    from google import genai
    import re
    
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Texto não fornecido"}), 400
        
    tipo = data.get("type", "servico") # 'servico' ou 'informacao'
    api_key = os.environ.get("GEMINI_API_KEY")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    try:
        from ai_utils import call_gemini
        
        # Carrega regras do prompt original (servico.md ou informacao.md)
        # get_prompt já adiciona .md
        regras = get_prompt(tipo, "Aja como um especialista em redação oficial e simplificação de serviços públicos.")
        
        # Constrói o prompt final com estrutura JSON explícita conforme ServicosClean/app.py
        if tipo == 'informacao':
            prompt = f"{regras}\n\n"
            prompt += "---\n\n## Conteúdo a Processar\n\n"
            prompt += f"**Texto de entrada:**\n\n{data['text']}\n\n"
            prompt += "---\n\n## Instruções de Saída\n\n"
            prompt += "Retorne APENAS um JSON com os seguintes campos (use os nomes exatos das chaves):\n"
            prompt += "- `titulo_informacao`: string\n"
            prompt += "- `descricao_resumida`: string\n"
            prompt += "- `descricao_completa`: string (Markdown estruturado)\n"
            prompt += "- `custo`: string\n"
            prompt += "- `legislacao_relacionada`: string\n"
            prompt += "- `canais_presenciais`: string\n"
            prompt += "- `canais_digitais`: string\n"
            prompt += "- `instrucoes_solicitante`: string\n"
            prompt += "- `documentos_necessarios`: string\n"
            prompt += "- `tempo_atendimento`: string\n\n"
            prompt += "Se uma informação não estiver disponível, retorne string vazia."
        else: # servico
            prompt = f"{regras}\n\n"
            prompt += "---\n\n## PROMPT PRINCIPAL - PADRONIZAÇÃO DE SERVIÇOS\n\n"
            prompt += "Siga a estrutura definida nas regras acima para padronizar o serviço.\n\n"
            prompt += "---\n\n## Serviço a Processar\n\n"
            prompt += f"**Texto de entrada (texto livre):**\n\n{data['text']}\n\n"
            prompt += "---\n\n## Instruções\n\n"
            prompt += "Analise o texto livre acima e extraia/processe as informações para criar uma descrição completa.\n"
            prompt += "Siga TODAS as regras especificadas.\n\n"
            prompt += "Retorne APENAS um JSON com os seguintes campos:\n"
            prompt += "- `descricao_resumida`\n"
            prompt += "- `descricao_completa` (Texto completo em Markdown conforme regras do servico.md)\n"
            prompt += "- `servico_nao_cobre`\n"
            prompt += "- `tempo_atendimento`\n"
            prompt += "- `custo`\n"
            prompt += "- `resultado_solicitacao`\n"
            prompt += "- `documentos_necessarios`\n"
            prompt += "- `instrucoes_solicitante`\n"
            prompt += "- `canais_digitais`\n"
            prompt += "- `canais_presenciais`\n"
            prompt += "- `legislacao_relacionada`"

        response = call_gemini(prompt, model=gemini_model)
        text_response = response.text
        
        # Extrai JSON do bloco de código
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            # Fallback: tenta procurar qualquer par de chaves
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                raise Exception("Não foi possível extrair um JSON válido da resposta da IA.")
        
        # Normaliza campos dependendo do tipo (Garante que todas as chaves existam)
        if tipo == 'informacao':
            campos = [
                'titulo_informacao', 'descricao_resumida', 'descricao_completa', 
                'custo', 'legislacao_relacionada', 'canais_presenciais',
                'canais_digitais', 'instrucoes_solicitante',
                'documentos_necessarios', 'tempo_atendimento'
            ]
        else:
            campos = [
                'descricao_resumida', 'descricao_completa', 
                'servico_nao_cobre', 'tempo_atendimento', 'custo', 'resultado_solicitacao',
                'documentos_necessarios', 'instrucoes_solicitante',
                'canais_digitais', 'canais_presenciais', 'legislacao_relacionada'
            ]
            
        for c in campos:
            if c not in result:
                result[c] = ''
                
        return jsonify({"sucesso": True, "resultado": result})
        
    except Exception as e:
        return jsonify({"error": str(e), "sucesso": False}), 500

@app.route("/api/upload-form", methods=["POST"])
def upload_form():
    """Recebe uma planilha Excel e gera automaticamente os wireframes."""
    import backend.scripts.process_excel_forms as form_gen
    
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
    file = request.files["file"]
    if not file.filename.endswith(".xlsx"):
        return jsonify({"error": "Formato inválido. Envie um arquivo .xlsx"}), 400
        
    try:
        # Salva o arquivo na pasta refs/Formulários Avulsos para backup e processamento
        save_path = BASE_DIR / "refs" / "Formulários Avulsos" / file.filename
        file.save(str(save_path))
        
        # Processa e gera os HTMLs
        # Nota: sync_all_existing atualiza a UI e retorna todos os mapeamentos
        mappings = form_gen.sync_all_existing()
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Processado com sucesso! {len(mappings)} serviços atualizados.",
            "mappings": mappings
        })
    except Exception as e:
        return jsonify({"error": str(e), "sucesso": False}), 500

@app.route("/api/save", methods=["POST"])
def save_data():
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        # Salva a hierarquia no JSON principal (live)
        with open(SERVICOS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        # Também gera uma versão AAAAMMDD_HHMMSS.json
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_filename = f"{timestamp}.json"
        version_path = VERSIONS_DIR / version_filename
        
        with open(version_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return jsonify({
            "message": "Dados salvos com sucesso!",
            "version": version_filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/list-versions", methods=["GET"])
def list_versions():
    """Lista todos os arquivos JSON de versões disponíveis."""
    try:
        versions = []
        for file in sorted(VERSIONS_DIR.glob("*.json"), reverse=True):
            versions.append(file.name)
        return jsonify({"versions": versions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/load-version/<filename>", methods=["GET"])
def load_version(filename):
    """Carrega o conteúdo de uma versão específica."""
    try:
        # Segurança: impede Path Traversal
        filename = os.path.basename(filename)
        path = VERSIONS_DIR / filename
        if not path.exists():
            return jsonify({"error": "Versão não encontrada"}), 404
            
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/restore-original", methods=["POST"])
def restore_original():
    import backend.scripts.servicos_organizacao as servicos_org
    try:
        success = servicos_org.restore_original_data()
        if success:
            items = servicos_org.extract_servicos()
            return jsonify({"items": [item.model_dump() for item in items]})
        else:
            return jsonify({"error": "Backup original não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/generate-description", methods=["POST"])
def ai_generate_description():
    import backend.scripts.ai_service as ai_service
    try:
        data = request.get_json()
        item_type = data.get("type")
        item_name = data.get("name")
        parent_name = data.get("parent_name", "")
        
        if not item_type or not item_name:
            return jsonify({"error": "Tipo e nome são obrigatórios"}), 400
            
        result = ai_service.generate_description(item_type, item_name, parent_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/env")
def api_env():
    """Expoe o modo de execucao atual (producao ou local) ao frontend."""
    return jsonify({"is_production": IS_PRODUCTION})


# =======================
# Autenticação e Usuários
# =======================

@app.route("/api/login", methods=["POST"])
def login():
    """Autentica usuário e inicia sessão."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    remember = data.get("remember", False)

    user = User.query.filter_by(username=username, is_active=True).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401

    login_user(user, remember=remember)
    log_user_action("Login realizado")
    return jsonify({"user": {"id": user.id, "username": user.username, "name": user.name, "role": user.role}})

@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """Encerra sessão do usuário."""
    log_user_action("Logout realizado")
    logout_user()
    return jsonify({"message": "Sessão encerrada"})

@app.route("/api/me")
@login_required
def me():
    """Retorna dados do usuário autenticado."""
    return jsonify({"user": {"id": current_user.id, "username": current_user.username, "name": current_user.name, "role": current_user.role}})

# =======================
# Atividades / Tarefas
# =======================

@app.route("/api/activities", methods=["GET"])
def list_activities():
    """Lista atividades. Publicamente mostra todas. Se logado e não-admin, filtra? 
    O usuário solicitou que qualquer um visualize tudo."""
    # Para visualização pública total, buscamos todas sem filtro de owner
    activities = Activity.query.all()

    return jsonify([{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "priority": a.priority,
        "status": a.status,
        "owner_id": a.owner_id,
        "owner_name": a.owner.name if a.owner else "Sem responsável",
        "parent_id": a.parent_id,
        "created_at": a.created_at.isoformat()
    } for a in activities])

@app.route("/api/activities", methods=["POST"])
@login_required
def create_activity():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")
    priority = data.get("priority", "medium")
    parent_id = data.get("parent_id")
    
    if not title:
        return jsonify({"error": "Título é obrigatório"}), 400

    activity = Activity(
        title=title, 
        description=description, 
        priority=priority,
        parent_id=parent_id,
        owner_id=current_user.id
    )
    db.session.add(activity)
    db.session.commit()
    
    log_user_action(f"Criou atividade: {title} (ID: {activity.id})")
    return jsonify({"message": "Atividade criada", "id": activity.id})

@app.route("/api/activities/<int:activity_id>", methods=["PUT"])
@login_required
def update_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.owner_id != current_user.id and current_user.role != 'admin':
        return jsonify({"error": "Sem permissão"}), 403
        
    data = request.get_json()
    activity.title = data.get("title", activity.title)
    activity.description = data.get("description", activity.description)
    activity.status = data.get("status", activity.status)
    activity.priority = data.get("priority", activity.priority)
    
    db.session.commit()
    log_user_action(f"Atualizou atividade: {activity.title} (ID: {activity_id})")
    return jsonify({"message": "Atividade atualizada"})

@app.route("/api/activities/<int:activity_id>", methods=["DELETE"])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.owner_id != current_user.id and current_user.role != 'admin':
        return jsonify({"error": "Sem permissão"}), 403
        
    title = activity.title
    db.session.delete(activity)
    db.session.commit()
    
    log_user_action(f"Removeu atividade: {title} (ID: {activity_id})")
    return jsonify({"message": "Atividade removida"})

# =======================
# Inicialização do Banco
# =======================

@app.before_request
def ensure_db():
    if not hasattr(app, '_db_initialized'):
        with app.app_context():
            db.create_all()
            # Admin
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', name='Administrador', role='admin')
                admin.set_password(os.environ.get("ADMIN_PASSWORD", "admin"))
                db.session.add(admin)
            
            # Test Users and Jira Users
            users_data = [
                ('user1', 'Analista 1', 'user123'),
                ('user2', 'Analista 2', 'user123'),
                ('bruna.barros', 'Bruna Ferreira de Castro Barros', 'crc123'),
                ('cynthia.bimbi', 'Cynthia Bimbi', 'crc123'),
                ('egon.bemfica', 'Egon Magno Azevedo da Silva Bemfica', 'crc123'),
                ('felipe.andrade', 'Felipe Costa de Andrade', 'crc123'),
                ('gabriela.gervason', 'Gabriela Gervason', 'crc123'),
                ('jose.silva', 'José Maurício Elias Da Silva', 'crc123'),
                ('juliana.oggione', 'Juliana Oggione', 'crc123'),
                ('patrick.ribeiro', 'Patrick Dourado Ribeiro', 'crc123'),
                ('pedro.meireles', 'Pedro Meireles', 'crc123'),
                ('rute.evangelista', 'Rute Gawantka Evangelista', 'crc123'),
                ('samir.costa', 'Samir de Menezes Costa', 'crc123'),
                ('gustavo.costa', 'Gustavo Costa', 'crc123'),
            ]
            for uname, name, pwd in users_data:
                user = User.query.filter_by(username=uname).first()
                if not user:
                    user = User(username=uname, name=name, role='user')
                    user.set_password(pwd)
                    db.session.add(user)
                    db.session.flush() # Get ID
                    
                    # Sample Tasks (only for user1/user2)
                    if uname == 'user1':
                        t1 = Activity(title="Revisar Documentação 1746", description="Verificar descrições de serviços", priority="high", owner_id=user.id)
                        db.session.add(t1)
                        db.session.flush()
                        db.session.add(Activity(title="Validar URLs", description="Testar links de acesso", parent_id=t1.id, owner_id=user.id))
                    elif uname == 'user2':
                        db.session.add(Activity(title="Mapear Fluxos", description="Documentar processos de triagem", priority="medium", owner_id=user.id))
            
            db.session.commit()
        app._db_initialized = True


@app.route("/api/prefrio-stats/summary", methods=["GET"])
def prefrio_summary():
    """Retorna resumo geral dos dados PrefRio."""
    import backend.scripts.prefrio_stats as prefrio
    try:
        summary = prefrio.get_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/prefrio-stats/orgaos", methods=["GET"])
def prefrio_orgaos():
    """Retorna estatísticas de serviços por órgão."""
    import backend.scripts.prefrio_stats as prefrio
    try:
        stats = prefrio.get_orgaos_stats()
        return jsonify({"orgaos": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/prefrio-stats/servicos", methods=["GET"])
def prefrio_servicos():
    """Busca serviços com filtros opcionais (órgão e relevância)."""
    import backend.scripts.prefrio_stats as prefrio
    try:
        orgao = request.args.get("orgao")
        relevancia = request.args.get("relevancia")
        servicos = prefrio.search_services(orgao, relevancia)
        return jsonify({"servicos": servicos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/prefrio-stats/relevancia-options", methods=["GET"])
def prefrio_relevancia_options():
    """Retorna opções de análise de relevância."""
    import backend.scripts.prefrio_stats as prefrio
    try:
        options = prefrio.get_relevancia_options()
        return jsonify({"options": options})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
