"""
Inferencia con zero-shot voice cloning usando el modelo fine-tuneado.
Uso: python zero_shot_inference.py
"""
import soundfile as sf
import torch
import numpy as np
from chatterbox.tts import ChatterboxTTS

# Configuración
MODEL_PATH = "./checkpoints_lora/merged_model"
REFERENCE_AUDIO = "reference_voice.wav"  # Audio de la voz que querés clonar (3-10 segundos)
OUTPUT_PATH = "cloned_voice_output.wav"
TEXT = "Mi nombre es Francisco, hoy no voy a ir a la universidad, prefiero quedarme trabajando en casa."
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Cargando modelo desde {MODEL_PATH}...")
model = ChatterboxTTS.from_local(ckpt_dir=MODEL_PATH, device=DEVICE)

print(f"Cargando audio de referencia: {REFERENCE_AUDIO}")
# Cargar audio de referencia
ref_audio, sr = sf.read(REFERENCE_AUDIO)

# Asegurar que sea mono
if len(ref_audio.shape) > 1:
    ref_audio = ref_audio.mean(axis=1)

# Resamplear a 24kHz si es necesario
if sr != 24000:
    import librosa
    ref_audio = librosa.resample(ref_audio, orig_sr=sr, target_sr=24000)
    sr = 24000

print(f"Generando audio...")
print(f"Texto: {TEXT}")

# Nota: Chatterbox maneja el voice cloning internamente a través del modelo fine-tuneado
# El modelo ya fue entrenado con voces LATAM, por lo que generará con ese acento
# Para true zero-shot cloning, pasamos el audio de referencia

try:
    wav = model.generate(
        text=TEXT,
        audio_prompt_path=REFERENCE_AUDIO,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.2,
        min_p=0.05
    )

    # Convertir a numpy si es tensor
    if isinstance(wav, torch.Tensor):
        wav = wav.cpu().numpy()

    # Asegurar que sea 1D
    if len(wav.shape) > 1:
        wav = wav.squeeze()
        
    # Trim silence (simple energy-based trimming)
    threshold = 0.01
    mask = np.abs(wav) > threshold
    if np.any(mask):
        start = np.argmax(mask)
        end = len(wav) - np.argmax(mask[::-1])
        pad = int(0.1 * 24000)
        start = max(0, start - pad)
        end = min(len(wav), end + pad)
        wav = wav[start:end]

    # Guardar resultado
    sf.write(OUTPUT_PATH, wav, 24000)
    print(f"✅ Audio generado: {OUTPUT_PATH} (Duration: {len(wav)/24000:.2f}s)")
    print(f"Usando referencia: {REFERENCE_AUDIO}")

except Exception as e:
    print(f"Error durante la generación: {e}")
