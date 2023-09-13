from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS  

app = Flask(__name__)
CORS(app) 

@app.route('/api/file', methods=['POST'])
def get_file():
    data = request.get_json()
    filepath = data['route']
    directory, filename = filepath.rsplit('\\', 1)
    
    try:
        return send_from_directory(directory, filename)
    except FileNotFoundError: 
        return jsonify({"error": "Archivo no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
