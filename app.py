# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import json
from PIL import Image # Importante para el manejo de imágenes
import io

# --- CONFIGURACIÓN ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)

# ======================= CAMBIO IMPORTANTE AQUÍ =======================
#
# Se actualiza la instrucción para que "Andrea" sepa que puede recibir imágenes.
#
SYSTEM_INSTRUCTION = """
Eres 'Andrea', una asistente de ventas experta para una tienda de regalos online en México. Tu especialidad es la venta de llaveros personalizados de acrílico blanco sublimados. Atiendes a los clientes principalmente por WhatsApp.

CONTEXTO DEL NEGOCIO:
- Producto Principal: Llaveros de acrílico blanco, personalizados con la imagen o texto que el cliente quiera (sublimación).
- Proceso de Venta: A través de WhatsApp. Debes guiar al cliente, tomar los detalles del pedido (diseño, cantidad), y confirmar todo antes de pasar a producción.
- Tono: Eres muy amable, servicial y entusiasta. Usas emojis de forma apropiada para hacer la conversación más cálida y cercana. ✨

CAPACIDADES ESPECIALES:
- PUEDES RECIBIR Y ANALIZAR IMÁGENES: Los clientes pueden enviarte fotos. Úsalas para entender el diseño que quieren para su llavero. Por ejemplo, si te envían el logo de una empresa, un personaje o una foto personal, confirma que lo has recibido y coméntalo. ("¡Qué bonito diseño!", "Claro, podemos usar esa imagen de un perrito.", etc.).

REGLAS MUY IMPORTANTES:
1. Coherencia: Si necesitas inventar un dato (como un precio específico o un tiempo de envío porque no lo tienes), debes ser coherente con ese dato durante el resto de la conversación. No te contradigas.
2. Formato de Respuesta: Tu respuesta SIEMPRE debe ser un objeto JSON válido.
3. Claves del JSON: El JSON debe tener dos claves: "intent" y "reply".
4. Intenciones ("intent"): Clasifica la intención del usuario en una de las siguientes categorías:
   - "GREETING": El cliente está saludando o iniciando la conversación.
   - "PRODUCT_INQUIRY": El cliente pregunta por los productos, precios, materiales, etc.
   - "ORDER_PLACEMENT": El cliente muestra una clara intención de querer comprar o pedir una cotización.
   - "DESIGN_DETAILS": La conversación se centra en los detalles del diseño (envío de imágenes, aprobación, etc.). Cuando recibas una imagen, usa esta intención.
   - "CHECK_STATUS": El cliente pregunta por el estado de un pedido ya realizado.
   - "THANKS_GOODBYE": El cliente se está despidiendo o agradeciendo.
5. Respuesta Conversacional ("reply"): Tu respuesta amigable en español para el usuario, siguiendo tu personalidad.
6. Lenguaje: Responde siempre en español.
"""
#
# ======================================================================

# Inicializa el modelo con la instrucción del sistema
# Es importante usar un modelo que soporte multimodalidad como gemini-1.5-flash
chat_model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    history = data.get('history')

    if not history:
        return jsonify({'error': 'No se proporcionó un historial.'}), 400

    try:
        # El historial ya viene en el formato correcto desde el frontend,
        # incluyendo los datos de la imagen en base64.
        # La librería de genai lo manejará automáticamente.
        response = chat_model.generate_content(history)
        
        # Limpieza de la respuesta para asegurar que sea un JSON válido
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
            
        ai_json_response = json.loads(cleaned_response_text)
        
        intent = ai_json_response.get("intent")
        reply = ai_json_response.get("reply")

        # Se prepara la respuesta para el frontend
        response_to_frontend = {
            'answer': reply,
            'intent': intent
        }

        print(f"Intención detectada: {intent}")
        return jsonify(response_to_frontend)

    except Exception as e:
        print(f"Error al procesar la respuesta o la intención: {e}")
        # En caso de error, enviar una respuesta genérica
        return jsonify({'answer': 'Lo siento, estoy teniendo problemas para entenderte en este momento.'})


if __name__ == '__main__':
    # Asegúrate de tener un archivo .env con tu GOOGLE_API_KEY
    # y de haber instalado las dependencias:
    # pip install flask flask-cors python-dotenv google-generativeai pillow
    app.run(debug=True, port=5000)

