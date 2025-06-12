# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import json # Importar la librería para manejar JSON

# --- CONFIGURACIÓN ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)

# ======================= CAMBIO IMPORTANTE AQUÍ =======================
#
# Ahora el prompt le pide a la IA que identifique intenciones
# y responda en un formato JSON estructurado.
#
CHATBOT_PERSONALITY = """
Eres un asistente de IA para un negocio. Eres eficiente y amable.

REGLA MUY IMPORTANTE: Tu respuesta SIEMPRE debe ser un objeto JSON válido.
El JSON debe tener dos claves: "intent" y "reply".

- "intent": Identifica la intención del usuario. Puede ser una de las siguientes:
  - "CHECK_STATUS": Si el usuario pregunta por el estado de su pedido.
  - "GREETING": Si el usuario solo está saludando.
  - "GENERAL_QUERY": Para cualquier otra pregunta.
- "reply": Tu respuesta conversacional en español para el usuario.

Ejemplo:
Pregunta del usuario: "¿qué onda con mi pedido?"
Tu respuesta JSON:
{
  "intent": "CHECK_STATUS",
  "reply": "¡Hola! Claro, déjame revisar el estado de tu pedido ahora mismo."
}
"""
#
# ======================================================================

chat_model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_question = data.get('question')

    if not user_question:
        return jsonify({'error': 'No se proporcionó ninguna pregunta.'}), 400

    try:
        # 1. ENVIAR EL PROMPT A GEMINI
        full_prompt = f"{CHATBOT_PERSONALITY}\n\nPREGUNTA DEL USUARIO:\n{user_question}"
        response = chat_model.generate_content(full_prompt)
        
        # Limpiar la respuesta para que sea un JSON válido
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        ai_json_response = json.loads(cleaned_response_text)
        
        intent = ai_json_response.get("intent")
        reply = ai_json_response.get("reply")

        # 2. EL PROGRAMADOR ACTÚA BASADO EN LA INTENCIÓN
        response_to_frontend = {'answer': reply}

        if intent == "CHECK_STATUS":
            # --- Aquí iría tu lógica de negocio ---
            # Por ejemplo, buscar en una base de datos el estado real del pedido.
            # Para este ejemplo, simplemente devolveremos un estado fijo.
            order_status = "Pendiente" 
            
            # Agregamos el estado a la respuesta que enviaremos al frontend
            response_to_frontend['status'] = order_status
            print(f"Intención detectada: CHECK_STATUS. Estado del pedido: {order_status}")

        # 3. ENVIAR RESPUESTA COMPLETA AL FRONTEND
        return jsonify(response_to_frontend)

    except Exception as e:
        print(f"Error al procesar la respuesta o la intención: {e}")
        # Enviar una respuesta genérica si falla la detección de intención
        return jsonify({'answer': 'Lo siento, estoy teniendo problemas para entenderte en este momento.'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
