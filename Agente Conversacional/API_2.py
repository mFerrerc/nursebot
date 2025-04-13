import requests
import json
from googletrans import Translator

# URL del servidor Flask
FLASK_SERVER_URL = "http://localhost:5000/generate"

SERVER_OLLAMA = "http://host.docker.internal:11434/api/generate"

def generate_audio(text, voice_name="JeiJo_", in_language="Spanish", out_language="es"):
    """
    Función para enviar texto al servidor Flask y generar audio.
    """
    payload = {
        "text": text,
        "voice_name": voice_name,
        "in_language": in_language,
        "out_language": out_language
    }
    try:
        response = requests.post(FLASK_SERVER_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            return {
                "audio_file": data["audio_file"],
                "duration": data["duration"],
                "message": data["message"]
            }
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error al conectar con el servidor: {e}"}

def traducir_texto(texto, src='auto', dest='es'):
    """
    Traduce un texto desde el idioma de origen al idioma de destino.
    
    Args:
        texto (str): Texto a traducir.
        src (str): Código del idioma de origen (por defecto 'auto' para detectar automáticamente).
        dest (str): Código del idioma de destino (por defecto 'es' para español).
    
    Returns:
        str: Texto traducido.
    """
    try:
        translator = Translator()
        traduccion = translator.translate(texto, src=src, dest=dest)
        return traduccion.text
    except Exception as e:
        return f"Error en la traducción: {e}"


