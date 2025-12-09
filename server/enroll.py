import torch
import librosa
import numpy as np
import argparse
import os
from chatterbox.tts import ChatterboxTTS

import sys
import os

# Add client export directory to path to import PrepareConditionalsModel
current_dir = os.path.dirname(os.path.abspath(__file__))
client_export_dir = os.path.join(current_dir, "..", "client", "export")
sys.path.append(client_export_dir)

try:
    from export_components import PrepareConditionalsModel, S3GEN_SR
except ImportError:
    print("Error: Could not import PrepareConditionalsModel. Make sure export_components.py is in ../client/export/")
    sys.exit(1)

def enroll_voice(audio_path, output_path, model_path=None, device="cuda"):
    """
    Generates a voice embedding (Voice ID) from an audio file.
    Saves a dictionary with: cond_emb, prompt_token, speaker_embeddings, speaker_features.
    """
    print(f"Loading model on {device}...")
    if model_path:
        model = ChatterboxTTS.from_local(ckpt_dir=model_path, device=device)
    else:
        model = ChatterboxTTS.from_pretrained(device=device)
        
    print(f"Processing audio: {audio_path}")
    # Load audio using librosa as expected by PrepareConditionalsModel
    # It expects 24kHz for S3GEN
    wav, sr = librosa.load(audio_path, sr=S3GEN_SR)
    
    # Ensure it's a tensor [1, T]
    audio_values = torch.from_numpy(wav).unsqueeze(0).to(device)
    
    # Initialize helper
    prep_model = PrepareConditionalsModel(model).to(device).eval()
    
    print("Extracting conditioning features...")
    with torch.no_grad():
        cond_emb, prompt_token, speaker_embeddings, speaker_features = prep_model(audio_values)
        
    # Convert to numpy
    voice_data = {
        "cond_emb": cond_emb.cpu().numpy(),
        "prompt_token": prompt_token.cpu().numpy(),
        "speaker_embeddings": speaker_embeddings.cpu().numpy(),
        "speaker_features": speaker_features.cpu().numpy()
    }
        
    # Save as .npy
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.save(output_path, voice_data)
    print(f"✅ Voice ID saved to: {output_path}")
    print(f"Keys: {list(voice_data.keys())}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enroll a new voice for Chatterbox TTS")
    parser.add_argument("--audio", type=str, required=True, help="Path to reference audio")
    parser.add_argument("--output", type=str, required=True, help="Path to save .npy file")
    parser.add_argument("--model", type=str, default=None, help="Path to fine-tuned model (optional)")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    
    args = parser.parse_args()
    
    enroll_voice(args.audio, args.output, args.model, args.device)
