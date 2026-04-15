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
PROMPTS_DIR = BASE_DIR / "backend" / "prompts"
TEMP_DIR = BASE_DIR / "backend" / "temp"

# Cria pasta temporária se não existir
os.makedirs(TEMP_DIR, exist_ok=True)

# Inicializa Flask configurado para servir o frontend como estático
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

# Detecta se está em Modo Produção (para desabilitar IA pesada se necessário)
IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"

def get_prompt(filename: str, default_text: str) -> str:
    """Carrega um prompt do diretório de prompts ou retorna um padrão."""
    path = PROMPTS_DIR / filename
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Erro ao ler arquivo de prompt {filename}: {e}")
    return default_text

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/temp/<path:filename>")
def serve_temp(filename):
    """Serve arquivos temporários (PDFs anonimizados)."""
    return send_from_directory(str(TEMP_DIR), filename)

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

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
    """Analisa o texto de um contrato usando Gemini com um prompt selecionado."""
    import google.generativeai as genai
    
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Texto não fornecido"}), 400
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500
        
    prompt_type = data.get("prompt_type", "prompt_generico")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        base_prompt = get_prompt(prompt_type, 
            "Você é um especialista jurídico e de gestão de contratos do CRC. "
            "Analise o texto abaixo e extraia os pontos principais."
        )
        
        prompt = f"{base_prompt}\n\nTexto para Análise:\n{data['text']}"
        response = model.generate_content(prompt)
        
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-prompts", methods=["GET"])
def list_prompts():
    """Retorna a lista de prompts disponíveis e seus conteúdos."""
    prompts = {
        "prompt_generico": "Análise Completa (Padrão)",
        "prompt_conciso": "Análise Executiva (Resumida)",
        "prompt_ti": "Análise Técnica (TI)"
    }
    result = []
    for filename, label in prompts.items():
        content = get_prompt(filename, "Conteúdo não disponível.")
        result.append({
            "id": filename,
            "label": label,
            "content": content
        })
    return jsonify({"prompts": result})

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

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
