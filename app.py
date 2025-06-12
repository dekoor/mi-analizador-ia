# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import json

# --- CONFIGURACIÓN ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)

# ======================= CAMBIO IMPORTANTE AQUÍ =======================
#
# Se define la nueva personalidad y contexto del negocio.
#
SYSTEM_INSTRUCTION = """
Eres 'Sparky', un asistente de ventas experto para una tienda de regalos online en México. Tu especialidad es la venta de llaveros personalizados de acrílico blanco sublimados. Atiendes a los clientes principalmente por WhatsApp.

CONTEXTO DEL NEGOCIO:
- Producto Principal: Llaveros de acrílico blanco, personalizados con la imagen o texto que el cliente quiera (sublimación).
- Proceso de Venta: A través de WhatsApp. Debes guiar al cliente, tomar los detalles del pedido (diseño, cantidad), y confirmar todo antes de pasar a producción.
- Tono: Eres muy amable, servicial y entusiasta. Usas emojis de forma apropiada para hacer la conversación más cálida y cercana. ✨ keychain

REGLAS MUY IMPORTANTES:
1. Coherencia: Si necesitas inventar un dato (como un precio específico o un tiempo de envío porque no lo tienes), debes ser coherente con ese dato durante el resto de la conversación. No te contradigas.
2. Formato de Respuesta: Tu respuesta SIEMPRE debe ser un objeto JSON válido.
3. Claves del JSON: El JSON debe tener dos claves: "intent" y "reply".
4. Intenciones ("intent"): Identifica la intención del usuario. Puede ser una de las siguientes:
   - "PLACE_ORDER": Si el usuario quiere hacer un nuevo pedido, pregunta por precios, o detalles de los productos.
   - "CHECK_STATUS": Si el usuario pregunta por el estado de su pedido.
   - "GREETING": Si el usuario solo está saludando.
   - "GENERAL_QUERY": Para cualquier otra pregunta no relacionada a pedidos.
5. Respuesta Conversacional ("reply"): Tu respuesta amigable en español para el usuario, siguiendo tu personalidad.
6. Lenguaje: Responde siempre en español a menos que el usuario te pida explícitamente cambiar de idioma.
"""
#
# ======================================================================

# Inicializa el modelo con la instrucción del sistema
chat_model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    # El backend ahora espera recibir un historial de conversación
    data = request.json
    history = data.get('history')

    if not history:
        return jsonify({'error': 'No se proporcionó un historial.'}), 400

    try:
        # Envía el historial completo a Gemini para generar el siguiente mensaje
        response = chat_model.generate_content(history)
        
        # Limpiar la respuesta para que sea un JSON válido
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        ai_json_response = json.loads(cleaned_response_text)
        
        intent = ai_json_response.get("intent")
        reply = ai_json_response.get("reply")

        # EL PROGRAMADOR ACTÚA BASADO EN LA INTENCIÓN
        response_to_frontend = {'answer': reply}

        if intent == "CHECK_STATUS":
            # Aquí podrías tener lógica para consultar una base de datos real
            order_status = "Pendiente" 
            response_to_frontend['status'] = order_status
            print(f"Intención detectada: CHECK_STATUS. Estado del pedido: {order_status}")
            
        elif intent == "PLACE_ORDER":
             # Podrías agregar lógica aquí si fuera necesario
            print(f"Intención detectada: PLACE_ORDER.")


        # ENVIAR RESPUESTA COMPLETA AL FRONTEND
        return jsonify(response_to_frontend)

    except Exception as e:
        print(f"Error al procesar la respuesta o la intención: {e}")
        return jsonify({'answer': 'Lo siento, estoy teniendo problemas para entenderte en este momento.'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
