import io
import numpy as np
import torch
import torchaudio
import pyaudio
import wave

# Silero VAD model setup
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=False)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

def int2float(sound):
    """Convert int16 numpy array to float32"""
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

# PyAudio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
CHUNK = 512

audio = pyaudio.PyAudio()

# Real-time VAD function
def start_recording():
    """Function to start recording audio and process it with Silero VAD"""
    
    stream = audio.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=SAMPLE_RATE,
                         input=True,
                         frames_per_buffer=CHUNK)

    print("Recording started...")
    
    silent_chunks = 0  # Counter for silent chunks
    silence_threshold = 0.2  # Confidence below this is considered silence
    secondsToStop = 2
    max_silent_chunks = int(secondsToStop / (CHUNK / SAMPLE_RATE))  # Chunks for 2 seconds of silence

    frames = []  # To store audio data
    recording_started = False  # Flag to indicate if recording has started

    while True:
        audio_chunk = stream.read(CHUNK)

        # Convert audio chunk to the required format
        audio_int16 = np.frombuffer(audio_chunk, np.int16)
        audio_float32 = int2float(audio_int16)

        # Get VAD confidence
        new_confidence = model(torch.from_numpy(audio_float32), SAMPLE_RATE).item()

        # Print VAD confidence
        print(f"VAD Confidence: {new_confidence:.2f}")

        # Check for silence and manage recording state
        if new_confidence < silence_threshold:
            if recording_started:
                silent_chunks += 1
        else:
            if not recording_started:
                print("Voice detected. Starting to save audio.")
                recording_started = True  # Start saving audio after detecting voice
            silent_chunks = 0

        # Save only relevant frames (after voice is detected)
        if recording_started:
            frames.append(audio_chunk)

        # Stop if silence persists for X seconds
        if recording_started and silent_chunks >= max_silent_chunks:
            print("Detectedsilence. Stopping recording.")
            break

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()

    # Save the audio to a file
    output_filename = "audio.wav"
    with wave.open(output_filename, 'wb') as archivo:
        archivo.setnchannels(CHANNELS)
        archivo.setsampwidth(audio.get_sample_size(FORMAT))
        archivo.setframerate(SAMPLE_RATE)
        archivo.writeframes(b''.join(frames))

    print(f"Audio saved to {output_filename}")

if __name__ == "__main__":
    start_recording()
