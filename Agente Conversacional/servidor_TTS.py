import os
import torch
import torchaudio
import warnings
import time
import numpy as np
from flask import Flask, request, jsonify
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from torch.cuda.amp import autocast  # Para precisión mixta
import subprocess  # Para reproducción de audio

warnings.simplefilter(action='ignore', category=FutureWarning)

# Configuración de la aplicación Flask
app = Flask(__name__)

# Ruta de salida de los audios
OUTPUT_AUDIO_DIR = "/home/drake/xtts-webui/salida/"
os.makedirs(OUTPUT_AUDIO_DIR, exist_ok=True)

# Diccionario de idiomas y sus códigos
leng_and_ids = {
    "Select language": "es",
    "Arabic": "ar",
    "Bulgarian": "bg",
    "Chinese": "zh",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Slovak": "sk",
    "Spanish": "es",
    "Swedish": "sv",
    "Tamil": "ta",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Vietnamese": "vi"
}

# Variable global del modelo
XTTS_MODEL = None

# Función para limpiar la caché de la GPU
def clear_gpu_cache():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Función para cargar el modelo XTTS
def load_model(xtts_checkpoint, xtts_config, xtts_vocab, xtts_speaker):
    global XTTS_MODEL
    clear_gpu_cache()
    if not xtts_checkpoint or not xtts_config or not xtts_vocab:
        raise ValueError("Faltan parámetros para cargar el modelo XTTS")

    config = XttsConfig()
    config.load_json(xtts_config)
    XTTS_MODEL = Xtts.init_from_config(config)
    print("Cargando modelo XTTS...")
    XTTS_MODEL.load_checkpoint(config, checkpoint_path=xtts_checkpoint, vocab_path=xtts_vocab, speaker_file_path=xtts_speaker, use_deepspeed=False)

    if torch.cuda.is_available():
        XTTS_MODEL.cuda()
        print("Modelo movido a GPU.")
    else:
        print("Modelo está en CPU.")

    XTTS_MODEL.eval()  # Modo evaluación para optimización
    print("Modelo cargado correctamente!")

# Función para generar el audio
def run_tts0(selected_language, lang, tts_text, speaker_audio_file, temperature, length_penalty, repetition_penalty, top_k, top_p, sentence_split, use_config):
    inicio = time.time()
    if XTTS_MODEL is None or not speaker_audio_file:
        raise ValueError("El modelo no está cargado o no has especificado un audio de referencia.")

    selec_language = leng_and_ids.get(selected_language)
    speaker_audio_path = f"/home/drake/xtts-webui/model/voices/{selec_language}/{speaker_audio_file}.mp3"

    gpt_cond_latent, speaker_embedding = XTTS_MODEL.get_conditioning_latents(
        audio_path=speaker_audio_path, 
        gpt_cond_len=XTTS_MODEL.config.gpt_cond_len, 
        max_ref_length=XTTS_MODEL.config.max_ref_len, 
        sound_norm_refs=XTTS_MODEL.config.sound_norm_refs
    )

    with torch.no_grad():  # Desactiva el cálculo de gradientes
        with autocast():  # Precisión mixta
            if use_config:
                out = XTTS_MODEL.inference(
                    text=tts_text,
                    language=lang,
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    temperature=XTTS_MODEL.config.temperature,
                    length_penalty=XTTS_MODEL.config.length_penalty,
                    repetition_penalty=XTTS_MODEL.config.repetition_penalty,
                    top_k=XTTS_MODEL.config.top_k,
                    top_p=XTTS_MODEL.config.top_p,
                    enable_text_splitting=True
                )
            else:
                out = XTTS_MODEL.inference(
                    text=tts_text,
                    language=lang,
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    temperature=temperature,
                    length_penalty=length_penalty,
                    repetition_penalty=float(repetition_penalty),
                    top_k=top_k,
                    top_p=top_p,
                    enable_text_splitting=sentence_split
                )

    # Convertir salida a tensor si es necesario
    if isinstance(out["wav"], torch.Tensor):
        wav_tensor = out["wav"].to('cuda')  # Asegúrate de que el tensor esté en la GPU
    elif isinstance(out["wav"], np.ndarray):
        wav_tensor = torch.from_numpy(out["wav"]).float().to('cuda')
    else:
        raise TypeError("Tipo desconocido de audio generado.")

    # Agregar una dimensión adicional si es necesario
    if wav_tensor.dim() == 1:
        wav_tensor = wav_tensor.unsqueeze(0)

    # Guardar el archivo generado
    output_filename = f"{speaker_audio_file}_{int(torch.randint(0, 1000000, (1,)).item())}.wav"
    output_path = os.path.join(OUTPUT_AUDIO_DIR, output_filename)
    torchaudio.save(output_path, wav_tensor.cpu(), 24000)
    fin = time.time()

    time_tts = fin - inicio
    print(f"Tiempo TTS: {time_tts:.2f} s")
    
    # Calcular duración del audio
    num_frames = wav_tensor.size(1)  # Número total de frames
    sample_rate = 24000  # Frecuencia de muestreo
    duration = num_frames / sample_rate  # Duración en segundos

    return "Speech generado correctamente!", output_path, duration

# Endpoint para generar audio
@app.route('/generate', methods=['POST'])
def generate_speech():
    data = request.json
    tts_text = data.get("text")
    speaker_audio_file = data.get("voice_name")
    input_language = data.get("in_language")
    output_language = data.get("out_language")

    if not tts_text or not speaker_audio_file or not input_language:
        return jsonify({"error": "Faltan datos necesarios. Incluye 'text', 'voice_name', 'in_language' y 'out_language'."}), 400

    try:
        tts_language = leng_and_ids.get(input_language, output_language)
        temperature = 0.75
        length_penalty = 1
        repetition_penalty = 5
        top_k = 50
        top_p = 0.85
        sentence_split = True
        use_config = False

        status, generated_audio, duration = run_tts0(
            input_language,
            tts_language,
            tts_text,
            speaker_audio_file,
            temperature,
            length_penalty,
            repetition_penalty,
            top_k,
            top_p,
            sentence_split,
            use_config
        )

        # Reproducir el audio generado con ffplay
        if generated_audio and os.path.exists(generated_audio):
            subprocess.run(["ffplay", "-nodisp", "-autoexit", generated_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return jsonify({"audio_file": generated_audio, "duration": round(duration, 2), "message": status}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicio del servidor Flask
if __name__ == "__main__":
    xtts_checkpoint0 = "model/model.pth"
    xtts_config0 = "model/config.json"
    xtts_vocab0 = "model/vocab.json"
    xtts_speaker0 = "model/speakers_xtts.pth"

    load_model(xtts_checkpoint0, xtts_config0, xtts_vocab0, xtts_speaker0)
    app.run(host='0.0.0.0', port=5000)
