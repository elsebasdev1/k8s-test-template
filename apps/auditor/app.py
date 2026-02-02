import os, psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de BD
DB_HOST = os.getenv("PG_HOST", "postgres-svc")
DB_PASS = os.getenv("PG_PASS", "123456")
DB_NAME = "auditor_db"
DB_USER = "postgres"

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Crear tabla al iniciar (Automático)
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS auditoria (id SERIAL PRIMARY KEY, info TEXT);')
        conn.commit()
        cur.close()
        conn.close()
        print("Tabla SQL verificada/creada", flush=True)
    except Exception as e:
        print(f"Esperando DB... {e}", flush=True)

# Intentamos iniciar la DB (puede fallar si Postgres aun no arranca, no importa)
init_db()

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    data['audit'].append("Audit Completed")
    data['status'] = "FINISHED"
    
    # --- PERSISTENCIA: Guardar en Postgres ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Guardamos el JSON como texto
        log_entry = str(data)
        cur.execute('INSERT INTO auditoria (info) VALUES (%s)', (log_entry,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"Guardado en Postgres: {log_entry}", flush=True)
    except Exception as e:
        print(f"Error Postgres: {e}", flush=True)
    # -----------------------------------------

    print(f"CICLO COMPLETADO: {data}", flush=True)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
