import os, requests, json
from flask import Flask, request

app = Flask(__name__)
# K8s inyectará esta URL por variable de entorno
NEXT_HOP = os.getenv("NEXT_SERVICE_URL", "http://processor-svc:5000")

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    print(f"Recibido: {data}")
    # Enviar al siguiente nodo (Service Discovery de K8s)
    try:
        response = requests.post(f"{NEXT_HOP}/process", json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)