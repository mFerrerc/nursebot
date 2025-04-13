import silero
import s2t
import api
import API_2
import time

FLASK_SERVER_URL = "http://localhost:5000/generate"
SERVER_OLLAMA = "http://host.docker.internal:11434/api/v1/translate"

# Mapeo de idiomas detectados a configuraciones de voz e idioma
language_config = {
    "es": {"voice_name": "Diego_Galán", "in_language": "Spanish"},
    "en": {"voice_name": "Broom", "in_language": "English"},
    "fr": {"voice_name": "Adina_-_French_teenager", "in_language": "French"},
    "pt": {"voice_name": "Adriano_-_Narrador3", "in_language": "Portuguese"},
    "it": {"voice_name": "Alessandro", "in_language": "Italian"},
    "de": {"voice_name": "Tommy_Studio_Voice_2", "in_language": "German"},
    "ru": {"voice_name": "Aleksandr_Petrov", "in_language": "Russian"},
}

if __name__ == '__main__':
    inicio_texto = "Buenos días, soy NurseBot, un asistente diseñado para suministrarles sus medicamentos, \
                    ayudar al equipo médico en sus cuidados diarios y ofrecerles compañía siempre que lo deseen. \
                    ¡Es un placer estar con ustedes!"

    # Generar introducción en audio
    # Inicialmente en español
    default_config = language_config["es"]
    API_2.generate_audio(inicio_texto, voice_name=default_config["voice_name"], in_language=default_config["in_language"], out_language="es")
    
    while True:
        # Iniciar grabación de audio
        silero.start_recording()
        audio_file = "audio.wav"

        # Transcripción de voz a texto (STT)
        inicio = time.time()
        transcription, detected_lang = s2t.trans(audio_file)
        fin = time.time()
        time_stt = fin - inicio
        print(f"Tiempo STT: {time_stt:.2f} s")

        # Consultar modelo de lenguaje
        inicio = time.time()
        text = api.post_({"question": transcription})
        fin = time.time()
        time_llm = fin - inicio
        print(f"Respuesta del modelo: {text}")
        print(f"Tiempo LLM: {time_llm:.2f} s")

        # Traducir si el idioma detectado no es español
        if detected_lang != "es":
            inicio = time.time()
            text_traducido = API_2.traducir_texto(text, dest=detected_lang)
            fin = time.time()
            tiempo_traducir = fin - inicio
            print(f"Texto traducido: {text_traducido}")
            print(f"Tiempo Traducir: {tiempo_traducir:.2f} s")
        else:
            text_traducido = text

        # Obtener configuración de idioma
        config = language_config.get(detected_lang, default_config)  # Usa configuración por defecto si no se encuentra el idioma detectado

        # Generar audio a partir del texto traducido
        inicio = time.time()
        API_2.generate_audio(text_traducido, voice_name=config["voice_name"], in_language=config["in_language"], out_language=detected_lang)
        fin = time.time()
        time_tts = (fin - inicio)/4
        print(f"Tiempo TTS: {time_tts:.2f} s")

        # Calcular tiempo total
        if detected_lang != "es":
            total_time = time_stt + time_llm + tiempo_traducir + time_tts
        else:
            total_time = time_stt + time_llm + time_tts
        print(f"Tiempo Total: {total_time:.2f} s")
