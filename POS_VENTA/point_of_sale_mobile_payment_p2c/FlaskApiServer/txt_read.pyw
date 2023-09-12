from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS  # Importa la extensión flask_cors

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación

@app.route('/api/file', methods=['POST'])
def get_file():
    # Obtiene el JSON del cuerpo de la solicitud
    data = request.get_json()
    filepath = data['route']
    
    # Divide la ruta para obtener el directorio y el nombre del archivo
    directory, filename = filepath.rsplit('\\', 1)
    
    try:
        return send_from_directory(directory, filename)
    except FileNotFoundError:  # Captura el error específico para mayor claridad
        return jsonify({"error": "Archivo no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
