import os, psycopg2, time, redis, json, threading
from flask import Flask, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
DB_HOST = os.getenv("PG_HOST", "postgres-svc")
DB_PASS = os.getenv("PG_PASS", "123456") # O usa os.getenv("POSTGRES_PASSWORD") si usas Secrets
DB_NAME = "auditor_db"
DB_USER = "postgres"

REDIS_HOST = os.getenv("REDIS_HOST", "redis-svc")
QUEUE_NAME = "cola_tareas"

# Conexión a Redis (Consumidor)
queue_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# --- BASE DE DATOS (Misma lógica resiliente) ---
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
            print("✅ [DB] Conexión Exitosa", flush=True)
            return True
        except Exception as e:
            print(f"⏳ [DB] Esperando... {e}", flush=True)
            retries -= 1
            time.sleep(3)
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
        print(f"💾 [DB] Guardado: {data.get('value')}", flush=True)
    except Exception as e:
        print(f"❌ [DB] Error: {e}", flush=True)

# --- WORKER LOOP (Procesamiento Asíncrono) ---
def run_worker():
    print("👷 [WORKER] Iniciado. Esperando tareas...", flush=True)
    while True:
        try:
            # BLPOP: Bloquea y espera hasta que llegue algo (timeout 1s para no colgarse eternamente)
            task = queue_client.blpop(QUEUE_NAME, timeout=1)
            
            if task:
                # task es una tupla: ('cola_tareas', '{"json"...}')
                raw_json = task[1]
                data = json.loads(raw_json)
                
                print(f"⚙️ [WORKER] Procesando: {data.get('id')}", flush=True)
                
                # Simulamos trabajo y auditamos
                data['audit'].append("Processed by Async Worker")
                data['status'] = "FINISHED_ASYNC"
                
                # Guardamos en Postgres
                save_to_db(data)
                
                print(f"✅ [WORKER] Ciclo Completado: {data}", flush=True)
            
        except Exception as e:
            print(f"⚠️ [WORKER] Error en loop: {e}", flush=True)
            time.sleep(1)

# --- FLASK (Solo para Health Check de K8s) ---
@app.route('/health', methods=['GET'])
def health():
    # Kubernetes llama aquí para saber si el pod está vivo
    return jsonify({"status": "worker_running", "mode": "async"}), 200

# --- ARRANQUE ---
if __name__ == "__main__":
    # 1. Iniciar DB
    init_db_with_retry()
    
    # 2. Arrancar el Worker en un hilo paralelo (Background)
    worker_thread = threading.Thread(target=run_worker)
    worker_thread.daemon = True # Se cierra si el programa principal se cierra
    worker_thread.start()
    
    # 3. Arrancar servidor Web (Para responder al Health Check en puerto 5000)
    app.run(host='0.0.0.0', port=5000)