import json, os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Nombre del archivo donde guardaremos los logs
LOG_FILE = "auditor_logs.txt"

# --- RUTA HEALTH (Vital para K8s) ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mode": "file-sync"}), 200

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    
    # Lógica de auditoría
    data['audit'].append("Log saved to file")
    data['status'] = "FINISHED_FILE"
    
    try:
        # --- ESCRITURA EN ARCHIVO ---
        # "a" = Append (Agregar al final sin borrar lo anterior)
        with open(LOG_FILE, "a") as f:
            # Escribimos el JSON como línea de texto
            f.write(json.dumps(data) + "\n")
            
        print(f"📄 Guardado en archivo local: {data['value']}", flush=True)
        
    except Exception as e:
        print(f"❌ Error escribiendo archivo: {e}", flush=True)
        return jsonify({"error": "File write failed"}), 500

    return jsonify(data)

if __name__ == "__main__":
    # Creamos el archivo al iniciar si no existe
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("--- INICIO DE REGISTRO ---\n")
            
    app.run(host='0.0.0.0', port=5000)