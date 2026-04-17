from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de caminhos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
SERVICOS_JSON = BASE_DIR / "backend" / "data" / "servicos.json"
PROMPTS_DIR   = BASE_DIR / "backend" / "prompts"
CONTRACTS_DIR = PROMPTS_DIR  # contratos .md ficam em prompts/<contrato_id>/
TEMP_DIR      = BASE_DIR / "backend" / "temp"

# Cria pasta temporária se não existir
os.makedirs(TEMP_DIR, exist_ok=True)

# Inicializa Flask configurado para servir o frontend como estático
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

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
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY nao configurada"}), 500

    prompt_type  = data.get("prompt_type", "prompt_generico")
    contract_id  = data.get("contract_id", "czrm")   # novo campo

    try:
        client = genai.Client(api_key=api_key)

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

        response = client.models.generate_content(model=gemini_model, contents=prompt)
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
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    
    try:
        client = genai.Client(api_key=api_key)
        
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
            prompt += "- `o_que_e`: string (Markdown)\n"
            prompt += "- `como_funciona`: string (Markdown)\n"
            prompt += "- `publico_alvo`: string (Markdown)\n"
            prompt += "- `informacoes_importantes`: string (Markdown)\n\n"
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

        response = client.models.generate_content(model=gemini_model, contents=prompt)
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
            campos = ['o_que_e', 'como_funciona', 'publico_alvo', 'informacoes_importantes']
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

@app.route("/api/save", methods=["POST"])
def save_data():
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        # Salva a hierarquia no JSON
        with open(SERVICOS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return jsonify({"message": "Dados salvos com sucesso!"})
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
