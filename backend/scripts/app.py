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

# Inicializa Flask configurado para servir o frontend como estático
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

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
