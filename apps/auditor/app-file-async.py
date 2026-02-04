import os, time, redis, json, threading
from flask import Flask, jsonify

app = Flask(__name__)

# Configuración Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis-svc")
QUEUE_NAME = "cola_tareas"
LOG_FILE = "worker_logs.txt"

# Conexión a Redis
try:
    queue_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
except Exception as e:
    print(f"⚠️ Error conectando a Redis: {e}", flush=True)

# --- FUNCIÓN DE GUARDADO EN ARCHIVO ---
def save_to_file(data):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"PROCESADO: {json.dumps(data)}\n")
        print(f"📄 [FILE] Guardado ID: {data.get('id')}", flush=True)
    except Exception as e:
        print(f"❌ [FILE] Error escribiendo: {e}", flush=True)

# --- WORKER LOOP ---
def run_worker():
    print("👷 [WORKER-FILE] Iniciado. Esperando tareas...", flush=True)
    while True:
        try:
            task = queue_client.blpop(QUEUE_NAME, timeout=1)
            
            if task:
                raw_json = task[1]
                data = json.loads(raw_json)
                
                print(f"⚙️ [WORKER] Procesando: {data.get('id')}", flush=True)
                
                # Modificamos el estado
                data['audit'].append("Saved to File by Worker")
                data['status'] = "FINISHED_ASYNC_FILE"
                
                # Guardar en archivo en lugar de BD
                save_to_file(data)
                
        except Exception as e:
            print(f"⚠️ [WORKER] Error: {e}", flush=True)
            time.sleep(1)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "worker_file_running"}), 200

if __name__ == "__main__":
    # Iniciar archivo
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("--- REGISTRO DE WORKER ---\n")

    # Arrancar Worker
    worker_thread = threading.Thread(target=run_worker)
    worker_thread.daemon = True 
    worker_thread.start()
    
    app.run(host='0.0.0.0', port=5000)