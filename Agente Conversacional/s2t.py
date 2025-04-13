import whisper
import torch
import time
import whisper_s2t

# Cargar el modelos
model = whisper.load_model("small")

models2t = whisper_s2t.load_model(
    model_identifier="medium",
    backend='CTranslate2',
    device='cuda',
    compute_type='float32'
)
#small float32
def trans(audio_file):
    start_time = time.time()
    
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)  

    # Archivo de audio
    files = [audio_file]

    # Configurar el idioma detectado para la transcripción
    lang_codes = [detected_lang]  # Configurar el idioma original detectado
    
    files = [audio_file]

    tasks = ['transcribe']
    initial_prompts = [None]

    start_time2 = time.time()

    # Transcribir el audio
    out = models2t.transcribe_with_vad(
        files,
        lang_codes="es",
        tasks=tasks,
        initial_prompts=initial_prompts,
        batch_size=24
    )

    '''end_time = time.time()
    print(f"\nTiempo para transcribir el audio completo: {end_time - start_time2:.2f} segundos")
    print("\n")
    '''
    
    transciption = ""

    # Mostrar solo el texto transcrito
    for segment in out[0]:
        print(segment['text'])
        transciption = segment['text']
    '''
    srt_filename = "s2t.txt"
    with open(srt_filename, 'w', encoding="utf-8") as srt_file:
        prev = 0
        for segment in out[0]:
            srt_file.write(segment['text'])'''

    print(f"Idioma detectado: {detected_lang}")
        
    return transciption, detected_lang