import soundfile as sf
import torch
import numpy as np
from chatterbox.tts import ChatterboxTTS

def main():
    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load merged model
    model_path = "./checkpoints_lora/merged_model"
    print(f"Loading merged model from {model_path}...")
    try:
        model = ChatterboxTTS.from_local(ckpt_dir=model_path, device=device)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure the model has been trained and merged to './checkpoints_lora/merged_model'.")
        return

    # Text to synthesize
    text = "Che, me voy al laburo en bondi porque el auto está hecho mierda."
    
    print(f"Generating audio for: '{text}'")
    
    # Generate audio
    # Generate audio
    try:
        # Tuned parameters for better stopping and quality
        wav = model.generate(
            text,
            temperature=0.7,  # Less random
            top_p=0.9,       # Nucleus sampling
            repetition_penalty=1.2,
            min_p=0.05
        )
        
        # Ensure wav is numpy array for soundfile
        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()
        
        # Ensure wav is 1D
        if len(wav.shape) > 1:
            wav = wav.squeeze()
            
        # Trim silence (simple energy-based trimming)
        # Assuming 24kHz sample rate
        threshold = 0.01
        # Find first and last sample above threshold
        mask = np.abs(wav) > threshold
        if np.any(mask):
            start = np.argmax(mask)
            end = len(wav) - np.argmax(mask[::-1])
            # Add a bit of padding (0.1s)
            pad = int(0.1 * 24000)
            start = max(0, start - pad)
            end = min(len(wav), end + pad)
            wav = wav[start:end]
            
        # Save to file
        output_path = "test_es_ar.wav"
        sf.write(output_path, wav, 24000)
        
        print(f"Listo, generé {output_path} (Duration: {len(wav)/24000:.2f}s)")
        
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    main()
