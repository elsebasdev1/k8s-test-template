import os, psycopg2, time, requests, json
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Apuntamos al INICIO del anillo (Receiver)
# Usamos el nombre del servicio interno de K8s
NEXT_HOP = os.getenv("NEXT_SERVICE_URL", "http://receiver-svc:5000")

# Credenciales de BD (Las mismas que ya funcionan)
DB_HOST = os.getenv("PG_HOST", "postgres-svc")
DB_PASS = os.getenv("PG_PASS", "admin") 
DB_USER = os.getenv("PG_USER", "admin")
DB_NAME = os.getenv("PG_DB", "auditor_db")

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

# --- INICIALIZACIÓN BD ---
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
            print("✅ [RING] BD Conectada", flush=True)
            return
        except Exception as e:
            print(f"⏳ [RING] Esperando BD... {e}", flush=True)
            retries -= 1
            time.sleep(3)

init_db()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ring_active"}), 200

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    
    # 1. CONTROL DE VUELTAS (Para evitar bucle infinito)
    # Si no viene el contador, empieza en 0
    current_loops = data.get('loops', 0)
    data['loops'] = current_loops + 1
    
    print(f"🔄 [RING] Vuelta #{data['loops']} recibida. Valor: {data.get('value')}", flush=True)

    # 2. DECISIÓN: ¿Seguir girando o parar?
    MAX_LOOPS = 3
    
    if data['loops'] < MAX_LOOPS:
        # --- MODO RECURSIVO: VOLVER AL INICIO ---
        data['audit'].append(f"Loop {data['loops']}: Returning to Receiver")
        
        try:
            # Llamamos al Receiver (Inicio del Anillo)
            # El Receiver llamará al Processor, que llamará al Auditor de nuevo...
            print(f"↩️ Enviando de vuelta al Receiver...", flush=True)
            response = requests.post(f"{NEXT_HOP}/start", json=data)
            
            # Devolvemos lo que nos responda la siguiente vuelta (Recursión)
            return jsonify(response.json())
            
        except Exception as e:
            print(f"❌ Error en el anillo: {e}", flush=True)
            return jsonify({"error": "Ring broken", "details": str(e)}), 500
            
    else:
        # --- FIN DEL ANILLO: GUARDAR Y TERMINAR ---
        data['audit'].append("Ring Finished (Max Loops Reached)")
        data['status'] = "FINISHED_RING"
        
        # Guardar en BD solo al final
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            log_entry = str(data)
            cur.execute('INSERT INTO auditoria (info) VALUES (%s)', (log_entry,))
            conn.commit()
            cur.close()
            conn.close()
            print(f"🏁 [RING] Meta alcanzada. Guardado en BD.", flush=True)
        except Exception as e:
            print(f"❌ Error BD: {e}", flush=True)

        return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)