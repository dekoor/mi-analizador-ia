# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# --- CONFIGURACIÓN ---
# Carga las variables de entorno (tu GOOGLE_API_KEY)
load_dotenv()
# Configura la API de Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Inicializa la aplicación Flask
app = Flask(__name__)
# Habilita CORS para permitir que tu página web se comunique con este servidor
CORS(app)

# --- LÓGICA DEL CHAT ---

# Crea el modelo generativo de Gemini que se usará para el chat
# Se inicializa una sola vez para ser más eficiente
chat_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- DEFINICIÓN DE LA RUTA (ENDPOINT) ---
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Este endpoint recibe una pregunta del usuario, la envía a Gemini
    y devuelve la respuesta del modelo.
    """
    # 1. Obtener los datos JSON de la solicitud
    # Se espera un formato como: {"question": "Tu pregunta aquí"}
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'No se proporcionó ninguna pregunta en formato JSON.'}), 400

    user_question = data['question']

    try:
        # 2. Enviar la pregunta al modelo de Gemini
        # El prompt es simplemente la pregunta del usuario
        print(f"Pregunta recibida para Gemini: {user_question}")
        response = chat_model.generate_content(user_question)
        print(f"Respuesta de Gemini: {response.text}")

        # 3. Devolver la respuesta de Gemini al frontend
        # La respuesta se envía en un formato JSON como: {"answer": "La respuesta de la IA"}
        return jsonify({'answer': response.text.strip()})

    except Exception as e:
        # Manejo de errores en caso de que algo falle con la API de Gemini
        print(f"Ocurrió un error al contactar a la API de Gemini: {e}")
        return jsonify({'error': 'No se pudo obtener una respuesta del modelo.'}), 500

# --- CÓDIGO PARA INICIAR EL SERVIDOR ---
if __name__ == '__main__':
    # Inicia el servidor en modo de depuración para ver los errores fácilmente
    # Escuchará en http://127.0.0.1:5000
    app.run(debug=True, port=5000)
