import os, requests
from flask import Flask, request

app = Flask(__name__)
NEXT_HOP = os.getenv("NEXT_SERVICE_URL", "http://auditor-svc:5000")

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    val = data.get('value', 0)
    
    # Lógica de Negocio (Fácil de cambiar en el examen)
    if val % 2 == 0:
        data['value'] = val * 2
        data['audit'].append("Multiplied by 2 (Even)")
    else:
        data['value'] = val + 1
        data['audit'].append("Added 1 (Odd)")

    # Pasar al siguiente
    response = requests.post(f"{NEXT_HOP}/audit", json=data)
    return response.json()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)