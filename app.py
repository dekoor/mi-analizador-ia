# app.py (Versión Corregida con CORS)

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from PIL import Image
from flask_cors import CORS # <-- 1. IMPORTACIÓN NUEVA

# 1. Configuración inicial
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app) # <-- 2. LÍNEA NUEVA PARA ACTIVAR CORS EN TODA LA APP

# 3. Creación de la ruta (endpoint) para analizar la imagen
@app.route('/analizar-imagen', methods=['POST'])
def analizar_imagen_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'El archivo no tiene nombre'}), 400

    if file:
        try:
            img = Image.open(file.stream)

            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            prompt = ["Describe el número en esta imagen. Responde solo con el número.", img]
            response = model.generate_content(prompt)

            print("Respuesta de Gemini:", response.text)

            return jsonify({'numero_detectado': response.text.strip()})

        except Exception as e:
            print(f"Ocurrió un error: {e}")
            return jsonify({'error': 'No se pudo procesar la imagen'}), 500

# 4. Código para iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)

