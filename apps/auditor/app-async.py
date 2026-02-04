import os, psycopg2, time, redis, json, threading
from flask import Flask, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN (Alineada con tu éxito actual) ---
# Usamos PG_... y admin/admin para coincidir con k8s/03-deployments.yaml
DB_HOST = os.getenv("PG_HOST", "postgres-svc")
DB_PASS = os.getenv("PG_PASS", "admin") 
DB_USER = os.getenv("PG_USER", "admin")
DB_NAME = os.getenv("PG_DB", "auditor_db")

# Configuración Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis-svc")
QUEUE_NAME = "cola_tareas"

# Conexión a Redis (Consumidor)
try:
    queue_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
except Exception as e:
    print(f"⚠️ Error conectando a Redis: {e}", flush=True)

# --- BASE DE DATOS (Lógica Robusta) ---
def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

def init_db_with_retry():
    retries = 5
    while retries > 0:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS auditoria (id SERIAL PRIMARY KEY, info TEXT);')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ [DB Async] Conexión Exitosa y Tabla Verificada", flush=True)
            return True
        except Exception as e:
            print(f"⏳ [DB Async] Esperando... {e}", flush=True)
            retries -= 1
            time.sleep(3)
    print("❌ [DB Async] Error fatal: No se pudo conectar", flush=True)
    return False

def save_to_db(data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        log_entry = str(data)
        cur.execute('INSERT INTO auditoria (info) VALUES (%s)', (log_entry,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"💾 [DB Async] Guardado: {data.get('value')}", flush=True)
    except Exception as e:
        print(f"❌ [DB Async] Error: {e}", flush=True)

# --- WORKER LOOP (Procesamiento en Segundo Plano) ---
def run_worker():
    print("👷 [WORKER] Iniciado. Esperando tareas en Redis...", flush=True)
    while True:
        try:
            # BLPOP: Espera bloqueante (eficiente)
            task = queue_client.blpop(QUEUE_NAME, timeout=1)
            
            if task:
                # task es una tupla: ('cola_tareas', '{"json"...}')
                raw_json = task[1]
                data = json.loads(raw_json)
                
                print(f"⚙️ [WORKER] Procesando ID: {data.get('id')}", flush=True)
                
                # Simulamos lógica de auditoría
                data['audit'].append("Processed by Async Worker")
                data['status'] = "FINISHED_ASYNC"
                
                # Guardamos en Postgres
                save_to_db(data)
                
                print(f"✅ [WORKER] Ciclo Completado.", flush=True)
            
        except Exception as e:
            print(f"⚠️ [WORKER] Error en loop: {e}", flush=True)
            time.sleep(1)

# --- FLASK (Solo para Health Check) ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "worker_running", "mode": "async"}), 200

# --- ARRANQUE ---
if __name__ == "__main__":
    # 1. Iniciar DB (Esperar a que esté lista)
    init_db_with_retry()
    
    # 2. Arrancar el Worker en un hilo paralelo
    worker_thread = threading.Thread(target=run_worker)
    worker_thread.daemon = True 
    worker_thread.start()
    
    # 3. Arrancar servidor Web (Para K8s)
    app.run(host='0.0.0.0', port=5000)