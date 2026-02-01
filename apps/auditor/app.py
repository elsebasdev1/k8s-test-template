from flask import Flask, request

app = Flask(__name__)

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    data['audit'].append("Audit Completed")
    data['status'] = "FINISHED"
    print(f"CICLO COMPLETADO: {data}") # Log para captura de pantalla
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)