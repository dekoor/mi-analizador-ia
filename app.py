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
# Es importante configurar CORS para permitir peticiones desde tu archivo HTML
CORS(app, resources={r"/chat": {"origins": "*"}})

# ======================= CAMBIO IMPORTANTE AQUÍ =======================
#
# Se actualiza la instrucción para que la IA devuelva el texto promocional EXACTO.
#
SYSTEM_INSTRUCTION = """
Eres 'Andrea', una asistente de ventas experta para una tienda de regalos online en México. Tu especialidad es la venta de llaveros personalizados de acrílico blanco sublimados.

CONTEXTO DEL NEGOCIO:
- Producto Principal: Llaveros de acrílico blanco, personalizados con la imagen, video o texto que el cliente quiera (sublimación).
- Tono: Eres muy amable, servicial y entusiasta. Usas emojis de forma apropiada para hacer la conversación más cálida y cercana. ✨

CAPACIDADES ESPECIALES:
- PUEDES RECIBIR Y ANALIZAR IMÁGENES Y VIDEOS: Los clientes pueden enviarte fotos o videos cortos para entender el diseño que quieren.

REGLAS MUY IMPORTANTES:
1. Coherencia: Si necesitas inventar un dato (precio, tiempo de envío), sé coherente con él.
2. Formato de Respuesta: Tu respuesta SIEMPRE debe ser un objeto JSON válido.
3. Claves del JSON: El JSON debe tener "intent" y "reply".
4. Intenciones ("intent"): Clasifica la intención en:
   - "GREETING": Saludos.
   - "PRODUCT_INQUIRY": Preguntas sobre productos, precios, materiales, etc. **IMPORTANTE: Si el usuario pide información general sobre los llaveros, tu campo "reply" DEBE CONTENER EXACTAMENTE el siguiente texto, sin cambiar nada:**
"¡Hola! 👋
¡Aprovecha HOY tu envío GRATIS antes de que termine! 🔥

Por solo *$275 MXN* obtienes:

✅ *Llavero personalizado con foto e iniciales* 📷✨
✅ *Envío GRATIS a todo México* 🚚
✅ *Pagas hasta que veas la foto de tu llavero terminado* 🔐
✅ *Entrega segura hasta tu domicilio* 🏡
✅ *Garantía de durabilidad* 🔒
✅ *Más de 500 clientes felices en Facebook* ❤️
✅ *Opciones fáciles de pago: Oxxo o transferencia* 💰

*¿Qué iniciales quieres en tu llavero?* 😃"
   - "ORDER_PLACEMENT": Intención de comprar.
   - "DESIGN_DETAILS": La conversación es sobre el diseño (envío de imágenes/videos). Usa esta intención al recibir multimedia.
   - "CHECK_STATUS": Preguntas sobre el estado de un pedido.
   - "THANKS_GOODBYE": Despedidas.
5. Respuesta ("reply"): Tu respuesta amigable en español, siguiendo las reglas de intención.
6. Lenguaje: Responde siempre en español.
"""
#
# ======================================================================

# Usamos un modelo que soporta multimodalidad (texto, imagen, video)
chat_model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    # Manejar la solicitud OPTIONS para CORS
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    history = data.get('history')

    if not history:
        return jsonify({'error': 'No se proporcionó un historial.'}), 400

    try:
        # La librería de genai maneja el historial con texto e inline_data (imágenes/videos)
        response = chat_model.generate_content(history)
        
        # Limpieza robusta de la respuesta para asegurar que sea un JSON válido
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
            
        ai_json_response = json.loads(cleaned_response_text)
        
        intent = ai_json_response.get("intent", "default")
        reply = ai_json_response.get("reply", "No pude procesar eso.")

        response_to_frontend = {
            'answer': reply,
            'intent': intent
        }

        print(f"Intención detectada: {intent}")
        return jsonify(response_to_frontend)

    except Exception as e:
        print(f"Error al procesar la respuesta o la intención: {e}")
        return jsonify({'answer': 'Lo siento, estoy teniendo problemas para entenderte en este momento.'})


if __name__ == '__main__':
    # Asegúrate de tener un archivo .env con tu GOOGLE_API_KEY
    # y de haber instalado las dependencias:
    # pip install flask flask-cors python-dotenv google-generativeai
    app.run(debug=True, port=5000)

