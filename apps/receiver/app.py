import os, requests, json
from flask import Flask, request, jsonify

app = Flask(__name__)

# K8s inyectará esta URL por variable de entorno (ConfigMap)
# Si no existe, usa el valor por defecto
NEXT_HOP = os.getenv("NEXT_SERVICE_URL", "http://processor-svc:5000")

# --- 🟢 BLOQUE CORS OBLIGATORIO ---
# Esto permite que el Frontend (HTML/JS) se comunique con este Backend
# sin que el navegador bloquee la petición por seguridad.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
# ----------------------------------

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    print(f"Recibido en Nodo A: {data}", flush=True) # flush=True asegura que salga en los logs de K8s

    # Enviar al siguiente nodo (Service Discovery de K8s)
    try:
        # Hacemos la petición al Processor (Nodo B)
        response = requests.post(f"{NEXT_HOP}/process", json=data)
        
        # Devolvemos la respuesta final al Frontend
        return jsonify(response.json())
    except Exception as e:
        print(f"Error conectando con {NEXT_HOP}: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)