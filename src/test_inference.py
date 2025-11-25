import soundfile as sf
import torch
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
    try:
        wav = model.generate(text, lang="es")
        
        # Ensure wav is numpy array for soundfile
        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()
            
        # Save to file
        output_path = "test_es_ar.wav"
        sf.write(output_path, wav, 24000)
        
        print(f"Listo, generé {output_path}")
        
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    main()
