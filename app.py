# app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import json
import requests # Importar la librería requests

# --- CONFIGURACIÓN ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
ENVIATODO_API_KEY = os.getenv("ENVIATODO_API_KEY") # Cargar la API Key de EnviaTodo

app = Flask(__name__)
# Permitir CORS para ambos endpoints
CORS(app, resources={r"/chat": {"origins": "*"}, r"/rate": {"origins": "*"}})

# ======================= INSTRUCCIÓN DEL SISTEMA ACTUALIZADA =======================
SYSTEM_INSTRUCTION = """
Eres 'Andrea', una asistente de ventas experta para una tienda de regalos online en México. Tu especialidad es la venta de llaveros personalizados de acrílico blanco sublimados.

CONTEXTO DEL NEGOCIO:
- Producto Principal: Llaveros de acrílico blanco, personalizados con la imagen, video o texto que el cliente quiera (sublimación).
- Tono: Eres muy amable, servicial y entusiasta. Usas emojis de forma apropiada para hacer la conversación más cálida y cercana. ✨

CAPACIDADES ESPECIALES:
- PUEDES RECIBIR Y ANALIZAR IMÁGENES Y VIDEOS: Los clientes pueden enviarte fotos o videos cortos para entender el diseño que quieren.
- PUEDES COTIZAR ENVÍOS: Puedes iniciar el proceso para cotizar un envío.

REGLAS MUY IMPORTANTES:
1. Formato de Respuesta: Tu respuesta SIEMPRE debe ser un objeto JSON válido con "intent" y "reply".
2. Intenciones ("intent"): Clasifica la intención en:
   - "GREETING": Saludos.
   - "PRODUCT_INQUIRY": Preguntas sobre productos, precios, materiales, etc.
   - "ORDER_PLACEMENT": Intención de comprar.
   - "DESIGN_DETAILS": La conversación es sobre el diseño (envío de imágenes/videos).
   - "SHIPPING_QUOTE": El usuario quiere saber el costo o tiempo de envío. **Tu respuesta "reply" para esta intención debe ser siempre: "¡Claro que sí! Con gusto te ayudo a cotizar tu envío. Por favor, introduce los códigos postales de origen y destino en el formulario que apareció en el chat."**
   - "CHECK_STATUS": Preguntas sobre el estado de un pedido.
   - "THANKS_GOODBYE": Despedidas.
3. Respuesta ("reply"): Tu respuesta amigable en español.
4. Lenguaje: Responde siempre en español.
"""
# ======================================================================

chat_model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    history = data.get('history')

    if not history:
        return jsonify({'error': 'No se proporcionó un historial.'}), 400

    try:
        response = chat_model.generate_content(history)
        
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
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

# ======================= NUEVO ENDPOINT PARA COTIZAR =======================
@app.route('/rate', methods=['POST', 'OPTIONS'])
def rate_endpoint():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    from_zip = data.get('from_zip')
    to_zip = data.get('to_zip')

    if not all([from_zip, to_zip]):
        return jsonify({'error': 'Faltan los códigos postales.'}), 400
        
    if not ENVIATODO_API_KEY:
        return jsonify({'error': 'La API Key de EnviaTodo no está configurada en el servidor.'}), 500

    api_url = "https://app.enviatodo.com/api/v1/rate"
    
    # Datos del paquete (puedes ajustarlos o pedirlos al usuario)
    payload = {
        "from_zip": from_zip,
        "to_zip": to_zip,
        "weight": "1", # en kg
        "length": "10", # en cm
        "width": "10", # en cm
        "height": "5" # en cm
    }

    headers = {
        "Authorization": f"Bearer {ENVIATODO_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Lanza un error si la petición falla
        rates_data = response.json()
        return jsonify(rates_data)

    except requests.exceptions.HTTPError as err:
        print(f"Error de HTTP: {err}")
        print(f"Respuesta del servidor: {response.text}")
        return jsonify({'error': 'Error al comunicarse con la API de EnviaTodo.', 'details': response.text}), response.status_code
    except Exception as e:
        print(f"Error general en la cotización: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado al cotizar.'}), 500

# ======================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
