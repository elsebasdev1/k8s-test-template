import os, psycopg2, time
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Usamos PG_... porque así se llaman en k8s/03-deployments.yaml
DB_HOST = os.getenv("PG_HOST", "postgres-svc")
DB_PASS = os.getenv("PG_PASS", "admin") 
DB_USER = os.getenv("PG_USER", "admin")
DB_NAME = os.getenv("PG_DB", "auditor_db")

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

# --- INICIALIZACIÓN ROBUSTA (Crea la tabla) ---
def init_db():
    retries = 5
    while retries > 0:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS auditoria (id SERIAL PRIMARY KEY, info TEXT);')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Base de Datos Conectada y Tabla Lista", flush=True)
            return
        except Exception as e:
            print(f"⏳ Esperando a Postgres... ({retries} intentos restantes): {e}", flush=True)
            retries -= 1
            time.sleep(3)
    print("❌ Error fatal: No se pudo conectar a la BD", flush=True)

# Ejecutamos esto AL INICIO para crear la tabla antes de recibir peticiones
init_db()

# --- RUTA HEALTH (Vital para que K8s no mate el pod) ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    data['audit'].append("Audit Completed")
    data['status'] = "FINISHED"
    
    # --- GUARDAR EN BD ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        log_entry = str(data)
        cur.execute('INSERT INTO auditoria (info) VALUES (%s)', (log_entry,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"💾 Guardado en Postgres: {log_entry}", flush=True)
    except Exception as e:
        print(f"❌ Error Postgres: {e}", flush=True)

    print(f"CICLO COMPLETADO: {data}", flush=True)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)