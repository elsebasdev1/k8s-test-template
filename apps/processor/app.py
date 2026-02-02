import os, requests, redis
from flask import Flask, request, jsonify

app = Flask(__name__)
NEXT_HOP = os.getenv("NEXT_SERVICE_URL", "http://auditor-svc:5000")
# Conexión a la BD Redis (nombre del servicio en K8s)
DB_HOST = os.getenv("REDIS_HOST", "redis-svc")

# Conectamos a Redis
cache = redis.Redis(host=DB_HOST, port=6379, decode_responses=True)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    val = data.get('value', 0)
    
    # Lógica de Negocio
    if val % 2 == 0:
        data['value'] = val * 2
        data['audit'].append("Multiplied by 2 (Even)")
    else:
        data['value'] = val + 1
        data['audit'].append("Added 1 (Odd)")

    # --- PERSISTENCIA: Guardar en Redis ---
    try:
        cache.set("ultimo_valor", data['value'])
        print(f"Guardado en Redis: {data['value']}", flush=True)
    except Exception as e:
        print(f"Error Redis: {e}", flush=True)
    # --------------------------------------

    # Pasar al siguiente
    response = requests.post(f"{NEXT_HOP}/audit", json=data)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
