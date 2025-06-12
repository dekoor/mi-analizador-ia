# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# --- CONFIGURACIÓN ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)

# ======================= CAMBIO IMPORTANTE AQUÍ =======================
#
# Define la personalidad de tu chatbot. ¡Aquí es donde ocurre la magia!
# Simplemente cambia el texto dentro de las comillas para darle un tono diferente.
#
CHATBOT_PERSONALITY = "Eres un asistente de IA llamado 'Sparky'. Eres extremadamente entusiasta, amigable y un poco bromista. Siempre respondes con energía y usas emojis para expresarte. Tu objetivo es hacer que el usuario se sienta animado."
#
# ======================================================================

# Inicializa el modelo de Gemini
chat_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- DEFINICIÓN DE LA RUTA (ENDPOINT) ---
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Este endpoint recibe una pregunta del usuario, la combina con la personalidad
    definida y devuelve la respuesta del modelo.
    """
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'No se proporcionó ninguna pregunta en formato JSON.'}), 400

    user_question = data['question']

    try:
        # Se combinan la personalidad definida y la pregunta del usuario en un solo prompt
        full_prompt = f"{CHATBOT_PERSONALITY}\n\nPREGUNTA DEL USUARIO:\n{user_question}"
        
        print(f"Enviando prompt completo a Gemini: {full_prompt}")
        response = chat_model.generate_content(full_prompt)
        print(f"Respuesta de Gemini: {response.text}")

        return jsonify({'answer': response.text.strip()})

    except Exception as e:
        print(f"Ocurrió un error al contactar a la API de Gemini: {e}")
        return jsonify({'error': 'No se pudo obtener una respuesta del modelo.'}), 500

# --- CÓDIGO PARA INICIAR EL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
