from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de caminhos
# Estrutura: /home/user/project/backend/scripts/app.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

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

@app.route("/api/data")
def get_data():
    import backend.scripts.core_logic as core_logic
    try:
        items = core_logic.extract_data()
        return jsonify({"items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/servicos-organizacao")
def get_servicos_organizacao():
    import backend.scripts.servicos_organizacao as servicos_org
    try:
        items = servicos_org.extract_servicos()
        # Converte modelos Pydantic para dicionários para o Flask
        return jsonify({"items": [item.model_dump() for item in items]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/save", methods=["POST"])
def save_data():
    import backend.scripts.core_logic as core_logic
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        result = core_logic.save_new_order(data["items"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host="0.0.0.0", port=8000, debug=True)
