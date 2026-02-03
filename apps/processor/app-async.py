import os, redis, json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración Redis (Cola de Tareas)
# Usamos el mismo host que ya tienes configurado
REDIS_HOST = os.getenv("REDIS_HOST", "redis-svc")
QUEUE_NAME = "cola_tareas"

# Conexión a Redis
try:
    cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
except Exception as e:
    print(f"⚠️ Error conectando a Redis: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    val = data.get('value', 0)
    
    # 1. Lógica de Negocio (Igual que siempre)
    if val % 2 == 0:
        data['value'] = val * 2
        data['audit'].append("Multiplied by 2 (Even)")
    else:
        data['value'] = val + 1
        data['audit'].append("Added 1 (Odd)")

    # 2. MODO ASÍNCRONO: Encolar en Redis (Productor)
    try:
        # rpush agrega el mensaje al final de la lista 'cola_tareas'
        cache.rpush(QUEUE_NAME, json.dumps(data))
        print(f"✅ Tarea encolada en '{QUEUE_NAME}': {data['value']}", flush=True)
        
        # 3. Respuesta INMEDIATA (No esperamos al Auditor)
        return jsonify({
            "status": "QUEUED", 
            "message": "Tarea recibida y encolada para procesamiento",
            "data": data
        })
    except Exception as e:
        print(f"❌ Error encolando tarea: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)